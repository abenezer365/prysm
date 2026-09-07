# Prysm AI Engine

The active server is `api.intelligence:app` (started by `python start.py`). The repository launcher selects `data/prysm-demo-v2` and `runs/demo-v2-build/model_bundle.json`, requires `AI_ENGINE_API_KEY`, and exposes protected `/v2/investigate`, `/v2/rank`, `/v2/people/search`, and `/ready` endpoints.

The teachable flow is: **validated facts → cutoff-safe features and graph → rules, anomaly, network, GNN → evidence and ranked review priorities**. Labels are used only for training and evaluation. Scores are not fraud probabilities.

From the repository root:

```powershell
# Rebuild the active dataset/model into a fresh output directory.
python -m generator.prysm_benchmark generate --config generator/prysm_benchmark/demo_config.json --output data/prysm-demo-v2-repeat
python ai-engine/scripts/run_intelligence.py build --dataset data/prysm-demo-v2-repeat --output ai-engine/runs/demo-v2-repeat

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
| `runs/demo-v2-build/` | Retrained bundle and all 10,800 chronological train/validation/test results |
| `Prysm_AI_Metrics.ipynb` | Executed metrics, confusion matrix, loss, threshold sensitivity, and availability notebook |
| `reports/phase3/` | Small reviewable copy of measured results, charts and selected configuration |
| `tests/test_benchmark.py`, `test_phase2.py`, `test_phase3.py` | Dataset, intelligence and evaluation safeguards |
| `src/prysm_ai/v1/` | Historical domain and documents, retained for compatibility |

The active model uses 180 epochs. Its perfect synthetic held-out metrics describe this designed demo benchmark only; they are not evidence of national-scale performance, calibrated fraud probability, or guilt.

Large generated V1 data and run directories were removed. Historical source remains only where it still supports compatibility tests; the live API uses `prysm_intelligence`.
