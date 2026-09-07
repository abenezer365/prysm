<!-- Durable project knowledge for future agents. Runtime status belongs in current-state.md; actionable work belongs in todo.md. -->

## Phase 5 backend finalization ? current

Read [PHASE5_STATE.md](../PHASE5_STATE.md) and [the frontend API guide](../server/docs/API.md). The backend now runs JavaScript ESM, keeps PostgreSQL for operational state, removes analytical database copies with two applied forward migrations, and connects the selected Phase 3 engine to Phase 4 protected explanations. TypeScript build paths and obsolete ingestion/ticket implementations are removed. Earlier entries below are historical and do not describe the active backend.

Next: Phase 6 frontend adoption and UI/content work, using the finalized 66-endpoint HTTP contract and WebSocket guide. Local LLM inference and the large generator remain deferred. No Phase 6 UI work was done.


# Prysm Project Memory

## Phase 4 requested scope complete

Read [PHASE4_STATE.md](../PHASE4_STATE.md). The RAG service now has protected `/explain`, local evidence-preserving summaries, bounded knowledge retrieval and optional Gemini reference selection using general approved content only. Private case context no longer enters Gemini prompts. 23 focused tests passed, including all 80 saved Phase 3 test results. Local-model download, connection and verification are deferred by explicit user request; setup is documented in `chatbot/local_llm/README.md`. No Phase 5/6 integration was implemented. Earlier phase entries below are historical.


## Phase 3 evaluation and optimization — complete

Read [PHASE3_STATE.md](../PHASE3_STATE.md) for measured results and the Phase 4 entry point. Selected GNN: 60 epochs, validation F1 .842, test F1 .800; fusion test F1 1.000 on 80 synthetic cases, with no real-world accuracy claim. Fixed graph-activity coverage for quiet personal accounts; anomaly unavailability remains explicit. Complete local output: `ai-engine/runs/evaluation-v3/`; portable reports/model: `ai-engine/reports/phase3/`. Two runs reproduced the selected model and all predictions exactly. Historical documents are grouped in `ai-engine/src/prysm_ai/v1/docs/`. Phase 4 has not been implemented; live HTTP still uses v1. Earlier entries below are historical.


## New six-phase improvement journey: Phase 2 completed

The current domain is `ai-engine/src/prysm_intelligence/`; exact decisions, commands and artifacts are in [../PHASE2_STATE.md](../PHASE2_STATE.md). The sixteen prior domain modules are collectively archived in `ai-engine/src/prysm_ai/v1/`, with legacy imports preserved. Phase 2 consumes canonical Phase 1 facts directly and does not use ground-truth membership at inference. It fits a robust training-normal anomaly baseline and a fully trained two-layer relational mean GNN on train only, then produces explicit rule/family/tax/network evidence, component-preserving fusion, red review annotations and computed rankings. The full local run contains 240 results under `ai-engine/runs/intelligence-v2/`; reviewable examples are in `ai-engine/examples/`. Verification: 88 tests passed, with three historical full-artifact integration tests excluded. Live HTTP still calls v1; integration and formal evaluation are not claimed. Continue with Phase 3 evaluation, preserving the cutoff/split and source-evidence boundaries.

## New six-phase improvement journey: Phase 1 completed

On 2026-09-05, the independent `prysm-benchmark-v1` dataset and pipeline were implemented. Read [../PHASE1_STATE.md](../PHASE1_STATE.md) for the exact handoff and commands, then [the canonical dataset manifest](../data/benchmarks/prysm-benchmark-v1/DATASET_MANIFEST.md). The new benchmark contains 240 cases (216 normal / 24 suspicious), 4,320 transactions and explicit family/business relationships. It uses separate evidence-backed retrospective labels, seed 20260905, fail-fast integrity validation and an existing-consumer export. No new models were trained; prior raw data and live artifact selection remain historical. Phase 2 starts from the new manifest. The 1–2 million-row generator is deferred until after all six phases.

## Durable decisions and invariants

- Prysm is decision-support software for financial investigations. Its output is an `uncalibrated_attention_assessment`, never a fraud verdict or calibrated probability. UI, API, reports, and prompts must preserve that language.
- Component ownership is strict: PostgreSQL owns operational facts and workflow state; the Python AI Engine owns feature/rule/model/GNN computation and evidence; RAG owns knowledge retrieval; Gemini owns natural-language generation; Express owns authentication, authorization, orchestration, persistence, auditing, and frontend DTOs. Do not duplicate AI/RAG logic in TypeScript or let clients call internal services directly.
- Canonical entity identity is `EntityType:entity_id`. Raw IDs are not globally unique; every polymorphic join must include both type and ID.
- `data/raw/` is immutable source material. Derived datasets, repaired labels, scenario data, graphs, features, models, and run artifacts live in isolated/versioned directories with manifests and hashes.
- Historical analysis is cutoff-safe: use as-of facts, exclude future transactions/edges, honor validity intervals, bound graph traversal, and record cutoff/snapshot provenance. Full-graph features and embeddings are retrospective caches, not valid historical inputs.
- Preserve source inconsistencies and expose validity/quality flags; never silently repair source facts. Ground-truth metadata and related-entity lists are label provenance only and are excluded from operational features and graphs.
- Evidence must resolve to supplied source-backed entities, transactions, relationships, graph edges, derived measurements, or versioned artifacts. Scores, relationships, and facts must never be invented by Gemini.
- Missing intelligence components are marked unavailable and excluded with weight renormalization; they are not zero-imputed. Assessment strength, confidence, coverage, evidence, and limitations remain separate concepts.
- The browser trusts only the backend. Permissions, clearance, account status, ownership/sharing, investigation classification, and authorized chat context are re-evaluated server-side from the live session/database. Browser claims such as `authenticated`, `clearance`, or arbitrary context are never trusted.
- Public chat is knowledge-only. Authorized chat requires a live session and investigation access; Express constructs a bounded `prysm-authorized-rag-context-v1` from permitted persisted analysis/GNN findings and evidence. RAG explains trusted context but never authorizes access or calculates risk.
- Secrets stay outside Git. Internal AI/RAG service keys are bearer credentials; protected RAG operations fail closed when its internal key is absent. Logs redact authorization, passwords, and refresh tokens.

