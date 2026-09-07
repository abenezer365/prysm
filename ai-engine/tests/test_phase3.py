"""Metric edge cases, split boundaries, selection and observer isolation."""
from copy import deepcopy
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from prysm_intelligence.metrics import classification, ranking
from prysm_intelligence.evaluation import select_trial, verify_observations, frame_from_results
from prysm_intelligence.gnn import RelationalSAGE
from prysm_intelligence.graph import GraphSample, NODE_FEATURES, RELATIONS


def test_hand_calculated_metrics_and_tied_operating_points():
    m = classification([0, 1, 0, 1], [.1, .4, .4, .9], .4)
    assert m["confusion"] == {"tn": 1, "fp": 1, "fn": 0, "tp": 2}
    assert m["precision"] == pytest.approx(2/3)
    assert m["f1"] == pytest.approx(.8)
    assert m["roc_auc"] == pytest.approx(.875)
    assert m["average_precision"] == pytest.approx(5/6)
    tied = classification([0, 1], [.5, .5])
    assert tied["roc_auc"] == .5
    assert tied["average_precision"] == .5


def test_missing_and_single_class_are_not_fabricated_negatives():
    m = classification([1, 0], [None, .1])
    assert m["unavailable"] == 1 and m["support"] == 1
    assert m["roc_auc"] is None and m["average_precision"] is None
    assert classification([], [])["support"] == 0
    assert classification([1], [.1])["precision"] == 0


@pytest.mark.parametrize("labels,scores", [([2], [.5]), ([1], [2]), ([1], [float('inf')]), ([1, 0], [.1]), ([[1]], [[.2]])])
def test_metrics_reject_invalid_input(labels, scores):
    with pytest.raises(ValueError):
        classification(labels, scores)


def test_ranking_uses_stable_key_ties_and_counts_unavailable_positives():
    r = ranking([1, 0, 1], [.5, .5, None], ["b", "a", "c"], (1, 10))
    assert r["1"]["precision"] == 0
    assert r["10"] == {"returned": 2, "true_positives": 1, "precision": .5, "recall": .5}
    with pytest.raises(ValueError):
        ranking([1, 0], [.5, .5], ["a", "a"])


def test_selection_prefers_quality_then_simplicity_without_test_metrics():
    a = {"name": "large", "validation": {"f1": .8, "average_precision": .9}, "parameters": 900, "config": {"epochs": 180}, "threshold": .65}
    b = {**a, "name": "small", "parameters": 300, "test": {"f1": 0}}
    assert select_trial([a, b])["name"] == "small"
    a["validation"] = {"f1": .9, "average_precision": .9}
    assert select_trial([a, b])["name"] == "large"


def test_partition_validation_rejects_overlap_and_future_training():
    d = pd.DataFrame({"ground_truth_id": list("abcdef"), "entity_key": list("abcdef"),
                      "split": ["train", "train", "validation", "validation", "test", "test"],
                      "is_suspicious": [False, True]*3, "as_of": pd.to_datetime(["2025-01-01"]*2+["2025-02-01"]*2+["2025-03-01"]*2, utc=True)})
    verify_observations(d)
    bad = d.copy()
    bad.loc[5, "entity_key"] = "a"
    with pytest.raises(ValueError):
        verify_observations(bad)
    bad = d.copy()
    bad.loc[0, "as_of"] = pd.Timestamp("2025-04-01", tz="UTC")
    with pytest.raises(ValueError):
        verify_observations(bad)


def test_observer_does_not_change_training():
    rng = np.random.default_rng(4)
    samples = [GraphSample(rng.normal(size=(3, len(NODE_FEATURES))), np.zeros((len(RELATIONS), 3, 3)), 0, ["a", "b", "c"], {}) for _ in range(4)]
    config = {"hidden_dim": 4, "epochs": 12, "learning_rate": .025, "l2": .001, "threshold": .65}
    seen = []
    def observe(model, epoch):
        seen.append(epoch)
        model._forward(samples[0])
    a = RelationalSAGE(deepcopy(config), 7).fit(samples, [0, 1, 0, 1])
    b = RelationalSAGE(deepcopy(config), 7).fit(samples, [0, 1, 0, 1], observe)
    assert seen == [1, 10, 12]
    assert a.to_dict() == b.to_dict()


def test_evaluation_join_rejects_cutoff_or_identity_mismatch():
    rows = pd.DataFrame({"entity_key": ["Person:1"], "as_of": ["2025-01-01T00:00:00Z"]})
    with pytest.raises(ValueError, match="identity or cutoff"):
        frame_from_results(rows, [{"subject": {"entity_key": "Person:2"}, "investigation_window": {"cutoff": "2025-01-01T00:00:00Z"}}])


def test_business_graph_activity_is_not_hidden_by_quiet_personal_account():
    from prysm_intelligence.pipeline import DEFAULT_DATASET, load_config
    from prysm_intelligence.data import Dataset
    from prysm_intelligence.engine import IntelligenceEngine
    class ConstantGraphModel:
        def to_dict(self):
            return {"test_model": True}
        def predict(self, sample):
            assert sample.adjacency.sum() > 0
            return .1
    dataset = Dataset.load(DEFAULT_DATASET)
    rows = pd.read_parquet(DEFAULT_DATASET / "ground_truth.parquet")
    row = rows[rows.split.eq("validation") & rows.scenario.eq("declared_trading")].iloc[0]
    result = IntelligenceEngine(dataset, load_config(), gnn=ConstantGraphModel()).investigate(row.entity_key, row.as_of)
    assert result["features"]["recent_count"] == 0
    assert result["intelligence_components"]["gnn"]["strength"] == .1
    assert result["intelligence_components"]["rules"]["strength"] == 0
    assert result["intelligence_components"]["network"]["strength"] == 0
    assert result["intelligence_components"]["anomaly"]["status"] == "unavailable"
    assert result["assessment"]["strength"] is not None
