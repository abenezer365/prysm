-- CreateSchema
CREATE SCHEMA IF NOT EXISTS "public";

CREATE EXTENSION IF NOT EXISTS "citext";

-- CreateEnum
CREATE TYPE "UserStatus" AS ENUM ('PENDING', 'ACTIVE', 'SUSPENDED', 'DISABLED', 'REJECTED');

-- CreateEnum
CREATE TYPE "ApplicationStatus" AS ENUM ('PENDING', 'APPROVED', 'REJECTED');

-- CreateEnum
CREATE TYPE "InvestigationStatus" AS ENUM ('OPEN', 'IN_REVIEW', 'CLOSED');

-- CreateEnum
CREATE TYPE "AnalysisStatus" AS ENUM ('QUEUED', 'RUNNING', 'SUCCEEDED', 'FAILED');

-- CreateEnum
CREATE TYPE "ChatScope" AS ENUM ('PUBLIC', 'AUTHORIZED');

-- CreateTable
CREATE TABLE "roles" (
    "id" UUID NOT NULL,
    "code" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "roles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "clearance_levels" (
    "id" UUID NOT NULL,
    "code" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "rank" INTEGER NOT NULL,
    "description" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "clearance_levels_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "permissions" (
    "id" UUID NOT NULL,
    "code" TEXT NOT NULL,
    "description" TEXT,

    CONSTRAINT "permissions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "role_permissions" (
    "role_id" UUID NOT NULL,
    "permission_id" UUID NOT NULL,

    CONSTRAINT "role_permissions_pkey" PRIMARY KEY ("role_id","permission_id")
);

-- CreateTable
CREATE TABLE "users" (
    "id" UUID NOT NULL,
    "email" CITEXT NOT NULL,
    "password_hash" TEXT NOT NULL,
    "display_name" TEXT NOT NULL,
    "profile_image_url" TEXT,
    "preferences" JSONB,
    "status" "UserStatus" NOT NULL DEFAULT 'PENDING',
    "role_id" UUID NOT NULL,
    "clearance_level_id" UUID NOT NULL,
    "last_login_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "auth_sessions" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "refresh_token_hash" TEXT NOT NULL,
    "device_info" TEXT,
    "ip_hash" TEXT,
    "user_agent_hash" TEXT,
    "expires_at" TIMESTAMP(3) NOT NULL,
    "revoked_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "last_used_at" TIMESTAMP(3),

    CONSTRAINT "auth_sessions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "account_applications" (
    "id" UUID NOT NULL,
    "email" CITEXT NOT NULL,
    "display_name" TEXT NOT NULL,
    "organization" TEXT,
    "requested_role_id" UUID,
    "requested_clearance_level_id" UUID,
    "reason" TEXT,
    "status" "ApplicationStatus" NOT NULL DEFAULT 'PENDING',
    "reviewed_by" UUID,
    "reviewed_at" TIMESTAMP(3),
    "review_reason" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "account_applications_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "subjects" (
    "id" UUID NOT NULL,
    "subject_type" TEXT NOT NULL,
    "external_ref" TEXT,
    "display_label" TEXT NOT NULL,
    "classification_rank" INTEGER NOT NULL DEFAULT 1,
    "status" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "subjects_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "subject_profiles" (
    "subject_id" UUID NOT NULL,
    "full_name" TEXT,
    "date_of_birth" DATE,
    "country_code" CHAR(2),
    "risk_category" TEXT,
    "sensitive_attributes" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "subject_profiles_pkey" PRIMARY KEY ("subject_id")
);

