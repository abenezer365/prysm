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
