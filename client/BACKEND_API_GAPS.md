# Backend API Gaps

Every item below is `BACKEND REQUIRED`. The frontend must not treat these contracts as implemented until the backend contract is updated.

## Dashboard aggregates

- Method/path: `GET /dashboard/summary`
- Authorization: authenticated, field-level permission filtering
- Response: `{models:{available}, investigations:{open,recent:[]}, activity:[], securityDistribution?:[], health:{status}}`
- Consumer: `/app/dashboard`
- Reason: meaningful overview without multiple calls or fabricated metrics
- Recommendation: compute server-side from authorized records and omit unauthorized modules
- Status: not implemented

## Application review

- Method/path: `GET /applications`, `PATCH /applications/:id`
- Authorization: proposed `application:review`, high clearance
- Request: `{status:"APPROVED"|"REJECTED", note?:string}`
- Response: application DTO with review audit metadata
- Consumer: future access-review workspace
- Reason: the public intake endpoint cannot support administrative review
- Status: not implemented

## Rich access application

- Method/path: extend `POST /applications` or add `POST /applications/:id/documents`
- Authorization: public intake with strict validation, throttling, malware scanning
- Request: profession, organization, role, evidence metadata, supporting document
- Response: safe application receipt only
- Consumer: `/request-access`
- Reason: current contract accepts only email, display name, and reason
- Status: not implemented

## User administration

- Method/path: `GET /users`, `GET /users/:id`, `PATCH /users/:id`
- Authorization: proposed `user:read` and `user:manage`
- Request: allowlisted status, role, and clearance changes with reason
- Response: safe user DTO and audit reference
- Consumer: `/app/users`
- Reason: no user listing or mutation exists
- Status: not implemented

## Session refresh and account recovery

- Method/path: `POST /auth/refresh`, `POST /auth/password/request`, `POST /auth/password/reset`, `POST /me/password`
- Authorization: rotation/recovery policy as appropriate
- Request/response: secure token rotation and one-time reset contracts, preferably HttpOnly refresh cookie
- Consumer: auth context, login, settings
- Reason: current sessions cannot be refreshed and passwords cannot be recovered or changed
- Status: not implemented

## Investigation lifecycle

- Method/path: `PATCH /investigations/:id`, `GET /investigations/:id/timeline`, `POST /investigations/:id/feedback`, `POST /investigations/:id/exports`
- Authorization: resource ownership, live clearance, discrete permission per action
- Request: allowlisted metadata/status changes; structured feedback; explicit export format
- Response: updated DTO, cursor event page, feedback receipt, asynchronous export job
- Consumer: `/app/investigations/:id`
- Reason: investigators cannot update, review chronology, provide feedback, or export
- Status: not implemented

## General activity and news

- Method/path: `GET /activity`, `GET /news`
- Authorization: authenticated, backend-filtered scope
- Response: cursor pages of safe activity summaries and verified news items
- Consumer: `/app/activity`, `/app/news`, dashboard
- Reason: audit events are Top Secret administrative data and are not a general activity feed; no news contract exists
- Status: not implemented

## Contact and bug intake

- Method/path: `POST /contact`, `POST /bug-reports`
- Authorization: public, rate limited
- Request: contact `{name,email,message}`; bug `{email,requestId?,message,clientVersion?}`
- Response: `202 {id,status,createdAt}`
- Consumer: `/contact`, `/report/bug`
- Reason: current forms cannot submit safely
- Status: not implemented

## Model artifacts

- Method/path: `POST /models/:id/download-tickets`
- Authorization: proposed `model:download`, model-specific policy
- Response: short-lived download ticket, checksum, expiry, audit reference
- Consumer: future model detail
- Reason: model registry exposes metadata only
- Status: not implemented
