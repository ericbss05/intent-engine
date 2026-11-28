import { BackendStatus } from "@/components/backend-status";

export default function Home() {
  return (
    <main className="mx-auto flex max-w-2xl flex-1 flex-col justify-center gap-4 px-6 py-16">
      <h1 className="text-3xl font-semibold tracking-tight">stage-finder</h1>
      <p className="text-muted-foreground">
        Aide à la recherche de stage et d&apos;alternance. Le service est en cours de construction.
      </p>
      <BackendStatus />
    </main>
  );
}
