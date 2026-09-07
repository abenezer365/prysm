# Phase 2 technical handoff

Current handoff: [PHASE3_STATE.md](PHASE3_STATE.md). This document preserves the earlier phase decisions.

**Completed: AI intelligence and graph evidence for the new six-phase improvement project.** Phase 3 has not been implemented. Start the next phase with this file, [the intelligence guide](ai-engine/INTELLIGENCE_V2.md), and `P3_Evaluation_&_Optimization.md`.

## Current implementation and ownership

The new domain is `ai-engine/src/prysm_intelligence/`. The entry point is `ai-engine/scripts/run_intelligence.py`. It receives validated source facts, a typed subject and a timezone-aware cutoff; it produces structured intelligence. It has no HTTP, authentication, database, frontend or RAG responsibilities.

The sixteen historical domain modules were moved together to `ai-engine/src/prysm_ai/v1/`. `ai-engine/src/prysm_ai/__init__.py` is a small package-path bridge preserving existing `prysm_ai.features`, `prysm_ai.graph`, `prysm_ai.investigation` and other imports. Existing API callers, old scripts and the Phase 1 compatibility tests continue to use the archive. No historical raw files or model artifacts were deleted. There is one new phase implementation, rather than duplicate edits in old and new algorithms.

The actual deployed HTTP adapter still calls v1. Phase 2 does **not** automatically activate its models in the backend or frontend. Later integration should consume the new domain result contract deliberately. Existing Phase 1 changes and unrelated user files were preserved.

## Phase 1 consumption

Canonical source: `data/benchmarks/prysm-benchmark-v1/`; read its `DATASET_MANIFEST.md` first. `Dataset.load()` in `data.py` reuses `generator.prysm_benchmark.storage.read_snapshot()` to validate physical/logical hashes, schema and scenario integrity. It then retains only the six fact tables. No ground-truth table or case-membership list is present in the runtime dataset object.

The new engine reads canonical source directly; the older `ai-engine/runs/benchmark-v1/data/processed/` export is not an intermediate dependency. Separate ground truth is read only in `pipeline.py` for training selection and evaluation output. Every inference neighborhood is discovered from facts and excludes future observations and inactive relationships. A future company sales declaration cannot trigger a tax lead.

## Files and algorithms

| File under `ai-engine/src/prysm_intelligence/` | Exact role |
| --- | --- |
| `data.py` | Typed entity/reference indexes and bounded cutoff snapshots. Defaults: 120-day history, nine-day observation window, 100 core nodes and 2,000 transactions. Institution nodes do not bridge neighborhoods. |
| `features.py` | Separate prior history from recent events; amount/prior-median ratio, peak 15-minute count, historical frequency ratio, new-counterparty fraction, new-device fraction, physical branch travel speed, and outflow/ETB-income ratio. Each measurement retains source transaction support. |
| `rules.py` | Configurable `STRUCTURED_DEPOSITS`, `HIGH_VELOCITY`, `UNEXPLAINED_AMOUNT`, `IMPOSSIBLE_BRANCH_TRAVEL`, `BUSINESS_RECEIPTS_MISMATCH`, and `NEW_DEVICE_RAPID_OUTFLOW`. |
| `network.py` | Chronological three-account, three-transfer cycles within 60 minutes and 5% amount tolerance. `FAMILY_PASS_THROUGH` additionally requires an active family edge; otherwise `RAPID_CIRCULAR_FLOW`. Indexed/pruned search has an explicit 20,000-comparison safeguard. |
| `graph.py` | Source-backed graph nodes/edges and separate numeric GNN input. Nodes: Person, Company, Account, Institution and Device. Edges: owns, held_at, explicit relationships, transfers and uses_device. Transactions remain edges. |
| `anomaly.py` | `RobustAnomaly`: training-normal log-feature median/MAD baseline, explicit top-three additive contributions, reloadable statistics and unavailable cold-start handling. |
| `gnn.py` | `RelationalSAGE`: two fully trained eight-unit mean-aggregation layers, five relation channels and subject-plus-neighborhood readout, implemented with NumPy backpropagation. |
| `fusion.py` | Weighted mean over available components, with explicit configured/effective weights, weighted contributions, heuristic confidence and coverage. |
| `evidence.py` | Source-reference validation, deterministic version-bound evidence IDs and graph annotations. |
| `engine.py` | `IntelligenceEngine.investigate()` and `rank()`, model eligibility, cutoff checks, result assembly, fingerprints and missing/truncated-component handling. |
| `pipeline.py` | Config validation, train-only fitting, artifact binding/reload, immutable build publication and raw prediction hooks for Phase 3. |

