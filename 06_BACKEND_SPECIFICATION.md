# PRYSM AI — Backend Specification
## Node.js + Express + PostgreSQL
### Authoritative implementation contract for the backend layer

**Status:** Implementation-ready specification  
**Purpose:** Build the production-oriented backend and its contracts so the future React/Next.js frontend can consume Prysm AI without knowing how the internal intelligence engine works.

---

# 1. Executive Decision

Prysm AI's backend is the **application and orchestration layer** between the frontend, PostgreSQL, the existing Python AI Engine, and the existing RAG service.

The backend MUST NOT reimplement the AI Engine or RAG.

The backend MUST:

1. Authenticate users.
2. Authorize every protected action using role + security clearance.
3. Store operational truth in PostgreSQL.
4. Build bounded, cutoff-aware **InvestigationContext** objects from database and graph relationships.
5. Call the existing AI Engine through a controlled adapter.
6. Call the existing RAG service through a controlled adapter once its API is supplied.
7. Record the middle conversation with RAG for auditing/evaluation/retraining.
8. Expose stable versioned API contracts to the frontend.
9. Store and expose investigation results, evidence references, graph relationships, model metadata, and audit events where required.
10. Enforce security boundaries centrally rather than scattering permission logic across controllers.
11. Keep static informational pages out of the backend unless they become dynamic later.
12. Make the frontend independent of internal Python/model implementation details.

The backend is NOT responsible for:

- training ML models;
- training the RAG model;
- implementing the RAG retrieval engine;
- replacing the existing AI Engine;
- becoming the model-training platform;
- turning every website page into an API resource;
- implementing static Terms, Privacy, Academy, Research prose, developer statements, etc.;
- inventing a new predictive methodology just to improve benchmark scores.

---

# 2. Existing Prysm Architecture

The backend must preserve this separation:

```text
                      PRYSM AI
                         |
       +-----------------+-----------------+
       |                 |                 |
 PostgreSQL          AI Engine             RAG
 source of truth     intelligence          explanation/
 operational data    + graph/ML            retrieval
       |                 |                 |
       +-----------------+-----------------+
                         |
                  Node.js / Express
                  orchestration/API
                         |
                    React / Next.js
```

The intended responsibility split is:

### PostgreSQL
Operational source of truth:
- users
- roles/clearances
- permissions
- investigations
- subjects/entities
- transaction and relationship data needed operationally
- graph node/edge mappings
- evidence references
- saved findings
- audit events
- RAG interaction metadata
- model registry metadata
- access decisions and workflow state

### AI Engine
Existing Python intelligence system:
- supervised ML
- anomaly detection
- rules
- graph/GNN intelligence
- behavioral signals
- transaction velocity
- foreign-income/currency anomalies
- network intelligence
- evidence-backed scoring
- model/version-specific inference

### RAG
Existing service in `/rag`:
- retrieval
- LLM prompting
- response generation
- public/authorized knowledge response according to its own implementation

The backend supplies the authorized context and records the interaction. RAG remains independently deployable.

---

# 3. Core Backend Principles

## 3.1 Contract over implementation

The frontend must interact with stable domain APIs such as:

```text
GET  /api/v1/investigations/:id
POST /api/v1/investigations
POST /api/v1/investigations/search
GET  /api/v1/subjects/:id
POST /api/v1/chat
```

The frontend must NOT know:

- Python module names;
- model file locations;
- internal model class names;
- database joins;
- graph database internals;
- RAG prompt construction;
- feature-engineering implementation.

## 3.2 Central authorization

Every protected route goes through:

```text
authentication
    ->
identity resolution
    ->
role/clearance authorization
    ->
resource-level authorization
    ->
controller/service
```

Controllers must never independently invent clearance rules.

## 3.3 Least privilege

A user receives only the information and actions required by their clearance and role.

Never return sensitive columns merely because the database query selected them.

Use response DTOs / serializers.

## 3.4 Evidence-first intelligence

AI results should point back to evidence references whenever evidence exists.

The backend should preserve:

```text
finding
 -> signal
 -> source entity/transaction
 -> evidence reference
 -> time
 -> model/rule version
```

## 3.5 Cutoff awareness

Any predictive investigation context must preserve:

- observation cutoff;
- prediction horizon when relevant;
- feature availability time;
- data snapshot/version.

Never silently mix future/post-cutoff evidence into a supposedly pre-cutoff predictive context.

---

# 4. Technology Stack

## Required

- Node.js
- Express
- TypeScript
- PostgreSQL
- Prisma ORM OR Knex/SQL migration layer

### Recommended implementation

Use:

- TypeScript
- Express
- Prisma for schema/migrations/query ergonomics
- `pg` underneath Prisma where appropriate
- Zod for request/response validation
- Pino for structured logging
- Helmet
- CORS
- express-rate-limit
- Argon2id for password hashing
- JWT access tokens + refresh-token strategy
- UUIDs
- OpenAPI 3.1
- Vitest or Jest
- Supertest
- ESLint
- Prettier

Do not add libraries solely for fashion. Each dependency must have a clear job.

---

# 5. Suggested Project Structure

```text
backend/
├── src/
│   ├── app.ts
│   ├── server.ts
│   │
│   ├── config/
│   │   ├── env.ts
│   │   ├── database.ts
│   │   ├── security.ts
│   │   └── services.ts
│   │
│   ├── middleware/
│   │   ├── authenticate.ts
│   │   ├── authorize.ts
│   │   ├── validate.ts
│   │   ├── errorHandler.ts
│   │   ├── requestId.ts
│   │   ├── rateLimit.ts
│   │   └── audit.ts
│   │
│   ├── common/
│   │   ├── errors/
│   │   ├── pagination/
│   │   ├── security/
│   │   ├── serializers/
│   │   └── types/
│   │
│   ├── modules/
│   │   ├── auth/
│   │   ├── users/
│   │   ├── access/
│   │   ├── subjects/
│   │   ├── investigations/
│   │   ├── graph/
│   │   ├── evidence/
│   │   ├── intelligence/
│   │   ├── chat/
│   │   ├── audit/
│   │   ├── models/
│   │   ├── applications/
│   │   └── health/
│   │
│   ├── integrations/
│   │   ├── ai-engine/
│   │   └── rag/
│   │
│   ├── db/
│   │   ├── schema/
│   │   ├── migrations/
│   │   └── seed/
│   │
│   └── routes/
│       └── index.ts
│
├── prisma/
│   └── schema.prisma
│
├── tests/
├── docs/
│   └── openapi.yaml
├── package.json
├── tsconfig.json
└── .env.example
```

Module boundaries are preferred over one giant controller/service directory.

---

# 6. Database Design

