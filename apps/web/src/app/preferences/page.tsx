import { PreferencesForm } from "@/components/preferences-form";

export default function PreferencesPage() {
  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-6 px-6 py-8">
      <h1 className="text-2xl font-semibold">Ma recherche</h1>
      <PreferencesForm />
    </main>
  );
}
