# PRYSM INTELLIGENCE — BACKEND FINALIZATION + FIRST ADMIN + AUTHENTICATED APPLICATION FOUNDATION

Continue from the existing Prysm Intelligence backend. Do not discard the current architecture or working API implementation. Inspect the existing database, authentication, authorization, AI Engine, RAG, GNN, investigations, and API work first, then finish the system so it is genuinely ready for the authenticated frontend.

## First Admin Bootstrap

I currently cannot seed the first administrator. Add a safe development/bootstrap mechanism that creates the initial administrator directly from the backend without requiring the normal public application workflow.

Create one initial admin with credentials that you clearly print once in the completion report, for example:

Email: `admin@prysm.local`
Username: `prysm.admin`
Password: generate a strong temporary password and tell me the exact value.

Give this account the highest appropriate development security clearance, full administrative permissions, and active/approved access. Make the bootstrap mechanism safe so it is not an unrestricted public endpoint. Prefer a startup/CLI/script/migration approach or another explicitly development-only mechanism, and clearly document how to disable/remove it before production.

Verify that this admin can actually log in, receive the correct tokens/session, access `/auth/me`, permissions, clearance, dashboard, users, activity, RAG, news, GNN, settings, bug reports, beta testers, and contributor administration.

## Finish the Authenticated Application Backend

The authenticated application should support a real operational UI consisting of a persistent sidebar, application header, and central workspace. The backend must provide real data for these areas rather than leaving the frontend dependent on fabricated metrics.

The sidebar routes should have backend support for:

* Dashboard
* Search / Case
* Users
* Activity Log
* RAG Administration
* News
* GNN Maze
* Settings
* Bug Reports
* Beta Testers
* Contributors

The dashboard API should provide real authorized metrics and summaries such as people/subjects, investigations/cases, relationships, recent activity, model status, system health, and other useful intelligence statistics. Keep each metric traceable to actual data.

## Main Search / Case Workflow

Make the search page the main gateway into actual intelligence.

An authorized officer should be able to search a person by name and refine the search with useful filters. When a subject is selected, the backend should build or reuse the proper investigation context and invoke the existing AI Engine analysis.

Return frontend-ready intelligence such as the available AML/financial risk indicators, transaction-related signals, behavioral/anomaly indicators, explanations, confidence/limitations, timestamps, model/version, and provenance. Persist the analysis result so it becomes part of the investigation/history instead of disappearing after the request.

Every search, subject access, analysis, and investigation action must generate an appropriate activity/audit event.

## GNN Maze

Finish the backend graph workflow for the GNN Maze.

Given an authorized subject, retrieve the relevant relationships from PostgreSQL and the existing GNN/graph intelligence implementation and return a clean graph DTO designed specifically for frontend graph libraries.

The response should contain stable node IDs, node labels/types, safe display information, and edges with relationship type and a normalized relationship/friendship score from `0–100` where the underlying model/data supports such a score.

The frontend must be able to draw people, companies, banks, accounts, and other supported entities directly from this response.

Return additional safe hover information so the frontend can show useful details when a node is selected and relationship information when an edge is hovered.

Enforce hop/node limits and all clearance/resource authorization before returning graph data.

## RAG Administration

Finish the RAG admin workflow so an authorized officer can see recent RAG conversations and manage knowledge ingestion.

Provide recent authenticated conversation/history APIs showing safe question/answer information, request/conversation IDs, user where permitted, scope, retrieval/source metadata, model/version, status, and timestamp.

Provide a real ingestion workflow for both text and supported files. It must actually send knowledge through the RAG pipeline: validation -> extraction -> normalization -> chunking -> embedding -> vector indexing -> metadata persistence.

Return an asynchronous document/job status so the frontend can show ingestion progress.

Allow authorized administrators to list indexed knowledge, inspect metadata/status, and disable/remove knowledge from retrieval when appropriate.

Store RAG communication metadata in the database so authenticated users/admins can review permitted conversations later. Never store credentials or unrestricted hidden context.

## News

