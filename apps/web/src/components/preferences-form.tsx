"use client";

import { useAuth } from "@clerk/nextjs";
import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { getPreferences, getSectors, savePreferences, type Sector } from "@/lib/preferences-api";
import {
  COMPANY_SIZES,
  CONTRACT_TYPES,
  DEFAULT_FORM_VALUES,
  PRIORITIES,
  RADIUS_OPTIONS,
  fromPayload,
  preferencesFormSchema,
  toPayload,
  type PreferencesFormValues,
} from "@/lib/preferences-schema";

type Load = "loading" | "ready" | "error";
type Save = "idle" | "saving" | "saved" | "error";

const inputClass = "w-full rounded-lg border border-input bg-background px-2.5 py-1.5 text-sm";

function FieldError({ message }: { message?: string }) {
  if (!message) return null;
  return (
    <p role="alert" className="text-sm text-destructive">
      {message}
    </p>
  );
}

export function PreferencesForm() {
  const { getToken } = useAuth();
  const [load, setLoad] = useState<Load>("loading");
  const [save, setSave] = useState<Save>("idle");
  const [sectors, setSectors] = useState<Sector[]>([]);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<PreferencesFormValues>({
    resolver: zodResolver(preferencesFormSchema),
    defaultValues: DEFAULT_FORM_VALUES,
  });

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const token = await getToken();
      const [sectorsResult, prefsResult] = await Promise.all([
        getSectors(),
        token ? getPreferences(token) : Promise.resolve(null),
      ]);
      if (cancelled) return;
      if (!sectorsResult.ok) return setLoad("error");
      setSectors(sectorsResult.data);
      if (prefsResult?.ok) {
        reset(fromPayload(prefsResult.data));
        setLoad("ready");
      } else if (prefsResult && prefsResult.status === 404) {
        setLoad("ready"); // première fois : formulaire vide
      } else {
        setLoad("error");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [getToken, reset]);

  async function onSubmit(values: PreferencesFormValues) {
    setSave("saving");
    const token = await getToken();
    const result = token ? await savePreferences(token, toPayload(values)) : null;
    setSave(result?.ok ? "saved" : "error");
  }

  if (load === "loading") return <p role="status">Chargement…</p>;
  if (load === "error") {
    return (
      <p role="alert" className="text-destructive">
        Impossible de charger le questionnaire pour le moment.
      </p>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-6" noValidate>
      <fieldset className="flex flex-col gap-2">
        <legend className="font-medium">Type de contrat</legend>
        <div className="flex gap-4">
          {CONTRACT_TYPES.map((c) => (
            <label key={c.value} className="flex items-center gap-2">
              <input type="radio" value={c.value} {...register("contract_type")} />
              {c.label}
            </label>
          ))}
        </div>
        <FieldError message={errors.contract_type?.message} />
      </fieldset>

      <div className="flex flex-col gap-1">
        <label htmlFor="duration" className="font-medium">
          Durée (en mois)
        </label>
        <input
          id="duration"
          inputMode="numeric"
          className={inputClass}
          {...register("duration_months")}
        />
        <FieldError message={errors.duration_months?.message} />
      </div>

      <div className="flex flex-col gap-1">
        <label htmlFor="role" className="font-medium">
          Métier visé
        </label>
        <input
          id="role"
          className={inputClass}
          placeholder="Ex. analyste financier"
          {...register("target_role")}
        />
        <FieldError message={errors.target_role?.message} />
      </div>

      <fieldset className="flex flex-col gap-2">
        <legend className="font-medium">Secteurs (10 maximum)</legend>
        <div className="grid gap-1 sm:grid-cols-2">
          {sectors.map((s) => (
            <label key={s.id} className="flex items-start gap-2 text-sm">
              <input type="checkbox" value={s.id} className="mt-1" {...register("sectors")} />
              {s.label}
            </label>
          ))}
        </div>
        <FieldError message={errors.sectors?.message} />
      </fieldset>

      <fieldset className="flex flex-col gap-2">
        <legend className="font-medium">Zone de recherche</legend>
        <div className="flex flex-wrap items-end gap-4">
          <div className="flex flex-col gap-1">
            <label htmlFor="location" className="text-sm">
              Code postal ou département
            </label>
            <input
              id="location"
              className={inputClass}
              placeholder="75011 ou 75"
              {...register("zone_location")}
            />
          </div>
          <div className="flex flex-col gap-1">
            <label htmlFor="radius" className="text-sm">
              Rayon
            </label>
            <select id="radius" className={inputClass} {...register("zone_radius_km")}>
              {RADIUS_OPTIONS.map((r) => (
                <option key={r} value={r}>
                  {r === 0 ? "Cette zone seulement" : `${r} km`}
                </option>
              ))}
            </select>
          </div>
        </div>
        <FieldError message={errors.zone_location?.message ?? errors.zone_radius_km?.message} />
      </fieldset>

      <fieldset className="flex flex-col gap-2">
        <legend className="font-medium">Taille d&apos;entreprise</legend>
        {COMPANY_SIZES.map((c) => (
          <label key={c.value} className="flex items-center gap-2 text-sm">
            <input type="checkbox" value={c.value} {...register("company_size")} />
            {c.label}
          </label>
        ))}
        <FieldError message={errors.company_size?.message} />
      </fieldset>

      <fieldset className="flex flex-col gap-2">
        <legend className="font-medium">Ce qui compte le plus (facultatif)</legend>
        {PRIORITIES.map((p) => (
          <label key={p.value} className="flex items-center gap-2 text-sm">
            <input type="checkbox" value={p.value} {...register("priorities")} />
            {p.label}
          </label>
        ))}
        <FieldError message={errors.priorities?.message} />
      </fieldset>

      <div className="flex flex-col gap-1">
        <label htmlFor="excluded" className="font-medium">
          Entreprises déjà contactées (facultatif)
        </label>
        <p className="text-sm text-muted-foreground">
          Un numéro SIREN (9 chiffres) par ligne : ces entreprises ne vous seront pas proposées.
        </p>
        <textarea
          id="excluded"
          rows={3}
          className={inputClass}
          {...register("excluded_sirens_text")}
        />
        <FieldError message={errors.excluded_sirens_text?.message} />
      </div>

      <div className="flex items-center gap-4">
        <Button type="submit" disabled={save === "saving"}>
          Enregistrer
        </Button>
        <Link href="/account" className="text-sm underline">
          Retour à mon compte
        </Link>
      </div>
      {save === "saved" && <p role="status">Préférences enregistrées.</p>}
      {save === "error" && (
        <p role="alert" className="text-destructive">
          L&apos;enregistrement a échoué. Vérifiez le formulaire puis réessayez.
        </p>
      )}
    </form>
  );
}
