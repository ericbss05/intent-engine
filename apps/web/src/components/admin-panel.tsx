"use client";

import { useAuth } from "@clerk/nextjs";
import { useEffect, useState } from "react";

import { getAdminStatus } from "@/lib/account-api";

type State = "loading" | "allowed" | "denied" | "error";

// Ce composant n'a AUCUN pouvoir : il affiche ce que le backend décide (200 ou 403).
export function AdminPanel() {
  const { getToken } = useAuth();
  const [state, setState] = useState<State>("loading");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const token = await getToken();
      const result = token ? await getAdminStatus(token) : null;
      if (cancelled) return;
      if (result?.ok) setState("allowed");
      else if (result && result.status === 403) setState("denied");
      else setState("error");
    })();
    return () => {
      cancelled = true;
    };
  }, [getToken]);

  if (state === "loading") return <p role="status">Chargement…</p>;
  if (state === "denied")
    return <p role="alert">Accès refusé : espace réservé aux administrateurs.</p>;
  if (state === "error") return <p role="alert">Service indisponible.</p>;
  return <p>Espace d&apos;administration (vide pour l&apos;instant).</p>;
}
