import { Prisma } from "@prisma/client";
import { prisma } from "../../config/database.js";
import type { AiAnalysisResponse } from "../../integrations/ai-engine/adapter.js";

const json = (value: unknown): Prisma.InputJsonValue => JSON.parse(JSON.stringify(value)) as Prisma.InputJsonValue;
export async function persistAnalysis(runId: string, investigationId: string, result: AiAnalysisResponse) {
  return prisma.$transaction(async tx => {
    const evidenceByExternalId = new Map<string, string>();
    for (const raw of result.evidence) {
      const externalId = String(raw.evidence_id || ""); if (!externalId) continue;
      const timestamps = Array.isArray(raw.timestamps) ? raw.timestamps : [];
      const eventTime = timestamps[0] ? new Date(String(timestamps[0])) : null;
      const record = await tx.evidenceReference.upsert({ where: { sourceType_sourceId: { sourceType: "AI_ENGINE", sourceId: externalId } }, update: { label: String(raw.description || raw.signal_type || "AI evidence"), excerpt: String(raw.description || ""), eventTime: eventTime && !Number.isNaN(eventTime.valueOf()) ? eventTime : null, metadata: json(raw) }, create: { sourceType: "AI_ENGINE", sourceId: externalId, label: String(raw.description || raw.signal_type || "AI evidence"), excerpt: String(raw.description || ""), eventTime: eventTime && !Number.isNaN(eventTime.valueOf()) ? eventTime : null, metadata: json(raw) } });
      evidenceByExternalId.set(externalId, record.id);
    }
    for (const [name, component] of Object.entries(result.components)) {
      if (component.status !== "available") continue;
      const finding = await tx.investigationFinding.create({ data: { investigationId, findingType: name.toUpperCase(), severity: component.strength != null && component.strength >= .75 ? "HIGH" : component.strength != null && component.strength >= .5 ? "MEDIUM" : "LOW", score: component.strength, confidence: component.confidence, title: `${name.replaceAll("_", " ")} signal`, summary: component.reason, sourceComponent: name.toUpperCase(), modelVersion: String(result.modelVersions[name] || result.engineVersion), metadata: json({ runId, assessmentType: result.assessment.type }) } });
      for (const externalId of component.evidence_ids) { const evidenceId = evidenceByExternalId.get(externalId); if (evidenceId) await tx.findingEvidence.create({ data: { findingId: finding.id, evidenceId, relevance: "SUPPORTING" } }); }
    }
    return tx.analysisRun.update({ where: { id: runId }, data: { status: "SUCCEEDED", responsePayload: json(result), aiEngineVersion: result.engineVersion, modelVersions: json(result.modelVersions), completedAt: new Date() } });
  });
}
