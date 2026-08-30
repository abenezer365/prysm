# PRYSM INTELLIGENCE — FRONTEND MASTER IMPLEMENTATION PROMPT

## 0. ROLE

You are the primary frontend engineering agent for **Prysm Intelligence**, a financial-intelligence and fraud/AML analysis application.

You are working inside a repository where:

- The AI Engine is already implemented.
- The backend is already implemented to a meaningful degree.
- The frontend `client/` directory is currently blank/empty.
- `BACKEND_API.md` is the current frontend-facing backend contract.
- The browser must communicate with the backend only. It must never call the AI Engine or RAG services directly.
- The frontend stack is **React + JavaScript + Tailwind CSS**. **Do not use TypeScript.**

Your job is to build the complete frontend foundation and implementation in a way that is realistic, scalable, maintainable, fast, and easy for another coding agent to continue.

Do not build a generic modern SaaS template.
Do not build a flashy “AI startup landing page”.
Do not over-animate the interface.
Do not introduce unnecessary visual effects merely because they are popular.

The product should feel like a serious research/intelligence platform with excellent UX, strong information hierarchy, mature visual design, and restrained technology aesthetics.

---

# 1. PRIMARY SOURCE OF TRUTH

Before implementing anything:

1. Read `BACKEND_API.md` completely.
2. Read the existing backend OpenAPI/API documentation if available through the repository.
3. Inspect the repository structure and existing assets.
4. Identify the existing Prysm logo and integrate it appropriately.
5. Do not invent existing backend capabilities when the contract does not provide them.
6. Where the frontend requires a backend capability that does not currently exist, document and specify the missing endpoint instead of silently faking the feature.

The frontend must be designed around the actual backend contract.

The current backend base URL is:

`http://127.0.0.1:4000/api/v1`

Realtime chat URL:

`ws://127.0.0.1:4000/api/v1/ws/chat`

Protected requests use:

`Authorization: Bearer <accessToken>`

The backend is authoritative for:

- authentication
- authorization
- ownership
- security clearance
- trusted context
- sensitive-data access

Never infer security clearance or permission from frontend state alone.

---

# 2. PRODUCT IDENTITY

Primary product name:

**Prysm Intelligence**

Contextual names such as **Prysm AI** or **Prysm IO** may appear where appropriate, especially in documentation, technical contexts, or branding language, but the primary public product identity is Prysm Intelligence.

The brand should communicate:

- intelligence
- financial awareness
- research
- trust
- controlled access
- evidence
- relationships
- analysis
- precision
- calm confidence

Avoid:

- cyberpunk styling
- neon hacker aesthetics
- excessive glowing elements
- robot imagery
- generic “AI brain” illustrations
- excessive glassmorphism
- excessive gradients
- noisy particle backgrounds
- fake futuristic dashboards

---

# 3. DESIGN PHILOSOPHY

The interface should combine:

- Apple-inspired clarity and discipline
- mature enterprise/research tooling
- subtle old-school operational-system character
- strong typography
- excellent readability
- restrained motion
- high information density where useful
- generous spacing where content needs focus
- very clear interaction states
- professional financial/research aesthetics

The UI should feel like a product that could realistically belong to a serious research organization.

The goal is not visual novelty.
The goal is **trustworthy, memorable, usable intelligence software**.

Prioritize:

1. UX
2. readability
3. information hierarchy
4. speed
5. consistency
6. accessibility
7. responsiveness
8. visual polish

---

# 4. COLOR SYSTEM

Use a global design-token system through CSS variables.

Core suggested palette:

- `#00614c`
- `#1d561a`
- `#317227`
- `#4da53b`
- `#acd1a9`

Combine these with monochrome neutrals and appropriate status colors.

Do not hard-code theme colors throughout individual components.

Create centralized tokens for at least:

- page background
- surface
- elevated surface
- text primary
- text secondary
- text muted
- border
- accent
- accent strong
- accent soft
- success
- warning
- danger
- info
- focus ring
- overlay
- shadow

Theme changes should primarily occur by changing variables rather than rewriting components.

Support multiple visual themes from the beginning, but keep the theme system restrained and useful.

At minimum support a polished light and dark appearance, with architecture allowing additional themes later.

---

# 5. TYPOGRAPHY

