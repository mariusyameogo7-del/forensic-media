"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { ShieldCheck, History, User, LogIn } from "lucide-react";

export const Header: React.FC = () => {
  const [hasAuth, setHasAuth] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      setHasAuth(Boolean(localStorage.getItem("auth_token")));
    }
  }, []);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200 bg-white/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-sky-700 flex items-center justify-center text-white shadow-xs">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <span className="font-bold text-slate-900 text-lg tracking-tight block leading-none">
              Forensic Media
            </span>
            <span className="text-[10px] text-slate-500 font-medium tracking-wide uppercase">
              Vérification Numérique
            </span>
          </div>
        </Link>

        <nav className="flex items-center space-x-2 sm:space-x-4">
          <Link
            href="/"
            className="text-sm font-medium text-slate-600 hover:text-sky-600 px-3 py-2 rounded-md transition-colors"
          >
            Analyser
          </Link>
          <Link
            href="/historique"
            className="text-sm font-medium text-slate-600 hover:text-sky-600 px-3 py-2 rounded-md transition-colors flex items-center gap-1.5"
          >
            <History className="w-4 h-4" />
            <span className="hidden sm:inline">Historique</span>
          </Link>

          {hasAuth ? (
            <Link
              href="/compte"
              className="text-sm font-medium text-slate-700 hover:bg-slate-100 px-3 py-2 rounded-lg border border-slate-200 flex items-center gap-1.5"
            >
              <User className="w-4 h-4" />
              <span>Mon Compte</span>
            </Link>
          ) : (
            <Link
              href="/connexion"
              className="text-sm font-medium text-white bg-slate-900 hover:bg-slate-800 px-3.5 py-1.5 rounded-lg shadow-xs flex items-center gap-1.5 transition-colors"
            >
              <LogIn className="w-4 h-4" />
              <span>Connexion</span>
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
};