The schema below is the baseline. During implementation, reconcile field names and relationships with the existing PostgreSQL schema rather than destroying compatible existing data.

Use UUID primary keys for application records.

Use explicit timestamps:

- `created_at`
- `updated_at` when mutable

Prefer UTC storage.

---

# 7. User and Access Schema

## 7.1 users

```text
users
-----
id UUID PK
email CITEXT UNIQUE NOT NULL
password_hash TEXT NOT NULL
display_name TEXT NOT NULL
profile_image_url TEXT NULL
status user_status NOT NULL
role_id UUID FK -> roles.id
clearance_level_id UUID FK -> clearance_levels.id
last_login_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Never expose `password_hash`.

Possible status:

```text
PENDING
ACTIVE
SUSPENDED
DISABLED
REJECTED
```

## 7.2 account_applications

Supports:

```text
application -> admin review -> approval/rejection -> account activation
```

```text
account_applications
--------------------
id UUID PK
email CITEXT NOT NULL
display_name TEXT NOT NULL
organization TEXT NULL
requested_role_id UUID NULL
requested_clearance_level_id UUID NULL
reason TEXT NULL
status application_status NOT NULL
reviewed_by UUID NULL FK -> users.id
reviewed_at TIMESTAMPTZ NULL
review_reason TEXT NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Do not automatically grant privileged clearance based on requested clearance.

## 7.3 roles

```text
roles
-----
id UUID PK
code TEXT UNIQUE NOT NULL
name TEXT NOT NULL
description TEXT
created_at TIMESTAMPTZ NOT NULL
```

Initial roles may include:

```text
REPORTER
ANALYST
INVESTIGATOR
SENIOR_INVESTIGATOR
ADMIN
```

These are implementation defaults and can be changed through seed/configuration rather than hard-coded into every route.

## 7.4 clearance_levels

Clearance is separate from role.

```text
clearance_levels
----------------
id UUID PK
code TEXT UNIQUE NOT NULL
name TEXT NOT NULL
rank INT UNIQUE NOT NULL
description TEXT
created_at TIMESTAMPTZ NOT NULL
```

Recommended initial hierarchy:

```text
PUBLIC
RESTRICTED
CONFIDENTIAL
SECRET
TOP_SECRET
TS_SCI
```

Higher rank means greater access.

Clearance alone must NOT imply every action. Combine:

```text
role permissions + clearance + resource policy
```

## 7.5 permissions

```text
permissions
-----------
id UUID PK
code TEXT UNIQUE NOT NULL
description TEXT
```

Examples:

```text
investigation:read
investigation:create
investigation:update
subject:read
subject:sensitive:read
graph:read
evidence:read
user:read
user:manage
user:delete
audit:read
model:download
chat:authorized
```

## 7.6 role_permissions

```text
role_permissions
----------------
role_id UUID FK -> roles.id
permission_id UUID FK -> permissions.id
PRIMARY KEY(role_id, permission_id)
```

---

# 8. Session / Refresh Token Schema

Do not store raw refresh tokens.

```text
auth_sessions
-------------
id UUID PK
user_id UUID FK -> users.id
refresh_token_hash TEXT UNIQUE NOT NULL
device_info TEXT NULL
ip_hash TEXT NULL
user_agent_hash TEXT NULL
expires_at TIMESTAMPTZ NOT NULL
revoked_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ NOT NULL
last_used_at TIMESTAMPTZ NULL
```

Access tokens should be short-lived.

Refresh tokens should be revocable.

---

# 9. Core Intelligence Entity Model

Prysm's operational graph revolves around connected entities.

The exact source entities must be aligned with the existing AI-engine data model. The backend should support at minimum:

```text
Person
Account
Transaction
Counterparty
Device
Identifier / contact point
```

Additional entity types may be introduced without redesigning the API.

## 9.1 subjects

Use a stable internal subject identifier.

```text
subjects
--------
id UUID PK
subject_type TEXT NOT NULL
external_ref TEXT NULL
display_label TEXT NOT NULL
status TEXT NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Do not use real-world names as primary keys.

## 9.2 subject_profiles

Sensitive profile attributes should be separated.

```text
subject_profiles
----------------
subject_id UUID PK FK -> subjects.id
full_name TEXT NULL
date_of_birth DATE NULL
country_code TEXT NULL
risk_category TEXT NULL
sensitive_attributes JSONB NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

The response serializer controls which fields each clearance sees.

For demo/student/public views, names must never be exposed unless explicitly permitted. Use hashed/pseudonymous labels.

---

# 10. Transaction Schema

Use the existing source dataset schema where available. If a normalized operational representation is required:

```text
transactions
------------
id UUID PK
source_transaction_id TEXT NULL
from_subject_id UUID NULL FK -> subjects.id
to_subject_id UUID NULL FK -> subjects.id
from_account_id UUID NULL FK -> subjects.id
to_account_id UUID NULL FK -> subjects.id
amount NUMERIC(24,8) NOT NULL
currency CHAR(3) NOT NULL
timestamp TIMESTAMPTZ NOT NULL
transaction_type TEXT NULL
country_from CHAR(2) NULL
country_to CHAR(2) NULL
channel TEXT NULL
device_subject_id UUID NULL FK -> subjects.id
source_system TEXT NULL
raw_metadata JSONB NULL
created_at TIMESTAMPTZ NOT NULL
```

If the current source schema already exists, create compatibility views/mappings instead of duplicating millions of rows unnecessarily.

Create indexes on:

```text
timestamp
from_subject_id
to_subject_id
currency
country_from
country_to
transaction_type
```

Consider composite indexes based on actual query plans.

---

# 11. Graph Schema

The goal is to make the operational graph explicit enough for:

1. investigation search;
2. subgraph retrieval;
3. RAG context;
4. GNN mapping;
5. evidence traversal;
6. graph visualization.

## 11.1 graph_nodes

```text
graph_nodes
-----------
id UUID PK
subject_id UUID NULL FK -> subjects.id
node_type TEXT NOT NULL
external_key TEXT NULL
label_hash TEXT NULL
features JSONB NULL
embedding VECTOR NULL
embedding_model_version TEXT NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

`embedding VECTOR` is used only when the deployment has pgvector enabled.

If vectors are large or versioned externally, store them in a dedicated feature/vector table.

## 11.2 graph_edges

```text
graph_edges
-----------
id UUID PK
source_node_id UUID FK -> graph_nodes.id
target_node_id UUID FK -> graph_nodes.id
edge_type TEXT NOT NULL
weight DOUBLE PRECISION NULL
first_seen_at TIMESTAMPTZ NULL
last_seen_at TIMESTAMPTZ NULL
valid_from TIMESTAMPTZ NULL
valid_to TIMESTAMPTZ NULL
source_reference TEXT NULL
properties JSONB NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Indexes:

