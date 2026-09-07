# Prysm Intelligence

Prysm combines controlled investigations, behavioral and graph analysis, source-backed evidence, and local evidence-grounded explanations. Its synthetic scores are review priorities, not calibrated fraud probabilities.

**Current implementation:** an integrated React, Express/PostgreSQL, Python intelligence, and evidence-grounded reasoning demo. The active synthetic snapshot contains 10,800 chronologically split cases and the UI renders live model, graph, evidence, and person-specific summary results.

- [Backend startup and verification](server/README.md)
- [Frontend API guide](server/docs/API.md)
- [OpenAPI contract](server/docs/openapi.json)
- [Architecture](architecture.md)
- [Database responsibilities and migration safety](server/docs/DATABASE.md)
- [AI engine and evaluation](ai-engine/README.md)
- [Phase 4 reasoning and local-model deferral](PHASE4_STATE.md)

## Local setup

Install Node.js 22.18+, Python with the AI/chatbot dependencies, and PostgreSQL. Configure `server/.env` and `chatbot/.env` from their examples without overwriting existing secrets. The backend needs PostgreSQL credentials, a strong access JWT secret, an internal AI key, and a RAG key matching the chatbot. AI requests fail closed without their internal credential.

Install dependencies and prepare the database from `server/`:

```powershell
npm ci
npm run db:generate
npm run db:backup       # existing databases before Phase 5 cleanup migration
npm run db:migrate
npm run db:seed         # initial access-control setup
npm run sync:metadata
```

Then run the repository-level launcher from the project root:

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

The launcher starts hidden AI, RAG, backend, and frontend processes, selects the retrained demo model when it is present, and waits for every service to become ready. Browser traffic goes only through the backend at `http://127.0.0.1:4000/api/v1`.

## Verification

From `server/`: `npm test`, `npm run build`, `npm run format`, `npm run verify:integration`, and `npm run verify:phase5`. The last command tests real PostgreSQL, AI and local RAG using disposable records and no provider calls. It can take several minutes for the full-population ranking.

The local-model download/inference and the later large synthetic generator remain deferred. Production reset-email delivery, attachment scanning/storage, retention automation and deployment hardening are not included in this phase.