Typography must be bold, weighted, readable, and structured.

Use a professional sans-serif system with strong hierarchy.

Create explicit type tokens/styles for:

- display
- page title
- section title
- card title
- body
- body strong
- metadata
- labels
- captions
- code/technical text
- numerical/statistical values

Numbers and financial figures should be visually easy to scan.

Avoid tiny unreadable text.

---

# 6. MOTION

Motion must communicate state, hierarchy, and continuity.

Use animation sparingly.

Allowed:

- subtle hover transitions
- sidebar expansion
- menu expansion
- modal transitions
- loading indicators
- page transition continuity
- graph interaction
- chat open/close

Avoid:

- unnecessary parallax
- excessive scroll-trigger animations
- animated gradients
- constant movement
- decorative particle effects
- bouncing UI
- excessive spring animations

The application should feel fast even when backend operations take time.

Always distinguish:

- instant UI feedback
- loading state
- processing state
- success state
- failure state

---

# 7. TECH STACK

Use:

- React
- JavaScript
- Tailwind CSS
- React Router or a similarly established React routing solution
- sensible lightweight libraries where they meaningfully improve the application

Do not use TypeScript.

No `.ts` or `.tsx` files.

Use reusable React components and hooks.

Prefer simple, explicit architecture over excessive abstraction.

Use an API client layer instead of scattering raw fetch calls across components.

---

# 8. APPLICATION ARCHITECTURE

Create a scalable structure similar to:

```text
client/
├── public/
│   ├── assets/
│   └── ...
├── src/
│   ├── app/
│   ├── assets/
│   ├── components/
│   │   ├── common/
│   │   ├── navigation/
│   │   ├── charts/
│   │   ├── intelligence/
│   │   ├── graph/
│   │   ├── chat/
│   │   └── forms/
│   ├── layouts/
│   │   ├── PublicLayout.jsx
│   │   └── AdminLayout.jsx
│   ├── pages/
│   │   ├── public/
│   │   ├── auth/
│   │   └── admin/
│   ├── services/
│   │   ├── api/
│   │   ├── auth/
│   │   └── chat/
│   ├── hooks/
│   ├── context/
│   ├── store/
│   ├── utils/
│   ├── config/
│   ├── styles/
│   └── main.jsx
├── docs/
├── package.json
└── ...
```

You may adjust the structure if a better architecture emerges, but keep responsibilities obvious.

The structure must make future page additions easy.

---

# 9. ROUTING ARCHITECTURE

Build explicit routing from the beginning.

Public routes should include at least:

- `/`
- `/about`
- `/contact`
- `/docs`
- `/research`
- `/research/ethical-ai`
- `/research/fraud-detection`
- `/research/modeling`
- `/report`
- `/report/bug`
- `/report/resolution-guide`
- `/beta`
- `/contribute`
- `/terms`
- `/privacy`
- `/academy`
- `/academy/data-science`
- `/academy/python`
- `/academy/opportunities`
- `/academy/institutions`
- `/academy/rules`
- `/intelligence`
- `/intelligence/models`
- `/intelligence/data`
- `/intelligence/playground`
- `/login`
- `/request-access`

Authenticated application routes should include at least:

- `/app`
- `/app/dashboard`
- `/app/search`
- `/app/users`
- `/app/rag`
- `/app/news`
- `/app/activity`
- `/app/gnn-maze`
- `/app/settings`
- `/app/investigations`
- `/app/investigations/:id`
- `/app/subjects/:id`

Architecture must make it easy to add future routes.

Do not make every future route fully functional if the backend does not support it. Instead create appropriate shell states and document dependencies.

---

# 10. PUBLIC HEADER

The public website should have a serious, elegant, expandable category header.

Core concept:

A compact header contains the Prysm logo and primary categories.

Categories expand on hover where appropriate and remain usable on touch devices through click/tap.

Primary categories:

- Research
- Report
- Academy
- Intelligence

Authentication CTA:

- Get Started

The header should not become a giant mega-menu that overwhelms the page.

Use grouped navigation, clear labels, and strong hierarchy.

The logo routes to `/`.

---

# 11. HOME PAGE

The home page is the primary pitch and must receive exceptional design attention.

It should immediately explain what Prysm Intelligence is without using marketing fluff.

Hero requirements:

