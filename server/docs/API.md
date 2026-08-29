# Prysm Frontend API Contract

Base URL: `http://localhost:4000/api/v1`. JSON is used for requests and responses. Protected endpoints require `Authorization: Bearer <accessToken>`. Never derive permissions from the UI; use `/auth/me`, `/me/permissions`, and `/me/clearance`.

## Errors and tracing

Every response includes `x-request-id`. Errors use:

```json
{"error":{"code":"PERMISSION_DENIED","message":"Permission denied","details":{},"requestId":"uuid"}}
```

Handle `400` validation, `401` authentication/session expiry, `403` permission/clearance/resource denial, `404`, `409`, `413`, `429`, `502`, and `503`. Never infer that a `403` resource exists.

## Actual endpoints

| Method | Route | Access | Purpose |
|---|---|---|---|
| GET | `/health` | Public | Process liveness. |
| GET | `/health/ready` | Public | PostgreSQL readiness; `503` if unavailable. |
| GET | `/health/dependencies` | `health:dependencies:read` | PostgreSQL, AI Engine, and RAG state. |
| POST | `/applications` | Public | Submit an account application. |
| POST | `/auth/login` | Public | Obtain access and refresh tokens. |
| POST | `/auth/logout` | Authenticated | Revoke the current session. |
| GET | `/auth/me` | Authenticated | Safe current-user DTO. |
| GET | `/me/permissions` | Authenticated | Current live permission codes. |
| GET | `/me/clearance` | Authenticated | Current clearance rank. |
| POST | `/search` | `subject:read` | Clearance-filtered subject search. |
| GET | `/subjects/:id` | `subject:read` + subject clearance | Safe subject summary. |
| GET | `/subjects/:id/profile` | `subject:sensitive:read`, rank ≥ 3 | Sensitive profile. |
| POST | `/investigations` | `investigation:create`, rank ≥ 2 | Create a cutoff-aware investigation. |
| GET | `/investigations` | `investigation:read` | Authorized investigation list. |
| GET | `/investigations/:id` | `investigation:read` + ownership/share + clearance | Investigation, findings, evidence links, runs, scientific status. |
| POST | `/investigations/:id/analyze` | `investigation:analyze`, rank ≥ 2 + resource policy | Run real AI analysis and persist it. |
| GET | `/investigations/:id/analysis-runs/:runId` | `investigation:read` + resource policy | Retrieve one immutable analysis run. |
| GET | `/graph/subjects/:id/subgraph` | `graph:read`, rank ≥ 2 | Bounded cutoff-valid graph. |
| GET | `/evidence/:id` | `evidence:read`, rank ≥ 2 | Source/evidence reference. |
| GET | `/models` | `model:read` | Safe model/version/scientific metadata. |
| GET | `/audit/events` | `audit:read`, rank ≥ 4 | Latest audit events. |
| POST | `/chat/public` | Public | Knowledge-only RAG; never receives database or investigation context. |
| POST | `/chat/authorized` | `chat:authorized`, rank ≥ 2 + investigation resource policy | RAG explanation using server-built, cutoff-aware context. |
| POST | `/rag/ingest` | `rag:ingest`, rank ≥ 4 | Controlled knowledge-base ingestion. |
| WS | `/ws/chat` | `chat:authorized`, rank ≥ 2 + investigation resource policy | Backend-authenticated authorized chat relay. |

Endpoints not listed here do not exist. Refresh, dashboards, admin mutation, findings-only, timeline, feedback, export, and model download endpoints are planned but must not be called by the frontend yet.

## Authentication

Login:

```http
POST /api/v1/auth/login
Content-Type: application/json

{"email":"analyst@example.com","password":"...","deviceInfo":"Chrome on Windows"}
```

```json
{"accessToken":"...","refreshToken":"session-id.random-secret","tokenType":"Bearer","expiresIn":900}
```

Keep the access token in memory where possible. Do not log either token. A refresh endpoint is not implemented yet; on access-token expiry, clear client state and return to login. Logout requires the access token and returns `204`.

## Search and subjects

```http
POST /api/v1/search
Authorization: Bearer <token>
Content-Type: application/json

{"query":"Company:C04166","limit":25}
```

