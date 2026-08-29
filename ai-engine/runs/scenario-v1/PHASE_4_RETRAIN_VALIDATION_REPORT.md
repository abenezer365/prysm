# Phase 4 Scenario Integration, Retraining, and Validation

## Scientific status

Dataset integration: **READY**  
Alignment: **valid_synthetic_scenario_evaluation** (7,000 eligible rows)  
Leakage audit: **PASS**  
Graph validation: **PASS**  
Evidence validation: **PASS**

The supervised result is valid only for this controlled synthetic future-scenario benchmark. It is not a calibrated fraud probability and does not establish real-world performance.

## Old versus new

| Metric | Original | Scenario dataset |
|---|---:|---:|
| Evaluation validity | invalid_unaligned_diagnostic_only | valid_aligned_synthetic_scenario_evaluation |
| Valid predictive rows | 0 | 7,000 |
| Test prevalence | 0.765 | 0.500 |
| Supervised ROC-AUC | 0.522 | 0.470 |
| Supervised PR-AUC | 0.774 | 0.467 |
| PR-AUC lift | 0.009 | -0.033 |
| Anomaly ROC-AUC | 0.477 | 0.487 |
| Rule ROC-AUC | 0.485 | 0.816 |

## Valid supervised test metrics

ROC-AUC 0.470444; PR-AUC 0.467240; precision 0.487884; recall 0.575238; F1 0.527972. Confusion matrix: `{'tn': 208, 'fp': 317, 'fn': 223, 'tp': 302}`.

## Scenario-level test results

| Scenario | Supervised ROC-AUC | PR-AUC | Recall | Rule recall | Anomaly ROC-AUC |
|---|---:|---:|---:|---:|---:|
| behavioral_shift | 0.480 | 0.112 | 0.560 | 0.200 | 0.456 |
| counterparty_change | 0.484 | 0.120 | 0.600 | 0.187 | 0.500 |
| foreign_currency_change | 0.502 | 0.135 | 0.667 | 0.240 | 0.522 |
| rapid_movement | 0.411 | 0.100 | 0.480 | 0.373 | 0.518 |
| shared_device | 0.439 | 0.107 | 0.547 | 0.227 | 0.460 |
| structuring | 0.493 | 0.130 | 0.587 | 0.280 | 0.466 |
| transaction_burst | 0.483 | 0.116 | 0.587 | 0.213 | 0.487 |

## GNN

Self-supervised structural link-reconstruction ROC-AUC: 0.515043. Supervised GNN status: `NOT_RUN_CUTOFF_SAFE_HEAD_REQUIRED`. The retrospective full-graph embedding was not used for predictive label evaluation because it contains post-cutoff edges.

## Recommendation

Use these results as the valid synthetic benchmark baseline. Improve scenario causal precursors and add a batched cutoff-safe GNN training/evaluation path before claiming predictive graph performance; do not tune thresholds or models solely to inflate scores.
