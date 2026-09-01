# PRYSM AI — STEP 4

# SCENARIO DATA INTEGRATION → RETRAINING → VALIDATION

## MISSION

The generator-side scenario regeneration task has produced a new, validated synthetic evaluation population.

The new dataset contains:

* 7,000 labeled entities
* 3,500 positive observations
* 3,500 negative observations
* 7 scenario families
* 500 observations per scenario
* 747,582 total transactions
* 46,094 evidence transactions
* valid entity affiliation
* valid temporal boundaries
* zero fabricated transaction IDs
* zero temporal violations
* zero invalid affiliations
* deterministic generation
* unchanged existing schemas

The objective of this task is to connect this new dataset to the existing Prysm AI Engine and determine how much the intelligence system improves when evaluated against correctly aligned scenario data.

This is NOT a new architecture phase.

The existing Phase 1, Phase 2, Phase 2.5, and Phase 3 implementations should be reused.

---

# 1. READ FIRST

Before modifying anything, read:

* `memory.md`
* `todo.md`
* `ai-engine.md`
* `PHASE_2_REPORT.md`
* `LABEL_ALIGNMENT_REPORT.md`
* `INTELLIGENCE_CONTRACTS.md`
* `DATA_CONTRACTS.md`
* `FEATURE_POLICY.md`
* `GRAPH_RISK_EVIDENCE.md`
* existing Phase 2 build scripts
* existing Phase 3 build scripts
* existing evaluation configuration
* generator scenario-generation README/report
* generator scenario-generation validation report

Understand how the existing AI engine currently discovers:

* processed data
* ground truth
* transaction data
* labels
* prediction snapshots
* graph inputs

Do not assume the paths.

---

# 2. IMPORTANT ARCHITECTURAL RULE

Do NOT rebuild:

* Phase 1
* Phase 2
* Phase 2.5
* Phase 3

Reuse the existing architecture.

Only make the smallest integration changes required to allow the new scenario dataset to flow through the existing pipelines.

Do not duplicate feature engineering.

Do not create a second competing ML pipeline.

Do not create a second graph implementation.

---

# 3. FIND THE NEW DATA

Locate the output of:

```text
generator/ground-truth-scenario-generation/
```

including:

* augmented transaction data
* repaired/augmented ground truth
* scenario metadata
* manifest
* validation report

Verify the dataset before using it.

Do not trust the generation report blindly.

Programmatically verify:

* schema compatibility
* transaction IDs
* account IDs
* entity IDs
* timestamps
* scenario labels
* evidence references
* positive/negative distribution

---

# 4. CREATE A CLEAN AI-ENGINE DATA BOUNDARY

The AI engine should consume the new scenario dataset through a clear, explicit data boundary.

Do not copy data unnecessarily.

Do not overwrite the original raw datasets.

If a processed/canonical representation is required, generate it through the existing Phase 1/processing architecture.

Keep the original dataset available for comparison.

Clearly identify:

```text
ORIGINAL DATA
vs.
SCENARIO-AUGMENTED DATA
```

in manifests/configuration.

---

# 5. RUN PHASE 2.5 ALIGNMENT AGAIN

Run the existing label-alignment logic against the new ground truth.

Do not rewrite the alignment logic unless an actual compatibility issue is discovered.

Verify:

* entity affiliation
* account ownership
* transaction evidence
* scenario timing
* prediction cutoff
* future-information exclusion
* sufficient history
* positive/negative population
* scenario distribution
* entity overlap

The resulting predictive population should now be meaningful.

If alignment rejects observations, investigate the actual reason.

Do not simply loosen validation rules.

---

# 6. REBUILD PHASE 2 FEATURES

Run the existing Phase 2 intelligence pipeline using the new valid prediction population.

Recreate:

* transaction features
* behavioral features
* velocity features
* foreign-currency features
* relationship features
* preprocessing artifacts

Use the existing feature contracts.

Do not leak:

* scenario
* target
* ground-truth metadata
* future evidence
* post-cutoff information

Every feature must remain available at the prediction cutoff.

---

# 7. RETRAIN EXISTING BASELINE MODELS

Retrain the existing Phase 2 models against the new valid dataset.

Use the existing:

* anomaly model
* supervised baseline

Do not immediately introduce new models.

The purpose of this task is to measure the improvement created by fixing the data problem.

