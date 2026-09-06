"""Prysm engine: build, evaluate, investigate or rank from any working directory."""
import argparse
import json
from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))
sys.path.insert(0, str(PROJECT.parent))

from prysm_intelligence.pipeline import DEFAULT_CONFIG, DEFAULT_DATASET, DEFAULT_OUTPUT, build, json_write, load_engine


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    training = commands.add_parser("build", help="Train on train only and emit all benchmark results")
    training.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    training.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    training.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    evaluation = commands.add_parser("evaluate", help="Select on validation; evaluate frozen models with charts and evidence")
    evaluation.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    evaluation.add_argument("--baseline", type=Path, default=DEFAULT_OUTPUT)
    evaluation.add_argument("--output", type=Path, default=PROJECT / "runs" / "evaluation-v3")
    evaluation.add_argument("--experiments", type=Path, default=PROJECT / "config" / "evaluation.json")
    evaluation.add_argument("--top-n", type=int, default=10)
    for command in ("investigate", "rank"):
        p = commands.add_parser(command)
        p.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
        p.add_argument("--models", type=Path, default=PROJECT / "runs" / "evaluation-v3" / "model_bundle.json")
        p.add_argument("--cutoff", required=True, help="Timezone-aware ISO timestamp")
        p.add_argument("--output", type=Path)
        if command == "investigate":
            p.add_argument("--subject", required=True, help="Typed key such as Person:P00640")
        else:
            p.add_argument("--top-n", type=int, default=10)
    args = parser.parse_args()
    try:
        if args.command == "evaluate":
            from prysm_intelligence.evaluation import evaluate
            evaluate(args.dataset, args.baseline, args.output, args.experiments, args.top_n, progress=lambda message: print(message, flush=True))
            return
        if args.command == "build":
            build(args.dataset, args.output, args.config, progress=lambda message: print(message, flush=True))
            return
        if args.output and args.output.exists():
            raise ValueError("Result output already exists; choose a fresh path")
        engine = load_engine(args.dataset, args.models)
        if args.command == "investigate":
            result = engine.investigate(args.subject, args.cutoff)
        else:
            import pandas as pd
            subjects = [key for key, (created, _) in engine.dataset.entities.items() if key.startswith("Person:") and created <= pd.Timestamp(args.cutoff)]
            result = {"population": "all observed people at cutoff", "ranking": engine.rank(subjects, args.cutoff, args.top_n)}
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            json_write(args.output, result)
            print(f"Wrote {args.output}")
        else:
            print(json.dumps(result, indent=2, allow_nan=False))
    except (ValueError, KeyError, OSError, TypeError) as error:
        parser.exit(1, f"Intelligence failed: {error}\n")


if __name__ == "__main__":
    main()
