import { AppError } from "../common/errors.js";
export async function postJson<T>(url: string, body: unknown, apiKey: string, timeoutMs = 15_000, extraHeaders: Record<string, string> = {}): Promise<T> {
  const controller = new AbortController(); const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try { const response = await fetch(url, { method: "POST", headers: { "content-type": "application/json", ...(apiKey ? { authorization: `Bearer ${apiKey}` } : {}), ...extraHeaders }, body: JSON.stringify(body), signal: controller.signal }); if (!response.ok) throw new AppError(502, "UPSTREAM_REJECTED", "Upstream service rejected the request"); return await response.json() as T; }
  catch (error) { if (error instanceof AppError) throw error; throw new AppError(503, "UPSTREAM_UNAVAILABLE", "Required upstream service is unavailable"); }
  finally { clearTimeout(timeout); }
}
