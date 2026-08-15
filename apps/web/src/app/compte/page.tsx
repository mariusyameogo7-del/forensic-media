"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { User as UserIcon, Shield, Lock, LogOut, Check } from "lucide-react";
import { Button } from "@/components/ui/Button";

export default function AccountPage() {
  const router = useRouter();
  const [profile, setProfile] = useState<any>(null);
  const [retainHistory, setRetainHistory] = useState(true);
  const [retainFiles, setRetainFiles] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("auth_token");
    if (!token) {
      router.push("/connexion");
      return;
    }

    // Mock fetch preferences
    setProfile({ email: "utilisateur@forensic-media.org", account_type: "Standard" });
  }, [router]);

  const handleSavePreferences = async () => {
    setSaving(true);
    setTimeout(() => {
      setSaving(false);
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    }, 400);
  };

  const handleLogout = () => {
    localStorage.removeItem("auth_token");
    router.push("/");
  };

  return (
    <div className="max-w-3xl mx-auto py-8 space-y-6">
      <div className="flex items-center justify-between border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Mon Compte</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Gérez vos informations de compte et vos préférences de confidentialité.
          </p>
        </div>

        <Button variant="outline" size="sm" onClick={handleLogout} className="gap-1.5 text-rose-600">
          <LogOut className="w-4 h-4" />
          <span>Déconnexion</span>
        </Button>
      </div>

      {/* Account Info */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-sky-50 text-sky-700">
            <UserIcon className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900 text-sm">Informations de profil</h3>
            <p className="text-xs text-slate-500">{profile?.email || "Chargement..."}</p>
          </div>
        </div>
      </div>

      {/* Privacy & Retention Settings */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-6">
        <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
          <div className="p-2.5 rounded-xl bg-emerald-50 text-emerald-700">
            <Shield className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900 text-sm">Politique de rétention et vie privée</h3>
            <p className="text-xs text-slate-500">
              Contrôlez la conservation de vos médias et résultats d&apos;analyse.
            </p>
          </div>
        </div>

        <div className="space-y-4">
          <label className="flex items-start gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={retainHistory}
              onChange={(e) => setRetainHistory(e.target.checked)}
              className="mt-1 rounded border-slate-300 text-sky-600 focus:ring-sky-500"
            />
            <div>
              <span className="text-sm font-semibold text-slate-900 block">
                Conserver l&apos;historique de mes analyses
              </span>
              <span className="text-xs text-slate-500 block mt-0.5">
                Permet de retrouver vos rapports et synthèses passées dans l&apos;onglet Historique.
              </span>
            </div>
          </label>

          <label className="flex items-start gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={retainFiles}
              onChange={(e) => setRetainFiles(e.target.checked)}
              className="mt-1 rounded border-slate-300 text-sky-600 focus:ring-sky-500"
            />
            <div>
              <span className="text-sm font-semibold text-slate-900 block">
                Conserver les fichiers images originaux
              </span>
              <span className="text-xs text-slate-500 block mt-0.5">
                Par défaut désactivé (Privacy-first). Si désactivé, le fichier original et les aperçus sont supprimés du stockage dès la fin de l&apos;analyse.
              </span>
            </div>
          </label>
        </div>

        <div className="pt-2 flex items-center justify-between">
          <Button variant="primary" onClick={handleSavePreferences} isLoading={saving} className="gap-2">
            <span>Enregistrer les préférences</span>
          </Button>

          {saved && (
            <span className="text-xs font-semibold text-emerald-600 flex items-center gap-1">
              <Check className="w-4 h-4" />
              <span>Préférences enregistrées !</span>
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
