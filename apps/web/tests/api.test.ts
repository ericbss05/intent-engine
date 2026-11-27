import { describe, expect, it, vi } from "vitest";

import { fetchBackendState } from "@/lib/api";

const respond = (body: unknown, status = 200) =>
  vi.fn().mockResolvedValue(new Response(JSON.stringify(body), { status }));

describe("fetchBackendState", () => {
  it("returns ok when the backend answers {status: 'ok'}", async () => {
    const fetchMock = respond({ status: "ok" });
    expect(await fetchBackendState("http://api.test", fetchMock)).toBe("ok");
    expect(fetchMock.mock.calls[0][0]).toBe("http://api.test/health");
  });

  it("returns error on a non-200 status", async () => {
    expect(await fetchBackendState("http://api.test", respond({}, 500))).toBe("error");
  });

  it("returns error when the payload has the wrong shape", async () => {
    expect(await fetchBackendState("http://api.test", respond({ status: "nope" }))).toBe("error");
  });

  it("returns error when the network fails", async () => {
    const failing = vi.fn().mockRejectedValue(new TypeError("network"));
    expect(await fetchBackendState("http://api.test", failing)).toBe("error");
  });
});
