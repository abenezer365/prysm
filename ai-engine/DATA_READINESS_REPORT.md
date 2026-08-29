# Data Readiness Report

Generated from all 1,756,020 raw rows by `scripts/build_foundation.py`. Detailed
counts, source SHA-256 hashes, and missingness rates are in
`reports/data_quality_report.json`.

## What is trustworthy

- All eight non-person primary keys are unique; all required keys are present.
- Every typed account owner, invoice party, relationship endpoint, and label
  entity resolves to the correct master domain. Every non-null transaction
  account, device, and invoice reference resolves.
- Amounts and balances contain no impossible nonpositive transaction/invoice
  amounts or negative average balances. ETB conversions are internally stable:
  medians are ETB 1, USD 57.5, EUR 62, GBP 72, AED 15.6, and CHF 65.
- No reversed start/end pairs occur in accounts, devices, invoices,
  relationships, or ground-truth windows. Relationship edge intervals have no
  repeated typed edge or exact interval duplicate.
- Label primary keys are unique, with no exact semantic duplicates and no
  same-window conflicting labels. All 24,850 related-entity values resolve.

## Required cautions

- Persons contain 101,000 rows but only 100,000 IDs. All 1,000 duplicated IDs
  conflict; duplicate rows disagree mostly on name and always on city. Canonical
  selection is deterministic and fully retained in duplicate lineage.
- Lifecycle data is not reliable as a hard constraint: 351,237 sender and
  350,914 receiver events predate account opening; 14,966 sender and 14,974
  receiver events follow closure. Also, 31,603 `Closed` accounts have no
  `closed_at`. Preserve and flag these rows until generation semantics are known.
- 252,649 invoice-linked transactions predate invoice issue. Invoice chronology
  cannot be assumed causal without an explicit validity filter.
- 6,272 account currencies are absent from their bank's declared supported list.
  This can represent synthetic inconsistency or off-manifest capability; it is
  not safe evidence of suspicious behavior.
- 180,374 transactions differ from the sender account's denomination. This may
  represent cross-currency transactions, so retain both currencies and do not
  classify the mismatch as fraud by itself.
- Country fields do not support international geography. Foreign-currency
  behavior is available; cross-border claims are not.

## Missingness by meaning

Open-ended relationship and label ends are structural. Transaction invoice,
device, IP, and reference fields are conditional on transaction behavior/channel.
Browser can be inapplicable. Person employment status is unknown data; phone and
address hashes are absent identifiers and must never be imputed. Account closure
is mixed: null is structural for non-closed accounts but an inconsistency for a
`Closed` account.

## Label and modeling risk

Labels are 3,801 anomalous versus 1,199 normal. Severity and behavior/risk fields
encode the label directly (`info` only occurs for normal rows here), so they are
targets/provenance, never model inputs. Seven entities change class across time.
Treat the label as a temporal window, enforce as-of joins, and exclude related
entity lists from input graphs. Synthetic regularities, fixed FX rates, and ID
formats must not become predictors.

## Readiness decision and next phase

The source is ready for controlled feature experiments and temporal graph
construction using the canonical contracts, but not for unguarded lifecycle or
cross-border modeling. The next step is an as-of feature builder with explicit
lifecycle-validity indicators, followed by leakage-safe temporal/group splits.
Do not build a model until those split and feature contracts are tested.

