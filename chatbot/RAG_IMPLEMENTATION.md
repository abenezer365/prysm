# PRYSM AI — Simple RAG Chatbot Service

## Goal

Build a **small, fast, easy-to-integrate RAG service** inside the existing RAG project.

The service has exactly **3 main API capabilities**:

```text
GET  /health
GET  /ask
POST /ingest
```

Also support **WebSocket live chat** using the same `/ask` logic.

Do not build a heavy architecture.

The existing Prysm architecture must remain:

```text
PostgreSQL → exact facts
AI Engine → intelligence/signals
Graph/GNN → relationships
RAG → knowledge retrieval
LLM → explanation
Backend → controlled middle layer
Frontend → presentation
```

The RAG must never calculate fraud risk or invent evidence.

The attached canonical architecture defines this separation and should remain the conceptual source of truth. fileciteturn0file0L21-L47

---

# 1. Two Chat Modes

## Mode A — Public user

Example:

```text
"What is Prysm AI?"
"Who built Prysm?"
"What is rapid outflow?"
```

The request is treated as a **knowledge question**.

Use only:

```text
ingested knowledge base
+
retrieved documents
+
LLM
```

Do NOT expose PostgreSQL financial/intelligence data.

The canonical architecture defines platform, financial-intelligence, methodology, investigator-guidance, and limitation knowledge as RAG knowledge domains. fileciteturn0file0L261-L337

---

## Mode B — Authorized investigator

The frontend sends the user's authenticated state/context.

Example:

```json
{
  "authenticated": true,
  "userId": "...",
  "message": "Why was this company flagged?",
  "subjectId": "...",
  "investigationId": "..."
}
```

The RAG service must NOT trust the frontend's authorization claim by itself.

The Node backend remains responsible for authentication, authorization, clearance, and creation of the permitted investigation context.

The final RAG request should therefore receive trusted context from the backend.

For investigator questions:

```text
Node Backend
    ↓
authorized InvestigationContext
    ↓
RAG
    ├── Knowledge retrieval
    ├── structured intelligence context
    └── graph/GNN information supplied by backend
    ↓
LLM
    ↓
fact/safety validation
    ↓
answer
```

Use PostgreSQL/graph information only through the authorized backend context.

Do not let RAG directly query arbitrary protected database records.

The canonical architecture explicitly separates structured intelligence from RAG and states that exact financial facts belong to PostgreSQL while RAG retrieves knowledge. fileciteturn0file0L121-L195

---

# 2. Query Routing

Keep routing lightweight.

Implement a simple classifier/router before retrieval.

At minimum distinguish:

```text
KNOWLEDGE
INVESTIGATION
```

Optionally:

```text
SIMILARITY
```

if the existing backend already exposes transaction similarity.

Examples:

```text
"What is structuring?"
→ KNOWLEDGE

"What is Prysm?"
→ KNOWLEDGE

"Tell me about Company C04166"
→ INVESTIGATION

"Why was C04166 flagged?"
→ INVESTIGATION + KNOWLEDGE
```

This follows the existing Prysm routing principle: definitions/how questions use Knowledge RAG, while named entities and investigation questions use structured intelligence. fileciteturn0file0L215-L255

Do not build a large ML classifier for this.

Use deterministic rules first and only use the LLM for ambiguous cases if necessary.

---

# 3. Knowledge Base

Use a simple local structure:

```text
rag/
├── knowledge_base/
│   ├── platform/
│   ├── concepts/
│   ├── algorithms/
│   ├── rules/
│   ├── features/
│   ├── limitations/
│   └── disclaimers/
├── ingestion/
├── retrieval/
├── api/
├── llm/
├── prompts/
└── tests/
```

Keep documents small and focused.

The canonical architecture recommends small atomic documents, roughly 200–500 words where practical, with metadata/version/source information. fileciteturn0file0L339-L421

Do not ingest the entire raw financial dataset as documents.

---

# 4. Ingestion

Implement:

```http
POST /ingest
```

Accept a document/article/data payload.

Support simple formats first:

```text
JSON
plain text
Markdown
```

If file upload is already supported by the project, support files through the same endpoint.

The ingestion pipeline should:

```text
input
→ validate
→ extract text
→ chunk
→ embed
→ store
→ metadata
```

Store:

```text
document ID
title
source
category
version
createdAt
content/chunks
embedding
metadata
```

On a future question, newly ingested knowledge must be retrievable.

Do not train/fine-tune the LLM after every upload.

This is RAG ingestion, not model training.

---

# 5. Vector Storage

Use the lightest reliable option.

Preferred:

```text
PostgreSQL + pgvector
```

only if it is already available and convenient.

Otherwise use a lightweight local vector store.

Do not introduce a separate heavy database unless required.

Exact financial facts remain in the main Prysm PostgreSQL system; document vectors are for semantic retrieval.

