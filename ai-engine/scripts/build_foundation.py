"""CLI for the Prysm data-readiness foundation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from prysm_ai.data_readiness import FoundationBuilder  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, default=PROJECT.parent / "data" / "raw")
    parser.add_argument("--output-dir", type=Path, default=PROJECT / "data" / "processed")
    parser.add_argument("--report-dir", type=Path, default=PROJECT / "reports")
    args = parser.parse_args()
    report = FoundationBuilder(args.raw_dir, args.output_dir, args.report_dir).run()
    rows = sum(item["rows"] for item in report["source"].values())
    print(f"Validated 9 datasets / {rows:,} rows; outputs written to {args.output_dir}")


if __name__ == "__main__":
    main()

