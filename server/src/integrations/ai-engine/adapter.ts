import { z } from "zod";
import type { Env } from "../../config/env.js";
import type { InvestigationContext } from "../../modules/investigations/context.js";
import { postJson } from "../http.js";

const component = z.object({ name: z.string(), status: z.string(), strength: z.number().nullable(), confidence: z.number(), reason: z.string(), evidence_ids: z.array(z.string()).default([]) }).passthrough();
const response = z.object({
  requestId: z.string(), investigationId: z.string(), engineVersion: z.string(), generatedAt: z.string(),
  assessment: z.object({ type: z.literal("uncalibrated_attention_assessment"), strength: z.number().min(0).max(1), confidence: z.number().min(0).max(1), isFraudProbability: z.literal(false) }),
  components: z.record(z.string(), component), findings: z.record(z.string(), z.unknown()), evidence: z.array(z.record(z.string(), z.unknown())),
  graphIntelligence: z.record(z.string(), z.unknown()), limitations: z.array(z.string()), modelVersions: z.record(z.string(), z.unknown()), provenance: z.record(z.string(), z.unknown()), caseSummary: z.string().optional()
});
export type AiAnalysisResponse = z.infer<typeof response>;
export class AiEngineAdapter {
  constructor(private env: Env) {}
  async analyze(context: InvestigationContext, request: { requestId: string; investigationId: string }) {
    return response.parse(await postJson<unknown>(`${this.env.AI_ENGINE_BASE_URL}/v1/analyze`, { ...context, ...request }, this.env.AI_ENGINE_API_KEY, this.env.AI_ENGINE_TIMEOUT_MS));
  }
  async searchPeople(query: string, limit: number) {
    const url = new URL("/v1/people/search", this.env.AI_ENGINE_BASE_URL);
    url.searchParams.set("q", query); url.searchParams.set("limit", String(limit));
    const response = await fetch(url, { headers: this.env.AI_ENGINE_API_KEY ? { Authorization: `Bearer ${this.env.AI_ENGINE_API_KEY}` } : {}, signal: AbortSignal.timeout(this.env.AI_ENGINE_TIMEOUT_MS) });
    if (!response.ok) throw new Error(`AI person index returned ${response.status}`);
    return z.object({ data: z.array(z.object({ externalRef: z.string(), label: z.string(), status: z.string().nullable(), profile: z.record(z.string(), z.unknown()) })), total: z.number(), datasetVersion: z.string() }).parse(await response.json());
  }
  async graph(externalRef: string, options: { cutoffAt: Date; maxHops: number; maxNodes: number }) {
    const url = new URL(`/v1/graph/${encodeURIComponent(externalRef)}`, this.env.AI_ENGINE_BASE_URL);
    url.searchParams.set("cutoffAt", options.cutoffAt.toISOString()); url.searchParams.set("maxHops", String(options.maxHops)); url.searchParams.set("maxNodes", String(options.maxNodes));
    const response = await fetch(url, { headers: this.env.AI_ENGINE_API_KEY ? { Authorization: `Bearer ${this.env.AI_ENGINE_API_KEY}` } : {}, signal: AbortSignal.timeout(this.env.AI_ENGINE_TIMEOUT_MS) });
    if (!response.ok) throw new Error(`AI graph service returned ${response.status}`);
    return z.object({ subject: z.string(), cutoffAt: z.string(), maxHops: z.number(), maxNodes: z.number(), truncated: z.boolean(), nodes: z.array(z.record(z.string(), z.unknown())), edges: z.array(z.record(z.string(), z.unknown())) }).parse(await response.json());
  }
  async health() { try { const r = await fetch(`${this.env.AI_ENGINE_BASE_URL}/health`, { signal: AbortSignal.timeout(2000) }); return r.ok ? "ok" : "degraded"; } catch { return "unavailable"; } }
}
