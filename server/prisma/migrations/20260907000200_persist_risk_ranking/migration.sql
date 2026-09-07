CREATE TABLE "risk_ranking_snapshots" (
    "id" UUID NOT NULL,
    "cutoff_at" TIMESTAMP(3) NOT NULL,
    "population" TEXT NOT NULL,
    "limit" INTEGER NOT NULL DEFAULT 10,
    "data" JSONB NOT NULL,
    "source" TEXT NOT NULL DEFAULT 'AI_ENGINE',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "risk_ranking_snapshots_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX "risk_ranking_snapshots_cutoff_at_key" ON "risk_ranking_snapshots"("cutoff_at");
CREATE INDEX "risk_ranking_snapshots_created_at_idx" ON "risk_ranking_snapshots"("created_at");