- Strong product identity
- Simple approximately-57-character positioning statement
- Clear explanation of the product
- Strong primary CTA
- Secondary path to learn more/about
- Prysm Intelligence visual identity

The exact hero statement can remain easy to edit from a centralized configuration/content file.

Do not make the wording a rigid hard-coded design constraint.

Home page sections:

1. Hero
2. What Prysm Intelligence does
3. About/why it exists
4. Interactive GNN relationship demonstration using safe demo data
5. How Prysm works
6. Intelligence capabilities
7. Fraud/AML analysis concepts
8. FAQ
9. Beta tester testimonials
10. CTA
11. Large research-organization-style footer

The GNN demo must clearly use synthetic/demo data and must not expose protected backend information to public users.

The GNN visualization should be useful, understandable, and visually restrained.

---

# 12. ABOUT PAGE

Include:

- origin of the project
- why the idea was created
- problem statement
- financial/fraud intelligence motivation
- project philosophy
- who built it
- founder/developer presentation for the two project builders
- placeholder photography where actual images are not yet supplied
- acknowledgements/special thanks
- project reflections
- future vision

Keep copy easy to update.

Do not fabricate personal biographies.

Use clearly marked editable placeholders where exact information is not known.

---

# 13. CONTACT PAGE

Brand/company association:

**Abyssinia Associates**

Include:

- company introduction
- social platform placeholders/configuration
- editable email/contact configuration
- contact form
- success/error states

The final contact destination can be edited in the codebase.

Do not hard-code fictional social links.

---

# 14. DOCS PAGE

Create a serious, technical documentation experience.

It should feel closer to documentation from a research/engineering organization than a normal marketing page.

Cover:

- what Prysm is
- system overview
- architecture
- frontend/backend relationship
- AI Engine relationship
- RAG relationship
- authentication
- authorization
- security clearance concept
- investigations
- subjects
- evidence
- graph intelligence
- search
- chat
- data representation
- inputs
- outputs
- limitations
- integration
- API usage
- examples where appropriate
- development structure
- contributor guidance

Provide a well-positioned GitHub repository link.

Do not make GitHub the primary hero CTA.

The docs architecture should be expandable into multiple documentation sections/pages later.

---

# 15. RESEARCH SECTION

Research should communicate that Prysm is a research/intelligence project, not merely a dashboard.

At minimum include:

## Ethical AI

Explain:

- ethical AI principles
- responsible data use
- consent concepts
- transparency
- limitations
- human oversight
- responsible interpretation
- risk of false positives
- explainability
- access control
- provenance

Do not make unsupported claims such as “bias-free AI” or “perfect fraud detection”.

## Fraud Detection

Describe the general purpose of live fraud detection and intelligence workflows without exposing protected information.

## Modeling

Explain high-level modeling concepts and the relationship between model outputs and investigative decisions.

Additional research pages should be easy to add.

---

# 16. REPORT SECTION

Include:

- Bug report
- Resolution guide
- Beta tester information
- Become a contributor
- Terms of agreement
- Privacy policy

Where backend functionality does not exist yet, provide a polished informational/form shell and document required backend integrations.

---

# 17. ACADEMY SECTION

Create an education-focused section for:

- Data Science Bootcamp
- Python Programming
- Opportunities
- Institutions
- Rules and Regulations

Keep it visually connected to Prysm but distinct enough to feel educational.

Architecture should support courses/content being expanded later.

---

# 18. INTELLIGENCE SECTION

Include public-facing information/preview pages for:

- Models
- Data Representation
- Playground

The public playground must not expose unauthorized production data.

Use synthetic or explicitly safe demonstration data where a demo is needed.

---

# 19. AUTHENTICATION

Login route:

`POST /auth/login`

Request:

```json
{
  "email": "...",
  "password": "...",
  "deviceInfo": "..."
}
```

Implement a proper authentication flow using backend-issued access/refresh tokens according to the backend's actual response.

Also support:

- `/auth/me`
- logout
- current permissions
- current clearance

Relevant backend routes:

- `POST /auth/login`
- `POST /auth/logout`
- `GET /auth/me`
- `GET /me/permissions`
- `GET /me/clearance`

Never decode or invent authorization semantics purely on the frontend.

