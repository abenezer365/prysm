# PRYSM INTELLIGENCE — BACKEND COMPLETION & FRONTEND CONTRACT

## Objective

Bring the existing Prysm Intelligence backend to a much more complete, frontend-ready state. First inspect the current backend, PostgreSQL schema/migrations, authentication, AI Engine/RAG/GNN integrations, and `BACKEND_API.md`. Preserve working architecture, but add the missing APIs, tables, relationships, validation, authorization, auditing, and background/update logic required below. The browser must call the backend only; the backend remains authoritative for identity, permissions, clearance, ownership, investigation scope, and sensitive context.

## 1. Complete the Missing API Surface — Implement the Behavior, Not Just the Routes

Do not simply create placeholder endpoints. For every missing API, first understand what the frontend needs to accomplish and implement the backend behavior, database access, validation, authorization, and response shape that makes that feature genuinely usable.

### Dashboard summary

Create `GET /dashboard/summary` as the single backend source for the main authenticated dashboard overview. When an officer opens the dashboard, this API should return the current authorized system picture: available models, open/recent investigations, recent safe activity, security-clearance distribution where the requester is allowed to see it, and system/dependency health. Compute these values from real database/system state rather than fabricating metrics in React. Apply permission/clearance filtering server-side so the frontend never receives data it should not display. Shape the response so the frontend can directly populate metric cards, small charts, recent-activity panels, and health indicators without combining many unrelated calls.

### Access-application review

Create `GET /applications` so an authorized reviewing officer can open the access-review workspace and see pending, approved, rejected, and other relevant applications within their authority. Create `PATCH /applications/:id` so the reviewer can approve or reject an application and record a review note. The review action must update the real access state of the applicant, record who made the decision and when, preserve the previous status, and create an audit event. An approved application must be able to transition the applicant into an active login-capable account; a rejected or pending application must not. The API should return safe application information and review metadata suitable for an administrative UI.

### Rich access-application submission

Expand `POST /applications` so the public access-request page can collect the information needed for a serious manual verification process: identity/contact information, profession, organization/role, reason for requesting access, a detailed written justification, and optional supporting evidence/document metadata. The backend should validate and safely persist this information, prevent duplicate or abusive submissions, and return only a safe submission receipt. If supporting files are accepted, add a document endpoint or multipart flow with type/size restrictions and a secure storage/scanning path. Do not grant access merely because an application was submitted.

### User administration

Create `GET /users` for an authorized administrator to browse users with safe filters such as status, role, and clearance. Create `GET /users/:id` to inspect one user's permitted profile and access information. Create `PATCH /users/:id` so authorized administrators can change only explicitly allowed fields such as account status, role, or security clearance, with a required reason for sensitive changes. Every administrative change must be persisted, validated against policy, and audited. The response should give the frontend the current user state so the Users page can immediately reflect the change.

### Session refresh and account recovery

Create `POST /auth/refresh` so an already authenticated client can obtain a new access token without forcing the user to log in repeatedly. The implementation should rotate/revoke refresh credentials according to the existing session model and prevent replay. Create `POST /auth/password/request` and `POST /auth/password/reset` so a user who has lost access can securely start and complete a one-time recovery flow. Create `POST /me/password` so an authenticated user can change their password from Settings. These flows must be real server-side security operations, not frontend-only state changes, and must create appropriate audit/session events.

### Investigation lifecycle

Create `PATCH /investigations/:id` so an investigator can safely update allowed investigation metadata or status. Create `GET /investigations/:id/timeline` so the investigation page can show a chronological record of important events, analysis runs, findings, evidence activity, and other relevant changes. Create `POST /investigations/:id/feedback` so an investigator can record structured feedback about an analysis result. Create `POST /investigations/:id/exports` so the system can start a controlled export job for an authorized investigation. All four APIs must enforce ownership/resource policy and live clearance, preserve history, and return stable data the frontend can render directly.

### General activity feed

