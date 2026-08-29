"""Deterministically repair ground-truth evidence using immutable source datasets.

The repaired artifact preserves the original ground-truth schema and row identity.
Only ``related_entity_ids`` is replaced. Unsupported scenarios receive an empty
evidence list and an explicit reason in the companion decision/report artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any, Iterable

import polars as pl


TRANSACTION_COLUMNS = [
    "transaction_id",
    "timestamp",
    "sender_account_id",
    "receiver_account_id",
    "amount_etb",
    "currency",
    "transaction_type",
    "device_id",
    "invoice_id",
    "status",
]


@dataclass(frozen=True)
class RepairConfig:
    structuring_limit_etb: float = 200_000.0
    pattern_min_transactions: int = 3
    repeated_window_days: int = 7
    rapid_hours: int = 24
    layering_hours: int = 72
    round_trip_days: int = 30
    max_evidence_transactions: int = 8


def _json_default(value: Any) -> str:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Cannot serialize {type(value)!r}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, default=_json_default, sort_keys=True, separators=(",", ":"))


def _end_of_day(value: date) -> datetime:
    return datetime.combine(value, time.max)


def _entity_key(entity_type: str, entity_id: str) -> tuple[str, str]:
    return str(entity_type), str(entity_id)


def build_entity_account_index(
    ground_truth: pl.DataFrame,
    accounts: pl.DataFrame,
    persons: pl.DataFrame,
    companies: pl.DataFrame,
) -> tuple[dict[str, tuple[str, ...]], dict[str, str | None]]:
    """Resolve every label to its real accounts without fuzzy ID matching."""
    account_ids = set(accounts.get_column("account_id").drop_nulls().to_list())
    person_ids = set(persons.get_column("person_id").drop_nulls().to_list())
    company_ids = set(companies.get_column("company_id").drop_nulls().to_list())
    owned: dict[tuple[str, str], list[str]] = defaultdict(list)
    for row in accounts.select("owner_type", "owner_id", "account_id").iter_rows(named=True):
        owned[_entity_key(row["owner_type"], row["owner_id"])].append(row["account_id"])

    resolved: dict[str, tuple[str, ...]] = {}
    errors: dict[str, str | None] = {}
    for row in ground_truth.select("ground_truth_id", "entity_type", "entity_id").iter_rows(named=True):
        gt_id = row["ground_truth_id"]
        entity_type = row["entity_type"]
        entity_id = row["entity_id"]
        exists = (
            entity_id in account_ids
            if entity_type == "Account"
            else entity_id in person_ids
            if entity_type == "Person"
            else entity_id in company_ids
            if entity_type == "Company"
            else False
        )
        if not exists:
            resolved[gt_id] = ()
            errors[gt_id] = "labeled_entity_not_found"
            continue
        accounts_for_label = (
            (entity_id,) if entity_type == "Account" else tuple(sorted(owned.get((entity_type, entity_id), [])))
        )
        resolved[gt_id] = accounts_for_label
        errors[gt_id] = None if accounts_for_label else "labeled_entity_has_no_account"
    return resolved, errors


def build_candidate_events(
    ground_truth: pl.DataFrame,
    transactions: pl.DataFrame,
    account_index: dict[str, tuple[str, ...]],
) -> dict[str, list[dict[str, Any]]]:
    """Use joins to produce only direct, completed, in-window label events."""
    label_account_rows = [
        {"ground_truth_id": gt_id, "account_id": account_id}
        for gt_id, account_ids in account_index.items()
        for account_id in account_ids
    ]
    if not label_account_rows:
        return {}
    label_accounts = pl.DataFrame(label_account_rows)
    tx = transactions.select(TRANSACTION_COLUMNS).filter(pl.col("status") == "Completed")
    outbound = tx.join(
        label_accounts,
        left_on="sender_account_id",
        right_on="account_id",
        how="inner",
    )
    inbound = tx.join(
        label_accounts,
        left_on="receiver_account_id",
        right_on="account_id",
        how="inner",
    )
    candidates = (
        pl.concat([outbound, inbound], how="vertical")
        .unique(subset=["ground_truth_id", "transaction_id"], keep="first")
        .join(
            ground_truth.select("ground_truth_id", "pattern_start", "pattern_end"),
            on="ground_truth_id",
            how="inner",
        )
        .filter(pl.col("timestamp") >= pl.col("pattern_start").cast(pl.Datetime))
        .filter(
            pl.col("pattern_end").is_null()
            | (pl.col("timestamp") <= pl.col("pattern_end").cast(pl.Datetime) + pl.duration(days=1) - pl.duration(microseconds=1))
        )
        .sort(["ground_truth_id", "timestamp", "transaction_id"])
    )
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in candidates.drop("pattern_start", "pattern_end").iter_rows(named=True):
        grouped[row.pop("ground_truth_id")].append(row)
    return dict(grouped)


def _direction(event: dict[str, Any], accounts: set[str]) -> str:
    sender_owned = event["sender_account_id"] in accounts
    receiver_owned = event["receiver_account_id"] in accounts
    if sender_owned and receiver_owned:
        return "internal"
    return "outbound" if sender_owned else "inbound"


def _counterparty(event: dict[str, Any], accounts: set[str]) -> str | None:
    direction = _direction(event, accounts)
    if direction == "outbound":
        return event["receiver_account_id"]
    if direction == "inbound":
        return event["sender_account_id"]
    return None


def _rolling_group(
    events: list[dict[str, Any]],
    days: int,
    minimum: int,
    key,
) -> list[dict[str, Any]]:
    for start in range(len(events)):
        deadline = events[start]["timestamp"] + timedelta(days=days)
        window = [event for event in events[start:] if event["timestamp"] <= deadline]
        groups: dict[Any, list[dict[str, Any]]] = defaultdict(list)
        for event in window:
            groups[key(event)].append(event)
        eligible = [group for group in groups.values() if len(group) >= minimum]
        if eligible:
            return sorted(eligible, key=lambda group: (group[0]["timestamp"], group[0]["transaction_id"]))[0]
    return []


def _paired_flow(
    events: list[dict[str, Any]],
    accounts: set[str],
    max_hours: int,
    min_ratio: float,
    max_ratio: float,
    require_different_counterparties: bool,
) -> list[dict[str, Any]]:
    inbound = [event for event in events if _direction(event, accounts) == "inbound"]
    outbound = [event for event in events if _direction(event, accounts) == "outbound"]
    for received in inbound:
        for sent in outbound:
            delta = sent["timestamp"] - received["timestamp"]
            if delta < timedelta(0) or delta > timedelta(hours=max_hours):
                continue
            received_amount = float(received["amount_etb"] or 0.0)
            sent_amount = float(sent["amount_etb"] or 0.0)
            if received_amount <= 0 or not min_ratio <= sent_amount / received_amount <= max_ratio:
                continue
            if require_different_counterparties and _counterparty(received, accounts) == _counterparty(sent, accounts):
                continue
            return [received, sent]
    return []


def _round_trip(events: list[dict[str, Any]], accounts: set[str], days: int) -> list[dict[str, Any]]:
    by_counterparty: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        counterparty = _counterparty(event, accounts)
        if counterparty:
            by_counterparty[counterparty].append(event)
    for counterparty in sorted(by_counterparty):
        path = by_counterparty[counterparty]
        for first_index, first in enumerate(path):
            for second in path[first_index + 1 :]:
                if second["timestamp"] - first["timestamp"] > timedelta(days=days):
                    break
                if _direction(first, accounts) == _direction(second, accounts):
                    continue
                first_amount = float(first["amount_etb"] or 0.0)
                second_amount = float(second["amount_etb"] or 0.0)
                if first_amount > 0 and 0.5 <= second_amount / first_amount <= 2.0:
                    return [first, second]
    return []


def select_scenario_evidence(
    label: dict[str, Any],
    events: list[dict[str, Any]],
    accounts: set[str],
    invoice_index: dict[str, tuple[str, str, str, str]],
    account_owner_index: dict[str, tuple[str, str]],
    config: RepairConfig,
) -> tuple[list[dict[str, Any]], str | None]:
    """Return semantically supported direct transactions or an honest reason."""
    behavior = label["behavior_type"]
    if not events:
        return [], "no_completed_affiliated_transaction_in_window"

    if behavior == "normal":
        return events[: config.max_evidence_transactions], None

    if behavior == "rapid_movement":
        selected = _paired_flow(events, accounts, config.rapid_hours, 0.5, 2.0, False)
        return (selected, None) if selected else ([], "no_inflow_outflow_pair_within_rapid_window")

    if behavior == "layering":
        selected = _paired_flow(events, accounts, config.layering_hours, 0.7, 1.3, True)
        return (selected, None) if selected else ([], "no_layered_flow_between_distinct_counterparties")

    if behavior == "round_tripping":
        selected = _round_trip(events, accounts, config.round_trip_days)
        return (selected, None) if selected else ([], "no_opposite_flow_with_same_counterparty")

    if behavior == "structuring":
        eligible = [
            event
            for event in events
            if _direction(event, accounts) in {"inbound", "outbound"}
            and 0 < float(event["amount_etb"] or 0.0) < config.structuring_limit_etb
        ]
        selected = _rolling_group(
            eligible,
            config.repeated_window_days,
            config.pattern_min_transactions,
            lambda event: _direction(event, accounts),
        )
        return (selected[: config.max_evidence_transactions], None) if selected else ([], "no_repeated_sub_threshold_movements")

    if behavior == "smurfing":
        eligible = [
            event
            for event in events
            if _direction(event, accounts) == "inbound"
            and 0 < float(event["amount_etb"] or 0.0) < config.structuring_limit_etb
        ]
        for start in range(len(eligible)):
            deadline = eligible[start]["timestamp"] + timedelta(days=config.repeated_window_days)
            window = [event for event in eligible[start:] if event["timestamp"] <= deadline]
            distinct: dict[str, dict[str, Any]] = {}
            for event in window:
                distinct.setdefault(event["sender_account_id"], event)
            if len(distinct) >= config.pattern_min_transactions:
                selected = sorted(distinct.values(), key=lambda event: (event["timestamp"], event["transaction_id"]))
                return selected[: config.max_evidence_transactions], None
        return [], "no_repeated_inflows_from_distinct_accounts"

    if behavior == "false_invoice":
        identities = {(label["entity_type"], label["entity_id"])}
        if label["entity_type"] == "Account" and label["entity_id"] in account_owner_index:
            identities.add(account_owner_index[label["entity_id"]])
        selected = []
        for event in events:
            invoice = invoice_index.get(event["invoice_id"])
            if invoice and ({(invoice[0], invoice[1]), (invoice[2], invoice[3])} & identities):
                selected.append(event)
        return (selected[: config.max_evidence_transactions], None) if selected else ([], "no_affiliated_transaction_with_subject_linked_invoice")

    if behavior == "shell_company":
        return [], "shell_company_behavior_not_observable_in_existing_activity_fields"

    return [], f"unsupported_behavior_type:{behavior}"


def _connected_accounts(selected: Iterable[dict[str, Any]], accounts: set[str]) -> list[str]:
    connected = {_counterparty(event, accounts) for event in selected}
    return sorted(value for value in connected if value is not None)


def audit_original_evidence(
    ground_truth: pl.DataFrame,
    transactions: pl.DataFrame,
    account_index: dict[str, tuple[str, ...]],
) -> dict[str, int]:
    transaction_ids = set(transactions.get_column("transaction_id").to_list())
    referenced = {
        value
        for values in ground_truth.get_column("related_entity_ids").to_list()
        for value in (values or [])
        if value in transaction_ids
    }
    referenced_tx = {
        row["transaction_id"]: row
        for row in transactions.filter(pl.col("transaction_id").is_in(list(referenced))).select(
            "transaction_id", "timestamp", "sender_account_id", "receiver_account_id"
        ).iter_rows(named=True)
    }
    valid = invalid = temporal = labels_with_valid = 0
    for label in ground_truth.iter_rows(named=True):
        accounts = set(account_index[label["ground_truth_id"]])
        has_valid = False
        start = datetime.combine(label["pattern_start"], time.min)
        end = _end_of_day(label["pattern_end"]) if label["pattern_end"] else None
        for value in label["related_entity_ids"] or []:
            event = referenced_tx.get(value)
            if not event:
                continue
            affiliated = event["sender_account_id"] in accounts or event["receiver_account_id"] in accounts
            if affiliated:
                valid += 1
                has_valid = True
                if event["timestamp"] < start or (end and event["timestamp"] > end):
                    temporal += 1
            else:
                invalid += 1
        labels_with_valid += int(has_valid)
    return {
        "declared_transaction_references": valid + invalid,
        "valid_transaction_affiliations": valid,
        "invalid_transaction_affiliations": invalid,
        "temporal_violations_among_valid_affiliations": temporal,
        "labels_with_any_valid_transaction_reference": labels_with_valid,
    }


def repair_frames(
    ground_truth: pl.DataFrame,
    accounts: pl.DataFrame,
    transactions: pl.DataFrame,
    persons: pl.DataFrame,
    companies: pl.DataFrame,
    invoices: pl.DataFrame,
    config: RepairConfig = RepairConfig(),
) -> tuple[pl.DataFrame, dict[str, Any], list[dict[str, Any]]]:
    """Repair in memory and return artifact, validation report, and decisions."""
    original_schema = ground_truth.schema
    account_index, resolution_errors = build_entity_account_index(ground_truth, accounts, persons, companies)
    candidates = build_candidate_events(ground_truth, transactions, account_index)
    account_owner_index = {
        row["account_id"]: (row["owner_type"], row["owner_id"])
        for row in accounts.select("account_id", "owner_type", "owner_id").iter_rows(named=True)
    }
    invoice_index = {
        row["invoice_id"]: (
            row["issuer_type"],
            row["issuer_id"],
            row["recipient_type"],
            row["recipient_id"],
        )
        for row in invoices.select(
            "invoice_id", "issuer_type", "issuer_id", "recipient_type", "recipient_id"
        ).iter_rows(named=True)
    }

    repaired_values: list[list[str]] = []
    decisions: list[dict[str, Any]] = []
    reason_counts: Counter[str] = Counter()
    scenario_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for label in ground_truth.iter_rows(named=True):
        gt_id = label["ground_truth_id"]
        accounts_for_label = set(account_index[gt_id])
        reason = resolution_errors[gt_id]
        selected: list[dict[str, Any]] = []
        if reason is None:
            selected, reason = select_scenario_evidence(
                label,
                candidates.get(gt_id, []),
                accounts_for_label,
                invoice_index,
                account_owner_index,
                config,
            )
        evidence_ids = [event["transaction_id"] for event in selected]
        connected_accounts = _connected_accounts(selected, accounts_for_label)
        connected_entities = sorted(
            f"{account_owner_index[account_id][0]}:{account_owner_index[account_id][1]}"
            for account_id in connected_accounts
            if account_id in account_owner_index
        )
        repaired_values.append(evidence_ids)
        status = "supported" if evidence_ids else "unsupported"
        scenario_counts[label["behavior_type"]][status] += 1
        if reason:
            reason_counts[reason] += 1
        decisions.append(
            {
                "ground_truth_id": gt_id,
                "entity_type": label["entity_type"],
                "entity_id": label["entity_id"],
                "behavior_type": label["behavior_type"],
                "status": status,
                "reason": reason,
                "resolved_account_ids": sorted(accounts_for_label),
                "evidence_transaction_ids": evidence_ids,
                "connected_counterparty_account_ids": connected_accounts,
                "connected_counterparty_entities": connected_entities,
            }
        )

    repaired = ground_truth.with_columns(
        pl.Series("related_entity_ids", repaired_values, dtype=original_schema["related_entity_ids"])
    )
    if repaired.columns != ground_truth.columns or repaired.schema != original_schema:
        raise AssertionError("Repaired ground truth did not preserve the exact source schema")

    after = validate_repaired(ground_truth, repaired, accounts, transactions)
    original = audit_original_evidence(ground_truth, transactions, account_index)
    supported = sum(decision["status"] == "supported" for decision in decisions)
    report: dict[str, Any] = {
        "algorithm": "prysm-ground-truth-affiliation-repair-v1",
        "deterministic": True,
        "source_data_modified": False,
        "original_label_count": ground_truth.height,
        "repaired_label_count": repaired.height,
        "supported_scenario_count": supported,
        "unsupported_scenario_count": repaired.height - supported,
        "evidence_coverage": supported / repaired.height if repaired.height else 0.0,
        "before": original,
        "after": after,
        "scenario_distribution": {
            behavior: dict(sorted(counts.items())) for behavior, counts in sorted(scenario_counts.items())
        },
        "unresolved_reason_distribution": dict(sorted(reason_counts.items())),
        "unresolved_cases": [
            {
                "ground_truth_id": item["ground_truth_id"],
                "behavior_type": item["behavior_type"],
                "reason": item["reason"],
            }
            for item in decisions
            if item["status"] == "unsupported"
        ],
        "configuration": config.__dict__,
        "invariants": {
            "identical_columns": repaired.columns == ground_truth.columns,
            "identical_schema": repaired.schema == ground_truth.schema,
            "identical_label_count": repaired.height == ground_truth.height,
            "identical_ground_truth_ids": repaired["ground_truth_id"].to_list() == ground_truth["ground_truth_id"].to_list(),
            "zero_invalid_evidence_relationships": after["invalid_transaction_affiliations_remaining"] == 0,
            "zero_temporal_violations": after["temporal_violations"] == 0,
            "zero_fabricated_transaction_ids": after["fabricated_transaction_ids"] == 0,
        },
    }
    return repaired, report, decisions


def validate_repaired(
    original: pl.DataFrame,
    repaired: pl.DataFrame,
    accounts: pl.DataFrame,
    transactions: pl.DataFrame,
) -> dict[str, int]:
    """Independently validate entity → account → transaction and time ordering."""
    owner_accounts: dict[tuple[str, str], set[str]] = defaultdict(set)
    account_ids = set(accounts.get_column("account_id").to_list())
    for row in accounts.select("owner_type", "owner_id", "account_id").iter_rows(named=True):
        owner_accounts[(row["owner_type"], row["owner_id"])].add(row["account_id"])
    evidence_ids = {
        value
        for values in repaired.get_column("related_entity_ids").to_list()
        for value in (values or [])
    }
    tx_index = {
        row["transaction_id"]: row
        for row in transactions.filter(pl.col("transaction_id").is_in(list(evidence_ids))).select(
            "transaction_id", "timestamp", "sender_account_id", "receiver_account_id"
        ).iter_rows(named=True)
    }
    valid_entities = invalid_entities = valid_tx = invalid_tx = temporal = fabricated = 0
    for label in repaired.iter_rows(named=True):
        if label["entity_type"] == "Account":
            subject_accounts = {label["entity_id"]} if label["entity_id"] in account_ids else set()
        else:
            subject_accounts = owner_accounts.get((label["entity_type"], label["entity_id"]), set())
        if subject_accounts:
            valid_entities += 1
        else:
            invalid_entities += 1
        start = datetime.combine(label["pattern_start"], time.min)
        end = _end_of_day(label["pattern_end"]) if label["pattern_end"] else None
        for evidence_id in label["related_entity_ids"] or []:
            event = tx_index.get(evidence_id)
            if event is None:
                fabricated += 1
                continue
            if event["sender_account_id"] in subject_accounts or event["receiver_account_id"] in subject_accounts:
                valid_tx += 1
            else:
                invalid_tx += 1
            if event["timestamp"] < start or (end and event["timestamp"] > end):
                temporal += 1
    return {
        "valid_entity_affiliations": valid_entities,
        "invalid_entity_affiliations_remaining": invalid_entities,
        "valid_transaction_affiliations": valid_tx,
        "invalid_transaction_affiliations_remaining": invalid_tx,
        "temporal_violations": temporal,
        "fabricated_transaction_ids": fabricated,
    }


def load_sources(source_dir: Path) -> dict[str, pl.DataFrame]:
    required = {
        "ground_truth": None,
        "accounts": ["account_id", "owner_id", "owner_type"],
        "transactions": TRANSACTION_COLUMNS,
        "persons": ["person_id"],
        "companies": ["company_id"],
        "invoices": ["invoice_id", "issuer_id", "issuer_type", "recipient_id", "recipient_type"],
    }
    sources: dict[str, pl.DataFrame] = {}
    for name, columns in required.items():
        path = source_dir / f"{name}.parquet"
        if not path.exists():
            raise FileNotFoundError(f"Required source dataset not found: {path}")
        sources[name] = pl.read_parquet(path, columns=columns)
    return sources


def run(source_dir: Path, output_dir: Path, verify_determinism: bool = True) -> dict[str, Any]:
    sources = load_sources(source_dir)
    repaired, report, decisions = repair_frames(**sources)
    if verify_determinism:
        second_repaired, second_report, second_decisions = repair_frames(**sources)
        if not repaired.equals(second_repaired) or _canonical_json(report) != _canonical_json(second_report):
            raise AssertionError("In-memory deterministic rerun did not match")
        if _canonical_json(decisions) != _canonical_json(second_decisions):
            raise AssertionError("Decision artifact changed across deterministic rerun")

    output_dir.mkdir(parents=True, exist_ok=True)
    repaired_path = output_dir / "repaired_ground_truth.parquet"
    report_path = output_dir / "validation_report.json"
    decisions_path = output_dir / "repair_decisions.jsonl"
    repaired.write_parquet(repaired_path, compression="zstd", statistics=True)
    decisions_text = "".join(_canonical_json(item) + "\n" for item in decisions)
    decisions_path.write_text(decisions_text, encoding="utf-8", newline="\n")
    report["artifacts"] = {
        "repaired_ground_truth": repaired_path.name,
        "repair_decisions": decisions_path.name,
        "repaired_ground_truth_sha256": _sha256(repaired_path),
        "repair_decisions_sha256": _sha256(decisions_path),
    }
    report_path.write_text(json.dumps(report, indent=2, default=_json_default, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    default_source = Path(__file__).resolve().parents[1] / "synthetic-financial-generator" / "data" / "raw"
    default_output = Path(__file__).resolve().parent / "output"
    parser.add_argument("--source-dir", type=Path, default=default_source)
    parser.add_argument("--output-dir", type=Path, default=default_output)
    parser.add_argument("--skip-determinism-check", action="store_true")
    args = parser.parse_args()
    report = run(args.source_dir.resolve(), args.output_dir.resolve(), not args.skip_determinism_check)
    print(json.dumps({
        "repaired_label_count": report["repaired_label_count"],
        "supported_scenario_count": report["supported_scenario_count"],
        "unsupported_scenario_count": report["unsupported_scenario_count"],
        "evidence_coverage": report["evidence_coverage"],
        "after": report["after"],
        "artifacts": report["artifacts"],
    }, indent=2))


if __name__ == "__main__":
    main()
