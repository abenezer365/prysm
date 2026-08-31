<!-- Durable project knowledge for future agents. Runtime status belongs in current-state.md; actionable work belongs in todo.md. -->

# Prysm Project Memory

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
