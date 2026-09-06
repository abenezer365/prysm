# Prysm Phase 5 frontend integration guide

Base URL: `http://127.0.0.1:4000/api/v1`. Browser clients call only the backend. Internal AI/RAG credentials never belong in the browser. Requests and responses use JSON; protected requests send `Authorization: Bearer <accessToken>`.

Every response includes `x-request-id`. Error example:

```json
{"error":{"code":"INSUFFICIENT_CLEARANCE","message":"Investigation classification exceeds clearance","requestId":"6fc9696a-2735-4a08-b1ab-94c1b60ffecf"}}
```

Handle 400 validation/malformed JSON, 401 expired/revoked sessions, 403 authorization, 404 missing resources, 409 incompatible state, 413 size, 429 rate limit, 500 internal failure, 502 invalid/rejected upstream and 503 unavailable dependencies. Do not retry mutations blindly. Lists are bounded windows, with `page:{limit,nextCursor:null}` where indicated; there is no cursor paging yet. Date strings must include a timezone. Optional request properties should be omitted rather than set to null unless their schema explicitly allows null.

## Investigator workflow

1. Sign up through `POST /applications`; approval by an authorized reviewer provisions an account and returns a temporary password to that reviewer. There is no unrestricted self-registration. Account approval does not imply investigator privileges; reviewer-selected role/clearance controls access.
2. Sign in, read `/auth/me`, `/me/permissions`, `/me/clearance`, and show only permitted controls. Change the temporary password through `/me/password`.
3. Search people or retrieve `/suspects/top?cutoffAt=2025-12-11T10:00:00Z&limit=10`. Use the returned operational UUID `subjectId` when opening a case. Canonical keys such as `Person:P01870` are separate from UUIDs.
4. Create the case, run analysis, and render its unchanged `result`. Retrieve it later through `/investigations/:id/intelligence`. Graph edges with `type:"transfers"` are transactions; other edge types describe ownership, institutions, devices and relationships. Use evidence references to select suspicious transactions/entities/relationships; the browser must not calculate suspicion.
5. Ask `/chat/authorized` with the case ID. The server loads the latest successful result and calls Phase 4 `/explain`; the browser cannot supply detector results or trusted context. Render `reasoning.detected` separately from `reasoning.explanation`. Retrieve your history through `/investigations/:id/conversation`.
6. Add feedback, update case status, or export `{format:"JSON"}`. Sign out through `/auth/logout`; the session is immediately revoked.

Full-population ranking can take minutes on its first request. The AI service caches up to eight cutoff rankings per process and serializes compute work. Display a loading state and use a suitably long request timeout (up to 600 seconds locally). Do not substitute the evaluation report's top entities: its population and labels are different.

## Example requests

```http
POST /api/v1/auth/login
Content-Type: application/json

{"email":"investigator@example.com","password":"your-private-password"}
```

```json
{"accessToken":"<access-token>","refreshToken":"<session-uuid>.<refresh-secret>","tokenType":"Bearer","expiresIn":900}
```

Keep tokens out of logs. Rotate through `POST /auth/refresh` with `{refreshToken}` before expiry, replace both returned tokens, and serialize refresh attempts. Reusing a refresh token revokes the session. Password reset token delivery is not configured for production; development responses can include the reset token.

```http
POST /api/v1/search
Authorization: Bearer <access-token>
Content-Type: application/json

{"query":"P01870","limit":5}
```

```http
POST /api/v1/investigations
Authorization: Bearer <access-token>
Content-Type: application/json

{"subjectId":"<UUID returned by search>","title":"Review deposit activity","cutoffAt":"2025-12-11T10:00:00Z"}
```

Call `POST /investigations/<case-uuid>/analyze` with `{}`. Success is **200**, with `{runId,status:"SUCCEEDED",result}`. This is synchronous. The result is also persisted; failures leave a failed run with a sanitized error code. Prevent duplicate Analyze submissions while a request is running.

The result contract is `prysm-intelligence-v2`:

```text
version, subject:{entity_key}, investigation_window:{cutoff,observation_start,history_start}
assessment:{strength,risk_level,confidence,coverage,breakdown,is_fraud_probability:false}
intelligence_components:{rules,anomaly,network,gnn}
findings, features, evidence[], graph, limitations[], provenance
```

