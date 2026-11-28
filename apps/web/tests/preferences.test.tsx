import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const getToken = vi.fn();
vi.mock("@clerk/nextjs", () => ({ useAuth: () => ({ getToken }) }));
vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: React.ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));

import { AiConsentPanel } from "@/components/ai-consent-panel";
import { PreferencesForm } from "@/components/preferences-form";
import {
  fromPayload,
  parseSirens,
  preferencesFormSchema,
  toPayload,
  DEFAULT_FORM_VALUES,
} from "@/lib/preferences-schema";

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });
const sectors = [
  { id: "informatique_telecoms", label: "Informatique, numérique et télécoms" },
  { id: "agroalimentaire", label: "Agroalimentaire" },
];
const valid = {
  ...DEFAULT_FORM_VALUES,
  target_role: "Data analyst",
  sectors: ["agroalimentaire"],
  zone_location: "75",
  company_size: ["10-49"],
};

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

describe("preferences schema (Zod)", () => {
  it("accepts a valid form and builds the API payload", () => {
    expect(preferencesFormSchema.safeParse(valid).success).toBe(true);
    const payload = toPayload({
      ...valid,
      zone_location: " 2a ",
      excluded_sirens_text: "552 100 554\n",
    });
    expect(payload.zone).toEqual({ location: "2A", radius_km: 30 });
    expect(payload.excluded_sirens).toEqual(["552100554"]);
    expect(payload.duration_months).toBe(6);
  });

  it.each([
    ["duration", { duration_months: "0" }],
    ["duration text", { duration_months: "six" }],
    ["role", { target_role: " " }],
    ["no sector", { sectors: [] }],
    ["street", { zone_location: "12 rue de la Paix" }],
    ["no size", { company_size: [] }],
    ["too many priorities", { priorities: ["a", "b", "c", "d"] }],
    ["bad siren", { excluded_sirens_text: "12345" }],
    ["duplicate siren", { excluded_sirens_text: "552100554\n552 100 554" }],
  ])("rejects %s", (_name, change) => {
    expect(preferencesFormSchema.safeParse({ ...valid, ...change }).success).toBe(false);
  });

  it("round-trips payload <-> form values", () => {
    const payload = toPayload({ ...valid, excluded_sirens_text: "552100554" });
    expect(toPayload(fromPayload(payload))).toEqual(payload);
    expect(parseSirens("1, 2;3\n 4 5")).toEqual(["1", "2", "3", "45"]);
  });
});

describe("PreferencesForm", () => {
  function stub(prefsStatus: number) {
    const calls: { url: string; method: string; body?: string }[] = [];
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string, init?: RequestInit) => {
        calls.push({ url, method: init?.method ?? "GET", body: init?.body as string | undefined });
        if (url.endsWith("/reference/sectors")) return json(sectors);
        if (url.endsWith("/me/preferences") && init?.method === "PUT")
          return json({ ...toPayload(valid), updated_at: "2026-11-28T10:00:00Z" });
        if (url.endsWith("/me/preferences"))
          return prefsStatus === 200
            ? json({ ...toPayload(valid), updated_at: "2026-11-28T10:00:00Z" })
            : json({ code: "preferences_not_found", message: "x" }, prefsStatus);
        return json({}, 404);
      }),
    );
    return calls;
  }

  it("does not call the server when the form is invalid and shows French messages", async () => {
    const calls = stub(404);
    render(<PreferencesForm />);
    fireEvent.click(await screen.findByRole("button", { name: "Enregistrer" }));
    expect(await screen.findByText("Indiquez le métier visé (2 caractères minimum).")).toBeTruthy();
    expect(screen.getByText("Choisissez au moins un secteur.")).toBeTruthy();
    expect(calls.some((c) => c.method === "PUT")).toBe(false);
  });

  it("loads existing preferences and saves modifications", async () => {
    const calls = stub(200);
    render(<PreferencesForm />);
    const role = (await screen.findByLabelText("Métier visé")) as HTMLInputElement;
    await waitFor(() => expect(role.value).toBe("Data analyst"));
    fireEvent.change(role, { target: { value: "Auditeur junior" } });
    fireEvent.click(screen.getByRole("button", { name: "Enregistrer" }));
    expect(await screen.findByText("Préférences enregistrées.")).toBeTruthy();
    const put = calls.find((c) => c.method === "PUT")!;
    expect(JSON.parse(put.body!).target_role).toBe("Auditeur junior");
    expect(JSON.parse(put.body!)).not.toHaveProperty("user_id");
  });
});

describe("AiConsentPanel", () => {
  const texts = {
    version_note: "n",
    privacy_notice: { version: "pv1", title: "t", text: "t" },
    ai_assist: { version: "av1", title: "t", text: "t" },
  };
  const state = (granted: boolean) => ({
    consents: [
      {
        kind: "ai_assist",
        granted,
        version_text: granted ? "av1" : null,
        recorded_at: null,
        current_version: "av1",
      },
    ],
  });

  it("shows 'désactivée' by default and lets the user give then withdraw", async () => {
    let granted = false;
    const bodies: string[] = [];
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string, init?: RequestInit) => {
        if (url.endsWith("/reference/consent-texts")) return json(texts);
        if (init?.method === "PUT") {
          bodies.push(init.body as string);
          granted = JSON.parse(init.body as string).granted;
        }
        return json(state(granted));
      }),
    );
    render(<AiConsentPanel />);
    expect(await screen.findByText(/désactivée/)).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Activer l'analyse assistée par IA" }));
    expect(await screen.findByText("activée")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Retirer mon accord" }));
    expect(await screen.findByText(/désactivée/)).toBeTruthy();
    expect(bodies.map((b) => JSON.parse(b))).toEqual([
      { granted: true, version_text: "av1" },
      { granted: false, version_text: "av1" },
    ]);
  });
});