The frontend may use current permissions/clearance to shape the UI, but backend authorization is always authoritative.

---

# 20. REQUEST ACCESS FLOW

There is intentionally no unrestricted public self-registration.

Public users request access through:

`POST /applications`

Current backend request:

```json
{
  "email": "...",
  "displayName": "...",
  "reason": "..."
}
```

The current contract only exposes these fields.

The UI should therefore initially represent the access request professionally using the supported fields.

The desired broader concept may later require fields/documents such as:

- profession
- organization
- role
- authorization/clearance evidence
- supporting letter/document
- reason for access

Do not pretend document upload/review exists if the backend does not support it.

Create a backend-gap document specifying the additional endpoint/schema needed for a full access-review workflow.

---

# 21. CLEARANCE MODEL

Clearance levels:

1. Restricted
2. Confidential
3. Secret
4. Top Secret

Higher number = higher clearance.

The backend provides authoritative live clearance information.

Frontend behavior should remain simple:

- show current level clearly
- disable/hide controls when permission data says access is unavailable
- explain restricted states without leaking protected details
- never rely on client-side numerical logic as the security boundary

The design should make clearance visible without making it visually theatrical.

---

# 22. ADMIN / APPLICATION SHELL

Authenticated users enter a separate application experience.

There is **no public website footer** inside the application shell.

The application should feel like a serious operational/research environment.

## Sidebar

Include:

- profile image/avatar
- name
- clearance
- navigation

Primary navigation:

- Dashboard
- Search
- Users
- RAG
- News
- Activity Log
- GNN Maze
- Investigations
- Settings

Design navigation so future sections can be added without redesigning the shell.

## Header

Include controls for:

- Home
- Back
- Reload
- Forward
- current time
- theme
- settings
- layout options

The time should be useful and visually understated.

Browser-like navigation controls should operate sensibly inside the SPA where possible.

Do not create fake functionality for controls that cannot meaningfully work.

---

# 23. DASHBOARD

The dashboard is the main operational landing page after authentication.

It should feel like a real intelligence workspace, not a collection of random charts.

Include meaningful modules such as:

### System/Model Analytics

Show available model metadata from:

`GET /models`

Where real metrics do not exist, do not fabricate live metrics. Use appropriate empty states or clearly marked derived/demo summaries.

### Security Distribution

Show available user distribution only if the backend provides authorized data.

If it does not, create a backend-gap requirement rather than inventing data.

### Investigation/Search Entry

A clear route into search and investigations.

### Top Suspects

Use real authorized subject/investigation data where available.

Do not expose sensitive subjects merely for visual completeness.

### Relationship Intelligence Preview

A small, meaningful GNN graph preview linking into the GNN Maze.

### Recent Activity

Show recent activity only when backed by an authorized API.

### System Health

Use available health endpoints where appropriate.

Potential endpoints:

- `/health`
- `/health/ready`
- `/health/dependencies`

Only expose dependency health details to users with the appropriate permission.

The dashboard should intentionally “sensitize” users to deeper pages without overwhelming them.

---

# 24. SEARCH

Backend:

`POST /search`

Request:

```json
{
  "query": "...",
  "limit": 20
}
```

Implement:

- search input
- query state
- loading state
- result cards/table
- pagination architecture even though `nextCursor` is currently null
- no-results state
- backend-error state
- retry state
- link to subject details

Do not expose sensitive profile data in basic search results.

---

# 25. SUBJECT PROFILE

Backend:

`GET /subjects/:id`

Sensitive profile:

`GET /subjects/:id/profile`

The basic subject page should handle redacted summaries cleanly.

Sensitive information should appear only when the backend allows it.

For clearance-restricted data:

- show a clear access state
- explain that additional authorization is required
- never reveal the hidden data through UI metadata, previews, counts, or browser state

---

# 26. INVESTIGATIONS

Available backend routes:

- `POST /investigations`
- `GET /investigations`
- `GET /investigations/:id`
- `POST /investigations/:id/analyze`
- `GET /investigations/:id/analysis-runs/:runId`

Investigation creation requires:

```json
{
  "subjectId": "uuid",
  "title": "optional",
  "purpose": "optional",
  "cutoffAt": "ISO-8601 UTC",
  "predictionHorizonStart": "optional",
  "predictionHorizonEnd": "optional"
}
```

