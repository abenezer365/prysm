import { PrismaClient } from "@prisma/client";
const db = new PrismaClient();
try {
  await db.$queryRaw`SELECT 1`;
  const counts = {};
  for (const name of [
    "role",
    "clearanceLevel",
    "permission",
    "subject",
    "investigation",
    "analysisRun",
    "investigationFinding",
    "evidenceReference",
    "ragInteraction",
    "auditEvent",
  ])
    counts[name] = await db[name].count();
  const legacy =
    await db.$queryRaw`SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename IN ('transactions','graph_nodes','graph_edges','gnn_graph_snapshots','gnn_nodes','gnn_edges','gnn_embeddings','dataset_records')`;
  if (legacy.length)
    throw new Error("Apply Phase 5 migration: analytical tables remain");
  console.log(
    JSON.stringify({ status: "ok", counts, analyticalCopies: legacy.length }),
  );
} finally {
  await db.$disconnect();
}
