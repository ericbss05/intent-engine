import { AccountPanel } from "@/components/account-panel";

export default function AccountPage() {
  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-6 px-6 py-8">
      <h1 className="text-2xl font-semibold">Mon compte</h1>
      <AccountPanel />
    </main>
  );
}
