# Phase 1 benchmark generator

Run from the repository root:

```powershell
python -m generator.prysm_benchmark generate
python -m generator.prysm_benchmark validate
python -m generator.prysm_benchmark export --output ai-engine/runs/benchmark-v1/data/processed
python -m pytest ai-engine/tests/test_benchmark.py -q
```

Read the [dataset contract](../../data/benchmarks/prysm-benchmark-v1/DATASET_MANIFEST.md) for entity fields, cases, assumptions, label cutoffs and compatibility. Read the [handoff](../../PHASE1_STATE.md) before Phase 2.

Read the implementation in this order:

1. `config.json`: seed, size, time splits and invented FX assumptions.
2. `contract.py`: seven explicit schemas and eight paired scenario definitions.
3. `generate.py`: local seeded randomness, entities, ordinary history, observation behavior, separate labels.
4. `validate.py`: references, lifecycles, geography, splits and evidence checks for both classes.
5. `storage.py`: checksums, immutable staging and loading.
6. `compatibility.py`: projection into existing AI interfaces without training.
7. `__main__.py`: the three CLI commands.

This module is the active **small benchmark** generator for the new six-phase work. The original `synthetic-financial-generator`, `ground-truth-repair`, `ground-truth-scenario-generation` and standalone `sythethic-modelizer` remain historical/isolated. Their old datasets and runtime artifacts are not deleted or silently replaced.
