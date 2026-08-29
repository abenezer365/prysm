# Ground-Truth Relationship Repair

This isolated tool repairs only the evidence references in the existing generated `ground_truth.parquet`. It does not import or modify the synthetic generator, source Parquet files, entity IDs, transaction IDs, schemas, or transaction values.

## Why the original relationship fails

The original `ground_truth.py` chooses `related_entity_ids` from a global slice of transaction and entity IDs. It does not resolve the labeled entity's accounts, inspect transaction endpoints, enforce the scenario window, or validate the declared behavior. Consequently, random evidence references are normally unrelated to the label subject.

## Repair contract

For each label, the tool:

1. resolves the typed entity and its existing account(s);
2. joins those accounts to completed sender/receiver transaction endpoints;
3. filters evidence to the declared inclusive scenario window;
4. applies deterministic behavior-specific requirements;
5. replaces `related_entity_ids` with existing, directly affiliated transaction IDs; and
6. emits an empty list and an explicit decision reason when existing data cannot support the scenario.

The output preserves all ground-truth columns, types, row identities, labels, and scenario descriptions. It does not invent evidence to increase coverage or model performance. `shell_company` is intentionally unresolved because the existing activity fields contain no defensible shell-company indicator.

Labels whose typed entity exists but owns no account are also unresolved. They are counted separately as unresolved entity-to-account mappings, not emitted as invalid evidence.

## Regenerate

From the repository root:

```powershell
python generator/ground-truth-repair/repair_ground_truth.py
```

Optional paths:

```powershell
python generator/ground-truth-repair/repair_ground_truth.py --source-dir generator/synthetic-financial-generator/data/raw --output-dir generator/ground-truth-repair/output
```

The default run performs the repair twice in memory and fails if either the repaired frame, validation report, or per-label decisions differ.

## Outputs

- `output/repaired_ground_truth.parquet` — schema-compatible repaired labels.
- `output/validation_report.json` — before/after counts, invariant checks, scenario coverage, and unresolved cases.
- `output/repair_decisions.jsonl` — per-label account resolution, selected transactions, connected counterparties, status, and reason.

## Tests

```powershell
python -m pytest generator/ground-truth-repair/tests -q
```
