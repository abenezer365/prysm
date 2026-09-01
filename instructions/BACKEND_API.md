# Prysm Backend API — Canonical Frontend Contract

Base HTTP URL: `http://127.0.0.1:4000/api/v1`
Realtime URL: `ws://127.0.0.1:4000/api/v1/ws/chat`

The browser calls this API only. Protected requests send `Authorization: Bearer <accessToken>`. Every response contains `x-request-id`. Errors use `{"error":{"code":"CODE","message":"Message","details":{},"requestId":"uuid"}}`. Dates are ISO-8601 UTC strings and IDs are UUIDs. Collections use `{data:[],page:{nextCursor:null,limit:20}}` unless noted. Handle `400`, `401`, `403`, `404`, `409`, `413`, `429`, `502`, and `503`.

## Public and account endpoints

| Method | Path | Request / behavior | Success |
|---|---|---|---|
| GET | `/health` | Process liveness | `{status:"ok"}` |
| GET | `/health/ready` | PostgreSQL readiness | `200`, or `503` |
| GET | `/health/dependencies` | Permission `health:dependencies:read` | PostgreSQL, AI, and RAG status |
| POST | `/applications` | `email`, `displayName`, `profession`, `organization`, `organizationRole`, `phone`, `justification`, optional `supportingEvidence[]` metadata | `202` pending application |
| POST | `/contact` | `name`, `email`, `subject`, `message` | `201` received submission |
| POST | `/bug-reports` | `email?`, `title`, `description`, `severity`, optional reproduction fields | `201` open report |
| GET | `/bug-resolutions` | Public resolved-report summaries | Collection |
| POST | `/beta/applications` | `email`, `displayName`, `organization?`, `role?`, `motivation`, `useCase?` | `202` pending application |
| GET | `/news` | Published news | Collection |
| GET | `/datasets` | Dataset metadata | Collection |
| POST | `/auth/login` | `email`, `password`, `deviceInfo?` | Access/refresh token pair and safe user |
| POST | `/auth/refresh` | `refreshToken`; rotated on every use | New token pair |
| POST | `/auth/logout` | Authenticated; revokes current session | `204` |
| POST | `/auth/password/request` | `email`; never reveals address existence | `202` |
| POST | `/auth/password/reset` | `token`, `newPassword` | `204`; revokes all sessions |
| GET | `/auth/me` | Authenticated | Safe identity |
| POST | `/me/password` | `currentPassword`, `newPassword` | `204`; revokes other sessions |
| PATCH | `/me/profile` | `displayName` | Updated identity |
| PATCH | `/me/settings` | Optional `profileImageUrl` and permitted `preferences` (`compactMode`, `emailNotifications`, `reducedMotion`) | Updated safe identity/settings DTO |
| GET | `/me/permissions` | Authenticated | Live permission codes |
| GET | `/me/clearance` | Authenticated | Live clearance |

Reset tokens are single-use and expire. Development responses may include `developmentResetToken`; production requires a notification provider.

## Administration

| Method | Path | Access | Purpose |
|---|---|---|---|
| GET | `/applications` | `application:review` | List applications |
| PATCH | `/applications/:id` | `application:review` | Approve/reject with notes and optional role/clearance; approval activates or provisions an account |
| GET | `/users` | `user:read` | Filterable users |
| GET | `/users/:id` | `user:read` | User detail |
| PATCH | `/users/:id` | `user:write` | Update status, role, clearance, or display name |
| GET | `/news/admin` | `news:manage` | All news and drafts |
| POST | `/news` | `news:manage` | Create news |
| PATCH | `/news/:id` | `news:manage` | Edit or publish news |
| GET | `/bug-reports` | `bug:manage` | List reports |
| PATCH | `/bug-reports/:id` | `bug:manage` | Update status, resolution, or assignee |
| GET | `/beta/applications` | `beta:review`, rank ≥ 3 | List applications |
| PATCH | `/beta/applications/:id` | `beta:review`, rank ≥ 3 | Approve/reject once; approval provisions a restricted `BETA_TESTER` |
| GET | `/contributors/applications` | `contributor:review`, rank ≥ 3 | List contributor applications independently of system-access applications |
| PATCH | `/contributors/applications/:id` | `contributor:review`, rank ≥ 3 | Approve/reject once with a moderation note; does not grant intelligence access |
| POST | `/datasets/refresh` | `dataset:manage` | Scan configured local datasets and upsert metadata |
| GET | `/audit/events` | `audit:read`, rank ≥ 4 | Administrative audit trail |

Approvals may return a one-time credential only in that response and set `mustChangePassword`. Secrets never appear in list/detail responses.

