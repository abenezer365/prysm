import type { RequestHandler } from "express";
import { jwtVerify } from "jose";
import { AppError } from "../common/errors.js";
import type { AuthRequest, Principal } from "../common/types.js";

const bytes = (secret: string) => new TextEncoder().encode(secret);
export const authenticate = (secret: string): RequestHandler => async (req, _res, next) => {
  try {
    const raw = req.header("authorization");
    if (!raw?.startsWith("Bearer ")) throw new AppError(401, "AUTHENTICATION_REQUIRED", "Bearer access token required");
    const { payload } = await jwtVerify(raw.slice(7), bytes(secret), { issuer: "prysm-backend", audience: "prysm-api" });
    if (payload.status !== "ACTIVE") throw new AppError(403, "ACCOUNT_INACTIVE", "Account is not active");
    (req as AuthRequest).principal = payload as unknown as Principal; next();
  } catch (error) { next(error instanceof AppError ? error : new AppError(401, "INVALID_TOKEN", "Access token is invalid or expired")); }
};
export const authorize = (permission: string, minimumClearance = 0): RequestHandler => (req, _res, next) => {
  const principal = (req as AuthRequest).principal;
  if (!principal) return next(new AppError(401, "AUTHENTICATION_REQUIRED", "Authentication required"));
  if (!principal.permissions.includes(permission)) return next(new AppError(403, "PERMISSION_DENIED", "Permission denied"));
  if (principal.clearanceRank < minimumClearance) return next(new AppError(403, "INSUFFICIENT_CLEARANCE", "Security clearance is insufficient"));
  next();
};
export const enforceOwnership = (ownerId: string, principal: Principal, shared = false) => {
  if (ownerId !== principal.userId && !shared && !principal.permissions.includes("investigation:read:any")) throw new AppError(403, "RESOURCE_ACCESS_DENIED", "Resource access denied");
};
