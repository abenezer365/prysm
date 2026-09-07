# PHASE 3 — EVALUATION & MODEL OPTIMIZATION

## ROLE

You are implementing Phase 3 of Prysm Intelligence.

Assume:

* Phase 1 dataset/data pipeline is complete.
* Phase 2 intelligence engine is complete.
* The repository contains a current technical state/manifest describing both.

Read those first.

Your job is to **measure, validate and improve the existing intelligence**, not redesign it.

---

## 1. PRIMARY OBJECTIVE

Determine how well Prysm performs on the controlled benchmark dataset and identify exactly where it fails.

Evaluate the actual implemented:

* Rule engine
* Anomaly engine
* Graph/GNN
* Family/network analysis
* Fusion/risk ranking

Do not add new models unless evaluation shows a genuine need.

---

## 2. BUILD A REAL EVALUATION PIPELINE

Create a reproducible evaluation process that clearly separates:

```text
training
validation
testing/evaluation
```

Use the ground-truth scenarios created in Phase 1.

Do not evaluate a model on the same data in a way that makes the result misleading.

The evaluation pipeline should produce machine-readable results that can be inspected later.

---

## 3. USE THE RIGHT METRICS

Choose metrics according to each model's actual task.

For classification, use appropriate metrics such as:

```text
precision
recall
F1
confusion matrix
ROC-AUC / PR-AUC where useful
```

For anomaly/ranking behavior, include appropriate measures such as:

```text
precision@K
recall@K
false positives
```

For the GNN, evaluate its actual graph-learning task rather than forcing generic metrics onto it.

Do not rely on accuracy alone because the dataset is intentionally imbalanced.

---

## 4. TRAINING EXPERIMENTS

For trainable models, make the important parameters easy to experiment with.

Where applicable, expose things such as:

```text
epochs
batch size
learning rate
```

and any other parameter that materially affects performance.

Do not invent training parameters for models that do not use them.

Run controlled experiments and compare results instead of changing many variables blindly.

---

## 5. PERFORMANCE VISUALIZATION

Generate useful evidence of model behavior.

Where applicable:

```text
training loss
validation loss
precision
recall
F1
```

across epochs.

Also produce the visualizations necessary to understand:

* class distribution
* score distributions
* false positives
* false negatives
* suspicious vs normal behavior
* ranking quality

Keep visualizations focused on understanding the system, not decoration.

---

## 6. INVESTIGATOR OUTPUT

Verify the ranking system produces something useful such as:

```text
Top N suspects
entity
overall score
risk level
score breakdown
supporting evidence
ground-truth status
```

Make N configurable.

Check whether high-risk entities are actually appearing near the top.

---

## 7. FAILURE ANALYSIS

This is a major deliverable.

Do not stop at:

> "F1 = 0.87"

Determine:

```text
Which cases failed?
Why?
Which engine missed them?
Which engine generated false positives?
Which features appear weak?
Which scenario types are difficult?
```

Use those findings to make **targeted improvements** to the existing system.

Do not rewrite the architecture unless the evidence requires it.

---

## 8. MODEL SELECTION

Compare reasonable configurations of the existing models.

Choose the simplest configuration that provides strong and stable results.

Do not select a model because it is more complicated or technically fashionable.

Document:

```text
configuration
metric results
reason for selection
known weaknesses
```

---

## 9. IMPORTANT LIMIT

The dataset is intentionally small.

Therefore, do not present the benchmark results as proof that Prysm will perform identically on a real national-scale dataset.

The purpose of this phase is:

```text
validate intelligence
find weaknesses
establish baseline
prove reproducibility
```

Large-scale performance testing comes later.

---

## 10. DO NOT IMPLEMENT PHASE 4

Do not redesign:

* backend
* PostgreSQL architecture
* authentication
* RAG
* local LLM
* frontend
* content/UI

Only create the evaluation outputs/interfaces needed for later integration.

---

## 11. ACCEPTANCE CRITERIA

Phase 3 is complete when:

1. Every implemented intelligence component has an appropriate evaluation method.
2. Results are reproducible.
3. Training/validation/testing are meaningfully separated where applicable.
4. Metrics are generated automatically.
5. Model behavior can be visualized.
6. Top-risk entities can be ranked and inspected.
7. False positives and false negatives can be identified.
8. Weaknesses are documented.
9. The simplest strong configuration is selected.
10. No unsupported performance claims are made.

---

## 12. STATE UPDATE

Update the root technical state file with:

```text
evaluation pipeline
datasets/splits
metrics
experiments
selected configurations
training curves
failure analysis
known limitations
commands
next phase entry point
```

Record actual measured results, not descriptions of what the code is supposed to do.

---

## FINAL RULE

Read the Phase 1/2 manifests and current implementation first.

Work only on evaluation and justified optimization.

Do not redesign working intelligence without evidence.

Measure first, change second.

Complete Phase 3, update the technical state, and STOP.
