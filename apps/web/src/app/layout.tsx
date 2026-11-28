import { ClerkProvider } from "@clerk/nextjs";
import { frFR } from "@clerk/localizations";
import type { Metadata } from "next";
import { Suspense } from "react";
import { Geist, Geist_Mono } from "next/font/google";
import { SiteHeader } from "@/components/site-header";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "stage-finder",
  description: "Aide à la recherche de stage et d'alternance",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <ClerkProvider
      localization={frFR}
      signInUrl="/sign-in"
      signUpUrl="/sign-up"
      signInFallbackRedirectUrl="/account"
    >
      <html lang="fr" className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}>
        <body className="min-h-full flex flex-col">
          {/* L'en-tête lit la session (donnée dynamique) : avec cacheComponents, elle doit être
              dans un Suspense, sinon Next.js ne peut pas pré-rendre le reste de la page. */}
          <Suspense fallback={<div className="h-14" />}>
            <SiteHeader />
          </Suspense>
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}
