# Prysm Backend API — Frontend Contract

Base HTTP URL: `http://127.0.0.1:4000/api/v1`. Realtime URL: `ws://127.0.0.1:4000/api/v1/ws/chat`. The browser calls only this backend, never the AI Engine or RAG directly. Protected requests use `Authorization: Bearer <accessToken>`; authorization, clearance, ownership, and trusted context are resolved server-side.

Every HTTP response has `x-request-id`. Errors use `{"error":{"code":"...","message":"...","details":{},"requestId":"uuid"}}`. Handle `400`, `401`, `403`, `404`, `409`, `413`, `429`, `502`, and `503`. Dates are ISO-8601 UTC strings; IDs are UUIDs unless documented otherwise.

## Implemented endpoints

| Method | Route | Access | Request / purpose | Success |
|---|---|---|---|---|
| GET | `/health` | Public | Process liveness. | `200 {status:"ok"}` |
| GET | `/health/ready` | Public | Real PostgreSQL readiness. | `200`, or `503` |
| GET | `/health/dependencies` | `health:dependencies:read` | Real PostgreSQL, AI, and RAG checks. | `{status,services:{postgres,aiEngine,rag}}` |
| POST | `/applications` | Public | `{email,displayName,reason}`. | `202` application DTO |
| POST | `/auth/login` | Public | `{email,password,deviceInfo?}`. | Access/refresh token pair |
| POST | `/auth/logout` | Authenticated | Revokes current live session. | `204` |
| GET | `/auth/me` | Authenticated | Safe current identity. | User DTO |
| GET | `/me/permissions` | Authenticated | Live permission codes for UI gates. | Permission data |
| GET | `/me/clearance` | Authenticated | Live clearance; never infer client-side. | Clearance data |
| POST | `/search` | `subject:read` | `{query,limit?}`; limit 1–50, default 20. | `{data,page}` |
| GET | `/subjects/:id` | `subject:read` + classification | UUID path. | Redacted summary |
| GET | `/subjects/:id/profile` | `subject:sensitive:read`, rank ≥3 | UUID path. | Sensitive profile |
| POST | `/investigations` | `investigation:create`, rank ≥2 | `{subjectId,title?,purpose?,cutoffAt,predictionHorizonStart?,predictionHorizonEnd?}`. | `201` investigation |
| GET | `/investigations` | `investigation:read` | Owned/shared or `read:any`. | `{data,page}` |
| GET | `/investigations/:id` | `investigation:read` + resource/clearance | UUID path. | Investigation, findings, evidence links, runs |
| POST | `/investigations/:id/analyze` | `investigation:analyze`, rank ≥2 + resource policy | Empty `{}`; prevent duplicate UI submissions. | `202 {runId,status,result}` |
| GET | `/investigations/:id/analysis-runs/:runId` | `investigation:read` + resource policy | Two UUID paths. | Immutable run |
| GET | `/graph/subjects/:id/subgraph` | `graph:read`, rank ≥2 | `cutoffAt?`, `maxHops` 1–3, `maxNodes` 1–250. | Bounded graph |
| GET | `/evidence/:id` | `evidence:read`, rank ≥2 | UUID path. | Evidence reference |
| POST | `/chat/public` | Public | `{question,conversationId?}` only. | Knowledge answer and sources |
| POST | `/chat/authorized` | `chat:authorized`, rank ≥2 + resource/clearance | `{question,investigationId,conversationId?}`. | Investigator answer, sources, evidence |
| WS | `/ws/chat` | `chat:authorized`, rank ≥2 + resource/clearance | Authenticate first, then question/investigation ID. | `token`, then `done` |
| POST | `/rag/ingest` | `rag:ingest`, rank ≥4 | `{title,content,source?,category?,version?,metadata?}`. | `201 {success,documentId,chunks}` |
| GET | `/models` | `model:read` | Safe metadata only. | Model list |
| GET | `/audit/events` | `audit:read`, rank ≥4 | Latest administrative audit events. | Event page |

## Chat behavior

Public chat rejects injected `authenticated`, `context`, `clearance`, or `accessScope` fields. Authorized chat revalidates the live session and builds a cutoff-aware context containing only permitted subject/investigation metadata, the latest persisted assessment/GNN output, findings/evidence, limitations, versions, provenance, and bounded relationships. Persisted interactions include conversation/request IDs, user where applicable, scope, question, answer, sources, minimal context metadata, status, and timestamp—not credentials or unrestricted context.

WebSocket clients connect, receive `ready`, send `{"type":"authenticate","accessToken":"..."}`, wait for `authenticated`, then send `{"question":"...","investigationId":"uuid","conversationId":"optional-uuid"}`. `done` preserves request ID, conversation ID, and sources; `error` is sanitized.

List/search results use `{data,page:{nextCursor,limit}}`; `nextCursor` is currently `null`. Refresh, password reset/change, dashboards, application review, user mutation, investigation update/timeline/feedback/export, and model downloads are not implemented.

Exact schemas and expanded examples: [docs/openapi.yaml](docs/openapi.yaml) and [docs/API.md](docs/API.md). Operational limitations are in [BACKEND_INTEGRATION_REPORT.md](BACKEND_INTEGRATION_REPORT.md).
