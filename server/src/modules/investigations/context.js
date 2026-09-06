import { z } from "zod";
import { prisma } from "../../config/database.js";
import { AppError, notFound } from "../../common/errors.js";
export class InvestigationContextBuilder {
  async build(subjectId, options) {
    const cutoff = z.coerce.date().parse(options.cutoffAt);
    const subject = await prisma.subject.findUnique({
      where: { id: subjectId },
    });
    if (!subject) throw notFound("Subject");
    if (!subject.externalRef)
      throw new AppError(
        409,
        "SUBJECT_NOT_LINKED",
        "Subject has no canonical intelligence reference",
      );
    return {
      version: "prysm-intelligence-v2",
      subject: {
        id: subject.id,
        type: subject.subjectType,
        externalRef: subject.externalRef,
      },
      cutoffAt: cutoff.toISOString(),
      dataSnapshot: "canonical-engine-source",
    };
  }
}
