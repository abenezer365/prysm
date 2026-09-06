"""Phase 1 contract, corruption, reproducibility and existing-consumer checks."""
from copy import deepcopy
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pyarrow as pa
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ai-engine"))

from generator.prysm_benchmark.contract import NORMAL, PATTERNS, SCHEMAS, VERSION
from generator.prysm_benchmark.compatibility import export_processed
from generator.prysm_benchmark.generate import generate
from generator.prysm_benchmark.storage import DEFAULT_CONFIG, build_snapshot, read_snapshot
from generator.prysm_benchmark.validate import validate
from prysm_ai.features import AsOfFeatureBuilder, MODEL_FEATURES, load_phase1, normalize_transactions
from prysm_ai.graph import CanonicalGraphBuilder, GraphStore


@pytest.fixture(scope="module")
def config():
    return json.loads(DEFAULT_CONFIG.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def tables(config):
    return generate(config)


@pytest.fixture(scope="module")
def snapshot(tmp_path_factory, config):
    path = tmp_path_factory.mktemp("benchmark") / "source"
    build_snapshot(config, path)
    return path


def test_size_and_reproducibility(tables, config):
    report = validate(tables, config)
    assert report["cases"] == 240 and report["suspicious_cases"] == 24
    assert report["rows"]["transactions"] == 4320
    assert all(tables[name].equals(frame) for name, frame in generate(config).items())
    different = generate({**config, "seed": 7})
    assert not different["transactions"].equals(tables["transactions"])
    assert validate(different, {**config, "seed": 7})["status"] == "passed"
    for name, table in tables.items():
        if name != "ground_truth":
            assert not {"scenario", "is_suspicious", "ground_truth_id", "split", "rationale"} & set(table.column_names)


@pytest.mark.parametrize("table,mutation,error", [
    ("persons", lambda r: r.append(r[0].copy()), "duplicate identifier"),
    ("persons", lambda r: r[0].update(first_name=None), "missing required"),
    ("persons", lambda r: r[0].update(declared_monthly_income=float("nan")), "non-finite"),
    ("persons", lambda r: r[0].update(latitude=200.), "geographic"),
    ("persons", lambda r: r[0].update(country="Kenya"), "contradictory city"),
    ("accounts", lambda r: r[0].update(owner_id="missing"), "typed owner"),
    ("accounts", lambda r: r[0].update(institution_id="missing"), "institution reference"),
    ("accounts", lambda r: r[0].update(closed_at=r[0]["opened_at"]), "contradictory status"),
    ("accounts", lambda r: r.pop(), "orphan without an account"),
    ("transactions", lambda r: r[0].update(receiver_account_id="missing"), "account reference"),
    ("transactions", lambda r: r[0].update(amount=-2.), "invalid amount"),
    ("transactions", lambda r: r[0].update(amount_etb=1.), "ETB conversion"),
    ("transactions", lambda r: r[0].update(timestamp=r[0]["timestamp"]-pd.Timedelta(days=800)), "account lifecycle"),
    ("relationships", lambda r: r[0].update(target_id=r[0]["source_id"]), "self reference"),
    ("relationships", lambda r: r[0].update(relationship_type="employer_employee"), "endpoint types"),
    ("relationships", lambda r: r.append({**r[0], "relationship_id": "Rextra"}), "duplicate/contradictory"),
    ("ground_truth", lambda r: r[0].update(is_suspicious=not r[0]["is_suspicious"]), "label/scenario"),
    ("ground_truth", lambda r: r[0].update(evidence_transaction_ids=["missing"]), "transaction evidence"),
    ("ground_truth", lambda r: r[0].update(evidence_transaction_ids=r[1]["evidence_transaction_ids"]), "unaffiliated"),
    ("ground_truth", lambda r: r[0].update(as_of=r[0]["history_start"]), "observation timestamps"),
    ("ground_truth", lambda r: r[0].update(split="test"), "split start"),
    ("ground_truth", lambda r: r[1].update(member_entity_keys=r[0]["member_entity_keys"], entity_key=r[0]["entity_key"]), "leakage"),
    ("ground_truth", lambda r: r[0].update(context_transaction_ids=[]), "missing context"),
])
def test_rejects_corruption(tables, config, table, mutation, error):
    broken = dict(tables)
    rows = tables[table].to_pylist()
    mutation(rows)
    broken[table] = pa.Table.from_pylist(rows, schema=SCHEMAS[table])
    with pytest.raises(ValueError, match=error):
        validate(broken, config)


@pytest.mark.parametrize("pattern", PATTERNS)
def test_rejects_positive_labels_without_behavior(tables, config, pattern):
    ground = next(r for r in tables["ground_truth"].to_pylist() if r["scenario"] == pattern)
    ids = set(ground["evidence_transaction_ids"])
    rows = tables["transactions"].to_pylist()
    reference = next(r for r in rows if r["transaction_id"] in ground["context_transaction_ids"] and r["transaction_type"] == "Purchase")
    j = 0
    for row in rows:
        if row["transaction_id"] in ids:
            row.update({**reference, "transaction_id": row["transaction_id"], "timestamp": ground["window_start"]+pd.Timedelta(days=j)})
            j += 1
    with pytest.raises(ValueError, match=f"{pattern} evidence"):
        validate({**tables, "transactions": pa.Table.from_pylist(rows, schema=SCHEMAS["transactions"])}, config)


def test_manifest_and_immutable_generation(snapshot, config, tmp_path):
    assert read_snapshot(snapshot)[3]["status"] == "passed"
    assert build_snapshot(config, snapshot)["status"] == "passed"
    with pytest.raises(ValueError, match="already exists"):
        build_snapshot({**config, "seed": 44}, snapshot)
    other = tmp_path / "second"
    build_snapshot(config, other)
    assert (other / "MANIFEST.json").read_bytes() == (snapshot / "MANIFEST.json").read_bytes()
    path = other / "transactions.parquet"
    path.write_bytes(path.read_bytes()+b"tamper")
    with pytest.raises(ValueError, match="checksum mismatch"):
        read_snapshot(other)


@pytest.mark.parametrize("scenario", NORMAL.values())
def test_rejects_normal_labels_without_benign_context(tables, config, scenario):
    ground = next(r for r in tables["ground_truth"].to_pylist() if r["scenario"] == scenario)
    ids = set(ground["evidence_transaction_ids"])
    rows = tables["transactions"].to_pylist()
    for row in rows:
        if row["transaction_id"] in ids:
            row.update(transaction_type="Transfer", timestamp=ground["window_start"])
    with pytest.raises(ValueError, match=f"{scenario} evidence"):
        validate({**tables, "transactions": pa.Table.from_pylist(rows, schema=SCHEMAS["transactions"])}, config)


def test_schema_and_config_failures(tables, config):
    with pytest.raises(ValueError, match="schema mismatch"):
        validate({**tables, "persons": tables["persons"].drop(["occupation"])}, config)
    with pytest.raises(ValueError, match="9..20"):
        generate({**config, "cases_per_pattern_per_split": 100000})
    invalid = deepcopy(config)
    invalid["splits"]["test"] = invalid["splits"]["train"]
    with pytest.raises(ValueError, match="chronological"):
        generate(invalid)


def test_existing_features_graph_and_search(snapshot, tmp_path):
    from api.runtime import EngineRuntime

    processed = tmp_path / "data" / "processed"
    export_processed(snapshot, processed)
    with pytest.raises(ValueError, match="already exists"):
        export_processed(snapshot, processed)
    accounts, tx, invoices, rel = load_phase1(processed)
    normalized = normalize_transactions(tx, accounts, invoices)
    assert normalized.sender_lifecycle_valid.all() and normalized.receiver_lifecycle_valid.all()
    assert normalized.invoice_chronology_valid.all()
    assert {"latitude", "longitude", "city", "region", "country"} <= set(normalized)
    labels = pd.read_parquet(processed / "ground_truth_labels.parquet")
    builder = AsOfFeatureBuilder(normalized, accounts, rel)
    features = builder.build_labels(labels)
    assert len(features) == 240 and np.isfinite(features[MODEL_FEATURES].to_numpy()).all()
    row = labels.iloc[0]
    before = builder.build_one(row.entity_key, row.window_start-pd.Timedelta(seconds=1))
    at_cutoff = builder.build_one(row.entity_key, row.as_of)
    assert at_cutoff["history_tx_count"] > before["history_tx_count"]
    future = tx.iloc[[0]].copy()
    future["transaction_id"] = "future"
    future["sender_account_id"] = accounts.loc[accounts.owner_key.eq(row.entity_key), "account_id"].iloc[0]
    future["timestamp"] = row.as_of+pd.Timedelta(days=1000)
    augmented = normalize_transactions(pd.concat([tx, future], ignore_index=True), accounts, invoices)
    assert AsOfFeatureBuilder(augmented, accounts, rel).build_one(row.entity_key, row.as_of) == at_cutoff
    graph_dir = tmp_path / "graph"
    manifest = CanonicalGraphBuilder(processed, graph_dir).build()
    assert manifest["invalid_endpoints"] == 0 and manifest["source_labels_used"] is False
    store = GraphStore(graph_dir)
    nodes, edges = store.subgraph(row.entity_key, row.as_of, 2, 100, 365, "predictive", None, .3)
    assert len(nodes) and len(edges)
    event = edges[edges.temporal_kind.eq("event")]
    assert event.event_time.le(row.as_of).all()
    runtime = EngineRuntime()
    runtime.root = tmp_path
    result = runtime.search_people(row.entity_id, 5)
    assert result.datasetVersion == VERSION and result.data[0].externalRef == row.entity_key
    runtime._engine = SimpleNamespace(graph_store=store)
    graph = runtime.graph(row.entity_key, row.as_of, 2, 100)
    businesses = [n for n in graph["nodes"] if n["type"] == "Company"]
    assert businesses and all(n["label"].startswith("Synthetic ") for n in businesses)
