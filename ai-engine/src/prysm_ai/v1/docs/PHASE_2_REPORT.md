# Phase 2 Intelligence Report

This report describes the reproducible outputs of `scripts/build_intelligence.py`.
Exact current metrics are machine-readable in `evaluation/evaluation.json`.

## Implemented

- A normalized transaction fact table retains all source fields and adds ETB
  log amount, foreign-currency, missing-link, account-lifecycle, sender-currency,
  and invoice-chronology indicators. Nothing is silently dropped or repaired.
- Leakage-safe as-of features aggregate only events at or before each label
  cutoff. Transaction histories are mapped through canonical typed ownership;
  active relationship features honor start/end intervals.
- Robust preprocessing uses train-only medians/IQRs and selected signed-log
  transforms. Missing/infinite values use training medians; scaling is clipped.
- Configurable rules cover amount deviation, bursts, rapid outflow,
  foreign-currency inflow change, counterparty change, shared identifiers, and
  invoice chronology. Thresholds and enablement live in one JSON configuration.
- Deterministic NumPy isolation forest and regularized logistic regression
  baselines support serialization and inference without SciPy/scikit-learn.
- Evaluation is forward temporal and entity-disjoint. Later observations of an
  entity already present in an earlier split are purged.

## Important interpretation

The ground truth is majority anomalous (about 76%), so F1 and PR-AUC can look
strong even when discrimination is weak. ROC-AUC and lift over prevalence are
the primary sanity checks here. Roughly one fifth of label snapshots have no
pre-cutoff transaction history, and typical 30-day activity is sparse. These
limitations constrain velocity, foreign-income change, and scenario detection.

On the held-out 983-row 2025 test set, supervised ROC-AUC is 0.522 and PR-AUC is
0.774 against 0.765 prevalence (only +0.009 lift); F1 is 0.786 and must not be
read independently of that base rate. Isolation-forest ROC-AUC is 0.477 and
rules ROC-AUC is 0.485. No feature group exceeds 0.521 ROC-AUC. The current
labels therefore appear weakly aligned with observable pre-cutoff behavior.
There are 846 rule findings: 388 invoice chronology, 252 shared-identifier, 114
frequency change, 75 foreign-currency inflow change, 15 counterparty change,
and 2 amount deviation. Burst and rapid-outflow thresholds did not trigger due
to sparse label-window activity; they remain tested and configurable.

Anomaly predictions and rule findings have operational value as explainable
signals but should not be treated as accusations. Foreign-income signals are
currency-based only; geography remains unsupported. Invoice chronology and
account lifecycle flags may reflect generator defects, so they are retained for
evidence/rules but excluded from supervised model features.

## Stopping boundary

No GNN, final score fusion, evidence narrative engine, API, graph database, or
deep learning was added. Phase 3 should consume these standardized signals only
after deciding how to improve scenario-aligned labels/history coverage.

## Phase 2.5 correction

The follow-up provenance audit established that all 16,634 ground-truth related
transaction values are unaffiliated with their labeled entity. The legacy
before-alignment metrics above remain diagnostic only. No aligned model was
trained and no after-alignment metric was fabricated; the predictive population
is empty. See `LABEL_ALIGNMENT_REPORT.md` and
`evaluation/alignment_evaluation.json` for the verified decision.
