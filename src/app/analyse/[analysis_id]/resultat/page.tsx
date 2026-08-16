"use client";

import React, { useEffect, useState, use } from "react";
import Link from "next/link";
import {
  ShieldCheck,
  FileSearch,
  Sparkles,
  Globe,
  Binary,
  FileText,
  Download,
  RotateCcw,
  AlertCircle,
  HelpCircle,
  ExternalLink,
} from "lucide-react";
import { ApiClient } from "@/lib/api-client";
import { AnalysisResultResponse } from "@/lib/types";
import { ConclusionBadge } from "@/components/analysis/ConclusionBadge";
import { IndicatorsGrid } from "@/components/analysis/IndicatorsGrid";
import { EvidenceList } from "@/components/results/EvidenceList";
import { EngineCard } from "@/components/results/EngineCard";
import { Button } from "@/components/ui/Button";

interface PageProps {
  params: Promise<{ analysis_id: string }>;
}

export default function AnalysisResultPage({ params }: PageProps) {
  const { analysis_id } = use(params);
  const [result, setResult] = useState<AnalysisResultResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const data = await ApiClient.getResult(analysis_id);
        setResult(data);
      } catch (err: any) {
        setError(err.message || "Erreur lors du chargement des résultats.");
      } finally {
        setLoading(false);
      }
    };
    fetchResult();
  }, [analysis_id]);

  if (loading) {
    return (
      <div className="py-16 text-center text-slate-500">
        Chargement des résultats de l&apos;analyse...
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="max-w-xl mx-auto py-12">
        <div className="p-6 bg-rose-50 border border-rose-200 rounded-2xl text-center space-y-4">
          <AlertCircle className="w-8 h-8 text-rose-600 mx-auto" />
          <h2 className="text-lg font-bold text-rose-900">Impossible d&apos;afficher le résultat</h2>
          <p className="text-sm text-rose-700">{error || "Analyse introuvable."}</p>
          <Link href="/">
            <Button variant="primary">Nouvelle analyse</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Top Action Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-900">
              Résultat d&apos;analyse de média
            </h1>
            <span className="font-mono text-xs px-2.5 py-0.5 rounded-full bg-slate-100 border border-slate-200 text-slate-700">
              {result.public_id}
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Fichier : <strong>{result.original_filename}</strong> ({(result.file_size / 1024).toFixed(1)} KB)
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link href={`/analyse/${result.analysis_id}/rapport`}>
            <Button variant="outline" size="sm" className="gap-1.5">
              <FileText className="w-4 h-4" />
              <span>Consulter le rapport</span>
            </Button>
          </Link>
          <Link href="/">
            <Button variant="primary" size="sm" className="gap-1.5">
              <RotateCcw className="w-4 h-4" />
              <span>Nouvelle analyse</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Claim Banner (if present) */}
      {result.claim && (
        <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-800">
          <span className="font-semibold text-xs text-slate-500 uppercase tracking-wider block mb-1">
            Affirmation fournie par l&apos;utilisateur :
          </span>
          <p className="italic text-slate-700">« {result.claim} »</p>
        </div>
      )}

      {/* LEVEL 1: Prudent Conclusion & 4 Independent Indicators */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-6">
        <div>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-2">
            Conclusion synthétique de l&apos;évaluation
          </span>
          <ConclusionBadge level={result.conclusion_level} size="lg" />
          {result.summary_fr && (
            <p className="text-sm text-slate-700 mt-3 leading-relaxed">
              {result.summary_fr}
            </p>
          )}
        </div>

        {/* 4 Independent Dimension Indicators */}
        <div>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
            Évaluation par dimension
          </span>
          <IndicatorsGrid
            provenance={result.provenance_status}
            integrity={result.integrity_status}
            ai={result.ai_status}
            context={result.context_status}
          />
        </div>
      </div>

      {/* LEVEL 2: "Pourquoi cette conclusion ?" (Verifiable Evidence List) */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-4">
        <div className="flex items-center gap-2">
          <HelpCircle className="w-5 h-5 text-sky-600" />
          <h2 className="text-base font-bold text-slate-900">
            Pourquoi cette conclusion ?
          </h2>
        </div>
        <p className="text-xs text-slate-500">
          Chaque constatation est rattachée à une source ou à une méthode identifiable (preuve technique, information déclarée, correspondance externe ou estimation).
        </p>
        <EvidenceList evidences={result.evidences} />
      </div>

      {/* LEVEL 3: Detailed Engine Breakdowns */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider">
          Détail des constatations techniques par moteur
        </h3>

        {/* 1. C2PA / Content Credentials */}
        <EngineCard
          title="Provenance & Content Credentials (C2PA)"
          icon={<ShieldCheck className="w-5 h-5 text-sky-600" />}
          defaultOpen={false}
        >
          <div className="space-y-2">
            <p>
              <strong>Manifeste C2PA :</strong>{" "}
              {result.provenance_status === "verified"
                ? "Manifeste présent et signature cryptographique valide."
                : "Aucun manifeste C2PA détecté. (L'absence de signature ne prouve pas une falsification)."}
            </p>
          </div>
        </EngineCard>

        {/* 2. Métadonnées EXIF */}
        <EngineCard
          title="Métadonnées & Structure de fichier (ExifTool)"
          icon={<FileSearch className="w-5 h-5 text-emerald-600" />}
          defaultOpen={false}
        >
          <div className="space-y-2">
            <p>
              <strong>Format :</strong> {result.mime_type} • {(result.file_size / 1024).toFixed(1)} KB
            </p>
            <p>
              <strong>État des métadonnées :</strong>{" "}
              {result.integrity_status === "clear"
                ? "Métadonnées de capture cohérentes."
                : "Métadonnées EXIF absentes (fréquent après compression WhatsApp/réseaux sociaux)."}
            </p>
          </div>
        </EngineCard>

        {/* 3. Détection IA */}
        <EngineCard
          title="Estimation d'indices IA (Hive AI)"
          icon={<Sparkles className="w-5 h-5 text-purple-600" />}
          defaultOpen={false}
        >
          <div className="space-y-2">
            <p>
              <strong>Évaluation :</strong> Indice {result.ai_status || "Indéterminé"}
            </p>
            <p className="text-slate-500">
              Note : La détection d&apos;IA est une estimation statistique probabiliste et ne constitue jamais une preuve absolue.
            </p>
          </div>
        </EngineCard>

        {/* 4. Contexte Web & Fact-checks */}
        <EngineCard
          title="Contexte Web & Fact-checks (Google Vision & Fact Check Tools)"
          icon={<Globe className="w-5 h-5 text-amber-600" />}
          defaultOpen={false}
        >
          <div className="space-y-2">
            <p>
              <strong>Statut contextuel :</strong> {result.context_status}
            </p>
          </div>
        </EngineCard>

        {/* 5. Empreintes cryptographiques */}
        <EngineCard
          title="Empreintes cryptographiques & Perceptuelles"
          icon={<Binary className="w-5 h-5 text-slate-700" />}
          defaultOpen={false}
        >
          <div className="space-y-2 font-mono text-[11px] break-all">
            <div>
              <span className="font-bold text-slate-900">SHA-256 (Original) :</span> {result.sha256}
            </div>
            {result.phash && (
              <div>
                <span className="font-bold text-slate-900">pHash :</span> {result.phash}
              </div>
            )}
          </div>
        </EngineCard>
      </div>
    </div>
  );
}
