import { z } from "zod";
import { AppError, notFound } from "../../common/errors.js";
import { prisma } from "../../config/database.js";

export const contextOptionsSchema = z.object({ cutoffAt: z.coerce.date(), lookbackDays: z.number().int().min(1).max(1095).default(365), maxHops: z.number().int().min(1).max(3).default(2), maxNodes: z.number().int().min(1).max(250).default(100) });
export type ContextOptions = z.infer<typeof contextOptionsSchema>;
export type InvestigationContext = { version: "prysm-investigation-context-v1"; subject: { id: string; type: string; label: string; externalRef: string | null }; cutoffAt: string; lookbackStart: string; dataSnapshot: string; transactions: unknown[]; graph: { nodes: unknown[]; edges: unknown[]; truncated: boolean }; provenance: { futureEventsExcluded: true; graphDepth: number; maxNodes: number } };

export class InvestigationContextBuilder {
  async build(subjectId: string, raw: ContextOptions): Promise<InvestigationContext> {
    const options = contextOptionsSchema.parse(raw); const cutoff = options.cutoffAt; const start = new Date(cutoff.getTime() - options.lookbackDays * 86400000);
    const subject = await prisma.subject.findUnique({ where: { id: subjectId }, include: { graphNodes: true } });
    if (!subject) throw notFound("Subject");
    const transactions = await prisma.transaction.findMany({ where: { timestamp: { gte: start, lte: cutoff }, OR: [{ fromSubjectId: subjectId }, { toSubjectId: subjectId }, { fromAccountId: subjectId }, { toAccountId: subjectId }] }, orderBy: [{ timestamp: "desc" }, { id: "asc" }], take: 500, select: { id: true, sourceTransactionId: true, amount: true, currency: true, timestamp: true, transactionType: true, fromSubjectId: true, toSubjectId: true, fromAccountId: true, toAccountId: true } });
    const seed = subject.graphNodes.map((n: { id: string }) => n.id); const seen = new Set(seed); let frontier = seed; const edges: any[] = [];
    for (let hop = 0; hop < options.maxHops && frontier.length && seen.size < options.maxNodes; hop++) {
      const batch = await prisma.graphEdge.findMany({ where: { AND: [{ OR: [{ sourceNodeId: { in: frontier } }, { targetNodeId: { in: frontier } }] }, { OR: [{ validFrom: null }, { validFrom: { lte: cutoff } }] }, { OR: [{ validTo: null }, { validTo: { gte: cutoff } }] }, { OR: [{ firstSeenAt: null }, { firstSeenAt: { lte: cutoff } }] }] }, orderBy: { id: "asc" }, take: options.maxNodes * 4 });
      const next: string[] = []; for (const edge of batch) { if (edges.some(x => x.id === edge.id)) continue; edges.push(edge); for (const id of [edge.sourceNodeId, edge.targetNodeId]) if (!seen.has(id) && seen.size < options.maxNodes) { seen.add(id); next.push(id); } } frontier = next;
    }
    const nodes = await prisma.graphNode.findMany({ where: { id: { in: [...seen] } }, select: { id: true, subjectId: true, nodeType: true, externalKey: true, labelHash: true } });
    if (nodes.length > options.maxNodes) throw new AppError(500, "GRAPH_BOUND_VIOLATION", "Graph traversal exceeded configured bound");
    return { version: "prysm-investigation-context-v1", subject: { id: subject.id, type: subject.subjectType, label: subject.displayLabel, externalRef: subject.externalRef }, cutoffAt: cutoff.toISOString(), lookbackStart: start.toISOString(), dataSnapshot: `postgres:${cutoff.toISOString()}`, transactions, graph: { nodes, edges: edges.filter(e => seen.has(e.sourceNodeId) && seen.has(e.targetNodeId)), truncated: seen.size === options.maxNodes }, provenance: { futureEventsExcluded: true, graphDepth: options.maxHops, maxNodes: options.maxNodes } };
  }
}
