"use client";

import React, { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import {
  CheckCircle2,
  Clock,
  Loader2,
  AlertCircle,
  Shield,
  FileSearch,
  Sparkles,
  Globe,
  Binary,
  Layers,
} from "lucide-react";
import { ApiClient } from "@/lib/api-client";
import { AnalysisProgressResponse } from "@/lib/types";

interface PageProps {
  params: Promise<{ analysis_id: string }>;
}

export default function AnalysisProgressPage({ params }: PageProps) {
  const { analysis_id } = use(params);
  const router = useRouter();
  const [progressData, setProgressData] = useState<AnalysisProgressResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isSubscribed = true;
    let timer: NodeJS.Timeout;

    const fetchProgress = async () => {
      try {
        const data = await ApiClient.getProgress(analysis_id);
        if (!isSubscribed) return;

        setProgressData(data);

        if (data.status === "completed") {
          // Redirect to Screen 3: Résultat
          setTimeout(() => {
            router.push(`/analyse/${analysis_id}/resultat`);
          }, 800);
          return;
        }

        if (data.status === "failed") {
          setError(data.public_error_message || "L'analyse a rencontré une erreur critique.");
          return;
        }

        // Poll every 1.5 seconds
        timer = setTimeout(fetchProgress, 1500);
      } catch (err: any) {
        if (!isSubscribed) return;
        setError(err.message || "Impossible de joindre le serveur.");
      }
    };

    fetchProgress();

    return () => {
      isSubscribed = false;
      clearTimeout(timer);
    };
  }, [analysis_id, router]);

  const stepDefinitions = [
    { code: "hashes", label: "Calcul de l'empreinte SHA-256 & pHash", icon: Binary },
    { code: "metadata", label: "Extraction des métadonnées EXIF & appareil", icon: FileSearch },
    { code: "c2pa", label: "Vérification des Content Credentials (C2PA)", icon: Shield },
    { code: "ai", label: "Estimation des indices de manipulation IA", icon: Sparkles },
    { code: "web_context", label: "Recherche de correspondances Web antérieures", icon: Globe },
    { code: "fact_check", label: "Interrogation des bases de fact-checking", icon: FileSearch },
    { code: "synthesis", label: "Synthèse et consolidation des preuves", icon: Layers },
  ];

  const getStepStatus = (code: string) => {
    if (!progressData) return "pending";
    if (progressData.status === "completed") return "completed";

    const step = progressData.steps?.find((s) => s.engine_code === code);
    if (!step) return "pending";
    return step.status;
  };

  return (
    <div className="max-w-2xl mx-auto py-8">
      <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-xs">
        {/* Header */}
        <div className="text-center space-y-2 mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-50 text-sky-700 text-xs font-semibold">
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
            <span>Analyse en cours</span>
          </div>

          <h1 className="text-2xl font-bold text-slate-900">
            Vérification du média en cours
          </h1>

          <p className="text-sm text-slate-500">
            Identifiant : <span className="font-mono font-semibold text-slate-700">{progressData?.public_id || "..."}</span>
          </p>

          {/* Progress Bar */}
          <div className="w-full bg-slate-100 rounded-full h-2.5 mt-6 overflow-hidden">
            <div
              className="bg-sky-600 h-2.5 rounded-full transition-all duration-500"
              style={{ width: `${progressData?.progress_percent || 10}%` }}
            />
          </div>
        </div>

        {error ? (
          <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 rounded-xl text-sm flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
            <span>{error}</span>
          </div>
        ) : (
          /* Step-by-step progress checklist */
          <div className="space-y-3.5">
            {stepDefinitions.map((stepDef) => {
              const status = getStepStatus(stepDef.code);
              const Icon = stepDef.icon;

              return (
                <div
                  key={stepDef.code}
                  className={`flex items-center justify-between p-3.5 rounded-xl border transition-colors ${
                    status === "completed"
                      ? "bg-slate-50/80 border-slate-200"
                      : status === "running"
                      ? "bg-sky-50/50 border-sky-200"
                      : "bg-white border-slate-100 opacity-60"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`p-2 rounded-lg ${
                        status === "completed"
                          ? "bg-emerald-100 text-emerald-700"
                          : status === "running"
                          ? "bg-sky-100 text-sky-700 animate-pulse"
                          : "bg-slate-100 text-slate-400"
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                    </div>
                    <span
                      className={`text-sm font-medium ${
                        status === "completed" || status === "running"
                          ? "text-slate-900"
                          : "text-slate-500"
                      }`}
                    >
                      {stepDef.label}
                    </span>
                  </div>

                  <div>
                    {status === "completed" && (
                      <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                    )}
                    {status === "running" && (
                      <Loader2 className="w-5 h-5 text-sky-600 animate-spin" />
                    )}
                    {status === "pending" && (
                      <Clock className="w-4 h-4 text-slate-300" />
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        <div className="mt-8 text-center text-xs text-slate-500">
          Les résultats seront consolidés et affichés dès la fin de la synthèse finale.
        </div>
      </div>
    </div>
  );
}