```text
source_node_id
target_node_id
edge_type
(last_seen_at)
(source_node_id, edge_type)
(target_node_id, edge_type)
```

For graph traversal, do not rely only on a JSONB blob.

---

# 12. GNN Mapping Requirements

The backend does not train the GNN. It exposes the graph representation and stores versioned GNN artifacts/results.

The graph-to-GNN mapping must preserve:

```text
node_id
node_type
edge_id
edge_type
source_node_id
target_node_id
timestamp validity
feature snapshot/version
embedding version
model version
```

A GNN mapping should be reproducible.

## 12.1 gnn_graph_snapshots

```text
gnn_graph_snapshots
-------------------
id UUID PK
graph_version TEXT NOT NULL
cutoff_at TIMESTAMPTZ NOT NULL
node_count BIGINT NOT NULL
edge_count BIGINT NOT NULL
feature_schema_version TEXT NOT NULL
created_at TIMESTAMPTZ NOT NULL
metadata JSONB NULL
```

## 12.2 gnn_nodes

```text
gnn_nodes
---------
snapshot_id UUID FK -> gnn_graph_snapshots.id
graph_node_id UUID FK -> graph_nodes.id
gnn_index BIGINT NOT NULL
node_type TEXT NOT NULL
feature_version TEXT NOT NULL
PRIMARY KEY(snapshot_id, graph_node_id)
UNIQUE(snapshot_id, gnn_index)
```

This is important because GNN tensor indices are not necessarily the same as PostgreSQL identifiers.

## 12.3 gnn_edges

```text
gnn_edges
---------
snapshot_id UUID FK -> gnn_graph_snapshots.id
graph_edge_id UUID FK -> graph_edges.id
source_gnn_index BIGINT NOT NULL
target_gnn_index BIGINT NOT NULL
edge_type TEXT NOT NULL
PRIMARY KEY(snapshot_id, graph_edge_id)
```

## 12.4 gnn_embeddings

```text
gnn_embeddings
--------------
id UUID PK
snapshot_id UUID FK -> gnn_graph_snapshots.id
graph_node_id UUID FK -> graph_nodes.id
model_version TEXT NOT NULL
embedding JSONB NULL
embedding VECTOR NULL
generated_at TIMESTAMPTZ NOT NULL
metadata JSONB NULL
```

Do not overwrite embeddings across versions.

A model evaluation must be able to reproduce which embedding version was used.

---

# 13. Evidence Model

## 13.1 evidence_references

```text
evidence_references
-------------------
id UUID PK
source_type TEXT NOT NULL
source_id TEXT NOT NULL
source_table TEXT NULL
event_time TIMESTAMPTZ NULL
label TEXT NOT NULL
excerpt TEXT NULL
metadata JSONB NULL
created_at TIMESTAMPTZ NOT NULL
```

Avoid copying sensitive source material into every result.

Reference the actual source whenever possible.

---

# 14. Investigation Model

Investigation is the main backend domain.

## 14.1 investigations

```text
investigations
--------------
id UUID PK
created_by UUID FK -> users.id
subject_id UUID FK -> subjects.id
status investigation_status NOT NULL
title TEXT NULL
purpose TEXT NULL
cutoff_at TIMESTAMPTZ NULL
prediction_horizon_start TIMESTAMPTZ NULL
prediction_horizon_end TIMESTAMPTZ NULL
context_version TEXT NULL
ai_engine_version TEXT NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
closed_at TIMESTAMPTZ NULL
```

## 14.2 investigation_queries

```text
investigation_queries
---------------------
id UUID PK
investigation_id UUID FK -> investigations.id
user_id UUID FK -> users.id
query_text TEXT NOT NULL
normalized_query TEXT NULL
query_type TEXT NULL
created_at TIMESTAMPTZ NOT NULL
```

## 14.3 investigation_findings

```text
investigation_findings
----------------------
id UUID PK
investigation_id UUID FK -> investigations.id
finding_type TEXT NOT NULL
severity TEXT NULL
score DOUBLE PRECISION NULL
confidence DOUBLE PRECISION NULL
title TEXT NOT NULL
summary TEXT NULL
source_component TEXT NOT NULL
model_version TEXT NULL
created_at TIMESTAMPTZ NOT NULL
```

Source component examples:

```text
RULE
SUPERVISED_MODEL
ANOMALY_MODEL
GNN
FUSION
RAG
HUMAN
```

## 14.4 finding_evidence

```text
finding_evidence
----------------
finding_id UUID FK -> investigation_findings.id
evidence_id UUID FK -> evidence_references.id
relevance DOUBLE PRECISION NULL
PRIMARY KEY(finding_id, evidence_id)
```

---

# 15. Investigation Context

InvestigationContext is the most important integration object.

The backend creates it. The AI Engine consumes it.

Conceptually:

```ts
type InvestigationContext = {
  contextId: string;
  investigationId: string;
  subject: SubjectContext;
  cutoff: {
    observedUntil: string | null;
    predictionStart: string | null;
    predictionEnd: string | null;
  };
  entities: ContextEntity[];
  transactions: ContextTransaction[];
  graph: ContextGraph;
  behavioralSignals: ContextSignal[];
  velocitySignals: ContextSignal[];
  foreignIncomeSignals: ContextSignal[];
  anomalySignals: ContextSignal[];
  ruleSignals: ContextSignal[];
  evidence: EvidenceContext[];
  accessScope: AccessScope;
  modelContext: ModelContext;
  metadata: {
    contextVersion: string;
    dataSnapshotVersion: string | null;
    createdAt: string;
  };
};
```

The backend must not fabricate AI signals that only the AI Engine can compute.

It gathers source observations and bounded context.

---

# 16. Context-Building Algorithm

When a protected investigator searches a subject:

```text
1. Authenticate user.
2. Resolve user role and clearance.
3. Validate search target.
4. Find subject/entity.
5. Check subject-level/resource-level access.
6. Resolve investigation cutoff if one exists.
7. Fetch permitted profile fields.
8. Fetch transaction history permitted by policy.
9. Fetch graph neighbors within bounded depth.
10. Fetch relationship metadata.
11. Fetch evidence references.
12. Fetch compatible precomputed signals when available.
13. Attach snapshot/version metadata.
14. Apply cutoff filtering.
15. Apply field-level redaction.
16. Build InvestigationContext.
17. Send to AI Engine.
18. Validate AI Engine response.
19. Persist appropriate findings.
20. Return frontend-safe InvestigationResponse.
```

Do not let arbitrary frontend query parameters bypass the context builder.

