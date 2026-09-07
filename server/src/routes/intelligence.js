import { Router } from "express";
import { z } from "zod";
import { prisma } from "../config/database.js";
import { authenticate, authorize } from "../middleware/security.js";
import { AiEngineAdapter } from "../integrations/ai-engine/adapter.js";
import { RagAdapter } from "../integrations/rag/adapter.js";
import { AuthorizedChatContextBuilder } from "../modules/chat/context.js";
import { audit } from "../modules/audit/service.js";

export function intelligenceRoutes(env) {
  const router = Router(),
    auth = authenticate(env.JWT_ACCESS_SECRET);
  const ai = new AiEngineAdapter(env),
    rag = new RagAdapter(env),
    contexts = new AuthorizedChatContextBuilder();
  async function persistRanking(q, principal, request) {
    const ranked = await ai.rank(q.cutoffAt, q.limit);
    return persistRankingRows(ranked, q.cutoffAt, q.limit, principal, request);
  }
  async function persistRankingRows(ranked, cutoffAt, limit, principal, request) {
    const data = [];
    for (const row of ranked.ranking) {
      let displayLabel = row.display_label || row.entity_key;
      if (!row.display_label) {
        try {
          const match = await ai.searchPeople(row.entity_key, 1);
          displayLabel = match.data[0]?.label || displayLabel;
        } catch {
          // Keep the canonical key if the label index is temporarily unavailable.
        }
      }
      const subject = await prisma.subject.upsert({
        where: { subjectType_externalRef: { subjectType: "Person", externalRef: row.entity_key } },
        update: { displayLabel },
        create: { subjectType: "Person", externalRef: row.entity_key, displayLabel, classificationRank: 2 },
      });
      if (subject.classificationRank <= principal.clearanceRank)
        data.push({ ...row, displayLabel, subjectId: subject.id });
    }
    const snapshot = await prisma.riskRankingSnapshot.upsert({
      where: { cutoffAt: new Date(cutoffAt) },
      update: { population: ranked.population, limit, data, source: "AI_ENGINE" },
      create: { cutoffAt: new Date(cutoffAt), population: ranked.population, limit, data, source: "AI_ENGINE" },
    });
    await audit(request, { action: "suspects.rank.persist", resourceType: "risk_ranking_snapshot", resourceId: snapshot.id, decision: "ALLOW", metadata: { count: data.length, cutoffAt } });
    return { data, population: snapshot.population, cutoffAt: snapshot.cutoffAt, source: snapshot.source, page: { limit, nextCursor: null }, snapshotId: snapshot.id, persistedAt: snapshot.updatedAt };
  }
  const rankingQuery = z.object({ cutoffAt: z.iso.datetime({ offset: true }).optional(), limit: z.coerce.number().int().min(1).max(50).default(10) }).strict();
  router.get(
    ["/suspects/top", "/dashboard/top-suspects"],
    auth,
    authorize("subject:read", 2),
    async (req, res) => {
      const q = rankingQuery.parse(req.query);
      const snapshot = q.cutoffAt
        ? await prisma.riskRankingSnapshot.findUnique({ where: { cutoffAt: new Date(q.cutoffAt) } })
        : await prisma.riskRankingSnapshot.findFirst({ orderBy: { createdAt: "desc" } });
      if (!snapshot && !q.cutoffAt) {
        const artifact = await ai.persistedRank(q.limit);
        return res.json(await persistRankingRows(
          { population: artifact.population, ranking: artifact.ranking },
          artifact.cutoff,
          q.limit,
          req.principal,
          req,
        ));
      }
      const data = snapshot ? snapshot.data.slice(0, q.limit) : [];
      res.json(snapshot ? { data, population: snapshot.population, cutoffAt: snapshot.cutoffAt, source: snapshot.source, page: { limit: q.limit, nextCursor: null }, snapshotId: snapshot.id, persistedAt: snapshot.updatedAt } : { data: [], population: "No persisted ranking at this cutoff", cutoffAt: null, source: null, page: { limit: q.limit, nextCursor: null }, snapshotId: null, persistedAt: null });
    },
  );
  router.post("/dashboard/top-suspects/run", auth, authorize("model:read", 4), async (req, res) => {
    const q = z.object({ cutoffAt: z.iso.datetime({ offset: true }), limit: z.coerce.number().int().min(1).max(50).default(10) }).strict().parse(req.body);
    res.json(await persistRanking(q, req.principal, req));
  });
  router.get(
    "/investigations/:id/intelligence",
    auth,
    authorize("investigation:read", 2),
    async (req, res) => {
      const built = await contexts.forInvestigation(
        z.string().uuid().parse(req.params.id),
        req.principal,
      );
      res.json({ runId: built.runId, result: built.context.intelligence });
    },
  );
  router.post(
    "/investigations/:id/summary",
    auth,
    authorize("investigation:read", 2),
    async (req, res) => {
      const built = await contexts.forInvestigation(
        z.string().uuid().parse(req.params.id),
        req.principal,
      );
      const result = built.context.intelligence;
      const label = built.context.subject?.label || result.subject.entity_key;
      const sections = Object.fromEntries(
        Object.entries(result.intelligence_components || {}).map(([name, component]) => {
          const available = component?.status === "available" && component?.strength != null;
          const score = available ? Math.round(Number(component.strength) * 100) : null;
          const source = name === "gnn" ? "the GNN relationship model" : name === "anomaly" ? "the anomaly model" : name === "network" ? "the relationship analysis" : "the configured evidence rules";
          return [name, {
            score,
            available,
            description: available
              ? `Based on ${source}, ${label}'s score is ${score}/100. ${score >= 65 ? "This pattern is unusually strong and should be checked against the cited evidence." : score >= 35 ? "This is a moderate review signal that needs supporting context." : "This signal is weak and does not independently support escalation."}`
              : `${source[0].toUpperCase() + source.slice(1)} could not produce a score for ${label}: ${component?.reason || "insufficient eligible evidence"}.`,
          }];
        }),
      );
      let narrative = result.ai_summary?.text || `${label}'s current result requires evidence-led review.`;
      let provider = "prysm_fallback";
      try {
        const explanation = await rag.askAuthorized({ context: { intelligence: result }, question: `Summarize the supported investigation topics and next evidence checks for ${label}.` }, req.requestId);
        narrative = `${label}: ${explanation.answer}`;
        provider = explanation.reasoning?.provenance?.provider || "grounded_rag";
      } catch {
        // The person-specific local result remains complete if Gemini/RAG is unavailable.
      }
      res.json({ narrative, provider, sections, suspicious: (result.evidence || []).slice(0, 8).map(e => e.description), generatedAt: new Date().toISOString() });
    },
  );
  router.get(
    "/investigations/:id/conversation",
    auth,
    authorize("chat:authorized", 2),
    async (req, res) => {
      const built = await contexts.forInvestigation(
        z.string().uuid().parse(req.params.id),
        req.principal,
      );
      const limit = z.coerce
        .number()
        .int()
        .min(1)
        .max(100)
        .default(50)
        .parse(req.query.limit);
      const data = await prisma.ragInteraction.findMany({
        where: {
          userId: req.principal.userId,
          scope: "AUTHORIZED",
          contextManifest: {
            path: ["investigationId"],
            equals: built.investigationId,
          },
        },
        orderBy: [{ createdAt: "desc" }, { id: "asc" }],
        take: limit,
        select: {
          id: true,
          conversationId: true,
          question: true,
          answer: true,
          sources: true,
          createdAt: true,
          contextManifest: true,
        },
      });
      res.json({ data, page: { limit, nextCursor: null } });
    },
  );
  return router;
}