The analysis action returns a run identifier.

Prevent duplicate UI submissions.

Use clear processing states.

Support immutable analysis-run presentation.

Do not claim that an analysis is complete before the backend reports it.

---

# 27. GNN MAZE

Backend:

`GET /graph/subjects/:id/subgraph`

Parameters:

- `cutoffAt?`
- `maxHops` 1–3
- `maxNodes` 1–250

Build a serious graph exploration experience.

Goals:

- show relationships
- make graph structure understandable
- highlight relevant nodes/edges
- allow focused exploration
- avoid visual clutter
- preserve performance

Use synthetic demo data for public visualization.
Use backend data for authorized application visualization.

Graph controls should be purposeful.

Do not turn the graph into a decorative animation.

---

# 28. EVIDENCE

Backend:

`GET /evidence/:id`

Create reusable evidence reference UI.

The UI should communicate:

- evidence identity
- provenance
- availability
- related investigation/subject where authorized
- limitations

Never display protected evidence unless returned by the backend for the authenticated user.

---

# 29. RAG

Public RAG:

`POST /chat/public`

Authorized RAG:

`POST /chat/authorized`

Authorized request:

```json
{
  "question": "...",
  "investigationId": "uuid",
  "conversationId": "optional-uuid"
}
```

Public chat accepts only the intended fields and must not allow the client to inject authenticated/context/clearance/accessScope values.

The backend builds authorized context.

Frontend must therefore treat backend responses as authoritative.

---

# 30. PRYSM AI CHATBOT

Every page should provide access to the Prysm AI assistant as a compact bottom-corner interaction.

Do not make the chatbot dominate the screen.

## Unauthenticated mode

Use:

`POST /chat/public`

The assistant can answer public/general questions such as:

- What is Prysm Intelligence?
- What does the platform do?
- What is GNN analysis?
- What is ethical AI?
- Who built Prysm?
- How does access work?

## Authenticated mode

Use:

`POST /chat/authorized`

Only when the user has appropriate authorization and an investigation context.

The assistant should be context-aware without the frontend manually sending fabricated security context.

## WebSocket mode

WebSocket endpoint:

`ws://127.0.0.1:4000/api/v1/ws/chat`

Expected flow:

1. Connect.
2. Receive `ready`.
3. Send `{"type":"authenticate","accessToken":"..."}`.
4. Wait for `authenticated`.
5. Send question + investigation ID + optional conversation ID.
6. Handle `done`.
7. Handle sanitized `error`.

Implement a reusable chat transport abstraction so HTTP and WebSocket behavior do not become tangled with presentation components.

The chat UI should show:

- question
- answer
- sources
- request state
- connection state
- retry capability
- conversation state
- clear distinction between public and authorized context

Never put credentials or unrestricted context into browser-visible metadata.

---

# 31. ERROR HANDLING

Backend errors have this structure:

```json
{
  "error": {
    "code": "...",
    "message": "...",
    "details": {},
    "requestId": "uuid"
  }
}
```

Every response has:

`x-request-id`

Handle at least:

- `400`
- `401`
- `403`
- `404`
- `409`
- `413`
- `429`
- `502`
- `503`

Create consistent UX for:

- validation errors
- expired authentication
- insufficient permission
- unavailable resource
- duplicate/conflict actions
- oversized uploads if later supported
- rate limiting
- upstream AI/RAG failure
- backend unavailable

Where useful, surface the request ID for support/debugging.

Do not expose internal stack traces.

---

# 32. LOADING / EMPTY / ERROR STATES

Every data-backed page needs deliberate states.

At minimum:

- loading
- success
- empty
- permission denied
- not found
- backend unavailable
- retry

Do not simply leave blank white cards when data is unavailable.

Make states visually consistent across the application.

---

# 33. RESPONSIVENESS

Build responsive behavior from the beginning.

Desktop is important because the platform is intelligence/dashboard oriented, but mobile/tablet layouts must remain functional.

Public:

- fully responsive
- expandable navigation becomes mobile-friendly menu
- readable sections

Admin:

- sidebar collapses/reduces sensibly
- charts remain usable
- graph tools remain accessible
- tables become scrollable or structurally adaptive

Do not rely on horizontal overflow for the entire application.

---

