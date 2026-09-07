# Phase 6 state: content and interface finalization

**Status:** Frontend contract repair and visual finalization pass completed on 2026-09-06. The Phase 1 to 5 analytical and backend systems were not redesigned.

## Frontend architecture

The client remains a React and Vite single-page application in `client/src`. Public routes use `PublicLayout`; authenticated investigator and administration routes use `AppLayout`; access continues to be enforced by `AuthContext` and the backend. API calls remain centralized in `client/src/services/api.js`.

The final visual layer is `client/src/styles/phase6.css`, loaded after the earlier compatibility styles. It establishes a strict black, near-black, white, and controlled-gray palette, minimal shadows, large geometric headings, generous viewport-oriented spacing, animated navigation underlines, and reduced-motion fallbacks. `client/src/components/MotionSystem.jsx` owns GSAP route and scroll entrances, while the live graph uses a bounded GSAP reveal for nodes and relationships.

## Phase 5 API alignment

- Ranked suspect requests now include the required `cutoffAt` and bounded `limit` query values.
- Graph requests now send only the required cutoff. Retired browser-controlled hop and node overrides were removed.
- Investigation reports read `intelligence_components`, with compatibility fallback for historical stored results.
- The API client exposes current intelligence and investigation conversation history endpoints.
- The operational dashboard no longer displays invented subject, relationship, model, or training-row totals. Its summary cards use live response values.
- Top suspect rows now consume `entity_key`, `subjectId`, `overall_risk`, `risk_level`, and `rank`, and state explicitly that the value is an attention score rather than a fraud probability.

## Investigator and graph experience

The core path remains dashboard to ranked lead or search, subject, investigation, analysis, evidence, graph, and explanation. Graph controls request an explicit evidence cutoff and render the backend-owned bounded graph. Nodes and edges carrying `attention: review` or the backend red highlight marker use the suspicious treatment; the UI does not calculate its own suspicious threshold.

Investigation reports expose overall attention, evidence confidence, component-level reasons, evidence measurements, and explicit model interpretation text. Rules and network component descriptions match the current Phase 2 vocabulary.

## RAG and conversation

Public chat retains public-only context, now follows new messages with smooth scrolling, gives a conversational thinking state, animates answer arrival, preserves sources and request IDs, and respects reduced-motion preferences.

Authorized investigation chat is available at `/app/investigations/:id/chat`. It restores permitted conversation history, posts through `/chat/authorized`, maintains the returned conversation ID, renders sources, and labels responses as generated explanations rather than evidence.

## Content and documentation

The public site keeps the evidence-first ethical position from `resources/Contents_Source.md`: source records, derived intelligence, evidence, explanation, human judgment, authorization, minimization, and auditability remain separate concepts. The home statement now uses “Track the flow, Connect the dots, Expose the Fraud.” as a large, readable three-line composition. The existing documentation hub continues to publish representative endpoints and architecture boundaries; the complete developer contract remains `server/docs/API.md` and `server/docs/openapi.json`.

## Validation

From `client/`, `npm.cmd run build` succeeds with Vite 8.2.2. `npm.cmd run lint` completes with zero errors and seven non-blocking warnings in pre-existing hook helpers and Fast Refresh context organization. Forty-eight benchmark, AI search, and graph checks pass; all 25 backend tests pass. The real workflow passes 31 live checks across PostgreSQL, AI Phase 3, local RAG, HTTP, and WebSocket, including search, analysis, graph, evidence, explanation, and full-population ranking.

## Run commands

```powershell
cd client
npm.cmd ci
npm.cmd run dev
npm.cmd run build
npm.cmd run lint
```

Start the Phase 5 service stack separately using `server/scripts/start-local.ps1`; the client defaults to `http://127.0.0.1:4000/api/v1` and can be pointed elsewhere with `VITE_API_BASE_URL`.

## Known limitations

The Phase 5 limitations remain: first full-population ranking can take minutes, local LLM inference is deferred, list pagination is bounded without continuation, and CSV/PDF exports are not implemented. The authorized chat route is separate from the report route so investigation evidence remains visually distinct from generated prose. No production deployment target or hosted credentials are configured in this repository.

## Demonstration flow

Sign in, open Dashboard, select a ranked lead or search for a person, create/open an investigation, run analysis, review attention and component breakdown, verify evidence, inspect the red-marked graph context at the investigation cutoff, then open the investigation chat route and request a grounded explanation. Administrative users can review live operational state, users, access queues, RAG documents, audit history, news, reports, and contributor workflows from the same authenticated shell.
