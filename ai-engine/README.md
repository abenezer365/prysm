# Phase 5 HTTP integration

The active server is `api.intelligence:app` (started by `python start.py`). It loads the selected portable Phase 3 bundle, requires `AI_ENGINE_API_KEY`, and exposes protected `/v2/investigate`, `/v2/rank`, `/v2/people/search` and `/ready`. Historical `api.app` remains only for archived v1 regression tests. See [PHASE5_STATE.md](../PHASE5_STATE.md) for backend integration.

# Prysm AI Engine

Start with [the Phase 3 handoff](../PHASE3_STATE.md), [the measured report](reports/phase3/REPORT.md), and [the engine guide](INTELLIGENCE_V2.md).

The teachable flow is: **validated facts → cutoff-safe features and graph → rules, anomaly, network, GNN → evidence and ranked review priorities**. Labels are used only for training and evaluation. Scores are not fraud probabilities.

From the repository root:

```powershell
# First-time preparation; existing output directories are never overwritten.
python ai-engine/scripts/run_intelligence.py build
python ai-engine/scripts/run_intelligence.py evaluate --top-n 10

# These commands default to the Phase 3 selected model.
python ai-engine/scripts/run_intelligence.py investigate --subject Person:P01870 --cutoff 2025-12-11T10:00:00Z
python ai-engine/scripts/run_intelligence.py rank --cutoff 2025-12-11T10:00:00Z --top-n 10
python -m pytest ai-engine/tests/test_phase3.py ai-engine/tests/test_phase2.py ai-engine/tests/test_benchmark.py -q
```

If the runs already exist, use them. To repeat an evaluation, pass `--output ai-engine/runs/evaluation-repeat`; select that bundle explicitly with `--models <run>/model_bundle.json`. Evaluation requires the optional `evaluation` dependencies declared in `pyproject.toml`; inference does not import plotting libraries.

| Location | Purpose |
|---|---|
| `src/prysm_intelligence/` | Current pure intelligence and evaluation code |
| `scripts/run_intelligence.py` | One current CLI: build, evaluate, investigate, rank |
| `config/benchmark_intelligence.json` | Original training baseline |
| `config/evaluation.json` | Controlled GNN experiments and threshold candidates |
| `runs/evaluation-v3/` | Selected model, all 240 results, labels-only evaluation reports and checksums; generated locally |
| `reports/phase3/` | Small reviewable copy of measured results, charts and selected configuration |
| `tests/test_benchmark.py`, `test_phase2.py`, `test_phase3.py` | Dataset, intelligence and evaluation safeguards |
| `src/prysm_ai/v1/` | Historical domain and documents, retained for compatibility |

The selected model uses 60 epochs instead of 180. The evaluation report records strengths, errors, availability and seed variation rather than claiming national-scale accuracy.

Historical API, scripts and artifact directories remain in place because existing service paths depend on them. Their reference documentation is grouped in [v1/docs](src/prysm_ai/v1/docs/RUNTIME.md); historical paths in those documents are relative to `ai-engine/`. The live API still uses v1. Phase 4 integration has not been implemented.
