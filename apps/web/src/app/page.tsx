"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { ShieldCheck, FileSearch, Sparkles, Globe2, Lock } from "lucide-react";
import { Dropzone } from "@/components/analysis/Dropzone";
import { ApiClient } from "@/lib/api-client";

export default function HomePage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const handleAnalyze = async (file: File, claim?: string) => {
    setIsLoading(true);
    try {
      const response = await ApiClient.createAnalysis(file, claim);
      router.push(`/analyse/${response.analysis_id}/progress`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <div className="text-center max-w-3xl mx-auto space-y-4 pt-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-50 border border-sky-200 text-sky-800 text-xs font-semibold">
          <ShieldCheck className="w-4 h-4 text-sky-600" />
          <span>Plateforme africaine d&apos;analyse de provenance et vérification</span>
        </div>

        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight leading-tight">
          Vérifiez une image avant de lui faire confiance
        </h1>

        <p className="text-base sm:text-lg text-slate-600 leading-relaxed">
          Nous ne vous disons pas seulement si un contenu semble suspect. Nous analysons ce qui peut être prouvé sur son origine, ses modifications et son contexte.
        </p>
      </div>

      {/* Screen 1: Dropzone & Claim Input */}
      <Dropzone onAnalyze={handleAnalyze} isLoading={isLoading} />

      {/* Four Dimensions Overview */}
      <div className="pt-8 border-t border-slate-200 max-w-5xl mx-auto">
        <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wider text-center mb-8">
          Quatre dimensions d&apos;analyse indépendantes
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-2.5">
            <div className="w-10 h-10 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-slate-900 text-sm">1. Provenance</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Vérification des manifestes cryptographiques C2PA et Content Credentials signés par les appareils et logiciels.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-2.5">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <FileSearch className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-slate-900 text-sm">2. Intégrité</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Examen approfondi des métadonnées EXIF, cohérence des horodatages et empreintes SHA-256 et pHash.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-2.5">
            <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
              <Sparkles className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-slate-900 text-sm">3. Estimation IA</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Évaluation probabiliste des artefacts de génération et retouche algorithmique par IA (sans verdict absolu).
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-2.5">
            <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
              <Globe2 className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-slate-900 text-sm">4. Contexte Web</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Détection des réutilisations antérieures sur le Web et rapprochement avec les vérifications de fact-checkers.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
