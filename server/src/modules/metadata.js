import { readFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { prisma } from "../config/database.js";
// Metadata only: no records, training labels, predictions or detection logic.
export async function syncMetadata() {
  const manifest = JSON.parse(
    await readFile(
      new URL(
        "../../../data/benchmarks/prysm-benchmark-v1/MANIFEST.json",
        import.meta.url,
      ),
      "utf8",
    ),
  );
  const model = await readFile(
    new URL(
      "../../../ai-engine/reports/phase3/model_bundle.json",
      import.meta.url,
    ),
  );
  const checksum = createHash("sha256").update(model).digest("hex");
  return prisma.$transaction(async (tx) => {
    await tx.datasetMetadata.updateMany({ data: { visibility: "ARCHIVED" } });
    for (const [file, entry] of Object.entries(manifest.files)) {
      if (file === "ground_truth.parquet") continue;
      const data = {
        name: file,
        sourceRef: "data/benchmarks/prysm-benchmark-v1/" + file,
        recordCount: BigInt(entry.rows),
        columns: [],
        visibility: "PUBLIC",
        metadata: {
          datasetVersion: manifest.dataset_version,
          sha256: entry.sha256,
        },
        lastScannedAt: new Date(),
      };
      await tx.datasetMetadata.upsert({
        where: { code: manifest.dataset_version + ":" + file },
        update: data,
        create: { code: manifest.dataset_version + ":" + file, ...data },
      });
    }
    await tx.modelRegistry.updateMany({ data: { status: "RETIRED" } });
    const data = {
      modelType: "INTELLIGENCE_BUNDLE",
      status: "ACTIVE",
      checksum,
      evaluationScope: manifest.evaluation_scope,
      isCalibratedProbability: false,
      metadata: {
        datasetVersion: manifest.dataset_version,
        modelSelection: "Phase 3 selected bundle",
        deployment: "api.intelligence:app",
      },
    };
    await tx.modelRegistry.upsert({
      where: {
        code_version: { code: "prysm-intelligence-v2", version: checksum },
      },
      update: data,
      create: { code: "prysm-intelligence-v2", version: checksum, ...data },
    });
    return 6;
  });
}
