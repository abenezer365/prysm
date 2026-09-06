import { prisma } from "../../config/database.js";
import { AppError } from "../../common/errors.js";
export async function ensureConversation(
  conversationId,
  userId,
  investigationId,
) {
  if (!conversationId) return;
  const previous = await prisma.ragInteraction.findMany({
    where: { conversationId },
    select: { userId: true, contextManifest: true, scope: true },
  });
  if (
    previous.some(
      (row) =>
        row.userId !== userId ||
        row.scope !== "AUTHORIZED" ||
        row.contextManifest?.investigationId !== investigationId,
    )
  )
    throw new AppError(
      403,
      "CONVERSATION_ACCESS_DENIED",
      "Conversation belongs to another context",
    );
}
