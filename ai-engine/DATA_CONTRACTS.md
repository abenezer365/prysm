# Canonical Data Contracts

## Global rules

- Raw Parquet in `../data/raw` is immutable evidence. The pipeline parses every
  date/datetime as UTC and never invents missing values or rewrites source facts.
- Primary keys are strings and non-null. Entity IDs are only unique inside their
  entity domain; all polymorphic joins use `EntityType:entity_id` keys.
- Allowed entity types are `Person`, `Company`, and `Account` where declared by
  each source type column. Referential validation must happen before graph use.
- Currency is ISO-like uppercase text from `{AED, CHF, ETB, EUR, GBP, USD}`.
  `amount` remains in transaction currency; `amount_etb` is the canonical
  transaction comparison amount. Do not derive historical FX behavior from the
  fixed synthetic conversion ratios.
- Null timestamps that mean “open-ended” remain null. Missing hashes remain null
  and are never imputed or interpreted as a shared identity.

## Processed outputs

| File | Grain / key | Contract |
|---|---|---|
| `persons.parquet` | one row / `person_id` | 100,000 canonical persons; duplicate resolution described below |
| `person_duplicate_lineage.parquet` | one source duplicate row | source-row lineage and selected-row flag for all 2,000 duplicate rows |
| `accounts.parquet` | one row / `account_id` | source account plus typed `owner_key` |
| `invoices.parquet` | one row / `invoice_id` | source invoice plus typed `issuer_key` and `recipient_key` |
| `relationship_edges.parquet` | one row / `relationship_id` | source edge plus typed `source_key` and `target_key` |
| `transaction_edges.parquet` | one row / `transaction_id` | temporal account edge; selected source fields plus typed account endpoints |
| `ground_truth_labels.parquet` | one row / `ground_truth_id` | labels plus typed `entity_key`; labels are excluded from features |

Ground-truth rows are immutable source metadata, not automatically valid model
targets. Predictive use additionally requires a matching row with
`predictive_eligible=true` in `data/alignment/label_alignment.parquet`; the
current dataset has none.

Banks, companies, and devices remain authoritative in raw form because no
normalization is presently needed. Every generated file and checksum is listed
in `data/processed/MANIFEST.json`.

## Person canonicalization

`person_id` is authoritative. For a duplicate ID, select the row with the most
non-null fields, then latest `created_at`, then earliest source row as a stable
tie-breaker. Never fuzzy-merge different IDs. The 1,000 duplicate IDs conflict
mostly on names and always on city, so the losing row is preserved in lineage;
the canonical row is a deterministic engineering choice, not verified identity.

## Temporal consumption contract

Feature builders must accept an `as_of` time, use only events at or before it,
and fit aggregations on the training fold. Relationship and label intervals are
`[start, end]`, with null end meaning open-ended. Because source account and
invoice lifecycles contain major inconsistencies, lifecycle-validity flags must
be features or filters chosen explicitly per experiment; rows must not be
silently dropped globally.

## Graph contract

Node keys use the typed key format. Ownership, bank membership, invoice-party,
device-use, relationship, and transaction edges must retain their source ID and
event/validity time. Transaction status must be retained: failed, pending, and
reversed events are observations, not equivalent to completed fund movement.
Ground-truth `related_entity_ids` are label provenance and must not become input
edges for supervised models.
