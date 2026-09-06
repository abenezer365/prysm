# Intelligence Output Contracts

All timestamps are UTC and inclusive at the `as_of` cutoff. Components remain
separate; Phase 2 does not produce a fused risk score.

## FeatureSet

`data/intelligence/label_feature_set.parquet` has one typed entity snapshot per
ground-truth cutoff. Identity columns are `ground_truth_id`, `entity_key`, and
`as_of`; `target`, `scenario`, and `split` are evaluation metadata and never
model inputs. `transaction_ids_30d` is traceability metadata. The 32 eligible
numeric features are enumerated in `FEATURESET.json` and cover behavior,
1/7/30-day velocity, currency-based foreign inflow, counterparties/devices,
invoice behavior, and active temporal relationships.

## RuleFinding

JSON Lines in `signals/rule_findings.jsonl` contain `rule_id`, `rule_name`,
`status`, `severity`, bounded `score`, explanation, typed `entity_ids`, relevant
operational `transaction_ids`, measurements, label-snapshot ID, and cutoff.
Findings describe observable patterns and are not fraud/AML declarations.

## AnomalyPrediction

`signals/anomaly_predictions.parquet` contains snapshot identity, continuous
`anomaly_score`, configured `is_anomaly`, and `model_version`. The score is an
isolation measure, not a fraud probability.

## ModelPrediction

`signals/model_predictions.parquet` contains snapshot identity, supervised
probability, thresholded prediction, and model version. The serialized robust
preprocessor and logistic model in `artifacts/` are required together for
inference.

## EvaluationResult

`evaluation/evaluation.json` records forward/entity-purged split boundaries,
prevalence, accuracy, precision, recall, F1, ROC-AUC, PR-AUC, confusion matrices,
scenario detection rates, feature-group results, coefficients, leakage
exclusions, and rule volume. Label descriptions are used here only.

## LabelAlignment

`data/alignment/label_alignment.parquet` preserves each source label and adds
history, event-window, evidence-affiliation, and predictive-eligibility fields.
`predictive_population.parquet` is the only permitted supervised population;
it is currently empty because no related transaction is affiliated with its
labeled entity. Consumers must check `artifacts/VALIDITY.json` before using any
legacy model or signal evaluation.

## GraphNode and GraphEdge

`graph/nodes.parquet` stores stable typed identity, safe attributes, and
provenance. Edge-family files under `graph/edges` store stable identity, typed
endpoints, semantics, event/interval time, confidence, financial attributes,
source record IDs, and source table.

## GraphEmbedding and structural signal

`node_embeddings.parquet` stores an unsupervised relation-aware embedding and
retrospective structural novelty. Historical investigations recompute the
representation from cutoff-valid bounded subgraphs. It is not a fraud score.

## SignalComponent, EvidenceItem, and InvestigationResult

Components separate availability, strength, confidence, reason, and evidence.
Evidence preserves supporting source IDs, measurements, timestamps, and
derivation. Investigation results combine the subject/window, graph summary,
components, uncalibrated assessment, confidence, findings, evidence,
limitations, and artifact versions.
