import json

import numpy as np
import pandas as pd

from prysm_ai.contracts import SignalComponent
from prysm_ai.evidence import EvidenceEngine
from prysm_ai.fusion import SignalFusion
from prysm_ai.gnn import RelationalGraphSAGEEncoder, subgraph_raw_features
from prysm_ai.graph import GraphStore, _edge_frame, temporal_filter
from prysm_ai.graph_features import build_graph_features


def _edges():
    return _edge_frame(
        edge_id=["E1", "E2", "E3"], source_key=["Person:P1", "Account:A1", "Account:A1"],
        target_key=["Account:A1", "Account:A2", "Device:D1"], edge_type=["owns", "transfers", "uses_device"],
        temporal_kind=["interval", "event", "event"],
        event_time=pd.to_datetime(["2023-01-01", "2024-01-01", "2025-01-01"], utc=True),
        end_time=pd.to_datetime([None, None, None], utc=True), confidence=[1.0, 1.0, 1.0],
        amount_etb=[None, 100.0, None], transaction_id=[None, "T1", "T2"], source_table="fixture",
    )


def test_temporal_filter_excludes_future_and_preserves_open_interval():
    filtered = temporal_filter(_edges(), pd.Timestamp("2024-06-01", tz="UTC"), 365, "predictive")
    assert filtered.edge_id.tolist() == ["E1", "E2"]
    assert len(temporal_filter(_edges(), pd.Timestamp("2024-06-01", tz="UTC"), 365, "retrospective")) == 3


def test_bounded_subgraph_is_typed_deterministic_and_hop_limited(tmp_path):
    graph = tmp_path / "graph"; (graph / "edges").mkdir(parents=True)
    nodes = pd.DataFrame({"node_key": ["Account:A1", "Account:A2", "Device:D1", "Person:P1"],
                          "node_type": ["Account", "Account", "Device", "Person"], "source_id": ["A1", "A2", "D1", "P1"]})
    nodes.to_parquet(graph / "nodes.parquet", index=False); _edges().to_parquet(graph / "edges" / "fixture.parquet", index=False)
    store = GraphStore(graph)
    first = store.subgraph("Person:P1", pd.Timestamp("2024-06-01", tz="UTC"), max_hops=1, max_nodes=2, lookback_days=365)
    second = store.subgraph("Person:P1", pd.Timestamp("2024-06-01", tz="UTC"), max_hops=1, max_nodes=2, lookback_days=365)
    assert first[0].node_key.tolist() == ["Account:A1", "Person:P1"]
    pd.testing.assert_frame_equal(first[1], second[1])
    assert set(first[1].edge_type) == {"owns"}


def test_graph_features_include_owner_financial_aggregation_and_validation(tmp_path):
    graph = tmp_path / "graph"; (graph / "edges").mkdir(parents=True)
    nodes = pd.DataFrame({"node_key": ["Account:A1", "Account:A2", "Person:P1"],
                          "node_type": ["Account", "Account", "Person"], "source_id": ["A1", "A2", "P1"]})
    nodes.to_parquet(graph / "nodes.parquet", index=False)
    _edges().iloc[[0]].to_parquet(graph / "edges" / "ownership.parquet", index=False)
    _edges().iloc[[1]].to_parquet(graph / "edges" / "transfers.parquet", index=False)
    report = build_graph_features(graph, tmp_path / "report.json")
    features = pd.read_parquet(graph / "node_features.parquet").set_index("node_key")
    assert report["invalid_endpoints"] == 0 and report["duplicate_edge_id_rows"] == 0
    assert features.loc["Account:A1", "unique_counterparties"] == 1
    assert features.loc["Person:P1", "network_transaction_count"] == 1
    assert features.loc["Person:P1", "network_transaction_volume_etb"] == 100


def test_gnn_forward_and_serialization_are_deterministic():
    x = np.array([[1, 0], [0, 1], [1, 1]], np.float32); types = np.array([0, 1, 0])
    source, target, relation = np.array([0, 1]), np.array([1, 2]), np.array([0, 1])
    encoder = RelationalGraphSAGEEncoder(2, 2, 2, hidden_dim=4, layers=2, random_seed=7, batch_size=1)
    output = encoder.forward(x, types, source, target, relation)
    restored = RelationalGraphSAGEEncoder.from_dict(encoder.to_dict())
    assert output.shape == (3, 4)
    assert np.allclose(output, restored.forward(x, types, source, target, relation))
    first = RelationalGraphSAGEEncoder(2, 2, 2, hidden_dim=4, layers=1, random_seed=9)
    second = RelationalGraphSAGEEncoder(2, 2, 2, hidden_dim=4, layers=1, random_seed=9)
    h1 = first.forward(x, types, source, target, relation); h2 = second.forward(x, types, source, target, relation)
    loss1 = first.fit_contrastive_projection(h1, source, target, types, 2, .01, 2, .001)
    loss2 = second.fit_contrastive_projection(h2, source, target, types, 2, .01, 2, .001)
    assert np.allclose(loss1, loss2) and np.allclose(first.projection, second.projection)


def test_gnn_inputs_use_only_the_temporally_filtered_subgraph():
    nodes = pd.DataFrame({"node_key": ["Account:A1", "Account:A2", "Device:D1", "Person:P1"],
                          "node_type": ["Account", "Account", "Device", "Person"]})
    columns = ["degree", "in_degree", "out_degree", "edge_type_diversity", "network_transaction_count",
               "network_transaction_volume_etb", "network_unique_counterparties", "connected_account_count",
               "connected_company_count", "shared_device_count", "shared_address_count", "component_size"]
    filtered = temporal_filter(_edges(), pd.Timestamp("2024-06-01", tz="UTC"), 365, "predictive")
    raw = subgraph_raw_features(nodes, filtered, columns).set_index("node_key")
    assert raw.loc["Account:A1", "degree"] == 2
    assert raw.loc["Account:A1", "network_transaction_count"] == 1
    assert raw.loc["Device:D1", "degree"] == 0  # future device-use edge is absent


def test_fusion_renormalizes_missing_signals_and_keeps_confidence_separate():
    config = {"weights": {"graph": 2.0, "rule": 1.0}, "attention_thresholds": {"low": .25, "moderate": .5, "elevated": .75}, "minimum_confidence": .2}
    fusion = SignalFusion(config)
    components = {"graph": SignalComponent("graph", "available", .8, .5, "structural"),
                  "rule": SignalComponent("rule", "unavailable", None, 0, "missing")}
    result = fusion.combine(components)
    assert result["strength"] == .8
    assert result["confidence"]["score"] < .5
    assert not result["is_fraud_probability"]


def test_evidence_preserves_only_supplied_source_identifiers():
    finding = {"rule_id": "R1", "ground_truth_id": "G1", "explanation": "Observed pattern", "severity": "low",
               "score": .6, "entity_ids": ["Account:A1"], "transaction_ids": ["T1", "T2"],
               "measurements": {"count": 2}, "as_of": "2024-01-01T00:00:00Z"}
    item = EvidenceEngine().from_rule("Account:A1", finding)
    assert item.supporting_transaction_ids == ["T1", "T2"]
    assert item.supporting_relationship_ids == []
    assert item.provenance["source"] == "signals/rule_findings.jsonl"
    anomaly = EvidenceEngine().anomaly_signal("Account:A1", .7, "m1", .4, ["T1"], "2024-01-01T00:00:00Z")
    assert anomaly.supporting_transaction_ids == ["T1"]
    assert anomaly.provenance["model_artifact"] == "artifacts/anomaly_model.json"
