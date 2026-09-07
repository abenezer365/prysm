# Phase 3 technical state — complete

The AI engine is ready for the Phase 4 handoff. Start with [the engine README](ai-engine/README.md), [the measured report](ai-engine/reports/phase3/REPORT.md), and [the code guide](ai-engine/INTELLIGENCE_V2.md). This phase implements evaluation and justified optimization; it adds no backend, UI, database, RAG or LLM integration.

## What changed

- One CLI now supports `build`, `evaluate`, `investigate` and `rank`. Inference defaults to the Phase 3 selected bundle.
- `evaluation.py` selects on validation, freezes configuration, then scores all partitions with complete source evidence. `metrics.py` implements confusion counts, precision/recall/F1, tie-aware ROC AUC and average precision, plus ranking metrics. Sorting/grouping avoids quadratic AUC memory.
- Three controlled GNN configurations and three thresholds are compared. The selected **60-epoch** model replaces the 180-epoch baseline; no new architecture or features were introduced. Training remains full-batch Adam, hidden size 8, learning rate .025, L2 .001, seed 20260905, 945 parameters, threshold .65.
- A validation coverage bug was fixed: nine normal business-trading cases per split had active business-account graphs but quiet personal accounts. Rules/network/GNN now check graph activity instead of suppressing the whole result. Personal anomaly remains unavailable for those nine cases, explicitly reported rather than counted as correct negatives.
- Nine historical top-level documents were moved into the existing `ai-engine/src/prysm_ai/v1/docs/` archive. The top level now has the current README and engine guide. Legacy runtime assets and import compatibility are preserved.

## Dataset and separation

Canonical input: `data/benchmarks/prysm-benchmark-v1/`, unchanged from [Phase 1](PHASE1_STATE.md). There are 240 cases: each partition has 72 normal and 8 suspicious primary business-owner observations. Train, validation and test cutoffs are respectively 2025-04-12, 2025-08-10 and 2025-12-11 at 10:00 UTC. Subjects/cases are disjoint; graph extraction uses source facts and cutoff-valid relationships, never label membership or scenario names.

The robust anomaly baseline is fitted on 72 training-normal cases. All GNN parameters and scaling are fitted on 80 training cases. Configuration selection uses validation F1, then average precision, then parameter/epoch simplicity. A fixed threshold tie prefers the original .65. Test does not select parameters. This benchmark was already inspected during Phase 2 development: it is a reused synthetic development benchmark, **not a pristine external holdout**.

## Measured selection

At the original .65 threshold:

| Configuration | Parameters | Epochs | Validation F1 | Validation AP | Fit seconds including monitoring |
|---|---:|---:|---:|---:|---:|
| baseline | 945 | 180 | 0.714 | 0.785 | 8.46 |
| compact | 377 | 180 | 0.667 | 0.890 | 7.54 |
| short | 945 | 60 | 0.842 | 0.966 | 2.64 |

All nine configuration/threshold combinations are in [selection.json](ai-engine/reports/phase3/selection.json). Lower .35/.5 thresholds introduced additional normal false positives. The selected model improves validation GNN recall from .625 to 1.000, at a precision tradeoff (.833 to .727). Second seed 20260906 gives F1 0.824, 7 TP, 2 FP and 1 FN: useful agreement, not proof of robust generalization. Rule/network logic, anomaly threshold and fusion weights remain unchanged.

## Frozen test results

| Component | Scored / 80 | Unavailable | Precision | Recall | F1 | FP | FN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| rules | 80 | 0 | 1.000 | 0.750 | 0.857 | 0 | 2 |
| anomaly | 71 | 9 | 1.000 | 0.125 | 0.222 | 0 | 7 |
| network | 80 | 0 | 1.000 | 0.250 | 0.400 | 0 | 6 |
| gnn | 80 | 0 | 0.667 | 1.000 | 0.800 | 4 | 0 |
| fusion | 80 | 0 | 1.000 | 1.000 | 1.000 | 0 | 0 |

GNN ROC AUC is 0.996528; average precision is 0.975. Fusion ROC AUC and AP are both 1.000. Review threshold is .35; the separate high tier starts at .65 and includes only 2/8 suspicious test cases. Do not interpret moderate-tier cases as missed simply because they are not in the high tier.

Each family/circular specialist detects its one target against 72 normal controls (F1 1.000). Overall rules miss the two routing cases; network analysis deliberately covers those and not the other six individual-behavior scenarios. The simple rules-OR-network baseline also scores F1 1.000. Removing GNN from the existing weighted fusion loses two cases at its unchanged threshold, but perfect fusion does **not** establish learned-model value over that simpler baseline.

Fusion precision@8 = 1.000 and recall@8 = 1.000; precision@10 = .800 and recall@10 = 1.000, in both validation and test. Ranking population here is the 80 primary subjects per split, not every person in the dataset. CLI `rank` separately supports all observed people. `--top-n` is configurable; the evaluation rank includes full evidence and ground truth only in its evaluation file.

## Exact failures and interpretation

All selected validation/test GNN false positives are normal asset sales:

