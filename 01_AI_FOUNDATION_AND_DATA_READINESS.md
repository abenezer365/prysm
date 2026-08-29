# PRYSM AI — AI FOUNDATION & DATA READINESS

## Mission

You are the first engineering agent working inside the **Prysm AI** project.

Prysm AI is an Ethiopia-first financial intelligence system designed to detect and explain unusual financial behavior, fraud patterns, AML/money-laundering patterns, transaction anomalies, behavioral changes, foreign-income anomalies, and relationship/network risks.

The raw synthetic datasets have already been generated and documented in a data manifest. **Do not repeat basic dataset discovery that the manifest already contains.**

Your mission is to turn the existing raw datasets into a **trustworthy, consistent, model-ready foundation for the future AI/ML and graph systems.**

## Scope — IMPORTANT

Work **ONLY inside:**

* `ai-engine/`
* `ai-engine/data/raw/`
* `ai-engine/data/DATASET_MANIFEST.md` as a data manifest destiny

Do NOT inspect or modify:

* `resource/`
* `resources/`
* `generator/`
* synthetic-data generation code
* logos, PDFs, documents, design files, frontend, mobile, or unrelated project areas

Do not spend tokens investigating those areas.

## What You Must Do

Starting from the existing manifest and raw Parquet data:

1. Validate actual referential integrity across entities and polymorphic relationships.
2. Investigate duplicate/ambiguous entities and determine a safe canonicalization strategy.
3. Audit temporal consistency, date ordering, overlapping relationships, and account/transaction lifecycles.
4. Validate financial consistency, currencies, ETB conversions, amounts, balances, and impossible values.
5. Analyze missingness **by meaning and behavior**, not simply by percentage.
6. Audit `ground_truth` for label quality, conflicts, duplicates, ambiguity, and possible target leakage.
7. Identify features that future fraud, AML, anomaly, behavioral, foreign-income, and GNN systems can safely use.
8. Identify dangerous or misleading features that should not enter models.
9. Define the canonical data contracts needed by future feature engineering and graph construction.
10. Implement only foundational preprocessing/normalization that is genuinely necessary.

## Deliverables

Produce concise, durable documentation inside `ai-engine/` covering:

* validated data assumptions
* canonical entity/link decisions
* preprocessing decisions
* label/leakage findings
* modeling risks
* recommended next-stage feature/graph requirements

Create model-ready processed outputs **only where necessary**.

## Boundaries

Do not build ML models, GNNs, sophisticated rules, scoring, or APIs yet.

Do not endlessly optimize.

Stop when the raw data has a reliable, documented foundation for the next AI phase.

## Definition of Done

The next engineer should be able to enter `ai-engine/` and clearly understand:

**what data can be trusted, what must be transformed, what must be excluded, how entities connect, and what the next modeling phase should consume.**
