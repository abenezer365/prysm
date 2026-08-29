# PRYSM AI — STEP 2.5

# LABEL & TEMPORAL ALIGNMENT

## Mission

Fix the main weakness discovered during Phase 2: the current ground-truth labels are heavily anomalous (~76.5%), while model performance against pre-cutoff historical behavior is close to random.

Do **not** manipulate labels to improve metrics.

The goal is to determine whether the current labels, scenario timing, historical coverage, and prediction snapshots are correctly aligned with the information available at prediction time, then make the smallest defensible changes necessary to create a reliable foundation for future GNN and risk modeling.

---

## Read First

Before changing anything, read:

* `memory.md`
* `todo.md`
* `ai-engine.md`
* `PHASE_2_REPORT.md`
* `INTELLIGENCE_CONTRACTS.md`
* `DATA_CONTRACTS.md`
* `FEATURE_POLICY.md`
* `evaluation/evaluation.json`
* the existing Phase 2 intelligence/preprocessing implementation

Do not repeat Phase 1 or Phase 2 work that is already correct.

---

## Scope

Work only inside `ai-engine/` and its existing data, model, evaluation, configuration, and documentation areas.

Do NOT inspect or modify:

* `generator/`
* `resource/`
* `resources/`
* frontend
* mobile
* unrelated project files

Do not investigate the synthetic-data generator to solve this problem.

---

# 1. INVESTIGATE THE ACTUAL PROBLEM

Trace the complete relationship:

```text
ground_truth
      ↓
scenario/event timing
      ↓
prediction cutoff
      ↓
available historical transactions
      ↓
engineered features
      ↓
target
```

Determine why the current labels have such high anomaly prevalence and why observable pre-cutoff behavior has weak discrimination.

Specifically investigate:

* when each labeled scenario actually begins
* whether the scenario occurs before, during, or after the prediction cutoff
* whether enough historical data exists before the cutoff
* whether the current snapshot represents a meaningful prediction opportunity
* whether labels describe an event that could realistically be predicted
* whether multiple labels for an entity create conflicts or duplication
* whether scenario labels are temporally aligned with features
* whether insufficient-history cases are being treated as normal/anomalous incorrectly
* whether synthetic scenario metadata leaks future information
* whether the current evaluation target is appropriate for the intended intelligence system

Do not assume the cause before verifying it.

---

# 2. DEFINE A DEFENSIBLE PREDICTION UNIT

Establish a clear concept of:

> **Entity + prediction cutoff + observable history + future target/event**

The prediction features must contain only information available at or before the cutoff.

The target must represent an event occurring after the information boundary when the intended task is predictive.

If the existing labels are better suited to retrospective detection rather than prediction, document that distinction instead of forcing them into a predictive task.

---

# 3. HANDLE INSUFFICIENT HISTORY

Identify snapshots where there is insufficient historical information to calculate meaningful behavioral or velocity signals.

Do not automatically classify these cases as normal.

Create an explicit and documented treatment such as:

* insufficient-history
* cold-start
* excluded-from-behavioral-evaluation

Choose the simplest defensible approach based on the actual data.

Ensure the treatment does not create hidden label bias.

---

# 4. FIX LABEL/SNAPSHOT ALIGNMENT

Where the current implementation is temporally misaligned, correct the snapshot/label construction.

The correction must:

* preserve ground-truth provenance
* avoid future-information leakage
* preserve entity identity
* preserve scenario meaning
* remain reproducible
* remain compatible with Phase 2 intelligence contracts

Do not invent new real-world labels.

Do not rewrite ground truth simply because the model performs poorly.

If some scenarios cannot be evaluated predictively with the available data, explicitly document that limitation rather than manufacturing a solution.

---

# 5. IMPROVE TRAINING/EVALUATION DATASET DESIGN

Create a defensible training/evaluation population for the existing Phase 2 models.

Prefer:

```text
historical information
        ↓
prediction cutoff
        ↓
features available at cutoff
        ↓
future event / aligned target
```

Maintain temporal separation between training, validation, and testing.

Maintain entity separation where required.

Ensure repeated observations do not create leakage.

Do not optimize the split merely to improve metrics.

---

# 6. RE-RUN PHASE 2 EVALUATION

After the alignment correction:

Re-run the existing Phase 2 intelligence evaluation.

Compare:

```text
BEFORE
vs.
AFTER
```

for:

* label prevalence
* available-history coverage
* supervised ROC-AUC
* PR-AUC
* PR-AUC lift over prevalence
* anomaly ROC-AUC
* rule performance
* scenario-level performance
* feature-group performance
* train/validation/test integrity

Do not hide the original results.

The comparison must remain reproducible.

---

# 7. INTERPRET THE RESULT HONESTLY

The objective is NOT:

> “Make ROC-AUC high.”

The objective is:

> “Make the prediction problem logically valid and temporally defensible.”

If performance remains weak after fixing the alignment, say so clearly.

Determine whether the remaining weakness is caused by:

* weak labels
* insufficient historical coverage
* sparse transactions
* synthetic-generation limitations
* missing features
* unsuitable prediction target
* insufficient scenario representation
* another verified cause

Recommend the next modeling improvement based on evidence.

---

# 8. PRESERVE CONFIGURABILITY

Do not hard-code new assumptions.

Where timing, history requirements, or evaluation thresholds must be configurable, use the existing configuration system.

Keep the implementation simple.

Do not create a new framework for this correction.

---

# 9. TESTING

Add or update focused tests for:

* cutoff correctness
* future-information exclusion
* scenario timing
* insufficient-history handling
* label alignment
* duplicate/overlapping labels
* deterministic dataset generation
* temporal/entity-disjoint evaluation

Use small fixtures for unit tests.

Run the relevant test suite and the complete evaluation pipeline.

---

# 10. DOCUMENTATION

Update:

* `PHASE_2_REPORT.md` or the appropriate current report
* `ai-engine.md`
* `memory.md`
* `todo.md`

Document:

* root cause discovered
* correction implemented
* prediction-unit definition
* history treatment
* label treatment
* before/after metrics
* remaining limitations
* exact recommendation for Phase 3

Do not claim improvement unless the measured results demonstrate it.

---

# STOPPING BOUNDARY

Do NOT implement:

* GNN
* graph neural networks
* final risk fusion
* final risk score
* evidence engine
* API
* RAG
* LLM
* frontend
* deep-learning architecture

This task exists only to make the **prediction/evaluation foundation defensible before Phase 3**.

---

# DEFINITION OF DONE

Stop only when:

* the cause of the weak label/history alignment has been investigated
* the prediction unit is clearly defined
* temporal leakage has been checked
* insufficient-history cases are explicitly handled
* necessary alignment corrections are implemented
* Phase 2 evaluation has been regenerated
* before/after results are documented
* tests pass
* project continuity files are updated
* remaining limitations are clearly documented
* Phase 3 has a clear starting point

If the evidence shows that the current synthetic labels fundamentally cannot support a particular predictive task, **do not fabricate a fix**. Document the limitation and identify the strongest defensible modeling task supported by the existing data.

When all requirements are satisfied, stop.
