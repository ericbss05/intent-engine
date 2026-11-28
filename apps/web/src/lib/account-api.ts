import { z } from "zod";

import { parseEnv } from "@/lib/env";

// Forme de GET /me. Toute autre réponse est traitée comme une erreur, pas comme un crash.
const meSchema = z.object({
  adult_confirmed: z.boolean(),
  ai_assist_consent: z.boolean(),
  created_at: z.string(),
  is_admin: z.boolean(),
});
export type Me = z.infer<typeof meSchema>;

const errorSchema = z.object({ code: z.string() });

export type ApiResult<T> = { ok: true; data: T } | { ok: false; status: number; code: string };

type Fetch = typeof fetch;

function apiBaseUrl(): string {
  return parseEnv({ NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL }).apiBaseUrl;
}

async function call(
  path: string,
  token: string,
  init: RequestInit = {},
  fetchImpl: Fetch = fetch,
): Promise<Response | { networkError: true }> {
  try {
    return await fetchImpl(`${apiBaseUrl()}${path}`, {
      ...init,
      cache: "no-store",
      // Le jeton Clerk prouve l'identité ; le backend le vérifie à chaque requête.
      headers: { ...init.headers, Authorization: `Bearer ${token}` },
    });
  } catch {
    return { networkError: true };
  }
}

async function toFailure(response: Response | { networkError: true }) {
  if ("networkError" in response) return { ok: false as const, status: 0, code: "network_error" };
  let code = `http_${response.status}`;
  try {
    const parsed = errorSchema.safeParse(await response.json());
    if (parsed.success) code = parsed.data.code;
  } catch {
    // corps vide ou non JSON : on garde le code générique
  }
  return { ok: false as const, status: response.status, code };
}

export async function getMe(token: string, fetchImpl?: Fetch): Promise<ApiResult<Me>> {
  const response = await call("/me", token, {}, fetchImpl);
  if ("networkError" in response || !response.ok) return toFailure(response);
  const parsed = meSchema.safeParse(await response.json().catch(() => null));
  if (!parsed.success) return { ok: false, status: response.status, code: "invalid_response" };
  return { ok: true, data: parsed.data };
}

export async function confirmAdult(token: string, fetchImpl?: Fetch): Promise<ApiResult<Me>> {
  const response = await call(
    "/me/adult-confirmation",
    token,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ confirmed: true }),
    },
    fetchImpl,
  );
  if ("networkError" in response || !response.ok) return toFailure(response);
  const parsed = meSchema.safeParse(await response.json().catch(() => null));
  if (!parsed.success) return { ok: false, status: response.status, code: "invalid_response" };
  return { ok: true, data: parsed.data };
}

export async function exportMyData(token: string, fetchImpl?: Fetch): Promise<ApiResult<Blob>> {
  const response = await call("/me/export", token, {}, fetchImpl);
  if ("networkError" in response || !response.ok) return toFailure(response);
  return { ok: true, data: await response.blob() };
}

export async function deleteMyAccount(token: string, fetchImpl?: Fetch): Promise<ApiResult<null>> {
  const response = await call("/me", token, { method: "DELETE" }, fetchImpl);
  if ("networkError" in response || !response.ok) return toFailure(response);
  return { ok: true, data: null };
}

const adminSchema = z.object({ status: z.literal("ok") });

// Le front ne décide PAS qui est admin : il demande au backend, qui répond 200 ou 403.
export async function getAdminStatus(token: string, fetchImpl?: Fetch): Promise<ApiResult<null>> {
  const response = await call("/admin/status", token, {}, fetchImpl);
  if ("networkError" in response || !response.ok) return toFailure(response);
  const parsed = adminSchema.safeParse(await response.json().catch(() => null));
  if (!parsed.success) return { ok: false, status: response.status, code: "invalid_response" };
  return { ok: true, data: null };
}
