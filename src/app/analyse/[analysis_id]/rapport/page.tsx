"use client";

import React, { useEffect, useState, use } from "react";
import Link from "next/link";
import {
  FileText,
  Download,
  ArrowLeft,
  ShieldCheck,
  Calendar,
  Binary,
  CheckCircle2,
  AlertTriangle,
  Info,
} from "lucide-react";
import { ApiClient } from "@/lib/api-client";
import { AnalysisResultResponse } from "@/lib/types";
import { Button } from "@/components/ui/Button";
import { ConclusionBadge } from "@/components/analysis/ConclusionBadge";

interface PageProps {
  params: Promise<{ analysis_id: string }>;
}

export default function AnalysisReportPage({ params }: PageProps) {
  const { analysis_id } = use(params);
  const [result, setResult] = useState<AnalysisResultResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const data = await ApiClient.getResult(analysis_id);
        setResult(data);
      } finally {
        setLoading(false);
      }
    };
    fetchResult();
  }, [analysis_id]);

  const handleDownloadPdf = async () => {
    setDownloading(true);
    try {
      const report = await ApiClient.createReport(analysis_id);
      const downloadUrl = ApiClient.getReportDownloadUrl(report.id, analysis_id);
      window.open(downloadUrl, "_blank");
    } catch (e) {
      alert("Erreur lors de la génération du fichier PDF.");
    } finally {
      setDownloading(false);
    }
  };

  if (loading || !result) {
    return <div className="py-16 text-center text-slate-500">Chargement du rapport...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Top Action Nav */}
      <div className="flex items-center justify-between">
        <Link href={`/analyse/${analysis_id}/resultat`}>
          <Button variant="ghost" size="sm" className="gap-1.5 text-slate-600">
            <ArrowLeft className="w-4 h-4" />
            <span>Retour au résultat</span>
          </Button>
        </Link>

        <Button
          variant="primary"
          size="md"
          onClick={handleDownloadPdf}
          isLoading={downloading}
          className="gap-2"
        >
          <Download className="w-4 h-4" />
          <span>Télécharger en PDF</span>
        </Button>
      </div>

      {/* Formal Web Report Document */}
      <div className="bg-white border border-slate-300 rounded-2xl p-8 sm:p-12 shadow-sm space-y-8 font-sans">
        {/* Header Document */}
        <div className="border-b-2 border-slate-900 pb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="text-xs font-bold text-sky-700 uppercase tracking-widest block">
              Forensic Media
            </span>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 mt-1">
              Rapport d&apos;analyse de média numérique
            </h1>
            <p className="text-xs text-slate-500 mt-1">
              Plateforme africaine de vérification numérique — Rapport horodaté et auditable
            </p>
          </div>
          <div className="text-right sm:border-l sm:border-slate-200 sm:pl-6">
            <div className="text-xs text-slate-500">Référence analyse</div>
            <div className="font-mono font-bold text-base text-slate-900">{result.public_id}</div>
          </div>
        </div>

        {/* Identification Metadata Box */}
        <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2 text-xs">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <div>
              <span className="font-semibold text-slate-600">Fichier original :</span> {result.original_filename}
            </div>
            <div>
              <span className="font-semibold text-slate-600">Format & Taille :</span> {result.mime_type} ({(result.file_size / 1024).toFixed(1)} KB)
            </div>
            <div className="sm:col-span-2 font-mono break-all">
              <span className="font-semibold text-slate-600 font-sans">SHA-256 (Original) :</span> {result.sha256}
            </div>
            {result.claim && (
              <div className="sm:col-span-2 italic text-slate-700 bg-white p-2.5 rounded border border-slate-200">
                <span className="font-semibold text-slate-600 not-italic">Affirmation analysée :</span> « {result.claim} »
              </div>
            )}
          </div>
        </div>

        {/* Synthesis Section */}
        <div className="space-y-4">
          <h2 className="text-base font-bold text-slate-900 border-b border-slate-200 pb-2">
            Synthèse de l&apos;évaluation
          </h2>
          <div className="flex items-center gap-3">
            <span className="text-sm font-semibold text-slate-700">Niveau de conclusion :</span>
            <ConclusionBadge level={result.conclusion_level} size="md" />
          </div>
          <p className="text-sm text-slate-700 leading-relaxed bg-slate-50 p-4 rounded-xl border border-slate-200">
            {result.summary_fr}
          </p>
        </div>

        {/* Indicators Table */}
        <div className="space-y-4">
          <h2 className="text-base font-bold text-slate-900 border-b border-slate-200 pb-2">
            Évaluation des 4 dimensions indépendantes
          </h2>
          <div className="border border-slate-200 rounded-xl overflow-hidden text-xs">
            <table className="w-full text-left">
              <thead className="bg-slate-100 border-b border-slate-200 text-slate-700 font-semibold">
                <tr>
                  <th className="p-3">Dimension</th>
                  <th className="p-3">Évaluation</th>
                  <th className="p-3">Description méthodologique</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 text-slate-600">
                <tr>
                  <td className="p-3 font-semibold text-slate-900">Provenance</td>
                  <td className="p-3 capitalize">{result.provenance_status}</td>
                  <td className="p-3">Examen des manifestes cryptographiques C2PA / Content Credentials.</td>
                </tr>
                <tr>
                  <td className="p-3 font-semibold text-slate-900">Intégrité</td>
                  <td className="p-3 capitalize">{result.integrity_status}</td>
                  <td className="p-3">Examen de la cohérence des métadonnées EXIF et de la structure du fichier.</td>
                </tr>
                <tr>
                  <td className="p-3 font-semibold text-slate-900">Indices IA</td>
                  <td className="p-3 capitalize">{result.ai_status}</td>
                  <td className="p-3">Estimation probabiliste des artefacts de génération et de retouche algorithmique.</td>
                </tr>
                <tr>
                  <td className="p-3 font-semibold text-slate-900">Contexte Web</td>
                  <td className="p-3 capitalize">{result.context_status}</td>
                  <td className="p-3">Recherche de réutilisations antérieures sur le Web et bases de fact-checking.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Evidence List */}
        <div className="space-y-4">
          <h2 className="text-base font-bold text-slate-900 border-b border-slate-200 pb-2">
            Justifications techniques et constatations
          </h2>
          <div className="space-y-2.5">
            {result.evidences.map((ev, idx) => (
              <div key={idx} className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs">
                <div className="font-semibold text-slate-900">
                  [{ev.evidence_type}] {ev.title_fr}
                </div>
                <div className="text-slate-600 mt-0.5">{ev.description_fr}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Notice of Transparency and Limits */}
        <div className="p-4 bg-slate-100 rounded-xl border border-slate-200 text-[11px] text-slate-600 leading-relaxed space-y-1">
          <div className="font-bold text-slate-800 flex items-center gap-1.5 mb-1">
            <Info className="w-3.5 h-3.5 text-sky-600" />
            <span>Principes d&apos;explicabilité et limites :</span>
          </div>
          <p>• Ce rapport constitue un enregistrement horodaté et immuable des constatations techniques au moment de l&apos;analyse.</p>
          <p>• L&apos;absence de manifeste C2PA ne prouve pas qu&apos;une image est fausse.</p>
          <p>• L&apos;absence de métadonnées EXIF ne signifie pas qu&apos;une image est générée par IA (courant après compression messageries).</p>
          <p>• Les scores de détection d&apos;IA sont des estimations probabilistes et non des certitudes absolues.</p>
          <p>• Ce document ne constitue pas un « certificat de vérité » absolu.</p>
        </div>
      </div>
    </div>
  );
}
