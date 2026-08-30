# Prysm AI — Generate Complete Postman Backend Test Suite

Create a complete, ready-to-use Postman testing setup for the existing Prysm AI backend.

## Goal

Inspect the actual backend implementation and generate:

```text
postman/
├── Prysm.postman_collection.json
├── Prysm.postman_environment.json
└── README.md
```

The collection must be importable directly into Postman and usable for testing the backend from start to finish.

## Source of Truth

Inspect these first:

```text
server/
server/BACKEND_API.md
server/docs/API.md
server/docs/openapi.yaml
server/.env.example
server/package.json
actual Express routes/controllers
actual validation schemas
actual authentication/RBAC/clearance logic
```

The **actual backend code is the final source of truth**.

Do not invent endpoints, request fields, response fields, permissions, or environment variables.

## Collection Structure

Organize requests into logical folders:

```text
01 Health
02 Authentication
03 Profile
04 Search
05 Subjects
06 Investigations
07 AI Analysis
08 Graph
09 Evidence
10 Models
11 Chat / RAG
12 Users / Admin
13 Applications
14 Audit
```

Only include folders/endpoints that actually exist.

## Environment

Create a Postman environment containing variables such as:

```text
baseUrl
accessToken
refreshToken
userId
subjectId
investigationId
analysisRunId
```

Add other variables only when actually required by the backend.

Do NOT put real passwords, API keys, database credentials, or secrets into the generated files.

Use placeholders where necessary and clearly explain them in `README.md`.

## Automatic Variable Chaining

Make the collection usable without manually copying IDs.

For example:

```text
Login
→ automatically save accessToken
→ automatically save refreshToken
→ automatically save userId
```

Then:

```text
Create/search subject
→ save subjectId

Create investigation
→ save investigationId

Run analysis
→ save analysisRunId
```

Use Postman scripts to chain dependent requests wherever practical.

## Postman Tests

Every request should have appropriate automated tests.

Check things such as:

```text
correct HTTP status
JSON response
required response fields
valid data types
authentication behavior
expected business result
```

Do not create meaningless tests that only check `200`.

## Security / Negative Tests

Include tests for the backend's real security behavior where applicable:

```text
missing authentication
invalid authentication
expired/invalid token
insufficient permission
insufficient clearance
invalid resource ID
invalid request body
unauthorized resource access
rate-limit behavior where practical
```

Expected results must come from the actual backend implementation.

Do not assume every endpoint should return the same status code.

## AI Engine Testing

Test the complete real workflow through the backend:

```text
PostgreSQL
→ Backend
→ AI Engine
→ Backend
→ PostgreSQL
```

Include:

```text
health/dependency check
investigation creation
analysis request
analysis response validation
analysis ID capture
finding/result validation
```

Do NOT call the Python AI Engine directly from the Postman frontend collection unless there is a specific internal-service test folder that is useful.

The main collection must test the public/backend contract.

## RAG / Chat Testing

If the backend's RAG endpoints are implemented, test:

```text
RAG health
public chat
authorized chat
chat response validation
conversation ID capture
```

Also test that unauthorized requests cannot obtain protected investigation context.

If RAG is not yet exposed by the backend, do not invent those requests.

## Database-Backed Workflow

Where possible, make the collection follow a realistic sequence:

```text
Health
→ Login
→ Current User
→ Search
→ Subject
→ Create Investigation
→ Investigation Detail
→ Run AI Analysis
→ Findings
→ Graph
→ Evidence
→ Analysis History
→ Chat
→ Logout
```

Do not make every request depend on every previous request if the endpoint can reasonably be tested independently.

## API Documentation

Create:

```text
postman/README.md
```

Explain:

- how to import the collection;
- how to import/select the environment;
- required variables;
- which placeholders the user must fill;
- required running services;
- recommended execution order;
- what the automated tests verify;
- known limitations.

Keep it concise.

## Environment Validation

Before declaring completion, inspect the generated environment against the actual `.env.example` and backend configuration.

Report any required values that cannot be determined automatically.

Never fabricate credentials.

## Final Validation

Actually run as much validation as possible.

At minimum verify:

```text
collection JSON is valid
environment JSON is valid
all request URLs resolve to real backend routes
variables are correctly referenced
Postman scripts contain valid JavaScript
no fake endpoints exist
no secrets are committed
```

If Postman CLI is available, run the collection with it.

If Postman CLI is unavailable, perform equivalent static validation and clearly report that limitation.

## Final Result

The final repository should contain:

```text
postman/
├── Prysm.postman_collection.json
├── Prysm.postman_environment.json
└── README.md
```

The collection should allow me to open Postman, select the environment, provide only genuinely required secrets/configuration, and run the backend tests with automatic ID/token chaining.

Do not modify backend behavior just to make Postman tests pass.

If the backend itself has a real bug discovered during testing, report it separately instead of hiding it with a weak test.

Finish by reporting:

```text
Endpoints discovered:
Requests generated:
Automated tests:
Security tests:
AI workflow:
RAG workflow:
Validation result:
Missing environment values:
Backend issues discovered:
```