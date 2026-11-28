"use client";

import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { DeleteAccountButton } from "@/components/delete-account-button";
import { Button } from "@/components/ui/button";
import { confirmAdult } from "@/lib/account-api";
import { getConsentTexts, setConsent, type ConsentTexts } from "@/lib/preferences-api";

type Step = "info" | "adult" | "ai";

// Parcours : 1) information RGPD → 2) 18 ans minimum → 3) choix IA (décoché par défaut).
// Rien n'est envoyé au serveur avant la dernière étape ; si la case 18+ n'est pas cochée,
// rien n'est jamais enregistré (on ne consigne pas qu'une personne est mineure).
export function OnboardingFlow() {
  const { getToken } = useAuth();
  const router = useRouter();
  const [texts, setTexts] = useState<ConsentTexts | null>(null);
  const [loadError, setLoadError] = useState(false);
  const [step, setStep] = useState<Step>("info");
  const [adult, setAdult] = useState(false);
  const [aiChoice, setAiChoice] = useState(false); // décoché par défaut (R12)
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getConsentTexts().then((result) => {
      if (cancelled) return;
      if (result.ok) setTexts(result.data);
      else setLoadError(true);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  async function onFinish() {
    if (!texts || !adult) return;
    setBusy(true);
    setError(null);
    const token = await getToken();
    if (!token) {
      setError("Session expirée. Reconnectez-vous puis réessayez.");
      setBusy(false);
      return;
    }
    // Chaque appel est idempotent : en cas d'échec au milieu, on peut simplement réessayer.
    const adultResult = await confirmAdult(token);
    const noticeResult = adultResult.ok
      ? await setConsent(token, "privacy_notice", true, texts.privacy_notice.version)
      : null;
    const aiResult =
      noticeResult?.ok && aiChoice
        ? await setConsent(token, "ai_assist", true, texts.ai_assist.version)
        : noticeResult;
    if (aiResult?.ok) {
      router.push("/preferences");
      return;
    }
    setError("Impossible d'enregistrer vos choix. Réessayez.");
    setBusy(false);
  }

  if (loadError) {
    return (
      <p role="alert" className="text-destructive">
        Impossible de charger les informations. Réessayez dans un instant.
      </p>
    );
  }
  if (!texts) return <p role="status">Chargement…</p>;

  return (
    <div className="flex flex-col gap-6">
      {step === "info" && (
        <section className="flex flex-col gap-4" aria-label="Information sur vos données">
          <h2 className="text-lg font-medium">{texts.privacy_notice.title}</h2>
          <p className="whitespace-pre-line text-sm">{texts.privacy_notice.text}</p>
          <Button className="self-start" onClick={() => setStep("adult")}>
            J&apos;ai lu cette information
          </Button>
        </section>
      )}

      {step === "adult" && (
        <section className="flex flex-col gap-4" aria-label="Majorité">
          <p className="text-muted-foreground">
            Ce service est réservé aux personnes majeures (18 ans ou plus).
          </p>
          <label className="flex items-start gap-2">
            <input
              type="checkbox"
              className="mt-1"
              checked={adult}
              onChange={(e) => setAdult(e.target.checked)}
            />
            <span>Je confirme avoir 18 ans ou plus.</span>
          </label>
          <Button className="self-start" disabled={!adult} onClick={() => setStep("ai")}>
            Continuer
          </Button>
          <div className="flex flex-col gap-2 border-t pt-4">
            <p className="text-sm text-muted-foreground">
              Vous avez moins de 18 ans, ou vous ne souhaitez pas continuer ? Vous pouvez supprimer
              votre compte.
            </p>
            <DeleteAccountButton label="Quitter et supprimer mon compte" />
          </div>
        </section>
      )}

      {step === "ai" && (
        <section className="flex flex-col gap-4" aria-label="Choix de l'analyse du CV">
          <h2 className="text-lg font-medium">{texts.ai_assist.title}</h2>
          <p className="whitespace-pre-line text-sm">{texts.ai_assist.text}</p>
          <label className="flex items-start gap-2">
            <input
              type="checkbox"
              className="mt-1"
              checked={aiChoice}
              onChange={(e) => setAiChoice(e.target.checked)}
            />
            <span>J&apos;accepte l&apos;analyse de mon CV assistée par IA (facultatif).</span>
          </label>
          <Button className="self-start" disabled={busy} onClick={onFinish}>
            Terminer
          </Button>
          {error && (
            <p role="alert" className="text-sm text-destructive">
              {error}
            </p>
          )}
        </section>
      )}
    </div>
  );
}
