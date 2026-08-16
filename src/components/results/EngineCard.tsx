"use client";

import React, { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

interface EngineCardProps {
  title: string;
  icon: React.ReactNode;
  statusBadge?: React.ReactNode;
  children: React.ReactNode;
  defaultOpen?: boolean;
}

export const EngineCard: React.FC<EngineCardProps> = ({
  title,
  icon,
  statusBadge,
  children,
  defaultOpen = false,
}) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden transition-all">
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="px-5 py-4 flex items-center justify-between cursor-pointer hover:bg-slate-50/70 select-none transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-slate-100 text-slate-700">
            {icon}
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-900">{title}</h4>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {statusBadge}
          <button
            type="button"
            className="text-slate-400 hover:text-slate-600 p-1"
            aria-label="Toggle details"
          >
            {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {isOpen && (
        <div className="px-5 py-4 border-t border-slate-100 bg-slate-50/40 text-xs text-slate-700">
          {children}
        </div>
      )}
    </div>
  );
};
