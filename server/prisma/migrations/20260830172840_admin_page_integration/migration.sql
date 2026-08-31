-- CreateTable
CREATE TABLE "contributor_applications" (
    "id" UUID NOT NULL,
    "email" CITEXT NOT NULL,
    "display_name" TEXT NOT NULL,
    "expertise" TEXT NOT NULL,
    "portfolio_url" TEXT,
    "motivation" TEXT NOT NULL,
    "availability" TEXT,
    "status" TEXT NOT NULL DEFAULT 'PENDING',
    "reviewed_by" UUID,
    "review_note" TEXT,
    "reviewed_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "contributor_applications_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "contributor_applications_status_created_at_idx" ON "contributor_applications"("status", "created_at");
