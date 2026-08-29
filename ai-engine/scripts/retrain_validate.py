"""Integrate the scenario dataset, retrain existing intelligence, and validate."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
REPOSITORY = PROJECT.parent
sys.path.insert(0, str(PROJECT / "src"))

from prysm_ai.phase4 import run_phase4  # noqa: E402


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario-root", type=Path, default=REPOSITORY / "generator" / "ground-truth-scenario-generation")
    parser.add_argument("--run-dir", type=Path, default=PROJECT / "runs" / "scenario-v1")
    parser.add_argument("--skip-retraining-check", action="store_true")
    args = parser.parse_args()
    result = run_phase4(PROJECT, args.scenario_root.resolve(), args.run_dir.resolve(), not args.skip_retraining_check)
    test = result["phase2"]["supervised"]["test"]
    print(json.dumps({
        "dataset_integration": result["dataset_integration"]["status"],
        "alignment": result["alignment"]["after"]["status"],
        "predictive_population": result["alignment"]["predictive_eligible_rows"],
        "supervised_test": test,
        "anomaly_test": result["phase2"]["anomaly"]["test"],
        "rules_test": result["phase2"]["rules"]["test"],
        "gnn": result["gnn"],
        "leakage_audit": result["leakage_audit"]["status"],
        "graph_validation": result["graph"]["status"],
        "evidence_validation": result["evidence"]["validation"]["status"],
    }, indent=2))
