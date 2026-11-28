import { describe, expect, it } from "vitest";

import { parseEnv } from "@/lib/env";

describe("parseEnv", () => {
  it("accepts a URL and removes trailing slashes", () => {
    expect(parseEnv({ NEXT_PUBLIC_API_BASE_URL: "http://localhost:8000/" }).apiBaseUrl).toBe(
      "http://localhost:8000",
    );
  });

  it("rejects a missing or invalid value", () => {
    expect(() => parseEnv({})).toThrow();
    expect(() => parseEnv({ NEXT_PUBLIC_API_BASE_URL: "not a url" })).toThrow();
  });
});
