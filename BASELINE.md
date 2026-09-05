# PHASE 0 — BASELINE & ARCHITECTURE AUDIT

## Mission

Understand the current Prysm implementation before changing it.

Inspect the repository and trace the real data → AI → backend → frontend flow.

## Focus

Identify:

* what currently works
* what is duplicated or unnecessary
* where responsibilities are mixed
* how the dataset currently flows through the system
* how rules, anomaly detection, graph/GNN, family analysis and reasoning currently work
* how graph findings reach the frontend
* how PostgreSQL is currently being used
* what should be preserved, refactored, replaced or removed

## Direction

Do not redesign from assumptions.

Use the current codebase to determine the cleanest implementation that satisfies the project requirements.

Do not implement major changes yet.

## Deliverable

Produce a concrete migration/implementation map with exact repository locations and dependencies.

Update the project memory/state file with the findings and current starting point.

STOP when the audit is complete.
