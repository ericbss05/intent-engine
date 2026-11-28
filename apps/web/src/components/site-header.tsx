import { Show, UserButton } from "@clerk/nextjs";
import Link from "next/link";

export function SiteHeader() {
  return (
    <header className="mx-auto flex w-full max-w-2xl items-center justify-between px-6 py-4">
      <Link href="/" className="font-semibold">
        stage-finder
      </Link>
      <nav className="flex items-center gap-4 text-sm">
        <Show when="signed-in">
          <Link href="/account">Mon compte</Link>
          {/* Le menu du bouton contient « Se déconnecter ». */}
          <UserButton />
        </Show>
        <Show when="signed-out">
          <Link href="/sign-in">Se connecter</Link>
          <Link href="/sign-up">Créer un compte</Link>
        </Show>
      </nav>
    </header>
  );
}
