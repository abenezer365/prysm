# Phase 5 state — backend finalization

**Completed:** JavaScript backend, PostgreSQL cleanup, Phase 3 intelligence integration, Phase 4 explanation integration, and the frontend API contract. No Phase 6 UI/content redesign or large dataset generation was performed. Phase 4's local-model download/inference deferral remains in force.

## Entry points and structure

- Backend: `server/src/server.js`, `app.js`, `routes/index.js`, `routes/completion.js`, `routes/intelligence.js`; JavaScript ESM on Node 22.18+ / Express 5.
- Runtime validation: Zod, `middleware/core.js`, `routes/queries.js`; live session/permission/clearance checks: `middleware/security.js`.
- Auth: `modules/auth/service.js`; cases and result persistence: `modules/investigations/`; authorized context, conversations and WebSocket: `modules/chat/`.
- Explicit upstream boundaries: `integrations/ai-engine/adapter.js`, `integrations/rag/adapter.js`, `integrations/http.js`.
- AI HTTP service: **`ai-engine/api/intelligence.py`**, target `api.intelligence:app`; `ai-engine/start.py` and the coordinated backend launcher use it. Historical `api.app/runtime/schemas` remain only for archived v1 regression use, not the active launch path.
- Source facts: `data/benchmarks/prysm-benchmark-v1/`. Selected model: `ai-engine/reports/phase3/model_bundle.json`. Engine logic/config/models and the Phase 1 dataset were not retrained or altered.

All owned backend `.ts` sources, scripts, seed and tests were migrated to `.js`. Removed TypeScript/tsx/direct `@types` dependencies, `tsconfig.json`, type-only module and strip-types/build-output launch paths. `npm run build` now validates JavaScript syntax; `npm start` runs source directly. Package lock is updated. No frontend code was changed.

## Audit and cleanup decisions

**Keep:** PostgreSQL, Prisma, reviewed account provisioning, users/sessions/RBAC, operational subject references, cases/results/evidence, knowledge/history/audit, and existing public/admin functions used by the client.

**Replace:** archived v1 analytical context/HTTP contract with subject-plus-cutoff calls into the selected Phase 3 engine; legacy authorized chat with trusted stored-result `/explain`; WebSocket upstream relay with the same protected explanation adapter. Graph rendering uses the engine's annotations, without backend severity thresholds.

**Remove:** the unreachable duplicate account-application handler, old finding-based top-suspect ranking, hardcoded dashboard totals, analytical full/slice ingestion scripts and export helper, operational slice JSON, obsolete model-registry startup sync, and download tickets with no redemption implementation. JSON exports now complete inline instead of leaving permanently queued jobs. CSV/PDF are rejected explicitly.

**Improve:** clearance and ownership checks for analysis/runs/graph/evidence; current subject classification checks for direct case operations; conversation context ownership; per-message WebSocket token revalidation and bounded messages; atomic refresh-token rotation; reviewer privilege bounds; finite pagination and UUID validation; consistent JSON error/rate-limit responses; redirect rejection at credentialed boundaries; ingestion updates reuse the existing document registry entry.

Earlier-phase work already present in the workspace was retained. Existing operational subjects and historical case/finding/run records were not purged merely because they originated from v1. Reanalyze a historical case before using its result with current reasoning.

## PostgreSQL

Schema: `server/prisma/schema.prisma`. Table-purpose guide: [server/docs/DATABASE.md](server/docs/DATABASE.md).

Applied successfully to the existing local `prysm` database:

1. `20260906000100_phase5_operational_cleanup`: removes `transactions`, `graph_nodes`, `graph_edges`, `gnn_graph_snapshots`, `gnn_nodes`, `gnn_edges`, `gnn_embeddings`, `dataset_records`, and `model_download_tickets`; adds case-result and conversation indexes.
2. `20260906000200_preserve_analysis_json`: converts `analysis_runs.response_payload` from JSONB to text while preserving existing contents. Engine JSON is serialized once and parsed for responses. This fixes an observed Prisma JSON round-trip that changed some final floating-point digits. Retrieved full results now compare exactly to the analysis response.

