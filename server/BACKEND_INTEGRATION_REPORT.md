# Backend Integration Report

## Outcome

Step 8 is operational locally. PostgreSQL, Express, the existing FastAPI AI boundary, and the existing RAG service were run together. Public retrieval, protected ingestion, authorized investigation explanation, backend-relayed WebSocket chat, dependency checks, and PostgreSQL chat persistence succeeded. Express remains the only frontend service boundary.

## Architecture and controls

- PostgreSQL owns operational/source facts and persisted analysis/chat records.
- The AI Engine owns rules, models, GNN intelligence, evidence, and the non-probability assessment.
- RAG owns knowledge retrieval and explanation; Gemini owns natural-language generation. Neither performs authorization or calculates risk.
- Express authenticates live sessions, checks permissions/clearance/resource policy, constructs bounded trusted context, calls internal services, validates responses, maps failures, audits actions, and returns frontend-safe DTOs.
- Public chat is knowledge-only. Authorized HTTP and WebSocket chat receive only server-built cutoff-aware subject, analysis/GNN, finding/evidence, version, limitation, provenance, and bounded-relationship context.
- `/rag/ingest` requires `rag:ingest` and clearance rank 4. Direct RAG POST, ingestion, and WebSocket operations fail closed without the internal key.

## Component status

- PostgreSQL: local connection healthy. Initial migration and `20260829000200_rag_integration` are applied. The latter adds backend/RAG request correlation and structured sources to existing chat persistence.
- AI Engine: `/health`, `/ready`, and `/v1/analyze` remain operational. The real Step 7 investigation/run is preserved; no retraining or model redesign occurred.
- GNN: the deterministic bounded slice remains 250 nodes, 249 edges, and a versioned snapshot. Retrospective embeddings remain reference-only; authorized chat uses persisted results and cutoff-valid context.
- RAG: existing `/health`, `/ask`, `/ingest`, and `/ws/chat` are integrated through a validated timeout-bound adapter. Retrieval is healthy. Gemini keys are configured, but the final provider probe reported `degraded` with safe failure classification `ConnectionError`; answers used the existing local fallback.
- Backend: TypeScript build clean. PostgreSQL and AI Engine reported `ok`; backend health now reports RAG `degraded` unless Gemini has completed a successful generation, so it cannot overstate the full dependency chain.
- Authentication: live database-backed session/user/status/role/permission/clearance checks protect HTTP and WebSocket. Browser-provided trusted context fields are rejected.
- Startup: `npm run dev:stack` starts PostgreSQL → AI Engine → RAG → backend with readiness polling and refuses mismatched/missing internal RAG keys.

## Real verification

- Protected ingestion created document `8f97c19f-567e-4a27-9739-f29e745851ed`. Public retrieval then returned its unique `cobalt-lantern-829` sentinel with the ingested document as a source.
- Public HTTP request `41cb937e-cf21-43cc-be80-4de70cbaaf44` persisted as `PUBLIC` without a user or protected context.
- Authorized HTTP request `82fb3ef6-31e0-4753-bb47-0dd15d55e1f9` used investigation `6e8914d7-e5cf-4dd3-af69-54d0c968b4ca` and persisted as `AUTHORIZED` with its user, sources, and minimal context manifest.
- Backend WebSocket request `ee77f93b-6c2c-4534-86a7-cd1829225ab7` completed `ready → authenticated → token → done`, returned five sources, and persisted.
- The final database query found all three request IDs with `SUCCEEDED` status.
- Automated validation: chatbot `8 passed`; backend `10 passed`; TypeScript build passed. The real stack used an ephemeral matching internal key in process memory, never written to Git or `.env`.

## Required environment input and blockers

One required value is genuinely unknown, and one external dependency is currently unreachable, so unconditional frontend sign-off remains blocked:

- `server/.env` → `RAG_API_KEY`: the user must provide a strong random internal service secret for backend-to-RAG authentication.
- `chatbot/.env` → `RAG_API_KEY`: the user must provide exactly the same value.

Do not commit it. Gemini keys were detected without being printed or changed. Known local URLs are `AI_ENGINE_BASE_URL=http://127.0.0.1:8100` and `RAG_BASE_URL=http://127.0.0.1:8200`; `RAG_TIMEOUT_MS` defaults to `30000`.

After supplying the RAG key, restore outbound connectivity to the configured Gemini endpoint (or correct the existing Gemini key/provider configuration if connectivity is not the cause) and require `/health` to report `llm: ok`. The observed safe error is `ConnectionError`; no secret or provider response body was logged.

Remaining production work is outside Step 8: durable async analysis/outbox, refresh/password/admin workflows, broader operational ingestion, query-plan/load/security testing, denial-audit hardening, dashboards, cursor completion, and controlled model downloads. npm still reports three high findings in the Prisma CLI development chain; the runtime client is not the reported path, and the proposed blind downgrade was not applied.

## Commands

From `server/`:

```text
npm install
npm run db:generate
npm run db:migrate
npm run db:seed
npm run build
npm test
npm run dev:stack
```

Independent services use `python -m uvicorn api.app:app --host 127.0.0.1 --port 8100` from `ai-engine/`, `python -m uvicorn main:app --host 127.0.0.1 --port 8200` from `chatbot/`, then `npm start` from `server/`.
