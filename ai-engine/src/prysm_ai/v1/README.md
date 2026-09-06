# Archived v1 intelligence domain

These sixteen modules preserve the historical raw-data foundation, future-event alignment, old features/rules/models, graph representation, fusion, evidence and investigation pipeline. They were moved together during the new Phase 2 implementation, without deleting the original algorithms or artifacts.

`../__init__.py` extends the legacy package search path, so imports such as `prysm_ai.features` and `prysm_ai.investigation` continue to resolve here. Existing `api/`, historical scripts and regression tests still use those imports. Relative imports within these modules remain unchanged. New phase work uses the separate `prysm_intelligence` package and `scripts/run_intelligence.py`.

This archive is not a second active implementation for the new benchmark. Its future-target semantics and mostly frozen GraphSAGE representation are historical. Do not train it on the new canonical observation labels or copy new features into both packages. Live API migration is deferred to the later integration phase; the original raw datasets, trained runs and backend contracts remain intact.
