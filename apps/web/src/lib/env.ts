import { z } from "zod";

// Validation des variables d'environnement du front, au chargement du module.
// NEXT_PUBLIC_* : visibles dans le navigateur, donc JAMAIS de secret ici.
const schema = z.object({
  NEXT_PUBLIC_API_BASE_URL: z.url(),
});

// Next.js ne remplace une variable NEXT_PUBLIC_* que si on écrit son nom en entier
// (process.env.NEXT_PUBLIC_...), d'où l'objet explicite plutôt que process.env en bloc.
export function parseEnv(raw: Record<string, string | undefined>) {
  const result = schema.safeParse(raw);
  if (!result.success) {
    throw new Error(
      "Invalid environment: NEXT_PUBLIC_API_BASE_URL must be a full URL (see .env.example)",
    );
  }
  return {
    apiBaseUrl: result.data.NEXT_PUBLIC_API_BASE_URL.replace(/\/+$/, ""),
  };
}