-- CreateTable
CREATE TABLE "transactions" (
    "id" UUID NOT NULL,
    "source_transaction_id" TEXT,
    "from_subject_id" UUID,
    "to_subject_id" UUID,
    "from_account_id" UUID,
    "to_account_id" UUID,
    "amount" DECIMAL(24,8) NOT NULL,
    "currency" CHAR(3) NOT NULL,
    "timestamp" TIMESTAMP(3) NOT NULL,
    "transaction_type" TEXT,
    "country_from" CHAR(2),
    "country_to" CHAR(2),
    "channel" TEXT,
    "device_subject_id" UUID,
    "source_system" TEXT,
    "raw_metadata" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "transactions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "graph_nodes" (
    "id" UUID NOT NULL,
    "subject_id" UUID,
    "node_type" TEXT NOT NULL,
    "external_key" TEXT,
    "label_hash" TEXT,
    "features" JSONB,
    "embedding" JSONB,
    "embedding_model_version" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "graph_nodes_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "graph_edges" (
    "id" UUID NOT NULL,
    "source_node_id" UUID NOT NULL,
    "target_node_id" UUID NOT NULL,
    "edge_type" TEXT NOT NULL,
    "weight" DOUBLE PRECISION,
    "first_seen_at" TIMESTAMP(3),
    "last_seen_at" TIMESTAMP(3),
    "valid_from" TIMESTAMP(3),
    "valid_to" TIMESTAMP(3),
    "source_reference" TEXT,
    "properties" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "graph_edges_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "gnn_graph_snapshots" (
    "id" UUID NOT NULL,
    "graph_version" TEXT NOT NULL,
    "cutoff_at" TIMESTAMP(3) NOT NULL,
    "node_count" BIGINT NOT NULL,
    "edge_count" BIGINT NOT NULL,
    "feature_schema_version" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "metadata" JSONB,

    CONSTRAINT "gnn_graph_snapshots_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "gnn_nodes" (
    "snapshot_id" UUID NOT NULL,
    "graph_node_id" UUID NOT NULL,
    "gnn_index" BIGINT NOT NULL,
    "node_type" TEXT NOT NULL,
    "feature_version" TEXT NOT NULL,

    CONSTRAINT "gnn_nodes_pkey" PRIMARY KEY ("snapshot_id","graph_node_id")
);

-- CreateTable
CREATE TABLE "gnn_edges" (
    "snapshot_id" UUID NOT NULL,
    "graph_edge_id" UUID NOT NULL,
    "source_gnn_index" BIGINT NOT NULL,
    "target_gnn_index" BIGINT NOT NULL,
    "edge_type" TEXT NOT NULL,

    CONSTRAINT "gnn_edges_pkey" PRIMARY KEY ("snapshot_id","graph_edge_id")
);

-- CreateTable
CREATE TABLE "gnn_embeddings" (
    "id" UUID NOT NULL,
    "snapshot_id" UUID NOT NULL,
    "graph_node_id" UUID NOT NULL,
    "model_version" TEXT NOT NULL,
    "embedding" JSONB NOT NULL,
    "generated_at" TIMESTAMP(3) NOT NULL,
    "metadata" JSONB,

    CONSTRAINT "gnn_embeddings_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "evidence_references" (
    "id" UUID NOT NULL,
    "source_type" TEXT NOT NULL,
    "source_id" TEXT NOT NULL,
    "source_table" TEXT,
    "event_time" TIMESTAMP(3),
    "label" TEXT NOT NULL,
    "excerpt" TEXT,
    "metadata" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "evidence_references_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "investigations" (
    "id" UUID NOT NULL,
    "created_by" UUID NOT NULL,
    "subject_id" UUID NOT NULL,
    "status" "InvestigationStatus" NOT NULL DEFAULT 'OPEN',
    "title" TEXT,
    "purpose" TEXT,
    "cutoff_at" TIMESTAMP(3),
    "prediction_horizon_start" TIMESTAMP(3),
    "prediction_horizon_end" TIMESTAMP(3),
    "context_version" TEXT,
    "ai_engine_version" TEXT,
    "minimum_clearance_rank" INTEGER NOT NULL DEFAULT 1,
    "shared" BOOLEAN NOT NULL DEFAULT false,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    "closed_at" TIMESTAMP(3),

    CONSTRAINT "investigations_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "investigation_queries" (
    "id" UUID NOT NULL,
    "investigation_id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "query_text" TEXT NOT NULL,
    "normalized_query" TEXT,
    "query_type" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "investigation_queries_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "investigation_findings" (
    "id" UUID NOT NULL,
    "investigation_id" UUID NOT NULL,
    "finding_type" TEXT NOT NULL,
    "severity" TEXT,
    "score" DOUBLE PRECISION,
    "confidence" DOUBLE PRECISION,
    "title" TEXT NOT NULL,
    "summary" TEXT,
    "source_component" TEXT NOT NULL,
    "model_version" TEXT,
    "metadata" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "investigation_findings_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "finding_evidence" (
    "finding_id" UUID NOT NULL,
    "evidence_id" UUID NOT NULL,
    "relevance" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "finding_evidence_pkey" PRIMARY KEY ("finding_id","evidence_id")
);