---

# 17. Graph Search Requirements

Graph traversal must be bounded.

Default:

```text
maxDepth = 2
maxNodes = 500
maxEdges = 2000
```

These are configurable and can vary by clearance.

The backend should support:

- direct connections;
- second-degree relationships;
- transaction relationships;
- shared devices;
- shared identifiers;
- common counterparties;
- network clusters;
- temporal relationship filtering.

Avoid unbounded recursive queries from HTTP requests.

---

# 18. AI Engine Adapter

The backend owns an adapter, not AI logic.

Suggested interface:

```ts
interface AiEngineClient {
  health(): Promise<AiHealth>;

  analyzeInvestigation(
    context: InvestigationContext
  ): Promise<AiInvestigationResult>;

  explainFinding(
    request: AiExplanationRequest
  ): Promise<AiExplanationResult>;
}
```

The actual HTTP/gRPC implementation can change later.

## AI Engine request

Conceptually:

```json
{
  "request_id": "...",
  "context_version": "1.0",
  "engine_version": "...",
  "investigation_id": "...",
  "subject_id": "...",
  "cutoff": {
    "observed_until": "...",
    "prediction_start": "...",
    "prediction_end": "..."
  },
  "subject": {},
  "entities": [],
  "transactions": [],
  "graph": {},
  "signals": [],
  "evidence": []
}
```

## AI Engine response

Conceptually:

```json
{
  "engine_version": "...",
  "model_versions": {},
  "risk": {
    "score": 0.0,
    "label": "LOW",
    "confidence": 0.0
  },
  "findings": [],
  "rules": [],
  "anomalies": [],
  "graph_intelligence": {},
  "evidence": [],
  "limitations": [],
  "generated_at": "..."
}
```

The backend validates this response before exposing it.

---

# 19. RAG Adapter

The RAG service is external to the backend's implementation.

The future adapter should look conceptually like:

```ts
interface RagClient {
  publicChat(request: RagPublicChatRequest): Promise<RagResponse>;

  authorizedChat(
    request: RagAuthorizedChatRequest
  ): Promise<RagResponse>;

  health(): Promise<RagHealth>;
}
```

Do not build the RAG internals here.

The URL, authentication mechanism, request shape, and response shape are configuration/adapter concerns and will be filled when the RAG API is supplied.

---

# 20. Public Chat

Public chatbot flow:

```text
POST /api/v1/chat/public
      |
      +-- validate request
      +-- rate limit
      +-- create conversation interaction ID
      +-- call RAG public API
      +-- persist user question + RAG response + metadata
      +-- return sanitized response
```

The public chat MUST NOT receive private investigation data.

---

# 21. Authorized Chat

Authorized Prysm AI chat flow:

```text
POST /api/v1/chat/authorized
      |
      +-- authenticate
      +-- authorize chat:authorized
      +-- resolve user clearance
      +-- identify investigation/subject context
      +-- build bounded context
      +-- call RAG authorized API
      +-- persist interaction + access scope + sources
      +-- audit
      +-- return response
```

The user's intent can be sent to RAG, but protected data must be explicitly scoped.

Never allow a prompt such as:

> "Show me everything about all users"

to become an unrestricted database query.

---

# 22. RAG Interaction Log

One row should represent a meaningful request/response interaction.

## rag_interactions

```text
rag_interactions
----------------
id UUID PK
conversation_id UUID NOT NULL
user_id UUID NULL FK -> users.id
mode TEXT NOT NULL
question TEXT NOT NULL
response TEXT NULL
status TEXT NOT NULL
rag_model_version TEXT NULL
rag_version TEXT NULL
context_version TEXT NULL
investigation_id UUID NULL FK -> investigations.id
subject_id UUID NULL FK -> subjects.id
access_scope JSONB NULL
retrieved_sources JSONB NULL
request_metadata JSONB NULL
response_metadata JSONB NULL
latency_ms INT NULL
feedback_label TEXT NULL
feedback_note TEXT NULL
created_at TIMESTAMPTZ NOT NULL
```

Possible modes:

```text
PUBLIC
AUTHORIZED
```

Possible status:

```text
SUCCESS
PARTIAL
ERROR
DENIED
```

Do not store unnecessary secrets, tokens, passwords, or raw authorization headers.

For privacy and governance, establish an explicit retention policy.

---

# 23. Conversation Model

Optional conversation grouping:

```text
chat_conversations
------------------
id UUID PK
user_id UUID NULL
mode TEXT NOT NULL
title TEXT NULL
started_at TIMESTAMPTZ NOT NULL
last_activity_at TIMESTAMPTZ NOT NULL
metadata JSONB NULL
```

One conversation can have many `rag_interactions`.

For public anonymous sessions, use a server-issued anonymous conversation UUID, not a user identity.

---

# 24. Models Registry

The UI may show model information, but the backend only needs metadata and controlled access.

## models

