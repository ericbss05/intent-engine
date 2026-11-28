"use client";

import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { DeleteAccountButton } from "@/components/delete-account-button";
import { Button } from "@/components/ui/button";
import { confirmAdult } from "@/lib/account-api";

// Étape « 18 ans minimum » (R13). Si la case n'est pas cochée, rien n'est enregistré :
// on ne consigne jamais qu'une personne est mineure.
export function OnboardingForm() {
  const { getToken } = useAuth();
  const router = useRouter();
  const [checked, setChecked] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!checked) return;
    setBusy(true);
    setError(null);
    const token = await getToken();
    const result = token ? await confirmAdult(token) : null;
    if (result?.ok) {
      router.push("/account");
      return;
    }
    setError("Impossible d'enregistrer votre confirmation. Réessayez.");
    setBusy(false);
  }

  return (
    <div className="flex flex-col gap-6">
      <form onSubmit={onSubmit} className="flex flex-col gap-4">
        <p className="text-muted-foreground">
          Ce service est réservé aux personnes majeures (18 ans ou plus).
        </p>
        <label className="flex items-start gap-2">
          <input
            type="checkbox"
            className="mt-1"
            checked={checked}
            onChange={(e) => setChecked(e.target.checked)}
          />
          <span>Je confirme avoir 18 ans ou plus.</span>
        </label>
        <Button type="submit" disabled={!checked || busy} className="self-start">
          Continuer
        </Button>
        {error && (
          <p role="alert" className="text-sm text-destructive">
            {error}
          </p>
        )}
      </form>
      <section className="flex flex-col gap-2 border-t pt-4">
        <p className="text-sm text-muted-foreground">
          Vous avez moins de 18 ans, ou vous ne souhaitez pas continuer ? Vous pouvez supprimer
          votre compte.
        </p>
        <DeleteAccountButton label="Quitter et supprimer mon compte" />
      </section>
    </div>
  );
}
