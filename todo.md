# Prysm Remaining Work

Completed history is retained in `memory.md`; this file contains unfinished work only, ordered by delivery priority.

## P0 — Unblock the complete local stack

- [ ] Put the same strong, uncommitted `RAG_API_KEY` in `server/.env` and `chatbot/.env`.
- [ ] Resolve the Gemini provider `ConnectionError` by verifying outbound reachability and the existing provider/model/key configuration; require RAG `/health` and backend dependency health to report `ok` without fallback.
- [ ] Run `npm run dev:stack` and repeat the login → subject → investigation → analysis → authorized chat → persistence smoke flow with the permanent local configuration.

## P1 — Frontend phase

- [ ] Confirm the frontend packaging choice (planned React via Next.js) and scaffold the application without exposing AI Engine or RAG URLs to the browser.
- [ ] Implement login/logout and bootstrap `/auth/me`, `/me/permissions`, and `/me/clearance`; keep access tokens in memory and handle expiry until refresh rotation exists.
- [ ] Implement clearance-filtered search, subject summary/profile, investigation list/detail/create, analysis execution/result, evidence, and bounded graph views.
- [ ] Implement public and authorized chat clients against backend HTTP/WebSocket contracts; gate chat on dependency health and never send trusted context/clearance claims.
- [ ] Render assessment strength, confidence, component availability, evidence, provenance, cutoff, limitations, and `isFraudProbability=false` accurately.
- [ ] Add frontend contract/error/accessibility tests and end-to-end tests for primary investigator workflows.

## P2 — Complete product workflows

- [ ] Implement refresh-token rotation/reuse protection, password change/reset, session management, and corresponding API/OpenAPI/frontend flows.
- [ ] Implement account-application review, user administration, role/clearance changes, and failure-safe denial auditing.
- [ ] Implement investigation update, timeline, feedback, and any approved export workflow; add real cursor pagination before large lists.
- [ ] Add approved dashboard aggregates and define a controlled model-download policy before exposing either capability.

## P3 — Reliability, data, and production hardening

- [ ] Move synchronous analysis execution to a durable queue/outbox with retries, idempotency, recovery, and observability while preserving the current `202` run contract.
- [ ] Add a disposable PostgreSQL integration environment with migration apply/rollback, live repository/RBAC/clearance/IDOR tests, ingestion reconciliation, and query-plan baselines.
- [ ] Expand operational ingestion through explicit idempotent mappings only where product workflows require broader coverage; keep Parquet sources authoritative.
- [ ] Benchmark and optimize bounded graph/context retrieval, RAG latency, and WebSocket concurrency; add caching/indexing only from measured bottlenecks.
- [ ] Add deployment/runtime packaging, secret management, TLS/reverse proxy, backups/restore, monitoring, retention, and incident procedures.
- [ ] Resolve the recorded Prisma CLI development advisory using a safe supported upgrade; do not apply the proposed blind downgrade.

## P4 — Scientific improvement

- [ ] Improve scenario causal precursors; current valid synthetic supervised/anomaly performance is weak.
- [ ] Build and evaluate a batched cutoff-safe supervised GNN head; never train predictive risk from retrospective full-graph embeddings.
- [ ] Improve structural GNN evaluation without presenting link reconstruction as AML/fraud performance.
- [ ] Defer calibration and real-world performance claims until externally valid data and evaluation support them.