```text
models
------
id UUID PK
name TEXT NOT NULL
slug TEXT UNIQUE NOT NULL
version TEXT NOT NULL
model_type TEXT NOT NULL
architecture TEXT NULL
status TEXT NOT NULL
metrics JSONB NULL
description TEXT NULL
limitations JSONB NULL
ethical_status TEXT NULL
artifact_path TEXT NULL
artifact_url TEXT NULL
checksum TEXT NULL
release_notes TEXT NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Example status:

```text
EXPERIMENTAL
VALIDATED
RELEASED
DEPRECATED
```

Do not store model binaries in PostgreSQL.

---

# 25. Model Downloads

Expose model metadata through:

```text
GET /api/v1/models
GET /api/v1/models/:id
```

For downloads:

```text
GET /api/v1/models/:id/download
```

The route must authorize access before generating/serving the download.

The backend does not need a complex model artifact management platform now.

The actual artifact can live on a configured filesystem/object store/download location.

---

# 26. Audit Logging

Audit is first-class.

## audit_events

```text
audit_events
------------
id UUID PK
event_type TEXT NOT NULL
actor_user_id UUID NULL FK -> users.id
target_type TEXT NULL
target_id TEXT NULL
action TEXT NOT NULL
result TEXT NOT NULL
clearance_code TEXT NULL
ip_hash TEXT NULL
user_agent_hash TEXT NULL
request_id TEXT NOT NULL
metadata JSONB NULL
created_at TIMESTAMPTZ NOT NULL
```

Record at minimum:

```text
AUTH_LOGIN_SUCCESS
AUTH_LOGIN_FAILURE
AUTH_LOGOUT
ACCOUNT_APPLICATION_SUBMITTED
ACCOUNT_APPLICATION_APPROVED
ACCOUNT_APPLICATION_REJECTED
USER_VIEWED
USER_UPDATED
USER_DISABLED
USER_DELETED
PERMISSION_CHANGED
CLEARANCE_CHANGED
INVESTIGATION_CREATED
INVESTIGATION_VIEWED
SUBJECT_SEARCHED
SENSITIVE_DATA_VIEWED
GRAPH_VIEWED
AI_ANALYSIS_REQUESTED
RAG_QUERY
MODEL_DOWNLOAD
DATA_EXPORT
ACCESS_DENIED
```

Do not put raw passwords, tokens, or unnecessary personal secrets into audit metadata.

Prefer append-only semantics.

---

# 27. API Conventions

Base prefix:

```text
/api/v1
```

Content type:

```text
application/json
```

Use UUID identifiers.

Use ISO-8601 timestamps.

Use cursor-based pagination for large datasets.

Example pagination:

```http
GET /api/v1/investigations?limit=50&cursor=...
```

Response:

```json
{
  "data": [],
  "pagination": {
    "nextCursor": "...",
    "hasMore": true
  }
}
```

---

# 28. Standard Error Contract

Every API error should look like:

```json
{
  "error": {
    "code": "INVESTIGATION_NOT_FOUND",
    "message": "Investigation was not found.",
    "requestId": "..."
  }
}
```

Do not leak stack traces in production.

Possible codes:

```text
VALIDATION_ERROR
AUTH_REQUIRED
INVALID_CREDENTIALS
SESSION_EXPIRED
FORBIDDEN
CLEARANCE_INSUFFICIENT
RESOURCE_NOT_FOUND
RATE_LIMITED
AI_ENGINE_UNAVAILABLE
RAG_UNAVAILABLE
AI_ENGINE_INVALID_RESPONSE
RAG_INVALID_RESPONSE
DATABASE_ERROR
INTERNAL_ERROR
```

---

# 29. API Endpoint Map

## Health

```text
GET /api/v1/health
GET /api/v1/health/ready
GET /api/v1/health/dependencies
```

`dependencies` must not expose secrets.

---

## Authentication

```text
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
GET  /api/v1/auth/me
POST /api/v1/auth/change-password
```

Optional later:

```text
POST /api/v1/auth/forgot-password
POST /api/v1/auth/reset-password
```

---

## Account Applications

```text
POST /api/v1/applications
GET  /api/v1/applications
GET  /api/v1/applications/:id
POST /api/v1/applications/:id/approve
POST /api/v1/applications/:id/reject
```

The last four are privileged.

---

## Current User

```text
GET  /api/v1/me
PATCH /api/v1/me/profile
PATCH /api/v1/me/preferences
GET  /api/v1/me/permissions
GET  /api/v1/me/clearance
GET  /api/v1/me/activity
```

---

## Users / Administration

```text
GET    /api/v1/users
GET    /api/v1/users/:id
PATCH  /api/v1/users/:id
POST   /api/v1/users/:id/disable
POST   /api/v1/users/:id/restore
DELETE /api/v1/users/:id
PATCH  /api/v1/users/:id/role
PATCH  /api/v1/users/:id/clearance
GET    /api/v1/users/:id/activity
```

`DELETE` should normally perform controlled soft deletion/deactivation rather than destroy audit history.

---

# 30. Search API

Search is the gateway to investigation.

```text
POST /api/v1/search
```

Request:

```json
{
  "query": "..."
  "types": ["PERSON", "ACCOUNT", "TRANSACTION"],
  "limit": 25
}
```

Results must contain only fields permitted to the requesting user.

The search service may use:

- PostgreSQL full-text search;
- trigram/fuzzy matching;
- indexed identifiers;
- exact ID lookup.

Do not perform unrestricted wildcard scans against large tables.

---

# 31. Subjects API

```text
GET /api/v1/subjects/:id
GET /api/v1/subjects/:id/profile
GET /api/v1/subjects/:id/transactions
GET /api/v1/subjects/:id/relationships
GET /api/v1/subjects/:id/evidence
GET /api/v1/subjects/:id/risk
```

The routes may later be consolidated behind investigation APIs, but these are useful primitive resources.

---

# 32. Investigation API

```text
POST /api/v1/investigations
GET  /api/v1/investigations
GET  /api/v1/investigations/:id
PATCH /api/v1/investigations/:id
POST /api/v1/investigations/:id/analyze
GET  /api/v1/investigations/:id/findings
GET  /api/v1/investigations/:id/evidence
GET  /api/v1/investigations/:id/graph
GET  /api/v1/investigations/:id/timeline
POST /api/v1/investigations/:id/queries
```

Typical creation:

```json
{
  "subjectId": "...",
  "title": "Subject Investigation",
  "purpose": "Review unusual transaction activity",
  "cutoffAt": "2026-08-01T00:00:00Z"
}
```

---

# 33. Intelligence API

```text
POST /api/v1/intelligence/analyze
POST /api/v1/intelligence/explain
GET  /api/v1/intelligence/model-state
```

Prefer investigation-scoped analysis:

```text
POST /api/v1/investigations/:id/analyze
```

instead of anonymous intelligence requests.

All analysis requests must be attributable to a user and investigation where possible.

---

# 34. Graph API

```text
GET /api/v1/graph/subjects/:id
GET /api/v1/graph/subjects/:id/neighbors
GET /api/v1/graph/subjects/:id/subgraph
GET /api/v1/graph/snapshots/:id
```

Request controls:

```text
depth
nodeLimit
edgeLimit
edgeTypes
observedUntil
```

Never allow user-controlled SQL fragments.

---

# 35. Evidence API

```text
GET /api/v1/evidence/:id
GET /api/v1/investigations/:id/evidence
```

Sensitive evidence requires clearance.

Evidence responses must preserve provenance.

---

# 36. Chat API

Public:

```text
POST /api/v1/chat/public
GET  /api/v1/chat/public/:conversationId
```

Authorized:

```text
POST /api/v1/chat/authorized
GET  /api/v1/chat/:conversationId
POST /api/v1/chat/:conversationId/feedback
```

The backend must distinguish public and authorized modes server-side.

Do not let the client simply claim:

```json
{ "mode": "authorized" }
```

and trust it.

---

# 37. RAG Audit/History API

Privileged:

```text
GET /api/v1/rag/interactions
GET /api/v1/rag/interactions/:id
```

Potential filters:

```text
userId
mode
status
modelVersion
dateFrom
dateTo
investigationId
```

These endpoints are for monitoring/evaluation, not for ordinary users.

---

# 38. Models API

```text
GET /api/v1/models
GET /api/v1/models/:id
GET /api/v1/models/:id/download
```

No model training endpoints are required.

No model upload UI is required in this phase.

---

# 39. Audit API

Admin/security only:

```text
GET /api/v1/audit/events
GET /api/v1/audit/events/:id
```

Strong filtering and pagination are required.

---

# 40. Student / Demo Data

The student pack and playground should NOT expose production subjects.

A safe backend can optionally expose:

```text
GET /api/v1/demo/graph
GET /api/v1/demo/subjects
```

Only against an isolated synthetic/demo dataset.

All display names must be pseudonymized.

No endpoint should use production personal data just because the caller is in student mode.

---

# 41. Access-Control Model

Authorization should evaluate:

```text
Is user authenticated?
        ↓
