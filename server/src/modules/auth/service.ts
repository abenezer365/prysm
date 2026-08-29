import { createHash, randomBytes } from "node:crypto";
import argon2 from "argon2";
import { SignJWT } from "jose";
import { AppError } from "../../common/errors.js";
import type { Env } from "../../config/env.js";
import { prisma } from "../../config/database.js";

const enc = (value: string) => new TextEncoder().encode(value);
const hash = (value: string) => createHash("sha256").update(value).digest("hex");
const seconds = (ttl: string) => ttl.endsWith("m") ? Number(ttl.slice(0, -1)) * 60 : ttl.endsWith("d") ? Number(ttl.slice(0, -1)) * 86400 : Number(ttl.replace("s", ""));
const claims = (user: any, sessionId: string) => ({ userId: user.id, sessionId, status: user.status, role: user.role.code, clearanceRank: user.clearance.rank, permissions: user.role.permissions.map((x: any) => x.permission.code) });

export class AuthService {
  constructor(private env: Env) {}
  async login(email: string, password: string, metadata: { deviceInfo?: string; ip?: string; userAgent?: string }) {
    const user = await prisma.user.findUnique({ where: { email }, include: { role: { include: { permissions: { include: { permission: true } } } }, clearance: true } });
    if (!user || !(await argon2.verify(user.passwordHash, password))) throw new AppError(401, "INVALID_CREDENTIALS", "Invalid email or password");
    if (user.status !== "ACTIVE") throw new AppError(403, "ACCOUNT_INACTIVE", "Account is not active");
    const refreshToken = randomBytes(48).toString("base64url");
    const session = await prisma.authSession.create({ data: { userId: user.id, refreshTokenHash: hash(refreshToken), deviceInfo: metadata.deviceInfo, ipHash: metadata.ip ? hash(metadata.ip) : undefined, userAgentHash: metadata.userAgent ? hash(metadata.userAgent) : undefined, expiresAt: new Date(Date.now() + seconds(this.env.REFRESH_TOKEN_TTL) * 1000) } });
    const accessToken = await new SignJWT(claims(user, session.id)).setProtectedHeader({ alg: "HS256" }).setIssuer("prysm-backend").setAudience("prysm-api").setSubject(user.id).setIssuedAt().setExpirationTime(this.env.ACCESS_TOKEN_TTL).sign(enc(this.env.JWT_ACCESS_SECRET));
    return { accessToken, refreshToken: `${session.id}.${refreshToken}`, tokenType: "Bearer", expiresIn: seconds(this.env.ACCESS_TOKEN_TTL) };
  }
  async logout(sessionId: string) { await prisma.authSession.updateMany({ where: { id: sessionId, revokedAt: null }, data: { revokedAt: new Date() } }); }
}
export const safeUser = (user: any, sensitive = false) => ({ id: user.id, email: user.email, displayName: user.displayName, profileImageUrl: user.profileImageUrl, status: user.status, role: user.role?.code, clearance: user.clearance?.code, ...(sensitive ? { createdAt: user.createdAt, lastLoginAt: user.lastLoginAt } : {}) });
