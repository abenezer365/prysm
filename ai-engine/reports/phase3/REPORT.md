# Phase 3 measured evaluation

Synthetic retrospective primary-subject classification: 80 cases per split, 72 normal and 8 suspicious. Train fits models; validation selects configuration; the frozen configuration then scores test. The benchmark was already used during Phase 2 development, so test is not a pristine external holdout.

## Results

| Split | Component | Scored / 80 | Unavailable | Precision | Recall | F1 | FP | FN | ROC AUC | Average precision |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| validation | rules | 80 | 0 | 1.000 | 0.750 | 0.857 | 0 | 2 | 0.875 | 0.775 |
| validation | anomaly | 71 | 9 | 1.000 | 0.125 | 0.222 | 0 | 7 | 0.867 | 0.639 |
| validation | network | 80 | 0 | 1.000 | 0.250 | 0.400 | 0 | 6 | 0.625 | 0.325 |
| validation | gnn | 80 | 0 | 0.727 | 1.000 | 0.842 | 3 | 0 | 0.995 | 0.966 |
| validation | fusion | 80 | 0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 1.000 | 1.000 |
| test | rules | 80 | 0 | 1.000 | 0.750 | 0.857 | 0 | 2 | 0.875 | 0.775 |
| test | anomaly | 71 | 9 | 1.000 | 0.125 | 0.222 | 0 | 7 | 0.861 | 0.634 |
| test | network | 80 | 0 | 1.000 | 0.250 | 0.400 | 0 | 6 | 0.625 | 0.325 |
| test | gnn | 80 | 0 | 0.667 | 1.000 | 0.800 | 4 | 0 | 0.997 | 0.975 |
| test | fusion | 80 | 0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 1.000 | 1.000 |

## Selection and limitations

Selected **short**, 945 parameters, 60 epochs, learning rate 0.025, GNN threshold 0.65. Baseline validation GNN F1 was 0.714; selected F1 is 0.842. Second-seed validation F1 is 0.824; inspect selection.json before claiming stability.

Rule/network detection logic, anomaly fitting/threshold and fusion weights remain unchanged. A measured availability bug was fixed: nine normal business-trading cases per split have recent business activity but quiet personal accounts. Rules/network/GNN now use graph activity for availability; personal-behavior anomaly correctly remains unavailable for those nine cases. Previous stored Phase 2 results excluded them from all component scores.

Family/circular specialists each detect their one positive against 72 normal controls. Rules OR network also matches fusion on this designed benchmark. Removing the GNN from the fixed weighted fusion misses two cases, but that does not establish incremental value over a simpler rules-OR-network decision. Keep these two comparisons distinct.

See failures.csv for exact errors and failures.json for their features and evidence. All selected validation/test GNN false positives are normal asset sales: graph aggregates capture their large amounts but omit transaction purpose. The amount rule already uses that purpose and correctly stays quiet. Generic anomaly deviation overlaps normal behavior and averaging dilutes isolated changes; seven suspicious cases per split remain below its conservative threshold. Feature diagnoses are interpretations, not causal experiments. Eight positive training cases are too few to establish broad generalization. No new model or label-derived feature was added.

Fusion moderate threshold is the review operating point; the high tier is a separate stricter queue, not the sole positive prediction. Scores and confidence are uncalibrated and do not establish guilt. Each suspicious scenario has only one validation and one test example; one error changes overall recall by 12.5 percentage points.

## Reading the artifacts

- metrics.json: all components, specialist tasks, per-scenario results, removal ablations and precision/recall@K.
- selection.json / experiment_plan.json: fixed controlled trials and validation-only selection.
- training_curves.csv / figures/: post-update unweighted train/validation BCE and classification metrics every 10 epochs (plus first/last); fitting itself uses balanced BCE plus L2, full batch of 80.
- rankings.json: configurable Top N with evaluation-only ground truth and complete supporting evidence. Raw *_results.jsonl contain no ground truth.
- model_bundle.json / config.json / MANIFEST.json: reloadable selected model, provenance and checksums.

Measured full-investigation latency: median 500.2 ms, p95 621.4 ms on this local run; includes graph/evidence and is not a production throughput claim. Graph samples are cached across experiments to avoid repeated feature extraction.

ROC AUC counts tied positive/negative pairs as half. Average precision uses recall increments at grouped score thresholds (not trapezoidal PR area). Undefined AUC/AP is null; no-prediction precision is zero. Missing component scores are excluded from component metrics and counted as unavailable. Ranking breaks ties by entity key; precision@K divides by returned count, recall@K includes all target positives.

## Phase 4 boundary

Load this model bundle through prysm_intelligence.pipeline.load_engine, then call investigate(subject, cutoff). Pass the evidence-backed result to later explanation work. Do not pass ground-truth labels, evaluation ranks or scenario rationales to an LLM. Existing API remains on the archived v1 integration until explicitly migrated. No Phase 4 implementation is included.