Is account active?
        ↓
Does role have required permission?
        ↓
Is clearance >= required level?
        ↓
Does resource policy permit this user?
        ↓
Return only fields allowed by the policy.
```

Example:

```text
REPORTER
- public information
- limited demo
- no sensitive subjects
- no unrestricted investigations
- no audit access

ANALYST
- investigation read
- bounded graph
- standard evidence
- limited sensitive fields

INVESTIGATOR
- investigation create/analyze
- broader graph
- more evidence
- authorized chat

SENIOR_INVESTIGATOR
- broader sensitive access
- investigation management
- advanced intelligence

ADMIN
- user/role/application management
- audit access according to policy

TS_SCI
- highest configured clearance
- still constrained by explicit permissions
```

Do not encode these as the only possible roles. Seed data may evolve.

---

# 42. Field-Level Security

A low-clearance response might contain:

```json
{
  "subjectId": "...",
  "displayLabel": "PERSON-8F3A",
  "risk": {
    "level": "HIGH"
  }
}
```

A higher-clearance response may additionally include permitted identity fields.

Do not rely on hiding fields in React.

Redaction occurs server-side.

---

# 43. Rate Limiting

At minimum:

```text
auth routes: strict
public chat: strict
search: moderate
investigation analysis: moderate
admin routes: moderate
health: permissive
```

AI/RAG calls should have concurrency protection.

---

# 44. Caching

Use caching selectively.

Good candidates:

- model metadata;
- immutable research/config metadata if ever exposed through API;
- static lookup/reference data;
- graph snapshot metadata.

Do NOT blindly cache:

- sensitive investigation data;
- clearance-specific data;
- rapidly changing user permissions.

A user's authorization must always be revalidated for protected resources.

---

# 45. Database Index Strategy

At minimum index:

```text
users.email
users.status
users.clearance_level_id
users.role_id

transactions.timestamp
transactions.from_subject_id
transactions.to_subject_id

graph_nodes.subject_id
graph_nodes.node_type

graph_edges.source_node_id
graph_edges.target_node_id
graph_edges.edge_type

investigations.created_by
investigations.subject_id
investigations.status

investigation_findings.investigation_id

audit_events.actor_user_id
audit_events.event_type
audit_events.created_at

rag_interactions.user_id
rag_interactions.conversation_id
rag_interactions.created_at
rag_interactions.investigation_id
```

Use `EXPLAIN ANALYZE` against realistic data before adding unnecessary indexes.

---

# 46. Search Optimization

For names/labels where supported, PostgreSQL may use:

```text
pg_trgm
```

For text:

```text
GIN
tsvector
```

For exact references:

```text
B-tree
```

The implementation must choose the actual index based on data volume and query plans.

---

# 47. API Request Validation

Every external request is validated.

Use Zod schemas for:

- body;
- query;
- path parameters;
- external service response contracts.

Never trust AI Engine or RAG responses simply because they came from internal services.

---

# 48. AI/RAG Failure Strategy

If AI Engine is unavailable:

```text
HTTP 503
code = AI_ENGINE_UNAVAILABLE
```

Do not return fabricated intelligence.

If RAG is unavailable:

```text
HTTP 503
code = RAG_UNAVAILABLE
```

The rest of the application can continue.

For an AI response with invalid schema:

```text
reject
log
audit
return controlled error
```

Do not silently coerce malformed model output into apparently valid findings.

---

# 49. Investigation Persistence Policy

The backend should distinguish:

### Source facts
Owned by PostgreSQL/source data.

### Derived AI results
Owned by an analysis run.

### Human actions
Owned by the investigation workflow.

A repeat analysis must not blindly overwrite historical analysis.

Store the analysis/model version.

Suggested future table:

```text
analysis_runs
-------------
id UUID PK
investigation_id UUID FK
requested_by UUID FK
ai_engine_version TEXT
model_versions JSONB
context_version TEXT
status TEXT
started_at TIMESTAMPTZ
completed_at TIMESTAMPTZ
result JSONB
error_code TEXT NULL
```

This makes model/version comparisons possible.

---

# 50. Analysis Runs

Recommended statuses:

```text
QUEUED
RUNNING
SUCCEEDED
PARTIAL
FAILED
```

If the AI Engine eventually becomes asynchronous, the frontend can use:

```text
POST /investigations/:id/analyze
GET /investigations/:id/analysis-runs/:runId
```

For now synchronous calls are acceptable if response time is controlled.

---

# 51. WebSocket / Streaming

Not mandatory for the first implementation.

The HTTP API should work independently.

When needed later, use WebSocket/SSE for:

- long AI analyses;
- streaming RAG responses;
- investigation progress;
- live job state.

The initial backend MUST NOT require WebSocket for basic functionality.

---

# 52. Data Ingestion

Do not create a public ingestion API by default.

The existing dataset/AI-engine pipeline should remain responsible for training/data preparation.

If backend ingestion is later required, make it a privileged internal endpoint or job system.

Never expose raw database import capability to ordinary users.

---

# 53. Data Retention

Define configurable retention policies for:

- audit events;
- chat interactions;
- investigation history;
- session records;
- temporary analysis context;
- error logs.

Do not delete historical audit records casually.

Privacy requirements must be considered before permanent retention.

---

# 54. Security Requirements

Required:

- HTTPS in deployment
- secure cookies if cookie auth is used
- password hashing with Argon2id
- short-lived access tokens
- refresh token rotation/revocation
- Helmet
- strict CORS
- request size limits
- parameterized DB queries
- schema validation
- rate limiting
- structured audit logging
- secret values only in environment/secret manager
- no secrets in logs
- no raw authorization headers in logs
- no stack traces in production responses

---

# 55. Request IDs

Every request receives a request ID.

Flow:

```text
frontend
  |
request-id
  |
Express
  |
DB / AI / RAG
  |