`strength` is nullable. Null means unavailable, never zero risk. Assessment breakdowns retain configured/effective weights and weighted contributions. `risk_level`, evidence and graph annotations are engine outputs. These are synthetic review priorities, not calibrated fraud probabilities. The portable complete example [phase2_investigation.json](../../ai-engine/examples/phase2_investigation.json) illustrates the contract; runtime uses the selected Phase 3 model, so its scores differ from that older example.

`RankingEntry` contains `rank,entity_key,cutoff,dataset_version,analysis_fingerprint,overall_risk,risk_level,is_fraud_probability:false,score_breakdown,evidence_ids`; the backend adds `subjectId`. The population is all people observed at the supplied cutoff, excluding unavailable assessments. Clearance filtering may leave rank gaps.

## GNN Maze and evidence

Read the graph from the saved result to keep it aligned with the displayed analysis. The standalone graph endpoint requires `cutoffAt` and recomputes through the same engine. Bounds belong to the engine configuration; browser `maxHops`/`maxNodes` overrides are rejected.

Nodes include `id,type,label,attention,evidence_ids,highlight_color` where applicable. Edges include `id,source,target,type`, source references, transaction/relationship fields and the same annotations. `highlight_color:"red"` means an evidence-linked review lead, not guilt. Preserve `analysis_fingerprint`, `truncated`, cutoff and limitations. Unmarked elements are not certified innocent.

Evidence items include `evidence_id,signal_source,signal_type,description,supporting_entity_ids,supporting_transaction_ids,supporting_relationship_ids,supporting_edge_ids,measurements,timestamps,provenance`. Exact graph IDs resolve source and target nodes. Evidence IDs are version/fingerprint-bound strings; `/evidence/:id` instead takes the operational UUID from case `findings[].evidence[].evidence.id`.

## Reasoning, history and knowledge

```http
POST /api/v1/chat/authorized
Authorization: Bearer <access-token>
Content-Type: application/json

{"investigationId":"<case-uuid>","question":"Explain the supporting transactions"}
```

The response includes `conversationId,requestId,answer,sources,mode:"investigator",evidence,reasoning`. Reasoning contains `version:"prysm-reasoning-v1",summary,detected:{subject,assessment,evidence},explanation:{findings,knowledge_context,uncertainty,recommended_direction},provenance`. Detector evidence and assessment remain unchanged. Local extraction explains the case; optional Gemini selection sees only allowlisted topics and approved general references. Local LLM inference remains deferred by the Phase 4 instruction. Public chat can send general questions to Gemini: private questions belong only in the authorized route.

Reuse a returned conversationId only within the same user's investigation. History contains stored question/answer, sources and the source analysis fingerprint/run ID; raw prompts and full intelligence are not stored again in conversation rows. Private data persists in PostgreSQL and is subject to operator-managed retention; no automatic retention policy is configured.

Knowledge ingestion is administrative. Submit `{title,content,source?,category?,version?,metadata?}` to `/rag/ingest`. Review `metadata.cloud_approved:true` explicitly before setting it. Do not ingest case records as general knowledge. Response is `201 {jobId,status,documentId,chunks}`; document routes expose the resulting job record.

## WebSocket

Connect to `ws://127.0.0.1:4000/api/v1/ws/chat`. Receive `ready`, then send `{"type":"authenticate","accessToken":"..."}` and wait for `authenticated`. Send `{"question":"Explain the findings","investigationId":"<uuid>","conversationId":"<optional uuid>"}`. The backend revalidates the live token and case for every message. Events are `token` (one local explanation chunk), `done` (requestId, conversationId, sources, evidence, reasoning), or sanitized `error`. Concurrent messages on one socket return `CHAT_BUSY`. It uses the same protected HTTP explanation boundary, with no upstream credential in a WebSocket URL.

## Phase 6 changes required

Use the current fields above instead of old `engineVersion/components/graphIntelligence/isFraudProbability` fields. Treat analyzed success as 200. Require a cutoff for ranking and graph. Download the returned JSON export directly. Remove links to the retired model download-ticket endpoint. Display actual dashboard totals and nullable relationship counts. No Phase 6 UI/content redesign is included in Phase 5.


## Complete HTTP endpoint reference

Generated from the mounted routes and their Zod request validators. `?` means optional. All protected endpoints additionally return 401 for invalid/revoked sessions and 403 for missing permission, clearance or case access. Every endpoint can return the standard 400/413/429/500/502/503 error envelope described above; resource routes can return 404 and conflicting mutations 409. Request field constraints below are enforced; complete machine-readable schemas are in [openapi.json](openapi.json).

