import { jwtVerify } from "jose";
import { AppError } from "../common/errors.js";
import { prisma } from "../config/database.js";
const bytes = (secret) => new TextEncoder().encode(secret);
export async function resolveAccessToken(secret, token) {
  const { payload } = await jwtVerify(token, bytes(secret), {
    issuer: "prysm-backend",
    audience: "prysm-api",
  });
  const sessionId = String(payload.sessionId || "");
  const session = await prisma.authSession.findUnique({
    where: { id: sessionId },
    include: {
      user: {
        include: {
          role: { include: { permissions: { include: { permission: true } } } },
          clearance: true,
        },
      },
    },
  });
  if (!session || session.revokedAt || session.expiresAt <= new Date())
    throw new AppError(401, "SESSION_REVOKED", "Session is revoked or expired");
  if (session.user.status !== "ACTIVE")
    throw new AppError(403, "ACCOUNT_INACTIVE", "Account is not active");
  return {
    userId: session.user.id,
    sessionId,
    status: session.user.status,
    role: session.user.role.code,
    clearanceRank: session.user.clearance.rank,
    permissions: session.user.role.permissions.map((x) => x.permission.code),
  };
}
export const authenticate = (secret) =>
  Object.assign(
    async (req, _res, next) => {
      try {
        const raw = req.header("authorization");
        if (!raw?.startsWith("Bearer "))
          throw new AppError(
            401,
            "AUTHENTICATION_REQUIRED",
            "Bearer access token required",
          );
        req.principal = await resolveAccessToken(secret, raw.slice(7));
        next();
      } catch (error) {
        if (["P1001", "P1002", "P2024"].includes(error?.code))
          return next(
            new AppError(
              503,
              "DATABASE_UNAVAILABLE",
              "Database is unavailable",
            ),
          );
        next(
          error instanceof AppError
            ? error
            : new AppError(
                401,
                "INVALID_TOKEN",
                "Access token is invalid or expired",
              ),
        );
      }
    },
    { authRequired: true },
  );
export const authorize = (permission, minimumClearance = 0) =>
  Object.assign(
    (req, _res, next) => {
      const principal = req.principal;
      if (!principal)
        return next(
          new AppError(
            401,
            "AUTHENTICATION_REQUIRED",
            "Authentication required",
          ),
        );
      if (!principal.permissions.includes(permission))
        return next(
          new AppError(403, "PERMISSION_DENIED", "Permission denied"),
        );
      if (principal.clearanceRank < minimumClearance)
        return next(
          new AppError(
            403,
            "INSUFFICIENT_CLEARANCE",
            "Security clearance is insufficient",
          ),
        );
      next();
    },
    { permission, minimumClearance },
  );
export const enforceOwnership = (ownerId, principal, shared = false) => {
  if (
    ownerId !== principal.userId &&
    !shared &&
    !principal.permissions.includes("investigation:read:any")
  )
    throw new AppError(403, "RESOURCE_ACCESS_DENIED", "Resource access denied");
};