Response: `{ "data": [{"id":"uuid","type":"Company","label":"Company:C04166","status":"active"}], "page":{"nextCursor":null,"limit":25} }`. Only safe fields are returned. Results are already clearance-filtered. The current implementation searches subject label and exact external reference; transaction-type filters are not yet implemented.

## Investigations and analysis

Create:

```json
{"subjectId":"uuid","title":"Review unusual activity","purpose":"Authorized investigation","cutoffAt":"2025-06-16T00:00:00Z","predictionHorizonStart":null,"predictionHorizonEnd":null}
```

Call `POST /investigations/:id/analyze` with `{}`. A successful response is `202`:

```json
{
  "runId":"uuid",
  "status":"SUCCEEDED",
  "result":{
    "requestId":"uuid",
    "investigationId":"uuid",
    "engineVersion":"prysm-ai-http-v1",
    "generatedAt":"...",
    "assessment":{"type":"uncalibrated_attention_assessment","strength":0.10,"confidence":0.68,"isFraudProbability":false},
    "components":{}, "findings":{}, "evidence":[], "graphIntelligence":{},
    "limitations":[], "modelVersions":{}, "provenance":{}
  }
}
```

The endpoint currently completes synchronously but uses `202` and a run record so it can become asynchronous without changing the result contract. Disable repeated Analyze clicks while a request is active. Treat all assessment language as investigative attention, never confirmed fraud or probability.

## Graph

`GET /graph/subjects/:id/subgraph?cutoffAt=<ISO>&maxHops=2&maxNodes=100`. Limits are 1–3 hops and 1–250 nodes. The response contains `{nodes, edges, truncated}`. The frontend must display truncation and cutoff when present and must not request arbitrary depth.

## RAG chat and ingestion

Public chat accepts `{"question":"What is structuring?","conversationId":"optional-uuid"}`. It returns `{"conversationId":"uuid","requestId":"uuid","answer":"...","sources":[{"title":"...","source":"...","category":"...","version":"..."}],"mode":"public"}`. Extra browser fields such as `authenticated`, `context`, `clearance`, or `accessScope` are rejected with `400`. A RAG outage maps to `503 RAG_UNAVAILABLE`.

Authorized chat accepts the same fields plus required `investigationId`. The backend revalidates the live session, `chat:authorized`, clearance rank 2, ownership/sharing, and investigation classification. It constructs the subject, latest analysis/GNN result, findings, evidence, cutoff, limitations, versions, and bounded relationships itself. The response uses mode `investigator` and may include curated `evidence`. Never send trusted context from the browser.

`POST /rag/ingest` accepts `title` and `content`, with optional `source`, `category`, `version`, and object `metadata`; success is `201 {"success":true,"documentId":"uuid","chunks":1}`. It requires `rag:ingest` and clearance rank 4. Ingestion is knowledge indexing, not training.

For realtime chat, connect to `ws://<backend>/api/v1/ws/chat`. First send `{"type":"authenticate","accessToken":"..."}` and wait for `{"type":"authenticated"}`. Then send `{"question":"...","investigationId":"uuid","conversationId":"optional-uuid"}`. Events are `ready`, `authenticated`, `token`, `done`, and sanitized `error`; `done` preserves request ID, conversation ID, and sources. The backend applies the same live authorization and context construction as HTTP.

## Pagination

List/search responses use `{data, page:{nextCursor, limit}}`. `nextCursor` is currently `null`; keep frontend state cursor-ready and do not invent page numbers.

## Frontend route consumption

- Login → `/auth/login`, `/auth/me`, `/me/permissions`, `/me/clearance`.
- Search → `/search`, then `/subjects/:id`.
- Investigation list/detail → `/investigations`, `/investigations/:id`.
- Analyze → `/investigations/:id/analyze`; run detail → `/analysis-runs/:runId`.
- Graph/evidence panels → bounded subgraph and evidence endpoints.
- Model/audit screens render only when corresponding permission is returned.
- Public/authorized chat should be feature-disabled unless protected dependency health reports RAG `ok`; `degraded` means retrieval/fallback may work but Gemini generation is not verified.
