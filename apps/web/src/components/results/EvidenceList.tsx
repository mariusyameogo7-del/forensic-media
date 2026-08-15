import React from "react";
import { CheckCircle, AlertTriangle, AlertCircle, Info, Sparkles } from "lucide-react";
import { EvidenceItem, EvidenceType, EvidenceSeverity } from "@/lib/types";

interface EvidenceListProps {
  evidences: EvidenceItem[];
}

export const EvidenceList: React.FC<EvidenceListProps> = ({ evidences }) => {
  const getTypeBadge = (type: EvidenceType) => {
    switch (type) {
      case "technical_proof":
        return { label: "Preuve technique", bg: "bg-emerald-50 text-emerald-800 border-emerald-200" };
      case "declared_info":
        return { label: "Information déclarée", bg: "bg-slate-100 text-slate-700 border-slate-200" };
      case "external_match":
        return { label: "Correspondance externe", bg: "bg-sky-50 text-sky-800 border-sky-200" };
      case "estimation":
        return { label: "Estimation algorithmique", bg: "bg-purple-50 text-purple-800 border-purple-200" };
      default:
        return { label: "Constat", bg: "bg-slate-100 text-slate-700 border-slate-200" };
    }
  };

  const getSeverityIcon = (sev: EvidenceSeverity) => {
    switch (sev) {
      case "positive":
        return <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />;
      case "warning":
        return <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />;
      case "critical":
        return <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />;
      default:
        return <Info className="w-4 h-4 text-sky-600 shrink-0 mt-0.5" />;
    }
  };

  if (!evidences || evidences.length === 0) {
    return (
      <div className="p-6 text-center text-slate-500 text-sm">
        Aucun élément de preuve individuel à afficher.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {evidences.map((ev, idx) => {
        const typeInfo = getTypeBadge(ev.evidence_type);
        return (
          <div
            key={ev.id || idx}
            className="p-4 rounded-xl border border-slate-200 bg-white hover:border-slate-300 transition-colors shadow-2xs flex items-start gap-3"
          >
            {getSeverityIcon(ev.severity)}
            <div className="flex-1 min-w-0">
              <div className="flex flex-wrap items-center gap-2 mb-1">
                <span className="text-sm font-semibold text-slate-900">
                  {ev.title_fr}
                </span>
                <span
                  className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-semibold border ${typeInfo.bg}`}
                >
                  {typeInfo.label}
                </span>
                <span className="text-[11px] text-slate-600 font-mono">
                  Moteur: {ev.source_engine}
                </span>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                {ev.description_fr}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
};
