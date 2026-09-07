# PostgreSQL ownership and migration notes

PostgreSQL remains the sole SQL application store. Prisma schema: `prisma/schema.prisma`. Canonical analytical facts and trained artifacts remain in Parquet/JSON under the AI engine; operational APIs neither import full datasets nor store GNN training graphs.

| Tables / Prisma models | Application reason |
|---|---|
| Role, Permission, RolePermission, ClearanceLevel | Live RBAC and clearance policy |
| User, AuthSession, PasswordResetToken | Identities, hashed sessions, password recovery |
| AccountApplication, ApplicationReviewHistory, ApplicationDocument | Reviewed account provisioning and supporting-document metadata |
| Subject, SubjectProfile | Small, lazily materialized canonical references and application classification; existing historical references retained for cases |
| Investigation, InvestigationQuery | Case state and historical query records |
| AnalysisRun | Run lifecycle, minimal subject/cutoff request, immutable engine response and provenance |
| InvestigationFinding, EvidenceReference, FindingEvidence | Evidence-backed case findings and source-reference links, with case-scoped access |
| InvestigationFeedback, InvestigationExport | Investigator feedback and completed JSON export audit records |
| RagInteraction, RagDocumentRecord | Conversation history with source run/fingerprint and administrative knowledge ingestion state |
| ModelRegistry, DatasetMetadata | Selected/retired artifact metadata and six current fact-table metadata entries; no source rows or evaluation ground truth |
| AuditEvent | Meaningful application activity without passwords, tokens or private question/result payloads |
| NewsItem, ContactSubmission, BugReport, BetaApplication, ContributorApplication | Existing public/admin application features consumed by the current frontend |

## Cleanup migrations

The five original migration files are retained because they are applied history. Deleting or rewriting them would break existing deployments. Two forward migrations implement Phase 5:

1. `20260906000100_phase5_operational_cleanup`: drops `transactions`, `graph_nodes`, `graph_edges`, `gnn_graph_snapshots`, `gnn_nodes`, `gnn_edges`, `gnn_embeddings`, `dataset_records`, and `model_download_tickets`. The context builder and dashboard no longer query these structures, ingestion scripts are removed, and tickets had no redemption implementation. Adds indexes for successful case-result lookup and case conversation history.
2. `20260906000200_preserve_analysis_json`: converts `analysis_runs.response_payload` to text, preserving existing contents. New engine results are stored using `JSON.stringify` and parsed at the API boundary. This prevents last-digit changes observed in the Prisma JSON round-trip; JSON API clients still receive objects. The field is immutable once the run succeeds. Its source model/cutoff remain separately queryable.

The expression index on `context_manifest->>'investigationId'` is intentionally SQL-managed because Prisma does not represent expression indexes. Existing legacy case findings, subjects and run provenance are retained for audit; old fields in those records do not activate the retired engine. A new analysis is required for current `/explain` use.

`sync:metadata` archives old dataset metadata and retires old model entries, then activates only the current benchmark facts and selected model bundle checksum. It never reads prediction tables or ground-truth content. The six fact metadata entries currently contain counts/checksums; full column schemas remain in the canonical dataset contract.

## Safe deployment and recovery

Stop old backend/ingestion processes, run `npm run db:backup`, then `npm run db:migrate`, `npm run db:generate`, and `npm run sync:metadata`. Start only the JavaScript backend and current AI service afterward. The Phase 5 migrations were applied successfully to the local `prysm` database after a successful custom-format `pg_dump` backup. Backups are private ignored artifacts under `.tmp/database-backups/`, not source-controlled.

For rollback, restore the backup into a separately named database using PostgreSQL `pg_restore` and point the matching older backend at that database. Do not attempt a schema-only rollback over new case results. This task did not delete the backup or old canonical datasets.

No automatic retention policy, attachment storage service, production email delivery, or national-scale analytical warehouse is introduced. JSON case export is completed inline; CSV/PDF requests are rejected instead of queued without a worker.
