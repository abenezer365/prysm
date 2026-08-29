# Prysm AI Engine

This directory contains Prysm's reproducible data-readiness and intelligence engine: preprocessing, leakage-safe features, configurable rules, anomaly/supervised benchmark artifacts, temporal graph/GNN intelligence, evidence, fusion, evaluation, and a FastAPI boundary over the existing `InvestigationEngine`. Its assessment is decision support, not a calibrated fraud probability.

The pipeline reads immutable Parquet sources from `../data/raw` by default, validates contracts and cross-table behavior, and writes derived artifacts beneath `ai-engine/`. Original inputs are never overwritten.

```powershell
cd ai-engine
python scripts/build_foundation.py
python scripts/build_intelligence.py
python scripts/align_labels.py
python scripts/build_graph_intelligence.py
python -m pytest
```

Generated outputs and constraints are documented in `DATA_CONTRACTS.md`, `DATA_READINESS_REPORT.md`, `FEATURE_POLICY.md`, `INTELLIGENCE_CONTRACTS.md`, and `GRAPH_RISK_EVIDENCE.md`. Phase 2 configuration is centralized in `config/intelligence.json`; outputs are written to `data/intelligence`, `signals`, `artifacts`, and `evaluation`. Always inspect `artifacts/VALIDITY.json` before consuming supervised artifacts because the original retrospective ground truth fails the predictive event-provenance gate.

Phase 3 graph artifacts live under `graph/`; `investigations/demo_investigation.json` is the investigator-facing example. Full-graph embeddings are retrospective reference artifacts. Historical/predictive investigation must use cutoff-filtered bounded graph computation.

The valid aligned synthetic benchmark is isolated under `runs/scenario-v1/`; it does not make the original labels predictive or establish real-world model efficacy.

The internal service exposes `GET /health`, `GET /ready`, and `POST /v1/analyze`:

```powershell
python -m uvicorn api.app:app --host 127.0.0.1 --port 8100
```

The frontend never calls this service directly. Express constructs the trusted cutoff-aware context, validates the response, and persists the resulting run, findings, evidence, versions, and audit metadata.
