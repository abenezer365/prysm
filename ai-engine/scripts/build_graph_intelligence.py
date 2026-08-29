"""Build Phase 3 graph, GNN representation, fusion, and evidence artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from prysm_ai.phase3_pipeline import run_phase3  # noqa: E402


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reuse-graph", action="store_true", help="reuse canonical nodes/edge partitions and rebuild derived graph intelligence")
    parser.add_argument("--reuse-derived", action="store_true", help="reuse graph features/GNN artifact and regenerate fusion/evidence only")
    args = parser.parse_args()
    result = run_phase3(PROJECT, reuse_graph=args.reuse_graph or args.reuse_derived, reuse_derived=args.reuse_derived)
    demo = result["demonstration"]
    print(f"Phase 3 graph complete: {result['graph_validation']['node_count']:,} nodes, {result['graph_validation']['edge_count']:,} edges; demo {demo['investigation_id']}")
