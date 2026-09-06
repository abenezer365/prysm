"""One-way export into existing AI processed contracts; canonical facts stay intact."""
from pathlib import Path
import tempfile

import pandas as pd

from .contract import VERSION
from .storage import digest, read_snapshot, write_json
from .validate import require


def export_processed(source, output):
    source, output = Path(source).resolve(), Path(output).resolve()
    tables, _, _, _ = read_snapshot(source)
    require(not output.exists(), "Processed output already exists; choose a new --output directory")
    frames = {name: table.to_pandas() for name, table in tables.items()}
    persons = frames["persons"].copy()
    # Nationality is unknown; do not infer it from residence (including diaspora).
    persons["nationality"] = pd.Series(pd.NA, index=persons.index, dtype="string")
    accounts = frames["accounts"].copy()
    accounts["owner_key"] = accounts.owner_type + ":" + accounts.owner_id
    rel = frames["relationships"].copy()
    for side in ("source", "target"):
        rel[f"{side}_key"] = rel[f"{side}_type"] + ":" + rel[f"{side}_id"]
    tx = frames["transactions"].copy()
    tx["sender_key"] = "Account:" + tx.sender_account_id
    tx["receiver_key"] = "Account:" + tx.receiver_account_id
    tx["invoice_id"] = pd.Series(pd.NA, index=tx.index, dtype="string")
    # Optional invoice evidence is unavailable, not invented to satisfy a loader.
    invoices = pd.DataFrame({c: pd.Series(dtype="string") for c in (
        "invoice_id", "issuer_id", "issuer_type", "issuer_key", "recipient_id", "recipient_type",
        "recipient_key", "currency", "service_type", "status")})
    for c in ("issue_date", "due_date"):
        invoices[c] = pd.Series(dtype="datetime64[ns, UTC]")
    invoices["amount"] = pd.Series(dtype="float64")
    truth = frames["ground_truth"]
    labels = truth[["ground_truth_id", "entity_key", "split", "window_start", "window_end", "as_of"]].copy()
    labels["entity_type"] = labels.entity_key.str.split(":").str[0]
    labels["entity_id"] = labels.entity_key.str.split(":").str[1]
    labels["behavior_type"] = truth.scenario
    labels["is_anomalous"] = truth.is_suspicious
    labels["risk_pattern"] = truth.is_suspicious.map({True: "SYNTHETIC_INDICATOR", False: "NORMAL"})
    labels["severity"] = truth.is_suspicious.map({True: "high", False: "info"})
    # build_labels() takes its feature cutoff from pattern_start. This export is
    # explicitly retrospective detection; real event boundaries remain window_*.
    labels["pattern_start"] = truth.as_of
    labels["pattern_end"] = truth.as_of
    labels["related_entity_ids"] = truth.evidence_transaction_ids
    labels["evaluation_scope"] = "synthetic_retrospective_detection"
    result = {"persons": persons, "companies": frames["companies"], "banks": frames["institutions"],
              "accounts": accounts, "transaction_edges": tx, "relationship_edges": rel,
              "invoices": invoices, "ground_truth_labels": labels}
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".processed-", dir=output.parent) as temporary:
        stage = Path(temporary) / "processed"
        stage.mkdir()
        for name, frame in result.items():
            frame.to_parquet(stage / f"{name}.parquet", index=False, compression="zstd")
        write_json(stage / "MANIFEST.json", {
            "dataset_version": VERSION, "source_manifest_sha256": digest(source / "MANIFEST.json"),
            "source_contract": "data/benchmarks/prysm-benchmark-v1/DATASET_MANIFEST.md",
            "evaluation_scope": "synthetic_retrospective_detection",
            "legacy_label_cutoff": "pattern_start=as_of; actual event boundaries are window_start/window_end",
            "files": {p.name: {"sha256": digest(p), "rows": len(result[p.stem])} for p in sorted(stage.glob("*.parquet"))},
        })
        stage.rename(output)
    return {"status": "exported", "dataset_version": VERSION, "output": str(output)}
