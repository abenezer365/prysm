# PRYSM — GROUND-TRUTH SCENARIO REGENERATION & AUGMENTATION

## Mission

The current Prysm ground truth has a serious data-generation/provenance problem.

Phase 2.5 proved that the original ground truth cannot support predictive supervised learning.

The isolated repair algorithm successfully fixed the **relationship integrity**, but its results exposed the deeper problem:

```text
5,000 original labels
        ↓
647 have supportable financial evidence
        ↓
only 1 supported anomalous scenario
```

Therefore the current dataset does not contain enough genuinely supported anomalous scenarios to train and evaluate Prysm's supervised intelligence properly.

Your mission is to solve this problem **at the generator/data level**.

The objective is to produce a substantially larger, statistically useful, correctly affiliated, temporally coherent ground-truth/scenario population using the existing financial data and, where necessary, controlled augmentation of the synthetic financial activity.

---

# 1. IMPORTANT: DO NOT CHEAT

The goal is NOT:

> Make the model achieve 90% accuracy.

The goal is:

> Create a realistic, correctly labeled, temporally coherent financial-behavior dataset in which the labels are genuinely supported by the underlying transactions and relationships.

Do not create labels first and then manufacture convenient features to make models score well.

Do not create arbitrary correlations.

Do not copy scenario labels into model features.

Do not use ground-truth metadata as evidence.

Do not fabricate transaction IDs.

Do not claim that synthetic behavior represents real-world fraud.

Scientific validity is more important than attractive metrics.

---

# 2. READ THE CURRENT SYSTEM FIRST

Before implementing anything, inspect the relevant existing artifacts.

Read:

* `generator/ground-truth-repair/README.md`
* `generator/ground-truth-repair/repair_ground_truth.py`
* its `validation_report.json`
* `repair_decisions.jsonl`
* the repaired ground truth
* the existing generated datasets required for scenario construction
* the Phase 2.5 label-alignment report
* the Phase 2 intelligence report
* the Phase 3 report/architecture where relevant

Also inspect the existing generator architecture only enough to understand:

* entity relationships
* account ownership
* transaction generation
* scenario representation
* available columns
* how generated records are linked

Do not blindly rewrite the existing generator.

---

# 3. CURRENT PROBLEM

The current situation is:

```text
Ground truth
     ↓
many labels
     ↓
weak/no real transaction affiliation
     ↓
repair
     ↓
only 647 supported
     ↓
only 1 anomalous
```

This means the existing synthetic financial activity does not sufficiently contain the behaviors claimed by the ground truth.

The solution therefore requires **scenario-bearing financial activity**, not merely corrected references.

---

# 4. YOUR JOB IS TO FIND THE BEST SOLUTION

You are not restricted to one implementation strategy.

Investigate the existing data and determine the most reliable approach.

Possible approaches include:

### A. Controlled scenario injection

Create additional synthetic transaction sequences for real existing entities/accounts.

Example:

```text
Account A
   ↓
normal history
   ↓
prediction cutoff
   ↓
scenario injection
   ↓
T1 → T2 → T3 → T4
```

### B. Ground-truth reconstruction

Identify naturally existing patterns in the generated data that genuinely satisfy a scenario definition and label those.

### C. Hybrid approach

Use naturally occurring supported cases and supplement them with controlled scenario injection.

### D. Another technically superior approach

If inspection reveals a better solution, implement it.

You are expected to choose based on evidence.

---

# 5. PRESERVE THE EXISTING DATA CONTRACT

This is extremely important.

Do NOT arbitrarily change the existing dataset schemas.

Do not rename existing columns.

Do not remove existing columns.

Do not change existing ID formats.

Do not break the existing AI-engine data contracts.

Do not modify unrelated generator functionality.

If augmentation requires new records, preserve all existing schema requirements.

If an additional metadata/artifact is necessary, keep it isolated from the existing source schema unless there is a strong technical reason otherwise.

---

# 6. AUGMENTATION PRINCIPLE

If controlled scenario injection is necessary, use **real existing entities and accounts** from the generated dataset.

Do not create disconnected fake entities simply for labels.

For example:

```text
Existing Person P123
       ↓
Existing Account A123
       ↓
Existing historical transactions
       ↓
Controlled scenario event
       ↓
New affiliated transactions
       ↓
Ground-truth scenario
```

