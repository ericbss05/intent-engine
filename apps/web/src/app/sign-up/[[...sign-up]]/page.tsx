import { SignUp } from "@clerk/nextjs";
import { Suspense } from "react";

export default function SignUpPage() {
  return (
    <main className="flex flex-1 items-center justify-center px-6 py-8">
      {/* Après l'inscription : étape « 18 ans minimum » avant tout le reste. */}
      <Suspense fallback={<p role="status">Chargement…</p>}>
        <SignUp forceRedirectUrl="/onboarding" />
      </Suspense>
    </main>
  );
}