`POST /contributors/applications` is public and accepts `email`, `displayName`, `expertise`, `motivation`, optional `portfolioUrl`, and optional `availability`. It returns `202 {id,status,createdAt}` and rejects a second pending application for the same email.

## Development administrator bootstrap

There is no public bootstrap endpoint. In development, provide `SEED_ADMIN_EMAIL` and `SEED_ADMIN_PASSWORD` only to the seed process, then run `npm run db:seed` from `server/`. The script creates the account only when both values are present, assigns `ADMIN`, `TOP_SECRET`, and the complete seeded permission set. Do not place these variables in production configuration; omit them after the initial bootstrap and rotate the temporary password immediately.

## Dashboard, intelligence, and activity

| Method | Path | Access / request | Success |
|---|---|---|---|
| GET | `/dashboard/summary` | Authenticated | Live scoped investigation, finding, model, user, clearance, and service totals |
| GET | `/dashboard/top-suspects` | `investigation:read` | Subjects ranked from persisted findings |
| GET | `/activity` | Authenticated | Principal-visible activity |
| POST | `/search` | `subject:read`; `{query,limit?}` | Matching subjects |
| GET | `/subjects/:id` | `subject:read` + classification | Redacted summary |
| GET | `/subjects/:id/profile` | `subject:sensitive:read`, rank ≥ 3 | Sensitive profile |
| POST | `/investigations` | `investigation:create`, rank ≥ 2 | `201` investigation |
| GET | `/investigations` | `investigation:read` | Owned/shared scope, or all with `read:any` |
| GET | `/investigations/:id` | Resource policy + clearance | Full permitted detail |
| PATCH | `/investigations/:id` | `investigation:update` + resource policy | Update metadata/status/horizon |
| GET | `/investigations/:id/timeline` | `investigation:read` + resource policy | Unified timeline |
| POST | `/investigations/:id/analyze` | `investigation:analyze`, rank ≥ 2 | `202` durable run and result |
| GET | `/investigations/:id/analysis-runs/:runId` | Resource policy | Immutable run |
| POST | `/investigations/:id/feedback` | `investigation:feedback` | Persist rating/comment/finding feedback |
| POST | `/investigations/:id/exports` | `investigation:export`; `{format:"PDF"|"JSON"|"CSV"}` | `202` queued export |
| GET | `/graph/subjects/:id/subgraph` | `graph:read`, rank ≥ 2; bounded query params | Bounded graph |
| GET | `/evidence/:id` | `evidence:read`, rank ≥ 2 | Evidence reference |

## Models, chat, and RAG

| Method | Path | Access / request | Success |
|---|---|---|---|
| GET | `/models` | `model:read` | Safe registry metadata |
| POST | `/models/:id/download-tickets` | `model:download` | Short-lived ticket metadata |
| POST | `/chat/public` | `{question,conversationId?}` | Grounded answer and sources |
| POST | `/chat/authorized` | `chat:authorized`, rank ≥ 2 + investigation policy | Scoped answer, sources, evidence |
| WS | `/ws/chat` | Same policy as authorized chat | Streaming `token` then `done` |
| GET | `/rag/conversations` | `rag:history:read` | Persisted conversations |
| POST | `/rag/ingest` | `rag:ingest`, rank ≥ 4; title/content/source/category/version/metadata | `201` record, document ID, chunks |
| GET | `/rag/documents` | `rag:documents:read` | Ingested documents |
| GET | `/rag/documents/:id` | `rag:documents:read` | Ingestion detail |
| PATCH | `/rag/documents/:id` | `rag:documents:write`; `{enabled:boolean}` | Retrieval state |

Authorized chat derives clearance and context server-side; injected client context is rejected. RAG document state persists across chatbot restarts, and disabled documents are excluded from retrieval.

## Async behavior and explicit gaps

- Analysis returns `202`, but currently awaits the AI adapter before responding; the persisted run remains the status resource.
- Export job creation is implemented; the PDF/CSV/JSON artifact worker is **not implemented**.
- Model download-ticket creation is implemented; binary artifact redemption/streaming is **not implemented**.
- RAG text ingestion and document controls are implemented; multipart upload, malware scanning, OCR, and async file ingestion are **not implemented**.
- Dataset refresh provides local metadata and CSV structure; full Parquet introspection and chart generation are **not implemented**.
- Password-reset email/SMS delivery is **not implemented**.

## WebSocket sequence

Wait for `ready`, send `{"type":"authenticate","accessToken":"..."}`, wait for `authenticated`, then send `{"question":"...","investigationId":"uuid","conversationId":"optional-uuid"}`. `done` includes request ID, conversation ID, answer, and sources. Errors are sanitized.

This file is authoritative when older examples in `docs/API.md` or `docs/openapi.yaml` differ.
