# Prysm RAG Integration

## Folder structure

The service is intentionally small and replacable. The root folder holds the FastAPI app, environment file, and tests, while the `rag` area contains the knowledge base and future retrieval logic. The `llm`/client responsibilities are isolated so Gemini can be swapped later without rewriting the rest of the app. The `tests` folder validates the public and authorized behaviors required for a clean integration.

## API

### GET /health
- Purpose: health check for the RAG service.
- Request: no body.
- Response: `status`, `service`, `llm`, and `knowledgeBase` fields.
- Authentication: none.
- Example: `GET /health`
- Errors: returns a simple JSON error only if the service is unavailable.

### GET /ask
- Purpose: answer a public or trusted investigator question with knowledge retrieval and optional backend context.
- Request: `?message=...&authenticated=true|false`
- Response: `answer`, `mode`, `sources`, `conversationId`, and `requestId`.
- Authentication: public mode does not require auth; investigator mode expects trusted backend-supplied context.
- Example: `GET /ask?message=What%20is%20Prysm%20AI`
- Errors: `400` for empty messages, `401` for invalid investigator context.

### POST /ingest
- Purpose: add a new knowledge item to the local vector-like knowledge store.
- Request: JSON with `title`, `content`, `source`, `category`, `version`, and optional `metadata`.
- Response: `success`, `documentId`, and `chunks`.
- Authentication: none for local ingestion; protect this in the Node backend if it is exposed externally.
- Example: `POST /ingest` with a document payload.
- Errors: invalid document payloads return validation errors.

### WS /ws/chat
- Purpose: real-time chat using the same ask pipeline.
- Request: JSON message with `message` and optional `authenticated`, `context`, `userId`.
- Response: sequence of `token` and `done` events.
- Authentication: same rule as `/ask`; only trusted backend context is accepted.
- Example: WebSocket connection to `/ws/chat` with a JSON message.
- Errors: invalid message payloads trigger structured error events.

## Architecture

Public users hit the knowledge RAG flow: the request is classified, relevant documents are retrieved from the local knowledge base, and the answer is explained by Gemini. Authorized investigators are routed through the backend-first trust model: the backend builds a bounded context from the authenticated investigation, passes it to the RAG service, and the service combines that evidence with local knowledge before generating a careful explanation.

## Backend integration

The Node backend is the trust boundary. It authenticates the user, checks clearance and access, builds a minimal investigation context, and sends it to the RAG service as a backend-supplied context object. The RAG service never decides authorization itself. A typical request passes `authenticated: true`, `userId`, `subjectId`, `investigationId`, and the trusted context payload.

## Environment

Required variables:

- `GOOGLE_API_KEYS` — comma-separated list of Gemini API keys
- `GEMINI_MODELS` — optional comma-separated model list; defaults to `GEMINI_MODEL`
- `GEMINI_MODEL` — default model, such as `gemini-1.5-flash`
- `GEMINI_API_BASE_URL` — default Google Gemini endpoint
- `RAG_HOST` and `RAG_PORT`
- `RAG_API_KEY` — optional service-level secret
- `DATABASE_URL` — optional if the RAG service is kept local-only

## Startup

Start the service with:

```bash
cd chatbot
python -m uvicorn main:app --host 127.0.0.1 --port 8200 --reload
```

## Frontend integration

```javascript
const res = await fetch('http://127.0.0.1:8200/ask?message=What%20is%20Prysm%20AI');
const data = await res.json();
console.log(data.answer);
```

```javascript
const res = await fetch('http://127.0.0.1:8200/ingest', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    title: 'Rapid Outflow',
    content: 'Rapid outflow is a short-duration pattern of unusually fast movement of funds away from a source account.',
    source: 'methodology',
    category: 'concepts',
    version: '1.0'
  })
});
const result = await res.json();
console.log(result.documentId);
```

```javascript
const ws = new WebSocket('ws://127.0.0.1:8200/ws/chat');
ws.onopen = () => ws.send(JSON.stringify({ message: 'What is rapid outflow?' }));
ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  if (msg.type === 'token') console.log(msg.text);
  if (msg.type === 'done') console.log('done', msg.sources);
};
```
