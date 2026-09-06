# Prysm Intelligence

Prysm combines controlled investigations, behavioral and graph analysis, source-backed evidence, and local evidence-grounded explanations. Its synthetic scores are review priorities, not calibrated fraud probabilities.

**Current implementation:** [PHASE5_STATE.md](PHASE5_STATE.md). The backend is JavaScript ESM with Express 5 and PostgreSQL/Prisma. It serves the selected Phase 3 intelligence and Phase 4 reasoning contracts. Phase 6 frontend work has not started.

- [Backend startup and verification](server/README.md)
- [Frontend API guide](server/docs/API.md)
- [OpenAPI contract](server/docs/openapi.json)
- [Architecture](architecture.md)
- [Database responsibilities and migration safety](server/docs/DATABASE.md)
- [AI engine and evaluation](ai-engine/README.md)
- [Phase 4 reasoning and local-model deferral](PHASE4_STATE.md)

## Local setup

Install Node.js 22.18+, Python with the AI/chatbot dependencies, and PostgreSQL. Configure `server/.env` and `chatbot/.env` from their examples without overwriting existing secrets. The backend needs PostgreSQL credentials, a strong access JWT secret, an internal AI key, and a RAG key matching the chatbot. AI requests fail closed without their internal credential.

From `server/`:

```powershell
npm ci
npm run db:generate
npm run db:backup       # existing databases before Phase 5 cleanup migration
npm run db:migrate
npm run db:seed         # initial access-control setup
npm run sync:metadata
npm run dev:stack
```

The Windows stack launcher starts hidden AI, RAG and backend processes with the current AI entry point. See the backend guide for independent terminals, environment requirements and optional initial administrator provisioning. Browser traffic goes only through the backend at `http://127.0.0.1:4000/api/v1`.

Run the existing frontend separately from `client/` with `npm install` then `npm start`. Its Phase 6 work must adopt the finalized API fields, explicit cutoff requirements and completed JSON exports.

## Verification

From `server/`: `npm test`, `npm run build`, `npm run format`, `npm run verify:integration`, and `npm run verify:phase5`. The last command tests real PostgreSQL, AI and local RAG using disposable records and no provider calls. It can take several minutes for the full-population ranking.

The local-model download/inference and the later large synthetic generator remain deferred. Production reset-email delivery, attachment scanning/storage, retention automation and deployment hardening are not included in this phase.
