# Frontend Context

## Current architecture

The client is a Vite React application using JavaScript, React Router, Tailwind CSS, Lucide icons, and a CSS-variable design system. Public and authenticated experiences use separate layouts. All network traffic is centralized in `src/services/api.js` and targets only the backend API.

## Route map

Public routes cover home, about, contact, docs, research and its three subpages, report and support, beta, contribute, terms, privacy, Academy and its five subpages, Intelligence and its three subpages, login, and request access. Authenticated routes cover dashboard, search, users, RAG, news, activity, GNN Maze, settings, investigations, investigation detail, and subject detail.

## Completed

- Responsive public header with grouped desktop menus and mobile navigation
- Research-style footer, light/dark themes, centralized tokens and content
- High-attention home page with clearly labeled synthetic graph
- First-pass editorial public routes, about, docs, contact, bug, and access forms
- Access application API integration
- Session-scoped token handling, `/auth/me`, live permissions and clearance, logout
- Protected application shell, local time, meaningful browser navigation controls
- Backend-connected dashboard health/model metadata, search, subjects, sensitive profile, investigations, analysis, and audit
- Reusable public chat through `/chat/public`
- Consistent loading, empty, error, and permission states

## Integration notes

Login supports `accessToken` and `access.token` response shapes. Tokens are stored in `sessionStorage`, never logged, and removed on session bootstrap failure. Refresh is not implemented because the backend contract has no refresh endpoint. Authorized investigation chat and WebSocket transport are the principal next integration tasks.

## Next recommended tasks

1. Add an investigation-bound authorized chat panel and WebSocket fallback/transport.
2. Add the subject-to-investigation creation workflow and live graph controls.
3. Replace verified placeholders for builders, contacts, repository, and legal copy.
4. Add component and browser tests, then run an accessibility audit.

## August 2026 public-site overhaul

The public experience was substantially deepened after the initial foundation. The current information architecture is now defined in `src/config/publicRegistry.js`, with more than 50 meaningful discovery destinations represented across Research, Intelligence, Academy, Resources, Organization, and Reports. Home, About, and Documentation are tailored deep pages; registered subjects use editorial article and technical-reference layouts.

The current design direction uses institutional/editorial typography, compact Windows-era enterprise controls, Wikipedia-like article navigation, conventional blue knowledge links, tables, diagrams, timelines, restrained green identity, and small radii. `client/docs/` is now the detailed source of truth for the overhaul.

The reported public-chat outage was traced through the complete path. The frontend endpoint and payload were correct. The backend and RAG service were offline, and `RAG_API_KEY` was blank in both service environment files. `server/scripts/configure-local-rag-key.ps1` now configures matching secret values without printing them. Public chat has been live-verified through the backend, including sources, request IDs, conversation continuity, and frontend-origin CORS. See `docs/CHATBOT_INTEGRATION.md`.
