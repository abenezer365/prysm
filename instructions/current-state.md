# Prysm Current State

## Phase 5 backend finalization ? current

Read [PHASE5_STATE.md](../PHASE5_STATE.md) and [the frontend API guide](../server/docs/API.md). The backend now runs JavaScript ESM, keeps PostgreSQL for operational state, removes analytical database copies with two applied forward migrations, and connects the selected Phase 3 engine to Phase 4 protected explanations. TypeScript build paths and obsolete ingestion/ticket implementations are removed. Earlier entries below are historical and do not describe the active backend.

Next: Phase 6 frontend adoption and UI/content work, using the finalized 66-endpoint HTTP contract and WebSocket guide. Local LLM inference and the large generator remain deferred. No Phase 6 UI work was done.


## Phase 4 requested scope complete

Read [PHASE4_STATE.md](../PHASE4_STATE.md). The RAG service now has protected `/explain`, local evidence-preserving summaries, bounded knowledge retrieval and optional Gemini reference selection using general approved content only. Private case context no longer enters Gemini prompts. 23 focused tests passed, including all 80 saved Phase 3 test results. Local-model download, connection and verification are deferred by explicit user request; setup is documented in `chatbot/local_llm/README.md`. No Phase 5/6 integration was implemented. Earlier phase entries below are historical.


## Phase 3 evaluation and optimization — complete

Read [PHASE3_STATE.md](../PHASE3_STATE.md) for measured results and the Phase 4 entry point. Selected GNN: 60 epochs, validation F1 .842, test F1 .800; fusion test F1 1.000 on 80 synthetic cases, with no real-world accuracy claim. Fixed graph-activity coverage for quiet personal accounts; anomaly unavailability remains explicit. Complete local output: `ai-engine/runs/evaluation-v3/`; portable reports/model: `ai-engine/reports/phase3/`. Two runs reproduced the selected model and all predictions exactly. Historical documents are grouped in `ai-engine/src/prysm_ai/v1/docs/`. Phase 4 has not been implemented; live HTTP still uses v1. Earlier entries below are historical.


## New Phase 2 intelligence — completed

Read [PHASE2_STATE.md](../PHASE2_STATE.md) for the current technical handoff. The new domain is `ai-engine/src/prysm_intelligence/`; `scripts/run_intelligence.py` trains/reloads the anomaly baseline and fully trained relational GNN, computes rules/family/tax/network evidence, fuses scores and emits graph highlights/rankings. The complete local run is `ai-engine/runs/intelligence-v2/`, with 240 results and train-only fitting. Verification: 88 tests passed, three historical artifact-dependent integration tests deselected. The prior domain is archived in `ai-engine/src/prysm_ai/v1/` behind an import bridge. The existing live HTTP runtime still uses that archive; no backend/frontend/RAG migration was performed. The next phase is `P3_Evaluation_&_Optimization.md`.

## New Phase 1 benchmark — completed 2026-09-05

The small dataset/pipeline implementation is complete. [PHASE1_STATE.md](../PHASE1_STATE.md) records its exact paths, 240-case distribution, schema, generation/validation/export commands, compatibility fixes, checks and limitations. The canonical source is `data/benchmarks/prysm-benchmark-v1/`; the local processed compatibility export is `ai-engine/runs/benchmark-v1/data/processed/`. The new Phase 2 engine consumes canonical source directly. The runtime audit below describes the existing historical deployment.

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
