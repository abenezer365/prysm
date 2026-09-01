# PRYSM AI — STEP 2

# DATA CLEANING → NORMALIZATION → PREPROCESSING → INTELLIGENCE & MODELING

## 1. MISSION

You are continuing the implementation of the **Prysm AI Engine**.

Prysm AI is an Ethiopia-first financial intelligence platform designed to understand financial behavior and relationships across people, accounts, companies, transactions, invoices, devices, banks, and other entities.

Its intelligence must eventually detect and explain patterns related to:

* financial fraud
* money-laundering/AML patterns
* unusual transaction activity
* behavioral anomalies
* transaction velocity
* foreign-income anomalies
* suspicious relationship patterns
* network-level financial behavior

Phase 1 — **AI Foundation & Data Readiness** — has already been completed.

Your mission now is:

> **Take the verified Phase 1 data foundation, make it genuinely clean and model-ready, then build the first substantial Prysm financial-intelligence layer on top of it.**

This phase must spend significantly more effort on **intelligence and modeling** than on basic cleaning.

---

# 2. READ PROJECT MEMORY FIRST

Before making changes, read:

* `memory.md`
* `todo.md`
* `ai-engine.md`
* `DATA_CONTRACTS.md`
* `FEATURE_POLICY.md`
* `DATA_READINESS_REPORT.md`

These files describe the work already completed and the constraints future work must preserve.

Do not repeat Phase 1 unnecessarily.

Do not assume that something is implemented merely because it is described in documentation. Verify important existing outputs before building on them.

---

# 3. STRICT SCOPE

Work only within the AI-engine project and its designated data/model directories.

Use:

* `ai-engine/`
* `ai-engine/raw-data/`
* existing Phase 1 processed-data locations
* existing AI-engine configuration, source, model, artifact, evaluation, and test directories

Do NOT inspect or modify:

* `generator/`
* `resource/`
* `resources/`
* frontend
* mobile
* logos
* PDFs
* project design documents
* unrelated project code

The synthetic-data generator is a separate completed project and is intentionally outside this task.

Do not waste context inspecting it.

---

# 4. PHASE 2 ARCHITECTURE

Build this pipeline:

```text
Phase 1 Canonical Data
        ↓
Data Cleaning
        ↓
Normalization
        ↓
Model-Specific Preprocessing
        ↓
Feature Engineering
        ↓
        ┌─────────────────────────────┐
        │     INTELLIGENCE LAYER     │
        │                             │
        │ Transaction Intelligence   │
        │ Behavioral Intelligence    │
        │ Velocity Intelligence      │
        │ Foreign-Income Intelligence│
        │ Rule Engine                │
        │ Anomaly Detection          │
        │ Supervised ML Baseline     │
        └──────────────┬──────────────┘
                       ↓
              Standardized Signals
                       ↓
                 Evaluation
```

Do NOT build the final risk-fusion/GNN/evidence system in this phase.

---

# 5. PART A — DATA CLEANING

Phase 1 performed validation and canonicalization.

That does NOT mean the data is automatically ready for modeling.

Perform the additional cleaning required for reliable feature engineering and ML.

Do not blindly remove records.

For every cleaning decision, determine whether the problem should be:

* corrected safely
* normalized
* retained as meaningful information
* excluded from a specific feature/model
* documented as unresolved

Pay particular attention to:

### Entity quality

* canonical persons
* duplicate lineage
* polymorphic IDs
* account ownership
* invoice parties
* relationship endpoints
* device references
* transaction references

### Temporal quality

Validate:

* event ordering
* account opening/closing versus transactions
* invoice dates versus payments
* relationship start/end intervals
* future information accidentally entering historical features

Do not invent dates to fix inconsistencies.

### Financial quality

Validate:

* numeric values
* currency handling
* ETB amounts
* conversion consistency
* impossible/negative values where not semantically valid
* extreme values
* balance relationships where meaningful

### Missing data

Treat missingness according to meaning.

For example:

* an open account with no `closed_at` is not necessarily dirty
* a transaction without an invoice may be legitimate
* a missing device is different from an invalid device
* missing identifiers affect relationship confidence

Do not fill missing values blindly.

---

# 6. PART B — NORMALIZATION

Create a consistent representation suitable for modeling.

Normalize where appropriate:

* numeric features
* currencies/financial measurements
* categorical representations
* timestamps
* entity identifiers
* temporal windows
* transaction direction
* incoming/outgoing semantics

Preserve original source values when they are needed for evidence or traceability.

Never destroy raw information simply because a normalized version is created.

The system should be able to distinguish:

```text
source value
normalized value
derived feature
```

where appropriate.

---

# 7. PART C — MODEL-SPECIFIC PREPROCESSING

After cleaning and normalization, create preprocessing required by the intelligence models.

