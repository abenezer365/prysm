# Prysm Remaining Work

## Phase 5 backend finalization ? current

Read [PHASE5_STATE.md](../PHASE5_STATE.md) and [the frontend API guide](../server/docs/API.md). The backend now runs JavaScript ESM, keeps PostgreSQL for operational state, removes analytical database copies with two applied forward migrations, and connects the selected Phase 3 engine to Phase 4 protected explanations. TypeScript build paths and obsolete ingestion/ticket implementations are removed. Earlier entries below are historical and do not describe the active backend.

Next: Phase 6 frontend adoption and UI/content work, using the finalized 66-endpoint HTTP contract and WebSocket guide. Local LLM inference and the large generator remain deferred. No Phase 6 UI work was done.


Completed implementation history is retained in `memory.md`. Only genuine remaining work appears here.

## Next step in the six-phase improvement project

- [ ] Implement `P5_Backend_Cleanup_Finalization.md` from [the Phase 4 handoff](../PHASE4_STATE.md). Connect trusted intelligence results to the protected explanation endpoint.
- [ ] When the user has downloaded local model weights, select/verify the runtime and connect it as documented in `chatbot/local_llm/README.md`; explicitly deferred in Phase 4.
- [ ] In the later integration phase, connect the new pure intelligence domain to the backend/GNN Maze deliberately; the current HTTP service still uses the archived v1 engine.
- [ ] After all six phases, build the requested larger synthetic generator with reviewed labels and richer scenarios.

## Production operations

- [ ] Deploy behind TLS with managed secrets, backup/restore, monitoring, retention, and incident procedures.
- [ ] Move analysis to a durable queue/outbox with retries, idempotency, recovery, and observability.
- [ ] Add disposable PostgreSQL migration/RBAC/IDOR tests and measured load/query-plan baselines.
- [ ] Validate Gemini connectivity in the target environment until health reports `ok` without fallback.

## Product completion

- [ ] Implement approved export artifact workers and model-ticket redemption.
- [ ] Add multipart RAG upload, malware scanning, and OCR after operational requirements are defined.
- [ ] Add automated browser end-to-end coverage for authentication, investigations, admin, themes, and chat.

## Scientific improvement

- [ ] Improve scenario causal precursors; valid synthetic supervised/anomaly performance remains weak.
- [ ] Evaluate the new cutoff-safe supervised observed-scenario GNN before extending it to future prediction; never claim predictive risk from retrospective full-graph embeddings.
- [ ] Defer calibration and real-world claims until externally valid data and evaluation support them.
