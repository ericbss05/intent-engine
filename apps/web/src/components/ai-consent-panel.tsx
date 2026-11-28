"use client";

import { useAuth } from "@clerk/nextjs";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { getConsentTexts, getConsents, setConsent, type ConsentTexts } from "@/lib/preferences-api";

type State =
  | { kind: "loading" }
  | { kind: "error" }
  | { kind: "ready"; granted: boolean; texts: ConsentTexts };

// Le consentement IA se retire aussi facilement qu'il se donne (R12).
export function AiConsentPanel() {
  const { getToken } = useAuth();
  const [state, setState] = useState<State>({ kind: "loading" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const token = await getToken();
      const [consents, texts] = await Promise.all([
        token ? getConsents(token) : Promise.resolve(null),
        getConsentTexts(),
      ]);
      if (cancelled) return;
      if (consents?.ok && texts.ok) {
        const ai = consents.data.consents.find((c) => c.kind === "ai_assist");
        setState({ kind: "ready", granted: ai?.granted ?? false, texts: texts.data });
      } else {
        setState({ kind: "error" });
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [getToken]);

  async function onToggle() {
    if (state.kind !== "ready") return;
    setBusy(true);
    setError(null);
    const token = await getToken();
    const next = !state.granted;
    const result = token
      ? await setConsent(token, "ai_assist", next, state.texts.ai_assist.version)
      : null;
    if (result?.ok) {
      setState({ ...state, granted: next });
    } else {
      setError("La modification a échoué. Rechargez la page puis réessayez.");
    }
    setBusy(false);
  }

  if (state.kind === "loading") return <p role="status">Chargement…</p>;
  if (state.kind === "error") {
    return (
      <p role="alert" className="text-destructive">
        Impossible de charger vos choix pour le moment.
      </p>
    );
  }
  return (
    <section className="flex flex-col gap-2">
      <h2 className="text-lg font-medium">Analyse du CV assistée par IA</h2>
      <p>
        État actuel : <strong>{state.granted ? "activée" : "désactivée (analyse simple)"}</strong>
      </p>
      <Button variant="outline" className="self-start" disabled={busy} onClick={onToggle}>
        {state.granted ? "Retirer mon accord" : "Activer l'analyse assistée par IA"}
      </Button>
      {error && (
        <p role="alert" className="text-sm text-destructive">
          {error}
        </p>
      )}
    </section>
  );
}
