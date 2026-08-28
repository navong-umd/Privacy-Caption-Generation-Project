// Centralized API layer. Every request goes through apiGet; no scattered fetch().

const BASE = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");

export class ApiError extends Error {
  status: number;
  detail?: string;
  constructor(status: number, message: string, detail?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

function buildUrl(path: string, params?: Record<string, unknown>): string {
  const url = `${BASE}${path}`;
  if (!params) return url;
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === null || v === "") continue;
    qs.set(k, String(v));
  }
  const s = qs.toString();
  return s ? `${url}?${s}` : url;
}

export async function apiGet<T>(
  path: string,
  params?: Record<string, unknown>,
  signal?: AbortSignal,
): Promise<T> {
  let res: Response;
  try {
    res = await fetch(buildUrl(path, params), {
      signal,
      headers: { Accept: "application/json" },
    });
  } catch {
    throw new ApiError(0, "Could not reach the research API. Is the backend running?");
  }

  if (!res.ok) {
    let detail: string | undefined;
    try {
      const body = await res.json();
      detail = body?.detail ?? body?.message;
    } catch {
      /* non-JSON error body */
    }
    const message =
      res.status === 404
        ? "Not found."
        : res.status === 422
          ? "The request was not valid."
          : res.status >= 500
            ? "The server could not complete the request."
            : `Request failed (${res.status}).`;
    throw new ApiError(res.status, message, detail);
  }

  try {
    return (await res.json()) as T;
  } catch {
    throw new ApiError(res.status, "The server returned a malformed response.");
  }
}
