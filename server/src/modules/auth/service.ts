import { createHash, randomBytes } from "node:crypto";
import argon2 from "argon2";
import { SignJWT } from "jose";
import { AppError } from "../../common/errors.js";
import type { Env } from "../../config/env.js";
import { prisma } from "../../config/database.js";

const enc = (value: string) => new TextEncoder().encode(value);
const hash = (value: string) =>
  createHash("sha256").update(value).digest("hex");
const seconds = (ttl: string) =>
  ttl.endsWith("m")
    ? Number(ttl.slice(0, -1)) * 60
    : ttl.endsWith("d")
      ? Number(ttl.slice(0, -1)) * 86400
      : Number(ttl.replace("s", ""));
const claims = (user: any, sessionId: string) => ({
  userId: user.id,
  sessionId,
  status: user.status,
  role: user.role.code,
  clearanceRank: user.clearance.rank,
  permissions: user.role.permissions.map((x: any) => x.permission.code),
});

export class AuthService {
  constructor(private env: Env) {}
  private async accessToken(user: any, sessionId: string) {
    return new SignJWT(claims(user, sessionId))
      .setProtectedHeader({ alg: "HS256" })
      .setIssuer("prysm-backend")
      .setAudience("prysm-api")
      .setSubject(user.id)
      .setIssuedAt()
      .setExpirationTime(this.env.ACCESS_TOKEN_TTL)
      .sign(enc(this.env.JWT_ACCESS_SECRET));
  }
  async login(
    email: string,
    password: string,
    metadata: { deviceInfo?: string; ip?: string; userAgent?: string },
  ) {
    const user = await prisma.user.findUnique({
      where: { email },
      include: {
        role: { include: { permissions: { include: { permission: true } } } },
        clearance: true,
      },
    });
    if (!user || !(await argon2.verify(user.passwordHash, password)))
      throw new AppError(
        401,
        "INVALID_CREDENTIALS",
        "Invalid email or password",
      );
    if (user.status !== "ACTIVE")
      throw new AppError(403, "ACCOUNT_INACTIVE", "Account is not active");
    const refreshToken = randomBytes(48).toString("base64url");
    const session = await prisma.authSession.create({
      data: {
        userId: user.id,
        refreshTokenHash: hash(refreshToken),
        deviceInfo: metadata.deviceInfo,
        ipHash: metadata.ip ? hash(metadata.ip) : undefined,
        userAgentHash: metadata.userAgent
          ? hash(metadata.userAgent)
          : undefined,
        expiresAt: new Date(
          Date.now() + seconds(this.env.REFRESH_TOKEN_TTL) * 1000,
        ),
      },
    });
    const accessToken = await this.accessToken(user, session.id);
    return {
      accessToken,
      refreshToken: `${session.id}.${refreshToken}`,
      tokenType: "Bearer",
      expiresIn: seconds(this.env.ACCESS_TOKEN_TTL),
    };
  }
  async refresh(compoundToken: string) {
    const [sessionId, secret, extra] = compoundToken.split(".");
    if (!sessionId || !secret || extra)
      throw new AppError(
        401,
        "INVALID_REFRESH_TOKEN",
        "Refresh token is invalid",
      );
    const session = await prisma.authSession.findUnique({
      where: { id: sessionId },
      include: {
        user: {
          include: {
            role: {
              include: { permissions: { include: { permission: true } } },
            },
            clearance: true,
          },
        },
      },
    });
    if (
      !session ||
      session.revokedAt ||
      session.expiresAt <= new Date() ||
      session.refreshTokenHash !== hash(secret)
    ) {
      if (session && !session.revokedAt)
        await prisma.authSession.update({
          where: { id: session.id },
          data: { revokedAt: new Date() },
        });
      throw new AppError(
        401,
        "REFRESH_TOKEN_REUSED",
        "Refresh token is invalid, expired, or already rotated",
      );
    }
    if (session.user.status !== "ACTIVE")
      throw new AppError(403, "ACCOUNT_INACTIVE", "Account is not active");
    const nextSecret = randomBytes(48).toString("base64url");
    await prisma.authSession.update({
      where: { id: session.id },
      data: { refreshTokenHash: hash(nextSecret), lastUsedAt: new Date() },
    });
    return {
      accessToken: await this.accessToken(session.user, session.id),
      refreshToken: `${session.id}.${nextSecret}`,
      tokenType: "Bearer",
      expiresIn: seconds(this.env.ACCESS_TOKEN_TTL),
    };
  }
  async requestPasswordReset(email: string) {
    const user = await prisma.user.findUnique({
      where: { email: email.toLowerCase() },
    });
    if (!user || user.status !== "ACTIVE") return null;
    const token = randomBytes(40).toString("base64url");
    await prisma.passwordResetToken.create({
      data: {
        userId: user.id,
        tokenHash: hash(token),
        expiresAt: new Date(Date.now() + 30 * 60_000),
      },
    });
    return token;
  }
  async resetPassword(token: string, password: string) {
    const record = await prisma.passwordResetToken.findUnique({
      where: { tokenHash: hash(token) },
    });
    if (!record || record.usedAt || record.expiresAt <= new Date())
      throw new AppError(
        400,
        "RESET_TOKEN_INVALID",
        "Reset token is invalid or expired",
      );
    const passwordHash = await argon2.hash(password, { type: argon2.argon2id });
    await prisma.$transaction([
      prisma.user.update({
        where: { id: record.userId },
        data: { passwordHash },
      }),
      prisma.passwordResetToken.update({
        where: { id: record.id },
        data: { usedAt: new Date() },
      }),
      prisma.authSession.updateMany({
        where: { userId: record.userId, revokedAt: null },
        data: { revokedAt: new Date() },
      }),
    ]);
  }
  async changePassword(
    userId: string,
    currentPassword: string,
    nextPassword: string,
    currentSessionId: string,
  ) {
    const user = await prisma.user.findUnique({ where: { id: userId } });
    if (!user || !(await argon2.verify(user.passwordHash, currentPassword)))
      throw new AppError(
        400,
        "CURRENT_PASSWORD_INVALID",
        "Current password is incorrect",
      );
    if (await argon2.verify(user.passwordHash, nextPassword))
      throw new AppError(
        409,
        "PASSWORD_REUSE",
        "New password must be different",
      );
    await prisma.$transaction([
      prisma.user.update({
        where: { id: userId },
        data: {
          passwordHash: await argon2.hash(nextPassword, {
            type: argon2.argon2id,
          }),
          preferences: {
            ...((user.preferences as Record<string, unknown>) || {}),
            mustChangePassword: false,
          },
        },
      }),
      prisma.authSession.updateMany({
        where: { userId, id: { not: currentSessionId }, revokedAt: null },
        data: { revokedAt: new Date() },
      }),
    ]);
  }
  async logout(sessionId: string) {
    await prisma.authSession.updateMany({
      where: { id: sessionId, revokedAt: null },
      data: { revokedAt: new Date() },
    });
  }
}
export const safeUser = (user: any, sensitive = false) => ({
  id: user.id,
  email: user.email,
  displayName: user.displayName,
  profileImageUrl: user.profileImageUrl,
  preferences: user.preferences || {},
  status: user.status,
  role: user.role?.code,
  clearance: user.clearance?.code,
  ...(sensitive
    ? { createdAt: user.createdAt, lastLoginAt: user.lastLoginAt }
    : {}),
});
