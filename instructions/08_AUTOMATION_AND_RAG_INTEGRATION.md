# PRYSM — Final RAG → Backend Integration

## Mission
Finish the integration of the completed `chatbot/` RAG service with the existing Prysm backend and leave the repository ready for frontend development.

Target:

PostgreSQL → Node/Express Backend → AI Engine / RAG → Gemini → Frontend

Keep existing architecture and working code. Do not redesign or add unnecessary infrastructure.

## 1. Inspect First
Inspect only what is necessary across:
- `server/`
- `ai-engine/`
- `chatbot/`
- Prisma schema/migrations
- existing API/OpenAPI docs
- `package.json`, Python requirements
- all relevant `.env` / `.env.example`
- startup scripts
- `memory.md`, `current-state.md`, `todo.md`

Use actual code as the source of truth. Do not invent routes, fields, credentials, models, or services.

## 2. Environment Audit
Check every relevant environment variable for PostgreSQL, backend, AI Engine, RAG, Gemini, auth/session, CORS and frontend URLs.

Fill values only when they are objectively known from the repository.

Never invent secrets, passwords, API keys or production URLs.

For every required unknown value, report:
- file
- variable
- why it is required
- exactly what the user must provide

Keep real secrets out of Git and synchronize `.env.example`.

## 3. PostgreSQL
Verify the existing database, Prisma migration and access-control seed.

Confirm the existing tables support:
- users/auth/RBAC/clearance
- subjects/accounts/transactions
- relationships/graph
- investigations
- analysis runs/findings/evidence
- chat interactions where already designed

Do not create a second database or duplicate schema.

Verify real connection and real persistence.

## 4. AI Engine
Verify the already completed FastAPI AI Engine integration:
- `/health`
- `/ready`
- `/v1/analyze`
- Node adapter
- real inference
- GNN context
- persistence

Do not retrain, redesign, or optimize the models in this task.

Preserve the existing cutoff/leakage rules.

## 5. RAG
The completed `chatbot/` service already provides:
- `GET /health`
- `GET /ask`
- `POST /ingest`
- `WS /ws/chat`

Use its existing implementation.

Do not rebuild the RAG, retrieval system, Gemini client, or knowledge base.

Do not make RAG calculate risk or invent evidence.

## 6. Backend → RAG
Connect the Node backend to the RAG service through a small adapter/client using environment configuration.

Browser must never call RAG directly:

Frontend → Backend → RAG

Use the existing HTTP stack where possible. Add only:
- timeout
- service authentication if configured
- request/response validation
- request IDs
- controlled error mapping

## 7. Public Chat
Public questions must use knowledge retrieval only:

Frontend → Backend → RAG knowledge → Gemini → Backend → Frontend

Never attach protected PostgreSQL, investigation, GNN or AI Engine context to public chat.

## 8. Authorized Chat
For authenticated investigators:

Frontend sends message plus relevant investigation/subject identifiers.

Backend must:
1. authenticate;
2. verify account status;
3. verify permission;
4. verify clearance/resource access;
5. build the permitted InvestigationContext;
6. include relevant AI Engine/GNN findings and evidence;
7. send only authorized context to RAG.

Never trust browser fields such as `authenticated=true`, `clearance`, or `accessScope`.

RAG explains trusted context; it does not authorize the user.

## 9. Intelligence Context
Where permitted, investigator RAG context may include:
- subject summary
- risk/assessment
- findings
- rules
- anomalies
- GNN/network findings
- relevant relationships
- evidence references
- model/version metadata
- cutoff
- limitations

Never let Gemini invent scores, evidence, relationships, or financial facts.

Use wording such as “the system detected” or “the analysis indicates”, not “confirmed fraud”, unless a verified outcome exists.

## 10. Chat Persistence
Use the existing chat interaction schema.

Record where applicable:
- conversation ID
- request ID
- user ID
- public/investigator mode
- question
- answer
- sources
- relevant metadata
- timestamp

Do not store unnecessary secrets or unrestricted sensitive context.

## 11. WebSocket
If the backend exposes realtime chat, route it through the backend:

Frontend WebSocket → Backend → RAG WebSocket → Backend → Frontend

Preserve authentication, clearance, investigation context, conversation ID and request ID.

Do not bypass backend authorization.

## 12. Ingestion
`POST /ingest` must not be publicly writable through the production-facing backend.

