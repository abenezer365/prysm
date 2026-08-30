# Frontend Decisions

## ADR-001: Session storage for access tokens

Access tokens use `sessionStorage`, limiting persistence beyond the current browser tab. Refresh-token persistence is intentionally absent because the backend contract does not provide a refresh operation or cookie contract.

## ADR-002: Backend-authoritative access

Permissions and clearance are loaded from live endpoints. The client never decodes token claims or uses numerical clearance as an authorization mechanism. UI checks only suppress futile or confusing requests.

## ADR-003: Explicit synthetic public graph

Public relationship visuals use a static, labeled synthetic network. Protected graph endpoints are never called from public routes.

## ADR-004: Honest unsupported states

Pages without backend support show polished explanatory states and reference the gap specification. They do not generate fake operational records or metrics.

## ADR-005: Central content map

First-pass public copy and navigation live in `src/config/content.js` to make owner edits straightforward. Bespoke pages remain separate where layout and information hierarchy warrant it.
