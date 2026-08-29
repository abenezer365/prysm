# Prysm Technical Architecture

This is the canonical technical architecture reference for Prysm. Use `memory.md` for durable decisions and history, `current-state.md` for present operational status, `todo.md` for unfinished work, and `server/BACKEND_API.md` plus `server/docs/openapi.yaml` for the frontend API contract.

## System purpose and boundaries

Prysm is an evidence-oriented financial investigation platform. It combines operational records, behavioral/rule signals, temporal graph intelligence, knowledge retrieval, and natural-language explanation. It supports investigators; it does not determine guilt or output a calibrated fraud probability.

```text
Source/derived Parquet ──bounded ingestion──> PostgreSQL
                                              │
Frontend (future Next.js/React) ──HTTP/WS──> Express/TypeScript backend
                                              ├──> FastAPI AI Engine ──> rules/models/GNN/evidence
                                              ├──> RAG service ──> retrieval ──> Gemini/fallback
                                              └──> PostgreSQL persistence/audit
```

The browser communicates only with `/api/v1` and the backend WebSocket. The AI Engine and RAG are internal specialist services. Express is the trust and orchestration boundary.

## Repository structure

| Path | Responsibility |
|---|---|
| `data/` | Immutable canonical raw Parquet inputs, small demo CSVs, and dataset manifests. |
| `generator/synthetic-financial-generator/` | Original configurable synthetic financial-data generator and validation reports. |
| `generator/sythethic-modelizer/` | Standalone synthetic modelizer/generator not referenced by the active backend or AI runtime. Its intended long-term status is not documented; the misspelled directory name is existing repository history. |
| `generator/ground-truth-repair/` | Isolated deterministic attempt to repair original label-to-transaction affiliations without mutating source data. |
| `generator/ground-truth-scenario-generation/` | Isolated balanced scenario dataset generator used for the aligned synthetic benchmark. |
| `ai-engine/` | Python intelligence domain: data readiness, preprocessing, label alignment, features, rules, models, temporal graph/GNN, evidence, fusion, evaluation, artifacts, and FastAPI service boundary. |
| `ai-engine/src/prysm_ai/` | Reusable intelligence implementation and stable contracts. |
| `ai-engine/api/` | FastAPI transport, request/response schemas, readiness, and runtime adapter over the existing engine. |
| `ai-engine/runs/scenario-v1/` | Reproducible isolated scenario integration run with manifests, processed data, graph, models, evaluations, and evidence cases. |
| `server/` | Trusted Node.js/Express/TypeScript API, PostgreSQL/Prisma operational model, authentication/authorization, context construction, AI/RAG adapters, persistence, audit, WebSocket relay, scripts, tests, and API documentation. |
| `server/prisma/` | PostgreSQL schema, additive migrations, and idempotent access-control seed. |
| `server/src/modules/` | Domain services for auth, investigation context/persistence, chat context/WebSocket, and audit. |
| `chatbot/` | Independent FastAPI RAG service, file-backed knowledge base, lightweight retrieval, Gemini key/model rotation, guarded ingestion/authorized calls, WebSocket chat, fallback generation, and tests. |
| `endpoints/` | Postman/API-client generation guidance; not a runtime service. |
| `resources/` | Project references and design assets, including legal/research PDFs and branding. |
| `01_…08_*.md` | Historical implementation specifications. They explain phase intent but are not runtime truth. |

No frontend directory currently exists. The next application layer is planned as React through Next.js, consuming only the backend contract.

## Technology stack

