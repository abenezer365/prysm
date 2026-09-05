# Prysm Baseline Report

**Audit date:** 2026-09-05  
**Scope:** Current repository implementation only; no redesign or major runtime changes were made.

## Executive verdict

Prysm is an implemented multi-service investigation platform, not the future-state architecture described in parts of the older documentation. The working path is:

```text
raw Parquet
  -> ai-engine foundation / feature / signal / graph artifacts
  -> FastAPI AI Engine
  -> Express + PostgreSQL context, authorization, persistence
  -> React/Vite client
```

The browser reaches only Express at `/api/v1`. Express is the security and orchestration boundary. The AI Engine owns analytical computation; the RAG service owns knowledge retrieval and language generation; PostgreSQL owns operational workflow and audit state.

The main baseline risks are documentation drift, two graph representations with different ownership, synchronous analysis behind a run-oriented API, and a large analytical artifact surface that must remain versioned and immutable. These are migration concerns, not reasons to redesign the system immediately.

## Repository implementation map

| Location | Actual responsibility | Primary dependencies |
| --- | --- | --- |
| `data/raw/` | Immutable source Parquet: 9 datasets, approximately 1.76M rows | pandas, PyArrow |
| `ai-engine/scripts/` | Foundation, intelligence, label alignment, and graph build entry points | Python, pandas, NumPy, PyArrow |
| `ai-engine/src/prysm_ai/features.py` | Normalization and cutoff/as-of feature construction | pandas, NumPy |
| `ai-engine/src/prysm_ai/rules.py` | Deterministic explainable rule findings | `config/intelligence.json` |
| `ai-engine/src/prysm_ai/models.py` | Local anomaly and supervised baseline inference | NumPy, persisted JSON artifacts |
| `ai-engine/src/prysm_ai/graph.py` | Typed temporal graph and bounded disk-backed subgraphs | pandas, Parquet |
| `ai-engine/src/prysm_ai/gnn.py` | Relation-aware GraphSAGE structural representation | NumPy |
| `ai-engine/src/prysm_ai/investigation.py` | Runtime feature, rule, model, graph, GNN, fusion, and evidence orchestration | all AI modules and artifacts |
| `ai-engine/api/` | FastAPI transport, readiness, search, graph, and analysis contracts | FastAPI, Pydantic, Uvicorn |
| `ai-engine/runs/scenario-v1/` | Isolated aligned scenario data and versioned runtime artifacts | generated Parquet/JSON |
| `server/prisma/schema.prisma` | PostgreSQL operational, investigation, graph, evidence, chat, and audit model | Prisma 6, PostgreSQL |
| `server/src/routes/index.ts` | Browser API routes and workflow orchestration | Express, Zod, Prisma |
| `server/src/modules/investigations/context.ts` | Cutoff-bounded PostgreSQL context builder | Prisma |
| `server/src/modules/investigations/persist-analysis.ts` | Transactional AI finding/evidence/run persistence | Prisma |
| `server/src/integrations/ai-engine/adapter.ts` | Internal AI HTTP adapter and response validation | `fetch`, Zod |
| `server/src/integrations/rag/adapter.ts` | Internal RAG HTTP adapter and response validation | `fetch`, Zod |
| `chatbot/main.py` | File-backed knowledge store, retrieval, Gemini/fallback answers, ingestion, chat WebSocket | FastAPI, Pydantic, local JSON, Gemini REST |
| `client/src/services/api.js` | Single browser HTTP client for Express | browser `fetch` |
| `client/src/app.jsx` | Public/protected route tree and auth gating | React Router |
| `client/src/pages/AppPages.jsx` | Search, investigations, reports, subject views, and GNN presentation | React, Express API |

## End-to-end data flow

### 1. Source data to intelligence artifacts

1. Raw Parquet remains under `data/raw/` and is treated as immutable.
2. AI foundation scripts normalize typed IDs, deduplicate persons with lineage, validate cross-table references, and write processed Parquet under the AI run or project data directories.
3. `features.py` creates leakage-aware as-of snapshots at label or investigation cutoffs. The model feature contract has 33 features covering transaction history, velocity, currency, counterparties, devices, invoices, and relationship behavior.
4. `pipeline.py` writes normalized transactions, feature sets, rule findings, anomaly predictions, supervised predictions, JSON model artifacts, and evaluation reports.
5. `graph.py` creates typed nodes and temporal edges for persons, companies, accounts, banks, devices, invoices, ownership, transfers, invoice links, devices, and relationships.
6. `gnn.py` builds a relation-aware GraphSAGE representation using self-supervised link reconstruction. The artifact explicitly says it is structural and not a predictive fraud-risk model.
7. `phase4.py` verifies the isolated scenario dataset, evaluates alignment/leakage, writes validity metadata, and creates representative investigations.

Important data boundary: the original raw labels are not automatically valid predictive targets. The aligned scenario run is the valid synthetic benchmark; neither benchmark establishes real-world fraud efficacy.

### 2. Search and investigation runtime

