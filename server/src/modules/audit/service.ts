import { createHash } from "node:crypto";
import type { AuthRequest } from "../../common/types.js";
import { prisma } from "../../config/database.js";
const hash = (x: string) => createHash("sha256").update(x).digest("hex");
export async function audit(req: AuthRequest, event: { action: string; resourceType: string; resourceId?: string; decision: "ALLOW" | "DENY"; reasonCode?: string; metadata?: object }) { await prisma.auditEvent.create({ data: { actorUserId: req.principal?.userId, requestId: req.requestId, ipHash: req.ip ? hash(req.ip) : undefined, userAgentHash: req.header("user-agent") ? hash(req.header("user-agent")!) : undefined, ...event } }); }