The scenario transactions must genuinely belong to the selected account/entity.

---

# 7. TEMPORAL DESIGN

Every predictive scenario must have a meaningful timeline:

```text
NORMAL HISTORY
       ↓
OBSERVATION / PREDICTION CUTOFF
       ↓
SCENARIO START
       ↓
SCENARIO TRANSACTIONS
       ↓
SCENARIO END
```

The prediction features must only use information available before the cutoff.

The ground-truth event must occur after the cutoff for predictive evaluation.

Do not allow the scenario to begin before the supposed prediction boundary.

Do not let evidence leak backward in time.

---

# 8. SCENARIO TYPES

Build a meaningful portfolio of scenarios relevant to Prysm.

At minimum investigate and support scenarios such as:

### Rapid outflow

Example:

```text
Receive 100,000 ETB
        ↓
within 24h
        ↓
transfer 90,000+ ETB
        ↓
multiple destinations
```

### Transaction burst

Example:

```text
Normal:
2–5 transactions/day

Scenario:
20–50 transactions within a short window
```

### Structuring / smurfing pattern

Multiple transactions arranged into a pattern that differs materially from the entity's normal behavior.

Do not simply generate identical transactions.

### Foreign-currency income change

Example:

```text
Normal foreign-currency activity:
low/stable

Scenario:
large unexpected foreign-currency inflow
```

Remember that the current dataset does not provide strong international geography.

Use currency-based intelligence only where justified.

### Behavioral shift

Example:

```text
Historical:
low-volume personal activity

After cutoff:
large/high-frequency activity
```

### Counterparty/network anomaly

Use actual connected accounts/entities and create meaningful changes in network behavior.

### Shared-device / shared-identifier pattern

Where the existing device/address relationship infrastructure supports it, create realistic shared infrastructure patterns.

### Invoice-related anomaly

Where appropriate, use actual invoice/transaction relationships and maintain chronological consistency.

### Other scenario

If the existing data supports another meaningful scenario, you may add it.

Do not create dozens of shallow scenarios.

Prefer a smaller number of strong, interpretable scenario families.

---

# 9. NORMAL / NEGATIVE POPULATION

A good supervised dataset needs both positive and negative observations.

Do not simply generate thousands of anomalies.

Construct a meaningful normal population from entities with ordinary behavior.

Negative observations must have:

* sufficient history
* a valid cutoff
* no injected target scenario in the prediction horizon
* legitimate financial activity

Do not define “normal” merely as “not labeled anomalous.”

It should represent genuine non-scenario behavior.

---

# 10. SCALE

The existing financial dataset contains approximately:

```text
1.756M rows
700k transactions
100k persons
150k accounts
500k relationships
```

The final scenario population should be large enough to be meaningful relative to this dataset.

Do not arbitrarily keep only 5,000 snapshots if the available data can support substantially more.

Determine an appropriate target population by examining:

* number of entities
* transaction coverage
* available history
* scenario diversity
* computational cost
* class balance
* temporal coverage

Aim for a dataset large enough to support serious evaluation.

Do NOT sacrifice realism merely to increase row counts.

A smaller valid population is better than a huge artificial one.

---

# 11. CLASS BALANCE

Do not reproduce the previous problem where approximately 76% of labels were anomalous.

Design a deliberate but defensible class distribution.

Consider a balanced or moderately imbalanced population appropriate for evaluation.

Do not make the positive class overwhelmingly dominant.

Document the chosen prevalence and why it was chosen.

Also preserve scenario-level balance so one scenario does not dominate all others.

---

# 12. ENTITY SPLIT SAFETY

Ensure that training, validation, and test populations can be separated without entity leakage.

Prefer:

```text
Train entities
      ≠
Validation entities
      ≠
Test entities
```

where the evaluation objective requires entity generalization.

Also preserve temporal separation where appropriate.

Do not generate scenarios in a way that causes the same entity to appear as both a clean negative and an unrelated positive in the same prediction population without a legitimate temporal reason.

---

# 13. REALISTIC SCENARIO GENERATION

Scenario injection must respect existing financial semantics.

Do not generate:

```text
impossible balances
impossible ownership
invalid account references
random entity IDs
impossible dates
invalid currencies
```

Respect:

* account ownership
* transaction direction
* timestamps
* currencies
* account lifecycle
* transaction status
* existing relationships
* invoice relationships where used

Scenario transactions should look like plausible synthetic financial activity.

---

# 14. SCENARIO EVIDENCE

Every positive scenario must have explicit evidence.

For example:

```text
Scenario:
RAPID_OUTFLOW

Entity:
P123

Cutoff:
2025-05-01

Evidence:
T9001
T9002
T9003
T9004

Reason:
91% of post-cutoff inflow was transferred
within the configured rapid-outflow window.
```

Evidence must be generated from actual transaction records.

Never create evidence references independently from the actual data.

---

# 15. GROUND-TRUTH SCHEMA

Preserve the existing ground-truth schema exactly unless there is a demonstrably unavoidable compatibility issue.

The existing columns and meanings must remain compatible.

The new ground truth should continue to represent:

* entity type
* entity ID
* behavior/scenario type
* risk pattern
* anomaly status
* severity
* pattern start
* pattern end
* related evidence entities

Do not introduce schema-breaking redesign simply because another representation looks cleaner.

If supplementary scenario metadata is necessary, store it separately.

---

# 16. VALIDATION

Build a comprehensive validation stage.

Every positive scenario must pass:

```text
entity exists
        ↓
entity owns/reaches referenced account
        ↓
referenced transaction exists
        ↓
transaction belongs to that account/entity
        ↓
transaction timestamp is valid
        ↓
transaction is inside scenario window
        ↓
scenario behavior is actually observable
```

Target:

```text
invalid entity affiliations = 0
invalid transaction affiliations = 0
fabricated IDs = 0
temporal violations = 0
schema violations = 0
```

Do not hide unsupported scenarios.

Report them.

---

# 17. SCENARIO BEHAVIOR VALIDATION

Do not validate only the relationships.

Validate the actual behavioral claim.

For example:

### Rapid outflow

Verify the measured inflow/outflow relationship.

### Burst

Verify transaction count and timing.

### Foreign-income change

Verify currency and historical comparison.

### Behavioral shift

Verify deviation from historical baseline.

### Structuring

Verify the actual transaction pattern.

### Network scenario

Verify the actual graph relationship.

The label must correspond to measurable behavior.

---

# 18. BEFORE / AFTER REPORT

Generate a clear report comparing:

```text
ORIGINAL
↓
REPAIRED
↓
AUGMENTED
```

Include:

* total labels
* supported labels
* unsupported labels
* positive count
* negative count
* scenario counts
* transaction evidence count
* entity coverage
* temporal coverage
* invalid references
* fabricated references
* schema changes
* deterministic hashes

---

# 19. MODEL-READINESS CHECK

Before declaring success, perform a lightweight readiness experiment.

Do NOT rebuild Phase 2 or Phase 3.

Instead verify that the new ground truth can produce:

```text
valid entity
+
valid cutoff
+
sufficient history
+
future scenario
+
affiliated evidence
```

for a meaningful number of observations.

A small sanity model may be used if useful, but do not optimize models during this task.

The purpose is to verify that the repaired/augmented dataset actually represents a learnable prediction problem without leakage.

---

# 20. AVOID ARTIFICIAL EASE

This is critical.

Do not create scenarios where:

```text
positive = amount > X
negative = amount < X
```

unless that genuinely represents the intended scenario.

Do not make every anomalous transaction dramatically different from every normal transaction.

Include realistic variation.

Use different:

* amounts
* time intervals
* counterparties
* transaction counts
* currencies
* channels
* scenario intensities

The model should learn patterns, not a single generator fingerprint.

---

# 21. MULTIPLE SCENARIO INTENSITIES

Where practical, create scenario severity levels such as:

```text
low
medium
high
```

The behavioral difference should increase progressively.

For example:

```text
Normal:
normal outflow

Low:
moderately elevated outflow

Medium:
strong rapid movement

High:
extreme rapid movement
```

This creates a more useful foundation for later risk scoring.

---

# 22. RANDOMNESS

If scenario generation uses randomness:

* make it deterministic
* use an explicit seed
* record the seed/configuration
* make the process reproducible

