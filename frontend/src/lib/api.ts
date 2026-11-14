const DEFAULT_API_BASE_URL = "http://localhost:8000";

/** Backend base URL, without a trailing slash. */
export function getApiBaseUrl(): string {
  const base = process.env.NEXT_PUBLIC_API_BASE_URL || DEFAULT_API_BASE_URL;
  return base.replace(/\/+$/, "");
}

/** Build an absolute backend URL from a path such as `/health`. */
export function buildApiUrl(path: string): string {
  return `${getApiBaseUrl()}${path.startsWith("/") ? path : `/${path}`}`;
}

/** Typed JSON GET/POST helper; throws on non-2xx responses. */
export async function apiFetch<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const res = await fetch(buildApiUrl(path), {
    ...init,
    headers: { Accept: "application/json", ...init?.headers },
  });
  if (!res.ok) {
    throw new Error(`API request failed: ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as T;
}