If exposed by Node, protect it with appropriate admin/contributor permissions.

Run a real test:

document → ingest → retrieval → answer

Do not treat ingestion as model training.

## 13. Backend API
Inspect the actual Express routes and make the frontend-facing API coherent.

Verify relevant dynamic areas:
- auth
- profile/current user
- search
- subjects
- investigations
- analysis
- findings
- graph
- evidence
- dashboard
- users/applications/admin
- models
- audit
- health
- public chat
- authorized chat

Do not create APIs for static pages such as Terms, Privacy, Academy prose or Research prose.

## 14. BACKEND_API.md
Create/update:

`server/BACKEND_API.md`

This must be the single practical frontend contract.

Document EVERY actual frontend-facing endpoint with:
- method
- route
- purpose
- auth
- permission/clearance
- path/query/body parameters
- request example
- response example
- errors
- pagination
- important frontend behavior

Use the actual implementation as the source of truth. Never invent endpoints or response fields.

## 15. API Consistency
Check and fix obvious inconsistencies in:
- status codes
- JSON shape
- errors
- request IDs
- pagination
- authentication
- IDs
- dates/times

Update OpenAPI if present.

## 16. Security
Verify:

Browser → Backend auth → permission/clearance → authorized context → AI/RAG

Confirm:
- public users cannot access investigations;
- clearance is enforced server-side;
- RAG cannot bypass authorization;
- AI Engine is not browser-accessible;
- secrets are not logged/committed;
- stack traces are not exposed;
- ingestion is protected.

## 17. Health
Backend dependency health must actually check:
- PostgreSQL
- AI Engine
- RAG

Example:

```json
{"postgres":"ok","aiEngine":"ok","rag":"ok"}
```

Report real states only.

## 18. Startup
Verify PostgreSQL, AI Engine, RAG and backend independently.

Then provide a simple coordinated local startup command if practical.

Preferred order:

PostgreSQL → AI Engine → RAG → Backend → Frontend later

Use readiness checks rather than arbitrary sleep delays.

Do not make frontend startup a requirement for backend validation.

## 19. Tests
Run existing tests and add only necessary integration tests.

Prove:
- PostgreSQL connection
- AI Engine health/inference
- RAG health
- backend dependency health
- public chat
- ingestion → retrieval
- authorized investigation chat
- unauthorized chat protection
- analysis persistence
- chat persistence
- WebSocket chat

Most important final flow:

Login → search subject → investigation → AI analysis → investigator asks chatbot about result → backend supplies authorized context → RAG retrieves knowledge → Gemini explains → response returns → interaction persists.

Use real local services for final end-to-end validation.

## 20. Repository Sanity
Check for integration blockers:
- broken imports
- stale environment variables
- hard-coded service URLs
- secrets
- duplicate configuration
- stale docs
- missing migrations
- incorrect API examples
- broken startup commands

Fix only issues required for the integrated project.

## 21. Final Architecture
Preserve these responsibilities:

PostgreSQL → operational/source facts
AI Engine → analysis/intelligence
GNN → graph intelligence
RAG → knowledge retrieval/explanation
Gemini → natural-language generation
Backend → authorization/orchestration/API
Frontend → UI

Do not merge these responsibilities.

## 22. Final Report
Update:

`server/BACKEND_INTEGRATION_REPORT.md`

State exact status for:
- PostgreSQL
- AI Engine
- RAG
- Backend
- GNN
- authentication
- chat/WebSocket
- environment
- startup
- tests

List every remaining blocker and every missing environment value.

Do not claim completion while a required configuration/secret is genuinely missing.

## 23. Completion Condition
The project is ready for frontend implementation only after this works with real local services:

PostgreSQL
↓
Backend
↓
AI Engine
↓
PostgreSQL persistence

and:

Frontend/API client
↓
Backend
↓
RAG
↓
Gemini
↓
Backend
↓
Frontend/API client

and an authorized investigation can flow:

User → Backend auth/clearance → InvestigationContext → AI Engine/GNN result → RAG → Gemini → Backend → persisted chat → frontend.

Do not rewrite working backend TypeScript.
Do not rebuild the AI Engine.
Do not rebuild the RAG.
Do not add unnecessary infrastructure.
Focus on finishing, validating, documenting, and making the whole project frontend-ready.