Two runs with identical inputs/configuration should produce identical outputs.

---

# 23. EFFICIENCY

The generator already handles a large dataset.

Do not repeatedly scan every transaction for every scenario.

Use:

* indexed mappings
* grouped data
* efficient joins
* cached entity/account mappings
* vectorized operations
* selective column loading

Avoid unnecessary memory duplication.

The augmentation should be practical to rerun.

---

# 24. ISOLATION

Implement this as an isolated generator-side capability.

Do not rewrite the existing generator architecture unless absolutely necessary.

Prefer a dedicated component such as:

```text
generator/
    ground-truth-repair/
    ground-truth-scenario-generation/
```

The exact naming is your decision.

The original generator must remain functional.

The new capability should have its own command and documentation.

---

# 25. TESTING

Add focused tests for:

* entity selection
* account selection
* scenario generation
* transaction affiliation
* scenario timing
* evidence generation
* schema preservation
* negative generation
* class balance
* deterministic output
* absence of fabricated IDs
* scenario behavior validation

Run all tests.

Run the complete generation/augmentation process at least once.

Run it twice and verify deterministic output.

---

# 26. FINAL OUTPUTS

Produce:

1. Augmented/generated financial data required for the scenarios.
2. Corrected/augmented ground truth.
3. Validation report.
4. Scenario statistics.
5. Deterministic manifest/checksum.
6. README describing exactly how to regenerate it.
7. Any isolated configuration used by the generator.

Do not overwrite the original datasets unless explicitly required by the existing project architecture.

Prefer a clearly identified generated/augmented dataset.

---

# 27. IMPORTANT: YOU MAY DISCOVER A BETTER SOLUTION

You have permission to deviate from the suggested implementation if analysis shows another approach is more correct.

You may:

* reconstruct scenarios from existing activity
* augment only selected entities
* create new controlled transactions
* combine natural and injected scenarios
* redesign the scenario-selection algorithm
* introduce a better validation mechanism
* create additional scenario families
* create a stronger negative-sampling strategy

provided that:

1. the existing schema remains compatible,
2. the original generator remains intact,
3. no fake evidence is created,
4. temporal correctness is preserved,
5. entity affiliation is real,
6. the resulting dataset is reproducible,
7. the method is documented.

Think like a senior synthetic-data engineer and ML evaluation designer.

Do not blindly follow this document if the actual data demonstrates a better approach.

---

# 28. SUCCESS CRITERIA

The task is successful when the resulting dataset provides a meaningful population containing:

* sufficient positive scenarios
* sufficient negative observations
* multiple scenario types
* meaningful scenario variation
* real entity/account affiliation
* valid temporal prediction boundaries
* sufficient historical coverage
* explicit evidence
* preserved schema compatibility
* zero invalid evidence references
* zero fabricated transaction IDs
* deterministic generation
* documented provenance

The exact final number of observations should be determined from the data and computational constraints rather than an arbitrary hard-coded number.

However, it should be **substantially larger and more useful than the current 647 supported scenarios**, provided the underlying data can support that scale honestly.

---

# 29. FINAL REPORT

When finished, report:

```text
Original population:
...

Supported original scenarios:
...

New/augmented scenarios:
...

Positive observations:
...

Negative observations:
...

Scenario distribution:
...

Entity coverage:
...

Transaction coverage:
...

Temporal coverage:
...

Invalid affiliations:
...

Temporal violations:
...

Fabricated IDs:
...

Schema changes:
...

Deterministic:
YES/NO

Model-readiness:
READY / NOT READY

Reason:
...
```

If the result is not sufficient for supervised evaluation, do not claim success.

Explain the remaining bottleneck and what must change.

---

# STOPPING BOUNDARY

This task ends when the ground-truth/scenario data problem has been solved as far as the existing synthetic data can honestly support.

Do NOT:

* retrain Phase 2 models
* retrain the GNN
* modify the AI engine
* modify frontend/backend
* tune models for high accuracy
* rewrite unrelated generator code
* create fake labels
* fabricate evidence

The next step after this task will be to point the existing AI-engine pipelines at the new dataset and **measure the actual improvement**.

Do not perform that downstream retraining now.

Update only the relevant generator documentation needed to explain the new dataset and regeneration process.

Then stop.