### POST /applications

Apply for an account (the sign-up flow).

- **Auth:** Public.
- **Request:** email: string (format="email"; pattern="^(?!\\.)(?!.*\\.\\.)([A-Za-z0-9_'+\\-\\.]*)[A-Za-z0-9_+-]@([A-Za-z0-9][A-Za-z0-9\\-]*\\.)+[A-Za-z]{2,}$"); displayName: string (minLength=2; maxLength=120); profession: string (minLength=2; maxLength=160); organization?: string (maxLength=200); organizationRole?: string (maxLength=160); phone?: string (maxLength=40); reason: string (minLength=20; maxLength=2000); justification: string (minLength=100; maxLength=10000); requestedRoleId?: string (format="uuid"; pattern="^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$"); requestedClearanceLevelId?: string (format="uuid"; pattern="^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$"); supportingEvidence?: array
- **Response:** 202 {id,status:"PENDING",createdAt}; duplicate pending application: 409.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /applications

Review pending account applications.

- **Auth:** application:review, minimum rank 3.
- **Request:** limit?: integer (minimum=1; maximum=100; default=20); status?: string (one of PENDING, APPROVED, REJECTED). No body.
- **Response:** {data:[Application],page}; Application includes identity, profession, justification, requestedRole, requestedClearance, documents metadata and review history.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### PATCH /applications/:id

Approve or reject an account application.

- **Auth:** application:review, minimum rank 3.
- **Request:** Path IDs are UUIDs. status: string (one of APPROVED, REJECTED); reviewNote: string (minLength=5; maxLength=4000)
- **Response:** Application; newly provisioned accounts also return oneTimeCredential:{temporaryPassword,mustChangePassword:true}. Deliver this credential privately. 409 if already reviewed.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### POST /auth/refresh

Rotate a single-use refresh token.

- **Auth:** Public.
- **Request:** refreshToken: string (minLength=20)
- **Response:** {accessToken,refreshToken,tokenType:"Bearer",expiresIn}; 401 REFRESH_TOKEN_REUSED on expired, revoked or reused token.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### POST /auth/password/request

Request a reset token.

- **Auth:** Public.
- **Request:** email: string (format="email"; pattern="^(?!\\.)(?!.*\\.\\.)([A-Za-z0-9_'+\\-\\.]*)[A-Za-z0-9_+-]@([A-Za-z0-9][A-Za-z0-9\\-]*\\.)+[A-Za-z]{2,}$")
- **Response:** 202 {accepted:true}; development only: developmentResetToken. No production email delivery is configured.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### POST /auth/password/reset

Consume a reset token and revoke sessions.

- **Auth:** Public.
- **Request:** token: string (minLength=20); password: string (minLength=12; maxLength=200)
- **Response:** 204; 400 RESET_TOKEN_INVALID.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### POST /me/password

Change password and revoke other sessions.

- **Auth:** Authenticated.
- **Request:** currentPassword: string (minLength=8); newPassword: string (minLength=12; maxLength=200)
- **Response:** 204; 400 CURRENT_PASSWORD_INVALID; 409 PASSWORD_REUSE.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### PATCH /me/profile

Update profile image and preferences.

- **Auth:** Authenticated.
- **Request:** profileImageUrl?: string/null; preferences?: object
- **Response:** User DTO.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### PATCH /me/settings

Update supported user settings.

- **Auth:** Authenticated.
- **Request:** profileImageUrl?: string/null; preferences?: object; fields: compactMode?: boolean; emailNotifications?: boolean; reducedMotion?: boolean
- **Response:** User DTO; preferences supports compactMode, emailNotifications, reducedMotion.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /users

List application users.

- **Auth:** user:read, minimum rank 3.
- **Request:** limit?: integer (minimum=1; maximum=100; default=20); status?: string (one of PENDING, ACTIVE, SUSPENDED, DISABLED, REJECTED); role?: string (maxLength=80); clearanceRank?: integer (minimum=1; maximum=100). No body.
- **Response:** {data:[User with createdAt,lastLoginAt],page}.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /users/:id

Read user and session metadata.