Create `GET /activity` as the authenticated user's operational activity feed, not as a replacement for the highly restricted administrative audit store. It should let the frontend show recent meaningful actions such as searches, investigation actions, graph exploration, chat activity, and other permitted events. The backend should filter the results according to the requesting user's scope. This gives the Activity page and dashboard a legitimate record of what has happened without exposing unrelated or overly sensitive audit information.

### News

Create `GET /news` so the public website and authenticated interface can request published news from the database instead of using hardcoded frontend content. The returned records should contain the title, description/body, image reference, author/display information where safe, publication date, and status appropriate for the caller. Later administrative create/edit/publish operations should use the same underlying model so the public site automatically reflects approved content. Drafts and restricted metadata must stay server-side.

### Contact submissions

Create `POST /contact` so the public contact form actually delivers a structured message to the backend. Persist the submission with the necessary contact details, message, timestamps, and safe metadata, apply rate limiting/validation, and return a simple receipt. The endpoint should integrate with the project's chosen email/notification path if one exists; otherwise persist the submission reliably for administrative processing. Never expose private contact submissions through public APIs.

### Bug reports and resolution knowledge

Create `POST /bug-reports` so visitors and users can submit detailed bug reports including the problem description, optional request ID, client version, contact information, and safe diagnostic metadata. Persist each report with status, severity, timestamps, and ownership/review information. Add the authorized query/update behavior needed by staff to investigate it, and store resolution notes, root cause, workaround, and final status. Public clients should then be able to query only approved, sanitized resolution information so the Bug Report / Resolution Guide pages can become dynamic knowledge pages without exposing private reporter information.

### Model download access

Create `POST /models/:id/download-tickets` as a controlled authorization step for model artifacts. When an authorized user requests a model download, the backend should verify the user's permission and model-specific policy, create a short-lived signed/download ticket, and return its expiry, checksum, and audit reference. Do not return permanent storage URLs or unrestricted model files directly through the API.

## 2. Users, Identity, Clearance and Access Approval

Extend the user model so every user has a complete safe profile and security clearance rank `1–4`:

1 = Restricted, 2 = Confidential, 3 = Secret, 4 = Top Secret.

Keep clearance server-authoritative. Support safe editable profile information such as profile picture and permitted minor fields, but do not allow casual changes to name or core identity fields. Require a documented/legal-change workflow for protected identity changes.

Build the access-request lifecycle around an actual approval process. A public applicant should be able to submit identity/contact details, profession, organization/role, reason for access, a detailed justification/essay, and optional supporting evidence/documents. Store application status, reviewer, review notes, timestamps, and status history.

Submitting an application must NOT automatically grant system access. An applicant must remain unable to log in until an authorized officer approves the application and activates access. Add strong validation, rate limiting, safe file handling/scanning hooks, and auditability. Add the necessary database tables/relations for applications, review history, supporting documents, and access state.

## 3. Authentication, Sessions and Recovery

Implement secure refresh-token/session rotation and password recovery/change flows. Prefer HttpOnly refresh cookies where compatible with the existing backend design. Login must verify credentials AND whether the account has approved active access. Logout must revoke the current session. Keep `/auth/me`, `/me/permissions`, and `/me/clearance` live and server-derived.

## 4. RAG and Communication Persistence

Persist chat/RAG communication for traceability and frontend history. Store appropriate metadata such as request/conversation ID, user ID where applicable, public/authorized scope, question, retrieval/vector-result references or bounded retrieval metadata, LLM answer, sources/evidence references, model/version metadata, status, and timestamp.

Never store passwords, tokens, unrestricted hidden context, or unnecessary sensitive information.

Add authenticated APIs to retrieve permitted communication history with pagination and safe filtering. Authorized history must remain scoped to the user, investigation, resource, and clearance rules. The persisted record should support frontend conversation/history screens, debugging, provenance, and responsible auditing.

## 5. Activity and Audit Logging

Create a proper activity/audit system for meaningful authenticated actions: login/logout, searches, subject access, investigation creation/analysis/updates, graph queries, chat activity, exports, settings changes, access approvals/rejections, clearance changes, model actions, and other sensitive operations.

