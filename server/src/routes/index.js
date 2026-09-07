import { randomUUID } from "node:crypto";
import { Router } from "express";
import { z } from "zod";
import { AppError, notFound } from "../common/errors.js";
import { prisma } from "../config/database.js";
import { validate } from "../middleware/core.js";
import {
  authenticate,
  authorize,
  enforceOwnership,
  resolveAccessToken,
} from "../middleware/security.js";
import { AuthService, safeUser } from "../modules/auth/service.js";
import { audit } from "../modules/audit/service.js";
import { InvestigationContextBuilder } from "../modules/investigations/context.js";
import { persistAnalysis } from "../modules/investigations/persist-analysis.js";
import { AiEngineAdapter } from "../integrations/ai-engine/adapter.js";
import { RagAdapter } from "../integrations/rag/adapter.js";
import { AuthorizedChatContextBuilder } from "../modules/chat/context.js";
import { intelligenceRoutes } from "./intelligence.js";
import { ensureConversation } from "../modules/chat/conversation.js";
import { completionRoutes } from "./completion.js";
const asyncRoute = (fn) => (req, res, next) =>
  Promise.resolve(fn(req, res, next)).catch(next);
const routeParam = (req, name) => {
  const value = req.params[name];
  if (!value || Array.isArray(value))
    throw new AppError(400, "INVALID_PATH_PARAMETER", `Invalid ${name}`);
  return z.string().uuid().parse(value);
};
const uuid = z.string().uuid();
const login = z.object({
  email: z.string().trim().toLowerCase().email(),
  password: z.string().min(8),
  deviceInfo: z.string().max(500).optional(),
});
const createInvestigation = z.object({
  subjectId: uuid,
  title: z.string().max(200).optional(),
  purpose: z.string().max(2000).optional(),
  cutoffAt: z.iso
    .datetime({ offset: true })
    .transform((value) => new Date(value)),
  predictionHorizonStart: z.coerce.date().optional(),
  predictionHorizonEnd: z.coerce.date().optional(),
});
const chat = z
  .object({
    question: z.string().min(1).max(4000),
    conversationId: uuid.optional(),
    subjectId: uuid.optional(),
    investigationId: uuid.optional(),
    cutoffAt: z.coerce.date().optional(),
  })
  .strict();
const ragDocument = z
  .object({
    title: z.string().min(1).max(300),
    content: z.string().min(1).max(100000),
    source: z.string().max(300).optional(),
    category: z.string().max(100).optional(),
    version: z.string().max(50).optional(),
    metadata: z.record(z.string(), z.unknown()).optional(),
  })
  .strict();
const bounds = z
  .object({
    cutoffAt: z.iso
      .datetime({ offset: true })
      .transform((value) => new Date(value)),
  })
  .strict();
