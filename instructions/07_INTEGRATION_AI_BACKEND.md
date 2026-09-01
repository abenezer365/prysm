# PRYSM AI — Seamless Local Integration Plan
## AI Engine API → PostgreSQL → Node.js Backend → Frontend

**Implementation style:** simple, explicit, maintainable  
**AI Engine API:** Python + FastAPI  
**Backend:** Node.js + Express (plain JavaScript, no TypeScript)  
**Database:** PostgreSQL  
**RAG:** separate service; do not integrate in this step  
**Frontend:** React / Next.js later

---

# 1. Goal

Finish the AI Engine API exposure and make the first complete local backend workflow work.

Target:

```text
PostgreSQL
    ↓
Node.js + Express
    ↓
InvestigationContext
    ↓
FastAPI AI Engine
    ↓
Existing AI / Rules / Anomaly / GNN
    ↓
Structured result
    ↓
Node backend
    ↓
PostgreSQL persistence + audit
    ↓
Frontend API
```

At the end of this task:

- AI Engine runs locally as an HTTP service.
- Backend can call it reliably.
- PostgreSQL is connected and used by the backend.
- Existing GNN data can be mapped to PostgreSQL cleanly.
- Backend can build an investigation context.
- Backend can request real AI analysis.
- Results are persisted.
- Frontend has a clear `API.md`.
- RAG remains separate and untouched.

Do not over-engineer.

---

# 2. Technology Decisions

Use:

## AI Engine

```text
Python
FastAPI
Pydantic
Uvicorn
```

Use the existing AI Engine code. FastAPI is only the HTTP boundary.

## Backend

```text
Node.js
Express
JavaScript
Prisma
Zod
Pino
Helmet
CORS
express-rate-limit
Argon2
JWT
```

Do NOT convert the existing backend to TypeScript.

Do NOT introduce NestJS.

Do NOT introduce GraphQL.

Do NOT introduce a separate microservice framework.

The Node backend should remain a straightforward Express application.

## Database

PostgreSQL is the source of operational truth.

Use the existing Prisma schema/migrations already created in `server/`.

---

# 3. Existing Environment

Backend `.env`:

```env
DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@localhost:5432/prysm"

AI_ENGINE_BASE_URL="http://127.0.0.1:8100"
AI_ENGINE_API_KEY=""
AI_ENGINE_TIMEOUT_MS="120000"
```

The real `.env` is local and must not be committed.

`.env.example` is documentation only.

The AI Engine should have its own environment/configuration.

Do not make the AI Engine depend on Node's `.env`.

---

# 4. AI Engine API

## 4.1 Inspect existing AI Engine first

Before implementation:

- inspect the current Python entrypoint;
- inspect model-loading code;
- inspect current inference functions;
- inspect rule engine;
- inspect anomaly pipeline;
- inspect supervised model;
- inspect GNN code;
- inspect graph feature construction;
- inspect existing result structures;
- inspect existing tests.

Do not rebuild working logic.

Wrap it.

---

# 5. FastAPI Structure

If no existing HTTP layer exists, create a small FastAPI layer around the engine.

Preferred:

```text
ai-engine/
├── api/
│   ├── app.py
│   ├── routes/
│   │   ├── health.py
│   │   └── analysis.py
│   └── schemas.py
├── engine/
├── models/
├── graph/
├── features/
├── rules/
├── anomaly/
└── ...
```

Do not move stable existing files just to match this structure.

A small adapter around the current engine is better than a large refactor.

---

# 6. AI Engine Endpoints

Implement:

```http
GET /health
GET /ready
POST /v1/analyze
```

Optional only where useful:

```http
POST /v1/explain
```

Do not implement an explain route merely because the specification mentions it. Use it only if the current engine already has a clean explanation function.

---

# 7. Health

```http
GET /health
```

Example:

```json
{
  "status": "ok",
  "service": "prysm-ai-engine",
  "version": "1.0.0"
}
```

Purpose:

- process is alive;
- simple local connectivity test.

---

# 8. Readiness

```http
GET /ready
```

This checks whether the components required for inference are loaded.

Example:

```json
{
  "status": "ready",
  "service": "prysm-ai-engine",
  "models": {
    "rules": "ready",
    "anomaly": "ready",
    "supervised": "ready",
    "gnn": "ready"
  }
}
```

Report the real state.

If a component is unavailable:

```json
{
  "status": "degraded",
  "models": {
    "rules": "ready",
    "anomaly": "ready",
    "supervised": "ready",
    "gnn": "unavailable"
  }
}
```

Do not pretend unavailable components are healthy.

---

# 9. API Authentication

For local development:

```env
AI_ENGINE_API_KEY=""
```

means no internal API-key requirement.

When configured:

