# Phase 1 technical handoff — 2026-09-05

Current handoff: [PHASE3_STATE.md](PHASE3_STATE.md). This document preserves the earlier phase decisions.

**Completed: the dataset and data pipeline phase of the new six-phase improvement plan.** This file records the Phase 1 handoff. Phase 2 is now also complete; read [PHASE2_STATE.md](PHASE2_STATE.md) for current intelligence, artifacts, validation and the Phase 3 entry point. Legacy `prysm_ai` source paths cited below now resolve through the compatibility bridge to `ai-engine/src/prysm_ai/v1/`.

## Read first

The source of truth is [data/benchmarks/prysm-benchmark-v1/DATASET_MANIFEST.md](data/benchmarks/prysm-benchmark-v1/DATASET_MANIFEST.md). Machine provenance is the adjacent `MANIFEST.json`; validation counts are in `validation_report.json`. The exact config is copied beside the data.

## Implemented state

- Generator: `generator/prysm_benchmark/`; entry point `python -m generator.prysm_benchmark`; source config `generator/prysm_benchmark/config.json`, seed **20260905**, `cases_per_pattern_per_split=10`.
- Canonical source: `data/benchmarks/prysm-benchmark-v1/`. Seven files: `persons.parquet` (720), `companies.parquet` (240), `institutions.parquet` (3), `accounts.parquet` (960), `relationships.parquet` (720), `transactions.parquet` (4,320), `ground_truth.parquet` (240). Total **7,203 rows / 240 cases**, approximately 125 KB of Parquet.
- Class distribution: **216 normal / 24 suspicious**. Eight suspicious types (`structuring`, `velocity`, `amount`, `geography`, `network`, `family`, `tax`, `theft`), three cases each; eight matched benign types, 27 cases each. Every split has 72 normal and 8 suspicious cases.
- Relationships: account ownership joins `(owner_type, owner_id)` to Person/Company; accounts reference institutions; transactions reference sender/receiver accounts; typed `family`, `beneficial_owner`, and `employer_employee` edges connect people and businesses. Ground truth references entire isolated case groups plus exact evidence IDs. No family inference from names.
- Types: explicit Arrow schemas in `contract.py`, UTC microsecond dates, finite currency amounts rounded to cents, native amount plus explicit synthetic FX and checked ETB equivalent, geographic residence/business/event fields, nullable lifecycle ends and physical-event device IDs. No labels or computed risk scores in behavior tables.
- Evaluation: retrospective detection at `as_of`, after the observation week and company sales declaration. Train cutoff `2025-04-12T10:00:00Z`; validation `2025-08-10T10:00:00Z`; test `2025-12-11T10:00:00Z`. Cases have disjoint people/businesses/accounts and forward time splits; institutions are shared infrastructure.
- Local derived export exists at `ai-engine/runs/benchmark-v1/data/processed/` (ignored run artifacts, regenerated with the command below). Its manifest references the source manifest hash. It contains people/company/bank catalogs, accounts, transaction/relationship edges, empty invoices, and separate labels. No model, signal, GNN or live-service artifacts were built.

## Commands and validation

From repository root:

```powershell
python -m generator.prysm_benchmark generate
python -m generator.prysm_benchmark validate
python -m generator.prysm_benchmark export --output ai-engine/runs/benchmark-v1/data/processed
python -m pytest ai-engine/tests/test_benchmark.py -q
```

Generation validates before publication and refuses to overwrite different data/config/code. Repeating generation on an identical snapshot verifies it; use a fresh `--output` for changes. Export refuses an existing target: it was already run in this workspace. Use a fresh output path for another export rather than mixing runs. Validators reject corrupt records; no implicit cleaning mutates source facts.

Verification: **43 Phase 1 tests passed**, covering deterministic logical and physical regeneration in this environment, alternate seeds, manifest tampering, schema/value/reference/lifecycle/geographic corruption, positive and negative scenario evidence, split leakage, legacy normalization/features, future-event exclusion, graph endpoints/cutoffs, person-search dataset version and graph display catalogs. A regression run also passed **22 existing tests** (57 combined before the final eight benign-control cases were added). Three existing tests requiring complete historical model artifacts were deliberately excluded; no full live investigation/inference or service startup was performed. The local Pydantic 2 installation emitted four existing deprecation warnings from the API schema; the project's declared dependency is Pydantic 1.x. No dependency changes were made.

Regression command used:

```powershell
python -m pytest ai-engine/tests/test_benchmark.py ai-engine/tests/test_data_readiness.py ai-engine/tests/test_intelligence.py ai-engine/tests/test_graph_intelligence.py ai-engine/tests/test_label_alignment.py ai-engine/tests/test_api.py -q --tb=short -k 'not ready_reports_real_artifacts and not real_existing_engine_analysis and not full_dataset_person_search'
```

## Inspection findings and compatibility decisions

The original nine-table generator independently sampled labels/references and optionally injected structural corruption. The existing scenario augmentation depends on that large dataset and creates a balanced benchmark. Reusing either as the small source would preserve unnecessary dependencies and a different evaluation contract. Both remain intact for historical reproducibility. The standalone modelizer remains isolated.

Reuse: existing typed identities, `load_phase1`, `normalize_transactions`, `AsOfFeatureBuilder`, `CanonicalGraphBuilder`, `GraphStore`, Parquet and manifest provenance. A single explicit exporter maps the new contract to processed interfaces. There was no AI/backend/frontend redesign.

Exact compatibility changes:

- `generator/prysm_benchmark/compatibility.py`: source-to-processed projection with geography preserved, company/bank catalogs, nullable unknown nationality and empty invoice evidence. Legacy exported `pattern_start=as_of` is a **detection cutoff**, with actual observation boundaries retained as `window_start/window_end` and an explicit evaluation scope. Never pass this projection into the old future-label alignment workflow.
- `ai-engine/src/prysm_ai/features.py`: handle an empty invoice lookup with a typed missing-date series; avoids pandas errors without inventing invoices.
- `ai-engine/api/runtime.py`: person-search version comes from processed manifest when available; graph labels use the selected processed catalogs, and versioned runs do not fall back to unrelated raw catalogs. Historical fallback remains for unversioned old artifacts.
- The old `build_foundation.py`, server full ingestion, active startup artifact root and trained models still use their historical contracts. New source inputs use the explicit export path above.

## Remaining work and Phase 2 entry

Read the dataset manifest, then `P2_AI_Intelligence_&_Graph_Engine.md`. Build as-of features/evidence over the actual contract. Existing models do not consume geographic coordinates or company declaration periods; those fields are available for Phase 2. Enforce declared splits and cutoff-safe graph neighborhoods. Shared institution nodes must not transmit held-out labels/features into training. Keep invoice features explicitly unavailable until real invoice facts exist.

The small dataset has simple repeated histories, completed transactions, no balance ledger, fictional fixed FX/income assumptions, limited occupations and only one positive of each type per split. Normal labels mean no suspicious intent injected. These constraints prevent meaningful real-world accuracy or calibration claims. Do not silently deploy the old models against this new distribution.

After all six phases, build the requested 1–2 million-row synthetic generator using this entity/behavior/ground-truth separation, streaming output and much richer reviewed scenarios. The current generator deliberately caps at 480 cases and is not that scale generator. More rows do not by themselves prove label validity or real-world performance.