All thresholds and model settings live in `ai-engine/config/benchmark_intelligence.json`, version `prysm-intelligence-v2`, seed **20260905**. Detailed rule predicates and feature rationale are documented in `ai-engine/INTELLIGENCE_V2.md` rather than repeated here.

Tax leads require **all** of: explicit beneficial ownership, personal-account business receipts, a same-period declaration available at cutoff, receipts above the declaration reference, and supporting proximity to the business. Geographic proximity or family membership alone never supplies risk.

## Models and actual fit

The anomaly model uses **72 training-normal observations**, not validation/test rows. It stores seven log-feature medians and robust scales, with a 0.2 scale floor. The score is the mean of the three largest one-sided transformed deviations; returned contributions sum to the score. The alert reference is 0.65. Fewer than four historical events or no recent activity is unavailable.

The GNN uses **80 training observations: 72 normal and eight suspicious**. Eleven node inputs are type indicators, recent incoming/outgoing counts and ETB volume, prior median, burst count, foreign-currency share and new-device fraction. Five channels are ownership, family, business relationships, incoming transfers and outgoing transfers. Institutions and devices are excluded from the learned graph; IDs and ground-truth metadata are never numerical features.

Task: synthetic retrospective primary-subject node classification. Model: two-layer relational mean GraphSAGE-style network, eight hidden units, **945 trainable parameters**. Fit: 180 full-batch Adam steps, learning rate 0.025, L2 0.001, balanced binary cross-entropy. All message-passing weights and biases plus the readout are trained. The persisted run's weighted training loss (excluding L2) went from **0.7621435 to 0.0627483**. This is a training sanity result, not a performance/generalization claim.

The fitted model population is ETB-income people with active beneficial ownership. Other subjects retain applicable deterministic analysis but do not receive out-of-population model scores. Truncated neighborhoods and model artifacts trained after the requested cutoff are explicitly excluded from model fusion. Training provenance is persisted in the model bundle; runtime results include a compact provenance summary.

GNN explanations remove an account-pair transfer connection and recompute the network, reporting positive score drops. Parallel transfers are removed together. Features are held fixed, so this is bounded sensitivity analysis, not a fully causal counterfactual. A high model score without localized positive sensitivity does not highlight an entire graph.

## Results, graph highlights and ranking

The domain result contract is `prysm-intelligence-v2`:

```text
version, subject, investigation_window
assessment: strength, risk_level, confidence, coverage, breakdown, is_fraud_probability=false
intelligence_components: rules, anomaly, network, gnn
findings: explicit checks/leads, network context, anomaly contributions, GNN sensitivity
features, evidence, graph, limitations, provenance
```

Fusion weights: rules **0.45**, anomaly **0.20**, network **0.20**, GNN **0.15**. Rule/network components take their strongest lead, rather than summing correlated findings. Available weights are renormalized. Levels are low below 0.35, moderate from 0.35 and high from 0.65. No available components means null strength/unavailable, not zero risk. Confidence is an engineering heuristic, not calibrated certainty.

Evidence keeps integration-friendly fields including `evidence_id`, `entity_id`, `signal_source`, `signal_type`, `description`, `supporting_entity_ids`, `supporting_transaction_ids`, `supporting_relationship_ids`, `supporting_edge_ids`, measurements, timestamps and provenance. Source checksum, cutoff and a fingerprint of the dataset/configuration/models/training metadata bind evidence identities to the analysis. Each referenced graph element must resolve.

GNN Maze can render `attention`, `highlight_color`, and `evidence_ids` directly on returned nodes/edges. `highlight_color="red"` means an evidence-linked review lead, not guilt. Unmarked elements are not certified innocent. Frontend logic does not decide suspicion.

`rank()` computes fused strength for supplied subjects, breaks ties by typed ID, and returns configurable N with cutoff, data version, fingerprint, level, component breakdown and evidence IDs. CLI `rank` scores all observed people at the requested cutoff. Build-time `top_entities.json` ranks each split's 80 primary subjects; these two populations are deliberately labeled differently.

## Generated artifacts and examples

The complete trained run exists locally at **`ai-engine/runs/intelligence-v2/`** (generated run artifacts remain ignored by Git):

- `model_bundle.json`: config, anomaly statistics, GNN parameters/preprocessing, loss trace and training provenance. Reload validates source dataset identity, artifact shapes/configuration and the run checksum when present.
- `train_results.jsonl`, `validation_results.jsonl`, `test_results.jsonl`: **80 full results each**, 240 total, with source evidence and graph annotations.
- `predictions.parquet`: observation IDs, subjects, cutoffs, split, target/scenario, in-sample marker, four component scores and fused score. This is the explicit evaluation-only table for Phase 3.
- `top_entities.json`: computed rankings per primary-subject split population.
- `config.json`, `training_report.json`, `MANIFEST.json`: settings, training-only sanity/measurements, source-code hashes and all artifact checksums.

