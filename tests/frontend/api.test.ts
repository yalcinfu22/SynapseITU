import { afterEach, expect, it, vi } from "vitest";
import { buildApiUrl, getApiBaseUrl } from "@/lib/api";

afterEach(() => {
  vi.unstubAllEnvs();
});

it("builds API URLs from the default and the configured base URL", () => {
  vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "");
  expect(getApiBaseUrl()).toBe("http://localhost:8000");
  expect(buildApiUrl("/health")).toBe("http://localhost:8000/health");

  vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "https://api.example.test/");
  expect(buildApiUrl("/v1/search")).toBe("https://api.example.test/v1/search");
  expect(buildApiUrl("v1/search")).toBe("https://api.example.test/v1/search");
});
