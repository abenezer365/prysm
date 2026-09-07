# Feature and Leakage Policy

## Safe candidates (when computed as-of-time)

- Transaction amount and `amount_etb`, counts, velocity, recency, status, type,
  channel, hour/day seasonality, counterparty diversity, and directional flow.
- Account age only where the experiment explicitly handles invalid pre-open
  events; account type, currency, status, and balance with missing/validity flags.
- Device/IP reuse counts, novelty, and change rates. Missing hashes or device IDs
  are absence indicators, never a shared-key value.
- Invoice linkage, age, amount discrepancy, party recurrence, and service type,
  provided only information available at the prediction time is used.
- Typed graph degree, component, motif, temporal-neighborhood, and confidence
  features from operational edges created before the prediction cutoff.
- Declared income ratios, occupation/employment context, and behavioral drift;
  apply robust transforms and group-aware validation.
- Currency mix and foreign-currency flow. Call this “foreign-currency” rather
  than cross-border behavior because observed person/transaction geography is
  Ethiopia-only.

## Exclude from model inputs

- `ground_truth_id`, `is_anomalous`, `behavior_type`, `risk_pattern`, `severity`,
  pattern dates, and `related_entity_ids` (direct label/provenance leakage).
- Raw IDs, hashes, names, phone/address values, invoice/reference IDs, or ID
  prefixes as numeric/categorical predictors. Use them only to construct safe
  historical aggregates and graph topology.
- Post-outcome status, closure, payment, reversal, investigation, or graph edges
  unavailable at scoring time.
- Random train/test row splits. Shared entities, repeated labels, graph neighbors,
  and overlapping time windows make them optimistic.
- `amount` without currency context, naive missing-value imputation, or geographic
  “foreign income” claims unsupported by the dataset.

## Evaluation requirements

Use forward temporal splits, purge overlap around label windows, and group by
typed entity so the same entity does not leak across folds. Report class-aware
precision/recall and calibration; accuracy is insufficient for the 76.02%
anomalous label mix. Seven entities carry both labels across time, so labels are
time-window outcomes rather than permanent entity classes.

Phase 2.5 supersedes direct use of those labels: supervised training or
label-based evaluation must first pass the event-provenance gate in
`data/alignment/label_alignment.parquet`. The current eligible population is
empty; legacy metrics are diagnostic only.
