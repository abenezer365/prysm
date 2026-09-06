import { z } from "zod";
import { AppError } from "../../common/errors.js";
import { postJson } from "../http.js";
export const intelligenceResult = z
  .object({
    version: z.literal("prysm-intelligence-v2"),
    subject: z.object({ entity_key: z.string() }).passthrough(),
    investigation_window: z.object({ cutoff: z.string() }).passthrough(),
    assessment: z
      .object({
        strength: z.number().min(0).max(1).nullable(),
        is_fraud_probability: z.literal(false),
        breakdown: z.unknown(),
      })
      .passthrough(),
    intelligence_components: z.record(z.string(), z.unknown()),
    findings: z.record(z.string(), z.unknown()),
    evidence: z.array(
      z
        .object({
          evidence_id: z.string(),
          provenance: z
            .object({ analysis_fingerprint: z.string() })
            .passthrough(),
        })
        .passthrough(),
    ),
    graph: z
      .object({
        nodes: z.array(z.record(z.string(), z.unknown())),
        edges: z.array(z.record(z.string(), z.unknown())),
        analysis_fingerprint: z.string(),
      })
      .passthrough(),
    limitations: z.array(z.string()),
    provenance: z
      .object({
        analysis_fingerprint: z.string(),
        dataset_version: z.string(),
        ground_truth_used_at_inference: z.literal(false),
      })
      .passthrough(),
  })
  .passthrough();
export function validateIntelligence(raw) {
  if (typeof raw === "string") {
    try {
      raw = JSON.parse(raw);
    } catch {
      throw new AppError(
        502,
        "AI_INVALID_RESPONSE",
        "Stored intelligence is invalid",
      );
    }
  }
  const parsed = intelligenceResult.safeParse(raw);
  if (!parsed.success)
    throw new AppError(
      502,
      "AI_INVALID_RESPONSE",
      "Intelligence service returned an invalid result",
    );
  const r = parsed.data,
    fingerprint = r.provenance.analysis_fingerprint;
  if (
    r.graph.analysis_fingerprint !== fingerprint ||
    new Set(r.evidence.map((e) => e.evidence_id)).size !== r.evidence.length ||
    r.evidence.some((e) => e.provenance.analysis_fingerprint !== fingerprint)
  )
    throw new AppError(
      502,
      "AI_INVALID_RESPONSE",
      "Intelligence provenance is inconsistent",
    );
  return r;
}
export class AiEngineAdapter {
  constructor(env) {
    this.env = env;
  }
  async analyze(context) {
    const subject = context.subject.externalRef.includes(":")
      ? context.subject.externalRef
      : context.subject.type + ":" + context.subject.externalRef;
    const result = validateIntelligence(
      await postJson(
        this.env.AI_ENGINE_BASE_URL + "/v2/investigate",
        { subject, cutoff: context.cutoffAt },
        this.env.AI_ENGINE_API_KEY,
        this.env.AI_ENGINE_TIMEOUT_MS,
      ),
    );
    if (
      result.subject.entity_key !== subject ||
      Date.parse(result.investigation_window.cutoff) !==
        Date.parse(context.cutoffAt)
    )
      throw new AppError(
        502,
        "AI_INVALID_RESPONSE",
        "Intelligence result does not match the request",
      );
    return result;
  }
  async rank(cutoff, limit) {
    const raw = await postJson(
      this.env.AI_ENGINE_BASE_URL + "/v2/rank",
      { cutoff, limit },
      this.env.AI_ENGINE_API_KEY,
      this.env.AI_ENGINE_TIMEOUT_MS,
    );
    const parsed = z
      .object({
        population: z.string(),
        ranking: z.array(
          z
            .object({
              entity_key: z.string(),
              overall_risk: z.number().min(0).max(1),
              is_fraud_probability: z.literal(false),
            })
            .passthrough(),
        ),
      })
      .safeParse(raw);
    if (!parsed.success)
      throw new AppError(
        502,
        "AI_INVALID_RESPONSE",
        "Invalid ranking response",
      );
    return parsed.data;
  }
  async searchPeople(query, limit) {
    const url = new URL("/v2/people/search", this.env.AI_ENGINE_BASE_URL);
    url.searchParams.set("q", query);
    url.searchParams.set("limit", limit);
    try {
      const response = await fetch(url, {
        redirect: "error",
        headers: { Authorization: "Bearer " + this.env.AI_ENGINE_API_KEY },
        signal: AbortSignal.timeout(this.env.AI_ENGINE_TIMEOUT_MS),
      });
      if (!response.ok) throw new Error();
      return z
        .object({
          data: z.array(
            z.object({
              externalRef: z.string(),
              label: z.string(),
              status: z.string().nullable(),
              profile: z.record(z.string(), z.unknown()),
              analysisCutoffAt: z.iso.datetime({ offset: true }).nullable(),
            }),
          ),
          total: z.number(),
          datasetVersion: z.string(),
        })
        .parse(await response.json());
    } catch {
      throw new AppError(503, "AI_UNAVAILABLE", "Person index is unavailable");
    }
  }
  async graph(externalRef, options) {
    return (
      await this.analyze({
        subject: { externalRef, type: "Person" },
        cutoffAt: options.cutoffAt.toISOString(),
      })
    ).graph;
  }
  async health() {
    try {
      const r = await fetch(this.env.AI_ENGINE_BASE_URL + "/ready", {
        redirect: "error",
        headers: { Authorization: "Bearer " + this.env.AI_ENGINE_API_KEY },
        signal: AbortSignal.timeout(2000),
      });
      return r.ok ? "ok" : "degraded";
    } catch {
      return "unavailable";
    }
  }
}
