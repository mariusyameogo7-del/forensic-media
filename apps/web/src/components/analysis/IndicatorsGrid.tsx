import React from "react";
import { Shield, FileCheck, Cpu, Globe } from "lucide-react";
import {
  ProvenanceStatus,
  IntegrityStatus,
  AIStatus,
  ContextStatus,
} from "@/lib/types";

interface IndicatorsGridProps {
  provenance?: ProvenanceStatus;
  integrity?: IntegrityStatus;
  ai?: AIStatus;
  context?: ContextStatus;
}

export const IndicatorsGrid: React.FC<IndicatorsGridProps> = ({
  provenance = "unknown",
  integrity = "review",
  ai = "indeterminate",
  context = "review",
}) => {
  const getProvenanceBadge = (status: ProvenanceStatus) => {
    switch (status) {
      case "verified":
        return { label: "Vérifiée (C2PA)", color: "text-emerald-700 bg-emerald-50 border-emerald-200" };
      case "partial":
        return { label: "Partielle", color: "text-sky-700 bg-sky-50 border-sky-200" };
      case "inconsistent":
        return { label: "Incohérente / Altérée", color: "text-rose-700 bg-rose-50 border-rose-200" };
      default:
        return { label: "Inconnue (Sans C2PA)", color: "text-slate-700 bg-slate-100 border-slate-200" };
    }
  };

  const getIntegrityBadge = (status: IntegrityStatus) => {
    switch (status) {
      case "clear":
        return { label: "Aucun problème", color: "text-emerald-700 bg-emerald-50 border-emerald-200" };
      case "major_anomaly":
        return { label: "Anomalie majeure", color: "text-rose-700 bg-rose-50 border-rose-200" };
      default:
        return { label: "Éléments à examiner", color: "text-amber-800 bg-amber-50 border-amber-200" };
    }
  };

  const getAIBadge = (status: AIStatus) => {
    switch (status) {
      case "declared":
        return { label: "Utilisation déclarée", color: "text-purple-700 bg-purple-50 border-purple-200" };
      case "high":
        return { label: "Indices élevés", color: "text-rose-700 bg-rose-50 border-rose-200" };
      case "moderate":
        return { label: "Indices modérés", color: "text-amber-800 bg-amber-50 border-amber-200" };
      case "low":
        return { label: "Faibles indices", color: "text-emerald-700 bg-emerald-50 border-emerald-200" };
      default:
        return { label: "Indéterminé", color: "text-slate-700 bg-slate-100 border-slate-200" };
    }
  };

  const getContextBadge = (status: ContextStatus) => {
    switch (status) {
      case "coherent":
        return { label: "Cohérent", color: "text-emerald-700 bg-emerald-50 border-emerald-200" };
      case "potential_decontextualization":
        return { label: "Décontextualisation potentielle", color: "text-rose-700 bg-rose-50 border-rose-200" };
      default:
        return { label: "À vérifier", color: "text-amber-800 bg-amber-50 border-amber-200" };
    }
  };

  const prov = getProvenanceBadge(provenance);
  const integ = getIntegrityBadge(integrity);
  const aiInfo = getAIBadge(ai);
  const ctx = getContextBadge(context);

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5 my-6">
      {/* 1. Provenance */}
      <div className="p-4 rounded-xl border border-slate-200 bg-white shadow-xs">
        <div className="flex items-center gap-2 text-slate-500 mb-2">
          <Shield className="w-4 h-4 text-sky-600" />
          <span className="text-xs font-semibold uppercase tracking-wider">Provenance</span>
        </div>
        <div className={`inline-block px-2.5 py-1 rounded-md text-xs font-semibold border ${prov.color}`}>
          {prov.label}
        </div>
      </div>

      {/* 2. Intégrité */}
      <div className="p-4 rounded-xl border border-slate-200 bg-white shadow-xs">
        <div className="flex items-center gap-2 text-slate-500 mb-2">
          <FileCheck className="w-4 h-4 text-emerald-600" />
          <span className="text-xs font-semibold uppercase tracking-wider">Intégrité</span>
        </div>
        <div className={`inline-block px-2.5 py-1 rounded-md text-xs font-semibold border ${integ.color}`}>
          {integ.label}
        </div>
      </div>

      {/* 3. IA */}
      <div className="p-4 rounded-xl border border-slate-200 bg-white shadow-xs">
        <div className="flex items-center gap-2 text-slate-500 mb-2">
          <Cpu className="w-4 h-4 text-indigo-600" />
          <span className="text-xs font-semibold uppercase tracking-wider">Indices IA</span>
        </div>
        <div className={`inline-block px-2.5 py-1 rounded-md text-xs font-semibold border ${aiInfo.color}`}>
          {aiInfo.label}
        </div>
      </div>

      {/* 4. Contexte */}
      <div className="p-4 rounded-xl border border-slate-200 bg-white shadow-xs">
        <div className="flex items-center gap-2 text-slate-500 mb-2">
          <Globe className="w-4 h-4 text-teal-600" />
          <span className="text-xs font-semibold uppercase tracking-wider">Contexte Web</span>
        </div>
        <div className={`inline-block px-2.5 py-1 rounded-md text-xs font-semibold border ${ctx.color}`}>
          {ctx.label}
        </div>
      </div>
    </div>
  );
};
