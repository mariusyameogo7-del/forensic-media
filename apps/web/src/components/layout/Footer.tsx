import React from "react";

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-slate-200 bg-white py-8 mt-16 text-slate-500 text-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <p className="font-semibold text-slate-700">
            Plateforme africaine de vérification numérique
          </p>
          <p className="mt-1">
            Analyse de provenance, intégrité, métadonnées et contexte médiatique.
          </p>
        </div>
        <div className="text-right">
          <p>Privacy-first — Suppression automatique des médias originaux.</p>
          <p className="mt-0.5 text-slate-400">
            © {new Date().getFullYear()} Forensic Media. Tous droits réservés.
          </p>
        </div>
      </div>
    </footer>
  );
};