Measured on the implementation environment: training including feature construction **24.14 seconds**; all 240 inference results and exports **67.08 seconds**; build before publication **91.77 seconds**. These are one local run's timings, not a production SLA or controlled latency benchmark. Numeric model/prediction content is reproducible for the same inputs/configuration/environment; timing fields vary.

Reviewable examples under `ai-engine/examples/`:

- `phase2_investigation.json`: the automatically highest-ranked test primary subject, `Person:P01790`; three evidence items and six red transfer edges. Selected from the computed ranking, not by a hardcoded positive list.
- `phase2_top_entities.json`: all ten computed test-primary ranking entries, with population/cutoff stated.
- `README.md`: how these examples were obtained and what they mean.

## Commands

Run from repository root:

```powershell
python ai-engine/scripts/run_intelligence.py build
python ai-engine/scripts/run_intelligence.py investigate --subject Person:P01870 --cutoff 2025-12-11T10:00:00Z --output .tmp/structuring-investigation.json
python ai-engine/scripts/run_intelligence.py rank --cutoff 2025-12-11T10:00:00Z --top-n 10 --output .tmp/top-people.json
python -m pytest ai-engine/tests/test_phase2.py -q
```

`build` has already run in this workspace and will refuse the existing destination. Use `--output ai-engine/runs/intelligence-v2-rebuild` for a fresh run, and point subsequent commands at its `--models <run>/model_bundle.json`. The dataset defaults to the Phase 1 canonical snapshot; `--dataset` and `--config` make alternative inputs explicit. Result paths also refuse overwrites.

The resumed verification executed individual `investigate` and all-people `rank` CLI paths using reloaded persisted models. Their scratch outputs are `.tmp/phase2-resume-investigation.json` and `.tmp/phase2-resume-ranking.json`; committed examples use the declared primary-subject benchmark population instead.

## Verification completed

**88 tests passed; three historical artifact-dependent integration tests were deliberately deselected.** This comprises 23 Phase 2 tests, 43 Phase 1 tests and 22 existing regression checks. The last resumed run passed after fingerprinting and all final code changes. Existing Pydantic deprecation warnings remain in the archived API boundary; dependencies were not changed.

```powershell
python -m pytest ai-engine/tests/test_phase2.py ai-engine/tests/test_benchmark.py ai-engine/tests/test_data_readiness.py ai-engine/tests/test_intelligence.py ai-engine/tests/test_graph_intelligence.py ai-engine/tests/test_label_alignment.py ai-engine/tests/test_api.py -q --tb=short -k 'not ready_reports_real_artifacts and not real_existing_engine_analysis and not full_dataset_person_search'
```

Tests cover all known suspicious scenario types and benign controls, source/graph evidence resolution, future-event exclusion, missing history, unavailable future declarations, ownership/geography prerequisites, expired family edges, unknown subjects, cutoff validation, deterministic ranking/fusion, truncated neighborhoods, anomaly explanations/reload, trained GNN edge sensitivity, finite-difference gradient checks for all parameter families, deterministic serialization, held-out poisoning isolation, artifact mismatch and preserved v1 imports. The final run's source-code and generated artifact hashes were independently verified; each result partition has 80 rows.

No live service startup, historical full inference smoke test, formal held-out metrics, hyperparameter search, calibration study, dashboard, backend migration, frontend change or RAG work was performed in Phase 2.

## Known limits and next phase

The benchmark has only eight positive training cases and repeated controlled histories. Training loss does not establish accuracy. The learned GNN lacks exact intra-window transaction ordering, legal purpose, geographic distance and declared-sales features; explicit rules carry those signals today. Anomaly training-normal selection uses labels, and its reference population is narrow. Confidence/fusion thresholds are initial engineering choices, not validated probability calibration.

Graph construction and scoring are bounded in-memory operations intended for this small benchmark. Display leaves can exceed the core node bound. The source has no real invoice evidence, full balance ledger or independently verified tax returns. Transaction purpose/location/declaration reliability must be challenged in later evaluation. Existing live API users still run v1 until a deliberate integration step.

**Phase 3 entry:** read this file and `ai-engine/INTELLIGENCE_V2.md`, then implement `P3_Evaluation_&_Optimization.md` against `predictions.parquet`, component evidence and canonical ground truth. Measure held-out behavior, scenario/benign errors, ranking, feature/graph leakage and GNN contribution before changing models. Keep train rows explicitly in-sample. Do not rebuild the dataset or start RAG/backend/frontend work as part of that evaluation. The 1–2 million-row generator remains deferred until after all six phases.