- **Auth:** user:read, minimum rank 3.
- **Request:** Path IDs are UUIDs. No body.
- **Response:** User plus clearanceRank and sessions (id,deviceInfo,createdAt,lastUsedAt,expiresAt,revokedAt).
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### PATCH /users/:id

Manage user status, role or clearance.

- **Auth:** user:manage, minimum rank 4.
- **Request:** Path IDs are UUIDs. status?: string (one of ACTIVE, SUSPENDED, DISABLED, REJECTED); roleId?: string (format="uuid"; pattern="^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$"); clearanceLevelId?: string (format="uuid"; pattern="^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$"); reason: string (minLength=10; maxLength=2000)
- **Response:** User DTO; 409 SELF_LOCKOUT_PREVENTED; live requests recheck database grants.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /dashboard/summary

Read live authorized dashboard totals.

- **Auth:** Authenticated.
- **Request:** No body.
- **Response:** {metrics:{availableModels,openInvestigations,totalAuthorizedSubjects,relationships:null,operationalInventoryTotal},recentInvestigations,recentActivity,clearanceDistribution,health,generatedAt}; null relationships means not stored operationally.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### PATCH /investigations/:id

Update case title, purpose, status or sharing.

- **Auth:** investigation:update, minimum rank 2.
- **Request:** Path IDs are UUIDs. title?: string (minLength=1; maxLength=200); purpose?: string (minLength=1; maxLength=2000); status?: string (one of OPEN, IN_REVIEW, CLOSED); shared?: boolean
- **Response:** Updated Investigation; applies case ownership and clearance.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /investigations/:id/timeline

Read case activity chronologically.

- **Auth:** investigation:read, minimum rank 1.
- **Request:** Path IDs are UUIDs. Optional query limit (bounded integer; default 20, cases/history 50; max 100, public news 50). No body.
- **Response:** {data:[{id,type,timestamp,title,status?,severity?,decision?}],page}.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### POST /investigations/:id/feedback

Persist investigator feedback about a case or run.

- **Auth:** investigation:feedback, minimum rank 2.
- **Request:** Path IDs are UUIDs. analysisRunId?: string (format="uuid"; pattern="^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$"); rating: string (one of USEFUL, PARTIAL, NOT_USEFUL, INCORRECT); rationale: string (minLength=10; maxLength=4000); metadata?: object
- **Response:** 201 {id,investigationId,analysisRunId,createdBy,rating,rationale,metadata,createdAt}; run must belong to this case.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### POST /investigations/:id/exports

Export the latest successful result as JSON.

- **Auth:** investigation:export, minimum rank 3.
- **Request:** Path IDs are UUIDs. format: string (must equal JSON)
- **Response:** 200 {jobId,status:"SUCCEEDED",format:"JSON",createdAt,result:Intelligence}; save result as JSON locally. CSV/PDF rejected (400); no background queue.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /activity

Read your own audit trail.

- **Auth:** Authenticated.
- **Request:** limit?: integer (minimum=1; maximum=100; default=20); action?: string (maxLength=100). No body.
- **Response:** {data:[{id,action,resourceType,resourceId,decision,reasonCode,requestId,metadata,createdAt}],page}.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /news

Read published public news.

- **Auth:** Public.
- **Request:** limit?: integer (minimum=1; maximum=50; default=20). No body.
- **Response:** {data:[{id,slug,title,description,body,imageRef,authorName,publishedAt,updatedAt}],page}.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /news/admin

List news drafts and published content.

- **Auth:** news:manage, minimum rank 3.
- **Request:** limit?: integer (minimum=1; maximum=100; default=20). No body.
- **Response:** {data:[NewsRecord],page}; includes status, metadata and authorId.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### POST /news

Create a news record.

- **Auth:** news:manage, minimum rank 3.
- **Request:** slug: string (maxLength=120; pattern="^[a-z0-9-]+$"); title: string (minLength=3; maxLength=240); description: string (minLength=10; maxLength=1000); body: string (minLength=20; maxLength=100000); imageRef?: string (maxLength=1000); authorName?: string (maxLength=160); status?: string (default="DRAFT"; one of DRAFT, PUBLISHED); metadata?: object
- **Response:** 201 NewsRecord with id and timestamps.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### PATCH /news/:id

Edit, publish or archive news.

