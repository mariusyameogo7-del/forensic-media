import type { Metadata } from "next";
import "@/styles/globals.css";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";

export const metadata: Metadata = {
  title: "Forensic Media — Plateforme africaine de vérification numérique",
  description:
    "Analysez l'origine, l'intégrité et le contexte d'un média numérique avant de lui faire confiance.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr" className="h-full bg-slate-50">
      <body className="flex flex-col min-h-full font-sans antialiased text-slate-900 bg-slate-50">
        <Header />
        <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}