This may include:

* categorical encoding
* numerical scaling
* robust transformations for highly skewed amounts
* missing-value strategies
* temporal aggregation
* rolling windows
* person/account-level aggregation
* feature eligibility filtering
* train/validation/test preparation

Choose preprocessing methods based on the actual data.

Do not apply transformations simply because they are common.

Avoid leakage from:

* future transactions
* ground-truth fields
* post-event information
* synthetic scenario metadata
* duplicate person records

Keep preprocessing reproducible.

---

# 8. PART D — FEATURE ENGINEERING

This is where the project begins transitioning from data processing into intelligence.

Build reusable features rather than one-off calculations hidden inside models.

Prioritize the following groups.

## Transaction Intelligence

Useful signals may include:

* transaction amount
* ETB-normalized amount
* transaction direction
* transaction frequency
* transaction-type distribution
* channel distribution
* currency usage
* counterparty count
* transaction status behavior
* invoice linkage
* device usage
* temporal activity

## Behavioral Intelligence

Build person/account baselines where sufficient history exists.

Examples:

* typical transaction amount
* median transaction amount
* income baseline
* transaction-frequency baseline
* normal inflow/outflow behavior
* historical variance
* recent-versus-historical change
* behavioral deviation

The goal is not merely to determine whether something is large.

The goal is to determine:

> **Is this behavior unusual for this entity?**

## Velocity Intelligence

Build configurable time-window features.

At minimum consider:

* 24-hour
* 7-day
* 30-day

Measure:

* incoming volume
* outgoing volume
* transaction count
* outflow ratio
* rapid movement
* transaction bursts
* time between incoming and outgoing activity
* number of destinations after incoming funds

## Foreign-Income Intelligence

This is a major Prysm use case.

Build signals around:

* foreign-currency income
* foreign-income volume
* foreign-income ratio
* foreign-payment frequency
* foreign-source diversity
* currency diversity
* income growth
* foreign-income baseline
* changes in foreign-income behavior

IMPORTANT:

The current dataset has limited geographic international information because person/transaction country fields are predominantly Ethiopia.

Do not manufacture international geographic intelligence that the data cannot support.

Currency-based foreign-income signals are valid where supported.

## Relationship Features

Prepare relationship-aware features that can later complement the GNN.

Examples:

* connected-account count
* counterparty count
* company connections
* employer relationships
* shared-device indicators
* shared-phone indicators
* shared-address indicators
* invoice relationships
* relationship confidence

Do not build the GNN yet.

---

# 9. PART E — CONFIGURABLE RULE ENGINE

Implement the first Prysm rule engine.

The rule engine must identify **patterns**, not declare that an entity committed fraud or money laundering.

Initial rule families should cover meaningful supported patterns such as:

* unusual transaction amount
* unusual transaction frequency
* sudden income increase
* sudden foreign-income increase
* rapid outflow
* transaction bursts
* unusual counterparty behavior
* behavioral change
* shared identifiers
* invoice/transaction inconsistencies
* other strongly supported patterns discovered during analysis

Rules must be configurable.

Do NOT scatter thresholds throughout source code.

Centralize important parameters such as:

* thresholds
* time windows
* minimum history
* minimum transaction counts
* enable/disable state
* severity boundaries

The rule engine should be easy to tune later.

Every triggered rule should produce a structured finding containing enough information for future evidence generation.

At minimum include:

* rule ID
* rule name
* status
* severity
* signal strength/score
* explanation
* relevant entity IDs
* relevant transaction IDs
* important measurements

---

# 10. PART F — ANOMALY DETECTION

Implement the first unsupervised anomaly-detection baseline.

Prefer a strong, simple baseline such as:

* Isolation Forest

or another method if the actual data justifies it.

Use engineered behavioral/transaction features.

Do not feed raw tables directly into the model.

Produce:

* anomaly score
* anomaly indicator where appropriate
* model metadata
* reproducible preprocessing
* reproducible inference

Evaluate whether anomalies correspond to the known synthetic ground-truth scenarios.

Remember:

> Anomaly ≠ fraud.

---

# 11. PART G — SUPERVISED ML BASELINE

Use `ground_truth` according to the Phase 1 feature/leakage policy.

Choose the strongest defensible prediction target supported by the labels.

Start with an interpretable baseline.

Prefer:

* Logistic Regression
* Random Forest
* Gradient Boosting

Choose based on the actual feature structure.

Do not build deep learning yet.

The purpose is to establish a measurable baseline for future Prysm models.

Prevent:

* target leakage
* temporal leakage
* duplicate-person contamination
* train/test contamination

The split strategy must reflect the temporal nature of financial behavior where appropriate.

---

# 12. PART H — EVALUATION

Evaluation is a first-class part of the intelligence layer.

Do not finish by saying:

