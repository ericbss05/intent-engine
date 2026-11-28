"use client";

import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { DeleteAccountButton } from "@/components/delete-account-button";
import { Button } from "@/components/ui/button";
import { exportMyData, getMe, type Me } from "@/lib/account-api";

type State = { kind: "loading" } | { kind: "error" } | { kind: "ready"; me: Me };

export function AccountPanel() {
  const { getToken } = useAuth();
  const router = useRouter();
  const [state, setState] = useState<State>({ kind: "loading" });
  const [exportError, setExportError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const token = await getToken();
      const result = token ? await getMe(token) : null;
      if (cancelled) return;
      if (result?.ok && result.data.adult_confirmed) {
        setState({ kind: "ready", me: result.data });
      } else if (result?.ok || (result && result.status === 404)) {
        // Profil absent ou case 18+ pas encore cochée : on passe par l'étape d'inscription.
        router.replace("/onboarding");
      } else {
        setState({ kind: "error" });
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [getToken, router]);

  async function onExport() {
    setExportError(false);
    const token = await getToken();
    const result = token ? await exportMyData(token) : null;
    if (!result?.ok) {
      setExportError(true);
      return;
    }
    // Téléchargement côté navigateur : le fichier n'est jamais stocké ailleurs.
    const url = URL.createObjectURL(result.data);
    const link = document.createElement("a");
    link.href = url;
    link.download = "mes-donnees.json";
    link.click();
    URL.revokeObjectURL(url);
  }

  if (state.kind === "loading") return <p role="status">Chargement…</p>;
  if (state.kind === "error") {
    return (
      <p role="alert" className="text-destructive">
        Impossible de charger votre compte pour le moment.
      </p>
    );
  }
  return (
    <div className="flex flex-col gap-8">
      <p>
        Compte actif. Analyse du CV assistée par IA :{" "}
        <strong>{state.me.ai_assist_consent ? "activée" : "désactivée"}</strong>.
      </p>
      <section className="flex flex-col gap-2">
        <h2 className="text-lg font-medium">Mes données</h2>
        <p className="text-sm text-muted-foreground">
          Téléchargez toutes les données que nous conservons sur vous (format JSON).
        </p>
        <Button variant="outline" onClick={onExport} className="self-start">
          Exporter mes données
        </Button>
        {exportError && (
          <p role="alert" className="text-sm text-destructive">
            L&apos;export a échoué. Réessayez.
          </p>
        )}
      </section>
      <section className="flex flex-col gap-2">
        <h2 className="text-lg font-medium">Supprimer mon compte</h2>
        <DeleteAccountButton />
      </section>
    </div>
  );
}
