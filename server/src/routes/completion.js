import { listQueries } from "./queries.js";
import { createHash, randomBytes } from "node:crypto";
import { syncMetadata } from "../modules/metadata.js";
import argon2 from "argon2";
import { Router } from "express";
import { z } from "zod";
import { AppError, notFound } from "../common/errors.js";
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
const asyncRoute = (fn) => (req, res, next) =>
  Promise.resolve(fn(req, res, next)).catch(next);
const id = (req, name = "id") => {
  const value = req.params[name];
  if (!value || Array.isArray(value))
    throw new AppError(400, "INVALID_PATH_PARAMETER", `Invalid ${name}`);
  return z.string().uuid().parse(value);
};
const pageLimit = (value, max = 100) =>
  z.coerce.number().int().min(1).max(max).default(20).parse(value);
const hash = (value) => createHash("sha256").update(value).digest("hex");
const safeApplication = (x) => ({
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
    x.documents?.map((d) => ({
      id: d.id,
      fileName: d.fileName,
      mimeType: d.mimeType,
      sizeBytes: d.sizeBytes,
      scanStatus: d.scanStatus,
      metadata: d.metadata,
    })) || [],
  history: x.history || [],
});
async function investigationFor(idValue, p) {
  const item = await prisma.investigation.findUnique({
    where: { id: idValue },
    include: { subject: true },
  });
  if (!item) throw notFound("Investigation");
  enforceOwnership(item.createdBy, p, item.shared);
  if (
    p.clearanceRank <
    Math.max(item.minimumClearanceRank, item.subject.classificationRank)
  )
    throw new AppError(
      403,
      "INSUFFICIENT_CLEARANCE",
      "Investigation classification exceeds clearance",
    );
  return item;
}
export function completionRoutes(env) {
  const router = Router(),
    requireAuth = authenticate(env.JWT_ACCESS_SECRET),
    auth = new AuthService(env),
    rag = new RagAdapter(env);
  router.use((req, _res, next) => {
    try {
      req.validatedQuery =
        req.method === "GET" && listQueries[req.path]
          ? listQueries[req.path].parse(req.query)
          : req.query;
      next();
    } catch (error) {
      next(error);
    }
  });
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
            create: (body.supportingEvidence || []).map((d) => ({
              ...d,
              scanStatus: "METADATA_ONLY",
            })),
          },
        },
      });
      res.status(202).json({
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
      const limit = pageLimit(req.validatedQuery.limit);
      const status =
        typeof req.validatedQuery.status === "string"
          ? req.validatedQuery.status
          : undefined;
      const data = await prisma.accountApplication.findMany({
        where: status ? { status: status } : undefined,
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
      const p = req.principal;
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
      if (
        (current.requestedClearance?.rank || 1) > p.clearanceRank ||
        (current.requestedRole?.code === "ADMIN" &&
          !p.permissions.includes("user:manage"))
      )
        throw new AppError(
          403,
          "ACCESS_GRANT_DENIED",
          "Requested privileges exceed reviewer authority",
        );
      let temporaryPassword;
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
                roleId: current.requestedRoleId || role.id,
                clearanceLevelId:
                  current.requestedClearanceLevelId || clearance.id,
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
      await audit(req, {
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
      res.status(202).json({
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
      const p = req.principal;
      await auth.changePassword(
        p.userId,
        req.body.currentPassword,
        req.body.newPassword,
        p.sessionId,
      );
      await audit(req, {
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
      const p = req.principal;
      const user = await prisma.user.update({
        where: { id: p.userId },
        data: req.body,
        include: { role: true, clearance: true },
      });
      await audit(req, {
        action: "user.profile.update",
        resourceType: "user",
        resourceId: p.userId,
        decision: "ALLOW",
      });
      res.json(safeUser(user, true));
    }),
  );
  router.patch(
    "/me/settings",
    requireAuth,
    validate(
      z
        .object({
          profileImageUrl: z.string().url().max(2000).nullable().optional(),
          preferences: z
            .object({
              compactMode: z.boolean().optional(),
              emailNotifications: z.boolean().optional(),
              reducedMotion: z.boolean().optional(),
            })
            .strict()
            .optional(),
        })
        .strict(),
    ),
    asyncRoute(async (req, res) => {
      const p = req.principal;
      const current = await prisma.user.findUniqueOrThrow({
        where: { id: p.userId },
      });
      const record = await prisma.user.update({
        where: { id: p.userId },
        data: {
          ...(req.body.profileImageUrl !== undefined
            ? { profileImageUrl: req.body.profileImageUrl }
            : {}),
          ...(req.body.preferences
            ? {
                preferences: {
                  ...(current.preferences || {}),
                  ...req.body.preferences,
                },
              }
            : {}),
        },
        include: { role: true, clearance: true },
      });
      await audit(req, {
        action: "user.settings.update",
        resourceType: "user",
        resourceId: p.userId,
        decision: "ALLOW",
        metadata: { fields: Object.keys(req.body) },
      });
      res.json(safeUser(record));
    }),
  );
  router.get(
    "/users",
    requireAuth,
    authorize("user:read", 3),
    asyncRoute(async (req, res) => {
      const limit = pageLimit(req.validatedQuery.limit);
      const data = await prisma.user.findMany({
        where: {
          ...(typeof req.validatedQuery.status === "string"
            ? { status: req.validatedQuery.status }
            : {}),
          ...(typeof req.validatedQuery.role === "string"
            ? { role: { code: req.validatedQuery.role } }
            : {}),
          ...(req.validatedQuery.clearanceRank
            ? { clearance: { rank: Number(req.validatedQuery.clearanceRank) } }
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
        p = req.principal;
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
      await audit(req, {
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
      const p = req.principal;
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
        null,
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
      let clearanceDistribution = [],
        dependencies = undefined;
      if (p.permissions.includes("user:read") && p.clearanceRank >= 4) {
        const users = await prisma.user.findMany({
          select: {
            clearance: { select: { code: true, name: true, rank: true } },
          },
        });
        const counts = new Map();
        for (const user of users) {
          const current = counts.get(user.clearance.code);
          counts.set(user.clearance.code, {
            code: user.clearance.code,
            name: user.clearance.name,
            rank: user.clearance.rank,
            count: (current?.count || 0) + 1,
          });
        }
        clearanceDistribution = [...counts.values()].sort(
          (a, b) => a.rank - b.rank,
        );
      }
      if (p.permissions.includes("health:dependencies:read")) {
        const [aiState, ragState] = await Promise.all([
          fetch(`${env.AI_ENGINE_BASE_URL}/health`, {
            signal: AbortSignal.timeout(2000),
          })
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
          operationalInventoryTotal: subjectCount,
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
      const p = req.principal,
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
      await audit(req, {
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
      const p = req.principal,
        item = await investigationFor(id(req), p),
        limit = pageLimit(req.validatedQuery.limit);
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
      const p = req.principal,
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
      await audit(req, {
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
    validate(z.object({ format: z.literal("JSON") }).strict()),
    asyncRoute(async (req, res) => {
      const p = req.principal,
        item = await investigationFor(id(req), p);
      const latest = await prisma.analysisRun.findFirst({
        where: { investigationId: item.id, status: "SUCCEEDED" },
        orderBy: { createdAt: "desc" },
      });
      if (!latest)
        throw new AppError(
          409,
          "ANALYSIS_REQUIRED",
          "Complete an analysis before exporting",
        );
      const job = await prisma.investigationExport.create({
        data: {
          investigationId: item.id,
          requestedBy: p.userId,
          format: req.body.format,
          status: "SUCCEEDED",
        },
      });
      await audit(req, {
        action: "investigation.export.request",
        resourceType: "investigation",
        resourceId: item.id,
        decision: "ALLOW",
        metadata: { jobId: job.id, format: job.format },
      });
      res.status(200).json({
        result: JSON.parse(latest.responsePayload),
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
      const p = req.principal,
        limit = pageLimit(req.validatedQuery.limit);
      const data = await prisma.auditEvent.findMany({
        where: {
          actorUserId: p.userId,
          ...(typeof req.validatedQuery.action === "string"
            ? { action: { startsWith: req.validatedQuery.action } }
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
      const limit = pageLimit(req.validatedQuery.limit, 50);
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
      const limit = pageLimit(req.validatedQuery.limit);
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
      const p = req.principal,
        record = await prisma.newsItem.create({
          data: {
            ...req.body,
            authorId: p.userId,
            publishedAt:
              req.body.status === "PUBLISHED" ? new Date() : undefined,
          },
        });
      await audit(req, {
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
      await audit(req, {
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
      res.status(202).json({
        id: record.id,
        status: "RECEIVED",
        createdAt: record.createdAt,
      });
    }),
  );
  router.post(
    "/intelligence-reports",
    validate(z.object({
      observed: z.string().min(20).max(20000),
      involved: z.string().min(2).max(5000),
      evidence: z.string().max(20000).optional(),
    }).strict()),
    asyncRoute(async (req, res) => {
      const record = await prisma.intelligenceReport.create({
        data: { ...req.body, ipHash: req.ip ? hash(req.ip) : undefined },
      });
      res.status(202).json({ id: record.id, status: record.status, createdAt: record.createdAt });
    }),
  );
  router.get(
    "/intelligence-reports",
    requireAuth,
    authorize("bug:manage", 3),
    asyncRoute(async (req, res) => {
      const limit = pageLimit(req.validatedQuery.limit);
      const data = await prisma.intelligenceReport.findMany({
        where: typeof req.validatedQuery.status === "string" ? { status: req.validatedQuery.status } : undefined,
        take: limit,
        orderBy: { createdAt: "desc" },
      });
      res.json({ data, page: { nextCursor: null, limit } });
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
      res.status(202).json({
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
      const limit = pageLimit(req.validatedQuery.limit, 50);
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
      const limit = pageLimit(req.validatedQuery.limit);
      const data = await prisma.bugReport.findMany({
        where:
          typeof req.validatedQuery.status === "string"
            ? { status: req.validatedQuery.status }
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
      await audit(req, {
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
      res.status(202).json({
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
      const limit = pageLimit(req.validatedQuery.limit);
      const data = await prisma.betaApplication.findMany({
        where:
          typeof req.validatedQuery.status === "string"
            ? { status: req.validatedQuery.status }
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
      const p = req.principal;
      const current = await prisma.betaApplication.findUnique({
        where: { id: id(req) },
      });
      if (!current) throw notFound("Beta application");
      if (current.status !== "PENDING")
        throw new AppError(
          409,
          "BETA_APPLICATION_ALREADY_REVIEWED",
          "Beta application has already been reviewed",
        );
      let temporaryPassword;
      const record = await prisma.$transaction(async (tx) => {
        const updated = await tx.betaApplication.update({
          where: { id: current.id },
          data: { ...req.body, reviewedBy: p.userId, reviewedAt: new Date() },
        });
        if (req.body.status === "APPROVED") {
          const role = await tx.role.findUnique({
            where: { code: "BETA_TESTER" },
          });
          const clearance = await tx.clearanceLevel.findUnique({
            where: { code: "RESTRICTED" },
          });
          if (!role || !clearance)
            throw new AppError(
              503,
              "BETA_ACCESS_POLICY_UNAVAILABLE",
              "Beta access policy is not configured",
            );
          const existing = await tx.user.findUnique({
            where: { email: current.email },
          });
          if (existing)
            await tx.user.update({
              where: { id: existing.id },
              data: {
                status: "ACTIVE",
                roleId: role.id,
                clearanceLevelId: clearance.id,
                preferences: { betaOnly: true, betaApplicationId: current.id },
              },
            });
          else {
            temporaryPassword = randomBytes(18).toString("base64url");
            await tx.user.create({
              data: {
                email: current.email,
                displayName: current.displayName,
                passwordHash: await argon2.hash(temporaryPassword, {
                  type: argon2.argon2id,
                }),
                status: "ACTIVE",
                roleId: role.id,
                clearanceLevelId: clearance.id,
                preferences: {
                  betaOnly: true,
                  mustChangePassword: true,
                  betaApplicationId: current.id,
                },
              },
            });
          }
        }
        return updated;
      });
      await audit(req, {
        action: `beta.${record.status.toLowerCase()}`,
        resourceType: "beta_application",
        resourceId: record.id,
        decision: "ALLOW",
      });
      res.json({
        ...record,
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
    "/contributors/applications",
    validate(
      z
        .object({
          email: z.string().email(),
          displayName: z.string().min(2).max(120),
          expertise: z.string().min(3).max(300),
          portfolioUrl: z.string().url().max(1000).optional(),
          motivation: z.string().min(50).max(5000),
          availability: z.string().max(300).optional(),
        })
        .strict(),
    ),
    asyncRoute(async (req, res) => {
      const pending = await prisma.contributorApplication.findFirst({
        where: { email: req.body.email.toLowerCase(), status: "PENDING" },
      });
      if (pending)
        throw new AppError(
          409,
          "CONTRIBUTOR_APPLICATION_PENDING",
          "A contributor application is already pending",
        );
      const record = await prisma.contributorApplication.create({
        data: { ...req.body, email: req.body.email.toLowerCase() },
      });
      res.status(202).json({
        id: record.id,
        status: record.status,
        createdAt: record.createdAt,
      });
    }),
  );
  router.get(
    "/contributors/applications",
    requireAuth,
    authorize("contributor:review", 3),
    asyncRoute(async (req, res) => {
      const limit = pageLimit(req.validatedQuery.limit);
      const status =
        typeof req.validatedQuery.status === "string"
          ? req.validatedQuery.status
          : undefined;
      const data = await prisma.contributorApplication.findMany({
        where: status ? { status } : undefined,
        orderBy: { createdAt: "desc" },
        take: limit,
      });
      res.json({ data, page: { nextCursor: null, limit } });
    }),
  );
  router.patch(
    "/contributors/applications/:id",
    requireAuth,
    authorize("contributor:review", 3),
    validate(
      z
        .object({
          status: z.enum(["APPROVED", "REJECTED"]),
          reviewNote: z.string().max(2000).optional(),
        })
        .strict(),
    ),
    asyncRoute(async (req, res) => {
      const existing = await prisma.contributorApplication.findUnique({
        where: { id: id(req) },
      });
      if (!existing) throw notFound("Contributor application");
      if (existing.status !== "PENDING")
        throw new AppError(
          409,
          "CONTRIBUTOR_APPLICATION_REVIEWED",
          "Contributor application has already been reviewed",
        );
      const principal = req.principal;
      const record = await prisma.contributorApplication.update({
        where: { id: existing.id },
        data: {
          status: req.body.status,
          reviewNote: req.body.reviewNote,
          reviewedBy: principal.userId,
          reviewedAt: new Date(),
        },
      });
      await audit(req, {
        action: "contributor.application.review",
        resourceType: "contributor_application",
        resourceId: record.id,
        decision: "ALLOW",
        metadata: { status: record.status },
      });
      res.json(record);
    }),
  );
  router.get(
    "/datasets",
    asyncRoute(async (req, res) => {
      const limit = pageLimit(req.validatedQuery.limit, 100);
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
      const refreshed = await syncMetadata();
      await audit(req, {
        action: "dataset.refresh",
        resourceType: "dataset",
        decision: "ALLOW",
        metadata: { refreshed },
      });
      res.json({ status: "COMPLETED", refreshed, lastScannedAt: new Date() });
    }),
  );
  router.get(
    "/rag/conversations",
    requireAuth,
    authorize("rag:history:read", 3),
    asyncRoute(async (req, res) => {
      const p = req.principal,
        limit = pageLimit(req.validatedQuery.limit);
      const canReadAny =
        p.permissions.includes("rag:history:read:any") && p.clearanceRank >= 4;
      const data = await prisma.ragInteraction.findMany({
        where: {
          ...(canReadAny ? {} : { userId: p.userId }),
          ...(typeof req.validatedQuery.scope === "string"
            ? { scope: req.validatedQuery.scope }
            : {}),
          ...(typeof req.validatedQuery.conversationId === "string"
            ? { conversationId: req.validatedQuery.conversationId }
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
      const limit = pageLimit(req.validatedQuery.limit);
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
          req.requestId,
        );
      const record = await prisma.ragDocumentRecord.update({
        where: { id: existing.id },
        data: {
          enabled: req.body.enabled,
          status: req.body.enabled ? "COMPLETED" : "DISABLED",
        },
      });
      await audit(req, {
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
