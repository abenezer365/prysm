# Prysm Current State

Audited against the working repository and local stack on 2026-08-31.

## Status

| Area | State | Current reality |
|---|---|---|
| PostgreSQL | Working | Prisma migrations cover authentication, administration, investigations, analysis, evidence, RAG, contributor review, user settings, and audit. |
| Backend | Working | Express exposes the documented `/api/v1` browser contract, RBAC/clearance checks, admin workflows, internal AI/RAG adapters, and stable errors. |
| Frontend | Working | React/Vite includes the public site, light/dark themes, authentication, investigations, graph/GNN views, permission-gated admin pages, chat, and responsive states. |
| AI Engine | Working with scientific limits | FastAPI health/readiness and analysis operate over the existing investigation engine. Outputs remain uncalibrated decision support. |
| RAG | Working, provider degraded | Retrieval and local evidence-grounded answers work. Gemini remains `configured_not_verified` until a real external response succeeds. |
| Production deployment | Pending | TLS, secret management, backups, monitoring, queue workers, load validation, and hosting remain environment work. |

## Integration baseline

- The browser calls only Express; it never calls AI Engine or RAG directly.
- Person search covers all 100,000 canonical people. Runtime inference builds the original 32 Phase 2 features for the requested person and cutoff, then runs rules, Isolation Forest, supervised baseline, cutoff-safe graph/GNN encoding, fusion, evidence, and an authorized Gemini summary.
- GNN Maze obtains a bounded typed neighborhood from the canonical 549,947-node Parquet graph through Express. It does not require the person to have been part of an old operational graph slice.
- PostgreSQL contains the complete canonical raw-data mirror in `dataset_records` (1,755,020 unique source rows across nine datasets) while retaining separate operational investigation and audit tables.
- Public chat receives knowledge-only questions. Authorized context is constructed server-side after live access checks.
- First-login password change is persisted by the backend; the client refreshes `/auth/me`, permissions, and clearance before routing.
- The admin workspace uses real APIs for users, RAG, news, activity, review queues, bugs, settings, and health.
- Supported Windows startup is `npm run dev:stack` from `server/`; see `Readme.md` for exact setup and manual commands.

## Genuine limits

- Gemini requires external connectivity and a valid provider key; grounded fallback remains available while degraded.
- Analysis waits for the AI adapter after creating a durable run instead of using a production queue.
- Export workers, model-ticket redemption, multipart RAG upload/scanning/OCR, deployment, and load testing are incomplete.
- Browser automation was unavailable during the latest polish pass; source, API, build, tests, and live HTTP flows were used.