# 34. ACCESSIBILITY

Include:

- keyboard navigation
- focus states
- semantic buttons/links
- accessible form labels
- meaningful aria labels where required
- sufficient color contrast
- no color-only status communication
- reduced-motion consideration

Accessibility should be structural, not an afterthought.

---

# 35. PERFORMANCE

Optimize for the perception and reality of speed.

Use:

- code splitting where useful
- lazy-loaded routes where useful
- memoization only where it solves a real problem
- efficient graph rendering
- controlled data fetching
- request cancellation where appropriate
- cached reusable state where appropriate

Avoid premature complexity.

---

# 36. API CLIENT

Centralize backend communication.

Create a service layer capable of:

- base URL configuration
- authorization headers
- request IDs
- standardized parsing
- standardized errors
- token/session management
- retries only where safe
- logout on irrecoverable authentication failure

Do not write raw fetch logic in every page.

Suggested organization:

```text
services/api/
  client.js
  auth.js
  search.js
  subjects.js
  investigations.js
  graph.js
  evidence.js
  chat.js
  models.js
  audit.js
  health.js
  applications.js
```

Adapt names if a better structure is found.

---

# 37. STATE MANAGEMENT

Do not introduce a heavyweight state library unless the application actually benefits from it.

Use a clear separation between:

- authentication/session state
- user/permission/clearance state
- UI state
- server/API state
- chat state
- theme state

Keep server state from becoming duplicated across many components.

---

# 38. SECURITY RULES FOR FRONTEND

Never:

- store passwords
- log tokens
- expose restricted data in console logs
- fabricate authorization
- bypass backend permission checks
- send manually injected clearance/context fields
- expose private API credentials
- directly call AI Engine or RAG services

Remember:

**The browser is not a security boundary.**

Frontend access gates are UX only.

---

# 39. FOOTER

Every public page should share the same broad footer component.

The admin application does not use this footer.

The footer should feel like an established research organization.

It should explicitly expose important public routes and categories, such as:

- About
- Research
- Ethical AI
- Fraud Detection
- Modeling
- Intelligence
- Models
- Data
- Playground
- Academy
- Docs
- Report
- Contact
- Beta
- Contribute
- Terms
- Privacy
- Get Started

Include:

- Prysm Intelligence identity
- Abyssinia Associates association where appropriate
- editable contact information
- editable social links
- legal links
- GitHub link
- concise research-oriented description

Avoid copying the visual language of any specific existing company.

---

# 40. DATA SAFETY IN PUBLIC DEMOS

Public pages must use:

- synthetic data
- static demo datasets
- explicitly safe information

Never accidentally connect public demo components to protected application endpoints in a way that exposes confidential information.

Clearly distinguish:

- public demonstration
- authenticated intelligence
- restricted information

---

# 41. PLACEHOLDER CONTENT

Where final content/assets are not yet available:

- create polished placeholders
- make replacements easy
- avoid lorem ipsum where possible
- identify editable configuration/content locations

Use placeholder imagery for:

- founders/developers
- testimonials
- research illustrations
- other areas requiring eventual real imagery

Do not invent false claims, organizations, statistics, testimonials, credentials, partnerships, or achievements.

---

# 42. CONTENT ARCHITECTURE

Keep major copy and editable marketing content reasonably centralized.

Avoid scattering large blocks of copy throughout deeply nested JSX.

Potential pattern:

```text
src/config/
src/content/
```

This should make it easy for the project owners to edit:

- hero text
- company info
- social links
- testimonials
- founder details
- legal copy
- navigation labels
- feature descriptions

---

# 43. BACKEND GAPS

The backend contract explicitly states that some requested application capabilities are not implemented.

The frontend work must include a document such as:

`client/BACKEND_API_GAPS.md`

For each missing capability document:

- feature name
- required endpoint
- HTTP method
- authorization requirement
- request schema
- response schema
- frontend consumer
- reason it is required
- implementation recommendation
- current status

Known backend gaps include, but are not necessarily limited to:

- dashboards
- application review
- user mutation
- refresh/password reset/change
- investigation update
- investigation timeline
- investigation feedback
- investigation export
- model downloads
- richer admin/user management

Do not make up a working backend implementation.

Where implementation is reasonable and clearly scoped, prepare a backend implementation specification for the backend agent rather than silently skipping the feature.