Preserve the same model/evaluation methodology where appropriate so the comparison is meaningful.

---

# 8. RE-EVALUATE RULES

Run the existing configurable rule engine against the new dataset.

Do not modify thresholds merely to improve metrics.

First evaluate the existing rules as they are.

Then, only if the new scenario definitions clearly reveal a legitimate configuration mismatch, document the mismatch and make a minimal justified configuration correction.

Keep rule configuration centralized.

Report rule performance by scenario.

---

# 9. RE-RUN GRAPH INTELLIGENCE

Run the existing Phase 3 graph pipeline against the scenario-augmented dataset.

Verify:

* graph construction
* node counts
* edge counts
* temporal graph filtering
* graph features
* investigation subgraphs
* GNN representation generation

Do not redesign the GNN.

Do not claim supervised GNN performance unless the new ground truth passes all Phase 2.5 validity checks.

---

# 10. SUPERVISED GNN EVALUATION

If the new scenario dataset passes temporal and provenance validation, determine whether it now supports legitimate supervised GNN training/evaluation.

If yes:

* train using valid labels
* maintain entity/temporal separation
* prevent scenario metadata leakage
* evaluate on held-out entities where appropriate
* report ROC-AUC
* PR-AUC
* precision
* recall
* F1
* confusion matrix
* scenario-level results

If it does not support a particular GNN task, do not force it.

Document why.

---

# 11. COMPARE OLD VS NEW

This is one of the most important outputs.

Create a comparison:

```text
                         ORIGINAL       NEW
------------------------------------------------
Label prevalence
Valid predictive rows
History coverage
Supervised ROC-AUC
Supervised PR-AUC
PR-AUC lift
Anomaly ROC-AUC
Rule ROC-AUC
Scenario detection
GNN evaluation
```

Preserve the original Phase 2 results.

Do not overwrite history.

The report must clearly distinguish:

```text
OLD INVALID/WEAK EVALUATION
```

from:

```text
NEW VALID SCENARIO EVALUATION
```

---

# 12. SCENARIO-LEVEL EVALUATION

Evaluate the new system separately for each scenario:

```text
rapid_movement
transaction_burst
structuring
foreign_currency_change
behavioral_shift
counterparty_change
shared_device_activity
```

Determine:

* detection rate
* precision
* recall
* F1
* ranking quality
* rule coverage
* feature usefulness

Do not allow the aggregate score to hide a scenario that performs poorly.

---

# 13. DO NOT OPTIMIZE FOR 90% BLINDLY

The project goal is strong performance, but do not manipulate the system to reach an arbitrary metric.

If performance is:

```text
95%
```

explain why.

If performance is:

```text
65%
```

explain why.

If performance is:

```text
99%
```

investigate whether the scenario generation created leakage or overly obvious synthetic artifacts.

A very high score is not automatically good.

Check whether the model is learning:

* legitimate behavior
* scenario structure
* generator artifacts
* hidden metadata
* trivial thresholds

---

# 14. LEAKAGE AUDIT

Before accepting high performance, actively search for leakage.

Check whether positive/negative observations differ because of:

* scenario metadata
* timestamps that reveal labels
* artificial transaction counts
* generated entity IDs
* unique patterns created only for positive cases
* deterministic scenario fingerprints
* fields unavailable at prediction time
* augmentation artifacts

Inspect important feature distributions between classes.

If a suspiciously predictive feature is found, investigate it.

Do not remove a feature solely because it is predictive.

Remove or restrict it only when evidence shows it violates the prediction contract or represents an unintended generator artifact.

---

# 15. DATASET SCALE AND GENERALIZATION

The new population is 7,000 observations.

Determine whether this is sufficient for the current models.

Do not automatically generate more data.

If results are unstable, inspect:

* scenario counts
* entity diversity
* temporal diversity
* transaction diversity
* class balance
* repeated structural patterns

Only recommend additional generation if the evidence shows it is necessary.

---

# 16. FUSION

Run the existing Phase 3 signal-fusion layer.

Verify that:

```text
Phase 2 signals
+
Graph signals
+
GNN signals
```

can be combined without breaking their contracts.

Do not recalibrate the final risk system merely to increase scores.

If calibration is now scientifically supportable, document it separately.

If it is not, retain the existing uncalibrated status.

---

# 17. EVIDENCE

Run the existing evidence engine against representative investigations.

