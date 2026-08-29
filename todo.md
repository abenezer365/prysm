# Prysm Project Tasks

## Completed

- [x] Phase 1: canonical data foundation, integrity audit, typed links, and leakage policy.
- [x] Phase 2: normalized transaction facts, leakage-safe as-of features, configurable rules, anomaly and supervised diagnostic baselines, standardized signals, and reproducible evaluation.
- [x] Phase 2.5: label/event provenance audit, cold-start classification, predictive eligibility gate, and invalidation of unaligned supervised evaluation without rewriting source labels.
- [x] Phase 3: canonical temporal financial graph, graph integrity/features, self-supervised relational GraphSAGE representation, cutoff-valid bounded investigations, configurable fusion/confidence, traceable evidence, evaluation artifacts, and validity metadata.
- [x] Phase 3 verification: 549,947 nodes, 3,036,895 edges, zero invalid endpoints/duplicate semantic edges/self-loops/reversed intervals, and 19 passing tests.
- [x] Isolated ground-truth relationship repair: deterministic label-to-account-to-transaction resolution, behavior-aware evidence selection, schema-preserving repaired artifact, per-label decisions, and before/after validation. Existing generator/data remain untouched; 8 focused tests pass.
- [x] Step 4 scenario integration and validation: verified 7,000 aligned two-class observations and 46,094 evidence references; rebuilt Phase 2/2.5/3 in an isolated run; leakage, graph, fusion/evidence, reproducibility, and 19 tests pass. Valid synthetic supervised ROC-AUC is 0.470444; report is `ai-engine/runs/scenario-v1/PHASE_4_RETRAIN_VALIDATION_REPORT.md`.
- [x] Step 6 backend foundation: Express/TypeScript API v1, Prisma operational schema and initial migration, seeded RBAC/clearance policy, live session authorization, cutoff-aware bounded context builder, versioned analysis persistence, AI/RAG adapters, public/authorized chat isolation, audit/model endpoints, OpenAPI, and integration report. Prisma/build validation and 10 tests pass.
- [x] Step 7 real AI/backend integration: FastAPI wraps the existing engine; PostgreSQL migration/seed and bounded canonical graph/GNN ingestion run locally; Express analysis persists request user, context, models, findings/evidence, and audit data. One unmocked end-to-end investigation succeeded; AI tests 24 pass and backend tests 10 pass.
- [x] Step 8 RAG/backend implementation: validated backend adapter, knowledge-only public chat, authorization/clearance/resource-gated investigation context, protected ingestion, backend WebSocket relay, request/source persistence, real dependency health, coordinated startup, OpenAPI/frontend contract, and real local end-to-end verification.

## Backend completion work

- [x] Provision local PostgreSQL, apply the initial migration, seed access controls, and verify live persistence.
- [x] Implement deterministic bounded canonical-data/graph/GNN ingestion without mutating source Parquet datasets.
- [x] Expose the existing Python `InvestigationEngine` behind FastAPI and complete one real Express-to-engine-to-PostgreSQL analysis.
- [ ] Add disposable-database migration rollback, repository/security integration tests, query-plan baselines, and broader ingestion coverage as product workflows require.
- [x] Connect and validate the existing RAG API over HTTP and WebSocket, including real ingestion→retrieval and public/authorized persistence.
- [ ] User configuration: set the same strong `RAG_API_KEY` in `server/.env` and `chatbot/.env`; no value was invented or committed.
- [ ] Resolve Gemini provider `ConnectionError` (network reachability or existing provider configuration), then verify RAG health transitions from `degraded` to `ok` without fallback.
- [ ] Complete refresh-token rotation, password reset/change, application review, user administration, investigation update/timeline/feedback, cursor pagination, dashboards, and controlled model downloads.
- [ ] Add a durable job/outbox path for analysis, audit denied decisions, benchmark graph-context latency, and close the recorded dependency audit findings before production deployment.

## Later scientific work

- [ ] Improve scenario causal precursors: aligned pre-cutoff supervised ROC-AUC 0.470444 and anomaly ROC-AUC 0.487010 show that valid labels alone did not create useful predictive separation.
- [ ] Add a batched cutoff-safe GNN training/evaluation head; never train a predictive head from retrospective full-graph embeddings.
- [ ] Keep supervised results scoped to the synthetic benchmark and defer probability calibration until external/real-world validation supports it.
- [ ] Generate production feature snapshots for arbitrary entity/cutoff batches only after the Phase 4 contract is defined; never deploy the invalid legacy supervised model.
- [ ] Improve and structurally benchmark the self-supervised graph representation (current link-reconstruction ROC-AUC 0.521) without using invalid risk labels.
