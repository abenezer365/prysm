"""Phase 2 behavior, leakage boundaries, genuine GNN training and evidence contracts."""
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from prysm_intelligence.anomaly import RobustAnomaly
from prysm_intelligence.data import Dataset
from prysm_intelligence.engine import IntelligenceEngine, rank_results
from prysm_intelligence.features import build_features, vector
from prysm_intelligence.fusion import fuse
from prysm_intelligence.gnn import RelationalSAGE
from prysm_intelligence.graph import GraphSample, NODE_FEATURES, RELATIONS, graph_sample
from prysm_intelligence.pipeline import DEFAULT_DATASET, load_config, load_engine, train, validate_config

EXPECTED = {"structuring": "STRUCTURED_DEPOSITS", "velocity": "HIGH_VELOCITY", "amount": "UNEXPLAINED_AMOUNT",
            "geography": "IMPOSSIBLE_BRANCH_TRAVEL", "network": "RAPID_CIRCULAR_FLOW", "family": "FAMILY_PASS_THROUGH",
            "tax": "BUSINESS_RECEIPTS_MISMATCH", "theft": "NEW_DEVICE_RAPID_OUTFLOW"}


@pytest.fixture(scope="module")
def dataset():
    return Dataset.load(DEFAULT_DATASET)


@pytest.fixture(scope="module")
def config():
    return load_config()


@pytest.fixture(scope="module")
def observations():
    return pd.read_parquet(DEFAULT_DATASET / "ground_truth.parquet")


@pytest.fixture(scope="module")
def results(dataset, config, observations):
    engine = IntelligenceEngine(dataset, config)
    return {r.ground_truth_id: engine.investigate(r.entity_key, r.as_of) for r in observations.itertuples(index=False)}


@pytest.mark.parametrize("pattern", EXPECTED)
def test_known_scenarios_have_exact_source_backed_leads(pattern, results, observations):
    for row in observations[observations.scenario.eq(pattern)].itertuples(index=False):
        result = results[row.ground_truth_id]
        findings = [e for e in result["evidence"] if e["signal_type"] == EXPECTED[pattern]]
        assert findings, pattern
        for finding in findings:
            assert set(finding["supporting_transaction_ids"]) <= set(row.evidence_transaction_ids)
            assert set(finding["supporting_relationship_ids"]) <= set(row.evidence_relationship_ids)
        assert not result["provenance"]["ground_truth_used_at_inference"]


def test_all_benign_controls_have_no_deterministic_leads(results, observations):
    for row in observations[~observations.is_suspicious].itertuples(index=False):
        result = results[row.ground_truth_id]
        assert not result["evidence"], (row.ground_truth_id, result["findings"])
        assert not any(e["highlight_color"] for e in result["graph"]["edges"])


def test_graph_annotations_and_evidence_resolve(results):
    for result in results.values():
        json.dumps(result, allow_nan=False)
        graph = result["graph"]
        nodes = {n["id"] for n in graph["nodes"]}
        edges = {e["id"] for e in graph["edges"]}
        evidence_ids = {e["evidence_id"] for e in result["evidence"]}
        for e in graph["edges"]:
            assert e["source"] in nodes and e["target"] in nodes
            assert pd.Timestamp(e["timestamp"]) <= pd.Timestamp(graph["cutoff"])
        for e in result["evidence"]:
            assert set(e["supporting_entity_ids"]) <= nodes and set(e["supporting_edge_ids"]) <= edges
        for element in [*graph["nodes"], *graph["edges"]]:
            assert set(element["evidence_ids"]) <= evidence_ids
            assert (element["highlight_color"] == "red") == bool(element["evidence_ids"])


def test_cutoff_and_future_events_do_not_change_results(dataset, config, observations):
    row = observations[observations.scenario.eq("structuring")].iloc[0]
    engine = IntelligenceEngine(dataset, config)
    before = engine.investigate(row.entity_key, row.window_start-pd.Timedelta(seconds=1))
    assert not before["evidence"]
    tables = {name: frame.copy() for name, frame in dataset.tables.items()}
    future = tables["transactions"].iloc[[0]].copy()
    future["transaction_id"] = "Tfuture"
    future["sender_account_id"] = dataset.snapshot(row.entity_key, row.as_of, config).accounts.iloc[0].account_id
    future["timestamp"] = row.as_of+pd.Timedelta(days=2000)
    tables["transactions"] = pd.concat([tables["transactions"], future], ignore_index=True)
    altered = IntelligenceEngine(Dataset(tables, dataset.version, dataset.checksum), config)
    assert altered.investigate(row.entity_key, row.as_of) == engine.investigate(row.entity_key, row.as_of)


