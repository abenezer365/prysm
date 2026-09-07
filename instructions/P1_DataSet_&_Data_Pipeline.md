# PHASE 1 — PRYSM DATASET + DATA PIPELINE

## ROLE

You are implementing Phase 1 of Prysm Intelligence.

Your job is to redesign and stabilize the dataset foundation so the later AI, graph, anomaly, family-analysis, backend, and reasoning work can build on it cleanly.

You have the repository. **Inspect the existing implementation before deciding what to change.**

Do not assume that the current structure is correct, and do not blindly follow a predefined schema.

---

# 1. PRIMARY OBJECTIVE

Create a **small, clean, realistic, reproducible, relationship-aware benchmark dataset** for Prysm.

The dataset must be able to represent the types of entities and interactions Prysm needs for:

* fraud detection
* money-laundering indicators
* theft/unusual financial activity
* tax-evasion indicators
* geographic analysis
* family/network investigation
* graph/GNN analysis
* behavioral anomaly detection
* explainable evidence generation

The first dataset is **not** intended to demonstrate scale.

The purpose is to create a reliable foundation on which the intelligence system can be developed and evaluated.

Start with approximately **200–500 records/scenarios**, depending on what the existing architecture requires.

---

# 2. FIRST INSPECT THE EXISTING DATA PIPELINE

Before changing anything, inspect:

* current dataset files
* schema definitions
* synthetic-data generator
* seed/randomization logic
* dataset loading code
* feature-generation code
* label generation
* relationship generation
* existing parquet/csv/json usage
* any code that assumes the old dataset structure

Trace:

```text
dataset generation
        ↓
stored data
        ↓
loading
        ↓
features / relationships
        ↓
AI consumers
```

Identify what can be reused, what is obsolete, and what must change.

Do not redesign the repository based only on this prompt.

---

# 3. DATA MODEL DIRECTION

The data should be organized around a **small number of coherent entities**, rather than many fragmented files.

At minimum, the final structure should clearly represent the equivalent concepts of:

```text
people
financial accounts
organizations / businesses
transactions
relationships
```

But decide the exact file boundaries yourself after inspecting the current project.

The rule is:

> Keep information together when it naturally belongs together; separate it when it represents an independent entity or makes the system materially clearer.

Avoid creating a file for every category.

Avoid duplicated information across files.

Use stable identifiers to connect entities.

---

# 4. REQUIRED DATA CAPABILITIES

The resulting dataset must be capable of representing:

### Person / demographic context

Enough information to establish a person's identity/context and support behavioral analysis.

### Financial context

Accounts and financial-institution context sufficient to understand ownership and movement of money.

### Organization/business context

Businesses/organizations and relevant characteristics needed for financial and geographic investigation.

### Transaction context

Enough information to understand:

```text
who
→ moved
→ what amount
→ to whom
→ when
→ where
→ through what channel/type
```

and anything else genuinely required by the current Prysm detection logic.

### Relationships

The system must be able to represent meaningful relationships between entities rather than reconstructing everything from duplicated fields.

### Family / household context

The dataset must support family-related investigation where useful.

Do not force a specific implementation such as a particular `family_id` column if another representation is cleaner. The requirement is the capability, not a specific column name.

### Geographic context

The data must support geographic reasoning involving relevant entities and transactions.

The geographic design should be useful later for cases such as:

```text
transaction location
→ nearby business/activity
→ receiver/person
→ relationships
→ possible suspicious pattern
```

Again, decide the exact representation from the repository and use case.

---

# 5. ETHIOPIA-ORIENTED SYNTHETIC DATA

The synthetic dataset must feel like data that an Ethiopian financial/intelligence ecosystem could plausibly collect or integrate in the future.

Do not simply translate a generic Western dataset into Ethiopian names.

Make the generated data coherent around things such as:

* Ethiopian geography
* Ethiopian financial behavior
* ETB and relevant foreign currencies
* realistic domestic/international activity
* plausible business categories
* realistic demographic distributions
* realistic transaction channels
* plausible relationships between people, accounts and organizations

Use realistic distributions rather than random independent values.

For example, if a person's occupation implies a certain income range, the generated financial behavior should broadly reflect that.

The same principle applies to businesses, geography, account usage and transaction behavior.

---

# 6. NORMAL VS SUSPICIOUS DATA

The benchmark dataset should be intentionally designed rather than randomly generated.

Target approximately:

```text
90% normal behavior
10% suspicious/faulty behavior
```

The exact ratio may be adjusted if necessary for meaningful evaluation.

The suspicious records must represent **known scenarios** that Prysm is expected to detect.

Include multiple distinguishable patterns relevant to the project, such as:

* structuring
* unusually high transaction velocity
* abnormal transaction amount
* unusual geographic behavior
* suspicious network movement
* family/network-related suspicious behavior
* potential tax-evasion indicators

Do not make suspicious records random.

Every injected scenario must have a reason for existing and enough surrounding normal data to make the anomaly meaningful.

---

# 7. GROUND TRUTH

This is important.

The dataset must contain enough information for us to know what was intentionally injected.

Maintain a clean distinction between:

