import { z } from "zod";

import { parseEnv } from "@/lib/env";

export type ApiResult<T> = { ok: true; data: T } | { ok: false; status: number; code: string };
export type Fetch = typeof fetch;
type Failure = { ok: false; status: number; code: string };

const errorSchema = z.object({ code: z.string() });

export function apiBaseUrl(): string {
  return parseEnv({ NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL }).apiBaseUrl;
}

// `token` absent = route publique (textes d'information, liste de secteurs).
export async function call(
  path: string,
  token: string | null,
  init: RequestInit = {},
  fetchImpl: Fetch = fetch,
): Promise<Response | { networkError: true }> {
  try {
    const headers: Record<string, string> = { ...(init.headers as Record<string, string>) };
    // Le jeton Clerk prouve l'identité ; le backend le vérifie à chaque requête.
    if (token) headers.Authorization = `Bearer ${token}`;
    return await fetchImpl(`${apiBaseUrl()}${path}`, { ...init, cache: "no-store", headers });
  } catch {
    return { networkError: true };
  }
}

export async function toFailure(response: Response | { networkError: true }): Promise<Failure> {
  if ("networkError" in response) return { ok: false, status: 0, code: "network_error" };
  let code = `http_${response.status}`;
  try {
    const parsed = errorSchema.safeParse(await response.json());
    if (parsed.success) code = parsed.data.code;
  } catch {
    // corps vide ou non JSON : on garde le code générique
  }
  return { ok: false, status: response.status, code };
}

// Appelle, vérifie le statut puis valide la forme de la réponse avec Zod.
export async function callParsed<T>(
  schema: z.ZodType<T>,
  path: string,
  token: string | null,
  init?: RequestInit,
  fetchImpl?: Fetch,
): Promise<ApiResult<T>> {
  const response = await call(path, token, init, fetchImpl);
  if ("networkError" in response || !response.ok) return toFailure(response);
  const parsed = schema.safeParse(await response.json().catch(() => null));
  if (!parsed.success) return { ok: false, status: response.status, code: "invalid_response" };
  return { ok: true, data: parsed.data };
}
