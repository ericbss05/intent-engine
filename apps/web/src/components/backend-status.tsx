"use client";

import { useEffect, useState } from "react";

import { fetchBackendState } from "@/lib/api";
import { parseEnv } from "@/lib/env";

type Status = "loading" | "ok" | "error";

// Appel fait depuis le navigateur (et non depuis le serveur Next) : c'est ce qui
// vérifie aussi que le CORS du backend est bien configuré pour ce front.
export function BackendStatus() {
  const [status, setStatus] = useState<Status>("loading");

  useEffect(() => {
    let cancelled = false;
    let apiBaseUrl: string;
    try {
      apiBaseUrl = parseEnv({
        NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
      }).apiBaseUrl;
    } catch {
      setTimeout(() => !cancelled && setStatus("error"), 0);
      return () => {
        cancelled = true;
      };
    }
    fetchBackendState(apiBaseUrl).then((state) => {
      if (!cancelled) setStatus(state);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const label = {
    loading: "Vérification du service…",
    ok: "OK",
    error: "Service indisponible",
  }[status];

  return (
    <p role="status" data-status={status} className="text-lg">
      État du service : <strong>{label}</strong>
    </p>
  );
}
