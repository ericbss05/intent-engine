import { z } from "zod";

import { callParsed, type ApiResult, type Fetch } from "@/lib/http";
import { preferencesPayloadSchema, type PreferencesPayload } from "@/lib/preferences-schema";

const sectorsSchema = z.array(z.object({ id: z.string(), label: z.string() }));
export type Sector = z.infer<typeof sectorsSchema>[number];

const consentTextSchema = z.object({ version: z.string(), title: z.string(), text: z.string() });
const consentTextsSchema = z.object({
  privacy_notice: consentTextSchema,
  ai_assist: consentTextSchema,
});
export type ConsentTexts = z.infer<typeof consentTextsSchema>;
export type ConsentKind = "privacy_notice" | "ai_assist";

const consentsSchema = z.object({
  consents: z.array(
    z.object({
      kind: z.enum(["privacy_notice", "ai_assist"]),
      granted: z.boolean(),
      version_text: z.string().nullable(),
      recorded_at: z.string().nullable(),
      current_version: z.string(),
    }),
  ),
});
export type ConsentsResponse = z.infer<typeof consentsSchema>;

const savedPreferencesSchema = preferencesPayloadSchema.extend({ updated_at: z.string() });

// --- routes publiques (lisibles avant la fin de l'inscription)
export const getSectors = (fetchImpl?: Fetch): Promise<ApiResult<Sector[]>> =>
  callParsed(sectorsSchema, "/reference/sectors", null, {}, fetchImpl);

export const getConsentTexts = (fetchImpl?: Fetch): Promise<ApiResult<ConsentTexts>> =>
  callParsed(consentTextsSchema, "/reference/consent-texts", null, {}, fetchImpl);

// --- routes de l'étudiant connecté
export const getPreferences = (token: string, fetchImpl?: Fetch) =>
  callParsed(savedPreferencesSchema, "/me/preferences", token, {}, fetchImpl);

export const savePreferences = (token: string, payload: PreferencesPayload, fetchImpl?: Fetch) =>
  callParsed(
    savedPreferencesSchema,
    "/me/preferences",
    token,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
    fetchImpl,
  );

export const getConsents = (token: string, fetchImpl?: Fetch) =>
  callParsed(consentsSchema, "/me/consents", token, {}, fetchImpl);

export const setConsent = (
  token: string,
  kind: ConsentKind,
  granted: boolean,
  versionText: string,
  fetchImpl?: Fetch,
) =>
  callParsed(
    consentsSchema,
    `/me/consents/${kind}`,
    token,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ granted, version_text: versionText }),
    },
    fetchImpl,
  );