The five earlier migrations remain intact as applied history. A successful pre-cleanup custom-format PostgreSQL backup is at `.tmp/database-backups/phase5-2026-09-06T13-02-55.176Z.dump` (private and Git-ignored). No live user/case/evidence records were deleted by cleanup.

`modules/metadata.js` / `npm run sync:metadata` archives old dataset metadata and retires old model registry entries, then exposes six fact-table metadata entries and the selected bundle checksum. It does not copy source facts, predictions or evaluation labels into PostgreSQL. Matching canonical subjects are lazily materialized by search/ranking only.

## AI and RAG contracts

Internal credential is mandatory for AI `/ready`, `/v2/people/search`, `/v2/investigate`, and `/v2/rank`. The backend sends only `{subject:"Person:P01870",cutoff:"2025-12-11T10:00:00Z"}` for analysis. The AI process loads validated canonical facts and the selected Phase 3 bundle, with process-local engine and bounded ranking caches. Computation is serialized. Ranking includes all observed people at the cutoff, not the evaluation-only primary-subject ranking.

The unchanged result contains `version:"prysm-intelligence-v2"`, subject, investigation window, assessment/breakdown, intelligence components, findings, features, evidence, graph, limitations and provenance. Nullable scores remain nullable. Evidence IDs and analysis fingerprints are checked at the backend boundary. No detection/fusion/graph-scoring logic moved into JavaScript.

The backend authorizes the case, reads a successful current result, and sends `{intelligence,question}` to protected Phase 4 `/explain`. It rejects altered detected subject/assessment/evidence or inconsistent provenance. HTTP and WebSocket use this same adapter. Conversations retain question/answer, sources and the source run/fingerprint, not another full intelligence copy. Knowledge ingestion is administrative and cloud approval stays explicit. WebSocket service credentials no longer appear in upstream URL query strings.

Case explanations work locally without an LLM. Optional Gemini reference selection retains Phase 4's allowlisted-topic/approved-general-reference policy. No local-model installation, download, live Gemini verification or cloud case submission is claimed.

## Authentication and important APIs

Sign-up remains `POST /applications` followed by authorized review/provisioning. Sign-in returns an access JWT and opaque refresh token. PostgreSQL stores refresh hashes; each protected request resolves the live session/user/grants. Refresh rotates atomically, logout revokes immediately, and password reset/change flows are retained. A reviewer cannot approve a higher clearance or administrator role beyond the enforced reviewer authority.

Base: `/api/v1`.

- `GET /suspects/top` and `/dashboard/top-suspects`: canonical ranked leads, explicit cutoff, operational subject UUIDs.
- `POST /search`, `GET /subjects/:id`: materialized subject access.
- `POST/GET /investigations`, `GET/PATCH /investigations/:id`: case workflow.
- `POST /investigations/:id/analyze`: synchronous **200** `{runId,status,result}`.
- `GET /investigations/:id/intelligence`: latest successful current result; `GET .../analysis-runs/:runId`: specific persisted run.
- `GET /graph/subjects/:id/subgraph?cutoffAt=...`: engine graph; browser depth/node overrides rejected.
- `GET /evidence/:id`: operational evidence UUID, authorized through linked cases.
- `POST /chat/authorized`, `GET /investigations/:id/conversation`, WebSocket `/ws/chat`: trusted explanation/history.
- `POST /rag/ingest`, document administration and controlled history endpoints: knowledge management.
- `POST /investigations/:id/exports` with `{format:"JSON"}`: completed export and result.

Frontend guide: **[server/docs/API.md](server/docs/API.md)**. Machine-readable schemas: **[server/docs/openapi.json](server/docs/openapi.json)**. All 66 mounted HTTP endpoints have method/path/purpose/auth/request/response/error documentation; WebSocket and realistic investigator examples are included. `npm run docs:generate` derives body schemas from live Zod validators and verifies route-description coverage. Old conflicting API docs are pointers; obsolete OpenAPI YAML is removed.

