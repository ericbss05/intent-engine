import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  confirmAdult,
  deleteMyAccount,
  exportMyData,
  getAdminStatus,
  getMe,
} from "@/lib/account-api";

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });
const me = {
  adult_confirmed: true,
  ai_assist_consent: false,
  created_at: "2026-11-28T10:00:00Z",
  is_admin: false,
};

beforeEach(() => vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://api.test"));
afterEach(() => vi.unstubAllEnvs());

describe("account api", () => {
  it("sends the bearer token and parses /me", async () => {
    const fetchMock = vi.fn().mockResolvedValue(json(me));
    const result = await getMe("tok", fetchMock);
    expect(result).toEqual({ ok: true, data: me });
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("http://api.test/me");
    expect(init.headers.Authorization).toBe("Bearer tok");
  });

  it("treats an invalid /me payload as an error, not a crash", async () => {
    const result = await getMe("tok", vi.fn().mockResolvedValue(json({ hello: "world" })));
    expect(result).toMatchObject({ ok: false, code: "invalid_response" });
  });

  it("keeps the backend error code (and the status)", async () => {
    const result = await getMe(
      "tok",
      vi.fn().mockResolvedValue(json({ code: "profile_not_found", message: "x" }, 404)),
    );
    expect(result).toEqual({ ok: false, status: 404, code: "profile_not_found" });
  });

  it("maps network failures", async () => {
    const result = await getMe("tok", vi.fn().mockRejectedValue(new TypeError("offline")));
    expect(result).toEqual({ ok: false, status: 0, code: "network_error" });
  });

  it("posts the 18+ confirmation with confirmed=true only", async () => {
    const fetchMock = vi.fn().mockResolvedValue(json(me));
    await confirmAdult("tok", fetchMock);
    const [, init] = fetchMock.mock.calls[0];
    expect(init.method).toBe("POST");
    expect(JSON.parse(init.body)).toEqual({ confirmed: true });
  });

  it("downloads the export as a blob", async () => {
    const result = await exportMyData("tok", vi.fn().mockResolvedValue(json({ tables: {} })));
    expect(result.ok && result.data instanceof Blob).toBe(true);
  });

  it("deletes the account with DELETE /me", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
    expect((await deleteMyAccount("tok", fetchMock)).ok).toBe(true);
    expect(fetchMock.mock.calls[0][1].method).toBe("DELETE");
  });

  it("reports 403 for a non-admin", async () => {
    const result = await getAdminStatus(
      "tok",
      vi.fn().mockResolvedValue(json({ code: "forbidden", message: "x" }, 403)),
    );
    expect(result).toMatchObject({ ok: false, status: 403 });
  });
});