Verify that high-risk/suspicious signals can be traced to:

* transactions
* entities
* relationships
* timestamps
* feature measurements
* rule findings
* graph findings
* model signals

No evidence may be fabricated.

Generate at least several representative investigation outputs across different scenario types.

---

# 18. ACCEPTANCE CRITERIA

The new dataset is considered successfully integrated only if:

* Phase 2.5 alignment passes
* entity affiliation is valid
* temporal boundaries are valid
* no future information enters features
* supervised evaluation becomes legitimately estimable
* existing Phase 2 models can train
* existing graph pipeline can consume the data
* graph construction remains valid
* GNN pipeline remains reproducible
* signal fusion remains functional
* evidence remains traceable
* tests pass

---

# 19. IMPORTANT FAILURE CONDITION

If the new dataset still fails alignment or produces suspiciously strong metrics:

DO NOT hide the problem.

Investigate.

Determine whether the issue is:

* generator design
* scenario definition
* feature leakage
* entity splitting
* temporal splitting
* insufficient history
* label construction
* model implementation

Make only corrections that are justified by evidence.

If the dataset itself needs another generator-side correction, document it clearly rather than silently modifying the AI engine to accommodate bad data.

---

# 20. REPRODUCIBILITY

Record:

* source dataset manifest/hash
* scenario dataset manifest/hash
* configuration
* feature version
* model configuration
* split configuration
* evaluation timestamp
* artifact versions

Running the pipeline twice with identical inputs/configuration should produce deterministic or appropriately reproducible results.

---

# 21. TESTING

Run:

* existing Phase 2 tests
* existing Phase 2.5 tests
* existing Phase 3 tests
* new integration tests where necessary

Add focused tests only where the new dataset integration exposes a genuine missing case.

Do not rewrite the test architecture.

---

# 22. DOCUMENTATION

Create a clear integration/evaluation report containing:

1. Dataset used
2. Alignment results
3. Feature population
4. Model results
5. Rule results
6. Graph results
7. GNN results
8. Fusion results
9. Evidence results
10. Leakage audit
11. Before/after comparison
12. Scenario-level performance
13. Limitations
14. Recommendation

Use exact machine-readable metrics.

Do not present invalid old metrics as current performance.

---

# 23. PROJECT MEMORY

Update:

* `memory.md`
* `todo.md`
* `ai-engine.md`

Record:

* new dataset integration
* whether supervised evaluation is now valid
* exact measured results
* major discoveries
* remaining weaknesses
* model limitations
* next recommended engineering step

Keep the continuity files concise.

---

# 24. NO UNNECESSARY ARCHITECTURAL CHANGES

Do not:

* rewrite the AI engine
* rewrite the graph
* replace the GNN
* replace the rule engine
* redesign the feature system
* introduce new frameworks unnecessarily
* modify frontend/backend
* modify the generator

This phase is primarily:

```text
NEW VALID DATA
      ↓
EXISTING AI ENGINE
      ↓
RETRAIN
      ↓
EVALUATE
      ↓
COMPARE
```

---

# 25. FINAL REPORT FORMAT

At completion, report:

```text
Dataset integration:
READY / FAILED

Alignment:
...

Predictive population:
...

Positive:
...

Negative:
...

Supervised:
ROC-AUC:
PR-AUC:
Precision:
Recall:
F1:

Anomaly:
ROC-AUC:

Rules:
ROC-AUC:
Findings:

GNN:
Status:
Evaluation validity:
Metrics:

Scenario performance:
...

Leakage audit:
PASS / FAIL

Graph validation:
PASS / FAIL

Evidence validation:
PASS / FAIL

Tests:
...

Overall conclusion:
...

Next step:
...
```

---

# STOPPING BOUNDARY

Do NOT proceed into:

* production API
* backend integration
* frontend
* RAG
* LLM
* chatbot
* TTS
* deployment
* real-time streaming

This task ends after the new scenario dataset has been integrated, the existing AI intelligence has been retrained/re-evaluated, the results have been compared, and the AI engine's current scientific status has been documented.

Do not continue beyond this boundary.

# FINAL PRINCIPLE

The purpose of this phase is to answer one question honestly:

> **Now that Prysm has correctly affiliated, temporally valid scenario data, does the intelligence architecture actually detect the behaviors it was designed to detect?**

Let the data answer that question.

Do not force the answer.