- **Auth:** news:manage, minimum rank 3.
- **Request:** Path IDs are UUIDs. title?: string (minLength=3; maxLength=240); description?: string (minLength=10; maxLength=1000); body?: string (minLength=20; maxLength=100000); imageRef?: string/null; authorName?: string (maxLength=160); status?: string (one of DRAFT, PUBLISHED, ARCHIVED); metadata?: object
- **Response:** Updated NewsRecord.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### POST /contact

Submit a contact message.

- **Auth:** Public.
- **Request:** name: string (minLength=2; maxLength=120); email: string (format="email"; pattern="^(?!\\.)(?!.*\\.\\.)([A-Za-z0-9_'+\\-\\.]*)[A-Za-z0-9_+-]@([A-Za-z0-9][A-Za-z0-9\\-]*\\.)+[A-Za-z]{2,}$"); subject?: string (maxLength=200); message: string (minLength=20; maxLength=10000); metadata?: object
- **Response:** 202 {id,status:"RECEIVED",createdAt}.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### POST /bug-reports

Submit a bug report.

- **Auth:** Public.
- **Request:** reporterName?: string (maxLength=120); contactEmail?: string (format="email"; pattern="^(?!\\.)(?!.*\\.\\.)([A-Za-z0-9_'+\\-\\.]*)[A-Za-z0-9_+-]@([A-Za-z0-9][A-Za-z0-9\\-]*\\.)+[A-Za-z]{2,}$"); description: string (minLength=20; maxLength=20000); severity?: string (default="MEDIUM"; one of LOW, MEDIUM, HIGH, CRITICAL); requestId?: string (format="uuid"; pattern="^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$"); clientVersion?: string (maxLength=100); diagnostics?: object
- **Response:** 202 {id,status,severity,createdAt}.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /bug-resolutions

Read approved public resolutions.

- **Auth:** Public.
- **Request:** limit?: integer (minimum=1; maximum=50; default=20). No body.
- **Response:** {data:[{id,description,severity,publicExplanation,workaround,resolvedAt}],page}.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /bug-reports

List internal bug reports.

- **Auth:** bug:manage, minimum rank 3.
- **Request:** limit?: integer (minimum=1; maximum=100; default=20); status?: string (one of OPEN, TRIAGED, IN_PROGRESS, RESOLVED, CLOSED). No body.
- **Response:** {data:[BugRecord],page}; includes diagnostics, assignment, rootCause, resolutionNotes and publication controls.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### PATCH /bug-reports/:id

Triage or resolve an internal bug.

- **Auth:** bug:manage, minimum rank 3.
- **Request:** Path IDs are UUIDs. status?: string (one of OPEN, TRIAGED, IN_PROGRESS, RESOLVED, CLOSED); severity?: string (one of LOW, MEDIUM, HIGH, CRITICAL); assignedTo?: string/null; rootCause?: string (maxLength=10000); resolutionNotes?: string (maxLength=20000); workaround?: string (maxLength=10000); publicExplanation?: string (maxLength=10000); publicApproved?: boolean
- **Response:** Updated BugRecord.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### POST /beta/applications

Apply for beta access.

- **Auth:** Public.
- **Request:** email: string (format="email"; pattern="^(?!\\.)(?!.*\\.\\.)([A-Za-z0-9_'+\\-\\.]*)[A-Za-z0-9_+-]@([A-Za-z0-9][A-Za-z0-9\\-]*\\.)+[A-Za-z]{2,}$"); displayName: string (minLength=2; maxLength=120); purpose: string (minLength=30; maxLength=4000)
- **Response:** 202 {id,status,createdAt}.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /beta/applications

List beta applications.

- **Auth:** beta:review, minimum rank 3.
- **Request:** limit?: integer (minimum=1; maximum=100; default=20); status?: string (one of PENDING, APPROVED, REJECTED). No body.
- **Response:** {data:[{id,email,displayName,purpose,status,reviewedBy,reviewNote,reviewedAt,createdAt,updatedAt}],page}.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### PATCH /beta/applications/:id

Approve or reject beta access.

- **Auth:** beta:review, minimum rank 3.
- **Request:** Path IDs are UUIDs. status: string (one of APPROVED, REJECTED); reviewNote: string (minLength=5; maxLength=2000)
- **Response:** Updated beta record; newly provisioned user also returns oneTimeCredential.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### POST /contributors/applications

Apply to contribute.