```env
AI_ENGINE_API_KEY="..."
```

require:

```http
Authorization: Bearer <key>
```

for:

```http
POST /v1/analyze
```

Never log the secret.

---

# 10. Analyze Request

The Node backend sends a backend-built InvestigationContext.

Example:

```json
{
  "requestId": "uuid",
  "investigationId": "uuid",
  "subjectId": "uuid",
  "contextVersion": "1.0",
  "cutoff": {
    "observedUntil": "2026-08-01T00:00:00Z",
    "predictionStart": null,
    "predictionEnd": null
  },
  "subject": {},
  "entities": [],
  "transactions": [],
  "graph": {
    "nodes": [],
    "edges": []
  },
  "signals": [],
  "evidence": [],
  "accessScope": {}
}
```

The precise fields must follow the actual InvestigationContext already implemented in the backend.

Do not invent a duplicate context schema.

Use one canonical shape.

---

# 11. AI Processing

The FastAPI route must delegate into the existing AI Engine:

```text
POST /v1/analyze
       ↓
Pydantic validation
       ↓
existing feature processing
       ↓
rules
       ↓
anomaly
       ↓
supervised model
       ↓
GNN
       ↓
existing aggregation/fusion
       ↓
structured response
```

If some components are intentionally unavailable, return honest availability/limitations information.

Do not manufacture values.

---

# 12. GNN Requirements

The GNN integration must be cutoff-safe.

The backend sends a bounded graph context.

The AI Engine maps:

```text
PostgreSQL graph_node_id
        ↕
GNN node index
```

and:

```text
PostgreSQL graph_edge_id
        ↕
GNN edge index
```

Preserve:

- graph snapshot;
- node mapping;
- edge mapping;
- feature version;
- model version;
- embedding version;
- cutoff.

Do not use retrospective full-graph embeddings for predictive claims.

Phase 4's scientific rule remains:

> post-cutoff graph information must not leak into a cutoff-safe prediction.

---

# 13. GNN Output

Return what the actual GNN can produce.

Example:

```json
{
  "graphIntelligence": {
    "available": true,
    "modelVersion": "gnn-v1",
    "graphSnapshotId": "uuid",
    "embeddingVersion": "embedding-v1",
    "results": [],
    "limitations": []
  }
}
```

Examples of useful results:

```text
node score
neighbor relevance
structural anomaly score
community/network information
embedding metadata
relationship ranking
```

Do not claim supervised predictive GNN performance unless a validated cutoff-safe supervised path exists.

---

# 14. AI Response

Use a stable structure:

```json
{
  "requestId": "uuid",
  "engineVersion": "1.0.0",
  "generatedAt": "2026-08-29T00:00:00Z",
  "risk": {
    "score": 0.0,
    "level": "LOW",
    "confidence": 0.0
  },
  "findings": [],
  "signals": {
    "behavioral": [],
    "velocity": [],
    "foreignCurrency": [],
    "anomaly": [],
    "rules": []
  },
  "graphIntelligence": {
    "available": true,
    "modelVersion": "gnn-v1",
    "results": []
  },
  "evidence": [],
  "modelVersions": {},
  "limitations": []
}
```

Use the engine's existing output names where available.

---

# 15. Node AI Engine Adapter

The Node backend already has an AI adapter.

Make it perform real HTTP calls.

Requirements:

```text
AI_ENGINE_BASE_URL
AI_ENGINE_API_KEY
AI_ENGINE_TIMEOUT_MS
```

Use plain HTTP/fetch or a small HTTP client.

No unnecessary RPC stack.

Flow:

```text
Backend
  ↓
AiEngineClient
  ↓ HTTP POST
FastAPI
  ↓
Existing AI Engine
```

Validate the response before returning it.

---

# 16. PostgreSQL Integration

The local PostgreSQL database has already been created.

Now:

1. run existing Prisma migration;
2. verify all expected tables;
3. seed access control;
4. verify the backend can connect;
5. verify queries against actual PostgreSQL;
6. verify investigation creation and retrieval.

Do not manually create the 25 tables.

Use the existing migration.

---

# 17. Canonical Data Ingestion

Inspect the existing datasets and current AI Engine data access.

Build the smallest reliable bridge from existing source data into PostgreSQL.

Required outcome:

```text
raw/source data
    ↓
canonical mapping
    ↓
PostgreSQL
    ↓
subjects
transactions
relationships
evidence
graph nodes
graph edges
```

Do not duplicate large raw datasets unnecessarily.

When existing tables already represent a source correctly, reuse them.

When a compatibility view is sufficient, prefer the view over another massive copy.

---

# 18. Data Mapping Rules

Every imported entity should have:

- stable internal ID;
- source/reference ID when available;
- type;
- timestamps;
- source information.

