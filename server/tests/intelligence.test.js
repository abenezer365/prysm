import { readFileSync } from "node:fs";
import { describe, it, expect, vi, afterEach } from "vitest";
import {
  validateIntelligence,
  AiEngineAdapter,
} from "../src/integrations/ai-engine/adapter.js";
import { RagAdapter } from "../src/integrations/rag/adapter.js";
import { AuthorizedChatContextBuilder } from "../src/modules/chat/context.js";
import { prisma } from "../src/config/database.js";
const real = JSON.parse(
  readFileSync(
    new URL(
      "../../ai-engine/examples/phase2_investigation.json",
      import.meta.url,
    ),
    "utf8",
  ),
);
afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});
describe("Phase 5 trusted contracts", () => {
  it("reports core RAG readiness independently of its optional cloud provider", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          status: "ok",
          knowledgeBase: "ok",
          llm: "configured_not_verified",
          providerRequiredForHealth: false,
        }),
      }),
    );
    const adapter = new RagAdapter({
      RAG_BASE_URL: "http://localhost:8200",
      RAG_TIMEOUT_MS: 1000,
    });
    await expect(adapter.health()).resolves.toBe("ok");
  });
  it("preserves the complete actual Phase 2 evidence, graph and nullable score", () => {
    expect(validateIntelligence(real)).toEqual(real);
    const empty = structuredClone(real);
    empty.assessment.strength = null;
    expect(validateIntelligence(empty).assessment.strength).toBeNull();
  });
  it("rejects malformed and mismatched evidence", () => {
    expect(() => validateIntelligence({})).toThrow();
    const bad = structuredClone(real);
    bad.evidence[0].provenance.analysis_fingerprint = "wrong";
    expect(() => validateIntelligence(bad)).toThrow();
  });
  it("sends only the canonical subject and cutoff and rejects substituted results", async () => {
    const fetch = vi
      .fn()
      .mockResolvedValue({ ok: true, json: async () => real });
    vi.stubGlobal("fetch", fetch);
    const adapter = new AiEngineAdapter({
      AI_ENGINE_BASE_URL: "http://localhost:8100",
      AI_ENGINE_API_KEY: "test",
      AI_ENGINE_TIMEOUT_MS: 1000,
    });
    const context = {
      subject: { externalRef: real.subject.entity_key, type: "Person" },
      cutoffAt: real.investigation_window.cutoff,
      transactions: ["must not leave"],
    };
    await adapter.analyze(context);
    expect(JSON.parse(fetch.mock.calls[0][1].body)).toEqual({
      subject: real.subject.entity_key,
      cutoff: real.investigation_window.cutoff,
    });
    await expect(
      adapter.analyze({ ...context, subject: { externalRef: "Person:other" } }),
    ).rejects.toThrow(/does not match/);
  });
  it("does not accept RAG edits to detector evidence", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          version: "prysm-reasoning-v1",
          summary: "x",
          detected: { evidence: [], assessment: real.assessment },
          provenance: real.provenance,
        }),
      }),
    );
    const adapter = new RagAdapter({
      RAG_BASE_URL: "http://localhost:8200",
      RAG_API_KEY: "test",
      RAG_TIMEOUT_MS: 1000,
    });
    await expect(
      adapter.askAuthorized(
        { question: "why", context: { intelligence: real } },
        "test",
      ),
    ).rejects.toThrow(/inconsistent/);
  });
  it("denies foreign or reclassified cases before returning private intelligence", async () => {
    const item = {
      createdBy: "owner",
      shared: false,
      minimumClearanceRank: 2,
      subject: { classificationRank: 4 },
      runs: [{ responsePayload: real }],
    };
    vi.spyOn(prisma.investigation, "findUnique").mockResolvedValue(item);
    const contexts = new AuthorizedChatContextBuilder();
    await expect(
      contexts.forInvestigation("id", {
        userId: "other",
        permissions: [],
        clearanceRank: 4,
      }),
    ).rejects.toThrow(/denied/);
    await expect(
      contexts.forInvestigation("id", {
        userId: "owner",
        permissions: [],
        clearanceRank: 2,
      }),
    ).rejects.toThrow(/clearance/);
  });
});