- **Auth:** Public.
- **Request:** email: string (format="email"; pattern="^(?!\\.)(?!.*\\.\\.)([A-Za-z0-9_'+\\-\\.]*)[A-Za-z0-9_+-]@([A-Za-z0-9][A-Za-z0-9\\-]*\\.)+[A-Za-z]{2,}$"); displayName: string (minLength=2; maxLength=120); expertise: string (minLength=3; maxLength=300); portfolioUrl?: string (format="uri"; maxLength=1000); motivation: string (minLength=50; maxLength=5000); availability?: string (maxLength=300)
- **Response:** 202 {id,status,createdAt}.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /contributors/applications

List contributor applications.

- **Auth:** contributor:review, minimum rank 3.
- **Request:** limit?: integer (minimum=1; maximum=100; default=20); status?: string (one of PENDING, APPROVED, REJECTED). No body.
- **Response:** {data:[{id,email,displayName,expertise,portfolioUrl,motivation,availability,status,reviewedBy,reviewNote,reviewedAt,createdAt,updatedAt}],page}.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### PATCH /contributors/applications/:id

Review contributor application.

- **Auth:** contributor:review, minimum rank 3.
- **Request:** Path IDs are UUIDs. status: string (one of APPROVED, REJECTED); reviewNote?: string (maxLength=2000)
- **Response:** Updated contributor record.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /datasets

Read canonical fact-table metadata only.

- **Auth:** Public.
- **Request:** limit?: integer (minimum=1; maximum=100; default=20). No body.
- **Response:** {data:[{id,code,name,sourceRef,recordCount:string,columns,features,dateStart,dateEnd,visibility,lastScannedAt,metadata,...}],page}; no analytical rows or ground truth.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### POST /datasets/refresh

Synchronize canonical fact and selected model metadata.

- **Auth:** dataset:manage, minimum rank 4.
- **Request:** Empty JSON object `{}`.
- **Response:** 200 {status:"COMPLETED",refreshed:6,lastScannedAt}; historical metadata is archived, not mixed with the current benchmark.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /rag/conversations

Read authorized conversation records for administration.

- **Auth:** rag:history:read, minimum rank 3.
- **Request:** limit?: integer (minimum=1; maximum=100; default=20); scope?: string (one of PUBLIC, AUTHORIZED); conversationId?: string (format="uuid"; pattern="^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$"). No body.
- **Response:** {data:[{id,conversationId,requestId,ragRequestId,userId,scope,question,answer,sources,ragVersion,latencyMs,status,createdAt}],page}; own records unless rag:history:read:any and rank 4.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /rag/documents

List knowledge ingestion records.

- **Auth:** rag:documents:read, minimum rank 3.
- **Request:** limit?: integer (minimum=1; maximum=100; default=20). No body.
- **Response:** {data:[KnowledgeRecord],page}; {id,externalId,title,description,source,category,version,status,chunkCount,enabled,metadata,createdBy,errorCode,createdAt,updatedAt}.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /rag/documents/:id

Read one knowledge ingestion record.

- **Auth:** rag:documents:read, minimum rank 3.
- **Request:** Path IDs are UUIDs. No body.
- **Response:** KnowledgeRecord.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### PATCH /rag/documents/:id

Enable or disable a knowledge document.

- **Auth:** rag:ingest, minimum rank 4.
- **Request:** Path IDs are UUIDs. enabled: boolean
- **Response:** Updated KnowledgeRecord after RAG service confirmation.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /suspects/top

Rank all observed people at an explicit cutoff using the selected engine.

- **Auth:** subject:read, minimum rank 2.
- **Request:** Required query cutoffAt (timezone-aware ISO date-time); limit? integer 1–50, default 10. No body.
- **Response:** {data:[RankingEntry with subjectId],population,cutoffAt,page}. No backend scoring. Clearance filtering may return fewer than limit.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /dashboard/top-suspects

Alias for the same canonical ranking.

- **Auth:** subject:read, minimum rank 2.
- **Request:** Required query cutoffAt (timezone-aware ISO date-time); limit? integer 1–50, default 10. No body.
- **Response:** Same as GET /suspects/top; cutoffAt is required.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /investigations/:id/intelligence

Retrieve the latest successful current-contract result.

- **Auth:** investigation:read, minimum rank 2.
- **Request:** Path IDs are UUIDs. No body.
- **Response:** {runId,result:Intelligence}; 409 ANALYSIS_REQUIRED or ANALYSIS_STALE; legacy v1 results require reanalysis.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /investigations/:id/conversation