Each event should capture actor, action, target/resource where appropriate, timestamp, request ID, outcome, and safe metadata. Provide a frontend-queryable activity endpoint with filtering and authorization. Keep highly sensitive administrative audit events separately protected where appropriate.

## 6. News System

Create a persistent news/content model and APIs. Authorized officers/admins should be able to create, edit, publish, unpublish, and retrieve news items. Support title, description/body, image/media reference, author, status, publication time, timestamps, and safe metadata.

Expose only published/safe content through public endpoints so news can dynamically appear on public-facing pages. Drafts and administrative information must remain protected.

## 7. Dashboard Metrics and Top Suspects

Create dynamic dashboard APIs that return authorized metrics such as total persons/subjects, open investigations/cases, relationships, recent activity, model availability, health, and other meaningful aggregates.

Create a dedicated top-suspects API returning the top three authorized subjects based on actual stored intelligence/risk results. Do not fabricate scores. Return available risk dimensions, concise explanation text, timestamp/version/provenance, and safe references needed by the frontend.

Response shapes must be easy for the frontend to use directly for cards, tables, charts, graphs, and trend visualizations without heavy reshaping.

## 8. Main Search + AI Engine + GNN Workflow

Make the admin search a real intelligence workflow. Support subject-name search plus useful filters and pagination. When a subject is selected, create/reuse the appropriate investigation context and call the existing AI Engine through the backend.

Persist the returned intelligence in the backend, including available AML risk, transaction risk, behavioral/anomaly indicators, confidence/limitations, explanation/description, model/version, timestamps, and provenance. Do not invent metrics that the AI Engine does not actually provide.

Also query the existing PostgreSQL relationship data and/or GNN implementation. Provide a dedicated graph/subgraph API that converts backend graph results into frontend-ready node/edge data. Nodes should identify entity type and safe display information; edges should identify relationship type, strength/friendship threshold, and useful metadata. Support people, companies, banks, accounts, peers, and other entity types available in the project.

The frontend GNN Maze should be able to draw the returned structure directly as a graph: person/company/bank/account nodes, connecting lines, relationship strength, and hoverable node/edge details. Enforce hop/node bounds and live clearance/resource authorization. Record search, analysis, and graph actions in the activity log.

## 9. Bug Reports and Resolution Knowledge

Create persistent bug-report storage and APIs. Support reporter/contact details, detailed description, severity, status, request ID, client version, timestamps, and safe diagnostic metadata. Provide authorized query/update operations.

Add resolution information: root cause, resolution notes, status history, workaround/solution, and approved public explanation. This data should power a dynamic public bug-resolution guide while preventing exposure of private reporter information.

## 10. Beta Tester Program

Create a beta-tester application flow separate from full intelligence access. Applicants can provide basic identity/contact information and testing purpose. Approved testers receive restricted beta access for model/testing functionality only, not the complete intelligence application.

Add database tables, application/review/status APIs, authentication, and clear authorization boundaries for beta users.

## 11. Dataset Representation System

Create a dataset metadata/representation table and API. Scan the project's available datasets and store safe metadata such as dataset name, source/path reference, row/record counts, columns, data types, feature summaries, date coverage, last scan time, and other useful statistics.

Add a refresh mechanism intended to run about weekly. Expose query endpoints for the public dataset-representation page and make the response directly usable for frontend charts.

Where useful, generate server-side chart/visualization artifacts (for example with matplotlib) and expose stable safe references. Do not expose sensitive raw data merely because metadata was requested.

## 12. User Settings

Provide authenticated APIs for profile picture and other allowed minor settings/profile fields. Protected identity fields must remain immutable through ordinary settings and require the appropriate legal/administrative process for changes.


## 12A. RAG Administration, Conversation Review and Ingestion

Build the RAG administration APIs around the actual workflows the frontend needs.

