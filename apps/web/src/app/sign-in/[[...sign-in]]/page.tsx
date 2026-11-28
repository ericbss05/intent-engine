import { SignIn } from "@clerk/nextjs";
import { Suspense } from "react";

export default function SignInPage() {
  return (
    <main className="flex flex-1 items-center justify-center px-6 py-8">
      <Suspense fallback={<p role="status">Chargement…</p>}>
        <SignIn />
      </Suspense>
    </main>
  );
}