> “The model trained successfully.”

Determine whether it actually works.

Evaluate:

* rules
* anomaly detection
* supervised ML
* important feature groups

Use appropriate metrics including:

* precision
* recall
* F1
* ROC-AUC when appropriate
* PR-AUC when appropriate
* confusion matrix
* scenario-level detection

Because suspicious behavior may be a minority class, do not rely on accuracy alone.

Evaluate known synthetic scenarios individually where the labels support it.

The evaluation should reveal:

* what Prysm detects well
* what Prysm misses
* which scenarios are difficult
* which features are useful
* whether labels are reliable
* whether models rely on synthetic artifacts
* whether leakage exists

---

# 13. THINK BEYOND THE CHECKLIST

You are expected to analyze the actual data and think like a senior ML/data engineer.

If you discover a significant modeling problem or opportunity not explicitly listed here, investigate it.

Examples could include:

* a feature that looks predictive but is actually leakage
* a synthetic-generation artifact
* severe class imbalance
* suspiciously deterministic labels
* a feature that requires a minimum history
* an unexpected behavioral pattern
* a better aggregation strategy
* an important missing feature
* a problem that would make later GNN training unreliable

You may make small improvements when they directly strengthen this phase.

Do not expand into unrelated architecture.

---

# 14. STANDARDIZED INTELLIGENCE OUTPUTS

All intelligence components should produce structured outputs.

Create clear contracts for:

```text
FeatureSet
RuleFinding
AnomalyPrediction
ModelPrediction
EvaluationResult
```

A future component should be able to consume these outputs without knowing how another component was implemented.

For example:

```text
Rule Engine
      ↓
RuleFinding

Anomaly Model
      ↓
AnomalyPrediction

Behavior Model
      ↓
ModelPrediction
```

Do NOT combine these into the final Prysm risk score yet.

---

# 15. ENGINEERING PRINCIPLES

Keep the system:

* modular
* simple
* configurable
* reproducible
* explainable
* testable
* data-driven

Prefer a small number of strong components over many weak models.

Do not introduce technology merely because it sounds advanced.

Do not build deep learning just to call the system “AI.”

The intelligence must be justified by measurable behavior.

---

# 16. TESTING

Create focused tests for:

* cleaning decisions
* normalization
* feature calculations
* temporal windows
* missing-data handling
* rule triggering
* rule non-triggering
* anomaly inference
* model training/inference
* leakage prevention
* deterministic/reproducible outputs

Use small fixtures for unit tests.

Do not repeatedly process the entire 1.7M-row dataset for every test.

Run the relevant test suite before completion.

---

# 17. DOCUMENTATION AND PROJECT MEMORY

At the end, update:

* `ai-engine.md`
* `memory.md`
* `todo.md`

Record:

* what was actually implemented
* important architectural decisions
* feature groups
* rules created
* models created
* configuration locations
* evaluation results
* limitations
* unresolved issues
* important discoveries
* exact recommended next step

Do not claim work was completed unless verified.

Keep these files concise and useful for a future coding agent.

---

# 18. DO NOT BUILD YET

This phase must stop before:

* GNN implementation
* advanced graph ML
* final risk-score fusion
* risk calibration across all models
* evidence engine
* investigation API
* FastAPI service
* RAG
* LLM
* frontend
* mobile
* Neo4j migration
* advanced deep-learning architecture

These are later phases.

---

# 19. DEFINITION OF DONE

Phase 2 is complete when:

1. Phase 1 outputs are successfully consumed.
2. Necessary additional cleaning is complete.
3. Necessary normalization is complete.
4. Model-specific preprocessing is reproducible.
5. Core intelligence features exist.
6. Configurable rules exist.
7. Anomaly detection baseline works.
8. Supervised ML baseline works where labels support it.
9. Leakage controls are verified.
10. Evaluation is reproducible.
11. Intelligence outputs have clear contracts.
12. Tests pass.
13. Documentation and project memory are updated.
14. The next phase can consume these signals without redesigning this layer.

The final conceptual output is:

```text
TRUSTED DATA
     ↓
CLEAN + NORMALIZED DATA
     ↓
MODEL-READY FEATURES
     ↓
┌───────────────────────────────┐
│ Transaction Intelligence      │
│ Behavioral Intelligence       │
│ Velocity Intelligence         │
│ Foreign-Income Intelligence   │
│ Configurable Rules            │
│ Anomaly Detection             │
│ Baseline Supervised ML        │
└───────────────┬───────────────┘
                ↓
       STANDARDIZED SIGNALS
                ↓
            EVALUATION
```

Do not produce the final Prysm risk score.

Do not continue into the GNN/risk-fusion phase.

**When the Definition of Done is satisfied, stop and report exactly what was implemented, what was discovered, and what Phase 3 should build next.**