def test_tax_requires_available_declaration_and_ownership(dataset, config, observations):
    row = observations[observations.scenario.eq("tax")].iloc[0]
    for mutation in ("declaration", "ownership", "geography", "matched_sales"):
        tables = {name: frame.copy() for name, frame in dataset.tables.items()}
        snapshot = dataset.snapshot(row.entity_key, row.as_of, config)
        cid = snapshot.companies.iloc[0].company_id
        mask = tables["companies"].company_id.eq(cid)
        if mutation == "declaration":
            tables["companies"].loc[mask, "sales_reported_at"] = row.as_of+pd.Timedelta(days=1)
        elif mutation == "ownership":
            r = tables["relationships"]
            tables["relationships"] = r[~(r.relationship_type.eq("beneficial_owner") & r.source_id.eq(row.entity_key.split(":")[1]))]
        elif mutation == "matched_sales":
            tables["companies"].loc[mask, "declared_sales_etb"] *= 20
        else:
            tables["companies"].loc[mask, "latitude"] = 0.
        result = IntelligenceEngine(Dataset(tables), config).investigate(row.entity_key, row.as_of)
        assert "BUSINESS_RECEIPTS_MISMATCH" not in {e["signal_type"] for e in result["evidence"]}


def test_expired_family_relation_does_not_produce_family_lead(dataset, config, observations):
    row = observations[observations.scenario.eq("family")].iloc[0]
    tables = {name: frame.copy() for name, frame in dataset.tables.items()}
    mask = tables["relationships"].relationship_id.isin(row.evidence_relationship_ids) & tables["relationships"].relationship_type.eq("family")
    tables["relationships"].loc[mask, "end_time"] = row.window_start-pd.Timedelta(days=1)
    result = IntelligenceEngine(Dataset(tables), config).investigate(row.entity_key, row.as_of)
    assert "FAMILY_PASS_THROUGH" not in {e["signal_type"] for e in result["evidence"]}


def test_missing_history_unknown_subject_and_naive_cutoff(dataset, config, observations):
    row = observations.iloc[0]
    engine = IntelligenceEngine(dataset, config)
    result = engine.investigate(row.entity_key, row.history_start)
    assert result["assessment"]["strength"] is None
    with pytest.raises(ValueError, match="unknown"):
        engine.investigate("Person:missing", row.as_of)
    with pytest.raises(ValueError, match="timezone-aware"):
        engine.investigate(row.entity_key, "2025-01-01")
    with pytest.raises(ValueError, match="positive integer"):
        engine.rank([row.entity_key], row.as_of, 0)


def test_anomaly_explanations_sum_to_score_and_reload(dataset, config, observations):
    train_rows = observations[observations.split.eq("train") & ~observations.is_suspicious]
    features = [build_features(dataset.snapshot(r.entity_key, r.as_of, config)) for r in train_rows.itertuples(index=False)]
    model = RobustAnomaly(config["anomaly"]).fit(features)
    row = observations[observations.scenario.eq("theft")].iloc[0]
    f = build_features(dataset.snapshot(row.entity_key, row.as_of, config))
    prediction = model.predict(f)
    assert prediction["score"] == pytest.approx(sum(c["score_contribution"] for c in prediction["contributions"]))
    assert prediction["flagged"]
    assert RobustAnomaly.from_dict(model.to_dict()).predict(f) == prediction
    cold = build_features(dataset.snapshot(row.entity_key, row.history_start, config))
    assert model.predict(cold)["status"] == "unavailable"
    assert np.isfinite(vector(f)).all()


def tiny_graph(seed=1):
    rng = np.random.default_rng(seed)
    x = rng.normal(0, .2, (4, len(NODE_FEATURES)))
    a = np.zeros((len(RELATIONS), 4, 4))
    a[0, 0, 1] = a[0, 1, 0] = a[1, 1, 2] = a[1, 2, 1] = 1
    a[3, 2, 3] = a[4, 3, 2] = 1
    return GraphSample(x, a, 0, [f"Person:{i}" for i in range(4)], {})


