import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const push = vi.fn();
const getToken = vi.fn();
vi.mock("@clerk/nextjs", () => ({
  useAuth: () => ({ getToken }),
  useClerk: () => ({ signOut: vi.fn() }),
}));
vi.mock("next/navigation", () => ({ useRouter: () => ({ push, replace: push }) }));

import { OnboardingFlow } from "@/components/onboarding-flow";

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });
const texts = {
  version_note: "n",
  privacy_notice: { version: "pv1", title: "Information RGPD", text: "Texte info" },
  ai_assist: { version: "av1", title: "Analyse IA", text: "Texte IA" },
};
const me = {
  adult_confirmed: true,
  ai_assist_consent: false,
  created_at: "2026-11-28T10:00:00Z",
  is_admin: false,
};
const consentsOk = { consents: [] };

function stubBackend() {
  const calls: { url: string; method: string; body?: string }[] = [];
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string, init?: RequestInit) => {
      calls.push({ url, method: init?.method ?? "GET", body: init?.body as string | undefined });
      if (url.endsWith("/reference/consent-texts")) return json(texts);
      if (url.endsWith("/me/adult-confirmation")) return json(me);
      if (url.includes("/me/consents/")) return json(consentsOk);
      return json({}, 404);
    }),
  );
  return calls;
}

beforeEach(() => {
  vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://api.test");
  getToken.mockResolvedValue("tok");
});
afterEach(() => {
  cleanup();
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
  vi.clearAllMocks();
});

async function toAiStep() {
  fireEvent.click(await screen.findByRole("button", { name: /J'ai lu cette information/ }));
  const button = screen.getByRole("button", { name: "Continuer" }) as HTMLButtonElement;
  expect(button.disabled).toBe(true); // 18+ obligatoire
  fireEvent.click(screen.getByRole("checkbox"));
  fireEvent.click(button);
}

describe("OnboardingFlow", () => {
  it("shows the information text first and sends nothing before the end", async () => {
    const calls = stubBackend();
    render(<OnboardingFlow />);
    expect(await screen.findByText("Texte info")).toBeTruthy();
    await toAiStep();
    expect(calls.filter((c) => c.method !== "GET")).toHaveLength(0);
  });

  it("leaves the AI choice unchecked by default and does not log an AI consent", async () => {
    const calls = stubBackend();
    render(<OnboardingFlow />);
    await toAiStep();
    const box = screen.getByRole("checkbox") as HTMLInputElement;
    expect(box.checked).toBe(false);
    fireEvent.click(screen.getByRole("button", { name: "Terminer" }));
    await waitFor(() => expect(push).toHaveBeenCalledWith("/preferences"));
    const writes = calls.filter((c) => c.method !== "GET").map((c) => c.url);
    expect(writes.some((u) => u.endsWith("/me/adult-confirmation"))).toBe(true);
    expect(writes.some((u) => u.endsWith("/me/consents/privacy_notice"))).toBe(true);
    expect(writes.some((u) => u.endsWith("/me/consents/ai_assist"))).toBe(false);
  });

  it("logs the AI consent with the text version only when the box is ticked", async () => {
    const calls = stubBackend();
    render(<OnboardingFlow />);
    await toAiStep();
    fireEvent.click(screen.getByRole("checkbox"));
    fireEvent.click(screen.getByRole("button", { name: "Terminer" }));
    await waitFor(() => expect(push).toHaveBeenCalled());
    const ai = calls.find((c) => c.url.endsWith("/me/consents/ai_assist"));
    expect(JSON.parse(ai!.body!)).toEqual({ granted: true, version_text: "av1" });
  });

  it("shows an error and stays on the page if saving fails", async () => {
    stubBackend();
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string) =>
        url.endsWith("/reference/consent-texts")
          ? json(texts)
          : json({ code: "x", message: "y" }, 500),
      ),
    );
    render(<OnboardingFlow />);
    await toAiStep();
    fireEvent.click(screen.getByRole("button", { name: "Terminer" }));
    expect((await screen.findByRole("alert")).textContent).toContain("Réessayez");
    expect(push).not.toHaveBeenCalled();
  });
});
