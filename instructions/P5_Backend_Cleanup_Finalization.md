# PHASE 5 — BACKEND CLEANUP + POSTGRESQL + API FINALIZATION

## ROLE

You are implementing Phase 5 of Prysm Intelligence.

Assume Phases 1–4 are complete.

Read the current project state/memory files first, especially:

* Phase 1 data manifest
* Phase 2 AI/evidence outputs
* Phase 3 evaluation results
* Phase 4 RAG/LLM interfaces

Then inspect the existing backend and PostgreSQL implementation.

Do not redesign from assumptions.

---

# 1. PRIMARY OBJECTIVE

Finish the backend behind the already-built Prysm intelligence system.

The goal is to:

1. remove obsolete/duplicate backend and PostgreSQL builds
2. clean and improve the existing PostgreSQL architecture
3. connect the backend properly to the completed AI/RAG capabilities
4. finalize the backend behavior behind the scenes
5. expose a clean API suitable for the frontend
6. finish with a clear frontend API guide

**PostgreSQL remains the SQL database.**

Do not migrate the backend database to MongoDB.

---

# 2. AUDIT THE EXISTING BACKEND FIRST

Trace the actual current system:

```text
frontend
→ API
→ backend
→ PostgreSQL
→ AI engine
→ RAG/LLM
```

Inspect:

* routes
* controllers
* services
* database queries
* schemas/migrations
* authentication
* investigation/case logic
* AI integration
* graph/evidence integration
* RAG integration
* logging
* duplicated/obsolete database structures

Determine what is:

```text
KEEP
IMPROVE
REMOVE
REPLACE
```

Do not preserve old implementations merely for compatibility when they are no longer needed.

---

# 3. CLEAN POSTGRESQL

Treat the existing PostgreSQL implementation as something to improve, not something to blindly preserve.

Remove obsolete tables, duplicate structures, unused columns, abandoned migrations, dead queries and old builds **only after tracing their dependencies**.

Keep the database focused on actual application/operational needs.

Do not copy the entire analytical dataset into PostgreSQL without a real application requirement.

Where analytical data should remain in its existing analytical form, keep that separation.

The final PostgreSQL structure should be clear enough that another developer can understand why each important table exists.

---

# 4. BACKEND RESPONSIBILITIES

Keep the backend responsible for application concerns.

It should support the functionality Prysm actually needs, including where applicable:

* authentication
* users/sessions
* investigations/cases
* suspect/result access
* evidence access
* graph evidence access
* RAG conversations
* knowledge ingestion
* persistence of required application state
* logging/auditing

Do not move AI detection logic into the backend.

Rules, anomaly detection, graph/GNN, family analysis, fusion and evidence generation remain intelligence responsibilities.

---

# 5. INTEGRATE THE AI ENGINE

Use the actual Phase 2 output contracts.

The backend must cleanly expose the intelligence already built.

It should be possible to retrieve information such as:

```text
top suspects
risk score
risk breakdown
evidence
suspicious transactions
suspicious entities
suspicious relationships
graph evidence
```

Do not recreate these calculations in backend code.

The backend should orchestrate and expose them.

---

# 6. INTEGRATE RAG / LOCAL LLM

Use the Phase 4 reasoning interface.

The backend should provide the application layer for:

```text
investigation context
reasoning requests
conversation history
knowledge ingestion
RAG responses
```

The local LLM remains the reasoning component.

Do not put prompt logic, retrieval logic or model logic into random controllers.

Keep the integration boundary explicit.

---

# 7. AUTHENTICATION / APPLICATION STATE

Finalize the real application flow needed by Prysm:

```text
sign up
sign in
sign out
authenticated requests
authorization
investigations/cases
```

Use the simplest secure design compatible with the existing project.

Persist only what the application actually needs.

---

# 8. API DESIGN

Design the API around the actual Prysm investigator workflow rather than exposing database tables directly.

The frontend should be able to do things such as:

```text
get top suspects
get suspect details
get risk breakdown
get evidence
get transactions
get graph/network evidence
create/open investigation
retrieve investigation state
send reasoning/RAG request
retrieve conversation/history
```

Use the actual implemented domain model to determine the final route structure.

Keep routes predictable and responses consistent.

Do not create dozens of endpoints without a frontend/use-case requirement.

---

# 9. GRAPH API

The frontend GNN Maze must be able to retrieve the graph information required to render:

```text
nodes
edges
relationships
transactions
suspicious elements
```

The API must preserve the AI-generated evidence identifying what should be highlighted.

The backend must not independently decide what is suspicious.

---

# 10. API CONTRACT / FRONTEND GUIDE

This is a required deliverable.

Create a clear API guide for the frontend containing, for every endpoint:

```text
METHOD
PATH
PURPOSE
AUTH REQUIREMENT
REQUEST
RESPONSE
ERROR CASES
```

Include realistic example requests/responses.

Document the endpoints required for the complete investigator flow.

The guide must be good enough that a frontend developer can implement Phase 6 without reading backend internals.

Keep it synchronized with the actual implementation.

---

# 11. ERROR HANDLING / VALIDATION

Finalize consistent handling for:

* invalid requests
* unauthorized access
* missing resources
* database failures
* AI failures
* RAG/LLM failures
* malformed data

Do not expose internal database/model details unnecessarily.

---

# 12. LOGGING / AUDIT

Finalize appropriate backend logging and audit behavior.

Record meaningful application events without unnecessarily logging sensitive information.

Ensure the implementation is consistent with the sovereignty requirements from Phase 4.

---

# 13. CLEANUP REQUIREMENT

This phase is explicitly allowed to remove old backend/database builds.

Do not leave multiple competing implementations of the same functionality simply because the repository already contains them.

After understanding dependencies, remove obsolete code and structures.

The final backend should have one clear implementation path for each major responsibility.

---

# 14. DO NOT IMPLEMENT PHASE 6

Do not perform the final frontend/content/UI redesign.

Do not consume the upcoming content guide yet unless it is already required to validate an API response.

Your output for the frontend is the **API and integration contract**, not the final UI.

---

# 15. ACCEPTANCE CRITERIA

Phase 5 is complete when:

1. PostgreSQL remains the application's SQL database.
2. Obsolete/duplicate database and backend structures have been removed safely.
3. The remaining PostgreSQL design is coherent and justified.
4. Backend responsibilities are clearly separated from AI responsibilities.
5. Phase 2 intelligence is correctly exposed through backend APIs.
6. Phase 4 RAG/LLM functionality is integrated correctly.
7. Authentication/application flows work.
8. Investigator/case functionality required by Prysm works.
9. Graph/evidence data is accessible to the frontend.
10. Top-suspect and investigation data are accessible.
11. API responses are consistent and usable.
12. A complete, accurate frontend API guide exists.
13. No unnecessary backend architecture remains.

---

# 16. STATE UPDATE

Update the root technical state/memory file with the actual final state.

Record:

```text
backend structure
PostgreSQL structure
removed legacy components
AI integration points
RAG integration points
authentication flow
important API routes
request/response contracts
frontend API guide location
startup commands
database commands/migrations
tests
known limitations
Phase 6 entry point
```

Record actual repository paths and implementation details.

---

# FINAL RULE

Inspect first.

Keep PostgreSQL.

Clean the existing backend instead of replacing it unnecessarily.

Remove obsolete builds.

Align the backend with the intelligence and reasoning already completed.

Finish the behind-the-scenes application flow.

Then produce a precise API guide that allows the frontend work in Phase 6 to begin immediately.

Complete Phase 5, verify the APIs end-to-end, update the technical state, and STOP.