---

# 44. FRONTEND DOCUMENTATION FILES

This requirement is mandatory.

Create persistent Markdown documentation inside `client/` so another coding agent can continue the work after a context/usage limit.

At minimum create:

### `client/FRONTEND_CONTEXT.md`

Contains:

- current architecture
- design decisions
- route map
- implementation status
- major components
- integration status
- known problems
- completed work
- next recommended tasks

### `client/FRONTEND_ARCHITECTURE.md`

Contains:

- folder architecture
- component boundaries
- page architecture
- layout architecture
- routing
- state architecture
- API architecture
- chat architecture

### `client/FRONTEND_DESIGN_SYSTEM.md`

Contains:

- colors
- CSS variables
- typography
- spacing
- cards
- buttons
- forms
- tables
- badges
- alerts
- navigation
- states
- themes

### `client/BACKEND_API_GAPS.md`

Contains all backend capabilities required by the frontend but not currently exposed.

### `client/IMPLEMENTATION_STATUS.md`

Maintain a practical checklist of completed/in-progress/pending work.

### `client/DECISIONS.md`

Record meaningful architecture/design decisions and their rationale.

These documents are continuity tools for future coding agents.

Update them as implementation evolves.

---

# 45. CODING AGENT LOG / CONTINUITY

As major work is completed, update the documentation.

Do not write meaningless logs like:

“Added button.”

Instead record meaningful engineering context such as:

- which components were introduced
- what backend endpoint they use
- what assumptions were made
- what remains incomplete
- why an architecture decision was taken
- where a future agent should continue

A future coding agent should be able to open the `client` documentation and understand the state of the project without reading the entire conversation.

---

# 46. QUALITY BAR

Before considering any implementation complete, verify:

### Functional

- routes work
- navigation works
- forms validate
- API calls use the correct endpoint
- authentication behavior is coherent
- protected routes are protected in the UI
- loading/error/empty states exist
- chat works through the intended backend interface

### Visual

- no obvious unstyled browser defaults
- consistent spacing
- consistent typography
- consistent colors
- consistent component states
- proper responsive behavior
- public and admin shells feel distinct

### UX

- users always understand where they are
- actions provide immediate feedback
- errors are understandable
- permissions are communicated clearly
- destructive/important actions are deliberate
- navigation is discoverable

### Engineering

- no TypeScript
- no duplicated API logic everywhere
- no giant monolithic component
- no random hard-coded theme colors
- no fake security
- no direct AI Engine/RAG calls
- no unnecessary dependencies
- no abandoned prototype code

---

# 47. VISUAL DETAILS THAT MATTER

The product should communicate meaning through small details.

Use restrained details such as:

- financial-style numeric formatting
- subtle clearance badges
- case/investigation identifiers
- structured metadata rows
- evidence/provenance indicators
- meaningful timestamps
- quiet operational statuses
- understated separators
- deliberate table density
- graph legends that actually explain relationships
- small references to Ethiopian/Abyssinian visual patterns where they fit naturally

These details should feel discovered rather than pasted on.

Do not turn Ethiopia/Abyssinia into a decorative theme everywhere.

---

# 48. WHAT NOT TO DO

Do not:

- use TypeScript
- make the interface look like a generic AI SaaS landing page
- overuse animation
- use emojis in application UI copy unless explicitly requested
- expose restricted data
- invent backend endpoints as though they exist
- make fake dashboards with made-up live statistics
- claim impossible model accuracy
- create security mechanisms exclusively in React
- call AI Engine/RAG directly from the browser
- hard-code user-specific security information
- make every section rounded-card-heavy
- fill every empty space with decoration
- use meaningless charts
- use fake testimonials presented as real
- make the product unnecessarily complicated

Also do not use an em dash (`—`) in generated interface/product copy. Prefer commas, periods, colons, or parentheses.

---

# 49. IMPLEMENTATION ORDER

Implement the application in this order unless repository realities require a better sequence:

## Phase 1 — Foundation

- initialize React application
- Tailwind setup
- routing
- CSS variables/theme system
- typography system
- API client
- error model
- basic shared UI primitives
- documentation files

## Phase 2 — Public Shell

- header
- hover/click category navigation
- footer
- shared page container
- mobile navigation
- theme switching

