# Prysm Current State

## System architecture

Prysm now has three explicit specialist runtime domains behind one trusted backend:

- `ai-engine/` owns feature engineering, rules, anomaly/supervised signals, graph/GNN representations, evidence, fusion, and the stable investigation result contract.
- `server/` owns authentication, live authorization, operational PostgreSQL state, bounded context construction, orchestration, persistence, auditing, and frontend-safe `/api/v1` DTOs.
- `chatbot/` owns knowledge retrieval and Gemini-backed explanation. Public access is knowledge-only; protected explanation accepts only backend-authenticated context.

The backend never retrains models, copies AI/RAG logic into TypeScript, or allows the frontend to supply trusted clearance/context. RAG remains independently deployable behind a typed adapter and backend-relayed WebSocket.

## Backend implementation status

Implemented:

- Express 5 and strict TypeScript foundation with validated environment configuration.
- Helmet, explicit CORS, 1 MB JSON limit, rate limiting, request IDs, Pino structured logging/redaction, and a stable error envelope.
- Prisma PostgreSQL schema plus additive initial migration for access, sessions, applications, operational subjects/transactions, graph/GNN mappings, evidence, investigations/findings/runs, RAG interactions, models, and audit events.
- Argon2id passwords, hashed refresh-token storage, short-lived JWT access tokens, and a live PostgreSQL session/user/role/clearance check on each protected request.
- Central permission, clearance, and resource-ownership enforcement; sensitive subject profiles require a separate permission and higher clearance.
- Cutoff-aware `InvestigationContext` v1 with fixed lookback, future-event exclusion, interval-valid graph edges, and hard graph bounds of three hops/250 nodes.
- Typed/sanitized AI Engine and RAG adapters, isolated public/authorized chat, persisted interaction scope, versioned analysis runs, model metadata, evidence lookup, and audit querying.
- OpenAPI 3.1, developer setup, idempotent access seed, and implementation report.
- Validated RAG adapter, public/authorized chat, protected ingestion, curated investigation context, backend WebSocket relay, correlated PostgreSQL chat persistence, and readiness-gated coordinated startup.

Validated:

- Prisma schema: valid.
- Initial SQL migration: generated; includes `citext` extension and indexed relational tables.
- TypeScript: clean build.
- Automated tests: 10 passed across authorization, clearance, IDOR, public-context isolation, authentication enforcement, payload limits, errors, and liveness.
- AI tests: 24 passed, including FastAPI health/readiness, optional API-key enforcement, invalid-context rejection, and real existing-engine inference through the HTTP boundary.
- RAG tests: 8 passed. Real ingestion→retrieval, public/authorized HTTP, WebSocket, and chat persistence passed. The provider-aware health check correctly reports RAG degraded because Gemini generation ended in `ConnectionError` and used fallback.

## Integration readiness

The local PostgreSQL/Express/AI/RAG integration is operational through retrieval, authorization, relay, and persistence. Normal startup is blocked until one matching strong `RAG_API_KEY` is placed in both environment files, and full Gemini readiness additionally requires resolving the observed provider `ConnectionError`. Frontend work can begin against the documented API, but chat should remain feature-gated until dependency health is `ok`.

The AI Engine's scenario result remains a valid controlled synthetic benchmark only: supervised ROC-AUC 0.470444 and anomaly ROC-AUC 0.487010 are weak; rules ROC-AUC is 0.816098 at low recall. Backend responses preserve `isFraudProbability: false`, evidence, cutoff, version, confidence, availability, and limitations.

## Immediate next engineering sequence

1. Add disposable-database migration rollback, live repository/security tests, query-plan baselines, and ingestion reconciliation checks.
2. Convert synchronous analysis execution to a durable job/outbox flow without changing the analysis-run contract.
3. Supply the matching internal RAG secret in both local `.env` files and re-run `npm run dev:stack`; the contract, isolation, timeout, ingestion, WebSocket, and persistence paths are implemented.
4. Finish refresh rotation and remaining administrative/session/workflow endpoints before frontend production integration.
5. Resolve the Prisma CLI development advisory against a safe patched current release; do not apply npm's proposed blind downgrade.