| Split | Subject | GNN score | Observed amount / own historical median |
|---|---|---:|---:|
| validation | Person:P01050 | 0.877 | 57.8 |
| validation | Person:P01380 | 0.826 | 43.2 |
| validation | Person:P01390 | 0.679 | 52.0 |
| test | Person:P02010 | 0.843 | 47.9 |
| test | Person:P02050 | 0.767 | 52.9 |
| test | Person:P02060 | 0.885 | 53.0 |
| test | Person:P02240 | 0.728 | 52.9 |

These cases have large amounts, one-event bursts and no new-device/travel signal. The graph representation contains amount/history information but omits transaction purpose. The explicit amount rule already recognizes asset-sale context and stays quiet; fusion correctly keeps these cases below review threshold. This is a feature-based interpretation, not a causal experiment. No test-driven feature or threshold tuning was performed.

Anomaly catches theft and misses the other seven suspicious scenarios in each held-out partition. Generic deviation overlaps ordinary behavior, and averaging three contributions dilutes an isolated change. Its conservative .65 threshold and .20 fusion weight are retained because combined validation already succeeds; anomaly alone must not be presented as a complete detector. Nine normal declared-trading cases have no personal recent behavior and remain anomaly-unavailable. The initial engine suppressed all components for those cases; the corrected engine provides rules/network/GNN assessments.

[failures.csv](ai-engine/reports/phase3/failures.csv) lists exact baseline/selected errors and unavailable cases. [failures.json](ai-engine/reports/phase3/failures.json) adds features, component breakdowns and source-evidence references. [metrics.json](ai-engine/reports/phase3/metrics.json) contains per-scenario component metrics and removal ablations.

## Artifacts and performance

- Complete local run: `ai-engine/runs/evaluation-v3/`; all 240 label-free investigation results, predictions, models, metrics, ranked evidence, configuration, plan and file/source checksums.
- Portable review snapshot: `ai-engine/reports/phase3/`, including a reloadable copy of the selected model. Its own manifest hashes only the included files; full JSONL investigation exports stay local.
- [Training curves](ai-engine/reports/phase3/training_curves.csv): post-update unweighted BCE and precision/recall/F1 for train/validation at epoch 1, every 10 epochs and the final epoch. The optimizer uses balanced BCE plus L2; these are different loss definitions.
- [Training figure](ai-engine/reports/phase3/figures/training.png), [experiment comparison](ai-engine/reports/phase3/figures/experiments.png), and [evaluation figure](ai-engine/reports/phase3/figures/evaluation.png): class balance, normal/suspicious scores, FP/FN/unavailability and ranking quality.
- Measured local median full-investigation latency 500.2 ms, p95 621.4 ms; end-to-end evaluation before plots 206.6 s. Includes graph/evidence and concurrent local verification activity; not a controlled before/after latency or national-scale throughput claim. Graphs are built once per train/validation case and reused across training experiments.

## Verification and commands

Final verification: **101 tests passed, 3 historical full-artifact integration tests deselected**, with four existing Pydantic deprecation warnings. The broad suite covered Phase 1/2/3 plus legacy readiness, intelligence, graph, label alignment and API contracts. The selected-model CLI investigation and portable model reload/Top-1 ranking also passed. All three generated figures were visually inspected.

Two complete runs reproduced the selected model bundle, all 240 prediction rows and metrics exactly. Artifact/source hashes, ranked evidence and inference label separation were verified; see [verification.json](ai-engine/reports/phase3/verification.json). Timing is deliberately excluded from reproducibility comparison. Tests cover metric ties/undefined cases, split identity/time boundaries, validation-only selection, observer isolation, and the quiet-personal/active-business regression.

From the repository root:

```powershell
python ai-engine/scripts/run_intelligence.py build
python ai-engine/scripts/run_intelligence.py evaluate --top-n 10
# Existing output directories are protected; repeat into a fresh location:
python ai-engine/scripts/run_intelligence.py evaluate --output ai-engine/runs/evaluation-repeat
python ai-engine/scripts/run_intelligence.py investigate --subject Person:P01870 --cutoff 2025-12-11T10:00:00Z
python ai-engine/scripts/run_intelligence.py rank --cutoff 2025-12-11T10:00:00Z --top-n 10
python -m pytest ai-engine/tests/test_phase3.py ai-engine/tests/test_phase2.py ai-engine/tests/test_benchmark.py -q
```

The existing local runs are complete; do not rerun `build` into its existing path. Use the optional `evaluation` dependencies from `pyproject.toml` for charts/tests. Standalone package deployment is still outside this phase.

## Phase 4 handoff

Continue with `P4_RAG_LLM_&_Sovereignty.md`. Add `ai-engine/src` and the repository root to Python's import path (the CLI already does so), load `ai-engine/runs/evaluation-v3/model_bundle.json` with `prysm_intelligence.pipeline.load_engine`, and call `investigate(subject, cutoff)`. The review snapshot's `model_bundle.json` is also loadable. The stable result contains assessment/breakdown, findings, evidence, annotated graph, limitations and provenance. Pass that source-backed result to future explanation code; never pass ground truth, scenario rationale or evaluation ranking labels.

Existing HTTP/backend/UI still call the archived v1 integration; they were not migrated. The 1–2 million-row generator remains deferred until all six phases are finished. Only eight positive training cases and one positive per scenario per held-out split cannot establish real-world accuracy, calibration or scale.
