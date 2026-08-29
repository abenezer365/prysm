from __future__ import annotations

import importlib.util
import sys
from datetime import date, datetime
from pathlib import Path

import polars as pl


MODULE_PATH = Path(__file__).resolve().parents[1] / "repair_ground_truth.py"
SPEC = importlib.util.spec_from_file_location("repair_ground_truth", MODULE_PATH)
assert SPEC and SPEC.loader
repair = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = repair
SPEC.loader.exec_module(repair)


def _sources(labels: list[dict], transactions: list[dict]):
    ground_truth = pl.DataFrame(
        labels,
        schema={
            "ground_truth_id": pl.String,
            "entity_type": pl.String,
            "entity_id": pl.String,
            "behavior_type": pl.String,
            "risk_pattern": pl.String,
            "is_anomalous": pl.Boolean,
            "severity": pl.String,
            "pattern_start": pl.Date,
            "pattern_end": pl.Date,
            "related_entity_ids": pl.List(pl.String),
        },
    )
    accounts = pl.DataFrame(
        [
            {"account_id": "A1", "owner_id": "P1", "owner_type": "Person"},
            {"account_id": "A2", "owner_id": "P2", "owner_type": "Person"},
            {"account_id": "A3", "owner_id": "C1", "owner_type": "Company"},
        ]
    )
    tx_schema = {
        "transaction_id": pl.String,
        "timestamp": pl.Datetime,
        "sender_account_id": pl.String,
        "receiver_account_id": pl.String,
        "amount_etb": pl.Float64,
        "currency": pl.String,
        "transaction_type": pl.String,
        "device_id": pl.String,
        "invoice_id": pl.String,
        "status": pl.String,
    }
    tx = pl.DataFrame(transactions, schema=tx_schema)
    persons = pl.DataFrame({"person_id": ["P1", "P2"]})
    companies = pl.DataFrame({"company_id": ["C1"]})
    invoices = pl.DataFrame(
        {
            "invoice_id": ["I1"],
            "issuer_id": ["P1"],
            "issuer_type": ["Person"],
            "recipient_id": ["C1"],
            "recipient_type": ["Company"],
        }
    )
    return ground_truth, accounts, tx, persons, companies, invoices


def _label(gt_id="GT1", entity_type="Person", entity_id="P1", behavior="normal"):
    return {
        "ground_truth_id": gt_id,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "behavior_type": behavior,
        "risk_pattern": "NORMAL" if behavior == "normal" else "AML_HIGH",
        "is_anomalous": behavior != "normal",
        "severity": "info" if behavior == "normal" else "high",
        "pattern_start": date(2024, 1, 1),
        "pattern_end": date(2024, 1, 31),
        "related_entity_ids": ["FABRICATED"],
    }


def _tx(tx_id, timestamp, sender, receiver, amount=1000.0, invoice=None, status="Completed"):
    return {
        "transaction_id": tx_id,
        "timestamp": timestamp,
        "sender_account_id": sender,
        "receiver_account_id": receiver,
        "amount_etb": amount,
        "currency": "ETB",
        "transaction_type": "Transfer",
        "device_id": "D1",
        "invoice_id": invoice,
        "status": status,
    }


def test_entity_account_resolution_and_direct_affiliation():
    sources = _sources(
        [_label()],
        [
            _tx("T1", datetime(2024, 1, 5), "A1", "A2"),
            _tx("T2", datetime(2024, 1, 6), "A2", "A3"),
        ],
    )
    repaired, report, _ = repair.repair_frames(*sources)
    assert repaired["related_entity_ids"].to_list() == [["T1"]]
    assert report["after"]["valid_transaction_affiliations"] == 1
    assert report["after"]["invalid_transaction_affiliations_remaining"] == 0


def test_temporal_and_status_filtering():
    sources = _sources(
        [_label()],
        [
            _tx("BEFORE", datetime(2023, 12, 31, 23, 59), "A1", "A2"),
            _tx("FAILED", datetime(2024, 1, 10), "A1", "A2", status="Failed"),
            _tx("END", datetime(2024, 1, 31, 23, 59), "A2", "A1"),
            _tx("AFTER", datetime(2024, 2, 1), "A2", "A1"),
        ],
    )
    repaired, report, _ = repair.repair_frames(*sources)
    assert repaired["related_entity_ids"].to_list() == [["END"]]
    assert report["after"]["temporal_violations"] == 0


def test_rapid_movement_requires_directional_pair():
    sources = _sources(
        [_label(behavior="rapid_movement")],
        [
            _tx("IN", datetime(2024, 1, 10, 8), "A2", "A1", 10_000),
            _tx("OUT", datetime(2024, 1, 10, 12), "A1", "A3", 8_000),
        ],
    )
    repaired, _, decisions = repair.repair_frames(*sources)
    assert repaired["related_entity_ids"].to_list() == [["IN", "OUT"]]
    assert decisions[0]["status"] == "supported"


def test_smurfing_requires_distinct_inbound_accounts():
    accounts = ["A2", "A3", "A4"]
    transactions = [
        _tx(f"T{i}", datetime(2024, 1, 10 + i), account, "A1", 10_000)
        for i, account in enumerate(accounts)
    ]
    sources = list(_sources([_label(behavior="smurfing")], transactions))
    sources[1] = pl.concat(
        [sources[1], pl.DataFrame({"account_id": ["A4"], "owner_id": ["C1"], "owner_type": ["Company"]})]
    )
    repaired, _, _ = repair.repair_frames(*sources)
    assert repaired["related_entity_ids"].list.len().item() == 3


def test_false_invoice_requires_subject_invoice_party():
    sources = _sources(
        [_label(behavior="false_invoice")],
        [_tx("T1", datetime(2024, 1, 12), "A1", "A2", invoice="I1")],
    )
    repaired, _, _ = repair.repair_frames(*sources)
    assert repaired["related_entity_ids"].to_list() == [["T1"]]


def test_unobservable_scenario_is_unresolved_without_fabrication():
    sources = _sources(
        [_label(entity_type="Company", entity_id="C1", behavior="shell_company")],
        [_tx("T1", datetime(2024, 1, 12), "A3", "A2")],
    )
    repaired, report, decisions = repair.repair_frames(*sources)
    assert repaired["related_entity_ids"].to_list() == [[]]
    assert decisions[0]["status"] == "unsupported"
    assert report["after"]["fabricated_transaction_ids"] == 0


def test_schema_identity_and_deterministic_output():
    sources = _sources(
        [_label()],
        [_tx("T1", datetime(2024, 1, 5), "A1", "A2")],
    )
    first, first_report, first_decisions = repair.repair_frames(*sources)
    second, second_report, second_decisions = repair.repair_frames(*sources)
    assert first.schema == sources[0].schema
    assert first.columns == sources[0].columns
    assert first.equals(second)
    assert repair._canonical_json(first_report) == repair._canonical_json(second_report)
    assert repair._canonical_json(first_decisions) == repair._canonical_json(second_decisions)


def test_original_ground_truth_is_not_mutated():
    sources = _sources(
        [_label()],
        [_tx("T1", datetime(2024, 1, 5), "A1", "A2")],
    )
    original = sources[0].clone()
    repair.repair_frames(*sources)
    assert sources[0].equals(original)
