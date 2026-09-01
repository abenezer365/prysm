import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();
const models = [
  { code: "anomaly", file: "anomaly_model.json", modelType: "ANOMALY" },
  { code: "supervised", file: "supervised_model.json", modelType: "SUPERVISED" },
  { code: "gnn-encoder", file: "gnn_encoder.json", modelType: "GRAPH_NEURAL_NETWORK" },
];

for (const model of models) {
  const artifactPath = join(process.cwd(), "..", "ai-engine", "artifacts", model.file);
  const content = await readFile(artifactPath);
  await prisma.modelRegistry.upsert({
    where: { code_version: { code: model.code, version: "1.0.0" } },
    update: { status: "ACTIVE", artifactUri: artifactPath, checksum: createHash("sha256").update(content).digest("hex") },
    create: { code: model.code, version: "1.0.0", modelType: model.modelType, status: "ACTIVE", artifactUri: artifactPath, checksum: createHash("sha256").update(content).digest("hex"), evaluationScope: "Prysm investigation decision support", isCalibratedProbability: false },
  });
}
await prisma.$disconnect();
console.log(`Synchronized ${models.length} active model artifacts.`);