Implement a real news system. Authorized officers/admins should be able to create, edit, publish, and unpublish news containing title, body/description, image/media reference, author, publication date, and status.

Published news must be available through a safe public API so the public website can display current news dynamically.

## Users

Implement a complete user administration API.

Administrators should be able to view users, inspect an individual user, change allowed account properties, and manage security clearance `1–4` according to their own authorization.

The API must distinguish ordinary profile edits from protected identity changes. Profile picture and minor settings may be editable by the user; name and core identity information must require an appropriate legal/administrative process.

Every sensitive user change must be audited.

## Access Approval

Finish the access-application lifecycle.

Public applicants submit identity/contact information, profession, organization/role, reason, detailed written justification, and optional supporting documents.

Applications remain pending until an authorized officer reviews them.

Approval activates access. Rejection or pending status must prevent login.

Store review decisions, notes, reviewer, timestamps, application history, and access state.

This must be enforced server-side rather than merely represented in the frontend.

## Activity Log

The activity system should record meaningful actions performed by authenticated users, especially sensitive officer actions such as searching a subject, opening sensitive profiles, running analysis, exploring relationships, using RAG, changing users/clearance, approving access, editing news, ingesting documents, changing settings, and exporting information.

The Activity page should be able to retrieve these records with useful filters and timestamps.

This is intended to make the system accountable and auditable: unusual or unnecessary activity should be traceable to the responsible account.

## Bug Reports, Beta Testers and Contributors

Finish the backend contracts needed for:

* detailed bug submission, staff review, status, resolution notes, and public sanitized resolution guidance;
* beta tester applications and approval, with restricted beta/model-only access rather than full intelligence access;
* contributor applications/profile data where appropriate, with moderation/review capability.

Keep these separate from full intelligence access.

## Settings

Provide authenticated settings endpoints for editable profile picture and permitted preferences/minor profile information.

Keep protected identification information immutable under normal self-service settings.

## Frontend-Friendly API Contract

Every response intended for the frontend should have stable, clean DTOs. Avoid returning raw database records. Clearly expose safe display fields, timestamps, IDs, statuses, explanations, and metadata needed by the interface.

Support pagination consistently.

Preserve:

`x-request-id`

and the existing error structure:

`{"error":{"code":"...","message":"...","details":{},"requestId":"uuid"}}`

Respect authentication, permissions, clearance, ownership, and resource policy on every protected endpoint.

## AI / RAG / GNN Integration

Do not simulate intelligence responses in the backend. Connect the existing AI Engine, RAG system, and GNN/relationship implementation properly.

When AI analysis is requested:

backend -> authorize -> create/reuse investigation context -> call AI Engine -> validate result -> persist result -> return frontend-ready result -> create activity event.

When graph analysis is requested:

backend -> authorize -> obtain subject relationships/GNN output -> normalize nodes/edges -> persist useful result where appropriate -> return frontend-ready graph -> create activity event.

When RAG is requested by an authenticated user:

backend -> authorize -> build permitted context -> execute RAG -> persist question/retrieval/result metadata -> return answer and sources.

## Development Verification

Before finishing, test the complete flow using the first admin:

login -> dashboard -> users -> search -> subject -> investigation -> AI analysis -> GNN Maze -> RAG conversation -> RAG ingestion -> activity log -> news -> settings.

Also test denied access where appropriate.

Make sure an unapproved applicant cannot log in.

Make sure clearance restrictions actually work.

Make sure public users cannot obtain private conversations, subjects, investigations, audit records, or administrative data.

## Final API Documentation

Once the backend is complete, replace/update `BACKEND_API.md` so it becomes the single authoritative frontend contract.

For every endpoint explain:

* what it does
* who uses it
* HTTP method/path
* authentication requirement
* permission requirement
* clearance requirement
* request body/query/path parameters
* response DTO
* example request/response
* pagination
* async behavior
* errors
* frontend purpose

Do not merely list routes. Explain the behavior each API enables.

Clearly mark anything still genuinely unavailable as `NOT IMPLEMENTED`.

The final objective is that the frontend can build a complete authenticated Prysm Intelligence application from this contract without guessing backend behavior.