-- CreateTable
CREATE TABLE "analysis_runs" (
    "id" UUID NOT NULL,
    "investigation_id" UUID NOT NULL,
    "requested_by" UUID NOT NULL,
    "status" "AnalysisStatus" NOT NULL DEFAULT 'QUEUED',
    "context_version" TEXT NOT NULL,
    "data_snapshot" TEXT NOT NULL,
    "cutoff_at" TIMESTAMP(3) NOT NULL,
    "graph_snapshot_id" UUID,
    "ai_engine_version" TEXT,
    "model_versions" JSONB,
    "request_payload" JSONB NOT NULL,
    "response_payload" JSONB,
    "error_code" TEXT,
    "started_at" TIMESTAMP(3),
    "completed_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "analysis_runs_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "rag_interactions" (
    "id" UUID NOT NULL,
    "conversation_id" UUID NOT NULL,
    "user_id" UUID,
    "scope" "ChatScope" NOT NULL,
    "question" TEXT NOT NULL,
    "answer" TEXT,
    "access_scope" JSONB NOT NULL,
    "context_manifest" JSONB,
    "rag_version" TEXT,
    "latency_ms" INTEGER,
    "status" TEXT NOT NULL,
    "feedback" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "rag_interactions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "models" (
    "id" UUID NOT NULL,
    "code" TEXT NOT NULL,
    "version" TEXT NOT NULL,
    "model_type" TEXT NOT NULL,
    "status" TEXT NOT NULL,
    "artifact_uri" TEXT,
    "checksum" TEXT,
    "evaluation_scope" TEXT NOT NULL,
    "is_calibrated_probability" BOOLEAN NOT NULL DEFAULT false,
    "metadata" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "models_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "audit_events" (
    "id" UUID NOT NULL,
    "actor_user_id" UUID,
    "action" TEXT NOT NULL,
    "resource_type" TEXT NOT NULL,
    "resource_id" TEXT,
    "decision" TEXT NOT NULL,
    "reason_code" TEXT,
    "request_id" TEXT,
    "ip_hash" TEXT,
    "user_agent_hash" TEXT,
    "metadata" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "audit_events_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "roles_code_key" ON "roles"("code");

-- CreateIndex
CREATE UNIQUE INDEX "clearance_levels_code_key" ON "clearance_levels"("code");

-- CreateIndex
CREATE UNIQUE INDEX "clearance_levels_rank_key" ON "clearance_levels"("rank");

-- CreateIndex
CREATE UNIQUE INDEX "permissions_code_key" ON "permissions"("code");

-- CreateIndex
CREATE UNIQUE INDEX "users_email_key" ON "users"("email");

-- CreateIndex
CREATE INDEX "users_status_idx" ON "users"("status");

-- CreateIndex
CREATE UNIQUE INDEX "auth_sessions_refresh_token_hash_key" ON "auth_sessions"("refresh_token_hash");

-- CreateIndex
CREATE INDEX "auth_sessions_user_id_revoked_at_idx" ON "auth_sessions"("user_id", "revoked_at");

-- CreateIndex
CREATE INDEX "account_applications_status_created_at_idx" ON "account_applications"("status", "created_at");

-- CreateIndex
CREATE INDEX "subjects_display_label_idx" ON "subjects"("display_label");

-- CreateIndex
CREATE UNIQUE INDEX "subjects_subject_type_external_ref_key" ON "subjects"("subject_type", "external_ref");

-- CreateIndex
CREATE UNIQUE INDEX "transactions_source_transaction_id_key" ON "transactions"("source_transaction_id");

-- CreateIndex
CREATE INDEX "transactions_timestamp_idx" ON "transactions"("timestamp");

-- CreateIndex
CREATE INDEX "transactions_from_subject_id_idx" ON "transactions"("from_subject_id");

-- CreateIndex
CREATE INDEX "transactions_to_subject_id_idx" ON "transactions"("to_subject_id");

-- CreateIndex
CREATE INDEX "transactions_from_account_id_timestamp_idx" ON "transactions"("from_account_id", "timestamp");

-- CreateIndex
CREATE INDEX "transactions_to_account_id_timestamp_idx" ON "transactions"("to_account_id", "timestamp");

-- CreateIndex
CREATE INDEX "transactions_currency_idx" ON "transactions"("currency");

-- CreateIndex
CREATE INDEX "transactions_transaction_type_idx" ON "transactions"("transaction_type");

-- CreateIndex
CREATE UNIQUE INDEX "graph_nodes_external_key_key" ON "graph_nodes"("external_key");

-- CreateIndex
CREATE INDEX "graph_nodes_subject_id_idx" ON "graph_nodes"("subject_id");

-- CreateIndex
CREATE INDEX "graph_nodes_node_type_idx" ON "graph_nodes"("node_type");

-- CreateIndex
CREATE INDEX "graph_edges_source_node_id_edge_type_idx" ON "graph_edges"("source_node_id", "edge_type");

-- CreateIndex
CREATE INDEX "graph_edges_target_node_id_edge_type_idx" ON "graph_edges"("target_node_id", "edge_type");

-- CreateIndex
CREATE INDEX "graph_edges_last_seen_at_idx" ON "graph_edges"("last_seen_at");

-- CreateIndex
CREATE UNIQUE INDEX "gnn_graph_snapshots_graph_version_cutoff_at_feature_schema__key" ON "gnn_graph_snapshots"("graph_version", "cutoff_at", "feature_schema_version");

-- CreateIndex
CREATE UNIQUE INDEX "gnn_nodes_snapshot_id_gnn_index_key" ON "gnn_nodes"("snapshot_id", "gnn_index");

-- CreateIndex
CREATE UNIQUE INDEX "gnn_embeddings_snapshot_id_graph_node_id_model_version_key" ON "gnn_embeddings"("snapshot_id", "graph_node_id", "model_version");

-- CreateIndex
CREATE INDEX "evidence_references_event_time_idx" ON "evidence_references"("event_time");

-- CreateIndex
CREATE UNIQUE INDEX "evidence_references_source_type_source_id_key" ON "evidence_references"("source_type", "source_id");

-- CreateIndex
CREATE INDEX "investigations_created_by_status_idx" ON "investigations"("created_by", "status");

-- CreateIndex
CREATE INDEX "investigations_subject_id_idx" ON "investigations"("subject_id");

-- CreateIndex
CREATE INDEX "investigation_findings_investigation_id_created_at_idx" ON "investigation_findings"("investigation_id", "created_at");

-- CreateIndex
CREATE INDEX "analysis_runs_investigation_id_created_at_idx" ON "analysis_runs"("investigation_id", "created_at");

-- CreateIndex
CREATE INDEX "analysis_runs_requested_by_created_at_idx" ON "analysis_runs"("requested_by", "created_at");

-- CreateIndex
CREATE INDEX "rag_interactions_conversation_id_created_at_idx" ON "rag_interactions"("conversation_id", "created_at");

-- CreateIndex
CREATE INDEX "rag_interactions_user_id_created_at_idx" ON "rag_interactions"("user_id", "created_at");

-- CreateIndex
CREATE UNIQUE INDEX "models_code_version_key" ON "models"("code", "version");

-- CreateIndex
CREATE INDEX "audit_events_actor_user_id_created_at_idx" ON "audit_events"("actor_user_id", "created_at");

-- CreateIndex
CREATE INDEX "audit_events_resource_type_resource_id_idx" ON "audit_events"("resource_type", "resource_id");

-- CreateIndex
CREATE INDEX "audit_events_action_created_at_idx" ON "audit_events"("action", "created_at");

-- AddForeignKey
ALTER TABLE "role_permissions" ADD CONSTRAINT "role_permissions_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "roles"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "role_permissions" ADD CONSTRAINT "role_permissions_permission_id_fkey" FOREIGN KEY ("permission_id") REFERENCES "permissions"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "users" ADD CONSTRAINT "users_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "roles"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "users" ADD CONSTRAINT "users_clearance_level_id_fkey" FOREIGN KEY ("clearance_level_id") REFERENCES "clearance_levels"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "auth_sessions" ADD CONSTRAINT "auth_sessions_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "account_applications" ADD CONSTRAINT "account_applications_requested_role_id_fkey" FOREIGN KEY ("requested_role_id") REFERENCES "roles"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "account_applications" ADD CONSTRAINT "account_applications_requested_clearance_level_id_fkey" FOREIGN KEY ("requested_clearance_level_id") REFERENCES "clearance_levels"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "account_applications" ADD CONSTRAINT "account_applications_reviewed_by_fkey" FOREIGN KEY ("reviewed_by") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "subject_profiles" ADD CONSTRAINT "subject_profiles_subject_id_fkey" FOREIGN KEY ("subject_id") REFERENCES "subjects"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "transactions" ADD CONSTRAINT "transactions_from_subject_id_fkey" FOREIGN KEY ("from_subject_id") REFERENCES "subjects"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "transactions" ADD CONSTRAINT "transactions_to_subject_id_fkey" FOREIGN KEY ("to_subject_id") REFERENCES "subjects"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "transactions" ADD CONSTRAINT "transactions_from_account_id_fkey" FOREIGN KEY ("from_account_id") REFERENCES "subjects"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "transactions" ADD CONSTRAINT "transactions_to_account_id_fkey" FOREIGN KEY ("to_account_id") REFERENCES "subjects"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "transactions" ADD CONSTRAINT "transactions_device_subject_id_fkey" FOREIGN KEY ("device_subject_id") REFERENCES "subjects"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "graph_nodes" ADD CONSTRAINT "graph_nodes_subject_id_fkey" FOREIGN KEY ("subject_id") REFERENCES "subjects"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "graph_edges" ADD CONSTRAINT "graph_edges_source_node_id_fkey" FOREIGN KEY ("source_node_id") REFERENCES "graph_nodes"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "graph_edges" ADD CONSTRAINT "graph_edges_target_node_id_fkey" FOREIGN KEY ("target_node_id") REFERENCES "graph_nodes"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "gnn_nodes" ADD CONSTRAINT "gnn_nodes_snapshot_id_fkey" FOREIGN KEY ("snapshot_id") REFERENCES "gnn_graph_snapshots"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "gnn_nodes" ADD CONSTRAINT "gnn_nodes_graph_node_id_fkey" FOREIGN KEY ("graph_node_id") REFERENCES "graph_nodes"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "gnn_edges" ADD CONSTRAINT "gnn_edges_snapshot_id_fkey" FOREIGN KEY ("snapshot_id") REFERENCES "gnn_graph_snapshots"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "gnn_edges" ADD CONSTRAINT "gnn_edges_graph_edge_id_fkey" FOREIGN KEY ("graph_edge_id") REFERENCES "graph_edges"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "gnn_embeddings" ADD CONSTRAINT "gnn_embeddings_snapshot_id_fkey" FOREIGN KEY ("snapshot_id") REFERENCES "gnn_graph_snapshots"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "gnn_embeddings" ADD CONSTRAINT "gnn_embeddings_graph_node_id_fkey" FOREIGN KEY ("graph_node_id") REFERENCES "graph_nodes"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "investigations" ADD CONSTRAINT "investigations_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "investigations" ADD CONSTRAINT "investigations_subject_id_fkey" FOREIGN KEY ("subject_id") REFERENCES "subjects"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "investigation_queries" ADD CONSTRAINT "investigation_queries_investigation_id_fkey" FOREIGN KEY ("investigation_id") REFERENCES "investigations"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "investigation_queries" ADD CONSTRAINT "investigation_queries_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "investigation_findings" ADD CONSTRAINT "investigation_findings_investigation_id_fkey" FOREIGN KEY ("investigation_id") REFERENCES "investigations"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "finding_evidence" ADD CONSTRAINT "finding_evidence_finding_id_fkey" FOREIGN KEY ("finding_id") REFERENCES "investigation_findings"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "finding_evidence" ADD CONSTRAINT "finding_evidence_evidence_id_fkey" FOREIGN KEY ("evidence_id") REFERENCES "evidence_references"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "analysis_runs" ADD CONSTRAINT "analysis_runs_investigation_id_fkey" FOREIGN KEY ("investigation_id") REFERENCES "investigations"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "analysis_runs" ADD CONSTRAINT "analysis_runs_requested_by_fkey" FOREIGN KEY ("requested_by") REFERENCES "users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "audit_events" ADD CONSTRAINT "audit_events_actor_user_id_fkey" FOREIGN KEY ("actor_user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;
