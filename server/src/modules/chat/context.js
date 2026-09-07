import { AppError, notFound } from "../../common/errors.js";
import { prisma } from "../../config/database.js";
import { enforceOwnership } from "../../middleware/security.js";
import { validateIntelligence } from "../../integrations/ai-engine/adapter.js";
export class AuthorizedChatContextBuilder {
  async forInvestigation(investigationId, principal) {
    const item = await prisma.investigation.findUnique({
      where: { id: investigationId },
      include: {
        subject: true,
        runs: {
          where: { status: "SUCCEEDED" },
          orderBy: { createdAt: "desc" },
          take: 1,
        },
      },
    });
    if (!item) throw notFound("Investigation");
    enforceOwnership(item.createdBy, principal, item.shared);
    if (
      principal.clearanceRank <
      Math.max(item.minimumClearanceRank, item.subject.classificationRank)
    )
      throw new AppError(
        403,
        "INSUFFICIENT_CLEARANCE",
        "Investigation classification exceeds clearance",
      );
    if (!item.runs[0])
      throw new AppError(
        409,
        "ANALYSIS_REQUIRED",
        "Complete an analysis before requesting an explanation",
      );
    const intelligence = validateIntelligence(item.runs[0].responsePayload);
    if (Date.parse(intelligence.investigation_window.cutoff) !== +item.cutoffAt)
      throw new AppError(
        409,
        "ANALYSIS_STALE",
        "Analyze the current investigation cutoff first",
      );
    return {
      subjectId: item.subjectId,
      investigationId,
      runId: item.runs[0].id,
      context: {
        intelligence,
        investigation: { cutoffAt: item.cutoffAt.toISOString() },
      },
    };
  }
}
