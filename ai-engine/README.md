# Prysm AI Engine — Data Foundation

This directory contains the reproducible data-readiness layer for Prysm's future
fraud, AML, anomaly, behavioral, foreign-income, and graph systems. It does not
contain models, scoring, APIs, or production rules.

The pipeline reads the immutable Parquet source in `../data/raw` by default,
validates contracts and cross-table behavior, and writes generated artifacts to
`data/processed` and `reports`. Override either path with command-line flags.

```powershell
cd ai-engine
python scripts/build_foundation.py
python scripts/build_intelligence.py
python scripts/align_labels.py
python scripts/build_graph_intelligence.py
python -m pytest
```

Generated outputs are described in `DATA_CONTRACTS.md`; audit findings and
modeling constraints are in `DATA_READINESS_REPORT.md`. The machine-readable
audit is `reports/data_quality_report.json`.

Phase 2 configuration is centralized in `config/intelligence.json`. Its outputs
are written to `data/intelligence`, `signals`, `artifacts`, and `evaluation`.
Use `python scripts/build_intelligence.py --reuse-features` only when retraining
or tuning against an already verified FeatureSet.

Always inspect `artifacts/VALIDITY.json` before consuming supervised artifacts.
The current source ground truth fails the predictive event-provenance gate.

Phase 3 graph artifacts live under `graph/`; the investigator-facing example is
`investigations/demo_investigation.json`. Use `--reuse-graph` to rebuild derived
graph intelligence after configuration changes without rewriting edge files.
