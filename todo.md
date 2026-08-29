# Prysm Project Tasks

## Completed

- [x] Phase 1: canonical data foundation, integrity audit, typed links, and leakage policy.
- [x] Phase 2: normalized transaction facts, leakage-safe as-of features, configurable rules, anomaly and supervised diagnostic baselines, standardized signals, and reproducible evaluation.
- [x] Phase 2.5: label/event provenance audit, cold-start classification, predictive eligibility gate, and invalidation of unaligned supervised evaluation without rewriting source labels.
- [x] Phase 3: canonical temporal financial graph, graph integrity/features, self-supervised relational GraphSAGE representation, cutoff-valid bounded investigations, configurable fusion/confidence, traceable evidence, evaluation artifacts, and validity metadata.
- [x] Phase 3 verification: 549,947 nodes, 3,036,895 edges, zero invalid endpoints/duplicate semantic edges/self-loops/reversed intervals, and 19 passing tests.
- [x] Isolated ground-truth relationship repair: deterministic label-to-account-to-transaction resolution, behavior-aware evidence selection, schema-preserving repaired artifact, per-label decisions, and before/after validation. Existing generator/data remain untouched; 8 focused tests pass.
- [x] Step 4 scenario integration and validation: verified 7,000 aligned two-class observations and 46,094 evidence references; rebuilt Phase 2/2.5/3 in an isolated run; leakage, graph, fusion/evidence, reproducibility, and 19 tests pass. Valid synthetic supervised ROC-AUC is 0.470444; report is `ai-engine/runs/scenario-v1/PHASE_4_RETRAIN_VALIDATION_REPORT.md`.

## Phase 4 starting work

- [ ] Define the typed Phase 4 service/API request and response schemas around `InvestigationEngine` and `InvestigationResult`.
- [ ] Optimize disk-backed bounded-neighborhood lookup with indexing, predicate pushdown, and/or caching; benchmark interactive latency before exposing an API.
- [ ] Add deterministic response-schema validation and investigation persistence/versioning.
- [ ] Present assessment strength, confidence, availability, evidence, provenance, and limitations without exposing raw model internals or claiming a calibrated probability.

## Later scientific work

- [ ] Improve scenario causal precursors: aligned pre-cutoff supervised ROC-AUC 0.470444 and anomaly ROC-AUC 0.487010 show that valid labels alone did not create useful predictive separation.
- [ ] Add a batched cutoff-safe GNN training/evaluation head; never train a predictive head from retrospective full-graph embeddings.
- [ ] Keep supervised results scoped to the synthetic benchmark and defer probability calibration until external/real-world validation supports it.
- [ ] Generate production feature snapshots for arbitrary entity/cutoff batches only after the Phase 4 contract is defined; never deploy the invalid legacy supervised model.
- [ ] Improve and structurally benchmark the self-supervised graph representation (current link-reconstruction ROC-AUC 0.521) without using invalid risk labels.
