-- Remove derived analytical copies. Canonical facts and trained artifacts stay
-- in Parquet/AI engine; persisted application investigations remain intact.
-- Existing migration history is retained for already deployed databases.
DROP TABLE "gnn_embeddings";
DROP TABLE "gnn_edges";
DROP TABLE "gnn_nodes";
DROP TABLE "gnn_graph_snapshots";
DROP TABLE "graph_edges";
DROP TABLE "graph_nodes";
DROP TABLE "transactions";
DROP TABLE "dataset_records";
-- Tickets had no redemption implementation and cannot produce downloads.
DROP TABLE "model_download_tickets";

CREATE INDEX "analysis_runs_investigation_id_status_created_at_idx"
  ON "analysis_runs" ("investigation_id", "status", "created_at");
CREATE INDEX "rag_interactions_investigation_idx"
  ON "rag_interactions" (("context_manifest"->>'investigationId'), "user_id", "created_at");
