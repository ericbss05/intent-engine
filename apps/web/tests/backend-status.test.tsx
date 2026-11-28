import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { BackendStatus } from "@/components/backend-status";

afterEach(() => {
  vi.unstubAllGlobals();
  vi.unstubAllEnvs();
});

describe("BackendStatus", () => {
  it("shows OK when /health answers ok", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://api.test");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response(JSON.stringify({ status: "ok" }))),
    );
    render(<BackendStatus />);
    expect(await screen.findByText("OK")).toBeTruthy();
  });

  it("shows unavailable when the API URL is not configured", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "");
    render(<BackendStatus />);
    expect(await screen.findByText("Service indisponible")).toBeTruthy();
  });
});
