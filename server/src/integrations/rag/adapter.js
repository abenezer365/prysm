import { isDeepStrictEqual } from "node:util";
import { AppError } from "../../common/errors.js";
import { z } from "zod";
import { postJson } from "../http.js";
const source = z.object({
  title: z.string(),
  source: z.string(),
  category: z.string(),
  version: z.string(),
});
const answer = z.object({
  answer: z.string(),
  mode: z.enum(["public", "investigator"]),
  sources: z.array(source),
  evidence: z.array(z.unknown()).optional(),
  conversationId: z.string(),
  requestId: z.string(),
});
const ingest = z.object({
  success: z.literal(true),
  documentId: z.string(),
  chunks: z.number().int().positive(),
});
function parseIngest(raw) {
  const result = ingest.safeParse(raw);
  if (!result.success)
    throw new AppError(
      502,
      "RAG_INVALID_RESPONSE",
      "Invalid knowledge ingestion response",
    );
  return result.data;
}
export class RagAdapter {
  env;
  constructor(env) {
    this.env = env;
  }
  async askPublic(question, requestId) {
    const url = new URL("/ask", this.env.RAG_BASE_URL);
    url.searchParams.set("message", question);
    try {
      const response = await fetch(url, {
        signal: AbortSignal.timeout(this.env.RAG_TIMEOUT_MS),
        headers: { "x-request-id": requestId },
      });
      if (!response.ok) throw new Error("rejected");
      return answer.parse(await response.json());
    } catch {
      throw new (await import("../../common/errors.js")).AppError(
        503,
        "RAG_UNAVAILABLE",
        "Knowledge service is unavailable",
      );
    }
  }
  async askAuthorized(input, requestId) {
    const raw = await postJson(
      this.env.RAG_BASE_URL + "/explain",
      { intelligence: input.context.intelligence, question: input.question },
      this.env.RAG_API_KEY,
      this.env.RAG_TIMEOUT_MS,
      { "x-request-id": requestId },
    );
    if (
      raw?.version !== "prysm-reasoning-v1" ||
      typeof raw.summary !== "string" ||
      raw.provenance?.analysis_fingerprint !==
        input.context.intelligence.provenance.analysis_fingerprint ||
      !isDeepStrictEqual(
        raw.detected?.evidence,
        input.context.intelligence.evidence,
      ) ||
      !isDeepStrictEqual(
        raw.detected?.assessment,
        input.context.intelligence.assessment,
      ) ||
      !isDeepStrictEqual(
        raw.detected?.subject,
        input.context.intelligence.subject,
      ) ||
      raw.provenance?.private_context_sent_to_cloud !== false ||
      !Array.isArray(raw.explanation?.knowledge_context)
    ) {
      throw new AppError(
        502,
        "RAG_INVALID_RESPONSE",
        "Explanation service returned an inconsistent response",
      );
    }
    return {
      answer: raw.summary,
      mode: "investigator",
      sources: raw.explanation.knowledge_context,
      evidence: raw.detected.evidence,
      reasoning: raw,
      requestId,
    };
  }
  async ingest(document, requestId) {
    return parseIngest(
      await postJson(
        `${this.env.RAG_BASE_URL}/ingest`,
        document,
        this.env.RAG_API_KEY,
        this.env.RAG_TIMEOUT_MS,
        { "x-request-id": requestId },
      ),
    );
  }
  async setDocumentEnabled(documentId, enabled, requestId) {
    try {
      const url = new URL(`/documents/${documentId}`, this.env.RAG_BASE_URL);
      url.searchParams.set("enabled", String(enabled));
      const response = await fetch(url, {
        method: "PATCH",
        redirect: "error",
        signal: AbortSignal.timeout(this.env.RAG_TIMEOUT_MS),
        headers: {
          authorization: `Bearer ${this.env.RAG_API_KEY}`,
          "x-request-id": requestId,
        },
      });
      if (!response.ok) throw new Error("rejected");
      return await response.json();
    } catch {
      throw new (await import("../../common/errors.js")).AppError(
        503,
        "RAG_DOCUMENT_UPDATE_FAILED",
        "Knowledge document could not be updated",
      );
    }
  }
  async health() {
    try {
      const r = await fetch(`${this.env.RAG_BASE_URL}/health`, {
        signal: AbortSignal.timeout(2000),
      });
      if (!r.ok) return "degraded";
      const body = await r.json();
      return body.status === "ok" && body.knowledgeBase === "ok"
        ? "ok"
        : "degraded";
    } catch {
      return "unavailable";
    }
  }
}