export function apiRoutes(env) {
  const router = Router();
  const auth = new AuthService(env);
  const requireAuth = authenticate(env.JWT_ACCESS_SECRET);
  const context = new InvestigationContextBuilder();
  const authorizedChatContext = new AuthorizedChatContextBuilder(context);
  const ai = new AiEngineAdapter(env);
  const rag = new RagAdapter(env);
  router.use(completionRoutes(env));
  router.use(intelligenceRoutes(env));
  router.get("/health", (_req, res) =>
    res.json({ status: "ok", version: "0.5.0" }),
  );
  router.get(
    "/health/ready",
    asyncRoute(async (_req, res) => {
      try {
        await prisma.$queryRaw`SELECT 1`;
        res.json({ status: "ready" });
      } catch {
        throw new AppError(503, "NOT_READY", "PostgreSQL is unavailable");
      }
    }),
  );
  router.get(
    "/health/dependencies",
    requireAuth,
    authorize("health:dependencies:read"),
    asyncRoute(async (_req, res) => {
      let postgres = "ok";
      try {
        await prisma.$queryRaw`SELECT 1`;
      } catch {
        postgres = "unavailable";
      }
      const [aiEngine, ragState] = await Promise.all([
        ai.health(),
        rag.health(),
      ]);
      res.json({
        status:
          postgres === "ok" && aiEngine === "ok" && ragState === "ok"
            ? "ok"
            : "degraded",
        services: { postgres, aiEngine, rag: ragState },
      });
    }),
  );
  router.post(
    "/auth/login",
    validate(login),
    asyncRoute(async (req, res) => {
      const result = await auth.login(
        req.body.email.toLowerCase(),
        req.body.password,
        {
          deviceInfo: req.body.deviceInfo,
          ip: req.ip,
          userAgent: req.header("user-agent"),
        },
      );
      const principal = await resolveAccessToken(
        env.JWT_ACCESS_SECRET,
        result.accessToken,
      );
      req.principal = principal;
      await audit(req, {
        action: "auth.login",
        resourceType: "session",
        resourceId: principal.sessionId,
        decision: "ALLOW",
      });
      res.json(result);
    }),
  );
  router.post(
    "/auth/logout",
    requireAuth,
    asyncRoute(async (req, res) => {
      await auth.logout(req.principal.sessionId);
      await audit(req, {
        action: "auth.logout",
        resourceType: "session",
        resourceId: req.principal.sessionId,
        decision: "ALLOW",
      });
      res.status(204).end();
    }),
  );
  router.get(
    "/auth/me",
    requireAuth,
    asyncRoute(async (req, res) => {
      const user = await prisma.user.findUnique({
        where: { id: req.principal.userId },
        include: { role: true, clearance: true },
      });
      if (!user) throw notFound("User");
      res.json(safeUser(user));
    }),
  );
  router.get("/me/permissions", requireAuth, (req, res) =>
    res.json({ permissions: req.principal.permissions }),
  );
  router.get("/me/clearance", requireAuth, (req, res) =>
    res.json({ rank: req.principal.clearanceRank }),
  );
  router.get(
    "/subjects/:id",
    requireAuth,
    authorize("subject:read"),
    asyncRoute(async (req, res) => {
      const subject = await prisma.subject.findUnique({
        where: { id: routeParam(req, "id") },
      });
      if (!subject) throw notFound("Subject");
      const p = req.principal;
      if (p.clearanceRank < subject.classificationRank)
        throw new AppError(
          403,
          "INSUFFICIENT_CLEARANCE",
          "Subject classification exceeds clearance",
        );
      res.json({
        id: subject.id,
        type: subject.subjectType,
        label: subject.displayLabel,
        status: subject.status,
      });
    }),
  );
  router.get(
    "/subjects/:id/profile",
    requireAuth,
    authorize("subject:sensitive:read", 3),
    asyncRoute(async (req, res) => {
      const subject = await prisma.subject.findUnique({
        where: { id: routeParam(req, "id") },
        include: { profile: true },
      });
      if (!subject) throw notFound("Subject");
      const p = req.principal;
      if (p.clearanceRank < subject.classificationRank)
        throw new AppError(
          403,
          "INSUFFICIENT_CLEARANCE",
          "Subject classification exceeds clearance",
        );
      res.json({
        id: subject.id,
        type: subject.subjectType,
        label: subject.displayLabel,
        profile: subject.profile,
      });
    }),
  );
  router.post(
    "/search",
    requireAuth,
    authorize("subject:read"),
    asyncRoute(async (req, res) => {
      const q = z
        .object({
          query: z.string().min(2).max(200),
          limit: z.number().int().min(1).max(50).default(20),
        })
        .parse(req.body);
      const rank = req.principal.clearanceRank;
      const rows = await prisma.subject.findMany({
        where: {
          classificationRank: { lte: rank },
          OR: [
            { displayLabel: { contains: q.query, mode: "insensitive" } },
            { externalRef: { contains: q.query, mode: "insensitive" } },
            {
              profile: {
                is: { fullName: { contains: q.query, mode: "insensitive" } },
              },
            },
          ],
        },
        take: q.limit,
        orderBy: { displayLabel: "asc" },
      });
      // PostgreSQL is the operational store, while the AI artifact contains the
      // complete canonical population. Materialize matching people lazily so
      // every dataset person can enter the normal investigation workflow.
      let datasetVersion = null;
      const activeMatches = [];
      try {
        const indexed = await ai.searchPeople(
          q.query,
          Math.min(50, Math.max(q.limit * 3, q.limit)),
        );
        datasetVersion = indexed.datasetVersion;
        const seenLabels = new Set();
        for (const person of indexed.data) {
          const normalizedLabel = person.label.trim().toLocaleLowerCase();
          if (seenLabels.has(normalizedLabel)) continue;
          seenLabels.add(normalizedLabel);
          if (activeMatches.length >= q.limit) break;
          const subject = await prisma.subject.upsert({
            where: {
              subjectType_externalRef: {
                subjectType: "Person",
                externalRef: person.externalRef,
              },
            },
            update: { displayLabel: person.label, status: person.status },
            create: {
              subjectType: "Person",
              externalRef: person.externalRef,
              displayLabel: person.label,
              status: person.status,
              classificationRank: 2,
            },
          });
          const profileJson = JSON.parse(JSON.stringify(person.profile));
          await prisma.subjectProfile.upsert({
            where: { subjectId: subject.id },
            update: {
              fullName: person.label,
              dateOfBirth: person.profile.dateOfBirth
                ? new Date(String(person.profile.dateOfBirth))
                : null,
              countryCode: person.profile.country === "Ethiopia" ? "ET" : null,
              sensitiveAttributes: profileJson,
            },
            create: {
              subjectId: subject.id,
              fullName: person.label,
              dateOfBirth: person.profile.dateOfBirth
                ? new Date(String(person.profile.dateOfBirth))
                : null,
              countryCode: person.profile.country === "Ethiopia" ? "ET" : null,
              sensitiveAttributes: profileJson,
            },
          });
          activeMatches.push({
            id: subject.id,
            type: subject.subjectType,
            label: person.label,
            status: person.status,
            externalRef: person.externalRef,
            analysisCutoffAt: person.analysisCutoffAt,
            profile: person.profile,
          });
        }
      } catch {
        if (!rows.length)
          throw new AppError(
            502,
            "PERSON_INDEX_UNAVAILABLE",
            "The complete person dataset index is temporarily unavailable",
          );
        activeMatches.push(
          ...rows.map((subject) => ({
            id: subject.id,
            type: subject.subjectType,
            label: subject.displayLabel,
            status: subject.status,
            externalRef: subject.externalRef,
            analysisCutoffAt: null,
            profile: null,
          })),
        );
        // Existing operational records remain searchable during a degraded AI
        // service window, but an empty result must never masquerade as a full
        // dataset search.
      }
      await audit(req, {
        action: "subject.search",
        resourceType: "search",
        decision: "ALLOW",
        metadata: {
          queryLength: q.query.length,
          resultCount: activeMatches.length,
          datasetVersion,
        },
      });
      res.json({
        data: activeMatches,
        page: { nextCursor: null, limit: q.limit },
        datasetVersion,
      });
    }),
  );
  router.post(
    "/investigations",
    requireAuth,
    authorize("investigation:create", 2),
    validate(createInvestigation),
    asyncRoute(async (req, res) => {
      const p = req.principal;
      const subject = await prisma.subject.findUnique({
        where: { id: req.body.subjectId },
      });
      if (!subject) throw notFound("Subject");
      if (p.clearanceRank < subject.classificationRank)
        throw new AppError(
          403,
          "INSUFFICIENT_CLEARANCE",
          "Subject classification exceeds clearance",
        );
      const item = await prisma.investigation.create({
        data: {
          ...req.body,
          createdBy: p.userId,
          contextVersion: "prysm-intelligence-v2",
          minimumClearanceRank: subject.classificationRank,
        },
      });
      await audit(req, {
        action: "investigation.create",
        resourceType: "investigation",
        resourceId: item.id,
        decision: "ALLOW",
      });
      res.status(201).json(item);
    }),
  );
  router.get(
    "/investigations",
    requireAuth,
    authorize("investigation:read"),
    asyncRoute(async (req, res) => {
      const p = req.principal;
      const limit = z.coerce
        .number()
        .int()
        .min(1)
        .max(100)
        .default(50)
        .parse(req.query.limit);
      const data = await prisma.investigation.findMany({
        where: {
          minimumClearanceRank: { lte: p.clearanceRank },
          OR: [
            { createdBy: p.userId },
            { shared: true },
            ...(p.permissions.includes("investigation:read:any") ? [{}] : []),
          ],
        },
        take: limit,
        orderBy: [{ createdAt: "desc" }, { id: "asc" }],
        include: { subject: true },
      });
      res.json({
        data: data.map((x) => ({
          id: x.id,
          status: x.status,
          title: x.title,
          cutoffAt: x.cutoffAt,
          subject: {
            id: x.subject.id,
            type: x.subject.subjectType,
            label: x.subject.displayLabel,
          },
          createdAt: x.createdAt,
        })),
        page: { nextCursor: null, limit },
      });
    }),
  );
  router.get(
    "/investigations/:id",
    requireAuth,
    authorize("investigation:read"),
    asyncRoute(async (req, res) => {
      const item = await prisma.investigation.findUnique({
        where: { id: routeParam(req, "id") },
        include: {
          subject: true,
          findings: { include: { evidence: { include: { evidence: true } } } },
          runs: { orderBy: { createdAt: "desc" }, take: 10 },
        },
      });
      if (!item) throw notFound("Investigation");
      const p = req.principal;
      enforceOwnership(item.createdBy, p, item.shared);
      if (
        p.clearanceRank <
        Math.max(
          item.minimumClearanceRank,
          item.subject?.classificationRank || 0,
        )
      )
        throw new AppError(
          403,
          "INSUFFICIENT_CLEARANCE",
          "Investigation classification exceeds clearance",
        );
      res.json({
        id: item.id,
        status: item.status,
        title: item.title,
        purpose: item.purpose,
        cutoffAt: item.cutoffAt,
        subject: {
          id: item.subject.id,
          type: item.subject.subjectType,
          label: item.subject.displayLabel,
        },
        findings: item.findings,
        analysisRuns: item.runs.map((run) => ({
          ...run,
          responsePayload: run.responsePayload
            ? JSON.parse(run.responsePayload)
            : null,
        })),
        scientificStatus: {
          benchmarkScope: "synthetic benchmark where applicable",
          isCalibratedProbability: false,
        },
      });
    }),
  );
  router.post(
    "/investigations/:id/analyze",
    requireAuth,
    authorize("investigation:analyze", 2),
    asyncRoute(async (req, res) => {
      const item = await prisma.investigation.findUnique({
        where: { id: routeParam(req, "id") },
        include: { subject: true },
      });
      if (!item) throw notFound("Investigation");
      const p = req.principal;
      enforceOwnership(item.createdBy, p, item.shared);
      if (
        p.clearanceRank <
        Math.max(
          item.minimumClearanceRank,
          item.subject?.classificationRank || 0,
        )
      )
        throw new AppError(
          403,
          "INSUFFICIENT_CLEARANCE",
          "Investigation classification exceeds clearance",
        );
      if (!item.cutoffAt)
        throw new AppError(
          409,
          "CUTOFF_REQUIRED",
          "Retrospective analysis requires a cutoff",
        );
      const ctx = await context.build(item.subjectId, {
        cutoffAt: item.cutoffAt,
        lookbackDays: 365,
        maxHops: 3,
        maxNodes: 250,
      });
      const requestId = req.requestId;
      const run = await prisma.analysisRun.create({
        data: {
          investigationId: item.id,
          requestedBy: p.userId,
          status: "RUNNING",
          contextVersion: ctx.version,
          dataSnapshot: ctx.dataSnapshot,
          cutoffAt: item.cutoffAt,
          requestPayload: JSON.parse(JSON.stringify(ctx)),
          startedAt: new Date(),
        },
      });
      try {
        let result = await ai.analyze(ctx, {
          requestId,
          investigationId: item.id,
        });
        const strength = Number(result.assessment?.strength || 0);
        result.ai_summary = {
          text: strength < 0.25
            ? `${item.subject.displayLabel} has insufficient evidence for escalation. No strong supported rule or anomaly was found; continue routine review and obtain additional evidence.`
            : `${item.subject.displayLabel} has evidence-supported indicators that require review. Verify each cited source record before drawing a conclusion.`,
          provider: "prysm_immediate_summary",
          suspicious: (result.evidence || []).slice(0, 5).map((e) => e.description),
          sufficient: (result.evidence || []).length > 0 && strength >= 0.25,
        };
        await persistAnalysis(run.id, item.id, result);
        await audit(req, {
          action: "investigation.analyze",
          resourceType: "investigation",
          resourceId: item.id,
          decision: "ALLOW",
          metadata: { runId: run.id, aiEngineVersion: result.version },
        });
        res.status(200).json({ runId: run.id, status: "SUCCEEDED", result });
      } catch (error) {
        await prisma.analysisRun.updateMany({
          where: { id: run.id, status: "RUNNING" },
          data: {
            status: "FAILED",
            errorCode: "AI_ENGINE_FAILURE",
            completedAt: new Date(),
          },
        });
        throw error;
      }
    }),
  );
  router.get(
    "/investigations/:id/analysis-runs/:runId",
    requireAuth,
    authorize("investigation:read"),
    asyncRoute(async (req, res) => {
      const runId = routeParam(req, "runId");
      if (!runId) throw notFound("Analysis run");
      const run = await prisma.analysisRun.findUnique({
        where: { id: runId },
        include: { investigation: { include: { subject: true } } },
      });
      if (!run || run.investigationId !== routeParam(req, "id"))
        throw notFound("Analysis run");
      enforceOwnership(
        run.investigation.createdBy,
        req.principal,
        run.investigation.shared,
      );
      if (
        req.principal.clearanceRank <
        Math.max(
          run.investigation.minimumClearanceRank,
          run.investigation.subject.classificationRank,
        )
      )
        throw new AppError(
          403,
          "INSUFFICIENT_CLEARANCE",
          "Investigation classification exceeds clearance",
        );
      res.json({
        ...run,
        responsePayload: run.responsePayload
          ? JSON.parse(run.responsePayload)
          : null,
      });
    }),
  );
  router.get(
    "/graph/subjects/:id/subgraph",
    requireAuth,
    authorize("graph:read", 2),
    asyncRoute(async (req, res) => {
      const q = bounds.parse(req.query);
      const subjectId = routeParam(req, "id");
      const subject = await prisma.subject.findUnique({
        where: { id: subjectId },
      });
      if (!subject?.externalRef) throw notFound("Subject");
      if (req.principal.clearanceRank < subject.classificationRank)
        throw new AppError(
          403,
          "INSUFFICIENT_CLEARANCE",
          "Subject classification exceeds clearance",
        );
      if (!q.cutoffAt)
        throw new AppError(
          400,
          "CUTOFF_REQUIRED",
          "Provide an explicit cutoffAt",
        );
      const cutoffAt = q.cutoffAt;
      const built = await ai.graph(subject.externalRef, { cutoffAt });
      await audit(req, {
        action: "graph.read",
        resourceType: "subject",
        resourceId: subjectId,
        decision: "ALLOW",
        metadata: { cutoffAt: cutoffAt.toISOString() },
      });
      res.json(built);
    }),
  );
  router.get(
    "/evidence/:id",
    requireAuth,
    authorize("evidence:read", 2),
    asyncRoute(async (req, res) => {
      const item = await prisma.evidenceReference.findUnique({
        where: { id: routeParam(req, "id") },
      });
      if (!item) throw notFound("Evidence");
      const links = await prisma.findingEvidence.findMany({
        where: { evidenceId: item.id },
        include: {
          finding: {
            include: { investigation: { include: { subject: true } } },
          },
        },
      });
      const p = req.principal;
      const allowed = links.some((link) => {
        const i = link.finding.investigation;
        return (
          Math.max(i.minimumClearanceRank, i.subject.classificationRank) <=
            p.clearanceRank &&
          (i.createdBy === p.userId ||
            i.shared ||
            p.permissions.includes("investigation:read:any"))
        );
      });
      if (!allowed)
        throw new AppError(
          403,
          "RESOURCE_ACCESS_DENIED",
          "Resource access denied",
        );
      res.json(item);
    }),
  );
  router.get(
    "/models",
    requireAuth,
    authorize("model:read"),
    asyncRoute(async (_req, res) =>
      res.json({
        data: await prisma.modelRegistry.findMany({
          select: {
            id: true,
            code: true,
            version: true,
            modelType: true,
            status: true,
            evaluationScope: true,
            isCalibratedProbability: true,
            metadata: true,
          },
        }),
      }),
    ),
  );
  router.get(
    "/audit/events",
    requireAuth,
    authorize("audit:read", 4),
    asyncRoute(async (_req, res) =>
      res.json({
        data: await prisma.auditEvent.findMany({
          take: 100,
          orderBy: { createdAt: "desc" },
        }),
      }),
    ),
  );
  router.post(
    "/chat/public",
    validate(
      chat.omit({ subjectId: true, investigationId: true, cutoffAt: true }),
    ),
    asyncRoute(async (req, res) => {
      const requestId = req.requestId;
      const requestedConversationId = randomUUID();
      const answer = await rag.askPublic(req.body.question, requestId);
      const conversationId = requestedConversationId;
      await prisma.ragInteraction.create({
        data: {
          conversationId,
          requestId,
          ragRequestId: answer.requestId,
          scope: "PUBLIC",
          question: req.body.question,
          answer: answer.answer,
          sources: answer.sources,
          accessScope: { publicOnly: true },
          contextManifest: { knowledgeOnly: true },
          ragVersion: "prysm-reasoning-v1",
          status: "SUCCEEDED",
        },
      });
      res.json({
        conversationId,
        requestId,
        answer: answer.answer,
        sources: answer.sources,
        mode: "public",
      });
    }),
  );
  router.post(
    "/chat/authorized",
    requireAuth,
    authorize("chat:authorized", 2),
    validate(chat),
    asyncRoute(async (req, res) => {
      const p = req.principal;
      if (!req.body.investigationId)
        throw new AppError(
          400,
          "INVESTIGATION_REQUIRED",
          "Authorized chat requires an investigationId",
        );
      const requestId = req.requestId;
      const built = await authorizedChatContext.forInvestigation(
        req.body.investigationId,
        p,
      );
      await ensureConversation(
        req.body.conversationId,
        p.userId,
        built.investigationId,
      );
      const answer = await rag.askAuthorized(
        {
          question: req.body.question,
          userId: p.userId,
          subjectId: built.subjectId,
          investigationId: built.investigationId,
          context: built.context,
        },
        requestId,
      );
      const conversationId =
        req.body.conversationId || answer.conversationId || randomUUID();
      await prisma.ragInteraction.create({
        data: {
          conversationId,
          requestId,
          ragRequestId: answer.requestId,
          userId: p.userId,
          scope: "AUTHORIZED",
          question: req.body.question,
          answer: answer.answer,
          sources: answer.sources,
          accessScope: { role: p.role, clearanceRank: p.clearanceRank },
          contextManifest: {
            contractVersion: "prysm-reasoning-v1",
            runId: built.runId,
            analysisFingerprint:
              built.context.intelligence.provenance.analysis_fingerprint,
            investigationId: built.investigationId,
            subjectId: built.subjectId,
            cutoffAt: built.context.investigation.cutoffAt,
          },
          ragVersion: "prysm-reasoning-v1",
          status: "SUCCEEDED",
        },
      });
      await audit(req, {
        action: "chat.authorized",
        resourceType: "conversation",
        resourceId: conversationId,
        decision: "ALLOW",
        metadata: {
          investigationId: built.investigationId,
          ragRequestId: answer.requestId,
        },
      });
      res.json({
        conversationId,
        requestId,
        answer: answer.answer,
        sources: answer.sources,
        mode: "investigator",
        evidence: answer.evidence || [],
        reasoning: answer.reasoning,
      });
    }),
  );
  router.post(
    "/rag/ingest",
    requireAuth,
    authorize("rag:ingest", 4),
    validate(ragDocument),
    asyncRoute(async (req, res) => {
      const requestId = req.requestId,
        p = req.principal;
      const pending = await prisma.ragDocumentRecord.create({
        data: {
          title: req.body.title,
          description: req.body.metadata?.description,
          source: req.body.source,
          category: req.body.category,
          version: req.body.version,
          metadata: req.body.metadata,
          createdBy: p.userId,
          status: "PROCESSING",
        },
      });
      try {
        const result = await rag.ingest(req.body, requestId);
        const record = await prisma.$transaction(async (tx) => {
          const existing = await tx.ragDocumentRecord.findUnique({
            where: { externalId: result.documentId },
          });
          const id = existing?.id || pending.id;
          const updated = await tx.ragDocumentRecord.update({
            where: { id },
            data: {
              externalId: result.documentId,
              status: "COMPLETED",
              chunkCount: result.chunks,
              title: req.body.title,
              source: req.body.source,
              category: req.body.category,
              version: req.body.version,
              metadata: req.body.metadata,
              errorCode: null,
            },
          });
          if (existing && existing.id !== pending.id)
            await tx.ragDocumentRecord.delete({ where: { id: pending.id } });
          return updated;
        });
        await audit(req, {
          action: "rag.ingest",
          resourceType: "knowledge_document",
          resourceId: record.id,
          decision: "ALLOW",
          metadata: {
            externalId: result.documentId,
            source: req.body.source,
            category: req.body.category,
            chunks: result.chunks,
          },
        });
        res.status(201).json({
          jobId: record.id,
          status: record.status,
          documentId: result.documentId,
          chunks: result.chunks,
        });
      } catch (error) {
        await prisma.ragDocumentRecord.updateMany({
          where: { id: pending.id, status: "PROCESSING" },
          data: { status: "FAILED", errorCode: "RAG_INGEST_FAILED" },
        });
        throw error;
      }
    }),
  );
  return router;
}
