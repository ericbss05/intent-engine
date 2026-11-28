import { z } from "zod";

import { call, toFailure, type ApiResult, type Fetch } from "@/lib/http";

// Forme de GET /me. Toute autre réponse est traitée comme une erreur, pas comme un crash.
const meSchema = z.object({
  adult_confirmed: z.boolean(),
  ai_assist_consent: z.boolean(),
  created_at: z.string(),
  is_admin: z.boolean(),
});
export type Me = z.infer<typeof meSchema>;

export type { ApiResult };

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