## Startup and database commands

From `server/`:

```powershell
npm ci
npm run db:generate
npm run db:backup       # existing deployments, before cleanup migration
npm run db:migrate
npm run db:seed         # new access-control setup; omit bootstrap credentials during routine reseeding
npm run sync:metadata
npm run dev:stack      # coordinated local Windows stack
# Or start configured services separately and run:
npm start
```

Use `server/.env` for PostgreSQL, JWT and upstream settings. The AI credential is configured locally without printing it; the local backend ranking timeout was set to 600000 ms. `start-local.ps1` propagates that AI credential into the current Python service. RAG keys must match backend/chatbot configuration. Individual AI launch requires `AI_ENGINE_API_KEY` in its environment. Details: [server/README.md](server/README.md).

## Verification

- **25 backend tests passed**: original API/security tests plus actual Phase 2 result preservation, invalid/substituted AI responses, RAG evidence mutation rejection, private/reclassified case denial, malformed JSON, finite pagination and rate-limit envelope checks.
- **5 new AI HTTP tests passed** against the real selected bundle: fail-closed internal auth, readiness, canonical search/investigation, invalid cutoff/context injection, and unknown subjects.
- **59 Phase 2/3 and chatbot regression tests passed**, including Phase 4's saved-result explanation checks.
- Real PostgreSQL + AI + local RAG + HTTP/WebSocket end-to-end verification passed **31 checks**, covering application approval/login, pre-analysis explanation rejection, private-case denial, exact stored-result retrieval, graph/evidence, local reasoning/history, JSON export, full-population ranking, refresh and logout. The final run also passed knowledge ingestion, re-ingestion/update and disabling. All temporary test services were stopped and disposable application records cleaned.
- Prisma schema validation, applied migration status, JavaScript syntax (35 files), formatting, generated route/document coverage and operational SQL verification passed. SQL verification reported zero analytical-copy tables and preserved baseline counts: 15 cases, 16 runs, 138 findings, 64 evidence references, 71 conversations and 160 audit events after disposable workflow cleanup. Search/ranking materialized four canonical subjects (295 → 299).

Commands:

```powershell
# server/
npm run build
npm test
npm run format
npm run verify:integration
npm run verify:phase5
npm run docs:generate
# repository root
python -B -m pytest ai-engine/tests/test_phase5_api.py -q --tb=short
python -B -m pytest ai-engine/tests/test_phase2.py ai-engine/tests/test_phase3.py chatbot/tests -q --tb=short
```

The integration verifier starts temporary ports 18100/18200 plus an ephemeral backend, uses disposable PostgreSQL users/cases, copies the knowledge directory, explicitly disables provider calls, and cleans its application records/processes afterward. No real private payload was sent to a cloud provider. The installed Prisma 6 warns about package.json seed configuration deprecation; the new AI adapter retains Pydantic 1-compatible class configuration, which warns under the installed Pydantic 2. These warnings do not fail the tests.

## Limitations and Phase 6 entry

This is the small synthetic benchmark, not production-scale efficacy or load validation. First full-population ranking can take minutes; it is synchronous and cached only within the AI process. List endpoints return bounded windows with no implemented continuation cursor. Case-analysis retries are not idempotency-key deduplicated; clients should prevent duplicate submissions. Production reset email delivery, uploaded attachment scanning/storage, automatic retention, TLS/deployment hardening and CSV/PDF export are not introduced.

The frontend still expects some old fields/routes. Phase 6 must adopt `intelligence_components`, `graph`, `is_fraud_probability`, nullable strength, explicit graph/ranking cutoff, synchronous analyze status 200, current explanation fields, JSON exports and retired-ticket removal. Start with the frontend guide and `P6_Content_&_UI-UX.md`. Do not use old evaluation labels/rationales as case evidence. Local LLM inference and the later 1–2 million-row generator remain deferred as previously directed.