```text
raw/generated behavior
```

and

```text
ground-truth scenario/label
```

so later model evaluation can determine:

```text
what actually happened
vs
what the AI predicted
```

Do not leak artificial labels directly into model input features unless the existing design specifically requires it.

---

# 8. DATA QUALITY

Build validation around the final dataset.

At minimum, validate the types of integrity problems that could break downstream intelligence:

* duplicate identifiers
* broken relationships
* orphan entities
* invalid transaction references
* impossible or malformed values
* inconsistent timestamps
* invalid geographic values
* inconsistent labels/scenarios
* missing required fields
* contradictory entity relationships

The validator should fail clearly instead of silently accepting corrupt data.

---

# 9. REPRODUCIBILITY

The dataset generator must be reproducible.

Use a controlled seed/configuration so that we can regenerate the benchmark dataset and obtain the same logical dataset when required.

Do not scatter random generation throughout unrelated modules.

The generation process should have a clear entry point.

We should be able to answer:

```text
How was this dataset generated?
With what configuration?
From which code?
With which seed?
```

without reverse-engineering the project.

---

# 10. STORAGE FORMAT

Choose the storage format based on how Prysm actually consumes the data.

The analytical dataset should use an efficient structured format appropriate for large-scale later expansion.

Parquet is the preferred direction unless the current architecture provides a strong reason otherwise.

Do not optimize the system for 50 million records yet.

The important requirement is:

> The benchmark structure must remain scalable so that the same generation/data contract can later produce much larger datasets without redesigning the intelligence architecture.

---

# 11. DO NOT BUILD AI IN THIS PHASE

Do not redesign or train the AI engines in this phase.

Do not use this phase to add:

* new anomaly models
* new GNN models
* new rule systems
* LLM reasoning
* RAG
* backend features
* frontend features

Only make the minimum compatibility changes needed so the existing consumers can read the new dataset.

Phase 1 is about establishing the **data contract**, not solving detection.

---

# 12. KEEP THE DATASET SIMPLE

Avoid the temptation to make the dataset impressive by adding dozens of meaningless columns.

Every important field should answer:

```text
Why does Prysm need this?
Which later capability uses it?
```

Prefer derived behavioral features to be created by the feature pipeline rather than permanently stuffing every calculated metric into the raw source data.

Do not duplicate:

* person information
* account information
* organization information
* transaction information
* relationship information

just because multiple components need them.

Establish clean references instead.

---

# 13. COMPATIBILITY

After changing the dataset, trace the existing consumers.

Identify exactly what will break because of the new structure.

Update only the necessary data-loading/schema interfaces so downstream systems can consume the new dataset.

Do not perform unrelated refactoring.

Do not rewrite the AI engine in Phase 1.

---

# 14. REQUIRED DELIVERABLES

By the end of this phase, the repository should contain:

### A. Final dataset structure

A small number of coherent dataset files/entities.

### B. Generator

A reproducible synthetic-data generation process.

### C. Benchmark dataset

Approximately 200–500 records/scenarios containing:

```text
mostly normal behavior
+
controlled suspicious scenarios
```

### D. Ground truth

Clear scenario/label information suitable for later evaluation.

### E. Validation

A repeatable dataset-integrity validation process.

### F. Data documentation

Document:

* what each dataset/entity represents
* how entities are connected
* important identifiers
* important fields
* how the dataset is generated
* how labels/scenarios are represented
* how to regenerate it
* how to validate it

Keep this technical and repository-specific.

---

# 15. ACCEPTANCE CRITERIA

Do not consider Phase 1 complete merely because files exist.

Phase 1 is complete only when:

1. The dataset structure is coherent and minimal.
2. Entity relationships are explicit and valid.
3. The data is plausibly Ethiopia-oriented.
4. Normal and suspicious scenarios are intentionally constructed.
5. Ground truth can be used later for model evaluation.
6. The dataset can be regenerated reproducibly.
7. Validation catches structural/integrity problems.
8. Existing downstream code has a clear path to consuming the new dataset.
9. No unnecessary AI/backend/frontend work was introduced.
10. The data model is suitable for later scaling without redesigning it.

---

# 16. MEMORY / STATE UPDATE

After implementation, update the Prysm root technical memory/state file.

Do not write a generic summary.

Record the exact current state:

```text
Phase completed
dataset files/entities
exact repository paths
schema decisions
identifier relationships
generation entry point
generation configuration/seed
benchmark size
scenario distribution
validation entry point
commands
downstream compatibility changes
known limitations
remaining work
next phase entry point
```

This file must allow another AI agent to continue Phase 2 without repeating the Phase 1 investigation.

---

# 17. IMPORTANT WORKING RULE

Use this prompt as the **goal and boundary**, not as a rigid implementation specification.

Inspect the repository first.

Make implementation decisions from the actual codebase.

Choose the simplest technically sound structure.

Do not add things because this prompt mentions a concept unless the repository and Prysm's requirements actually need them.

Do not remove working functionality without understanding its dependencies.

Do not touch unrelated areas.

When Phase 1 is genuinely complete, update the technical state and STOP.
