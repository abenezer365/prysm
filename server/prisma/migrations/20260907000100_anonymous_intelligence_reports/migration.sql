CREATE TABLE "intelligence_reports" (
  "id" UUID NOT NULL,
  "observed" TEXT NOT NULL,
  "involved" TEXT NOT NULL,
  "evidence" TEXT,
  "status" TEXT NOT NULL DEFAULT 'NEW',
  "ip_hash" TEXT,
  "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "intelligence_reports_pkey" PRIMARY KEY ("id")
);

CREATE INDEX "intelligence_reports_status_created_at_idx" ON "intelligence_reports"("status", "created_at");
