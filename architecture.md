# Prysm technical architecture — Phase 5

Current handoff: [PHASE5_STATE.md](PHASE5_STATE.md). Earlier scientific decisions remain in [Phase 1](PHASE1_STATE.md), [Phase 2](PHASE2_STATE.md), [Phase 3](PHASE3_STATE.md), and [Phase 4](PHASE4_STATE.md).

## Runtime boundaries

```text
React/Vite client
    |
    | authenticated HTTP / WebSocket
    v
Express 5 JavaScript backend
    |-- PostgreSQL / Prisma: users, live sessions, access policy, cases,
    |                       exact result JSON, evidence references,
    |                       conversations, knowledge jobs, audit
    |
    |-- internal authenticated HTTP --> api.intelligence:app
    |                                   Phase 3 selected engine
    |                                   canonical Phase 1 Parquet facts
    |                                   rules / anomaly / network / GNN / fusion
    |
    +-- trusted stored result --------> Phase 4 /explain
                                        local evidence summary + retrieval
                                        optional approved general references
                                        selected by Gemini
```

The browser receives intelligence; it does not determine suspicion. The backend authorizes and orchestrates; it does not calculate scores. PostgreSQL stores application state, not full analytical datasets or GNN training graphs. Rules, geographic/family/network analysis, anomaly detection, GNN training/inference, fusion and evidence generation remain Python intelligence responsibilities.

## Contracts and ownership

- Canonical facts and provenance: `data/benchmarks/prysm-benchmark-v1/`, [dataset contract](data/benchmarks/prysm-benchmark-v1/DATASET_MANIFEST.md). Ground truth stays evaluation-only.
- Selected model: `ai-engine/reports/phase3/model_bundle.json`; engine implementation: `ai-engine/src/prysm_intelligence/`. [Scientific guide](ai-engine/INTELLIGENCE_V2.md), [measured evaluation](ai-engine/reports/phase3/REPORT.md).
- Active AI HTTP boundary: `ai-engine/api/intelligence.py`. Protected `/v2/investigate`, `/v2/rank`, `/v2/people/search`, `/ready`. Historical v1 modules remain for scientific regression/reproducibility only.
- Backend source: `server/src/`; JavaScript ESM, Node 22.18+, Express 5. [Frontend API](server/docs/API.md), [OpenAPI](server/docs/openapi.json).
- PostgreSQL: `server/prisma/schema.prisma`; [table responsibilities and migrations](server/docs/DATABASE.md). Forward migrations remove analytical duplicates without rewriting applied history.
- Reasoning: `chatbot/reasoning.py` and `chatbot/main.py`. [Phase 4](PHASE4_STATE.md) defines sovereignty boundaries. Stored case results remain private; optional Gemini sees only allowlisted topics and cloud-approved general references.
- Frontend: existing `client/` React/Vite JavaScript. Phase 6 must adopt the finalized contract; no UI/content redesign was performed in Phase 5.

## Workflow and security

Account applications are reviewed before provisioning. Argon2 protects passwords; short-lived access JWTs refer to live PostgreSQL sessions. Opaque refresh tokens are hashed and atomically rotated. Each request rechecks current user status, role permissions and clearance. Cases additionally enforce ownership/sharing and classification. WebSocket messages revalidate live sessions and use the same explanation adapter as HTTP.

An investigation identifies an operational subject UUID and explicit timezone-aware cutoff. The backend resolves its canonical typed key, calls the selected engine, validates provenance, and persists the result. The authoritative response is JSON text in PostgreSQL to preserve exact numeric round trips; API clients still receive a JSON object. Graph/evidence annotations and nullable scores are preserved. Case reasoning uses that stored result, never browser-supplied intelligence or evaluation labels.

Audit records contain event/resource IDs and limited operational metadata, not passwords, tokens, private question text or detector payloads. Conversation records intentionally retain questions/answers locally; retention is operator-managed. Public chat is for general questions and may use cloud generation. Knowledge cloud approval is an explicit administrative decision.

## Current limits

Synthetic scores are review priorities, not calibrated probabilities or guilt determinations. Full-population ranking is synchronous, bounded to the small benchmark and cached per process; its first request can take minutes. Case analysis is synchronous and duplicate submissions are not idempotency-key deduplicated. Lists are bounded windows. JSON export completes inline; unsupported CSV/PDF and obsolete model tickets are unavailable.

Local LLM download/connection/inference remains deferred by the Phase 4 instruction. Production deployment, reset email delivery, attachment scanning/storage and retention automation remain environment-specific work. Phase 6 starts from the API guide; the large synthetic generator remains deferred until after all six phases.
