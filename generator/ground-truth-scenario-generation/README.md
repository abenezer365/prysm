# Ground-Truth Scenario Generation

This isolated generator-side capability creates a statistically useful, leakage-safe scenario dataset from existing Prysm entities, accounts, devices, and transaction history. It does not modify the original synthetic generator, original Parquet files, AI engine, models, or graph.

## Design

- Strategy: controlled scenario injection with matched normal generation.
- Subjects: one existing Person/Company owner and one lifecycle-valid existing account per label.
- History gate: at least five completed transactions before the prediction cutoff.
- Timeline: cutoff, then scenario start at least one day later, then evidence inside a bounded 14-day horizon.
- Splits: entity-disjoint train, validation, and test populations in forward temporal cutoff bands.
- Balance: 3,500 positive and 3,500 normal observations. Each of seven positive scenario families contributes 500 rows.
- Variation: low, medium, and high intensities; varied amounts, intervals, counterparties, currencies, channels, and counts.
- Counterparties and devices: existing source IDs only. No new entity, account, or device IDs are created.
- Negatives: entities with sufficient history receive sparse, spaced, baseline-scaled activity using familiar counterparties where possible. They are generated through the same transaction path as positives to avoid an obvious source fingerprint.

Scenario families are `rapid_movement`, `transaction_burst`, `structuring`, `foreign_currency_change`, `behavioral_shift`, `counterparty_change`, and `shared_device`. The generator independently measures and validates the behavioral claim for every label.

This is synthetic scenario data for system evaluation. It is not evidence that these patterns represent real fraud or AML outcomes.

## Regenerate

From the repository root:

```powershell
python generator/ground-truth-scenario-generation/generate_scenarios.py
```

The default command builds the complete dataset twice in memory and fails on any deterministic mismatch. Optional paths are available through `--source-dir`, `--output-dir`, and `--config`.

## Output

`output/data/` is a complete standalone nine-file dataset. Unchanged source datasets are byte-for-byte copies; `transactions.parquet` contains the original 700,000 rows plus generated scenario activity, and `ground_truth.parquet` contains the new 7,000-row prediction population.

Supplementary files:

- `output/scenario_metadata.parquet`: cutoff, split, subject account, intensity, history, evidence, auxiliary activity, and measured provenance.
- `output/validation_report.json`: original/repaired/augmented comparison and readiness result.
- `output/MANIFEST.json`: deterministic checksums and sizes.
- `output/config.json`: exact isolated generation configuration.

The ground-truth and transaction schemas remain exactly compatible with the original datasets. Supplementary metadata is deliberately separate and must not be used as a model feature.

## Tests

Generate the output first, then run:

```powershell
python -m pytest generator/ground-truth-scenario-generation/tests -q
```

The tests cover source preservation, schemas, entity/account/transaction affiliation, timing, scenario behavior, negatives, class balance, split isolation, history sufficiency, determinism, fabricated IDs, and manifest integrity.
