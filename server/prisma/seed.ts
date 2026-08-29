import argon2 from "argon2";
import { PrismaClient } from "@prisma/client";
const db = new PrismaClient();
const clearances = [["PUBLIC", 0], ["RESTRICTED", 1], ["CONFIDENTIAL", 2], ["SECRET", 3], ["TOP_SECRET", 4], ["TS_SCI", 5]] as const;
const permissions = ["health:dependencies:read", "investigation:read", "investigation:read:any", "investigation:create", "investigation:analyze", "subject:read", "subject:sensitive:read", "graph:read", "evidence:read", "model:read", "model:download", "chat:authorized", "rag:ingest", "audit:read", "user:read", "user:manage"];
const grants: Record<string, string[]> = {
  REPORTER: ["subject:read"],
  ANALYST: ["subject:read", "investigation:read", "investigation:create", "graph:read", "evidence:read", "model:read", "chat:authorized"],
  INVESTIGATOR: ["subject:read", "subject:sensitive:read", "investigation:read", "investigation:create", "investigation:analyze", "graph:read", "evidence:read", "model:read", "chat:authorized"],
  SENIOR_INVESTIGATOR: ["subject:read", "subject:sensitive:read", "investigation:read", "investigation:read:any", "investigation:create", "investigation:analyze", "graph:read", "evidence:read", "model:read", "chat:authorized"],
  ADMIN: permissions
};
async function main() {
  for (const [code, rank] of clearances) await db.clearanceLevel.upsert({ where: { code }, update: { rank }, create: { code, name: code.replaceAll("_", " "), rank } });
  for (const code of permissions) await db.permission.upsert({ where: { code }, update: {}, create: { code } });
  for (const [code, allowed] of Object.entries(grants)) { const role = await db.role.upsert({ where: { code }, update: {}, create: { code, name: code.replaceAll("_", " ") } }); const rows = await db.permission.findMany({ where: { code: { in: allowed } } }); for (const permission of rows) await db.rolePermission.upsert({ where: { roleId_permissionId: { roleId: role.id, permissionId: permission.id } }, update: {}, create: { roleId: role.id, permissionId: permission.id } }); }
  if (process.env.SEED_ADMIN_EMAIL && process.env.SEED_ADMIN_PASSWORD) { const role = await db.role.findUniqueOrThrow({ where: { code: "ADMIN" } }); const clearance = await db.clearanceLevel.findUniqueOrThrow({ where: { code: "TS_SCI" } }); await db.user.upsert({ where: { email: process.env.SEED_ADMIN_EMAIL }, update: {}, create: { email: process.env.SEED_ADMIN_EMAIL, displayName: "Development Administrator", passwordHash: await argon2.hash(process.env.SEED_ADMIN_PASSWORD, { type: argon2.argon2id }), status: "ACTIVE", roleId: role.id, clearanceLevelId: clearance.id } }); }
}
main().finally(() => db.$disconnect());
