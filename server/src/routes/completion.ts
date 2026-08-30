import { createHash, randomBytes } from "node:crypto";
import { readdir, stat, readFile } from "node:fs/promises";
import { basename, extname, join } from "node:path";
import argon2 from "argon2";
import { Router, type RequestHandler } from "express";
import { z } from "zod";
import { AppError, notFound } from "../common/errors.js";
import type { AuthRequest, Principal } from "../common/types.js";
import type { Env } from "../config/env.js";
import { prisma } from "../config/database.js";
import {
  authenticate,
  authorize,
  enforceOwnership,
} from "../middleware/security.js";
import { validate } from "../middleware/core.js";
import { audit } from "../modules/audit/service.js";
import { AuthService, safeUser } from "../modules/auth/service.js";
import { RagAdapter } from "../integrations/rag/adapter.js";

const asyncRoute =
  (fn: RequestHandler): RequestHandler =>
  (req, res, next) =>
    Promise.resolve(fn(req, res, next)).catch(next);
const id = (req: any, name = "id") => {
  const value = req.params[name];
  if (!value || Array.isArray(value))
    throw new AppError(400, "INVALID_PATH_PARAMETER", `Invalid ${name}`);
  return value as string;
};
const pageLimit = (value: unknown, max = 100) =>
  Math.max(1, Math.min(Number(value || 20), max));
const hash = (value: string) =>
  createHash("sha256").update(value).digest("hex");
const safeApplication = (x: any) => ({
  id: x.id,
  email: x.email,
  displayName: x.displayName,
  profession: x.profession,
  organization: x.organization,
  organizationRole: x.organizationRole,
  phone: x.phone,
  reason: x.reason,
  justification: x.justification,
  status: x.status,
  requestedRole: x.requestedRole
    ? {
        id: x.requestedRole.id,
        code: x.requestedRole.code,
        name: x.requestedRole.name,
      }
    : null,
  requestedClearance: x.requestedClearance
    ? {
        id: x.requestedClearance.id,
        code: x.requestedClearance.code,
        name: x.requestedClearance.name,
        rank: x.requestedClearance.rank,
      }
    : null,
  reviewedBy: x.reviewedBy,
  reviewedAt: x.reviewedAt,
  reviewReason: x.reviewReason,
  createdAt: x.createdAt,
  updatedAt: x.updatedAt,
  documents:
    x.documents?.map((d: any) => ({
      id: d.id,
      fileName: d.fileName,
      mimeType: d.mimeType,
      sizeBytes: d.sizeBytes,
      scanStatus: d.scanStatus,
      metadata: d.metadata,
    })) || [],
  history: x.history || [],
});
async function investigationFor(idValue: string, p: Principal) {
  const item = await prisma.investigation.findUnique({
    where: { id: idValue },
  });
  if (!item) throw notFound("Investigation");
  enforceOwnership(item.createdBy, p, item.shared);
  if (p.clearanceRank < item.minimumClearanceRank)
    throw new AppError(
      403,
      "INSUFFICIENT_CLEARANCE",
      "Investigation classification exceeds clearance",
    );
  return item;
}

