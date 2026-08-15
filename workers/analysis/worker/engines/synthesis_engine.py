from typing import Dict, Any, List, Tuple, Optional
from apps.api.app.models.enums import (
    ConclusionLevel,
    ProvenanceStatus,
    IntegrityStatus,
    AIStatus,
    ContextStatus,
    EvidenceType,
    EvidenceSeverity,
    EngineCode,
)
from workers.analysis.worker.engines.base import BaseEngine


class SynthesisEngine(BaseEngine):
    engine_code = EngineCode.SYNTHESIS
    provider_name = "forensic_synthesis"
    version = "1.0.0"

    def run(
        self,
        c2pa_data: Optional[Dict[str, Any]],
        metadata_data: Optional[Dict[str, Any]],
        hash_data: Optional[Dict[str, Any]],
        ai_data: Optional[Dict[str, Any]],
        web_matches: List[Any],
        fact_checks: List[Any],
        claim: Optional[str] = None
    ) -> Tuple[ConclusionLevel, ProvenanceStatus, IntegrityStatus, AIStatus, ContextStatus, str, List[Dict[str, Any]]]:
        """
        Calculates the 4 independent indicators, the overall conclusion level,
        and generates the verifiable evidence list for 'Pourquoi cette conclusion ?'.
        """
        evidences = []

        # 1. Evaluate Provenance
        if c2pa_data and c2pa_data.get("has_manifest"):
            if c2pa_data.get("is_valid"):
                provenance_status = ProvenanceStatus.VERIFIED
                evidences.append({
                    "evidence_type": EvidenceType.TECHNICAL_PROOF,
                    "title_fr": "Manifeste C2PA / Content Credentials valide",
                    "description_fr": f"Signature cryptographique vérifiée. Émetteur / Générateur : {c2pa_data.get('claim_generator') or c2pa_data.get('issuer') or 'Non spécifié'}.",
                    "source_engine": "c2pa",
                    "severity": EvidenceSeverity.POSITIVE,
                })
            else:
                provenance_status = ProvenanceStatus.INCONSISTENT
                evidences.append({
                    "evidence_type": EvidenceType.TECHNICAL_PROOF,
                    "title_fr": "Manifeste C2PA altéré ou invalide",
                    "description_fr": "Un manifeste de provenance est présent mais sa signature cryptographique a échoué à la validation.",
                    "source_engine": "c2pa",
                    "severity": EvidenceSeverity.CRITICAL,
                })
        else:
            provenance_status = ProvenanceStatus.UNKNOWN
            evidences.append({
                "evidence_type": EvidenceType.DECLARED_INFO,
                "title_fr": "Absence de manifeste C2PA",
                "description_fr": "Aucune preuve de provenance C2PA détectée. Origine technique directe indéterminée (l'absence de C2PA ne prouve pas une manipulation).",
                "source_engine": "c2pa",
                "severity": EvidenceSeverity.INFO,
            })

        # 2. Evaluate Integrity
        if metadata_data:
            make = metadata_data.get("make")
            model = metadata_data.get("model")
            software = metadata_data.get("software")

            if make or model:
                integrity_status = IntegrityStatus.CLEAR
                evidences.append({
                    "evidence_type": EvidenceType.DECLARED_INFO,
                    "title_fr": "Métadonnées d'appareil photo déclarées",
                    "description_fr": f"Appareil déclaré : {make or ''} {model or ''}. Logiciel : {software or 'Non spécifié'}.",
                    "source_engine": "metadata",
                    "severity": EvidenceSeverity.POSITIVE,
                })
            else:
                integrity_status = IntegrityStatus.REVIEW
                evidences.append({
                    "evidence_type": EvidenceType.DECLARED_INFO,
                    "title_fr": "Métadonnées EXIF absentes ou purgées",
                    "description_fr": "Les métadonnées EXIF de l'appareil ne sont pas présentes (cas fréquent après partage sur les réseaux sociaux / messageries comme WhatsApp).",
                    "source_engine": "metadata",
                    "severity": EvidenceSeverity.INFO,
                })
        else:
            integrity_status = IntegrityStatus.REVIEW

        # 3. Evaluate AI Indices
        if c2pa_data and c2pa_data.get("ai_declared"):
            ai_status = AIStatus.DECLARED
            evidences.append({
                "evidence_type": EvidenceType.TECHNICAL_PROOF,
                "title_fr": "Utilisation d'IA déclarée dans les Content Credentials",
                "description_fr": "Le manifeste d'origine déclare explicitement la création ou l'édition par un outil d'intelligence artificielle.",
                "source_engine": "c2pa",
                "severity": EvidenceSeverity.WARNING,
            })
        elif ai_data:
            category = ai_data.get("category", AIStatus.INDETERMINATE)
            raw_score = ai_data.get("raw_score", 0.0)
            ai_status = category

            severity_map = {
                AIStatus.HIGH: EvidenceSeverity.CRITICAL,
                AIStatus.MODERATE: EvidenceSeverity.WARNING,
                AIStatus.LOW: EvidenceSeverity.POSITIVE,
                AIStatus.INDETERMINATE: EvidenceSeverity.INFO,
            }
            evidences.append({
                "evidence_type": EvidenceType.ESTIMATION,
                "title_fr": f"Estimation IA : {category.value}",
                "description_fr": f"Le détecteur algorithmique a évalué la probabilité de génération ou manipulation IA (Indice : {category.value}). Ceci constitue une estimation statistique et non une certitude absolue.",
                "source_engine": "ai",
                "severity": severity_map.get(category, EvidenceSeverity.INFO),
            })
        else:
            ai_status = AIStatus.INDETERMINATE

        # 4. Evaluate Context & Fact-checks
        has_debunk = len(fact_checks) > 0
        has_prior_web = any(getattr(m, "earliest_date_found", None) is not None for m in web_matches) or (len(web_matches) > 0 and claim)

        if has_debunk:
            context_status = ContextStatus.POTENTIAL_DECONTEXTUALIZATION
            for fc in fact_checks:
                pub = getattr(fc, "publisher_name", "Organisme de fact-checking")
                rating = getattr(fc, "rating", "Contesté")
                evidences.append({
                    "evidence_type": EvidenceType.EXTERNAL_MATCH,
                    "title_fr": f"Fact-check publié par {pub}",
                    "description_fr": f"Évaluation : « {rating} » concernant cette affirmation ou ce média.",
                    "source_engine": "fact_check",
                    "severity": EvidenceSeverity.CRITICAL,
                })
        elif has_prior_web and claim:
            context_status = ContextStatus.POTENTIAL_DECONTEXTUALIZATION
            evidences.append({
                "evidence_type": EvidenceType.EXTERNAL_MATCH,
                "title_fr": "Antériorité Web identifiée en décalage avec l'affirmation",
                "description_fr": f"Des occurrences antérieures de ce média ont été retrouvées sur le Web, suggérant une réutilisation hors de son contexte d'origine.",
                "source_engine": "web_context",
                "severity": EvidenceSeverity.WARNING,
            })
        elif len(web_matches) > 0:
            context_status = ContextStatus.REVIEW
            evidences.append({
                "evidence_type": EvidenceType.EXTERNAL_MATCH,
                "title_fr": f"{len(web_matches)} correspondance(s) Web retrouvée(s)",
                "description_fr": "Ce média a déjà circulé sur internet.",
                "source_engine": "web_context",
                "severity": EvidenceSeverity.INFO,
            })
        else:
            context_status = ContextStatus.COHERENT
            evidences.append({
                "evidence_type": EvidenceType.EXTERNAL_MATCH,
                "title_fr": "Aucune correspondance Web contradictoire trouvée",
                "description_fr": "Le média n'a pas fait l'objet d'un fact-check public indexé ou d'une antériorité majeure signalée.",
                "source_engine": "web_context",
                "severity": EvidenceSeverity.INFO,
            })

        # 5. Determine Overall Conclusion Level
        if (
            context_status == ContextStatus.POTENTIAL_DECONTEXTUALIZATION
            or provenance_status == ProvenanceStatus.INCONSISTENT
            or ai_status in (AIStatus.HIGH, AIStatus.DECLARED)
        ):
            conclusion_level = ConclusionLevel.IMPORTANT_ATTENTION
            summary_fr = (
                "Attention importante requise : Des éléments techniques ou contextuels contradictoires "
                "(tels qu'une antériorité Web, un fact-check existant ou des indices élevés de manipulation) "
                "ont été identifiés. Une prudence extrême est recommandée avant tout partage."
            )
        elif (
            context_status == ContextStatus.REVIEW
            or integrity_status == IntegrityStatus.REVIEW
            or ai_status == AIStatus.MODERATE
            or (provenance_status == ProvenanceStatus.UNKNOWN and claim)
        ):
            conclusion_level = ConclusionLevel.REVIEW_RECOMMENDED
            summary_fr = (
                "Vérification supplémentaire recommandée : Le média présente des éléments incomplets "
                "(absence de signature C2PA, métadonnées épurées ou correspondances Web nécessitant confirmation). "
                "Consultez les détails des preuves ci-dessous."
            )
        else:
            conclusion_level = ConclusionLevel.NO_MAJOR_ALERT
            summary_fr = (
                "Aucune alerte majeure détectée : Les analyses techniques et contextuelles n'ont pas révélé "
                "d'incohérence manifeste, d'antériorité trompeuse ou d'indice prépondérant de manipulation."
            )

        return (
            conclusion_level,
            provenance_status,
            integrity_status,
            ai_status,
            context_status,
            summary_fr,
            evidences,
        )