| Technology | Role and rationale |
|---|---|
| PostgreSQL 18 | Relational source of operational facts, identity/access state, investigations, evidence, analysis/chat persistence, versions, and audits. Transactions and constraints provide traceability. |
| Prisma 6 | Typed TypeScript database access, schema definition, migrations, and deterministic access-control seeding. |
| Node.js + Express 5 + TypeScript | Frontend-facing orchestration and security boundary; well suited to API middleware, typed adapters, and HTTP/WebSocket coordination. |
| Zod | Runtime validation for environment, HTTP payloads, context bounds, and internal-service responses. |
| JOSE + Argon2id | Signed short-lived JWT access tokens and password hashing. Refresh tokens are random values stored only as SHA-256 hashes. |
| Helmet, CORS, rate limiting, Pino | HTTP hardening, explicit browser origin policy, abuse limits, structured tracing, and credential redaction. |
| FastAPI + Pydantic + Uvicorn | Typed internal HTTP boundaries for both Python intelligence and RAG services. |
| Python, NumPy, pandas, PyArrow | Deterministic data preparation, features, model inference/evaluation, and Parquet processing. |
| Temporal graph + relational GraphSAGE | Typed network representation and self-supervised structural embeddings; historical investigations recompute from cutoff-valid bounded neighborhoods. |
| RAG knowledge store + lightweight vector retrieval | Retrieves versioned explanatory knowledge without mixing it with operational risk computation. |
| Gemini REST API | Natural-language generation over retrieved knowledge and explicitly authorized context; local evidence-grounded fallback preserves service usability when unavailable. |
| `ws` WebSocket library | Backend-mediated realtime authorized chat while preserving live authentication, context, request IDs, and persistence. |
| Vitest/Supertest and pytest | Backend boundary/security tests and Python intelligence/RAG validation. |
| React via Next.js (planned) | Future browser UI and routing layer. It is not implemented and must not absorb backend authorization or internal-service responsibilities. |

## Data and persistence architecture

Raw analytical data remains in Parquet and is not bulk-copied into the application database. A deterministic exporter creates a bounded operational slice; the server ingestion script maps that slice into PostgreSQL. Expansion must remain explicit, idempotent, and reconcilable.

The Prisma schema groups data into:

- identity and policy: roles, permissions, role grants, clearance levels, users, hashed sessions, and account applications;
- operational facts: subjects, protected profiles, accounts represented through subject references, and transactions;
- graph/GNN mapping: graph nodes/edges, graph snapshots, GNN nodes/edges, and versioned embeddings;
- investigation intelligence: investigations, queries, immutable analysis runs, findings, evidence references, and finding/evidence links;
- RAG and governance: correlated chat interactions, model registry, and audit events.

`RagInteraction` stores conversation ID, backend request ID, upstream RAG request ID, user where applicable, public/authorized scope, question, answer, sources, minimal access/context manifests, version, status, and timestamp. It does not store credentials or unrestricted authorized context.

## AI Engine and GNN

The AI Engine exposes:

- `GET /health`: lightweight process health;
- `GET /ready`: real artifact/runtime readiness;
- `POST /v1/analyze`: optional internal bearer authentication and typed analysis over `prysm-investigation-context-v1`.

Express constructs the context from PostgreSQL using an investigation cutoff, a 365-day lookback, at most three graph hops, at most 250 nodes, interval-valid edges, and future-event exclusion. The AI adapter validates the response before persistence.

The engine combines available behavioral features, configured rules, anomaly/supervised artifacts, graph features, and cutoff-valid GNN structure. Fusion emits strength and confidence with per-component availability, evidence, limitations, model versions, and provenance. Unavailable components are excluded and weights renormalized.

Full-graph features and embeddings are retrospective artifacts. They may support reproducibility and structural reference, but predictive/historical analysis must use a bounded graph filtered at the requested cutoff. The self-supervised GNN evaluates graph representation, not fraud prediction.

## Backend API and orchestration

Express mounts all HTTP routes at `/api/v1` and the authorized chat WebSocket at `/api/v1/ws/chat`. Endpoint families are health, applications/auth/current user, subjects/search, investigations/analysis, graph/evidence, models/audit, public/authorized chat, and protected RAG ingestion. `server/BACKEND_API.md` is the practical frontend guide; OpenAPI is machine-readable.

Cross-cutting behavior includes:

- generated/preserved request IDs and a stable JSON error envelope;
- 1 MB JSON limit, Helmet, explicit credentialed CORS, and rate limiting;
- structured logs with authorization/password/refresh-token redaction;
- timeout-bound, response-validated AI and RAG adapters with sanitized `503` mapping;
- real dependency health for PostgreSQL, AI Engine, retrieval, and successful Gemini generation state;
- audit events for allowed sensitive workflows, including investigation analysis, authorized chat, and ingestion.

Analysis currently executes synchronously but creates a durable run and responds `202`. A future queue/outbox must retain the same run-oriented contract.

