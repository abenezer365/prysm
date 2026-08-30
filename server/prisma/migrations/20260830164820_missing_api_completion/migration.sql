-- AlterTable
ALTER TABLE "account_applications" ADD COLUMN     "justification" TEXT,
ADD COLUMN     "organization_role" TEXT,
ADD COLUMN     "phone" TEXT,
ADD COLUMN     "profession" TEXT;

-- CreateTable
CREATE TABLE "application_review_history" (
    "id" UUID NOT NULL,
    "application_id" UUID NOT NULL,
    "previous_status" "ApplicationStatus" NOT NULL,
    "new_status" "ApplicationStatus" NOT NULL,
    "reviewer_id" UUID NOT NULL,
    "note" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "application_review_history_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "application_documents" (
    "id" UUID NOT NULL,
    "application_id" UUID NOT NULL,
    "file_name" TEXT NOT NULL,
    "mime_type" TEXT NOT NULL,
    "size_bytes" INTEGER NOT NULL,
    "storage_ref" TEXT,
    "scan_status" TEXT NOT NULL DEFAULT 'PENDING',
    "metadata" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "application_documents_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "investigation_feedback" (
    "id" UUID NOT NULL,
    "investigation_id" UUID NOT NULL,
    "analysis_run_id" UUID,
    "created_by" UUID NOT NULL,
    "rating" TEXT NOT NULL,
    "rationale" TEXT NOT NULL,
    "metadata" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "investigation_feedback_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "investigation_exports" (
    "id" UUID NOT NULL,
    "investigation_id" UUID NOT NULL,
    "requested_by" UUID NOT NULL,
    "format" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'QUEUED',
    "expires_at" TIMESTAMP(3),
    "artifact_ref" TEXT,
    "error_code" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "investigation_exports_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "password_reset_tokens" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "token_hash" TEXT NOT NULL,
    "expires_at" TIMESTAMP(3) NOT NULL,
    "used_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "password_reset_tokens_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "news_items" (
    "id" UUID NOT NULL,
    "slug" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "body" TEXT NOT NULL,
    "image_ref" TEXT,
    "author_id" UUID,
    "author_name" TEXT,
    "status" TEXT NOT NULL DEFAULT 'DRAFT',
    "published_at" TIMESTAMP(3),
    "metadata" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "news_items_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "contact_submissions" (
    "id" UUID NOT NULL,
    "name" TEXT NOT NULL,
    "email" CITEXT NOT NULL,
    "subject" TEXT,
    "message" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'NEW',
    "ip_hash" TEXT,
    "metadata" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "contact_submissions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "bug_reports" (
    "id" UUID NOT NULL,
    "reporter_name" TEXT,
    "contact_email" CITEXT,
    "description" TEXT NOT NULL,
    "severity" TEXT NOT NULL DEFAULT 'MEDIUM',
    "status" TEXT NOT NULL DEFAULT 'OPEN',
    "request_id" TEXT,
    "client_version" TEXT,
    "diagnostics" JSONB,
    "assigned_to" UUID,
    "root_cause" TEXT,
    "resolution_notes" TEXT,
    "workaround" TEXT,
    "public_explanation" TEXT,
    "public_approved" BOOLEAN NOT NULL DEFAULT false,
    "resolved_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "bug_reports_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "beta_applications" (
    "id" UUID NOT NULL,
    "email" CITEXT NOT NULL,
    "display_name" TEXT NOT NULL,
    "purpose" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'PENDING',
    "reviewed_by" UUID,
    "review_note" TEXT,
    "reviewed_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "beta_applications_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "dataset_metadata" (
    "id" UUID NOT NULL,
    "code" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "source_ref" TEXT NOT NULL,
    "record_count" BIGINT,
    "columns" JSONB NOT NULL,
    "features" JSONB,
    "date_start" TIMESTAMP(3),
    "date_end" TIMESTAMP(3),
    "visibility" TEXT NOT NULL DEFAULT 'PUBLIC',
    "last_scanned_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "metadata" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "dataset_metadata_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "model_download_tickets" (
    "id" UUID NOT NULL,
    "model_id" UUID NOT NULL,
    "requested_by" UUID NOT NULL,
    "token_hash" TEXT NOT NULL,
    "checksum" TEXT,
    "expires_at" TIMESTAMP(3) NOT NULL,
    "used_at" TIMESTAMP(3),
    "audit_event_id" UUID,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "model_download_tickets_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "rag_document_records" (
    "id" UUID NOT NULL,
    "external_id" TEXT,
    "title" TEXT NOT NULL,
    "description" TEXT,
    "source" TEXT,
    "category" TEXT,
    "version" TEXT,
    "status" TEXT NOT NULL DEFAULT 'QUEUED',
    "chunk_count" INTEGER NOT NULL DEFAULT 0,
    "enabled" BOOLEAN NOT NULL DEFAULT true,
    "metadata" JSONB,
    "created_by" UUID NOT NULL,
    "error_code" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "rag_document_records_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "application_review_history_application_id_created_at_idx" ON "application_review_history"("application_id", "created_at");

-- CreateIndex
CREATE INDEX "application_documents_application_id_idx" ON "application_documents"("application_id");

-- CreateIndex
CREATE INDEX "investigation_feedback_investigation_id_created_at_idx" ON "investigation_feedback"("investigation_id", "created_at");

-- CreateIndex
CREATE INDEX "investigation_exports_investigation_id_created_at_idx" ON "investigation_exports"("investigation_id", "created_at");

-- CreateIndex
CREATE UNIQUE INDEX "password_reset_tokens_token_hash_key" ON "password_reset_tokens"("token_hash");

-- CreateIndex
CREATE INDEX "password_reset_tokens_user_id_expires_at_idx" ON "password_reset_tokens"("user_id", "expires_at");

-- CreateIndex
CREATE UNIQUE INDEX "news_items_slug_key" ON "news_items"("slug");

-- CreateIndex
CREATE INDEX "news_items_status_published_at_idx" ON "news_items"("status", "published_at");

-- CreateIndex
CREATE INDEX "contact_submissions_status_created_at_idx" ON "contact_submissions"("status", "created_at");

-- CreateIndex
CREATE INDEX "bug_reports_status_created_at_idx" ON "bug_reports"("status", "created_at");

-- CreateIndex
CREATE INDEX "bug_reports_public_approved_resolved_at_idx" ON "bug_reports"("public_approved", "resolved_at");

-- CreateIndex
CREATE INDEX "beta_applications_status_created_at_idx" ON "beta_applications"("status", "created_at");

-- CreateIndex
CREATE UNIQUE INDEX "dataset_metadata_code_key" ON "dataset_metadata"("code");

-- CreateIndex
CREATE INDEX "dataset_metadata_visibility_last_scanned_at_idx" ON "dataset_metadata"("visibility", "last_scanned_at");

-- CreateIndex
CREATE UNIQUE INDEX "model_download_tickets_token_hash_key" ON "model_download_tickets"("token_hash");

-- CreateIndex
CREATE INDEX "model_download_tickets_model_id_requested_by_idx" ON "model_download_tickets"("model_id", "requested_by");

-- CreateIndex
CREATE UNIQUE INDEX "rag_document_records_external_id_key" ON "rag_document_records"("external_id");

-- CreateIndex
CREATE INDEX "rag_document_records_status_created_at_idx" ON "rag_document_records"("status", "created_at");

-- AddForeignKey
ALTER TABLE "application_review_history" ADD CONSTRAINT "application_review_history_application_id_fkey" FOREIGN KEY ("application_id") REFERENCES "account_applications"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "application_documents" ADD CONSTRAINT "application_documents_application_id_fkey" FOREIGN KEY ("application_id") REFERENCES "account_applications"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "investigation_feedback" ADD CONSTRAINT "investigation_feedback_investigation_id_fkey" FOREIGN KEY ("investigation_id") REFERENCES "investigations"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "investigation_exports" ADD CONSTRAINT "investigation_exports_investigation_id_fkey" FOREIGN KEY ("investigation_id") REFERENCES "investigations"("id") ON DELETE CASCADE ON UPDATE CASCADE;
