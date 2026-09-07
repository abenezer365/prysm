import { prisma } from "../../config/database.js";
import { validateIntelligence } from "../../integrations/ai-engine/adapter.js";
export async function persistAnalysis(runId, investigationId, raw) {
  const result = validateIntelligence(raw);
  return prisma.$transaction(async (tx) => {
    for (const evidence of result.evidence) {
      const record = await tx.evidenceReference.upsert({
        where: {
          sourceType_sourceId: {
            sourceType: "AI_ENGINE",
            sourceId: evidence.evidence_id,
          },
        },
        update: {},
        create: {
          sourceType: "AI_ENGINE",
          sourceId: evidence.evidence_id,
          label: evidence.description || evidence.signal_type,
          metadata: evidence,
        },
      });
      await tx.investigationFinding.create({
        data: {
          investigationId,
          findingType: evidence.signal_type,
          title: evidence.signal_type,
          summary: evidence.description,
          sourceComponent: evidence.signal_source,
          modelVersion: result.version,
          metadata: { runId },
          evidence: {
            create: { evidenceId: record.id, relevance: "SUPPORTING" },
          },
        },
      });
    }
    await tx.investigation.update({
      where: { id: investigationId },
      data: { aiEngineVersion: result.version },
    });
    return tx.analysisRun.update({
      where: { id: runId },
      data: {
        status: "SUCCEEDED",
        responsePayload: JSON.stringify(result),
        dataSnapshot: result.provenance.dataset_version,
        aiEngineVersion: result.version,
        modelVersions: result.provenance.model_training || {},
        completedAt: new Date(),
      },
    });
  });
}
