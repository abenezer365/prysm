import { z } from "zod";
import type { Env } from "../../config/env.js";
import type { InvestigationContext } from "../../modules/investigations/context.js";
import { postJson } from "../http.js";

const component = z.object({ name: z.string(), status: z.string(), strength: z.number().nullable(), confidence: z.number(), reason: z.string(), evidence_ids: z.array(z.string()).default([]) }).passthrough();
const response = z.object({
  requestId: z.string(), investigationId: z.string(), engineVersion: z.string(), generatedAt: z.string(),
  assessment: z.object({ type: z.literal("uncalibrated_attention_assessment"), strength: z.number().min(0).max(1), confidence: z.number().min(0).max(1), isFraudProbability: z.literal(false) }),
  components: z.record(z.string(), component), findings: z.record(z.string(), z.unknown()), evidence: z.array(z.record(z.string(), z.unknown())),
  graphIntelligence: z.record(z.string(), z.unknown()), limitations: z.array(z.string()), modelVersions: z.record(z.string(), z.unknown()), provenance: z.record(z.string(), z.unknown())
});
export type AiAnalysisResponse = z.infer<typeof response>;
export class AiEngineAdapter {
  constructor(private env: Env) {}
  async analyze(context: InvestigationContext, request: { requestId: string; investigationId: string }) {
    return response.parse(await postJson<unknown>(`${this.env.AI_ENGINE_BASE_URL}/v1/analyze`, { ...context, ...request }, this.env.AI_ENGINE_API_KEY, this.env.AI_ENGINE_TIMEOUT_MS));
  }
  async health() { try { const r = await fetch(`${this.env.AI_ENGINE_BASE_URL}/health`, { signal: AbortSignal.timeout(2000) }); return r.ok ? "ok" : "degraded"; } catch { return "unavailable"; } }
}
