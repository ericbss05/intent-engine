import { z } from "zod";

// Ce que le backend doit répondre. Toute autre forme = erreur gérée, pas un crash.
const healthSchema = z.object({ status: z.literal("ok") });

export type BackendState = "ok" | "error";

export async function fetchBackendState(
  apiBaseUrl: string,
  fetchImpl: typeof fetch = fetch,
): Promise<BackendState> {
  try {
    const response = await fetchImpl(`${apiBaseUrl}/health`, { cache: "no-store" });
    if (!response.ok) return "error";
    return healthSchema.safeParse(await response.json()).success ? "ok" : "error";
  } catch {
    // Réseau coupé, CORS refusé, JSON invalide : le front affiche « indisponible ».
    return "error";
  }
}
