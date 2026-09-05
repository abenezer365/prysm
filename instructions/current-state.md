# Prysm Current State

Audited against the working repository on 2026-09-05. The detailed migration map is in `BASELINE_REPORT.md`.

## Runtime status

| Area | State | Verified repository reality |
| --- | --- | --- |
| Raw data and AI artifacts | Implemented | `data/raw/` contains immutable Parquet source; `ai-engine/` contains foundation, feature, rule, model, graph, GNN, evidence, evaluation, and FastAPI runtime code. |
| AI Engine | Implemented with scientific limits | `ai-engine/api/` exposes `/health`, `/ready`, person search, bounded graph, and `/v1/analyze`. Supervised output is synthetic-scope only; GNN output is structural and unsupervised. |
| PostgreSQL | Implemented operational store | Prisma models cover identity, subjects, transactions, graph mappings, investigations, findings, evidence, runs, RAG interactions, dataset metadata/records, and audit. |
| Backend | Implemented | `server/` provides Express `/api/v1`, live session authorization, RBAC/clearance, context building, AI/RAG adapters, persistence, audits, and WebSocket relay. |
| Frontend | Implemented | `client/` is a React/Vite/React Router application with public pages, authentication, search, investigations, reports, graph/GNN presentation, chat, and admin pages. |
| RAG | Implemented, provider-dependent | `chatbot/main.py` provides local JSON retrieval, guarded ingestion, Gemini calls, fallback answers, HTTP chat, and WebSocket chat. Gemini may degrade while local fallback remains available. |
| Startup | Implemented locally | `server/scripts/start-local.ps1` starts PostgreSQL, AI Engine, RAG, and backend with readiness checks and matching `RAG_API_KEY` validation. |
| Production operations | Pending | Durable queue/outbox, deployment, backups, monitoring, load/query-plan validation, and browser end-to-end coverage remain incomplete. |

## Actual data flow

1. Raw Parquet is transformed by the AI foundation/intelligence/graph scripts into versioned processed data, signals, models, graph artifacts, and evaluations.
2. `ai-engine/api/runtime.py` loads the configured artifact root, indexes people from processed Parquet, and delegates analysis to `InvestigationEngine`.
3. The browser calls only `server/src/routes/index.ts` through `client/src/services/api.js`.
4. Express searches/creates operational subjects, builds a bounded cutoff-aware PostgreSQL context, calls the AI Engine, validates the response, and persists an `AnalysisRun`, findings, evidence references, model versions, and audit event.
5. The client renders the returned or persisted run in `client/src/pages/AppPages.jsx`.
6. Public and authorized chat are mediated by Express; RAG receives knowledge-only public input or a server-built authorized context.

## Graph and family-analysis reality

The system has two graph paths with different ownership:

- AI Engine Parquet graph artifacts power cutoff-safe analytical graph/GNN computation and the graph endpoint used by the GNN Maze UI.
- PostgreSQL graph nodes/edges power backend investigation context, authorization-aware chat context, and operational persistence.

There is no separate family model/service. Family and related-party analysis is represented by typed relationship edges and as-of features such as `family`, `employer_employee`, `shared_device`, `shared_address`, company links, degree, and relationship confidence.

## Confirmed limits and risks

- Analysis is synchronous despite returning `202` and storing a run record; it creates `RUNNING` directly rather than using the `QUEUED` state.
- The active AI artifact root is configurable, so stale or unintended runs can be consumed unless deployment configuration declares the active version.
- PostgreSQL and Parquet contain parallel graph representations without a single enforced snapshot/version synchronization contract.
- Full `DatasetRecord` ingestion mirrors raw data into PostgreSQL and must remain explicit; Parquet remains the analytical authority.
- The older architecture documentation claimed the frontend was absent; this has been corrected. Historical phase documents remain context, not runtime truth.
- Dependencies were cleaned from the workspace before this audit. This report is static; packages, PostgreSQL, services, and the full test suite were not rerun in this pass.

## Next implementation order

1. Declare and persist the active AI artifact/run version across readiness, analysis provenance, and PostgreSQL.
2. Define a shared graph snapshot contract between Parquet and PostgreSQL.
3. Move analysis behind a durable queue/outbox while preserving the current run-oriented API.
4. Add end-to-end browser coverage for search -> investigation -> analysis -> report -> chat.
5. Measure bounded graph/context query plans and latency before scaling claims.
