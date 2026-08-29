# GROUND-TRUTH RELATIONSHIP REPAIR — ISOLATED TASK

## Mission

Create a new isolated repair algorithm inside `generator/` whose **only purpose** is to fix the broken relationship between `ground_truth` labels and the existing generated financial activity.

The Phase 2.5 audit proved that the current ground-truth scenario evidence transactions are not correctly affiliated with their labeled entities/accounts.

The goal is to produce a corrected ground-truth relationship that is:

* entity-affiliated
* transaction-affiliated
* temporally coherent
* scenario-consistent
* reproducible
* suitable for future supervised ML/GNN evaluation

## Critical Safety Rule

**DO NOT modify the existing synthetic-data generator.**

Do not modify:

* existing generator algorithms
* existing generator source files
* existing dataset schemas
* existing column names
* existing column types
* existing entity IDs
* existing transaction IDs
* existing transaction records
* existing account records
* existing person/company records
* existing relationships
* existing invoice structure

The existing generated datasets are the source data.

Your new code must operate as an **independent repair/validation layer**.

---

## 1. READ ONLY WHAT IS NECESSARY

Inspect only the relevant generator code and the generated datasets required to understand:

* entity IDs
* account ownership
* transaction sender/receiver accounts
* ground-truth entity IDs
* scenario types
* event windows
* existing related entity IDs

Do not explore unrelated project resources.

Do not spend time reading PDFs, logos, documentation assets, or unrelated generator modules.

---

## 2. FIND THE RELATIONSHIP FAILURE

Programmatically verify the current relationship between:

```text
ground_truth entity
        ↓
entity's accounts
        ↓
transactions involving those accounts
        ↓
declared scenario/event window
```

Determine exactly why the existing `related_entity_ids` / scenario evidence does not correspond to the labeled entity's actual financial activity.

Do not guess.

Produce measurable before/after validation.

---

## 3. REPAIR THE RELATIONSHIP — NOT THE DATA SCHEMA

The repair algorithm should use the existing data to establish valid scenario evidence.

For every ground-truth scenario:

1. Resolve the labeled entity using its `entity_type` and `entity_id`.
2. Resolve the entity's actual accounts.
3. Identify transactions involving those accounts.
4. Respect transaction direction.
5. Identify transactions occurring inside the scenario/event window.
6. Identify relevant connected entities.
7. Ensure referenced transactions/entities are genuinely connected to the labeled entity.
8. Remove or replace invalid evidence references.
9. Preserve the original scenario identity and meaning.
10. Preserve all existing ground-truth columns exactly.

If the existing scenario cannot be supported by existing transactions, **do not invent transaction IDs**.

Instead mark the scenario as unresolved/unsupported in the repair output and report why.

---

## 4. TEMPORAL CONSISTENCY

The repaired evidence must respect:

```text
scenario start
        ≤
evidence transaction time
        ≤
scenario end
```

For open-ended scenarios, use the available bounded information without inventing an end date.

Do not use future transactions as evidence for an event that supposedly occurred earlier.

The repair algorithm must explicitly validate temporal ordering.

---

## 5. ENTITY AFFILIATION

A transaction should count as direct evidence for an entity only when it is actually connected to that entity through the existing account ownership structure.

For example:

```text
Person P123
    ↓ owns
Account A123
    ↓ sends
Transaction T900
    ↓ receives
Account A777
```

`T900` is valid evidence for `P123`.

But:

```text
Person P123

Transaction T900
belongs to unrelated Account A999
```

must NOT become evidence for `P123`.

Use the existing typed ownership fields.

Never rely on an ID appearing numerically similar.

---

## 6. SCENARIO-AWARE REPAIR

Do not treat every transaction as generic evidence.

Where the scenario type implies a particular behavior, validate that the selected evidence actually relates to the scenario.

Examples:

### Rapid outflow

Look for actual affiliated inflow followed by affiliated outflow within the relevant window.

### Structuring/smurfing

Look for actual affiliated transaction patterns and repeated movements rather than simply selecting random transactions.

### Foreign-income behavior

Use actual currency/amount information supported by the transaction.

