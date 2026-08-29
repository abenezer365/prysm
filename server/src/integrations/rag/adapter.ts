import { z } from "zod";
import type { Env } from "../../config/env.js";
import { postJson } from "../http.js";

const source = z.object({ title: z.string(), source: z.string(), category: z.string(), version: z.string() });
const answer = z.object({ answer: z.string(), mode: z.enum(["public", "investigator"]), sources: z.array(source), evidence: z.array(z.unknown()).optional(), conversationId: z.string(), requestId: z.string() });
const ingest = z.object({ success: z.literal(true), documentId: z.string(), chunks: z.number().int().positive() });
export type RagAnswer = z.infer<typeof answer>;
export class RagAdapter {
  constructor(private env: Env) {}
  async askPublic(question: string, requestId: string) {
    const url = new URL("/ask", this.env.RAG_BASE_URL); url.searchParams.set("message", question);
    try { const response = await fetch(url, { signal: AbortSignal.timeout(this.env.RAG_TIMEOUT_MS), headers: { "x-request-id": requestId } }); if (!response.ok) throw new Error("rejected"); return answer.parse(await response.json()); }
    catch { throw new (await import("../../common/errors.js")).AppError(503, "RAG_UNAVAILABLE", "Knowledge service is unavailable"); }
  }
  async askAuthorized(input: { question: string; userId: string; subjectId?: string; investigationId?: string; context: unknown }, requestId: string) {
    return answer.parse(await postJson(`${this.env.RAG_BASE_URL}/ask`, { message: input.question, authenticated: true, userId: input.userId, subjectId: input.subjectId, investigationId: input.investigationId, context: input.context }, this.env.RAG_API_KEY, this.env.RAG_TIMEOUT_MS, { "x-request-id": requestId }));
  }
  async ingest(document: { title: string; content: string; source?: string; category?: string; version?: string; metadata?: Record<string, unknown> }, requestId: string) { return ingest.parse(await postJson(`${this.env.RAG_BASE_URL}/ingest`, document, this.env.RAG_API_KEY, this.env.RAG_TIMEOUT_MS, { "x-request-id": requestId })); }
  async health() { try { const r = await fetch(`${this.env.RAG_BASE_URL}/health`, { signal: AbortSignal.timeout(2000) }); if (!r.ok) return "degraded"; const body=await r.json() as any; return body.status === "ok" && body.knowledgeBase === "ok" && body.llm === "ok" ? "ok" : "degraded"; } catch { return "unavailable"; } }
}
