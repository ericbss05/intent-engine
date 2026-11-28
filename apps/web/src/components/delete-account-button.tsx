"use client";

import { useAuth, useClerk } from "@clerk/nextjs";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { deleteMyAccount } from "@/lib/account-api";

// Deux clics volontaires : la suppression est définitive.
export function DeleteAccountButton({ label = "Supprimer mon compte" }: { label?: string }) {
  const { getToken } = useAuth();
  const { signOut } = useClerk();
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onConfirm() {
    setBusy(true);
    setError(null);
    const token = await getToken();
    if (!token) {
      setError("Session expirée. Reconnectez-vous puis réessayez.");
      setBusy(false);
      return;
    }
    const result = await deleteMyAccount(token);
    if (result.ok) {
      await signOut({ redirectUrl: "/" });
      return;
    }
    // 502 : nos données sont déjà effacées mais la suppression du compte doit être relancée.
    setError(
      result.code === "identity_deletion_failed"
        ? "Vos données sont supprimées, mais la fermeture du compte a échoué. Réessayez."
        : "La suppression a échoué. Réessayez dans un instant.",
    );
    setBusy(false);
  }

  if (!confirming) {
    return (
      <Button variant="destructive" onClick={() => setConfirming(true)}>
        {label}
      </Button>
    );
  }
  return (
    <div className="flex flex-col gap-2" role="alertdialog" aria-label="Confirmer la suppression">
      <p className="text-sm">
        Cette action supprime définitivement votre compte et toutes vos données. Elle est
        irréversible.
      </p>
      <div className="flex gap-2">
        <Button variant="destructive" disabled={busy} onClick={onConfirm}>
          Oui, tout supprimer
        </Button>
        <Button variant="outline" disabled={busy} onClick={() => setConfirming(false)}>
          Annuler
        </Button>
      </div>
      {error && (
        <p role="alert" className="text-sm text-destructive">
          {error}
        </p>
      )}
    </div>
  );
}
