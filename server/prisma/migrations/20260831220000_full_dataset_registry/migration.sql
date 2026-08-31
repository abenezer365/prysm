CREATE TABLE "dataset_records" (
  "id" UUID NOT NULL DEFAULT gen_random_uuid(),
  "dataset" TEXT NOT NULL,
  "source_id" TEXT NOT NULL,
  "entity_key" TEXT,
  "event_at" TIMESTAMPTZ,
  "payload" JSONB NOT NULL,
  "source_ref" TEXT NOT NULL,
  "ingested_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "dataset_records_pkey" PRIMARY KEY ("id")
);
CREATE UNIQUE INDEX "dataset_records_dataset_source_id_key" ON "dataset_records"("dataset", "source_id");
CREATE INDEX "dataset_records_dataset_entity_key_idx" ON "dataset_records"("dataset", "entity_key");
CREATE INDEX "dataset_records_dataset_event_at_idx" ON "dataset_records"("dataset", "event_at");