Read your conversation history for an accessible analyzed case.

- **Auth:** chat:authorized, minimum rank 2.
- **Request:** Path IDs are UUIDs. Optional query limit (bounded integer; default 20, cases/history 50; max 100, public news 50). No body.
- **Response:** {data:[{id,conversationId,question,answer,sources,createdAt,contextManifest}],page}; newest first.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /health

Process liveness.

- **Auth:** Public.
- **Request:** No body.
- **Response:** {status:"ok",version:"0.5.0"}.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /health/ready

PostgreSQL readiness.

- **Auth:** Public.
- **Request:** No body.
- **Response:** {status:"ready"}; 503 NOT_READY on database failure.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /health/dependencies

Check PostgreSQL, selected AI artifacts and RAG.

- **Auth:** health:dependencies:read, minimum rank 0.
- **Request:** No body.
- **Response:** {status,services:{postgres,aiEngine,rag}}.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### POST /auth/login

Sign in with an approved active account.

- **Auth:** Public.
- **Request:** email: string (format="email"; pattern="^(?!\\.)(?!.*\\.\\.)([A-Za-z0-9_'+\\-\\.]*)[A-Za-z0-9_+-]@([A-Za-z0-9][A-Za-z0-9\\-]*\\.)+[A-Za-z]{2,}$"); password: string (minLength=8); deviceInfo?: string (maxLength=500)
- **Response:** {accessToken,refreshToken,tokenType:"Bearer",expiresIn:900}; 401 INVALID_CREDENTIALS, 403 ACCOUNT_INACTIVE.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### POST /auth/logout

Revoke the current session immediately.

- **Auth:** Authenticated.
- **Request:** Empty JSON object `{}`.
- **Response:** 204 (no body).
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /auth/me

Read current user identity.

- **Auth:** Authenticated.
- **Request:** No body.
- **Response:** User: {id,email,displayName,profileImageUrl,preferences,status,role,clearance}; never passwordHash.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /me/permissions

Read current permission codes.

- **Auth:** Authenticated.
- **Request:** No body.
- **Response:** {permissions:[string]}.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /me/clearance

Read current clearance rank.

- **Auth:** Authenticated.
- **Request:** No body.
- **Response:** {rank:number}.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /subjects/:id

Read a subject summary.

- **Auth:** subject:read, minimum rank 0.
- **Request:** Path IDs are UUIDs. No body.
- **Response:** {id,type,label,status}; subject clearance required.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /subjects/:id/profile

Read operational profile data.

- **Auth:** subject:sensitive:read, minimum rank 3.
- **Request:** Path IDs are UUIDs. No body.
- **Response:** {id,type,label,profile}; imported canonical people have a minimal profile.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### POST /search

Find canonical people and materialize only matching operational subjects.

- **Auth:** subject:read, minimum rank 0.
- **Request:** query: string (minLength=2; maxLength=200); limit: integer (minimum=1; maximum=50; default=20)
- **Response:** {data:[{id,type,label,status}],page,datasetVersion}; 502 PERSON_INDEX_UNAVAILABLE if neither index nor operational results are available.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### POST /investigations

Create an investigation for a materialized subject and explicit cutoff.

- **Auth:** investigation:create, minimum rank 2.
- **Request:** subjectId: string (format="uuid"; pattern="^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$"); title?: string (maxLength=200); purpose?: string (maxLength=2000); cutoffAt: string (format="date-time"; pattern="^(?:(?:\\d\\d[2468][048]|\\d\\d[13579][26]|\\d\\d0[48]|[02468][048]00|[13579][26]00)-02-29|\\d{4}-(?:(?:0[13578]|1[02])-(?:0[1-9]|[12]\\d|3[01])|(?:0[469]|11)-(?:0[1-9]|[12]\\d|30)|(?:02)-(?:0[1-9]|1\\d|2[0-8])))T(?:(?:[01]\\d|2[0-3]):[0-5]\\d:[0-5]\\d(?:\\.\\d+)?(?:Z|([+-](?:[01]\\d|2[0-3]):[0-5]\\d)))$"); predictionHorizonStart?: value; predictionHorizonEnd?: value
- **Response:** 201 Investigation: {id,createdBy,subjectId,status,title,purpose,cutoffAt,contextVersion,minimumClearanceRank,shared,createdAt,updatedAt,...}.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /investigations

