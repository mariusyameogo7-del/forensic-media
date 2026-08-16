"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Search,
  Filter,
  Plus,
  Trash2,
  FileText,
  Eye,
  Calendar,
  AlertCircle,
  ImageIcon,
} from "lucide-react";
import { ApiClient } from "@/lib/api-client";
import { AnalysisListItem } from "@/lib/types";
import { ConclusionBadge } from "@/components/analysis/ConclusionBadge";
import { Button } from "@/components/ui/Button";

export default function HistoryPage() {
  const [items, setItems] = useState<AnalysisListItem[]>([]);
  const [search, setSearch] = useState("");
  const [conclusionFilter, setConclusionFilter] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const params: Record<string, any> = {};
      if (search) params.search = search;
      if (conclusionFilter) params.conclusion = conclusionFilter;

      const data = await ApiClient.listAnalyses(params);
      setItems(data.items || []);
    } catch (e) {
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [conclusionFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchHistory();
  };

  const handleDelete = async (analysisId: string) => {
    if (confirm("Confirmer la suppression de cette analyse et de ses fichiers associés ?")) {
      await ApiClient.deleteAnalysis(analysisId);
      setItems((prev) => prev.filter((i) => i.analysis_id !== analysisId));
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            Historique des analyses
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Retrouvez et gérez l&apos;ensemble de vos vérifications médias.
          </p>
        </div>

        <Link href="/">
          <Button variant="primary" className="gap-2">
            <Plus className="w-4 h-4" />
            <span>Nouvelle analyse</span>
          </Button>
        </Link>
      </div>

      {/* Filters Bar */}
      <div className="p-4 bg-white border border-slate-200 rounded-xl shadow-xs flex flex-col sm:flex-row gap-3 items-center justify-between">
        <form onSubmit={handleSearchSubmit} className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Nom de fichier, AN-2026-..., mot-clé"
            className="w-full pl-9 pr-3 py-1.5 text-xs rounded-lg border border-slate-300 text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500"
          />
        </form>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-400 shrink-0" />
          <select
            value={conclusionFilter}
            onChange={(e) => setConclusionFilter(e.target.value)}
            className="text-xs rounded-lg border border-slate-300 py-1.5 px-2.5 text-slate-700 focus:outline-none focus:ring-2 focus:ring-sky-500"
          >
            <option value="">Toutes les conclusions</option>
            <option value="no_major_alert">Aucune alerte majeure</option>
            <option value="review_recommended">Vérification recommandée</option>
            <option value="important_attention">Attention importante</option>
          </select>
        </div>
      </div>

      {/* List */}
      {loading ? (
        <div className="py-12 text-center text-slate-500 text-sm">
          Chargement de l&apos;historique...
        </div>
      ) : items.length === 0 ? (
        <div className="py-16 text-center bg-white border border-slate-200 rounded-2xl p-8 shadow-xs">
          <ImageIcon className="w-10 h-10 text-slate-300 mx-auto mb-3" />
          <h3 className="font-semibold text-slate-800 text-base">Aucune analyse trouvée</h3>
          <p className="text-xs text-slate-500 mt-1 mb-5">
            Lancez votre première analyse d&apos;image pour commencer à vérifier vos médias.
          </p>
          <Link href="/">
            <Button variant="primary">Vérifier une image</Button>
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <div
              key={item.analysis_id}
              className="p-5 bg-white border border-slate-200 rounded-xl hover:border-slate-300 transition-all shadow-2xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
            >
              <div className="space-y-1.5 flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-semibold text-sky-700 bg-sky-50 px-2 py-0.5 rounded border border-sky-200">
                    {item.public_id}
                  </span>
                  <span className="font-semibold text-sm text-slate-900 truncate">
                    {item.original_filename}
                  </span>
                  {!item.has_original_file && (
                    <span className="text-[10px] text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded">
                      Original supprimé
                    </span>
                  )}
                </div>

                {item.claim_preview && (
                  <p className="text-xs text-slate-600 italic truncate max-w-md">
                    « {item.claim_preview} »
                  </p>
                )}

                <div className="flex items-center gap-3 text-xs text-slate-400">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5" />
                    {new Date(item.created_at).toLocaleDateString("fr-FR", {
                      day: "numeric",
                      month: "short",
                      year: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                  <span>•</span>
                  <span>{(item.file_size / 1024).toFixed(1)} KB</span>
                </div>
              </div>

              <div className="flex items-center gap-3 w-full sm:w-auto justify-between sm:justify-end">
                <ConclusionBadge level={item.conclusion_level} size="sm" />

                <div className="flex items-center gap-1.5">
                  <Link href={`/analyse/${item.analysis_id}/resultat`}>
                    <Button variant="outline" size="sm" title="Voir l'analyse">
                      <Eye className="w-4 h-4" />
                    </Button>
                  </Link>
                  <Link href={`/analyse/${item.analysis_id}/rapport`}>
                    <Button variant="outline" size="sm" title="Rapport">
                      <FileText className="w-4 h-4" />
                    </Button>
                  </Link>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(item.analysis_id)}
                    className="text-rose-600 hover:bg-rose-50"
                    title="Supprimer"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