logs
```

Propagate the request ID to internal service calls where supported.

This makes a user investigation traceable across systems without leaking sensitive information.

---

# 56. Observability

Structured logs should contain:

```text
timestamp
level
requestId
route
method
status
durationMs
userId when safe
service
errorCode
```

Metrics should include:

```text
request count
error count
response latency
DB latency
AI Engine latency
RAG latency
AI failures
RAG failures
authorization denials
analysis success/failure
```

Do not put investigation contents into generic application logs.

---

# 57. OpenAPI Documentation

Generate/maintain an OpenAPI 3.1 document.

Every frontend-facing endpoint should define:

- request schema;
- response schema;
- auth requirements;
- error responses;
- pagination;
- examples;
- clearance/permission requirements where appropriate.

The frontend team should be able to use this as the contract without reading backend source code.

---

# 58. Recommended DTOs

Use explicit DTOs such as:

```text
UserSummaryDTO
UserDetailDTO
SearchResultDTO
SubjectSummaryDTO
SubjectDetailDTO
InvestigationSummaryDTO
InvestigationDetailDTO
InvestigationResponseDTO
FindingDTO
EvidenceDTO
GraphNodeDTO
GraphEdgeDTO
RiskDTO
AIAnalysisDTO
RagResponseDTO
ModelDTO
AuditEventDTO
```

Never serialize Prisma/database records directly to HTTP.

---

# 59. Investigation Response Contract

A frontend-friendly response can look like:

```json
{
  "investigation": {
    "id": "...",
    "status": "OPEN",
    "subjectId": "...",
    "cutoffAt": "..."
  },
  "subject": {
    "id": "...",
    "displayLabel": "PERSON-8F3A"
  },
  "risk": {
    "score": 0.0,
    "level": "HIGH",
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
  "graph": {
    "nodes": [],
    "edges": []
  },
  "evidence": [],
  "model": {
    "engineVersion": "...",
    "versions": {}
  },
  "limitations": []
}
```

The exact field list can evolve while keeping backward compatibility.

---

# 60. Search Response Contract

```json
{
  "data": [
    {
      "id": "...",
      "type": "PERSON",
      "displayLabel": "PERSON-8F3A",
      "matchType": "FUZZY",
      "relevance": 0.91,
      "permitted": true
    }
  ],
  "pagination": {
    "nextCursor": null,
    "hasMore": false
  }
}
```

Do not return sensitive attributes in search results.

Fetch detail after access checks.

---

# 61. Chat Response Contract

```json
{
  "conversationId": "...",
  "interactionId": "...",
  "mode": "AUTHORIZED",
  "answer": "...",
  "sources": [],
  "context": {
    "investigationId": "...",
    "subjectId": "..."
  },
  "metadata": {
    "ragVersion": "...",
    "modelVersion": "...",
    "createdAt": "..."
  }
}
```

The backend should not expose internal prompts.

---

# 62. Frontend Independence Requirement

The backend must make these frontend tasks simple:

```text
Dashboard
 -> GET dashboard/summary or investigation summary

Search
 -> POST /search

Investigation
 -> GET /investigations/:id
 -> GET /investigations/:id/graph
 -> GET /investigations/:id/findings

Chat
 -> POST /chat/public
 -> POST /chat/authorized

Users
 -> GET /users
 -> PATCH /users/:id
```

The frontend does not need to understand SQL or AI Engine internals.

---

# 63. Dashboard API

Although the dashboard is frontend UI, it needs a small dynamic endpoint.

Recommended:

```text
GET /api/v1/dashboard/summary
```

Response should contain only useful aggregate/authorized data, for example:

```json
{
  "activeInvestigations": 0,
  "highRiskSubjects": 0,
  "recentFindings": [],
  "recentActivity": [],
  "modelState": {}
}
```

Do not force the frontend to make dozens of calls for one dashboard.

This endpoint can later expand without coupling the dashboard to database structure.

---

# 64. Admin Dashboard

Recommended:

```text
GET /api/v1/admin/summary
```

Only for appropriate permissions.

Possible data:

```text
pending applications
active users
recent access denials
recent audit activity
service health
AI/RAG availability
```

---

# 65. Service Health

Health endpoint should report logical service state:

```json
{
  "status": "ok",
  "services": {
    "postgres": "ok",
    "aiEngine": "ok",
    "rag": "ok"
  }
}
```

Never expose internal service credentials or URLs to untrusted users.

---

# 66. Migration Strategy

1. Inspect current PostgreSQL schema.
2. Preserve compatible existing tables.
3. Add migrations incrementally.
4. Never drop production data during initial backend implementation.
5. Seed only:
   - roles;
   - clearance levels;
   - permissions;
   - role-permission mappings;
   - safe development/demo data.
6. Create indexes after schema/data volume is understood.
7. Run migrations in CI before tests that rely on database state.

---

# 67. Existing AI Engine Integration Rules

The backend must adapt to the existing AI Engine rather than redesigning it.

Before final wiring, identify:

```text
AI Engine entrypoint
request format
response format
health endpoint
configuration
model loading mechanism
current inference command/API
versioning
expected context
```

Do not copy AI-engine source into the Node backend.

Use a typed adapter.

---

# 68. GNN Integration Rules

The backend's responsibility is:

```text
PostgreSQL graph data
   ->
versioned graph snapshot
   ->
GNN mapping
   ->
AI Engine
```

For each analysis, record enough metadata to know:

```text
which graph snapshot
which cutoff
which feature schema
which GNN model version
which embedding version
```

A retrospective full-graph embedding must never be silently presented as a cutoff-safe predictive result.

This matches Prysm Phase 4's existing validation rule.

---

# 69. Synthetic Benchmark Separation

The backend should not label benchmark results as production fraud probabilities.

When benchmark evaluation is exposed anywhere, make its status explicit:

```text
synthetic benchmark
controlled evaluation
not calibrated real-world probability
```

Production investigations and scientific benchmark datasets should have distinct namespaces/flags/contexts where possible.

---

# 70. Ethical / Scientific Metadata

For AI outputs, preserve:

```text
model version
context version
data snapshot
cutoff
limitations
confidence
evidence
```

Do not turn uncertain outputs into authoritative statements.

The UI may later display language such as:

```text
"High-risk signal"
```

rather than:

```text
"Confirmed fraud"
```

unless confirmed by a separately defined process.

---

# 71. Data Export

If exports are supported later:

```text
POST /api/v1/investigations/:id/export
```

This must be:

- permission controlled;
- clearance controlled;
- audited;
- rate limited;
- preferably generated asynchronously for large exports.

No public data export endpoint is required in the first phase.

---

# 72. Delete Policy

For security-sensitive data:

Prefer:

```text
disable/deactivate
```

over:

```text
hard delete
```

Keep audit history.

Hard deletion should only happen under explicit policy and with cascading behavior carefully defined.

---

# 73. Testing Requirements

Minimum test layers:

## Unit tests
- authorization rules
- clearance comparison
- DTO serialization
- context building
- graph traversal limits
- request validation
- adapter response parsing

## Integration tests
- PostgreSQL repositories
- migrations
- search
- investigation creation
- finding persistence
- audit persistence

## API tests
- authentication
- access denial
- reporter restrictions
- investigator workflow
- admin workflow
- public chat isolation
- authorized chat context
- AI Engine unavailable
- RAG unavailable

## Security tests
- privilege escalation attempts
- IDOR/resource authorization
- malformed JWT
- session revocation
- query injection
- oversized payloads
- rate limiting

---

# 74. Critical Security Tests

Must test examples such as:

```text
low clearance requesting high clearance subject
reporter requesting investigator endpoint
user A opening user B's restricted investigation
anonymous caller requesting authorized chat
disabled account using a valid old token
changed clearance using an existing session
user manipulating subjectId in chat request
user attempting arbitrary graph depth
user requesting raw database fields
```

Every case should result in the appropriate denial/redaction.

---

# 75. Development Environment

`.env.example` should include conceptual values for:

```text
NODE_ENV
PORT
DATABASE_URL

JWT_ACCESS_SECRET
JWT_REFRESH_SECRET
ACCESS_TOKEN_TTL
REFRESH_TOKEN_TTL

AI_ENGINE_BASE_URL
AI_ENGINE_API_KEY

RAG_BASE_URL
RAG_API_KEY

CORS_ORIGIN

RATE_LIMIT_WINDOW_MS
RATE_LIMIT_MAX

MODEL_ARTIFACT_BASE_URL
```

Secrets must never be committed.

---

# 76. API Versioning

Use:

```text
/api/v1
```

When breaking contracts later:

```text
/api/v2
```

Do not silently break the frontend.

---

# 77. Recommended Build Order

Codex should implement in this order:

## Phase A — Foundation

- TypeScript
- Express
- environment validation
- PostgreSQL connection
- Prisma/schema/migrations
- global error handling
- request ID
- logging
- health checks

## Phase B — Security

- users
- roles
- clearances
- permissions
- password hashing
- login
- refresh tokens
- authorization middleware

## Phase C — Core Data

- subjects
- transactions/adapters to existing source schema
- graph nodes
- graph edges
- evidence references
- graph snapshots/GNN mappings

## Phase D — Investigation

- search
- investigations
- investigation context builder
- findings
- analysis runs
- AI Engine adapter

## Phase E — RAG

- RAG adapter placeholder
- public chat route
- authorized chat route
- RAG interaction logging
- feedback
- audit events

The RAG integration becomes concrete once the RAG API contract is supplied.

## Phase F — Administration

- applications
- user administration
- activity
- audit queries
- model metadata/download policy

## Phase G — Documentation/Test

- OpenAPI
- integration tests
- security tests
- seed data
- developer setup
- frontend integration examples

---

# 78. What Codex Must Not Do

Codex MUST NOT:

- create endpoints for every frontend page;
- build an extra RAG implementation;
- move AI Engine logic into JavaScript;
- retrain models during backend setup;
- make claims that the current 0.47 ROC-AUC proves production performance;
- use retrospective graph embeddings for cutoff-safe predictive claims;
- expose unrestricted PostgreSQL queries;
- allow frontend-supplied clearance to control access;
- return raw database records;
- expose password hashes;
- expose secrets in API responses;
- delete audit logs when users are deleted;
- build a giant monolithic route file.

---

# 79. Definition of Done

The backend is considered ready for frontend integration when:

### Database
- migrations run cleanly;
- required tables exist;
- indexes are validated;
- GNN graph mappings are reproducible;
- seed access controls exist.

### Security
- registration/application flow works;
- login works;
- session revocation works;
- clearance/permission checks work;
- field-level redaction works;
- unauthorized access is tested.

### Intelligence
- search resolves subjects accurately;
- investigation context is built consistently;
- graph traversal is bounded;
- evidence references are retained;
- AI Engine adapter successfully calls current engine;
- analysis results are versioned.

### RAG
- adapter contract is isolated;
- public chat is separated from authorized chat;
- RAG interaction is recorded;
- access scope/context is recorded;
- failures are handled safely.

### API
- `/api/v1` endpoints are documented;
- OpenAPI is generated/maintained;
- error schema is consistent;
- pagination is consistent;
- frontend DTOs are stable.

### Quality
- automated tests pass;
- no critical security issue remains;
- logs are structured;
- request IDs are traceable;
- environment configuration is documented.

---

# 80. Final Architecture Contract

The final request path for a protected investigation is:

```text
React / Next.js
      |
      | HTTPS
      v
Node + Express
      |
      +--> Authentication
      |
      +--> Authorization
      |       |
      |       +--> role
      |       +--> clearance
      |       +--> resource policy
      |
      +--> PostgreSQL
      |       |
      |       +--> subject
      |       +--> transactions
      |       +--> graph
      |       +--> evidence
      |
      +--> InvestigationContext Builder
      |
      +--> AI Engine Adapter
      |       |
      |       +--> rules
      |       +--> anomaly
      |       +--> supervised
      |       +--> GNN
      |       +--> evidence-backed fusion
      |
      +--> RAG Adapter
      |       |
      |       +--> explanation / retrieval
      |
      +--> Audit
      |
      v
Frontend-safe InvestigationResponse
```

For authorized chat:

```text
User
 |
 v
Express
 |
 +--> authenticate
 |
 +--> authorize
 |
 +--> build bounded context
 |
 +--> RAG API
 |
 +--> record interaction
 |
 +--> audit
 |
 v
answer
```

The backend is therefore the **trusted orchestration boundary**, not the intelligence engine itself.

---

# 81. Immediate Implementation Instruction for Codex

Implement this specification as the authoritative backend contract.

Before altering existing tables or importing duplicated data:

1. inspect the existing project and PostgreSQL/AI Engine interfaces;
2. map compatible existing entities to the proposed schema;
3. preserve existing working AI-engine interfaces;
4. create migrations instead of destructive schema replacement;
5. implement the API contract in dependency order;
6. add tests after each domain;
7. keep AI Engine and RAG integration behind adapters;
8. document every endpoint in OpenAPI;
9. produce a final integration report listing:
   - implemented endpoints;
   - created/modified tables;
   - AI Engine integration status;
   - RAG adapter status;
   - GNN mapping status;
   - tests;
   - known limitations;
   - environment variables;
   - commands to run backend;
   - commands to run migrations;
   - commands to run tests.

Do not declare the backend complete merely because Express starts. It is complete only when the database, authorization, investigation context, AI adapter, RAG adapter boundary, auditability, API contracts, and tests are all operational.