## Scientific history worth preserving

- Phases 1–3 established canonical data, leakage-safe transaction intelligence, label/event alignment, a typed temporal graph, self-supervised relational GraphSAGE representations, evidence, and fusion.
- The original 5,000-row retrospective ground truth was not a valid predictive entity-event dataset: its 16,634 referenced transactions were unaffiliated with labeled entities, leaving zero predictive-eligible rows. The original source was retained unchanged.
- `generator/ground-truth-repair/` is an isolated deterministic repair attempt. It supports 647 scenarios with 2,356 valid references, but only one supported scenario is anomalous; it is not training-ready.
- `generator/ground-truth-scenario-generation/` produced the isolated scenario dataset consumed by `ai-engine/runs/scenario-v1/`: 747,582 transactions and 7,000 aligned observations (3,500/3,500) with 46,094 affiliated future evidence references.
- The aligned synthetic benchmark is valid but weak: supervised ROC-AUC 0.470444 and PR-AUC 0.467240; anomaly ROC-AUC 0.487010; rules ROC-AUC 0.816098 with recall 0.245714 at the evaluated threshold. These results establish a reproducible baseline, not real-world efficacy.
- Canonical graph `prysm-financial-graph-v1` contains 549,947 typed nodes and 3,036,895 typed temporal edges. Its self-supervised link-reconstruction result has structural meaning only; no supervised cutoff-safe GNN risk head has been validated.

## Implementation history and lessons

- The backend foundation introduced Express/TypeScript, Prisma/PostgreSQL, live-session RBAC/clearance/resource checks, cutoff-aware context building, typed internal adapters, stable errors/request IDs, auditing, and OpenAPI.
- The AI integration wraps the existing `InvestigationEngine` with FastAPI rather than rebuilding it. Express sends `prysm-investigation-context-v1`, validates the response, and transactionally persists analysis runs, findings, evidence links, model versions, and audit records.
- Operational PostgreSQL ingestion is intentionally bounded and deterministic; large Parquet sources remain authoritative. Expand ingestion only through explicit idempotent mappings.
- RAG integration preserves the existing knowledge store and Gemini client. Express mediates public HTTP chat, authorized HTTP/WebSocket chat, admin-only ingestion, source/request correlation, and chat persistence.
- Synchronous analysis currently returns `202` with a durable run record. Preserve that contract when moving execution to a queue/outbox.
- The React/Vite frontend and integrated administrator workspace are implemented. The UI has exactly light and dark themes, uses the normal browser cursor, Lucide icons, Sonner feedback, a large bounded graph demonstration, and backend-mediated public/authorized chat.
- Password-required routing must always follow refreshed backend user state. After a password change, refresh `/auth/me`, permissions, and clearance before navigation; never bypass the guard with a hardcoded redirect.
- Primary technical reference: `ARCHITECTURE.md`. Runtime truth: `current-state.md`. Remaining work only: `todo.md`. Frontend contract: `server/BACKEND_API.md` plus `server/docs/openapi.yaml`.

## Phase 0 baseline audit (2026-09-05)

- The implemented browser is `client/`, a React/Vite/React Router application. It calls Express only; older claims that the frontend was future or absent are stale.
- The runtime ownership boundary is: Parquet and versioned AI artifacts for analytical computation; PostgreSQL/Prisma for operational workflow and persistence; Express for authentication, authorization, orchestration, DTO validation, and audit; RAG for retrieval/generation only.
- There are two graph paths that must remain explicit: AI Engine disk-backed Parquet graph artifacts for analytical graph/GNN recomputation, and PostgreSQL graph nodes/edges for backend context and authorized chat. They need a shared graph snapshot/version contract before scaling.
- Family analysis is not a separate model. It is represented through typed relationship edges and cutoff-aware features such as `family`, `employer_employee`, `shared_device`, `shared_address`, company links, degree, and confidence.
- `POST /investigations/:id/analyze` is synchronous behind HTTP `202`; the database supports `QUEUED`, but the route creates `RUNNING` and completes the run before responding. A durable queue/outbox is the next operational refactor and must preserve the run contract.
- The active AI artifact root is configurable in `ai-engine/api/runtime.py`; deployment must declare and persist the selected run/version to prevent stale artifact consumption.
- The complete baseline, exact repository locations, dependencies, preserve/refactor/remove decisions, and migration map are in root `BASELINE_REPORT.md`.