The admin RAG page needs to show what the system has recently been asked and how the RAG/LLM responded. Provide an authenticated recent-conversations API that returns safe conversation records with question, answer/result summary, conversation/request IDs, user information where permitted, scope, sources or retrieval metadata, model/version metadata, status, and timestamps. Support pagination and safe filters. The backend must enforce clearance/resource rules before returning a conversation; an administrator should never receive hidden prompts, credentials, unrestricted retrieved context, or records outside their authority.

The same RAG section needs an ingestion form. Create an authorized ingestion endpoint that accepts knowledge as text and supported uploaded files. The purpose is not merely to save an uploaded file in PostgreSQL: the backend must actually put the knowledge into the existing RAG pipeline so future retrieval can use it. The flow should be: receive -> validate -> safely store/process -> extract text -> normalize -> chunk -> embed -> insert/update the vector index -> persist document/chunk metadata -> report processing status.

Support metadata such as title, description, source, category, version, and custom metadata. For files, enforce size/type limits and provide a safe extraction/scanning hook. Long ingestion should be asynchronous, returning a document/job ID that the frontend can poll for `queued`, `processing`, `completed`, or `failed` state plus useful counts such as chunks created.

If the current RAG implementation cannot ingest files or the requested content types, extend it rather than building a fake ingestion layer. The final behavior must be verifiable by asking the RAG a question that can retrieve the newly ingested content.

Also provide authorized document-management operations so admins can list indexed documents, inspect metadata/status, and disable/remove a document from future retrieval. These operations must update the real vector/index state as well as the database record where applicable, and every administrative RAG change must create an audit event.

The final API contract must explain exactly how the frontend should use these conversation, ingestion, processing-status, and document-management operations.

## 13. Public Dynamic Content

Public pages that need backend data must have safe public APIs. At minimum ensure contact submissions, bug reports/resolution information, published news, and other intended public content have clear contracts. Public endpoints must never return protected subjects, investigations, audit records, private chat history, or sensitive user data.

## 14. API Design Rules

Keep the established patterns from `BACKEND_API.md`:

- ISO-8601 UTC timestamps
- UUID identifiers where appropriate
- `{data,page:{nextCursor,limit}}` for paged collections
- `Authorization: Bearer <accessToken>` for protected HTTP requests unless a secure cookie/session mechanism is explicitly used
- consistent `x-request-id`
- consistent error shape: `{"error":{"code","message","details":{},"requestId":"uuid"}}`
- handle 400, 401, 403, 404, 409, 413, 429, 502, and 503 correctly
- use asynchronous run/job IDs for long AI/analysis/export work rather than unnecessary long blocking requests

Return stable, explicit DTOs designed for direct frontend consumption. Never leak credentials, tokens, unrestricted internal context, or database-private fields.

## 15. Database and Integration Work

Add or modify PostgreSQL tables, indexes, foreign keys, status histories, and audit relations wherever necessary. Keep migrations clean and reversible. Reuse existing entities instead of duplicating concepts.

Verify the complete flow between backend, AI Engine, RAG, GNN/relationship logic, and PostgreSQL. The backend should collect, normalize, authorize, persist, and expose the intelligence needed by the frontend.

## 16. Final Deliverables

After implementation:

1. update migrations/schema and add only safe development seed data if needed;
2. test authentication, approval/denial, clearance, permissions, audit, public/private boundaries, search, AI analysis, RAG persistence, GNN graph responses, news, bug reports, beta access, datasets, and settings;
3. verify the access-request workflow truly blocks unapproved login;
4. verify every sensitive action creates the correct activity/audit record;
5. verify public endpoints expose only approved public information;
6. create/replace the canonical `BACKEND_API.md` with every available endpoint, including method, path, purpose, access requirement, permission/clearance rule, request parameters/body, response schema/examples, pagination, async behavior, errors, and frontend usage notes;
7. explicitly mark anything genuinely still unavailable as `NOT IMPLEMENTED`.

The final backend should leave the frontend with a dependable dynamic contract for authentication, access review, users, clearance, settings, dashboard metrics, top suspects, search, investigations, AI analysis, RAG/chat history, GNN relationships, activity logs, news, bug reports/resolutions, beta testing, dataset representation, and model-related capabilities.
