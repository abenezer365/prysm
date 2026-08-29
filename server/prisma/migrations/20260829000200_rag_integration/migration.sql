ALTER TABLE "rag_interactions"
  ADD COLUMN "request_id" TEXT,
  ADD COLUMN "rag_request_id" TEXT,
  ADD COLUMN "sources" JSONB;

UPDATE "rag_interactions"
SET "request_id" = 'legacy:' || "id"::text
WHERE "request_id" IS NULL;

ALTER TABLE "rag_interactions"
  ALTER COLUMN "request_id" SET NOT NULL;

CREATE INDEX "rag_interactions_request_id_idx" ON "rag_interactions"("request_id");