def test_gnn_full_gradient_matches_finite_differences(config):
    model = RelationalSAGE({**config["gnn"], "hidden_dim": 3}, 4)
    sample = tiny_graph()
    _, gradients = model.loss_gradient(sample, 1.)
    epsilon = 1e-5
    for name, parameter in model.parameters.items():
        for flat_index in (0, parameter.size//2, parameter.size-1):
            index = np.unravel_index(flat_index, parameter.shape)
            original = parameter[index]
            parameter[index] = original+epsilon
            plus = model.loss_gradient(sample, 1.)[0]
            parameter[index] = original-epsilon
            minus = model.loss_gradient(sample, 1.)[0]
            parameter[index] = original
            assert gradients[name][index] == pytest.approx((plus-minus)/(2*epsilon), abs=1e-7)


def test_gnn_learns_message_weights_and_uses_edges(config):
    settings = {**config["gnn"], "epochs": 35, "hidden_dim": 4}
    samples = [tiny_graph(i) for i in range(8)]
    labels = [0, 1]*4
    model = RelationalSAGE(settings, 11)
    initial = {k: v.copy() for k, v in model.parameters.items()}
    model.fit(samples, labels)
    assert model.losses[-1] < model.losses[0]
    assert not np.array_equal(initial["w1"], model.parameters["w1"])
    assert not np.array_equal(initial["w2"], model.parameters["w2"])
    assert model.predict(samples[0]) != pytest.approx(model.predict(replace(samples[0], adjacency=np.zeros_like(samples[0].adjacency))))
    restored = RelationalSAGE.from_dict(model.to_dict())
    assert restored.predict(samples[0]) == model.predict(samples[0])
    repeat = RelationalSAGE(settings, 11).fit(samples, labels)
    assert repeat.to_dict() == model.to_dict()
    assert model.predict(replace(samples[0], node_keys=["renamed"]*4)) == model.predict(samples[0])
    with pytest.raises(ValueError, match="both binary"):
        RelationalSAGE(settings, 11).fit(samples, [0]*8)


def test_graph_tensors_do_not_use_institution_nodes_or_labels(dataset, config, observations):
    train_row = observations[observations.split.eq("train")].iloc[0]
    test_row = observations[observations.split.eq("test")].iloc[0]
    a = graph_sample(dataset.snapshot(train_row.entity_key, train_row.as_of, config))
    b = graph_sample(dataset.snapshot(test_row.entity_key, test_row.as_of, config))
    assert not set(a.node_keys) & set(b.node_keys)
    assert not any(k.startswith(("Institution:", "Device:")) for k in a.node_keys)
    assert a.x.shape[1] == len(NODE_FEATURES) and np.isfinite(a.x).all()
    assert "ground_truth" not in dataset.tables


def test_fusion_keeps_sources_and_unavailable_coverage(config):
    components = {name: {"status": "unavailable", "strength": None, "confidence": 0.} for name in config["fusion"]["weights"]}
    assert fuse(components, config["fusion"])["strength"] is None
    components["rules"] = {"status": "available", "strength": .9, "confidence": .9}
    result = fuse(components, config["fusion"])
    assert result["strength"] == .9 and result["coverage"] == pytest.approx(.45)
    assert sum(v["weighted_contribution"] for v in result["breakdown"].values()) == result["strength"]
    assert not result["is_fraud_probability"]


def test_ranking_is_computed_deterministically(results):
    values = list(results.values())
    ranked = rank_results(values, 7)
    assert len(ranked) == 7 and ranked == rank_results(values[::-1], 7)
    assert [r["overall_risk"] for r in ranked] == sorted([r["overall_risk"] for r in ranked], reverse=True)
    assert all(r["evidence_ids"] and not r["is_fraud_probability"] for r in ranked)


def test_held_out_rows_never_affect_fit_and_bundle_reload(dataset, config, observations, tmp_path):
    settings = deepcopy(config)
    settings["gnn"]["epochs"] = 3
    training = observations[observations.split.eq("train")]
    small = pd.concat([training[~training.is_suspicious].head(4), training[training.is_suspicious].head(4),
                       observations[~observations.split.eq("train")]])
    a, g, provenance = train(dataset, small, settings)
    poison = small.copy()
    held_out = ~poison.split.eq("train")
    poison.loc[held_out, "is_suspicious"] = ~poison.loc[held_out, "is_suspicious"]
    poison.loc[held_out, "entity_key"] = "Person:do-not-read"
    a2, g2, provenance2 = train(dataset, poison, settings)
    assert a.to_dict() == a2.to_dict() and g.to_dict() == g2.to_dict() and provenance == provenance2
    bundle = {"version": settings["version"], "source_manifest_sha256": dataset.checksum,
              "config": settings, "training": provenance, "anomaly": a.to_dict(), "gnn": g.to_dict()}
    path = tmp_path / "model_bundle.json"
    path.write_text(json.dumps(bundle), encoding="utf-8")
    restored = load_engine(DEFAULT_DATASET, path)
    row = small.iloc[0]
    original = IntelligenceEngine(dataset, settings, a, g, provenance)
    assert restored.investigate(row.entity_key, row.as_of) == original.investigate(row.entity_key, row.as_of)
    earlier = original.investigate(row.entity_key, row.as_of-pd.Timedelta(days=1))
    assert earlier["intelligence_components"]["gnn"]["status"] == "unavailable"
    assert earlier["intelligence_components"]["anomaly"]["status"] == "unavailable"
    bundle["source_manifest_sha256"] = "wrong-dataset"
    path.write_text(json.dumps(bundle), encoding="utf-8")
    with pytest.raises(ValueError, match="different engine or dataset"):
        load_engine(DEFAULT_DATASET, path)


def test_truncation_is_explicit_not_a_clean_bill_of_health(dataset, config, observations):
    limited = {**config, "max_nodes": 1}
    row = observations.iloc[0]
    result = IntelligenceEngine(dataset, limited).investigate(row.entity_key, row.as_of)
    assert result["graph"]["truncated"]
    assert result["assessment"]["strength"] is None and not result["evidence"]
    assert all(c["status"] == "unavailable" for c in result["intelligence_components"].values())


def test_invalid_config_and_artifact_shapes_fail(config):
    broken = deepcopy(config)
    broken["fusion"]["weights"]["gnn"] = float("nan")
    with pytest.raises(ValueError, match="fusion weights"):
        validate_config(broken)
    model = RelationalSAGE(config["gnn"], 1)
    artifact = model.to_dict()
    artifact["parameters"]["w1"] = [[0]]
    with pytest.raises(ValueError, match="artifact parameters"):
        RelationalSAGE.from_dict(artifact)
