import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const push = vi.fn();
const signOut = vi.fn();
const getToken = vi.fn();

// Clerk et le routeur sont simulés : aucun appel réseau, aucune clé.
vi.mock("@clerk/nextjs", () => ({
  useAuth: () => ({ getToken }),
  useClerk: () => ({ signOut }),
}));
vi.mock("next/navigation", () => ({ useRouter: () => ({ push, replace: push }) }));

import { AdminPanel } from "@/components/admin-panel";
import { DeleteAccountButton } from "@/components/delete-account-button";

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });

beforeEach(() => {
  vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://api.test");
  getToken.mockResolvedValue("tok");
});
afterEach(() => {
  cleanup(); // pas de nettoyage automatique sans « globals » dans Vitest
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
  vi.clearAllMocks();
});

describe("DeleteAccountButton", () => {
  it("needs a second, explicit click before deleting", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
    vi.stubGlobal("fetch", fetchMock);
    render(<DeleteAccountButton />);
    fireEvent.click(screen.getByRole("button", { name: "Supprimer mon compte" }));
    expect(fetchMock).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "Oui, tout supprimer" }));
    await waitFor(() => expect(signOut).toHaveBeenCalled());
    expect(fetchMock.mock.calls[0][1].method).toBe("DELETE");
  });

  it("explains when the account closing must be retried", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(json({ code: "identity_deletion_failed", message: "x" }, 502)),
    );
    render(<DeleteAccountButton />);
    fireEvent.click(screen.getByRole("button", { name: "Supprimer mon compte" }));
    fireEvent.click(screen.getByRole("button", { name: "Oui, tout supprimer" }));
    expect((await screen.findByRole("alert")).textContent).toContain("Réessayez");
    expect(signOut).not.toHaveBeenCalled();
  });
});

describe("AdminPanel", () => {
  it("shows access denied when the backend answers 403", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(json({ code: "forbidden", message: "x" }, 403)),
    );
    render(<AdminPanel />);
    expect((await screen.findByRole("alert")).textContent).toContain("Accès refusé");
  });

  it("shows the empty admin area when the backend answers 200", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(json({ status: "ok" })));
    render(<AdminPanel />);
    expect(await screen.findByText(/Espace d'administration/)).toBeTruthy();
  });
});