For transactions preserve:

- timestamp;
- amount;
- currency;
- sender/receiver;
- source transaction ID;
- transaction type;
- relevant location/channel metadata.

For graph relationships preserve:

- source node;
- target node;
- relationship type;
- first/last seen;
- validity;
- source reference.

---

# 19. GNN PostgreSQL Mapping

Populate the already-created GNN tables.

At minimum:

```text
gnn_graph_snapshots
gnn_nodes
gnn_edges
gnn_embeddings
```

Use:

```text
graph snapshot
    ↓
stable graph node IDs
    ↓
sequential GNN indices
```

Never assume a PostgreSQL UUID can directly be used as a tensor index.

The mapping table is what makes the GNN reproducible.

---

# 20. Investigation Workflow

The main protected workflow must be:

```text
POST /api/v1/investigations/:id/analyze
```

Implementation:

```text
1. authenticate user
2. check account status
3. check permission
4. check clearance
5. load investigation
6. load subject
7. enforce ownership/resource policy where applicable
8. build InvestigationContext
9. enforce cutoff
10. fetch bounded graph
11. attach evidence
12. call AI Engine
13. validate response
14. persist analysis run
15. persist findings
16. persist evidence links
17. audit
18. return result
```

This is the main end-to-end milestone.

---

# 21. Investigation Context

The context builder should produce enough depth for meaningful analysis while remaining bounded.

Default graph:

```text
depth: 3
maxNodes: 250
maxEdges: 2000
```

Respect existing implementation values if already configured.

Include:

```text
subject
related entities
transactions
relationships
temporal information
behavioral signals
velocity data
foreign currency information
rules
anomaly context
evidence
graph structure
cutoff
data snapshot
model/context versions
```

Do not include unrestricted database dumps.

---

# 22. Search

The search endpoint should support investigator workflows:

```http
POST /api/v1/search
```

Example:

```json
{
  "query": "some identifier or subject text",
  "types": ["PERSON", "ACCOUNT", "TRANSACTION"],
  "limit": 25
}
```

Search should return only safe summary fields.

Search results lead to investigation.

Do not expose the entire subject record through search.

---

# 23. Analysis Persistence

Store each analysis run separately.

Required information:

```text
analysis id
investigation id
requesting user
context version
AI Engine version
model versions
graph snapshot
cutoff
status
timestamps
result
```

Do not overwrite previous analyses.

This provides:

- reproducibility;
- version comparison;
- auditability;
- later model evaluation.

---

# 24. RAG Is Not Part of This Task

Do not modify RAG.

Do not invent its API.

Do not make backend startup fail because RAG is not running.

The existing RAG adapter remains a future integration point.

Later:

```text
Backend
   ↓
RAG adapter
   ↓
RAG service
```

Only after the real RAG API is available.

---

# 25. Health Checks

Backend:

```http
GET /api/v1/health
GET /api/v1/health/dependencies
```

Dependencies should include:

```text
postgres
aiEngine
rag
```

At this stage:

```json
{
  "postgres": "ok",
  "aiEngine": "ok",
  "rag": "not_configured"
}
```

Do not report RAG as a failure while intentionally disconnected.

---

# 26. Real Local Test

Prove all of this with real services.

Start:

```text
PostgreSQL
AI Engine
Backend
```

Then test:

```text
GET http://127.0.0.1:8100/health
GET http://127.0.0.1:8100/ready

GET http://localhost:<backend>/api/v1/health/dependencies
```

Then:

```text
login
 ↓
create/open investigation
 ↓
POST /api/v1/investigations/:id/analyze
 ↓
backend builds context
 ↓
FastAPI receives context
 ↓
AI Engine performs actual analysis
 ↓
Node receives result
 ↓
PostgreSQL stores analysis
 ↓
audit event stored
 ↓
frontend-safe JSON returned
```

No mock AI Engine for the final demonstration.

---

# 27. Simple Local Startup

First make all services independently reliable.

Commands should eventually look like:

```bash
# PostgreSQL
# local Windows service/application

# AI Engine
python -m uvicorn api.app:app --host 127.0.0.1 --port 8100

# Backend
npm run dev

# Frontend
npm run dev
```

Once those work independently, create one root-level command.

Preferred final experience:

```bash
npm run dev
```

That root command should start/wait for:

```text
PostgreSQL
→ AI Engine
→ RAG
→ Backend
→ Frontend
```

Do not create artificial sleeps.

Use health/readiness checks.

The orchestrator can be a simple Node script, shell/PowerShell script, or process runner. Choose the most reliable option for the repository's target OS.

---

# 28. Dependency Review

The backend previously reported three high-severity `npm install` findings.

Review them deliberately.

For each:

- determine direct/transitive;
- identify affected package;
- determine exploitability in this project;
- identify safe upgrade;
- test after upgrade.

Do not blindly run a destructive dependency upgrade.

Record the result.

---

# 29. Documentation

Update:

```text
server/README.md
server/docs/openapi.yaml
```

Create/update:

```text
server/BACKEND_INTEGRATION_REPORT.md
```

The report must include:

- startup commands;
- environment variables;
- AI Engine URL;
- AI Engine endpoints;
- database status;
- migration status;
- GNN status;
- end-to-end test result;
- dependency review;
- remaining limitations.

---

# 30. Frontend Contract

Create:

```text
server/docs/API.md
```

This is specifically for the future frontend developer.

It must explain:

- base URL;
- authentication;
- login;
- refresh;
- current user;
- search;
- subject;
- investigations;
- investigation analysis;
- findings;
- graph;
- evidence;
- dashboard;
- users/admin;
- public chat placeholder;
- authorized chat placeholder;
- models;
- audit where permitted;
- pagination;
- error format;
- request IDs;
- examples.

The frontend developer should be able to build the UI using only this file and not need to inspect backend code.

A complete API contract is provided separately below in this task.

---

# 31. Do Not Add Unnecessary APIs

No backend endpoints are needed just for:

```text
Terms
Privacy
Academy static content
Research static content
Developer statement
Static modeling explanations
Static intelligence prose
```

Only dynamic/product behavior receives an API.

---

# 32. Keep It Simple

Do not introduce:

- TypeScript;
- NestJS;
- GraphQL;
- Kafka;
- Redis unless actually required;
- a separate graph database;
- another ORM;
- another service registry;
- Kubernetes;
- unnecessary message queues.

PostgreSQL + Express + FastAPI + the existing AI Engine is sufficient for this stage.

---

# 33. Completion Criteria

This step is complete only if:

### AI Engine
- FastAPI server starts;
- `/health` works;
- `/ready` works;
- `/v1/analyze` works;
- actual existing AI Engine logic runs;
- structured output works.

### PostgreSQL
- backend connects;
- migration works;
- seeded roles/clearances/permissions work;
- canonical data is accessible;
- graph/GNN mapping works.

### Backend
- Node/Express starts;
- AI adapter connects;
- investigation context builds;
- analysis route works;
- results persist;
- audit records persist;
- health reflects real service state.

### Frontend contract
- `server/docs/API.md` exists and accurately describes all frontend-facing APIs.

### Validation
At least one real investigation is analyzed through:

```text
PostgreSQL
→ Express
→ FastAPI
→ existing AI Engine
→ Express
→ PostgreSQL
→ API response
```

No mocked service in the final end-to-end test.

---

# 34. Final Operating Model

Prysm should ultimately run as:

```text
                PostgreSQL
                     ↑
                     |
               Node + Express
                     |
          +----------+----------+
          |                     |
     AI Engine              RAG service
      FastAPI               separate API
          |
     Existing AI
       models
     Rules/ML/GNN
                     |
                     ↓
              React / Next.js
```

The backend is the controlled middle layer.

AI Engine remains independently testable.

RAG remains independently testable.

PostgreSQL remains operational source of truth.

The frontend consumes stable contracts.

---

# 35. Final Instructions to Codex

Inspect first. Reuse existing working code. Simplify rather than duplicate.

Implement the AI Engine HTTP exposure with FastAPI.

Keep the backend in plain Node.js/Express JavaScript.

Connect PostgreSQL through the existing Prisma setup.

Map the existing graph/GNN representation into PostgreSQL without inventing a second GNN architecture.

Make the investigation analysis endpoint fully real.

Do not touch RAG.

Create the frontend `API.md`.

Run the actual services locally and validate the complete end-to-end path.

Report exact results, not assumptions.





After finishing the backend, inspect the entire `server/` implementation and generate:

`server/BACKEND_API.md`

This file is the single API guide for the future React/Next.js frontend.

Document EVERY frontend-facing endpoint that actually exists in the backend, including:
- HTTP method
- full route
- authentication requirement
- required role/clearance/permission
- request headers
- path/query/body parameters
- exact JSON request example
- exact JSON response example
- pagination where applicable
- possible error responses
- short description of what the endpoint does

Cover all relevant areas such as:
auth, users, profile, applications, dashboard, search, subjects, investigations, analysis, findings, graph, evidence, models, audit, health, and chat endpoints that are actually implemented.

Do NOT document internal AI Engine endpoints unless the frontend calls them through the backend.
Do NOT invent endpoints.
Do NOT document static frontend pages.
Use the actual implemented routes and schemas as the source of truth.

Keep `BACKEND_API.md` clean, concise, and easy for a frontend developer/Codex to follow without reading backend code.
Update it whenever the backend API changes.