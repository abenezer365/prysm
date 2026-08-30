# Chatbot Integration and Diagnosis

## Public lifecycle

`ChatWidget` calls `api.publicChat`, which sends `POST {VITE_API_BASE_URL}/chat/public` with only `question` and an optional backend-issued `conversationId`. It does not send authentication, clearance, context, or access scope. The client displays answer, sources, request ID, busy state, diagnostic outage text, and retry.

The backend validates the payload, calls `RagAdapter.askPublic`, persists the interaction, and returns `{conversationId,requestId,answer,sources,mode}`. A retrieval outage becomes `503 RAG_UNAVAILABLE`.

## Reported failure diagnosis and repair

The reported request `93965fe9-9e7b-46ea-9974-b45200586270` could not be found in committed logs. Direct local checks initially found both `127.0.0.1:4000` and `127.0.0.1:8200` offline, with blank `RAG_API_KEY` values in both service environments. `server/scripts/start-local.ps1` intentionally refused that configuration. This was the root operational blocker, not a frontend endpoint or payload mismatch.

`server/scripts/configure-local-rag-key.ps1` now safely creates a cryptographically random internal key and writes the same value to the two ignored local environment files without printing it. The coordinated startup then brought PostgreSQL, AI Engine, RAG, and backend to ready state.

Live verification returned HTTP 200 through the backend public endpoint, four grounded sources, a request ID, and a backend-issued conversation ID. A second request preserved that conversation ID. A browser-origin test returned `Access-Control-Allow-Origin: http://localhost:5173`. Never place the internal key in `client/.env`.

The first repaired request used the evidence-grounded fallback because the environment still pinned the retired `gemini-1.5-flash` model, producing `HTTP_404`. The RAG service now uses `gemini-3.5-flash`, its current fallback list excludes shut-down 1.5/2.0 models, and legacy sampling parameters were removed from the request. After restart, live health reports `llm: ok` and `llmLastFailure: null`. The chatbot test suite passes all eight tests.

Authorized HTTP chat uses `/chat/authorized` with token, question, investigation ID, and optional conversation ID. WebSocket clients connect to the backend socket, wait for `ready`, authenticate, wait for `authenticated`, then send the investigation-bound question. The authorized UI transport remains a documented next task.
