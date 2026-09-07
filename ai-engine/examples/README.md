# Phase 2 generated examples

`phase2_top_entities.json` contains the computed Top 10 among the **80 test-partition primary subjects**, each investigated at `2025-12-11T10:00:00Z`. It is derived from `runs/intelligence-v2/top_entities.json`.

`phase2_investigation.json` is the full result for the first-ranked subject in that ranking, selected from `runs/intelligence-v2/test_results.jsonl`. It contains the component scores, three source-backed evidence items and six highlighted transfer edges. No label list was used to select the subject. Red means linked to an investigation lead, not confirmed fraud.

Regenerate the full run with:

```powershell
python ai-engine/scripts/run_intelligence.py build --output ai-engine/runs/intelligence-v2-rebuild
```

Read the test ranking's first `entity_key`, then select that subject from `test_results.jsonl` to refresh these examples. A single subject can also be reproduced through `run_intelligence.py investigate --subject <key> --cutoff 2025-12-11T10:00:00Z --models <run>/model_bundle.json --output <fresh-path>`.

CLI `rank` uses **all observed people** at a cutoff, which is a different population from the 80 benchmark primary subjects shown here. These are demonstration artifacts; formal performance claims belong to Phase 3.
