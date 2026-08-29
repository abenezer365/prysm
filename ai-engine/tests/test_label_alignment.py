import numpy as np
import pandas as pd

from prysm_ai.label_alignment import build_alignment_table


def _inputs(event_time="2024-01-02", history=5, related=True):
    labels = pd.DataFrame({
        "ground_truth_id": ["G1"], "entity_key": ["Person:P1"], "entity_type": ["Person"],
        "entity_id": ["P1"], "behavior_type": ["scenario"], "risk_pattern": ["RISK"],
        "is_anomalous": [True], "pattern_start": pd.to_datetime(["2024-01-01"], utc=True),
        "pattern_end": pd.to_datetime(["2024-01-10"], utc=True),
        "related_entity_ids": [np.array(["T1"]) if related else np.array(["P2"])],
    })
    transactions = pd.DataFrame({
        "transaction_id": ["T1"], "timestamp": pd.to_datetime([event_time], utc=True),
        "sender_account_id": ["A1"], "receiver_account_id": ["A2"],
    })
    accounts = pd.DataFrame({"account_id": ["A1", "A2"], "owner_key": ["Person:P1", "Person:P2"]})
    features = pd.DataFrame({"ground_truth_id": ["G1"], "history_tx_count": [history]})
    config = {"minimum_history_transactions": 5, "require_bounded_event_window": True,
              "require_affiliated_transaction_evidence": True, "require_event_after_cutoff": True}
    return labels, transactions, accounts, features, config


def test_affiliated_future_event_with_history_is_eligible():
    result = build_alignment_table(*_inputs())
    assert result.loc[0, "predictive_eligible"]
    assert result.loc[0, "aligned_future_event_count"] == 1
    assert result.loc[0, "source_label_unchanged"]


def test_pre_cutoff_event_is_not_future_target():
    result = build_alignment_table(*_inputs(event_time="2023-12-31"))
    assert not result.loc[0, "predictive_eligible"]
    assert result.loc[0, "related_before_cutoff_count"] == 1


def test_cold_start_is_explicit_and_not_relabelled():
    result = build_alignment_table(*_inputs(history=0))
    assert result.loc[0, "history_status"] == "cold_start_no_history"
    assert not result.loc[0, "predictive_eligible"]
    assert result.loc[0, "is_anomalous"]


def test_unaffiliated_or_missing_evidence_is_excluded_deterministically():
    inputs = _inputs(related=False)
    first = build_alignment_table(*inputs)
    second = build_alignment_table(*inputs)
    pd.testing.assert_frame_equal(first, second)
    assert first.loc[0, "evidence_status"] == "no_transaction_evidence"
    assert not first.loc[0, "predictive_eligible"]


def test_overlapping_labels_are_preserved_not_silently_deduplicated():
    labels, transactions, accounts, features, config = _inputs()
    second = labels.copy()
    second["ground_truth_id"] = "G2"
    second["pattern_start"] = pd.to_datetime(["2024-01-05"], utc=True)
    labels = pd.concat([labels, second], ignore_index=True)
    features = pd.concat([features, pd.DataFrame({"ground_truth_id": ["G2"], "history_tx_count": [5]})], ignore_index=True)
    result = build_alignment_table(labels, transactions, accounts, features, config)
    assert result["ground_truth_id"].tolist() == ["G1", "G2"]
    assert result["entity_key"].nunique() == 1
