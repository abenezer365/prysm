# Phase 2.5 Label and Temporal Alignment Report

Exact evidence is in `evaluation/alignment_evaluation.json`; row-level decisions
are in `data/alignment/label_alignment.parquet`. Source ground truth is unchanged.

## Root cause

The ground-truth table is a synthetic scenario catalog, not a verified
entity-event prediction dataset. Its 3,801 anomalous rows are seven scenario
classes that are always positive; 1,199 separate `normal` rows are always
negative. This construction explains the 76.02% prevalence and does not
represent a naturally sampled future-event population.

More critically, the 5,000 labels contain 16,634 transaction IDs as related
evidence, but none of those transactions involve the labeled account, or an
account owned by the labeled person/company. Therefore no scenario event can be
attributed to its labeled entity from the available data.

The evidence timestamps are also inconsistent with the declared windows:

- 8,259 related transactions occur before `pattern_start`.
- 3,973 occur inside the source window.
- 4,402 occur after a bounded window.
- The median first related transaction occurs 337.8 days before the cutoff.
- Only 2,936 labels have bounded end dates; 2,064 are open-ended.

The same timing pattern occurs for normal and every anomaly scenario, supporting
the conclusion that label windows and related transactions were independently
assigned rather than observable scenario events.

## Prediction unit and correction

The required predictive unit is:

`typed entity + pattern_start cutoff + observable pre-cutoff history + affiliated transaction event after cutoff within a bounded pattern window`.

Phase 2 features already respect the cutoff. Phase 2.5 does not rewrite labels
or move cutoffs. It adds reproducible provenance fields, history/evidence status,
and `predictive_eligible`. Eligibility requires all configurable conditions in
`config/intelligence.json`. Zero current labels satisfy the event-provenance
requirement, so `predictive_population.parquet` correctly contains zero rows.

Original labels are retained as `retrospective synthetic metadata only`. They
remain useful for inspecting dataset intent, not for measuring prediction,
anomaly-label agreement, or rule detection.

## History and repeated labels

- 1,006 labels are `cold_start_no_history`.
- 1,733 have 1–4 events and are `insufficient_history`.
- 2,261 meet the configured five-event history minimum.

Anomaly prevalence is similar across these groups, so cold-start exclusion does
not explain the weak discrimination and cold starts are not relabeled as normal.
There are 80 rows across 40 repeated entities, seven entities with both classes,
and 21 overlapping later windows. All rows and provenance are preserved; any
future valid evaluation must continue entity/time purging.

## Before versus aligned evaluation

Before alignment, the held-out diagnostic produced supervised ROC-AUC 0.522,
PR-AUC 0.774 at 0.765 prevalence (+0.009 lift), anomaly ROC-AUC 0.477, and rule
ROC-AUC 0.485. Those values remain available for reproduction.

After alignment, metrics are `not_estimable`: there are zero defensible target
rows. Reporting a new ROC-AUC or training a replacement model would manufacture
an event definition. `artifacts/VALIDITY.json` marks the legacy supervised model
and predictions invalid for predictive use. Rules and anomaly scores remain
operational pattern signals, but their agreement with these labels is invalid.

## Required upstream repair and Phase 3 gate

A usable predictive target requires newly provided provenance—not inferred
labels—with scenario transaction IDs that involve the labeled entity, explicit
event start/end times, a bounded prediction horizon, and valid negative
observation windows. After that repair, rerun `scripts/align_labels.py`; proceed
to supervised/GNN evaluation only when eligible rows cover both classes and all
time/entity split partitions. Until then, Phase 3 may develop unsupervised and
rule-based graph signals, but must not calibrate or validate them against the
current ground truth.

