import { Prisma } from "@prisma/client";
import { AppError, notFound } from "../../common/errors.js";
import type { Principal } from "../../common/types.js";
import { prisma } from "../../config/database.js";
import { enforceOwnership } from "../../middleware/security.js";
import { InvestigationContextBuilder } from "../investigations/context.js";

const asObject = (value: Prisma.JsonValue | null): Record<string, any> => value && typeof value === "object" && !Array.isArray(value) ? value as Record<string, any> : {};
export class AuthorizedChatContextBuilder {
  constructor(private operational = new InvestigationContextBuilder()) {}
  async forInvestigation(investigationId: string, principal: Principal) {
    const investigation = await prisma.investigation.findUnique({ where: { id: investigationId }, include: { subject: true, findings: { orderBy: { createdAt: "desc" }, take: 25, include: { evidence: { take: 10, include: { evidence: true } } } }, runs: { where: { status: "SUCCEEDED" }, orderBy: { createdAt: "desc" }, take: 1 } } });
    if (!investigation) throw notFound("Investigation"); enforceOwnership(investigation.createdBy, principal, investigation.shared);
    if (principal.clearanceRank < investigation.minimumClearanceRank) throw new AppError(403, "INSUFFICIENT_CLEARANCE", "Investigation classification exceeds clearance");
    const cutoff=investigation.cutoffAt || new Date(); const operational=await this.operational.build(investigation.subjectId,{cutoffAt:cutoff,lookbackDays:365,maxHops:2,maxNodes:75}); const latest=investigation.runs[0]; const result=asObject(latest?.responsePayload || null);
    return { subjectId: investigation.subjectId, investigationId, context: { contractVersion:"prysm-authorized-rag-context-v1", subject:{id:investigation.subject.id,type:investigation.subject.subjectType,label:investigation.subject.displayLabel}, investigation:{id:investigation.id,title:investigation.title,purpose:investigation.purpose,status:investigation.status,cutoffAt:cutoff.toISOString()}, assessment:result.assessment || null, components:result.components || {}, graphIntelligence:result.graphIntelligence || {available:false}, findings:investigation.findings.map(f=>({id:f.id,type:f.findingType,severity:f.severity,score:f.score,confidence:f.confidence,title:f.title,summary:f.summary,sourceComponent:f.sourceComponent,modelVersion:f.modelVersion,evidence:f.evidence.map(link=>({id:link.evidence.id,label:link.evidence.label,eventTime:link.evidence.eventTime,sourceType:link.evidence.sourceType,sourceId:link.evidence.sourceId}))})), limitations:Array.isArray(result.limitations)?result.limitations:[], modelVersions:result.modelVersions || latest?.modelVersions || {}, provenance:{requestingRole:principal.role,clearanceRank:principal.clearanceRank,contextVersion:operational.version,dataSnapshot:operational.dataSnapshot,cutoffAt:operational.cutoffAt,futureEventsExcluded:true}, relationships:operational.graph.edges.slice(0,150).map((e:any)=>({sourceNodeId:e.sourceNodeId,targetNodeId:e.targetNodeId,edgeType:e.edgeType,firstSeenAt:e.firstSeenAt,lastSeenAt:e.lastSeenAt})), transactionSummary:{count:operational.transactions.length} } };
  }
}
