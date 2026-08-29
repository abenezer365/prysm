"""Build Phase 2 features, signals, models, and evaluation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from prysm_ai.pipeline import run_intelligence  # noqa: E402


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reuse-features", action="store_true", help="reuse an existing verified FeatureSet and retrain/evaluate")
    args = parser.parse_args()
    result = run_intelligence(PROJECT, reuse_features=args.reuse_features)
    test = result["supervised"]["test"]
    print(f"Phase 2 complete: test F1={test['f1']:.3f}, PR-AUC={test['pr_auc']:.3f}; see evaluation/evaluation.json")