1. The client calls `POST /api/v1/search` through `client/src/services/api.js`.
2. Express searches PostgreSQL subjects and asks `AiEngineAdapter.searchPeople()` for the complete Parquet-backed person index.
3. Matching people are lazily upserted into `Subject` and `SubjectProfile` records.
4. Creating an investigation stores a PostgreSQL `Investigation` with subject, cutoff, ownership, and minimum clearance.
5. `POST /investigations/:id/analyze` builds a bounded PostgreSQL context, creates an `AnalysisRun`, calls `/v1/analyze`, validates the response, persists findings/evidence/model versions, audits the action, and returns the result.
6. The AI runtime resolves the canonical typed subject key, loads the configured artifact root, computes cutoff-safe graph/GNN and as-of features, evaluates rules and models, fuses available components, and returns source-backed evidence and limitations.
7. The client renders the persisted or newly returned result in `InvestigationReport`; it presents an attention assessment, not a fraud probability.

The analysis endpoint returns HTTP `202`, but the current implementation waits synchronously for AI completion before responding. The database enum includes `QUEUED`, but the route currently creates `RUNNING` directly.

### 3. Graph and GNN flow to the frontend

There are two related graph paths:

- **Analysis path:** Express builds a bounded PostgreSQL graph context and sends it in `prysm-investigation-context-v1`; the AI Engine uses the subject's canonical typed key and its disk-backed Parquet graph to recompute graph/GNN signals. The resulting graph summary and evidence are persisted in the analysis run.
- **GNN Maze path:** `GET /api/v1/graph/subjects/:id/subgraph` resolves the subject's external reference, calls `AiEngineAdapter.graph()`, and returns an AI Engine graph DTO containing nodes, edges, labels, timestamps, confidence, transaction IDs, and relationship IDs. The client presents this through the GNN Maze page/demo.
- **Authorized chat path:** The backend uses PostgreSQL graph edges from `InvestigationContextBuilder`, limits the chat relationship context to 150 records, and sends that context to RAG. Chat does not directly call the AI graph endpoint.

This is functional but duplicated in representation: PostgreSQL graph tables support authorization/context, while Parquet graph artifacts support analytical graph computation and the visual graph endpoint.

### 4. Chat and reasoning flow

- Public chat: browser -> Express `/chat/public` -> RAG knowledge-only `/ask` -> Gemini or local fallback -> PostgreSQL `RagInteraction`.
- Authorized HTTP chat: Express authenticates the live session, checks ownership/clearance, builds `prysm-authorized-rag-context-v1` from the investigation, latest successful run, findings/evidence, bounded relationships, and limitations, then calls protected RAG.
- Authorized WebSocket chat: backend WebSocket authenticates first, repeats the investigation context/authorization step, relays the upstream RAG WebSocket, and persists the completed interaction.
- RAG retrieves local JSON documents with a lightweight token/frequency embedder. Gemini is optional; fallback answers preserve evidence-oriented language when the provider is unavailable.

RAG explains supplied facts. It does not authorize access, calculate risk, or invent evidence. The backend remains responsible for context construction and persistence.

## Intelligence behavior audit

### Rules

`RuleEngine` evaluates configured rules for unusual amount, transaction bursts, unusual frequency, rapid outflow, foreign-currency inflow change, counterparty change, shared identifiers, and invoice chronology. Each rule emits an explanation, measurements, entity IDs, and transaction IDs. `EvidenceEngine.from_rule()` converts those findings to persisted source references.

### Anomaly and supervised models

The anomaly path uses the persisted NumPy Isolation Forest artifact. The supervised path uses a persisted regularized logistic baseline. Both consume the same leakage-aware feature contract after the persisted preprocessor. The supervised result is explicitly scoped to the aligned synthetic scenario target and is never presented as a calibrated probability.

### Graph, GNN, and family/network analysis

Graph construction is typed and temporal. Predictive mode excludes future event edges, applies interval validity, uses a configurable lookback, and bounds hops/nodes. The GNN is self-supervised structural encoding and neighborhood novelty, not a supervised risk head.

There is no separate family-analysis service or family model. Family and related-party behavior is represented by relationship edge types and as-of relationship features, especially `family`, `employer_employee`, `shared_device`, `shared_address`, company connections, degree, and confidence. These signals enter feature/rule analysis and graph evidence. If family-specific explainability is required later, it should be added as a named evidence view over these existing source edges rather than as a second graph implementation.

### Fusion and evidence

`SignalFusion` renormalizes weights over available components and separates strength, confidence, and coverage. `EvidenceEngine` limits evidence items and references source-backed entities, transactions, relationships, edges, measurements, timestamps, and model artifacts. The contract deliberately returns `is_fraud_probability: false`.

## PostgreSQL audit

PostgreSQL is the operational system of record for:

- identity, sessions, roles, permissions, clearance, applications, and audit events;
- lazily materialized subjects/profiles and bounded operational transactions;
- graph nodes/edges and optional GNN snapshots/embeddings;
- investigations, queries, analysis runs, findings, evidence references, and finding/evidence links;
- RAG interactions and backend-side RAG document records;
- dataset metadata and the optional full `DatasetRecord` mirror populated by `server/scripts/ingest-full-dataset.ts`.

