import { OnboardingForm } from "@/components/onboarding-form";

export default function OnboardingPage() {
  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-6 px-6 py-8">
      <h1 className="text-2xl font-semibold">Avant de commencer</h1>
      <OnboardingForm />
    </main>
  );
}
