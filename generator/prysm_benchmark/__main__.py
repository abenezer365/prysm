"""Run from the repository root: python -m generator.prysm_benchmark --help."""
import argparse
import json
from pathlib import Path

from .compatibility import export_processed
from .storage import DEFAULT_CONFIG, DEFAULT_OUTPUT, build_snapshot, read_snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate", help="Build or verify an identical immutable benchmark")
    generate.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    generate.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    validate = commands.add_parser("validate", help="Check hashes, schema, integrity and label evidence")
    validate.add_argument("--dataset", type=Path, default=DEFAULT_OUTPUT)
    export = commands.add_parser("export", help="Write existing AI processed interfaces without training")
    export.add_argument("--dataset", type=Path, default=DEFAULT_OUTPUT)
    export.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "generate":
            report = build_snapshot(json.loads(args.config.read_text(encoding="utf-8")), args.output)
        elif args.command == "validate":
            report = read_snapshot(args.dataset)[3]
        else:
            report = export_processed(args.dataset, args.output)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f"Benchmark failed: {error}\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