## Trust, authentication, RBAC, and clearance

Login verifies an Argon2id password, requires an active account, creates a database session, stores only the refresh-token hash, and signs a short-lived HS256 access token with issuer/audience checks. Every protected HTTP request and WebSocket authentication resolves the token to the current database session, user status, role permissions, and clearance; token claims alone are not treated as current authorization.

Authorization is layered:

1. valid access token and live, unrevoked, unexpired session;
2. active user;
3. required permission code;
4. minimum clearance rank;
5. subject/investigation classification;
6. resource ownership, explicit sharing, or `investigation:read:any`.

Sensitive profiles, graph/evidence, investigations, authorized chat, dependency health, model metadata, audit records, and RAG ingestion each have explicit permissions/clearance. A denial does not reveal whether a protected resource exists.

## Public and authorized chat

### Public chat

```text
Browser → POST /api/v1/chat/public → Express validation
        → RAG GET /ask (knowledge only) → Gemini or fallback
        → Express persists PUBLIC interaction → Browser
```

Only `question` and optional `conversationId` are accepted. Attempts to attach subject, investigation, authentication, clearance, or context fields fail validation. No PostgreSQL investigation, AI result, GNN data, or evidence is sent to RAG.

### Authorized investigator chat

```text
Investigator → Express live auth/RBAC/clearance/resource check
             → AuthorizedChatContextBuilder
             → persisted assessment + GNN + findings/evidence + cutoff/bounded relationships
             → protected RAG HTTP or backend-relayed WebSocket
             → Gemini or fallback → Express persistence/audit → Investigator
```

Authorized HTTP chat requires `investigationId`. The context builder loads only the permitted investigation, latest successful analysis, up to 25 findings with bounded evidence links, limitations and versions, plus a two-hop/75-node operational neighborhood and at most 150 relationships. RAG receives this trusted contract through an internal bearer credential.

Realtime clients must first send an access token to the backend WebSocket, then send a question and investigation ID. Express performs the same authorization/context construction, opens the protected upstream RAG WebSocket, relays `token`/`done`, preserves request/conversation IDs and sources, and persists the completed interaction. The browser never receives the RAG credential or URL.

Knowledge ingestion is not training. Backend `POST /rag/ingest` requires `rag:ingest` and clearance rank 4; direct RAG POST/ingestion/WebSocket operations fail closed if `RAG_API_KEY` is absent.

## Evidence, models, audits, and scientific presentation

Analysis responses and persisted findings link to traceable evidence references. Model registry records expose safe code/version/type/status/evaluation scope and whether a result is calibrated; artifacts and secrets are not downloadable through the current API. Audit records capture actor/session/request, action, resource, decision, metadata, and timestamp where implemented.

Frontend presentation must retain cutoff, version, source/evidence, availability, confidence, limitations, synthetic evaluation scope, and `isFraudProbability=false`. Phrases such as “the system detected” or “the analysis indicates” are appropriate; “confirmed fraud” is not.

## Runtime configuration and startup

Configuration is service-local and validated from `.env`; examples are in `server/.env.example` and `chatbot/.env.example`. Known local defaults are backend `4000`, AI Engine `8100`, RAG `8200`, and planned frontend `3000`. Secrets and production URLs must be supplied by the operator.

`server/scripts/start-local.ps1` starts PostgreSQL → AI Engine → RAG → backend, polling readiness rather than sleeping blindly. It refuses startup when backend and chatbot `RAG_API_KEY` values are empty or different. Each service can also run independently for diagnosis.

## Architectural limits and future direction

- There is no frontend implementation, production deployment topology, durable job queue/outbox, or broad operational ingestion yet.
- Refresh rotation, password recovery, administration/review workflows, dashboards, full cursor pagination, investigation feedback/timeline/export, and controlled model downloads are not implemented.
- Gemini generation is an external dependency; retrieval/fallback may remain usable while provider health is degraded, but the frontend must feature-gate chat based on backend dependency health.
- Disk-backed analytical neighborhood scans and bounded PostgreSQL graph retrieval need measured latency/query-plan baselines before production scale claims.
- Predictive quality remains weak on the valid synthetic scenario benchmark. Calibration and real-world claims require externally valid data and evaluation.