The analytical Parquet files remain authoritative for the AI artifact pipeline. The full dataset ingestion script is a separate operational mirror and should not silently become a replacement for the versioned AI run inputs.

## What currently works

- Typed temporal Parquet foundation, feature generation, rule evaluation, anomaly/supervised baseline artifacts, graph construction, structural GNN encoding, fusion, evidence, and readiness checks.
- Express authentication, refresh rotation, RBAC/clearance, ownership checks, request IDs, validation, audit records, AI/RAG adapters, investigation persistence, public/authorized chat, and backend-relayed WebSocket chat.
- React/Vite public site and protected application with search, subjects, investigations, reports, admin surfaces, chat, and GNN presentation.
- PostgreSQL migrations/schema and deterministic seeds are present.
- Startup orchestration in `server/scripts/start-local.ps1` starts PostgreSQL, AI Engine, RAG, and backend with readiness checks and matching internal RAG keys.

## Duplicated or unnecessary surfaces

1. `ARCHITECTURE.md` previously described a future frontend although `client/` is implemented; documentation must use the actual React/Vite stack.
2. PostgreSQL graph tables and Parquet graph artifacts are both valid for different boundaries, but their ownership and synchronization need one explicit version/snapshot policy.
3. `DatasetRecord` full ingestion duplicates raw Parquet content operationally. Preserve it only for deliberate search/reporting requirements and keep its source version/checksum explicit.
4. `ai-engine/` has root/project outputs and an isolated `runs/scenario-v1/` output. The artifact root is configurable, but operators need one declared active run to avoid consuming stale artifacts.
5. `generator/synthetic-financial-generator/` and the misspelled `generator/sythethic-modelizer/` are separate generator surfaces; the latter is not on the active runtime path and should remain isolated until its ownership is decided.
6. Analysis DTOs, persisted JSON payloads, and frontend report formatting overlap. Keep the AI contract stable and move presentation-only interpretation into a versioned frontend/view contract if it grows.

## Preserve, refactor, replace, remove

### Preserve

- Typed `EntityType:id` identity, immutable raw data, manifests/checksums, cutoff-safe feature/graph rules, validity metadata, evidence provenance, non-probability language, backend-only authorization, and RAG separation.
- `InvestigationEngine`, FastAPI contracts, Express adapters, Prisma investigation/evidence/audit models, and the existing client API boundary.

### Refactor next

- Make the active AI artifact/run version explicit in backend configuration, response provenance, and PostgreSQL `AnalysisRun`.
- Define a shared graph snapshot/version contract between Parquet graph artifacts and PostgreSQL graph tables.
- Move analysis execution behind a durable queue/outbox while preserving the current run-oriented API.
- Add measured pagination/query-plan limits for dataset search, graph retrieval, findings, and audit views.
- Centralize duplicated DTO-to-view mapping and add browser end-to-end coverage.

### Replace only with evidence

- Replace the lightweight RAG embedder only after retrieval evaluation demonstrates a material need.
- Replace the NumPy baselines or add a predictive GNN only with a valid leakage-safe dataset and evaluation protocol.
- Replace disk-backed graph access only after PostgreSQL or another graph store meets measured latency and provenance requirements.

### Do not remove yet

- Raw Parquet, aligned scenario artifacts, validity/evaluation reports, graph manifests, evidence references, startup scripts, lockfiles, or either generator until their outputs are archived and their replacement is verified.

## Migration / implementation map

| Priority | Change | Owning locations | Dependency / exit condition |
| --- | --- | --- | --- |
| P0 | Correct architecture/state documentation | `ARCHITECTURE.md`, `instructions/current-state.md`, `instructions/memory.md` | This report is the baseline; no runtime behavior change |
| P0 | Declare active artifact root and version | `ai-engine/api/runtime.py`, `server/.env.example`, `AnalysisRun` persistence | `/ready`, response provenance, and run record agree |
| P1 | Reconcile graph snapshot ownership | `ai-engine/src/prysm_ai/graph.py`, `server/prisma/schema.prisma`, graph ingestion scripts | Same graph version/cutoff can be traced across AI, DB, UI |
| P1 | Introduce durable analysis execution | `server/src/routes/index.ts`, new worker/outbox module, `AnalysisRun` | Retries/idempotency preserve current 202/run contract |
| P1 | Add contract and end-to-end checks | `ai-engine/tests/`, `server/tests/`, browser test location | Search -> investigation -> analysis -> report -> chat is automated |
| P2 | Measure and optimize data/graph retrieval | `server/src/modules/investigations/context.ts`, AI `GraphStore`, indexes/migrations | Query plans and bounded latency are recorded |
| P2 | Decide generator ownership | `generator/` documentation and manifests | Active generator and archival status are explicit |

## Audit limits

This was a static repository audit after dependency cleanup. It did not reinstall packages, start PostgreSQL/services, or rerun the full test suite. Existing integration documentation records prior successful local runs, but current live readiness should be re-established after dependencies and environment variables are recreated.
