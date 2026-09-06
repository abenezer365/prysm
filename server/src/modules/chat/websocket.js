import { randomUUID } from "node:crypto";
import { WebSocketServer, WebSocket } from "ws";
import { z } from "zod";
import { prisma } from "../../config/database.js";
import { resolveAccessToken } from "../../middleware/security.js";
import { AuthorizedChatContextBuilder } from "./context.js";
import { ensureConversation } from "./conversation.js";
import { RagAdapter } from "../../integrations/rag/adapter.js";
export function attachChatWebSocket(server, env) {
  const wss = new WebSocketServer({
    server,
    path: "/api/v1/ws/chat",
    maxPayload: 64 * 1024,
  });
  const contexts = new AuthorizedChatContextBuilder(),
    rag = new RagAdapter(env);
  wss.on("connection", (client) => {
    let token = null,
      busy = false;
    const send = (value) => {
      if (client.readyState === WebSocket.OPEN)
        client.send(JSON.stringify(value));
    };
    send({
      type: "ready",
      message: "Authenticate before sending chat messages.",
    });
    client.on("message", async (raw) => {
      if (busy) return send({ type: "error", code: "CHAT_BUSY" });
      busy = true;
      try {
        const data = JSON.parse(raw.toString());
        if (data.type === "authenticate") {
          token = null;
          const candidate = z.string().min(1).parse(data.accessToken);
          const p = await resolveAccessToken(env.JWT_ACCESS_SECRET, candidate);
          if (!p.permissions.includes("chat:authorized") || p.clearanceRank < 2)
            throw new Error();
          token = candidate;
          send({ type: "authenticated" });
          return;
        }
        if (!token)
          return send({ type: "error", code: "AUTHENTICATION_REQUIRED" });
        const p = await resolveAccessToken(env.JWT_ACCESS_SECRET, token);
        if (!p.permissions.includes("chat:authorized") || p.clearanceRank < 2)
          throw new Error();
        const input = z
          .object({
            question: z.string().trim().min(1).max(4000),
            investigationId: z.string().uuid(),
            conversationId: z.string().uuid().optional(),
          })
          .strict()
          .parse(data);
        const built = await contexts.forInvestigation(input.investigationId, p);
        await ensureConversation(
          input.conversationId,
          p.userId,
          input.investigationId,
        );
        const requestId = randomUUID(),
          conversationId = input.conversationId || randomUUID();
        const answer = await rag.askAuthorized(
          { ...input, context: built.context },
          requestId,
        );
        await prisma.ragInteraction.create({
          data: {
            conversationId,
            requestId,
            userId: p.userId,
            scope: "AUTHORIZED",
            question: input.question,
            answer: answer.answer,
            sources: answer.sources,
            accessScope: { role: p.role, clearanceRank: p.clearanceRank },
            contextManifest: {
              investigationId: built.investigationId,
              subjectId: built.subjectId,
              runId: built.runId,
              transport: "websocket",
              analysisFingerprint:
                built.context.intelligence.provenance.analysis_fingerprint,
            },
            ragVersion: "prysm-reasoning-v1",
            status: "SUCCEEDED",
          },
        });
        send({ type: "token", text: answer.answer, requestId });
        send({
          type: "done",
          requestId,
          conversationId,
          sources: answer.sources,
          evidence: answer.evidence,
          reasoning: answer.reasoning,
        });
      } catch (error) {
        send({
          type: "error",
          code:
            error.code && !error.code.startsWith("P")
              ? error.code
              : "CHAT_REQUEST_FAILED",
        });
      } finally {
        busy = false;
      }
    });
  });
  return wss;
}
