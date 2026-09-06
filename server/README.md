# Prysm backend — Phase 5

Node.js 22.18+ / Express 5 **JavaScript ESM**, PostgreSQL and Prisma 6. The backend manages access, cases, persisted results, conversation history, knowledge jobs and audit. It never calculates detection scores. The React frontend was not redesigned.

Frontend contract: [docs/API.md](docs/API.md), [OpenAPI JSON](docs/openapi.json). Handoff and measured checks: [PHASE5_STATE.md](../PHASE5_STATE.md). Database ownership: [docs/DATABASE.md](docs/DATABASE.md).

## Setup

From `server/`:

```powershell
npm ci
# Copy .env.example to .env only for a new installation; preserve existing values.
npm run db:generate
npm run db:backup       # existing database, before deploying cleanup migrations
npm run db:migrate
npm run db:seed         # access-control roles/permissions; optional bootstrap admin
npm run sync:metadata
npm run build          # JavaScript syntax check; no compiled dist directory
npm test
npm start
```

Configure `DATABASE_URL`, a random `JWT_ACCESS_SECRET` of at least 32 characters, `AI_ENGINE_API_KEY`, and matching `RAG_API_KEY` in `server/.env` and `chatbot/.env`. Internal secrets must not be empty. `AI_ENGINE_TIMEOUT_MS=600000` allows the first full-population ranking on the small benchmark. Refresh tokens are opaque random values stored only as SHA-256 hashes; a separate refresh JWT secret is not used.

For a new database only, optional `SEED_ADMIN_EMAIL` and `SEED_ADMIN_PASSWORD` provision the bootstrap administrator. The seed updates the bootstrap password if those variables are supplied again; omit them during routine reseeding. Sign-up uses the existing reviewed application flow, not open registration.

## Local services

The coordinated Windows launcher reads the backend AI credential and the matching RAG credentials, starts hidden services and waits for readiness:

```powershell
npm run dev:stack
```

It requires a running local PostgreSQL Windows service and Python with the AI/chatbot dependencies installed. The AI target is **`api.intelligence:app`**, with the selected portable bundle at `ai-engine/reports/phase3/model_bundle.json`; canonical facts remain at `data/benchmarks/prysm-benchmark-v1/`. `PRYSM_MODELS` and `PRYSM_DATASET` override those paths explicitly. Restart the AI process after changing artifacts; its loaded engine/ranking caches are process-local.

For separate terminals, set `AI_ENGINE_API_KEY` in the AI process environment and run `python start.py` from `ai-engine/`; run `python main.py` from `chatbot/`; run `npm start` here. Python services bind to loopback ports 8100/8200, backend port 4000. Local LLM download/inference remains deferred; case explanations work via Phase 4 local evidence extraction. Optional Gemini selects approved general references only.

## Verification and documentation

```powershell
npm run build
npm test
npm run format
npm run verify:integration
npm run verify:phase5
npm run docs:generate
```

`verify:phase5` starts isolated AI/RAG listeners on 18100/18200, an ephemeral backend port, and disables provider calls. It uses the real PostgreSQL schema with disposable users/cases and a copied knowledge corpus, then removes its test application records and stops its services. It can lazily materialize canonical subject summaries, as normal search/ranking does. Do not run it concurrently with another copy. The initial ranking can take minutes.

`docs:generate` checks that all 66 mounted HTTP routes have a reviewed description and generates request schemas from the actual Zod validators. Edit [FRONTEND_FLOW.md](docs/FRONTEND_FLOW.md) and [contract-descriptions.js](docs/contract-descriptions.js), then regenerate. WebSocket behavior is documented alongside the HTTP guide.

Removed entry points: TypeScript compilation/strip-types, `dist/src/server.js`, analytical ingestion scripts and operational slice, old model-registry startup sync, model download tickets, and the old OpenAPI YAML. Existing migration history and historical case results remain preserved. Reanalyze old v1 cases before asking the current explanation service to use them.
