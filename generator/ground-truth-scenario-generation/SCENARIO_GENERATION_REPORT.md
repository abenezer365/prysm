# Ground-Truth Scenario Generation Report

## Outcome

The isolated augmented dataset is model-ready at the data-contract level. No model was trained or tuned during this task.

| Population | Total | Supported | Unsupported | Positive | Negative |
|---|---:|---:|---:|---:|---:|
| Original | 5,000 | 0 | 5,000 | 3,801 | 1,199 |
| Relationship repair | 5,000 | 647 | 4,353 | 1 supported | 646 supported |
| Scenario generation | 7,000 | 7,000 | 0 | 3,500 | 3,500 |

The generated population contains 500 cases for each positive family and 3,500 normal observations. Positive prevalence is deliberately 50% for controlled evaluation, not as an estimate of real-world fraud prevalence.

## Coverage and validity

- Unique labeled entities: 7,000.
- Evidence transactions: 46,094.
- Generated transactions: 47,582; augmented transaction total: 747,582.
- Cutoffs: 2024-06-01 through 2025-08-15.
- Scenario activity: 2024-06-02 through 2025-08-29.
- Invalid entity affiliations: 0.
- Invalid transaction affiliations: 0.
- Fabricated transaction IDs: 0.
- Temporal violations: 0.
- Pre-cutoff evidence rows: 0.
- Schema violations: 0.
- Invalid generated account endpoints: 0.
- Generated account lifecycle violations: 0.
- Scenario-behavior validation failures: 0.
- Entity overlap between splits: 0.
- Rows with at least five pre-cutoff completed transactions: 7,000.

## Split distribution

- Train: 2,450 positive and 2,450 negative.
- Validation: 525 positive and 525 negative.
- Test: 525 positive and 525 negative.

Cutoff ranges move forward from train to validation to test, and each typed entity appears exactly once.

## Interpretation

Model-readiness status: **READY**.

This means the population now has valid typed subjects, sufficient pre-cutoff history, explicit future evidence, measurable scenario behavior, two classes in every entity-disjoint temporal partition, and no reference/schema violations. It does not mean that a model will achieve high accuracy or that the simulated scenarios represent real fraud. Supplementary scenario metadata is provenance and must remain excluded from model features.
