"use client";

import React, { useState, useRef } from "react";
import { UploadCloud, Image as ImageIcon, X, AlertCircle, ShieldAlert, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/Button";

interface DropzoneProps {
  onAnalyze: (file: File, claim?: string) => Promise<void>;
  isLoading?: boolean;
}

export const Dropzone: React.FC<DropzoneProps> = ({ onAnalyze, isLoading = false }) => {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [claim, setClaim] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const MAX_BYTES = 20 * 1024 * 1024; // 20 MiB
  const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"];

  const handleFileSelect = (selectedFile: File) => {
    setError(null);

    if (selectedFile.size > MAX_BYTES) {
      setError("La taille du fichier dépasse la limite autorisée de 20 MiB.");
      return;
    }

    if (!ALLOWED_TYPES.includes(selectedFile.type)) {
      setError("Format non pris en charge. Veuillez utiliser un fichier JPG, JPEG, PNG ou WEBP.");
      return;
    }

    setFile(selectedFile);
    const url = URL.createObjectURL(selectedFile);
    setPreviewUrl(url);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleClear = () => {
    setFile(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    setClaim("");
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    try {
      await onAnalyze(file, claim);
    } catch (err: any) {
      setError(err.message || "Une erreur est survenue lors de l'envoi.");
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      {error && (
        <div className="mb-4 p-3.5 bg-rose-50 border border-rose-200 text-rose-800 rounded-xl text-sm flex items-center gap-2">
          <AlertCircle className="w-5 h-5 shrink-0 text-rose-600" />
          <span>{error}</span>
        </div>
      )}

      {!file ? (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all ${
            isDragging
              ? "border-sky-500 bg-sky-50/50 scale-[1.01]"
              : "border-slate-300 hover:border-slate-400 bg-white hover:bg-slate-50/50 shadow-xs"
          }`}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".jpg,.jpeg,.png,.webp"
            className="hidden"
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                handleFileSelect(e.target.files[0]);
              }
            }}
          />

          <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-sky-50 text-sky-600 flex items-center justify-center">
            <UploadCloud className="w-8 h-8" />
          </div>

          <h3 className="text-lg font-semibold text-slate-900 mb-1">
            Glissez-déposez votre image ici
          </h3>
          <p className="text-sm text-slate-500 mb-5">
            Formats acceptés : <strong>JPG, PNG, WEBP</strong> (jusqu&apos;à 20 MiB)
          </p>

          <Button type="button" variant="primary" size="md">
            Sélectionner une image
          </Button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
          <div className="flex flex-col sm:flex-row gap-5 items-start">
            {/* Preview image */}
            <div className="relative w-full sm:w-48 h-48 bg-slate-100 rounded-xl overflow-hidden border border-slate-200 shrink-0">
              {previewUrl && (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={previewUrl}
                  alt="Aperçu"
                  className="w-full h-full object-cover"
                />
              )}
              <button
                type="button"
                onClick={handleClear}
                className="absolute top-2 right-2 p-1.5 bg-black/60 hover:bg-black/80 text-white rounded-full transition-colors"
                title="Supprimer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* File info and Claim input */}
            <div className="flex-1 w-full space-y-4">
              <div>
                <h4 className="font-semibold text-slate-900 truncate" title={file.name}>
                  {file.name}
                </h4>
                <p className="text-xs text-slate-500 mt-0.5">
                  {(file.size / (1024 * 1024)).toFixed(2)} MiB • {file.type}
                </p>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                  Affirmation ou contexte accompagnant l&apos;image (facultatif)
                </label>
                <textarea
                  value={claim}
                  onChange={(e) => setClaim(e.target.value)}
                  placeholder="Ex : « Cette photo aurait été prise aujourd'hui lors d'une manifestation à Ouagadougou. »"
                  rows={3}
                  className="w-full text-sm rounded-xl border border-slate-300 px-3 py-2 text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent transition-all"
                />
                <p className="text-[11px] text-slate-500 mt-1">
                  Cette affirmation permettra au moteur de rechercher des antériorités Web contradictoires et des fact-checks existants.
                </p>
              </div>

              <div className="pt-2 flex items-center justify-between gap-3">
                <Button
                  type="button"
                  variant="outline"
                  size="md"
                  onClick={handleClear}
                  disabled={isLoading}
                >
                  Changer d&apos;image
                </Button>

                <Button
                  type="submit"
                  variant="primary"
                  size="md"
                  isLoading={isLoading}
                  className="gap-2"
                >
                  <Sparkles className="w-4 h-4" />
                  <span>Analyser cette image</span>
                </Button>
              </div>
            </div>
          </div>
        </form>
      )}

      {/* Privacy Notice */}
      <div className="mt-4 text-center">
        <p className="text-xs text-slate-500 flex items-center justify-center gap-1.5">
          <ShieldAlert className="w-3.5 h-3.5 text-slate-400" />
          <span>
            Le média original est analysé de manière sécurisée et supprimé par défaut après traitement.
          </span>
        </p>
      </div>
    </div>
  );
};