### Shared-device behavior

Use actual device relationships between the entity's transactions and other entities.

### Invoice-related behavior

Use actual invoice/transaction linkage.

### Round-tripping

Require an actual connected transaction path rather than simply selecting multiple transactions.

If a scenario cannot be supported by the existing records, report it rather than fabricating evidence.

---

## 7. OUTPUT

Create the repair tool in a new isolated directory under:

```text
generator/
```

Choose a clear name.

The tool should generate a corrected ground-truth artifact without changing the existing dataset schemas.

Prefer producing:

```text
repaired_ground_truth.parquet
```

plus a machine-readable validation report.

The original ground truth must remain untouched.

The repaired file must preserve:

* identical columns
* compatible data types
* original scenario semantics
* original entity domains

If an existing field such as `related_entity_ids` is the intended evidence field, repair its values while preserving its schema.

---

## 8. VALIDATION REPORT

Produce a report containing at minimum:

* original label count
* repaired label count
* supported scenario count
* unsupported scenario count
* valid entity affiliations
* invalid entity affiliations remaining
* valid transaction affiliations
* invalid transaction affiliations remaining
* temporal violations
* scenario distribution
* evidence coverage
* unresolved cases

Most importantly:

```text
ground_truth entity
→ account
→ transaction
```

must be independently validated.

Target:

> **Zero invalid evidence relationships in the repaired output.**

Do not manufacture evidence merely to reach this target.

---

## 9. REPRODUCIBILITY

The repair algorithm must be deterministic.

Running it twice on the same datasets should produce the same repaired output and validation report.

Do not use uncontrolled randomness.

If randomness is genuinely necessary, make the seed explicit and configurable.

---

## 10. EFFICIENCY

The generated data is large.

Avoid:

```text
for every ground_truth:
    scan every transaction
```

Use indexed/grouped/vectorized processing where practical.

Build reusable mappings such as:

```text
entity → accounts
account → transactions
transaction → invoice
entity → relationships
```

Load only the necessary columns when possible.

Do not repeatedly reload the same Parquet files.

The tool should be practical to run repeatedly during development.

---

## 11. TESTING

Create focused tests for:

* entity/account resolution
* transaction affiliation
* temporal validity
* scenario-specific evidence
* preservation of columns
* deterministic output
* unresolved scenarios
* absence of fabricated IDs

At minimum verify:

```text
Every repaired evidence transaction
is genuinely connected to its labeled entity.
```

---

## 12. DO NOT OPTIMIZE FOR MODEL METRICS

The purpose of this task is NOT:

> “Make the future ML model achieve 90% accuracy.”

The purpose is:

> **Create truthful, correctly affiliated, temporally coherent ground truth from the existing generated financial activity.**

If honest repair still produces weak labels, report that.

Never create artificially easy labels.

---

## 13. EXISTING CODEBASE PROTECTION

Before finishing, verify that the repair task did not modify existing generator behavior.

Do not rewrite or refactor existing generator files.

Do not rename datasets.

Do not add/remove columns.

Do not alter source transaction values.

Do not alter entity IDs.

Do not modify the original ground-truth file.

The new repair algorithm must be independently executable.

---

## DEFINITION OF DONE

Stop when:

1. The relationship failure is identified.
2. The repair algorithm is implemented.
3. Existing generator code remains unchanged.
4. Existing dataset schemas remain unchanged.
5. Existing source datasets remain unchanged.
6. Ground-truth entities are correctly resolved.
7. Evidence transactions are genuinely affiliated.
8. Evidence respects scenario timing.
9. Unsupported scenarios are explicitly reported.
10. Repaired ground truth is generated.
11. Validation reports are generated.
12. Tests pass.
13. Running the repair twice produces deterministic results.
14. No fabricated transaction/entity IDs exist.
15. The exact command required to regenerate the repaired ground truth is documented.

After completing this task, **STOP**.

Do not modify the AI engine.

Do not retrain models.

Do not build GNNs.

Do not change the existing generator.

Do not attempt Phase 4.

This task ends with a **validated repaired ground-truth dataset and its repair/validation algorithm**.
