import React from "react";
import { CheckCircle2, AlertTriangle, AlertOctagon } from "lucide-react";
import { ConclusionLevel } from "@/lib/types";

interface ConclusionBadgeProps {
  level?: ConclusionLevel;
  size?: "sm" | "md" | "lg";
}

export const ConclusionBadge: React.FC<ConclusionBadgeProps> = ({
  level = "review_recommended",
  size = "md",
}) => {
  const configs = {
    no_major_alert: {
      label: "Aucune alerte majeure identifiée",
      icon: CheckCircle2,
      bg: "bg-emerald-50 text-emerald-800 border-emerald-200",
      iconColor: "text-emerald-600",
    },
    review_recommended: {
      label: "Vérification supplémentaire recommandée",
      icon: AlertTriangle,
      bg: "bg-amber-50 text-amber-900 border-amber-200",
      iconColor: "text-amber-600",
    },
    important_attention: {
      label: "Attention importante requise",
      icon: AlertOctagon,
      bg: "bg-rose-50 text-rose-900 border-rose-200",
      iconColor: "text-rose-600",
    },
  };

  const config = configs[level] || configs.review_recommended;
  const Icon = config.icon;

  const sizeClasses = {
    sm: "px-2.5 py-1 text-xs gap-1.5",
    md: "px-3.5 py-2 text-sm gap-2 font-semibold",
    lg: "px-5 py-3 text-base gap-3 font-bold",
  };

  return (
    <div
      className={`inline-flex items-center rounded-xl border ${config.bg} ${sizeClasses[size]} shadow-xs`}
    >
      <Icon className={`w-5 h-5 shrink-0 ${config.iconColor}`} />
      <span>{config.label}</span>
    </div>
  );
};
