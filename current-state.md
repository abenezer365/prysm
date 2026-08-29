# Prysm Current State

Audited against repository code, Prisma migrations/schema, environment examples, API contracts, integration reports, and tests on 2026-08-29. See `ARCHITECTURE.md` for design; this file records only what exists and works now.

## Status summary

| Area | State | Current reality |
|---|---|---|
| PostgreSQL | Working | Local PostgreSQL 18 service is running. Prisma models and both migrations cover access/session, operational facts, graph/GNN mappings, investigations, analysis/evidence, RAG interactions, models, and audit. Local migration, seed, bounded ingestion, analysis persistence, and chat persistence were exercised. |
| Backend | Working | Express 5/TypeScript builds and exposes `/api/v1`; security middleware, request validation, stable errors, request IDs, rate limiting, redacted logs, AI/RAG adapters, audit, and WebSocket relay are implemented. No backend process is currently listening on port 4000. |
| AI Engine | Working | FastAPI exposes `/health`, `/ready`, and `/v1/analyze` over the existing Python `InvestigationEngine`. Real Express → AI → PostgreSQL analysis previously succeeded with persisted findings/evidence. No AI process is currently listening on port 8100. |
| GNN | Working with scientific limits | Typed temporal graph, graph features, cutoff-filtered bounded inference, self-supervised GraphSAGE artifacts, evidence, and fusion exist. Retrospective embeddings are reference-only; no validated supervised cutoff-safe GNN risk head exists. |
| RAG/retrieval | Working | Existing knowledge store, lightweight retrieval, `/health`, GET/POST `/ask`, protected `/ingest`, and `/ws/chat` work. Express HTTP/WebSocket integration, protected ingestion, authorized context, sources, request correlation, and persistence were validated. No RAG process is currently listening on port 8200. |
| Gemini generation | Degraded | Keys are configured locally, but the last real provider attempt ended with safe classification `ConnectionError`; RAG used its local evidence-grounded fallback. RAG dependency health remains degraded until an actual Gemini response succeeds. |
| Internal RAG authentication | Blocked by configuration | `RAG_API_KEY` is blank in both local `.env` files. Normal coordinated startup deliberately fails closed. The same strong secret must be supplied to `server/.env` and `chatbot/.env`. |
| Frontend | Pending | No React/Next.js application exists. The frontend-facing HTTP/WebSocket contract is documented and implementation can begin, with chat feature-gated until RAG dependency health is `ok`. |
| Production deployment | Pending | No container/orchestrator/cloud deployment, durable analysis queue, broad operational ingestion, load/query-plan baseline, or production security validation exists. |

## Implemented API and integration

- Backend HTTP groups: liveness/readiness/dependencies; account application; login/logout/current user; permissions/clearance; subject search/profile; investigation create/list/detail/analyze/run; bounded graph; evidence; models; audit; public chat; authorized chat; protected RAG ingestion.
- Backend realtime endpoint: `/api/v1/ws/chat`; it requires first-message access-token authentication, then applies live permission, clearance, and investigation resource checks before relaying trusted context to RAG.
- Public chat rejects protected context fields and persists a `PUBLIC` interaction. Authorized chat requires `investigationId`, constructs current permitted AI/GNN/findings/evidence context, and persists an `AUTHORIZED` interaction with sources and a minimal manifest.
- Dependency health performs real PostgreSQL, AI Engine, and provider-aware RAG checks. The overall status is degraded unless all three report `ok`.
- Coordinated Windows startup is `npm run dev:stack` from `server/`; it uses readiness polling and requires matching non-empty RAG service keys.

## Data and scientific state

- Canonical graph artifacts: 549,947 nodes and 3,036,895 temporal edges with zero invalid endpoints recorded in the manifest.
- Scenario run: 7,000 leakage-audited synthetic observations over 747,582 transactions. Supervised and anomaly discrimination are weak; rules rank better but have low recall. All outputs remain synthetic benchmark evidence and non-probabilistic decision support.
- PostgreSQL contains a bounded representative operational slice rather than the full Parquet corpus. Raw/derived Parquet artifacts remain the analytical source of truth.

## Verification baseline

- Backend: TypeScript build passed; Prisma schema validated; 10 Vitest tests passed.
- AI Engine: 24 pytest tests previously passed, including real FastAPI inference through the existing engine.
- RAG: 8 pytest tests passed; real protected ingestion→retrieval, public/authorized HTTP chat, backend WebSocket relay, and database persistence were exercised.
- OpenAPI YAML parses successfully. The test suite does not yet provide disposable-database migration rollback, full live repository authorization coverage, load testing, or frontend tests.

## Readiness decision

The backend, AI/GNN boundary, retrieval integration, persistence contracts, and frontend API documentation are sufficiently complete to start the frontend phase. Non-chat screens can integrate now. Chat must remain feature-gated until a matching internal `RAG_API_KEY` is configured and Gemini health changes from `degraded` to `ok`. Production readiness is not claimed.
