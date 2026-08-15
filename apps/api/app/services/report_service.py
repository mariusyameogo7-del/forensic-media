import os
import io
import json
from datetime import datetime, timezone
from uuid import UUID
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from apps.api.app.core.config import settings
from apps.api.app.core.errors import NotFoundError
from apps.api.app.core.security import compute_sha256
from apps.api.app.models.enums import StoredObjectType
from apps.api.app.models.analysis import Analysis
from apps.api.app.models.report import AnalysisReport
from apps.api.app.models.stored_object import StoredObject
from apps.api.app.models.event import AnalysisEvent
from apps.api.app.services.storage_service import storage_service

REPORT_TEMPLATE_HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Rapport d'analyse de média numérique - {public_id}</title>
  <style>
    body {{ font-family: sans-serif; color: #1a202c; margin: 20px; }}
    .header {{ border-bottom: 2px solid #2b6cb0; padding-bottom: 8px; }}
    .title {{ font-size: 20px; color: #2b6cb0; font-weight: bold; }}
    .meta {{ background: #f7fafc; padding: 12px; border-radius: 6px; margin-top: 10px; font-size: 12px; }}
    .section {{ font-size: 14px; font-weight: bold; margin-top: 15px; border-bottom: 1px solid #cbd5e0; }}
    .evidence {{ background: #f7fafc; border-left: 3px solid #3182ce; padding: 6px 10px; margin-top: 6px; font-size: 12px; }}
  </style>
</head>
<body>
  <div class="header">
    <div class="title">Rapport d'analyse de média numérique</div>
    <div>Plateforme africaine de vérification numérique</div>
  </div>
  <div class="meta">
    <p><strong>Référence :</strong> {public_id}</p>
    <p><strong>Fichier :</strong> {original_filename} ({file_size} octets)</p>
    <p><strong>SHA-256 (Original) :</strong> {sha256}</p>
  </div>
  <div class="section">Synthèse de l'évaluation</div>
  <p><strong>Conclusion :</strong> {conclusion_level}</p>
  <p>{summary_fr}</p>
  <div class="section">Éléments de preuve et justifications</div>
  {evidences_html}
</body>
</html>
"""


class ReportService:
    """Service to create, render, hash, and persist immutable analysis reports."""

    def create_report(
        self,
        db: Session,
        analysis: Analysis,
        template_version: str = "1.0.0"
    ) -> AnalysisReport:
        # 1. Build immutable snapshot data
        snapshot_data = self._build_snapshot(analysis)

        # 2. Determine report version
        latest_report = db.execute(
            select(AnalysisReport)
            .where(AnalysisReport.analysis_id == analysis.id)
            .order_by(desc(AnalysisReport.report_version))
        ).scalars().first()
        next_version = (latest_report.report_version + 1) if latest_report else 1

        # 3. Render HTML
        rendered_html = self._render_template(snapshot_data)

        # 4. Generate PDF
        pdf_bytes = self._compile_pdf(rendered_html)
        pdf_sha256 = compute_sha256(pdf_bytes)

        # 5. Store PDF in private storage
        storage_path = f"{analysis.id}/reports/report_v{next_version}.pdf"
        storage_service.upload_file(
            bucket_name=settings.STORAGE_BUCKET_REPORTS,
            storage_path=storage_path,
            data=pdf_bytes,
            content_type="application/pdf"
        )

        stored_obj = StoredObject(
            analysis_id=analysis.id,
            object_type=StoredObjectType.REPORT_PDF,
            bucket_name=settings.STORAGE_BUCKET_REPORTS,
            storage_path=storage_path,
            mime_type="application/pdf",
            file_size=len(pdf_bytes),
            sha256=pdf_sha256,
        )
        db.add(stored_obj)
        db.flush()

        # 6. Save Immutable AnalysisReport record
        report = AnalysisReport(
            analysis_id=analysis.id,
            report_version=next_version,
            template_version=template_version,
            snapshot_data=snapshot_data,
            pdf_stored_object_id=stored_obj.id,
            pdf_sha256=pdf_sha256,
        )
        db.add(report)

        # 7. Log Event
        event = AnalysisEvent(
            analysis_id=analysis.id,
            event_type="report_generated",
            message=f"Rapport v{next_version} généré (SHA-256: {pdf_sha256[:12]}...).",
            metadata_json={"report_version": next_version, "pdf_sha256": pdf_sha256}
        )
        db.add(event)

        db.commit()
        db.refresh(report)
        return report

    def _build_snapshot(self, analysis: Analysis) -> Dict[str, Any]:
        evidences_data = [
            {
                "id": str(e.id),
                "evidence_type": e.evidence_type.value,
                "title_fr": e.title_fr,
                "description_fr": e.description_fr,
                "source_engine": e.source_engine,
                "severity": e.severity.value,
                "reference_id": e.reference_id
            }
            for e in analysis.synthesis_evidences
        ]

        return {
            "analysis": {
                "id": str(analysis.id),
                "public_id": analysis.public_id,
                "original_filename": analysis.original_filename,
                "mime_type": analysis.mime_type,
                "file_size": analysis.file_size,
                "sha256": analysis.sha256,
                "phash": analysis.phash,
                "claim": analysis.claim,
                "created_at": analysis.created_at.isoformat(),
                "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None
            },
            "synthesis": {
                "conclusion_level": analysis.conclusion_level.value if analysis.conclusion_level else "review_recommended",
                "provenance_status": analysis.provenance_status.value if analysis.provenance_status else "unknown",
                "integrity_status": analysis.integrity_status.value if analysis.integrity_status else "review",
                "ai_status": analysis.ai_status.value if analysis.ai_status else "indeterminate",
                "context_status": analysis.context_status.value if analysis.context_status else "review",
                "summary_fr": analysis.synthesis_result.summary_fr if analysis.synthesis_result else "Synthèse d'analyse."
            },
            "evidences": evidences_data,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

    def _render_template(self, snapshot: Dict[str, Any]) -> str:
        try:
            from jinja2 import Template
            # Try full Jinja rendering if available
            t = Template(REPORT_TEMPLATE_HTML)
            return t.render(snapshot=snapshot)
        except Exception:
            # Fallback formatting
            an = snapshot["analysis"]
            syn = snapshot["synthesis"]
            evs = snapshot["evidences"]
            evs_html = "".join([
                f'<div class="evidence"><strong>[{e["evidence_type"]}] {e["title_fr"]}</strong><br>{e["description_fr"]}</div>'
                for e in evs
            ])
            return REPORT_TEMPLATE_HTML.format(
                public_id=an["public_id"],
                original_filename=an["original_filename"],
                file_size=an["file_size"],
                sha256=an["sha256"],
                conclusion_level=syn["conclusion_level"],
                summary_fr=syn["summary_fr"],
                evidences_html=evs_html
            )

    def _compile_pdf(self, html_content: str) -> bytes:
        try:
            from weasyprint import HTML
            return HTML(string=html_content).write_pdf()
        except Exception:
            return html_content.encode("utf-8")


report_service = ReportService()
