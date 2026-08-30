# Backend Required APIs

These contracts are proposals, not implemented endpoints. Each must follow the standard safe error envelope and return `x-request-id`.

| Feature | Proposed endpoint | Method | Authorization | Frontend consumer | Suggested location |
|---|---|---|---|---|---|
| Dashboard summary | `/dashboard/summary` | GET | Authenticated, field-filtered permissions | App dashboard | `server/src/routes` plus dashboard service |
| Application review | `/applications`, `/applications/:id` | GET, PATCH | `application:review` | Future reviewer console | application route/service |
| User administration | `/users`, `/users/:id` | GET, PATCH | `user:read`, `user:manage` | `/app/users` | user route/service with audit |
| Session refresh | `/auth/refresh` | POST | Valid refresh session | Auth context | auth module, preferably HttpOnly rotation |
| Password recovery | `/auth/password/request`, `/auth/password/reset` | POST | Public one-time workflow | Login/settings | auth module |
| Password change | `/me/password` | POST | Authenticated plus current password | Settings | auth module |
| Investigation update | `/investigations/:id` | PATCH | owner/resource policy | Investigation detail | investigation route/service |
| Timeline | `/investigations/:id/timeline` | GET | `investigation:read` plus resource policy | Investigation detail | investigation query service |
| Feedback | `/investigations/:id/feedback` | POST | `investigation:feedback` | Findings review | investigation service with audit |
| Export | `/investigations/:id/exports` | POST | `investigation:export` | Case export | asynchronous export service |
| Model download | `/models/:id/download-tickets` | POST | `model:download` | Future model detail | model registry/artifact service |
| General activity | `/activity` | GET | Authenticated and scope-filtered | Activity/dashboard | separate from Top Secret audit log |
| News | `/news` | GET | Authenticated or public by item | News | verified editorial service |
| Contact | `/contact` | POST | Public, throttled | Contact page | public intake service |
| Bug reporting | `/bug-reports` | POST | Public, throttled | Bug page | support intake service |

Application review request should accept an allowlisted status and review note, returning a safe DTO plus audit reference. User mutations require reason, audit, and constrained role/clearance changes. Investigation feedback should identify run/finding, structured assessment, rationale, and timestamp. Exports should return a job ID rather than synchronously assembling protected data.

All list responses should use cursor pagination. All protected endpoints must revalidate live identity, permission, clearance, ownership, and resource classification. Do not accept client-supplied trusted clearance or context.