export function completionRoutes(env: Env) {
  const router = Router(),
    requireAuth = authenticate(env.JWT_ACCESS_SECRET),
    auth = new AuthService(env),
    rag = new RagAdapter(env);
  const richApplication = z
    .object({
      email: z.string().email(),
      displayName: z.string().min(2).max(120),
      profession: z.string().min(2).max(160),
      organization: z.string().max(200).optional(),
      organizationRole: z.string().max(160).optional(),
      phone: z.string().max(40).optional(),
      reason: z.string().min(20).max(2000),
      justification: z.string().min(100).max(10000),
      requestedRoleId: z.string().uuid().optional(),
      requestedClearanceLevelId: z.string().uuid().optional(),
      supportingEvidence: z
        .array(
          z.object({
            fileName: z.string().min(1).max(255),
            mimeType: z.enum([
              "application/pdf",
              "image/png",
              "image/jpeg",
              "text/plain",
            ]),
            sizeBytes: z.number().int().min(1).max(5_000_000),
            metadata: z.record(z.string(), z.unknown()).optional(),
          }),
        )
        .max(5)
        .optional(),
    })
    .strict();
  router.post(
    "/applications",
    validate(richApplication),
    asyncRoute(async (req, res) => {
      const body = req.body;
      const recent = await prisma.accountApplication.findFirst({
        where: {
          email: body.email.toLowerCase(),
          status: "PENDING",
          createdAt: { gte: new Date(Date.now() - 7 * 86400_000) },
        },
      });
      if (recent)
        throw new AppError(
          409,
          "APPLICATION_ALREADY_PENDING",
          "A recent application is already pending",
        );
      const record = await prisma.accountApplication.create({
        data: {
          email: body.email.toLowerCase(),
          displayName: body.displayName,
          profession: body.profession,
          organization: body.organization,
          organizationRole: body.organizationRole,
          phone: body.phone,
          reason: body.reason,
          justification: body.justification,
          requestedRoleId: body.requestedRoleId,
          requestedClearanceLevelId: body.requestedClearanceLevelId,
          documents: {
            create: (body.supportingEvidence || []).map((d: any) => ({
              ...d,
              scanStatus: "METADATA_ONLY",
            })),
          },
        },
      });
      res
        .status(202)
        .json({
          id: record.id,
          status: record.status,
          createdAt: record.createdAt,
        });
    }),
  );
  router.get(
    "/applications",
    requireAuth,
    authorize("application:review", 3),
    asyncRoute(async (req, res) => {
      const limit = pageLimit(req.query.limit);
      const status =
        typeof req.query.status === "string" ? req.query.status : undefined;
      const data = await prisma.accountApplication.findMany({
        where: status ? { status: status as any } : undefined,
        take: limit,
        orderBy: { createdAt: "desc" },
        include: {
          requestedRole: true,
          requestedClearance: true,
          documents: true,
          history: { orderBy: { createdAt: "desc" } },
        },
      });
      res.json({
        data: data.map(safeApplication),
        page: { nextCursor: null, limit },
      });
    }),
  );
  router.patch(
    "/applications/:id",
    requireAuth,
    authorize("application:review", 3),
    validate(
      z
        .object({
          status: z.enum(["APPROVED", "REJECTED"]),
          reviewNote: z.string().min(5).max(4000),
        })
        .strict(),
    ),
    asyncRoute(async (req, res) => {
      const p = (req as AuthRequest).principal!;
      const current = await prisma.accountApplication.findUnique({
        where: { id: id(req) },
        include: { requestedRole: true, requestedClearance: true },
      });
      if (!current) throw notFound("Application");
      if (current.status !== "PENDING")
        throw new AppError(
          409,
          "APPLICATION_ALREADY_REVIEWED",
          "Application has already been reviewed",
        );
      let temporaryPassword: string | undefined;
      const result = await prisma.$transaction(async (tx) => {
        const app = await tx.accountApplication.update({
          where: { id: current.id },
          data: {
            status: req.body.status,
            reviewedBy: p.userId,
            reviewedAt: new Date(),
            reviewReason: req.body.reviewNote,
          },
        });
        await tx.applicationReviewHistory.create({
          data: {
            applicationId: current.id,
            previousStatus: current.status,
            newStatus: req.body.status,
            reviewerId: p.userId,
            note: req.body.reviewNote,
          },
        });
        if (req.body.status === "APPROVED") {
          let user = await tx.user.findUnique({
            where: { email: current.email },
          });
          if (user) {
            await tx.user.update({
              where: { id: user.id },
              data: {
                status: "ACTIVE",
                ...(current.requestedRoleId
                  ? { roleId: current.requestedRoleId }
                  : {}),
                ...(current.requestedClearanceLevelId
                  ? { clearanceLevelId: current.requestedClearanceLevelId }
                  : {}),
              },
            });
          } else {
            const role = current.requestedRoleId
              ? null
              : await tx.role.findUnique({ where: { code: "REPORTER" } });
            const clearance = current.requestedClearanceLevelId
              ? null
              : await tx.clearanceLevel.findUnique({
                  where: { code: "RESTRICTED" },
                });
            if (
              (!current.requestedRoleId && !role) ||
              (!current.requestedClearanceLevelId && !clearance)
            )
              throw new AppError(
                503,
                "ACCESS_DEFAULTS_UNAVAILABLE",
                "Default access policy is not configured",
              );
            temporaryPassword = randomBytes(18).toString("base64url");
            await tx.user.create({
              data: {
                email: current.email,
                displayName: current.displayName,
                passwordHash: await argon2.hash(temporaryPassword, {
                  type: argon2.argon2id,
                }),
                status: "ACTIVE",
                roleId: current.requestedRoleId || role!.id,
                clearanceLevelId:
                  current.requestedClearanceLevelId || clearance!.id,
                preferences: {
                  mustChangePassword: true,
                  provisionedFromApplication: current.id,
                },
              },
            });
          }
        }
        return app;
      });
      await audit(req as AuthRequest, {
        action: `application.${req.body.status.toLowerCase()}`,
        resourceType: "application",
        resourceId: current.id,
        decision: "ALLOW",
        metadata: { previousStatus: current.status },
      });
      res.json({
        ...safeApplication(result),
        ...(temporaryPassword
          ? {
              oneTimeCredential: {
                temporaryPassword,
                mustChangePassword: true,
              },
            }
          : {}),
      });
    }),
  );

  router.post(
    "/auth/refresh",
    validate(z.object({ refreshToken: z.string().min(20) }).strict()),
    asyncRoute(async (req, res) =>
      res.json(await auth.refresh(req.body.refreshToken)),
    ),
  );
  router.post(
    "/auth/password/request",
    validate(z.object({ email: z.string().email() }).strict()),
    asyncRoute(async (req, res) => {
      const token = await auth.requestPasswordReset(req.body.email);
      res
        .status(202)
        .json({
          accepted: true,
          ...(env.NODE_ENV === "development" && token
            ? { developmentResetToken: token }
            : {}),
        });
    }),
  );
  router.post(
    "/auth/password/reset",
    validate(
      z
        .object({
          token: z.string().min(20),
          password: z.string().min(12).max(200),
        })
        .strict(),
    ),
    asyncRoute(async (req, res) => {
      await auth.resetPassword(req.body.token, req.body.password);
      res.status(204).end();
    }),
  );
  router.post(
    "/me/password",
    requireAuth,
    validate(
      z
        .object({
          currentPassword: z.string().min(8),
          newPassword: z.string().min(12).max(200),
        })
        .strict(),
    ),
    asyncRoute(async (req, res) => {
      const p = (req as AuthRequest).principal!;
      await auth.changePassword(
        p.userId,
        req.body.currentPassword,
        req.body.newPassword,
        p.sessionId,
      );
      await audit(req as AuthRequest, {
        action: "user.password.change",
        resourceType: "user",
        resourceId: p.userId,
        decision: "ALLOW",
      });
      res.status(204).end();
    }),
  );
  router.patch(
    "/me/profile",
    requireAuth,
    validate(
      z
        .object({
          profileImageUrl: z.string().url().max(1000).nullable().optional(),
          preferences: z.record(z.string(), z.unknown()).optional(),
        })
        .strict(),
    ),
    asyncRoute(async (req, res) => {
      const p = (req as AuthRequest).principal!;
      const user = await prisma.user.update({
        where: { id: p.userId },
        data: req.body,
        include: { role: true, clearance: true },
      });
      await audit(req as AuthRequest, {
        action: "user.profile.update",
        resourceType: "user",
        resourceId: p.userId,
        decision: "ALLOW",
      });
      res.json(safeUser(user, true));
    }),
  );

  router.get(
    "/users",
    requireAuth,
    authorize("user:read", 3),
    asyncRoute(async (req, res) => {
      const limit = pageLimit(req.query.limit);
      const data = await prisma.user.findMany({
        where: {
          ...(typeof req.query.status === "string"
            ? { status: req.query.status as any }
            : {}),
          ...(typeof req.query.role === "string"
            ? { role: { code: req.query.role } }
            : {}),
          ...(req.query.clearanceRank
            ? { clearance: { rank: Number(req.query.clearanceRank) } }
            : {}),
        },
        take: limit,
        orderBy: { createdAt: "desc" },
        include: { role: true, clearance: true },
      });
      res.json({
        data: data.map((x) => safeUser(x, true)),
        page: { nextCursor: null, limit },
      });
    }),
  );
  router.get(
    "/users/:id",
    requireAuth,
    authorize("user:read", 3),
    asyncRoute(async (req, res) => {
      const user = await prisma.user.findUnique({
        where: { id: id(req) },
        include: {
          role: true,
          clearance: true,
          sessions: {
            select: {
              id: true,
              deviceInfo: true,
              createdAt: true,
              lastUsedAt: true,
              expiresAt: true,
              revokedAt: true,
            },
            orderBy: { createdAt: "desc" },
            take: 10,
          },
        },
      });
      if (!user) throw notFound("User");
      res.json({
        ...safeUser(user, true),
        clearanceRank: user.clearance.rank,
        sessions: user.sessions,
      });
    }),
  );
  router.patch(
    "/users/:id",
    requireAuth,
    authorize("user:manage", 4),
    validate(
      z
        .object({
          status: z
            .enum(["ACTIVE", "SUSPENDED", "DISABLED", "REJECTED"])
            .optional(),
          roleId: z.string().uuid().optional(),
          clearanceLevelId: z.string().uuid().optional(),
          reason: z.string().min(10).max(2000),
        })
        .strict(),
    ),
    asyncRoute(async (req, res) => {
      const target = id(req),
        p = (req as AuthRequest).principal!;
      if (
        target === p.userId &&
        req.body.status &&
        req.body.status !== "ACTIVE"
      )
        throw new AppError(
          409,
          "SELF_LOCKOUT_PREVENTED",
          "Administrators cannot deactivate their current account",
        );
      const before = await prisma.user.findUnique({ where: { id: target } });
      if (!before) throw notFound("User");
      const { reason, ...changes } = req.body;
      const user = await prisma.user.update({
        where: { id: target },
        data: changes,
        include: { role: true, clearance: true },
      });
      if (changes.status && changes.status !== "ACTIVE")
        await prisma.authSession.updateMany({
          where: { userId: target, revokedAt: null },
          data: { revokedAt: new Date() },
        });
      await audit(req as AuthRequest, {
        action: "user.access.update",
        resourceType: "user",
        resourceId: target,
        decision: "ALLOW",
        metadata: { reason, changes: Object.keys(changes) },
      });
      res.json(safeUser(user, true));
    }),
  );

  router.get(
    "/dashboard/summary",
    requireAuth,
    asyncRoute(async (req, res) => {
      const p = (req as AuthRequest).principal!;
      const investigationWhere = {
        minimumClearanceRank: { lte: p.clearanceRank },
        OR: [
          { createdBy: p.userId },
          { shared: true },
          ...(p.permissions.includes("investigation:read:any") ? [{}] : []),
        ],
      };
      const [
        models,
        openInvestigations,
        recentInvestigations,
        subjectCount,
        relationshipCount,
        activity,
      ] = await Promise.all([
        p.permissions.includes("model:read")
          ? prisma.modelRegistry.count({ where: { status: "ACTIVE" } })
          : 0,
        p.permissions.includes("investigation:read")
          ? prisma.investigation.count({
              where: { ...investigationWhere, status: { not: "CLOSED" } },
            })
          : 0,
        p.permissions.includes("investigation:read")
          ? prisma.investigation.findMany({
              where: investigationWhere,
              take: 5,
              orderBy: { updatedAt: "desc" },
              include: { subject: true },
            })
          : [],
        p.permissions.includes("subject:read")
          ? prisma.subject.count({
              where: { classificationRank: { lte: p.clearanceRank } },
            })
          : 0,
        p.permissions.includes("graph:read") ? prisma.graphEdge.count() : 0,
        prisma.auditEvent.findMany({
          where: { actorUserId: p.userId },
          take: 8,
          orderBy: { createdAt: "desc" },
          select: {
            id: true,
            action: true,
            resourceType: true,
            resourceId: true,
            decision: true,
            createdAt: true,
          },
        }),
      ]);
      let clearanceDistribution: any[] = [],
        dependencies: any = undefined;
      if (p.permissions.includes("user:read") && p.clearanceRank >= 4) {
        const users = await prisma.user.findMany({
          select: { clearance: { select: { code: true, name: true, rank: true } } },
        });
        const counts = new Map<string, { code: string; name: string; rank: number; count: number }>();
        for (const user of users) {
          const current = counts.get(user.clearance.code);
          counts.set(user.clearance.code, {
            code: user.clearance.code,
            name: user.clearance.name,
            rank: user.clearance.rank,
            count: (current?.count || 0) + 1,
          });
        }
        clearanceDistribution = [...counts.values()].sort((a, b) => a.rank - b.rank);
      }
      if (p.permissions.includes("health:dependencies:read")) {
        const [aiState, ragState] = await Promise.all([
          fetch(`${env.AI_ENGINE_BASE_URL}/health`)
            .then((r) => (r.ok ? "ok" : "degraded"))
            .catch(() => "unavailable"),
          rag.health(),
        ]);
        dependencies = { postgres: "ok", aiEngine: aiState, rag: ragState };
      }
      res.json({
        metrics: {
          availableModels: models,
          openInvestigations,
          totalAuthorizedSubjects: subjectCount,
          relationships: relationshipCount,
        },
        recentInvestigations: recentInvestigations.map((x) => ({
          id: x.id,
          title: x.title,
          status: x.status,
          subject: {
            id: x.subject.id,
            label: x.subject.displayLabel,
            type: x.subject.subjectType,
          },
          updatedAt: x.updatedAt,
        })),
        recentActivity: activity,
        clearanceDistribution,
        health: {
          status:
            dependencies && Object.values(dependencies).every((x) => x === "ok")
              ? "ok"
              : dependencies
                ? "degraded"
                : "available",
          ...(dependencies ? { services: dependencies } : {}),
        },
        generatedAt: new Date(),
      });
    }),
  );
  router.get(
    "/dashboard/top-suspects",
    requireAuth,
    authorize("subject:read", 2),
    asyncRoute(async (req, res) => {
      const p = (req as AuthRequest).principal!;
      const findings = await prisma.investigationFinding.findMany({
        where: {
          score: { not: null },
          investigation: {
            minimumClearanceRank: { lte: p.clearanceRank },
            OR: [
              { createdBy: p.userId },
              { shared: true },
              ...(p.permissions.includes("investigation:read:any") ? [{}] : []),
            ],
          },
        },
        orderBy: { score: "desc" },
        take: 30,
        include: { investigation: { include: { subject: true } } },
      });
      const seen = new Set<string>();
      const data = findings
        .filter((x) => {
          const key = x.investigation.subjectId;
          if (seen.has(key)) return false;
          seen.add(key);
          return true;
        })
        .slice(0, 3)
        .map((x) => ({
          subject: {
            id: x.investigation.subject.id,
            label: x.investigation.subject.displayLabel,
            type: x.investigation.subject.subjectType,
            status: x.investigation.subject.status,
          },
          risk: {
            dimension: x.findingType,
            score: x.score,
            confidence: x.confidence,
            severity: x.severity,
            explanation: x.summary,
          },
          model: { version: x.modelVersion, source: x.sourceComponent },
          observedAt: x.createdAt,
          investigationId: x.investigationId,
        }));
      res.json({
        data,
        generatedAt: new Date(),
        provenance: "persisted investigation findings",
      });
    }),
  );

  router.patch(
    "/investigations/:id",
    requireAuth,
    authorize("investigation:update", 2),
    validate(
      z
        .object({
          title: z.string().min(1).max(200).optional(),
          purpose: z.string().min(1).max(2000).optional(),
          status: z.enum(["OPEN", "IN_REVIEW", "CLOSED"]).optional(),
          shared: z.boolean().optional(),
        })
        .strict(),
    ),
    asyncRoute(async (req, res) => {
      const p = (req as AuthRequest).principal!,
        item = await investigationFor(id(req), p);
      const updated = await prisma.investigation.update({
        where: { id: item.id },
        data: {
          ...req.body,
          ...(req.body.status === "CLOSED"
            ? { closedAt: new Date() }
            : req.body.status
              ? { closedAt: null }
              : {}),
        },
      });
      await audit(req as AuthRequest, {
        action: "investigation.update",
        resourceType: "investigation",
        resourceId: item.id,
        decision: "ALLOW",
        metadata: { fields: Object.keys(req.body) },
      });
      res.json(updated);
    }),
  );
  router.get(
    "/investigations/:id/timeline",
    requireAuth,
    authorize("investigation:read", 1),
    asyncRoute(async (req, res) => {
      const p = (req as AuthRequest).principal!,
        item = await investigationFor(id(req), p),
        limit = pageLimit(req.query.limit);
      const [runs, findings, feedback, exports, events] = await Promise.all([
        prisma.analysisRun.findMany({
          where: { investigationId: item.id },
          take: limit,
        }),
        prisma.investigationFinding.findMany({
          where: { investigationId: item.id },
          take: limit,
        }),
        prisma.investigationFeedback.findMany({
          where: { investigationId: item.id },
          take: limit,
        }),
        prisma.investigationExport.findMany({
          where: { investigationId: item.id },
          take: limit,
        }),
        prisma.auditEvent.findMany({
          where: { resourceType: "investigation", resourceId: item.id },
          take: limit,
        }),
      ]);
      const data = [
        {
          id: item.id,
          type: "INVESTIGATION_CREATED",
          timestamp: item.createdAt,
          title: "Investigation created",
        },
        ...runs.map((x) => ({
          id: x.id,
          type: "ANALYSIS_RUN",
          timestamp: x.createdAt,
          title: `Analysis ${x.status}`,
          status: x.status,
        })),
        ...findings.map((x) => ({
          id: x.id,
          type: "FINDING",
          timestamp: x.createdAt,
          title: x.title,
          severity: x.severity,
        })),
        ...feedback.map((x) => ({
          id: x.id,
          type: "FEEDBACK",
          timestamp: x.createdAt,
          title: `Analysis feedback: ${x.rating}`,
        })),
        ...exports.map((x) => ({
          id: x.id,
          type: "EXPORT",
          timestamp: x.createdAt,
          title: `${x.format} export ${x.status}`,
        })),
        ...events.map((x) => ({
          id: x.id,
          type: "ACTIVITY",
          timestamp: x.createdAt,
          title: x.action,
          decision: x.decision,
        })),
      ]
        .sort((a, b) => +new Date(b.timestamp) - +new Date(a.timestamp))
        .slice(0, limit);
      res.json({ data, page: { nextCursor: null, limit } });
    }),
  );
  router.post(
    "/investigations/:id/feedback",
    requireAuth,
    authorize("investigation:feedback", 2),
    validate(
      z
        .object({
          analysisRunId: z.string().uuid().optional(),
          rating: z.enum(["USEFUL", "PARTIAL", "NOT_USEFUL", "INCORRECT"]),
          rationale: z.string().min(10).max(4000),
          metadata: z.record(z.string(), z.unknown()).optional(),
        })
        .strict(),
    ),
    asyncRoute(async (req, res) => {
      const p = (req as AuthRequest).principal!,
        item = await investigationFor(id(req), p);
      if (req.body.analysisRunId) {
        const run = await prisma.analysisRun.findFirst({
          where: { id: req.body.analysisRunId, investigationId: item.id },
        });
        if (!run) throw notFound("Analysis run");
      }
      const record = await prisma.investigationFeedback.create({
        data: { investigationId: item.id, createdBy: p.userId, ...req.body },
      });
      await audit(req as AuthRequest, {
        action: "investigation.feedback",
        resourceType: "investigation",
        resourceId: item.id,
        decision: "ALLOW",
        metadata: { feedbackId: record.id, rating: record.rating },
      });
      res.status(201).json(record);
    }),
  );
  router.post(
    "/investigations/:id/exports",
    requireAuth,
    authorize("investigation:export", 3),
    validate(z.object({ format: z.enum(["JSON", "CSV", "PDF"]) }).strict()),
    asyncRoute(async (req, res) => {
      const p = (req as AuthRequest).principal!,
        item = await investigationFor(id(req), p);
      const job = await prisma.investigationExport.create({
        data: {
          investigationId: item.id,
          requestedBy: p.userId,
          format: req.body.format,
          status: "QUEUED",
        },
      });
      await audit(req as AuthRequest, {
        action: "investigation.export.request",
        resourceType: "investigation",
        resourceId: item.id,
        decision: "ALLOW",
        metadata: { jobId: job.id, format: job.format },
      });
      res
        .status(202)
        .json({
          jobId: job.id,
          status: job.status,
          format: job.format,
          createdAt: job.createdAt,
        });
    }),
  );

  router.get(
    "/activity",
    requireAuth,
    asyncRoute(async (req, res) => {
      const p = (req as AuthRequest).principal!,
        limit = pageLimit(req.query.limit);
      const data = await prisma.auditEvent.findMany({
        where: {
          actorUserId: p.userId,
          ...(typeof req.query.action === "string"
            ? { action: { startsWith: req.query.action } }
            : {}),
        },
        take: limit,
        orderBy: { createdAt: "desc" },
        select: {
          id: true,
          action: true,
          resourceType: true,
          resourceId: true,
          decision: true,
          reasonCode: true,
          requestId: true,
          metadata: true,
          createdAt: true,
        },
      });
      res.json({ data, page: { nextCursor: null, limit } });
    }),
  );

  router.get(
    "/news",
    asyncRoute(async (req, res) => {
      const limit = pageLimit(req.query.limit, 50);
      const data = await prisma.newsItem.findMany({
        where: { status: "PUBLISHED", publishedAt: { lte: new Date() } },
        take: limit,
        orderBy: { publishedAt: "desc" },
        select: {
          id: true,
          slug: true,
          title: true,
          description: true,
          body: true,
          imageRef: true,
          authorName: true,
          publishedAt: true,
          updatedAt: true,
        },
      });
      res.json({ data, page: { nextCursor: null, limit } });
    }),
  );
  router.get(
    "/news/admin",
    requireAuth,
    authorize("news:manage", 3),
    asyncRoute(async (req, res) => {
      const limit = pageLimit(req.query.limit);
      const data = await prisma.newsItem.findMany({
        take: limit,
        orderBy: { updatedAt: "desc" },
      });
      res.json({ data, page: { nextCursor: null, limit } });
    }),
  );
  router.post(
    "/news",
    requireAuth,
    authorize("news:manage", 3),
    validate(
      z
        .object({
          slug: z
            .string()
            .regex(/^[a-z0-9-]+$/)
            .max(120),
          title: z.string().min(3).max(240),
          description: z.string().min(10).max(1000),
          body: z.string().min(20).max(100000),
          imageRef: z.string().max(1000).optional(),
          authorName: z.string().max(160).optional(),
          status: z.enum(["DRAFT", "PUBLISHED"]).default("DRAFT"),
          metadata: z.record(z.string(), z.unknown()).optional(),
        })
        .strict(),
    ),
    asyncRoute(async (req, res) => {
      const p = (req as AuthRequest).principal!,
        record = await prisma.newsItem.create({
          data: {
            ...req.body,
            authorId: p.userId,
            publishedAt:
              req.body.status === "PUBLISHED" ? new Date() : undefined,
          },
        });
      await audit(req as AuthRequest, {
        action: "news.create",
        resourceType: "news",
        resourceId: record.id,
        decision: "ALLOW",
      });
      res.status(201).json(record);
    }),
  );
  router.patch(
    "/news/:id",
    requireAuth,
    authorize("news:manage", 3),
    validate(
      z
        .object({
          title: z.string().min(3).max(240).optional(),
          description: z.string().min(10).max(1000).optional(),
          body: z.string().min(20).max(100000).optional(),
          imageRef: z.string().max(1000).nullable().optional(),
          authorName: z.string().max(160).optional(),
          status: z.enum(["DRAFT", "PUBLISHED", "ARCHIVED"]).optional(),
          metadata: z.record(z.string(), z.unknown()).optional(),
        })
        .strict(),
    ),
    asyncRoute(async (req, res) => {
      const existing = await prisma.newsItem.findUnique({
        where: { id: id(req) },
      });
      if (!existing) throw notFound("News item");
      const record = await prisma.newsItem.update({
        where: { id: existing.id },
        data: {
          ...req.body,
          ...(req.body.status === "PUBLISHED" && !existing.publishedAt
            ? { publishedAt: new Date() }
            : req.body.status === "DRAFT"
              ? { publishedAt: null }
              : {}),
        },
      });
      await audit(req as AuthRequest, {
        action: "news.update",
        resourceType: "news",
        resourceId: record.id,
        decision: "ALLOW",
      });
      res.json(record);
    }),
  );
  router.post(
    "/contact",
    validate(
      z
        .object({
          name: z.string().min(2).max(120),
          email: z.string().email(),
          subject: z.string().max(200).optional(),
          message: z.string().min(20).max(10000),
          metadata: z.record(z.string(), z.unknown()).optional(),
        })
        .strict(),
    ),
    asyncRoute(async (req, res) => {
      const recent = await prisma.contactSubmission.count({
        where: {
          email: req.body.email.toLowerCase(),
          createdAt: { gte: new Date(Date.now() - 3600_000) },
        },
      });
      if (recent >= 3)
        throw new AppError(
          429,
          "CONTACT_RATE_LIMITED",
          "Too many recent contact submissions",
        );
      const record = await prisma.contactSubmission.create({
        data: {
          ...req.body,
          email: req.body.email.toLowerCase(),
          ipHash: req.ip ? hash(req.ip) : undefined,
        },
      });
      res
        .status(202)
        .json({
          id: record.id,
          status: "RECEIVED",
          createdAt: record.createdAt,
        });
    }),
  );
  router.post(
    "/bug-reports",
    validate(
      z
        .object({
          reporterName: z.string().max(120).optional(),
          contactEmail: z.string().email().optional(),
          description: z.string().min(20).max(20000),
          severity: z
            .enum(["LOW", "MEDIUM", "HIGH", "CRITICAL"])
            .default("MEDIUM"),
          requestId: z.string().uuid().optional(),
          clientVersion: z.string().max(100).optional(),
          diagnostics: z.record(z.string(), z.unknown()).optional(),
        })
        .strict(),
    ),
    asyncRoute(async (req, res) => {
      const record = await prisma.bugReport.create({ data: req.body });
      res
        .status(202)
        .json({
          id: record.id,
          status: record.status,
          severity: record.severity,
          createdAt: record.createdAt,
        });
    }),
  );
  router.get(
    "/bug-resolutions",
    asyncRoute(async (req, res) => {
      const limit = pageLimit(req.query.limit, 50);
      const data = await prisma.bugReport.findMany({
        where: { publicApproved: true, publicExplanation: { not: null } },
        take: limit,
        orderBy: { resolvedAt: "desc" },
        select: {
          id: true,
          severity: true,
          status: true,
          clientVersion: true,
          rootCause: true,
          workaround: true,
          publicExplanation: true,
          resolvedAt: true,
          updatedAt: true,
        },
      });
      res.json({ data, page: { nextCursor: null, limit } });
    }),
  );
  router.get(
    "/bug-reports",
    requireAuth,
    authorize("bug:manage", 3),
    asyncRoute(async (req, res) => {
      const limit = pageLimit(req.query.limit);
      const data = await prisma.bugReport.findMany({
        where:
          typeof req.query.status === "string"
            ? { status: req.query.status }
            : undefined,
        take: limit,
        orderBy: { createdAt: "desc" },
      });
      res.json({ data, page: { nextCursor: null, limit } });
    }),
  );
  router.patch(
    "/bug-reports/:id",
    requireAuth,
    authorize("bug:manage", 3),
    validate(
      z
        .object({
          status: z
            .enum(["OPEN", "TRIAGED", "IN_PROGRESS", "RESOLVED", "CLOSED"])
            .optional(),
          severity: z.enum(["LOW", "MEDIUM", "HIGH", "CRITICAL"]).optional(),
          assignedTo: z.string().uuid().nullable().optional(),
          rootCause: z.string().max(10000).optional(),
          resolutionNotes: z.string().max(20000).optional(),
          workaround: z.string().max(10000).optional(),
          publicExplanation: z.string().max(10000).optional(),
          publicApproved: z.boolean().optional(),
        })
        .strict(),
    ),
    asyncRoute(async (req, res) => {
      const existing = await prisma.bugReport.findUnique({
        where: { id: id(req) },
      });
      if (!existing) throw notFound("Bug report");
      const record = await prisma.bugReport.update({
        where: { id: existing.id },
        data: {
          ...req.body,
          ...(req.body.status === "RESOLVED" ? { resolvedAt: new Date() } : {}),
        },
      });
      await audit(req as AuthRequest, {
        action: "bug.update",
        resourceType: "bug_report",
        resourceId: record.id,
        decision: "ALLOW",
        metadata: { fields: Object.keys(req.body) },
      });
      res.json(record);
    }),
  );

  router.post(
    "/beta/applications",
    validate(
      z
        .object({
          email: z.string().email(),
          displayName: z.string().min(2).max(120),
          purpose: z.string().min(30).max(4000),
        })
        .strict(),
    ),
    asyncRoute(async (req, res) => {
      const pending = await prisma.betaApplication.findFirst({
        where: { email: req.body.email.toLowerCase(), status: "PENDING" },
      });
      if (pending)
        throw new AppError(
          409,
          "BETA_APPLICATION_PENDING",
          "A beta application is already pending",
        );
      const record = await prisma.betaApplication.create({
        data: { ...req.body, email: req.body.email.toLowerCase() },
      });
      res
        .status(202)
        .json({
          id: record.id,
          status: record.status,
          createdAt: record.createdAt,
        });
    }),
  );
  router.get(
    "/beta/applications",
    requireAuth,
    authorize("beta:review", 3),
    asyncRoute(async (req, res) => {
      const limit = pageLimit(req.query.limit);
      const data = await prisma.betaApplication.findMany({
        where:
          typeof req.query.status === "string"
            ? { status: req.query.status }
            : undefined,
        take: limit,
        orderBy: { createdAt: "desc" },
      });
      res.json({ data, page: { nextCursor: null, limit } });
    }),
  );
  router.patch(
    "/beta/applications/:id",
    requireAuth,
    authorize("beta:review", 3),
    validate(
      z
        .object({
          status: z.enum(["APPROVED", "REJECTED"]),
          reviewNote: z.string().min(5).max(2000),
        })
        .strict(),
    ),
    asyncRoute(async (req, res) => {
      const p = (req as AuthRequest).principal!,
        record = await prisma.betaApplication.update({
          where: { id: id(req) },
          data: { ...req.body, reviewedBy: p.userId, reviewedAt: new Date() },
        });
      await audit(req as AuthRequest, {
        action: `beta.${record.status.toLowerCase()}`,
        resourceType: "beta_application",
        resourceId: record.id,
        decision: "ALLOW",
      });
      res.json(record);
    }),
  );

  router.get(
    "/datasets",
    asyncRoute(async (req, res) => {
      const limit = pageLimit(req.query.limit, 100);
      const data = await prisma.datasetMetadata.findMany({
        where: { visibility: "PUBLIC" },
        take: limit,
        orderBy: { name: "asc" },
      });
      res.json({
        data: data.map((x) => ({
          ...x,
          recordCount: x.recordCount?.toString() || null,
        })),
        page: { nextCursor: null, limit },
      });
    }),
  );
  router.post(
    "/datasets/refresh",
    requireAuth,
    authorize("dataset:manage", 4),
    asyncRoute(async (req, res) => {
      const root = join(process.cwd(), "..", "data"),
        files = await readdir(root).catch(() => [] as string[]);
      let refreshed = 0;
      for (const file of files) {
        const path = join(root, file),
          info = await stat(path).catch(() => null);
        if (!info?.isFile()) continue;
        const extension = extname(file).toLowerCase();
        if (![".csv", ".json", ".parquet"].includes(extension)) continue;
        let columns: any[] = [];
        let recordCount: bigint | undefined;
        if (extension === ".csv") {
          const content = await readFile(path, "utf8");
          const lines = content.split(/\r?\n/).filter(Boolean);
          columns = (lines[0] || "")
            .split(",")
            .map((name) => ({ name: name.trim(), type: "unknown" }));
          recordCount = BigInt(Math.max(0, lines.length - 1));
        }
        await prisma.datasetMetadata.upsert({
          where: { code: basename(file, extension) },
          update: {
            name: file,
            sourceRef: `data/${file}`,
            recordCount,
            columns,
            lastScannedAt: new Date(),
            metadata: { extension, sizeBytes: info.size },
          },
          create: {
            code: basename(file, extension),
            name: file,
            sourceRef: `data/${file}`,
            recordCount,
            columns,
            metadata: { extension, sizeBytes: info.size },
          },
        });
        refreshed++;
      }
      await audit(req as AuthRequest, {
        action: "dataset.refresh",
        resourceType: "dataset",
        decision: "ALLOW",
        metadata: { refreshed },
      });
      res
        .status(202)
        .json({ status: "COMPLETED", refreshed, lastScannedAt: new Date() });
    }),
  );
  router.post(
    "/models/:id/download-tickets",
    requireAuth,
    authorize("model:download", 4),
    asyncRoute(async (req, res) => {
      const p = (req as AuthRequest).principal!,
        model = await prisma.modelRegistry.findUnique({
          where: { id: id(req) },
        });
      if (!model || model.status !== "ACTIVE")
        throw notFound("Available model");
      if (!model.artifactUri)
        throw new AppError(
          409,
          "MODEL_ARTIFACT_UNAVAILABLE",
          "Model artifact is not available for download",
        );
      const token = randomBytes(40).toString("base64url"),
        expiresAt = new Date(Date.now() + 5 * 60_000);
      const record = await prisma.modelDownloadTicket.create({
        data: {
          modelId: model.id,
          requestedBy: p.userId,
          tokenHash: hash(token),
          checksum: model.checksum,
          expiresAt,
        },
      });
      await audit(req as AuthRequest, {
        action: "model.download.ticket",
        resourceType: "model",
        resourceId: model.id,
        decision: "ALLOW",
        metadata: { ticketId: record.id },
      });
      res
        .status(201)
        .json({
          ticketId: record.id,
          downloadToken: token,
          expiresAt,
          checksum: model.checksum,
          auditReference: (req as AuthRequest).requestId,
        });
    }),
  );

  router.get(
    "/rag/conversations",
    requireAuth,
    authorize("rag:history:read", 3),
    asyncRoute(async (req, res) => {
      const p = (req as AuthRequest).principal!,
        limit = pageLimit(req.query.limit);
      const canReadAny =
        p.permissions.includes("rag:history:read:any") && p.clearanceRank >= 4;
      const data = await prisma.ragInteraction.findMany({
        where: {
          ...(canReadAny ? {} : { userId: p.userId }),
          ...(typeof req.query.scope === "string"
            ? { scope: req.query.scope as any }
            : {}),
          ...(typeof req.query.conversationId === "string"
            ? { conversationId: req.query.conversationId }
            : {}),
        },
        take: limit,
        orderBy: { createdAt: "desc" },
        select: {
          id: true,
          conversationId: true,
          requestId: true,
          ragRequestId: true,
          userId: true,
          scope: true,
          question: true,
          answer: true,
          sources: true,
          ragVersion: true,
          latencyMs: true,
          status: true,
          createdAt: true,
        },
      });
      res.json({ data, page: { nextCursor: null, limit } });
    }),
  );
  router.get(
    "/rag/documents",
    requireAuth,
    authorize("rag:documents:read", 3),
    asyncRoute(async (req, res) => {
      const limit = pageLimit(req.query.limit);
      const data = await prisma.ragDocumentRecord.findMany({
        take: limit,
        orderBy: { createdAt: "desc" },
      });
      res.json({ data, page: { nextCursor: null, limit } });
    }),
  );
  router.get(
    "/rag/documents/:id",
    requireAuth,
    authorize("rag:documents:read", 3),
    asyncRoute(async (req, res) => {
      const record = await prisma.ragDocumentRecord.findUnique({
        where: { id: id(req) },
      });
      if (!record) throw notFound("RAG document");
      res.json(record);
    }),
  );
  router.patch(
    "/rag/documents/:id",
    requireAuth,
    authorize("rag:ingest", 4),
    validate(z.object({ enabled: z.boolean() }).strict()),
    asyncRoute(async (req, res) => {
      const existing = await prisma.ragDocumentRecord.findUnique({
        where: { id: id(req) },
      });
      if (!existing) throw notFound("RAG document");
      if (existing.externalId)
        await rag.setDocumentEnabled(
          existing.externalId,
          req.body.enabled,
          (req as AuthRequest).requestId!,
        );
      const record = await prisma.ragDocumentRecord.update({
        where: { id: existing.id },
        data: {
          enabled: req.body.enabled,
          status: req.body.enabled ? "COMPLETED" : "DISABLED",
        },
      });
      await audit(req as AuthRequest, {
        action: req.body.enabled
          ? "rag.document.enable"
          : "rag.document.disable",
        resourceType: "knowledge_document",
        resourceId: record.id,
        decision: "ALLOW",
      });
      res.json(record);
    }),
  );
  return router;
}