## Phase 3 — Public Pages

- home
- about
- contact
- docs
- research
- report
- academy
- intelligence
- legal/support pages

## Phase 4 — Authentication

- login
- request access
- session handling
- protected routing
- permissions
- clearance
- logout

## Phase 5 — Application Shell

- sidebar
- admin header
- responsive shell
- profile/clearance presentation
- navigation
- application theme/layout controls

## Phase 6 — Core Intelligence Pages

- dashboard
- search
- subjects
- investigations
- evidence
- GNN Maze
- models
- RAG/chat
- activity/audit where backend permits

## Phase 7 — Advanced Integration

- WebSocket chat
- richer investigation UX
- deeper graph interactions
- system health
- backend-gap implementations when backend work is added

## Phase 8 — Polish

- responsive refinement
- performance
- accessibility
- visual consistency
- empty/error/loading states
- final documentation

---

# 50. DO NOT WAIT FOR PERFECT CONTENT

The owners will later refine individual pages by giving those pages additional attention and weight.

Therefore:

- build all major routes
- establish the complete architecture
- create strong first-pass UI
- make content easy to edit
- leave intentional extension points
- do not block implementation because final copy is unknown

When exact content is unknown, use high-quality editable placeholder content rather than asking the owner to specify every sentence before implementing the page.

---

# 51. BACKEND IMPLEMENTATION REQUESTS

When you reach a frontend feature that the backend cannot currently support:

1. Do not fake it.
2. Add the requirement to `BACKEND_API_GAPS.md`.
3. Specify the proposed API contract.
4. Identify the frontend route/component that consumes it.
5. Clearly label it as `BACKEND REQUIRED`.
6. Continue building the surrounding frontend so the application remains useful.

If the repository workflow allows backend modifications, create the backend implementation task/specification explicitly and make it easy for a backend agent to implement.

Never silently change the backend contract without documenting it.

---

# 52. API DETAILS CURRENTLY KNOWN

The current contract exposes:

### Public

- `GET /health`
- `GET /health/ready`
- `POST /applications`
- `POST /auth/login`
- `POST /chat/public`

### Authenticated

- `POST /auth/logout`
- `GET /auth/me`
- `GET /me/permissions`
- `GET /me/clearance`

### Subject/Search

- `POST /search`
- `GET /subjects/:id`
- `GET /subjects/:id/profile`

### Investigation

- `POST /investigations`
- `GET /investigations`
- `GET /investigations/:id`
- `POST /investigations/:id/analyze`
- `GET /investigations/:id/analysis-runs/:runId`

### Graph

- `GET /graph/subjects/:id/subgraph`

### Evidence

- `GET /evidence/:id`

### Authorized Chat

- `POST /chat/authorized`
- `WS /ws/chat`

### RAG Administration

- `POST /rag/ingest`

### Models

- `GET /models`

### Audit

- `GET /audit/events`

Protected permissions and clearance requirements must come from the actual API contract.

---

# 53. RESPONSE/PAGINATION PATTERN

List/search endpoints generally return:

```json
{
  "data": [],
  "page": {
    "nextCursor": null,
    "limit": 20
  }
}
```

Build pagination architecture even though `nextCursor` is currently null.

Do not build pagination that assumes page numbers if the backend is cursor-oriented.

---

# 54. DATE/TIME

Backend dates are ISO-8601 UTC strings.

Render human-friendly local time while preserving access to exact timestamps.

The application header can display current local client time.

Operational timestamps should remain unambiguous.

---

# 55. FINAL ENGINEERING INSTRUCTION

Build Prysm Intelligence as a coherent product, not a pile of pages.

Every component should have a reason to exist.
Every route should have a clear role.
Every visual pattern should repeat intentionally.
Every API call should map cleanly to backend capabilities.
Every restricted state should be communicated safely.
Every unfinished backend dependency should be documented.
Every major implementation decision should be recorded for the next coding agent.

The result should feel:

**calm, intelligent, trustworthy, operational, research-driven, elegant, slightly old-school, highly usable, and distinctly Prysm.**

Do the work directly in the repository.
Do not stop after scaffolding.
Build the actual frontend foundation and first-pass implementation.

When complete, update the continuity Markdown files so another coding agent can continue immediately.
