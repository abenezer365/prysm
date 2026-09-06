import { createHash } from "node:crypto";
import { prisma } from "../../config/database.js";
const hash = (x) => createHash("sha256").update(x).digest("hex");
export async function audit(req, event) {
  await prisma.auditEvent.create({
    data: {
      actorUserId: req.principal?.userId,
      requestId: req.requestId,
      ipHash: req.ip ? hash(req.ip) : undefined,
      userAgentHash: req.header("user-agent")
        ? hash(req.header("user-agent"))
        : undefined,
      ...event,
    },
  });
}
