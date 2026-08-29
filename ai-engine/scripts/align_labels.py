"""Audit label/event timing and materialize predictive eligibility."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from prysm_ai.label_alignment import run_alignment  # noqa: E402


if __name__ == "__main__":
    report = run_alignment(PROJECT)
    print(f"Audited {report['source_rows']:,} labels; predictive eligible: {report['predictive_eligible_rows']:,}; after evaluation: {report['after']['status']}")

