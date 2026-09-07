// Human-reviewed response and workflow descriptions; request schemas come from route validators.
export const contracts = {
  "GET /health": ["Process liveness", '{status:"ok",version:"0.5.0"}'],
  "GET /health/ready": [
    "PostgreSQL readiness",
    '{status:"ready"}; 503 NOT_READY on database failure',
  ],
  "GET /health/dependencies": [
    "Check PostgreSQL, selected AI artifacts and RAG",
    "{status,services:{postgres,aiEngine,rag}}",
  ],
  "POST /applications": [
    "Apply for an account (the sign-up flow)",
    '202 {id,status:"PENDING",createdAt}; duplicate pending application: 409',
  ],
  "GET /applications": [
    "Review pending account applications",
    "{data:[Application],page}; Application includes identity, profession, justification, requestedRole, requestedClearance, documents metadata and review history",
  ],
  "PATCH /applications/:id": [
    "Approve or reject an account application",
    "Application; newly provisioned accounts also return oneTimeCredential:{temporaryPassword,mustChangePassword:true}. Deliver this credential privately. 409 if already reviewed",
  ],
  "POST /auth/login": [
    "Sign in with an approved active account",
    '{accessToken,refreshToken,tokenType:"Bearer",expiresIn:900}; 401 INVALID_CREDENTIALS, 403 ACCOUNT_INACTIVE',
  ],
  "POST /auth/refresh": [
    "Rotate a single-use refresh token",
    '{accessToken,refreshToken,tokenType:"Bearer",expiresIn}; 401 REFRESH_TOKEN_REUSED on expired, revoked or reused token',
  ],
  "POST /auth/logout": [
    "Revoke the current session immediately",
    "204 (no body)",
  ],
  "GET /auth/me": [
    "Read current user identity",
    "User: {id,email,displayName,profileImageUrl,preferences,status,role,clearance}; never passwordHash",
  ],
  "GET /me/permissions": [
    "Read current permission codes",
    "{permissions:[string]}",
  ],
  "GET /me/clearance": ["Read current clearance rank", "{rank:number}"],
  "POST /auth/password/request": [
    "Request a reset token",
    "202 {accepted:true}; development only: developmentResetToken. No production email delivery is configured",
  ],
  "POST /auth/password/reset": [
    "Consume a reset token and revoke sessions",
    "204; 400 RESET_TOKEN_INVALID",
  ],
  "POST /me/password": [
    "Change password and revoke other sessions",
    "204; 400 CURRENT_PASSWORD_INVALID; 409 PASSWORD_REUSE",
  ],
  "PATCH /me/profile": ["Update profile image and preferences", "User DTO"],
  "PATCH /me/settings": [
    "Update supported user settings",
    "User DTO; preferences supports compactMode, emailNotifications, reducedMotion",
  ],
  "GET /users": [
    "List application users",
    "{data:[User with createdAt,lastLoginAt],page}",
  ],
  "GET /users/:id": [
    "Read user and session metadata",
    "User plus clearanceRank and sessions (id,deviceInfo,createdAt,lastUsedAt,expiresAt,revokedAt)",
  ],
  "PATCH /users/:id": [
    "Manage user status, role or clearance",
    "User DTO; 409 SELF_LOCKOUT_PREVENTED; live requests recheck database grants",
  ],
  "POST /search": [
    "Find canonical people and materialize only matching operational subjects",
    "{data:[{id,type,label,status}],page,datasetVersion}; 502 PERSON_INDEX_UNAVAILABLE if neither index nor operational results are available",
  ],
  "GET /subjects/:id": [
    "Read a subject summary",
    "{id,type,label,status}; subject clearance required",
  ],
  "GET /subjects/:id/profile": [
    "Read operational profile data",
    "{id,type,label,profile}; imported canonical people have a minimal profile",
  ],
  "GET /suspects/top": [
    "Rank all observed people at an explicit cutoff using the selected engine",
    "{data:[RankingEntry with subjectId],population,cutoffAt,page}. No backend scoring. Clearance filtering may return fewer than limit",
  ],
  "GET /dashboard/top-suspects": [
    "Alias for the same canonical ranking",
    "Same as GET /suspects/top; cutoffAt is required",
  ],
  "GET /dashboard/summary": [
    "Read live authorized dashboard totals",
    "{metrics:{availableModels,openInvestigations,totalAuthorizedSubjects,relationships:null,operationalInventoryTotal},recentInvestigations,recentActivity,clearanceDistribution,health,generatedAt}; null relationships means not stored operationally",
  ],
  "POST /investigations": [
    "Create an investigation for a materialized subject and explicit cutoff",
    "201 Investigation: {id,createdBy,subjectId,status,title,purpose,cutoffAt,contextVersion,minimumClearanceRank,shared,createdAt,updatedAt,...}",
  ],
  "GET /investigations": [
    "List cases allowed by ownership, sharing and clearance",
    "{data:[{id,status,title,cutoffAt,subject:{id,type,label},createdAt}],page}",
  ],
  "GET /investigations/:id": [
    "Open a case with its persisted findings and runs",
    "{id,status,title,purpose,cutoffAt,subject,findings,analysisRuns,scientificStatus}; finding.evidence[].evidence.id is the operational evidence UUID",
  ],
  "PATCH /investigations/:id": [
    "Update case title, purpose, status or sharing",
    "Updated Investigation; applies case ownership and clearance",
  ],
  "POST /investigations/:id/analyze": [
    "Run synchronous canonical analysis and persist the exact result",
    '200 {runId,status:"SUCCEEDED",result:Intelligence}; 409 CUTOFF_REQUIRED or SUBJECT_NOT_LINKED; failed upstream runs remain FAILED',
  ],
  "GET /investigations/:id/intelligence": [
    "Retrieve the latest successful current-contract result",
    "{runId,result:Intelligence}; 409 ANALYSIS_REQUIRED or ANALYSIS_STALE; legacy v1 results require reanalysis",
  ],
  "GET /investigations/:id/analysis-runs/:runId": [
    "Read a particular case run",
    "AnalysisRun: {id,investigationId,status,cutoffAt,dataSnapshot,requestPayload,responsePayload:Intelligence|null,errorCode,startedAt,completedAt,createdAt,...}",
  ],
  "GET /investigations/:id/timeline": [
    "Read case activity chronologically",
    "{data:[{id,type,timestamp,title,status?,severity?,decision?}],page}",
  ],
  "POST /investigations/:id/feedback": [
    "Persist investigator feedback about a case or run",
    "201 {id,investigationId,analysisRunId,createdBy,rating,rationale,metadata,createdAt}; run must belong to this case",
  ],
  "POST /investigations/:id/exports": [
    "Export the latest successful result as JSON",
    '200 {jobId,status:"SUCCEEDED",format:"JSON",createdAt,result:Intelligence}; save result as JSON locally. CSV/PDF rejected (400); no background queue',
  ],
  "GET /graph/subjects/:id/subgraph": [
    "Read the engine graph at an explicit cutoff",
    "Graph: {version,subject,cutoff,truncated,nodes,edges,analysis_fingerprint,highlight_semantics}. Engine configuration owns bounds; maxHops/maxNodes overrides rejected",
  ],
  "GET /evidence/:id": [
    "Read a stored evidence reference linked to an accessible case",
    "{id,sourceType,sourceId,label,excerpt,eventTime,metadata:EngineEvidence,...}; 403 if no linked case is accessible",
  ],
  "POST /chat/public": [
    "Ask a general knowledge question",
    '{conversationId,requestId,answer,sources,mode:"public"}; each response starts a new public conversation ID. Never send private case questions here',
  ],
  "POST /chat/authorized": [
    "Explain a trusted stored investigation using Phase 4",
    '{conversationId,requestId,answer,sources,mode:"investigator",evidence,reasoning:Reasoning}; 409 ANALYSIS_REQUIRED; 403 CONVERSATION_ACCESS_DENIED; 502 RAG_INVALID_RESPONSE',
  ],
  "GET /investigations/:id/conversation": [
    "Read your conversation history for an accessible analyzed case",
    "{data:[{id,conversationId,question,answer,sources,createdAt,contextManifest}],page}; newest first",
  ],
  "GET /rag/conversations": [
    "Read authorized conversation records for administration",
    "{data:[{id,conversationId,requestId,ragRequestId,userId,scope,question,answer,sources,ragVersion,latencyMs,status,createdAt}],page}; own records unless rag:history:read:any and rank 4",
  ],
  "POST /rag/ingest": [
    "Ingest reviewed general knowledge",
    '201 {jobId,status:"COMPLETED",documentId,chunks}; failed jobs retain FAILED state; metadata.cloud_approved must be explicitly reviewed',
  ],
  "GET /rag/documents": [
    "List knowledge ingestion records",
    "{data:[KnowledgeRecord],page}; {id,externalId,title,description,source,category,version,status,chunkCount,enabled,metadata,createdBy,errorCode,createdAt,updatedAt}",
  ],
  "GET /rag/documents/:id": [
    "Read one knowledge ingestion record",
    "KnowledgeRecord",
  ],
  "PATCH /rag/documents/:id": [
    "Enable or disable a knowledge document",
    "Updated KnowledgeRecord after RAG service confirmation",
  ],
  "GET /models": [
    "List model registry metadata",
    "{data:[{id,code,version,modelType,status,evaluationScope,isCalibratedProbability,metadata}]}; active selected bundle and retired historical entries; no download tickets",
  ],
  "GET /audit/events": [
    "Read recent security/application audit events",
    "{data:[AuditEvent]}; event metadata excludes question text, passwords, tokens and analysis payloads",
  ],
  "GET /activity": [
    "Read your own audit trail",
    "{data:[{id,action,resourceType,resourceId,decision,reasonCode,requestId,metadata,createdAt}],page}",
  ],
  "GET /news": [
    "Read published public news",
    "{data:[{id,slug,title,description,body,imageRef,authorName,publishedAt,updatedAt}],page}",
  ],
  "GET /news/admin": [
    "List news drafts and published content",
    "{data:[NewsRecord],page}; includes status, metadata and authorId",
  ],
  "POST /news": [
    "Create a news record",
    "201 NewsRecord with id and timestamps",
  ],
  "PATCH /news/:id": ["Edit, publish or archive news", "Updated NewsRecord"],
  "POST /contact": [
    "Submit a contact message",
    '202 {id,status:"RECEIVED",createdAt}',
  ],
  "POST /bug-reports": [
    "Submit a bug report",
    "202 {id,status,severity,createdAt}",
  ],
  "GET /bug-resolutions": [
    "Read approved public resolutions",
    "{data:[{id,description,severity,publicExplanation,workaround,resolvedAt}],page}",
  ],
  "GET /bug-reports": [
    "List internal bug reports",
    "{data:[BugRecord],page}; includes diagnostics, assignment, rootCause, resolutionNotes and publication controls",
  ],
  "PATCH /bug-reports/:id": [
    "Triage or resolve an internal bug",
    "Updated BugRecord",
  ],
  "POST /beta/applications": [
    "Apply for beta access",
    "202 {id,status,createdAt}",
  ],
  "GET /beta/applications": [
    "List beta applications",
    "{data:[{id,email,displayName,purpose,status,reviewedBy,reviewNote,reviewedAt,createdAt,updatedAt}],page}",
  ],
  "PATCH /beta/applications/:id": [
    "Approve or reject beta access",
    "Updated beta record; newly provisioned user also returns oneTimeCredential",
  ],
  "POST /contributors/applications": [
    "Apply to contribute",
    "202 {id,status,createdAt}",
  ],
  "GET /contributors/applications": [
    "List contributor applications",
    "{data:[{id,email,displayName,expertise,portfolioUrl,motivation,availability,status,reviewedBy,reviewNote,reviewedAt,createdAt,updatedAt}],page}",
  ],
  "PATCH /contributors/applications/:id": [
    "Review contributor application",
    "Updated contributor record",
  ],
  "GET /datasets": [
    "Read canonical fact-table metadata only",
    "{data:[{id,code,name,sourceRef,recordCount:string,columns,features,dateStart,dateEnd,visibility,lastScannedAt,metadata,...}],page}; no analytical rows or ground truth",
  ],
  "POST /datasets/refresh": [
    "Synchronize canonical fact and selected model metadata",
    '200 {status:"COMPLETED",refreshed:6,lastScannedAt}; historical metadata is archived, not mixed with the current benchmark',
  ],
};