List cases allowed by ownership, sharing and clearance.

- **Auth:** investigation:read, minimum rank 0.
- **Request:** Optional query limit (bounded integer; default 20, cases/history 50; max 100, public news 50). No body.
- **Response:** {data:[{id,status,title,cutoffAt,subject:{id,type,label},createdAt}],page}.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /investigations/:id

Open a case with its persisted findings and runs.

- **Auth:** investigation:read, minimum rank 0.
- **Request:** Path IDs are UUIDs. No body.
- **Response:** {id,status,title,purpose,cutoffAt,subject,findings,analysisRuns,scientificStatus}; finding.evidence[].evidence.id is the operational evidence UUID.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### POST /investigations/:id/analyze

Run synchronous canonical analysis and persist the exact result.

- **Auth:** investigation:analyze, minimum rank 2.
- **Request:** Path IDs are UUIDs. Empty JSON object `{}`.
- **Response:** 200 {runId,status:"SUCCEEDED",result:Intelligence}; 409 CUTOFF_REQUIRED or SUBJECT_NOT_LINKED; failed upstream runs remain FAILED.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /investigations/:id/analysis-runs/:runId

Read a particular case run.

- **Auth:** investigation:read, minimum rank 0.
- **Request:** Path IDs are UUIDs. No body.
- **Response:** AnalysisRun: {id,investigationId,status,cutoffAt,dataSnapshot,requestPayload,responsePayload:Intelligence|null,errorCode,startedAt,completedAt,createdAt,...}.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /graph/subjects/:id/subgraph

Read the engine graph at an explicit cutoff.

- **Auth:** graph:read, minimum rank 2.
- **Request:** Path IDs are UUIDs. Required query cutoffAt (timezone-aware ISO date-time). No body.
- **Response:** Graph: {version,subject,cutoff,truncated,nodes,edges,analysis_fingerprint,highlight_semantics}. Engine configuration owns bounds; maxHops/maxNodes overrides rejected.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /evidence/:id

Read a stored evidence reference linked to an accessible case.

- **Auth:** evidence:read, minimum rank 2.
- **Request:** Path IDs are UUIDs. No body.
- **Response:** {id,sourceType,sourceId,label,excerpt,eventTime,metadata:EngineEvidence,...}; 403 if no linked case is accessible.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /models

List model registry metadata.

- **Auth:** model:read, minimum rank 0.
- **Request:** No body.
- **Response:** {data:[{id,code,version,modelType,status,evaluationScope,isCalibratedProbability,metadata}]}; active selected bundle and retired historical entries; no download tickets.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### GET /audit/events

Read recent security/application audit events.

- **Auth:** audit:read, minimum rank 4.
- **Request:** No body.
- **Response:** {data:[AuditEvent]}; event metadata excludes question text, passwords, tokens and analysis payloads.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### POST /chat/public

Ask a general knowledge question.

- **Auth:** Public.
- **Request:** question: string (minLength=1; maxLength=4000); conversationId?: string (format="uuid"; pattern="^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$")
- **Response:** {conversationId,requestId,answer,sources,mode:"public"}; each response starts a new public conversation ID. Never send private case questions here.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### POST /chat/authorized

Explain a trusted stored investigation using Phase 4.

- **Auth:** chat:authorized, minimum rank 2.
- **Request:** question: string (minLength=1; maxLength=4000); conversationId?: string (format="uuid"; pattern="^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$"); subjectId?: string (format="uuid"; pattern="^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$"); investigationId?: string (format="uuid"; pattern="^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$"); cutoffAt?: value
- **Response:** {conversationId,requestId,answer,sources,mode:"investigator",evidence,reasoning:Reasoning}; 409 ANALYSIS_REQUIRED; 403 CONVERSATION_ACCESS_DENIED; 502 RAG_INVALID_RESPONSE.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.

### POST /rag/ingest

Ingest reviewed general knowledge.

- **Auth:** rag:ingest, minimum rank 4.
- **Request:** title: string (minLength=1; maxLength=300); content: string (minLength=1; maxLength=100000); source?: string (maxLength=300); category?: string (maxLength=100); version?: string (maxLength=50); metadata?: object
- **Response:** 201 {jobId,status:"COMPLETED",documentId,chunks}; failed jobs retain FAILED state; metadata.cloud_approved must be explicitly reviewed.
- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.
