import json
from pathlib import Path

import numpy as np
import pandas as pd

from prysm_ai.evaluation import binary_metrics, temporal_entity_split
from prysm_ai.features import AsOfFeatureBuilder, normalize_transactions
from prysm_ai.models import IsolationForestBaseline, LogisticBaseline, RobustPreprocessor
from prysm_ai.rules import RuleEngine


UTC = "UTC"


def _accounts():
    return pd.DataFrame({
        "account_id": ["A1", "A2"], "owner_key": ["Person:P1", "Person:P2"],
        "currency": ["ETB", "ETB"], "opened_at": pd.to_datetime(["2023-01-01"] * 2, utc=True),
        "closed_at": pd.to_datetime([None, None], utc=True),
    })


def _transactions():
    return pd.DataFrame({
        "transaction_id": ["T1", "T2"],
        "timestamp": pd.to_datetime(["2024-01-01", "2024-02-01"], utc=True),
        "sender_account_id": ["A1", "A2"], "receiver_account_id": ["A2", "A1"],
        "amount": [100.0, 50.0], "currency": ["USD", "ETB"], "amount_etb": [5750.0, 50.0],
        "transaction_type": ["Transfer"] * 2, "channel": ["Branch"] * 2,
        "device_id": [None, "D1"], "invoice_id": ["I1", None], "status": ["Completed", "Failed"],
    })


def test_normalization_preserves_rows_and_semantic_missingness():
    invoices = pd.DataFrame({"invoice_id": ["I1"], "issue_date": pd.to_datetime(["2024-01-02"], utc=True)})
    result = normalize_transactions(_transactions(), _accounts(), invoices)
    assert len(result) == 2
    assert result.loc[0, "is_foreign_currency"]
    assert not result.loc[0, "has_device"]
    assert not result.loc[0, "invoice_chronology_valid"]
    assert np.isclose(result.loc[0, "amount_etb_log1p"], np.log1p(5750))


def test_asof_features_exclude_future_transactions():
    invoices = pd.DataFrame({"invoice_id": ["I1"], "issue_date": pd.to_datetime(["2023-12-01"], utc=True)})
    tx = normalize_transactions(_transactions(), _accounts(), invoices)
    relationships = pd.DataFrame(columns=["source_key", "target_key", "source_type", "target_type", "relationship_type", "start_time", "end_time", "confidence"])
    builder = AsOfFeatureBuilder(tx, _accounts(), relationships, {"Person:P1"})
    result = builder.build_one("Person:P1", pd.Timestamp("2024-01-15", tz=UTC))
    assert result["history_tx_count"] == 1
    assert result["history_outflow_etb"] == 5750


def test_temporal_split_is_forward_and_entity_disjoint():
    frame = pd.DataFrame({
        "entity_key": ["P:repeat", "P:a", "P:b", "P:c", "P:repeat"],
        "as_of": pd.to_datetime(["2022-01-01", "2022-02-01", "2023-01-01", "2024-01-01", "2025-01-01"], utc=True),
    })
    split = temporal_entity_split(frame)
    entities = {name: set(frame.iloc[index]["entity_key"]) for name, index in split.items()}
    assert entities["train"].isdisjoint(entities["validation"] | entities["test"])
    assert 4 not in split["test"]  # later occurrence of a train entity is purged
    assert frame.iloc[split["train"]]["as_of"].max() < frame.iloc[split["validation"]]["as_of"].min()


def test_rule_trigger_and_non_trigger_are_config_driven():
    project = Path(__file__).resolve().parents[1]
    config = json.loads((project / "config" / "intelligence.json").read_text())["rules"]
    base = {"entity_key": "Account:A1", "history_tx_count": 10, "recent_amount_z": 0,
            "history_mean_amount_etb": 10, "tx_count_1d": 0, "tx_count_30d": 0, "inflow_etb_7d": 0,
            "outflow_etb_7d": 0, "outflow_ratio_7d": 0, "foreign_inflow_etb_30d": 0,
            "foreign_recent_to_history_ratio": 0, "counterparty_count_30d": 0,
            "recent_to_history_count_ratio": 0, "shared_device_relationship_count": 0,
            "shared_address_relationship_count": 0, "invoice_invalid_count_30d": 0}
    assert RuleEngine(config).evaluate(base) == []
    base["tx_count_1d"] = config["transaction_burst"]["count_24h"]
    finding = RuleEngine(config).evaluate(base)[0]
    assert finding.rule_id == "TX_BURST_24H" and finding.status == "triggered"


def test_models_are_reproducible_and_inference_metrics_work():
    x = np.array([[0.0, 0.0], [0.1, 0.2], [5.0, 5.0], [6.0, 5.0], [0.2, 0.1], [5.5, 6.0]])
    y = np.array([0, 0, 1, 1, 0, 1])
    prep = RobustPreprocessor().fit(x)
    z = prep.transform(x)
    logistic = LogisticBaseline(iterations=200).fit(z, y)
    assert logistic.predict_proba(z)[0] < logistic.predict_proba(z)[3]
    restored_logistic = LogisticBaseline.from_dict(logistic.to_dict())
    assert np.allclose(logistic.predict_proba(z), restored_logistic.predict_proba(z))
    first = IsolationForestBaseline(trees=8, sample_size=4, random_seed=7).fit(z)
    second = IsolationForestBaseline(trees=8, sample_size=4, random_seed=7).fit(z)
    assert np.allclose(first.score_samples(z), second.score_samples(z))
    restored_forest = IsolationForestBaseline.from_dict(first.to_dict())
    assert np.allclose(first.score_samples(z), restored_forest.score_samples(z))
    assert binary_metrics(y, logistic.predict_proba(z))["roc_auc"] > 0.9