The canonical design explicitly separates semantic knowledge retrieval from exact structured financial facts. fileciteturn0file0L491-L515

---

# 6. LLM

Use Google's Gemini API as the generation brain rather than running a large local LLM.

Keep the model configurable through:

```env
GOOGLE_API_KEY=
GEMINI_MODEL=
```

Use a fast/lightweight Gemini model appropriate for low-cost chatbot generation.

Do not hard-code a model name if the current Google API offers a better supported lightweight model.

The LLM's job is:

```text
retrieved knowledge
+
authorized structured context
+
instructions
→
human-readable explanation
```

The LLM must NOT:

```text
calculate fraud risk
invent evidence
make legal determinations
override backend authorization
```

---

# 7. Three Main APIs

## A. Health

```http
GET /health
```

Return:

```json
{
  "status": "ok",
  "service": "prysm-rag",
  "llm": "ok",
  "knowledgeBase": "ok"
}
```

Keep this cheap.

---

## B. Ask

```http
GET /ask
```

Required query:

```text
?message=What%20is%20Prysm%20AI
```

For public mode:

```text
GET /ask?message=What%20is%20Prysm%20AI&authenticated=false
```

For authorized use, prefer the backend to call the RAG service with trusted server-side context rather than trusting browser-supplied authorization.

A conceptual internal request can contain:

```json
{
  "message": "Why was this company flagged?",
  "authenticated": true,
  "userId": "...",
  "subjectId": "...",
  "investigationId": "...",
  "context": {}
}
```

Response:

```json
{
  "answer": "...",
  "mode": "public",
  "sources": [],
  "conversationId": "...",
  "requestId": "..."
}
```

or:

```json
{
  "answer": "...",
  "mode": "investigator",
  "sources": [],
  "evidence": [],
  "conversationId": "...",
  "requestId": "..."
}
```

Keep responses small and frontend-friendly.

---

## C. Ingest

```http
POST /ingest
```

Example:

```json
{
  "title": "Rapid Outflow",
  "content": "Rapid outflow is ...",
  "source": "Prysm methodology",
  "category": "rules",
  "version": "1.0"
}
```

Return:

```json
{
  "success": true,
  "documentId": "...",
  "chunks": 4
}
```

---

# 8. WebSocket Chat

Add:

```text
/ws/chat
```

This is not a fourth knowledge system.

It is simply a realtime transport for the same `/ask` pipeline.

Flow:

```text
WebSocket message
→ route/classify
→ retrieve
→ build context
→ Gemini
→ stream response
→ send tokens/chunks
→ close message
```

Example frontend message:

```json
{
  "message": "What is rapid outflow?",
  "conversationId": "..."
}
```

Stream events such as:

```json
{
  "type": "token",
  "text": "Rapid"
}
```

then:

```json
{
  "type": "done",
  "conversationId": "...",
  "sources": []
}
```

If streaming is not supported by the selected Gemini API path, send incremental message chunks rather than pretending token streaming exists.

Keep the WebSocket implementation lightweight.

---

# 9. Conversation Records

Record chatbot interactions.

Each interaction should be traceable with:

```text
conversationId
requestId
mode
userId when authorized
question
answer
retrieved sources
metadata
timestamp
```

Do not store unnecessary sensitive database information in the conversation record.

For public users, user identity may be null/anonymous.

For authorized users, use the authenticated user ID supplied by the trusted backend.

---

# 10. Fact/Safety Layer

Before returning an investigator-oriented answer, enforce simple validation.

The canonical Prysm architecture requires factual claims to remain traceable and says unsupported claims should be removed, downgraded, regenerated, or replaced by a deterministic response. fileciteturn0file0L707-L745

At minimum:

```text
answer
→ check source/context support
→ check forbidden claims
→ add investigation disclaimer when required
→ return
```

Never allow the LLM to state:

```text
"This person is a money launderer."
"This is confirmed fraud."
"This constitutes a crime."
```

Prefer:

```text
"The system detected..."
"The analysis indicates..."
"The rule triggered because..."
"The available evidence shows..."
```

The investigator remains the decision maker. fileciteturn0file0L801-L867

---

# 11. Public vs Investigator Boundary

Public:

```text
User
 ↓
/ask
 ↓
Knowledge Base
 ↓
Gemini
 ↓
Answer
```

Authorized:

```text
Frontend
 ↓
Node Backend
 ↓
authentication + clearance
 ↓
InvestigationContext
 ↓
RAG
 ├── Knowledge retrieval
 └── authorized structured context
 ↓
Gemini
 ↓
validation
 ↓
Backend
 ↓
Frontend
```

Do not expose PostgreSQL credentials to RAG.

Do not allow public requests to access investigator data.

Do not let RAG determine clearance.

---

# 12. Performance

This service is intended to run on a normal PC/server.

Keep it lightweight:

- async FastAPI;
- small document chunks;
- cached embeddings where possible;
- limited retrieval count;
- short prompts;
- bounded context;
- request timeout;
- connection reuse;
- no unnecessary background workers;
- no local large LLM.

Use a small retrieval count such as top 3–5 documents initially.

Do not retrieve the entire knowledge base.

---

# 13. Error Handling

Use simple JSON errors:

```json
{
  "error": {
    "code": "LLM_UNAVAILABLE",
    "message": "The language model is temporarily unavailable.",
    "requestId": "..."
  }
}
```

Handle:

```text
invalid question
LLM unavailable
LLM timeout
empty retrieval
invalid document
embedding failure
database/vector failure
unauthorized investigator context
```

Never expose API keys or stack traces.

---

# 14. Environment

Create a `.env` for the RAG service.

Example:

```env
GOOGLE_API_KEY=
GEMINI_MODEL=
RAG_HOST=127.0.0.1
RAG_PORT=8200
RAG_API_KEY=
DATABASE_URL=
```

Keep secrets out of Git.

Use `.env.example` as the safe template.

---

# 15. Integration with Prysm Backend

The Node backend is the trusted middle layer.

Future connection:

```text
Frontend
 ↓
Node Backend
 ↓
RAG API
```

For public chat:

```text
Backend → RAG /ask
```

For authorized chat:

```text
Backend
 ↓
authenticate user
 ↓
build authorized context
 ↓
RAG /ask
 ↓
answer
```

The RAG service should not independently decide whether a user is authorized.

---

# 16. AI Engine Relationship

Do not merge the RAG and AI Engine.

For questions such as:

```text
"Why was C04166 flagged?"
```

the backend should provide AI Engine/InvestigationResult information to the RAG explanation layer.

The RAG can additionally retrieve:

```text
rapid outflow definition
rule methodology
GNN explanation
confidence methodology
limitations
```

Then Gemini explains the verified context.

The canonical architecture explicitly defines this distinction: RAG explains what a signal means, while AI Engine evidence explains what happened to the entity. fileciteturn0file0L1027-L1097

---

# 17. Keep It Replaceable

Do not couple the entire RAG project directly to Gemini.

Create one small LLM client:

```text
llm/
└── gemini_client
```

Then the rest of RAG calls:

```text
generate()
```

or:

```text
stream()
```

This allows the model provider to be replaced later without rewriting retrieval.

---

# 18. Tests

Test only what matters:

```text
GET /health
GET /ask public
POST /ingest
GET /ask after ingestion
authorized ask
unauthorized data access
WebSocket chat
LLM failure
empty retrieval
```

Most important test:

```text
POST /ingest
   ↓
GET /ask
   ↓
answer contains information from newly ingested document
```

---

# 19. Final Documentation

Create exactly one documentation file:

```text
RAG_INTEGRATION.md
```

It must contain:

## Folder structure

Explain each important folder in one short paragraph.

## API

Document:

```text
GET /health
GET /ask
POST /ingest
WS /ws/chat
```

For every endpoint show:

- purpose;
- request;
- response;
- authentication;
- example;
- error behavior.

## Architecture

Explain:

```text
Public user
→ knowledge RAG
→ Gemini

Authorized investigator
→ Node backend
→ authorized InvestigationContext
→ RAG + structured intelligence
→ Gemini
```

## Backend integration

Explain exactly how Node/Express should call the RAG API.

## Environment

List required `.env` variables.

## Startup

Give the exact command to start the RAG service.

## Frontend integration

Give a minimal JavaScript example for:

```text
GET /ask
POST /ingest
WebSocket /ws/chat
```

Keep this document practical and short.

---

# 20. Completion Criteria

Do not declare completion until all of these work:

```text
[ ] FastAPI starts
[ ] GET /health works
[ ] POST /ingest works
[ ] ingested knowledge is retrievable
[ ] GET /ask works
[ ] public questions cannot access private intelligence
[ ] authorized backend context can be explained
[ ] GNN/AI Engine context can be explained when supplied by backend
[ ] WebSocket chat works
[ ] conversations are recorded
[ ] Gemini generation works
[ ] errors are controlled
[ ] RAG_INTEGRATION.md exists
```

Final target:

```text
PUBLIC

Frontend
 ↓
Node Backend
 ↓
RAG
 ↓
Knowledge Base
 ↓
Gemini
 ↓
Answer


AUTHORIZED

Frontend
 ↓
Node Backend
 ↓
Auth + Clearance
 ↓
InvestigationContext
 ↓
RAG
 ├── Knowledge
 └── AI/GNN structured context
 ↓
Gemini
 ↓
Validation
 ↓
Node Backend
 ↓
Frontend
```

Keep the entire implementation small, fast, understandable, and replaceable.

Do not rebuild the AI Engine.

Do not turn RAG into a risk engine.

Do not expose PostgreSQL directly to the browser.

Do not make the public chatbot capable of accessing investigator data.
