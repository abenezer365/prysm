import { Router } from "express";
import { z } from "zod";
import { prisma } from "../config/database.js";
import { authenticate, authorize } from "../middleware/security.js";
import { AiEngineAdapter } from "../integrations/ai-engine/adapter.js";
import { AuthorizedChatContextBuilder } from "../modules/chat/context.js";
import { audit } from "../modules/audit/service.js";

export function intelligenceRoutes(env) {
  const router = Router(),
    auth = authenticate(env.JWT_ACCESS_SECRET);
  const ai = new AiEngineAdapter(env),
    contexts = new AuthorizedChatContextBuilder();
  router.get(
    ["/suspects/top", "/dashboard/top-suspects"],
    auth,
    authorize("subject:read", 2),
    async (req, res) => {
      const q = z
        .object({
          cutoffAt: z.iso.datetime({ offset: true }),
          limit: z.coerce.number().int().min(1).max(50).default(10),
        })
        .strict()
        .parse(req.query);
      const ranked = await ai.rank(q.cutoffAt, q.limit);
      const data = [];
      for (const row of ranked.ranking) {
        const subject = await prisma.subject.upsert({
          where: {
            subjectType_externalRef: {
              subjectType: "Person",
              externalRef: row.entity_key,
            },
          },
          update: {},
          create: {
            subjectType: "Person",
            externalRef: row.entity_key,
            displayLabel: row.entity_key,
            classificationRank: 2,
          },
        });
        if (subject.classificationRank <= req.principal.clearanceRank)
          data.push({ ...row, subjectId: subject.id });
      }
      await audit(req, {
        action: "suspects.rank",
        resourceType: "ranking",
        decision: "ALLOW",
        metadata: { count: data.length, cutoffAt: q.cutoffAt },
      });
      res.json({
        data,
        population: ranked.population,
        cutoffAt: q.cutoffAt,
        page: { limit: q.limit, nextCursor: null },
      });
    },
  );
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
