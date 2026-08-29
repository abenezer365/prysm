# Prysm RAG Integration

The RAG service is an independently runnable FastAPI knowledge-retrieval and explanation service. It does not authorize users, query arbitrary protected PostgreSQL data, calculate risk, or invent evidence. Express is the browser-facing trust boundary; see `../ARCHITECTURE.md` and `../server/BACKEND_API.md`.

## Internal API

- `GET /health`: public process, knowledge-base, and real Gemini provider status (`not_configured`, `configured_not_verified`, `degraded`, or `ok`).
- `GET /ask?message=...`: public knowledge-only retrieval. It cannot accept authenticated context.
- `POST /ask`: authorized explanation using backend-supplied identity/resource fields and trusted context. Requires `Authorization: Bearer <RAG_API_KEY>` and fails closed if the key is absent.
- `POST /ingest`: knowledge document ingestion, not model training. Requires the same internal bearer key. The frontend-facing backend additionally requires `rag:ingest` and clearance rank 4.
- `WS /ws/chat?api_key=<RAG_API_KEY>`: protected realtime use of the same pipeline. Browser clients use the backend WebSocket, never this socket directly.

Answers contain `answer`, `mode`, versioned `sources`, `conversationId`, and `requestId`; authorized answers may also return curated finding/evidence summaries supplied by the backend.

## Request flows

Public requests are Browser → Express `/api/v1/chat/public` → RAG public retrieval → Gemini or evidence-grounded fallback → Express persistence → Browser. No investigation, database, AI, GNN, or protected evidence context is attached.

Authorized requests are Investigator → Express live session/RBAC/clearance/resource check → server-built `prysm-authorized-rag-context-v1` → protected RAG HTTP/WebSocket → Gemini or fallback → Express persistence/audit → Investigator. The RAG service trusts the internal credential and supplied context for explanation only; authorization remains an Express responsibility.

## Environment

- `GOOGLE_API_KEYS`: configured Gemini keys, comma-separated.
- `GEMINI_MODELS` or `GEMINI_MODEL`: configured model rotation/default.
- `GEMINI_API_BASE_URL`: Gemini REST model endpoint.
- `RAG_HOST`, `RAG_PORT`: local bind configuration.
- `RAG_API_KEY`: required internal secret; must match `server/.env` and stay out of Git.
- `MAX_RETRIEVAL_DOCS`, `REQUEST_TIMEOUT_SECONDS`, `LOG_LEVEL`: retrieval/runtime controls where consumed.
- `DATABASE_URL`: present in the example but the current file-backed RAG implementation does not query PostgreSQL directly.

## Startup

```powershell
cd chatbot
python -m uvicorn main:app --host 127.0.0.1 --port 8200
```

For the complete local system, use `npm run dev:stack` from `server/`; it verifies matching non-empty RAG keys and starts services in dependency order with readiness polling.
