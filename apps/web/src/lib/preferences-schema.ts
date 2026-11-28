import { z } from "zod";

// Valeurs autorisées : DOIVENT rester identiques à apps/api/app/domain/schemas.py.
// Le backend revalide tout (le front n'est qu'un confort pour l'étudiant).
export const CONTRACT_TYPES = [
  { value: "stage", label: "Stage" },
  { value: "alternance", label: "Alternance" },
] as const;

export const COMPANY_SIZES = [
  { value: "1-9", label: "1 à 9 salariés" },
  { value: "10-49", label: "10 à 49 salariés" },
  { value: "50-249", label: "50 à 249 salariés" },
  { value: "250-999", label: "250 à 999 salariés" },
  { value: "1000+", label: "1 000 salariés et plus" },
] as const;

export const PRIORITIES = [
  { value: "sector", label: "Le secteur" },
  { value: "distance", label: "La proximité" },
  { value: "company_size", label: "La taille de l'entreprise" },
] as const;

export const RADIUS_OPTIONS = [0, 10, 20, 30, 50, 100, 200] as const;

const POSTCODE = /^\d{5}$/;
const DEPARTMENT = /^(0[1-9]|[1-8]\d|9[0-5]|2A|2B|97[1-6]|98[4-9])$/;

export function parseSirens(text: string): string[] {
  return text
    .split(/[\n,;]+/)
    .map((line) => line.replace(/\s+/g, ""))
    .filter((line) => line.length > 0);
}

// Valeurs du formulaire (tout est du texte ou des listes de textes, comme dans le navigateur).
export const preferencesFormSchema = z.object({
  contract_type: z.enum(["stage", "alternance"], { error: "Choisissez stage ou alternance." }),
  duration_months: z
    .string()
    .regex(/^\d+$/, "Indiquez un nombre de mois.")
    .refine((v) => Number(v) >= 1 && Number(v) <= 36, "La durée doit être entre 1 et 36 mois."),
  target_role: z
    .string()
    .trim()
    .min(2, "Indiquez le métier visé (2 caractères minimum).")
    .max(100, "100 caractères maximum."),
  sectors: z
    .array(z.string())
    .min(1, "Choisissez au moins un secteur.")
    .max(10, "10 secteurs maximum."),
  zone_location: z
    .string()
    .trim()
    .toUpperCase()
    .refine(
      (v) => POSTCODE.test(v) || DEPARTMENT.test(v),
      "Indiquez un code postal (5 chiffres) ou un département (ex. 75, 2A, 971).",
    ),
  zone_radius_km: z.string().regex(/^\d+$/, "Choisissez un rayon."),
  company_size: z.array(z.string()).min(1, "Choisissez au moins une taille d'entreprise."),
  priorities: z.array(z.string()).max(3, "3 priorités maximum."),
  excluded_sirens_text: z.string().superRefine((text, ctx) => {
    const sirens = parseSirens(text);
    if (sirens.length > 200) ctx.addIssue({ code: "custom", message: "200 numéros maximum." });
    if (sirens.some((s) => !/^\d{9}$/.test(s)))
      ctx.addIssue({ code: "custom", message: "Chaque SIREN doit comporter 9 chiffres." });
    if (new Set(sirens).size !== sirens.length)
      ctx.addIssue({ code: "custom", message: "Un SIREN apparaît deux fois." });
  }),
});
export type PreferencesFormValues = z.infer<typeof preferencesFormSchema>;

export const DEFAULT_FORM_VALUES: PreferencesFormValues = {
  contract_type: "stage",
  duration_months: "6",
  target_role: "",
  sectors: [],
  zone_location: "",
  zone_radius_km: "30",
  company_size: [],
  priorities: [],
  excluded_sirens_text: "",
};

// Forme exacte attendue par PUT /me/preferences.
export const preferencesPayloadSchema = z.object({
  contract_type: z.enum(["stage", "alternance"]),
  duration_months: z.number().int().min(1).max(36),
  target_role: z.string(),
  sectors: z.array(z.string()),
  zone: z.object({ location: z.string(), radius_km: z.number().int().min(0).max(200) }),
  company_size: z.array(z.string()),
  priorities: z.array(z.string()),
  excluded_sirens: z.array(z.string()),
});
export type PreferencesPayload = z.infer<typeof preferencesPayloadSchema>;

export function toPayload(values: PreferencesFormValues): PreferencesPayload {
  return {
    contract_type: values.contract_type,
    duration_months: Number(values.duration_months),
    target_role: values.target_role.trim(),
    sectors: values.sectors,
    zone: {
      location: values.zone_location.trim().toUpperCase(),
      radius_km: Number(values.zone_radius_km),
    },
    company_size: values.company_size,
    priorities: values.priorities,
    excluded_sirens: parseSirens(values.excluded_sirens_text),
  };
}

export function fromPayload(payload: PreferencesPayload): PreferencesFormValues {
  return {
    contract_type: payload.contract_type,
    duration_months: String(payload.duration_months),
    target_role: payload.target_role,
    sectors: payload.sectors,
    zone_location: payload.zone.location,
    zone_radius_km: String(payload.zone.radius_km),
    company_size: payload.company_size,
    priorities: payload.priorities,
    excluded_sirens_text: payload.excluded_sirens.join("\n"),
  };
}
