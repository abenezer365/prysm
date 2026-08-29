from pathlib import Path

import pandas as pd

from prysm_ai.data_readiness import FoundationBuilder


def test_person_canonicalization_is_deterministic_and_prefers_complete_latest():
    rows = pd.DataFrame({
        "person_id": ["P1", "P1", "P2"],
        "created_at": pd.to_datetime(["2024-01-01", "2024-02-01", "2024-01-01"], utc=True),
        "phone_hash": [None, "hash", "other"],
    })
    canonical, lineage = FoundationBuilder.canonicalize_persons(rows)
    assert canonical["person_id"].tolist() == ["P1", "P2"]
    assert canonical.loc[canonical.person_id.eq("P1"), "phone_hash"].item() == "hash"
    assert lineage["selected_as_canonical"].sum() == 1


def test_required_raw_files_exist():
    raw = Path(__file__).resolve().parents[2] / "data" / "raw"
    expected = {"accounts", "banks", "companies", "devices", "ground_truth", "invoices", "persons", "relationships", "transactions"}
    assert expected == {path.stem for path in raw.glob("*.parquet")}

