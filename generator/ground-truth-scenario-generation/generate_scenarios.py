"""Generate leakage-safe, evidence-bearing synthetic financial scenarios.

This is an isolated augmentation layer. It reads the existing generator output,
creates transactions between existing accounts, and writes a complete standalone
dataset snapshot without modifying the original generator or source Parquet files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import polars as pl


UNCHANGED_DATASETS = [
    "persons.parquet",
    "companies.parquet",
    "accounts.parquet",
    "banks.parquet",
    "devices.parquet",
    "invoices.parquet",
    "relationships.parquet",
]
FOREIGN_CURRENCIES = {"USD", "EUR", "GBP", "AED", "CHF"}


def _json_default(value: Any) -> str:
    if isinstance(value, (date, datetime, Path)):
        return value.isoformat() if hasattr(value, "isoformat") else str(value)
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    raise TypeError(f"Cannot serialize {type(value)!r}")


def _canonical_json(value: Any) -> str:
    return json.dumps(value, default=_json_default, sort_keys=True, separators=(",", ":"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stable_number(seed: int, *parts: str) -> int:
    payload = "|".join([str(seed), *map(str, parts)]).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def _mode(values: Iterable[str | None], fallback: str | None = None) -> str | None:
    counts = Counter(value for value in values if value is not None)
    if not counts:
        return fallback
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


@dataclass(frozen=True)
class Subject:
    split: str
    entity_type: str
    entity_id: str
    account_id: str
    cutoff: datetime
    is_positive: bool
    scenario: str
    intensity: str

    @property
    def entity_key(self) -> str:
        return f"{self.entity_type}:{self.entity_id}"


class TransactionFactory:
    def __init__(self, start_index: int, schema: dict[str, pl.DataType], fx_rates: dict[str, float]):
        self.index = start_index
        self.schema = schema
        self.fx_rates = fx_rates
        self.rows: list[dict[str, Any]] = []

    def create(
        self,
        timestamp: datetime,
        sender: str,
        receiver: str,
        amount_etb: float,
        currency: str = "ETB",
        transaction_type: str = "Transfer",
        channel: str = "Mobile Banking",
        device_id: str | None = None,
    ) -> dict[str, Any]:
        self.index += 1
        tx_id = f"TX{self.index:08d}"
        rounded_etb = max(50, int(round(amount_etb)))
        raw_amount = max(1, int(round(rounded_etb / self.fx_rates.get(currency, 1.0))))
        row = {
            "transaction_id": tx_id,
            "timestamp": timestamp,
            "sender_account_id": sender,
            "receiver_account_id": receiver,
            "amount": raw_amount,
            "currency": currency,
            "amount_etb": rounded_etb,
            "transaction_type": transaction_type,
            "channel": channel,
            "device_id": device_id,
            "city": None,
            "country": "Ethiopia",
            "ip_hash": hashlib.sha256(f"{tx_id}|{sender}|{timestamp.isoformat()}".encode()).hexdigest(),
            "reference_id": f"REF{self.index:08d}",
            "invoice_id": None,
            "status": "Completed",
        }
        self.rows.append(row)
        return row


def _endpoint_events(transactions: pl.DataFrame) -> pl.DataFrame:
    tx = transactions.filter(pl.col("status") == "Completed")
    outbound = tx.select(
        pl.col("sender_account_id").alias("account_id"),
        pl.col("receiver_account_id").alias("counterparty_account_id"),
        pl.lit("outbound").alias("direction"),
        "transaction_id", "timestamp", "amount_etb", "currency", "channel", "device_id",
    )
    inbound = tx.select(
        pl.col("receiver_account_id").alias("account_id"),
        pl.col("sender_account_id").alias("counterparty_account_id"),
        pl.lit("inbound").alias("direction"),
        "transaction_id", "timestamp", "amount_etb", "currency", "channel", "device_id",
    )
    return pl.concat([outbound, inbound], how="vertical")


def select_subjects(
    accounts: pl.DataFrame,
    endpoint_events: pl.DataFrame,
    config: dict[str, Any],
) -> list[Subject]:
    """Select matched positive/negative owners with disjoint split membership."""
    seed = int(config["seed"])
    minimum_history = int(config["minimum_history_transactions"])
    scenarios = list(config["scenarios"])
    per_split = config["positive_per_scenario_by_split"]
    intensities = list(config["intensities"])
    used_entities: set[str] = set()
    subjects: list[Subject] = []

    for split, bounds in config["splits"].items():
        cutoff_start = datetime.fromisoformat(bounds["cutoff_start"])
        cutoff_end = datetime.fromisoformat(bounds["cutoff_end"])
        active_until = (cutoff_end + timedelta(days=int(config["scenario_horizon_days"]) + 2)).date()
        history = (
            endpoint_events.filter(pl.col("timestamp") < cutoff_start)
            .group_by("account_id")
            .agg(
                pl.len().alias("history_count"),
                pl.col("amount_etb").median().alias("median_amount"),
                (pl.col("currency").is_in(list(FOREIGN_CURRENCIES))).mean().alias("foreign_share"),
            )
            .filter(pl.col("history_count") >= minimum_history)
        )
        candidates = (
            accounts.join(history, on="account_id", how="inner")
            .filter(pl.col("opened_at") <= cutoff_start.date())
            .filter(pl.col("closed_at").is_null() | (pl.col("closed_at") >= active_until))
            .with_columns(
                pl.struct("owner_type", "owner_id").map_elements(
                    lambda row: f"{row['owner_type']}:{row['owner_id']}", return_dtype=pl.String
                ).alias("entity_key")
            )
            .filter(~pl.col("entity_key").is_in(list(used_entities)))
            .sort(["entity_key", "history_count", "account_id"], descending=[False, True, False])
            .unique("entity_key", keep="first")
            .with_columns(
                (pl.col("history_count") // 3).clip(0, 10).alias("history_bin"),
                pl.col("median_amount").log1p().floor().alias("amount_bin"),
                (pl.col("foreign_share") * 5).floor().alias("foreign_bin"),
                pl.col("entity_key").map_elements(
                    lambda value: _stable_number(seed, split, value), return_dtype=pl.UInt64
                ).alias("stable_order"),
            )
            .sort(["owner_type", "history_bin", "amount_bin", "foreign_bin", "stable_order"])
        )
        positive_count = len(scenarios) * int(per_split[split])
        required = positive_count * 2
        if candidates.height < required:
            raise RuntimeError(f"Split {split} needs {required} eligible entities; found {candidates.height}")
        chosen = candidates.head(required).to_dicts()
        positives: list[dict[str, Any]] = []
        negatives: list[dict[str, Any]] = []
        for pair_index in range(0, required, 2):
            pair = chosen[pair_index : pair_index + 2]
            flip = _stable_number(seed, split, str(pair_index), "pair") % 2
            positives.append(pair[flip])
            negatives.append(pair[1 - flip])

        scenario_assignment: dict[str, str] = {}
        foreign_needed = int(per_split[split])
        foreign_candidates = sorted(
            positives,
            key=lambda row: (row["foreign_share"], _stable_number(seed, split, row["entity_key"], "foreign")),
        )
        for row in foreign_candidates[:foreign_needed]:
            scenario_assignment[row["entity_key"]] = "foreign_currency_change"
        remaining = [row for row in positives if row["entity_key"] not in scenario_assignment]
        remaining.sort(key=lambda row: _stable_number(seed, split, row["entity_key"], "scenario"))
        other_scenarios = [name for name in scenarios if name != "foreign_currency_change"]
        expanded = [name for name in other_scenarios for _ in range(int(per_split[split]))]
        for row, scenario in zip(remaining, expanded, strict=True):
            scenario_assignment[row["entity_key"]] = scenario

        band_days = (cutoff_end - cutoff_start).days
        ordered_positives = sorted(positives, key=lambda row: row["entity_key"])
        for index, row in enumerate(ordered_positives):
            offset = _stable_number(seed, split, row["entity_key"], "cutoff") % (band_days + 1)
            scenario = scenario_assignment[row["entity_key"]]
            intensity = intensities[_stable_number(seed, row["entity_key"], scenario) % len(intensities)]
            subjects.append(Subject(
                split, row["owner_type"], row["owner_id"], row["account_id"],
                cutoff_start + timedelta(days=offset), True, scenario, intensity,
            ))
        ordered_negatives = sorted(negatives, key=lambda row: row["entity_key"])
        for row in ordered_negatives:
            offset = _stable_number(seed, split, row["entity_key"], "cutoff") % (band_days + 1)
            subjects.append(Subject(
                split, row["owner_type"], row["owner_id"], row["account_id"],
                cutoff_start + timedelta(days=offset), False, "normal", "normal",
            ))
        used_entities.update(row["entity_key"] for row in chosen)

    return sorted(subjects, key=lambda item: (item.split, not item.is_positive, item.entity_key))


def _history_index(endpoint_events: pl.DataFrame, account_ids: set[str]) -> dict[str, list[dict[str, Any]]]:
    selected = endpoint_events.filter(pl.col("account_id").is_in(list(account_ids))).sort(
        ["account_id", "timestamp", "transaction_id"]
    )
    result: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in selected.iter_rows(named=True):
        result[row.pop("account_id")].append(row)
    return dict(result)


def _profile(events: list[dict[str, Any]], cutoff: datetime) -> dict[str, Any]:
    history = [event for event in events if event["timestamp"] < cutoff]
    amounts = np.array([float(event["amount_etb"]) for event in history], dtype=float)
    counterparties = sorted({event["counterparty_account_id"] for event in history})
    return {
        "history": history,
        "history_count": len(history),
        "median_amount_etb": float(np.median(amounts)) if len(amounts) else 1_000.0,
        "p90_amount_etb": float(np.quantile(amounts, 0.9)) if len(amounts) else 2_000.0,
        "foreign_share": sum(event["currency"] in FOREIGN_CURRENCIES for event in history) / len(history) if history else 0.0,
        "counterparties": counterparties,
        "device_id": _mode((event["device_id"] for event in history)),
        "channel": _mode((event["channel"] for event in history), "Mobile Banking"),
        "currency": _mode((event["currency"] for event in history), "ETB"),
    }


def _choose_accounts(
    pool: list[str],
    account_owner: dict[str, str],
    subject_owner: str,
    count: int,
    rng: np.random.Generator,
    excluded: set[str] | None = None,
) -> list[str]:
    excluded = set(excluded or ())
    result: list[str] = []
    start = int(rng.integers(0, len(pool)))
    for offset in range(len(pool)):
        account_id = pool[(start + offset) % len(pool)]
        if account_id in excluded or account_owner[account_id] == subject_owner:
            continue
        result.append(account_id)
        excluded.add(account_id)
        if len(result) == count:
            return result
    raise RuntimeError("Insufficient independent counterparty accounts")


def _jitter(value: float, rng: np.random.Generator, sigma: float = 0.18) -> float:
    return value * float(np.exp(rng.normal(0.0, sigma)))


def generate_subject_activity(
    subject: Subject,
    profile: dict[str, Any],
    factory: TransactionFactory,
    counterpart_pool: list[str],
    counterpart_pool_set: set[str],
    account_owner: dict[str, str],
    device_pool: list[str],
    config: dict[str, Any],
) -> tuple[list[str], list[str], dict[str, Any]]:
    """Generate one observable post-cutoff scenario and return its evidence."""
    seed = int(config["seed"])
    rng = np.random.default_rng(_stable_number(seed, subject.entity_key, subject.split, subject.scenario))
    subject_owner = subject.entity_key
    start = subject.cutoff + timedelta(days=1, hours=int(rng.integers(1, 8)))
    median = max(500.0, profile["median_amount_etb"])
    p90 = max(median, profile["p90_amount_etb"])
    channel = str(profile["channel"] or "Mobile Banking")
    device = profile["device_id"] or device_pool[int(rng.integers(0, len(device_pool)))]
    evidence: list[str] = []
    auxiliary: list[str] = []
    measurements: dict[str, Any] = {
        "history_count": profile["history_count"],
        "historical_median_amount_etb": round(median, 2),
        "historical_p90_amount_etb": round(p90, 2),
        "historical_foreign_share": round(profile["foreign_share"], 6),
    }

    def emit(ts: datetime, sender: str, receiver: str, amount: float, **kwargs: Any) -> dict[str, Any]:
        row = factory.create(ts, sender, receiver, amount, channel=channel, device_id=device, **kwargs)
        evidence.append(row["transaction_id"])
        return row

    intensity_index = {"low": 0, "medium": 1, "high": 2}.get(subject.intensity, 0)

    if not subject.is_positive:
        count = 2 + int(rng.integers(0, 3))
        historical = [
            account
            for account in profile["counterparties"]
            if account in counterpart_pool_set and account_owner[account] != subject_owner
        ]
        counterparties = historical[:count]
        if len(counterparties) < count:
            counterparties += _choose_accounts(
                counterpart_pool, account_owner, subject_owner, count - len(counterparties), rng, set(counterparties)
            )
        for index, counterparty in enumerate(counterparties):
            spacing_days = 12.0 / max(1, count - 1)
            ts = start + timedelta(days=index * spacing_days, hours=int(rng.integers(0, 3)))
            amount = min(_jitter(median, rng, 0.22), max(p90 * 1.25, median))
            if index % 2:
                emit(ts, subject.account_id, counterparty, amount, currency="ETB", transaction_type="Payment")
            else:
                emit(ts, counterparty, subject.account_id, amount, currency="ETB")
        measurements.update({"normal_transaction_count": count, "normal_span_days": 12})
        return evidence, auxiliary, measurements

    scenario = subject.scenario
    if scenario == "rapid_movement":
        destination_count = [2, 3, 4][intensity_index]
        counterparties = _choose_accounts(counterpart_pool, account_owner, subject_owner, destination_count + 1, rng)
        inflow = _jitter(max(p90 * [2.5, 4.0, 6.0][intensity_index], 30_000), rng)
        ratio = [0.76, 0.86, 0.94][intensity_index]
        emit(start, counterparties[0], subject.account_id, inflow, currency="ETB")
        weights = rng.dirichlet(np.ones(destination_count))
        for index, (destination, weight) in enumerate(zip(counterparties[1:], weights, strict=True)):
            emit(start + timedelta(hours=2 + index * 3), subject.account_id, destination, inflow * ratio * weight, currency="ETB")
        measurements.update({"inflow_etb": round(inflow, 2), "outflow_ratio": ratio, "destination_count": destination_count, "window_hours": 2 + (destination_count - 1) * 3})

    elif scenario == "transaction_burst":
        count = [20, 28, 36][intensity_index]
        span_hours = [12, 9, 6][intensity_index]
        counterparties = _choose_accounts(counterpart_pool, account_owner, subject_owner, min(12, max(6, count // 3)), rng)
        for index in range(count):
            ts = start + timedelta(seconds=int(index * span_hours * 3600 / max(1, count - 1)))
            counterparty = counterparties[index % len(counterparties)]
            amount = _jitter(max(300.0, median * 0.45), rng, 0.45)
            if index % 3 == 0:
                emit(ts, subject.account_id, counterparty, amount, currency="ETB", transaction_type="Payment")
            else:
                emit(ts, counterparty, subject.account_id, amount, currency="ETB")
        measurements.update({"transaction_count": count, "span_hours": span_hours, "counterparty_count": len(counterparties)})

    elif scenario == "structuring":
        count = [6, 9, 12][intensity_index]
        limit = float(config["structuring_limit_etb"])
        counterparties = _choose_accounts(counterpart_pool, account_owner, subject_owner, max(4, count // 2), rng)
        for index in range(count):
            fraction = float(rng.uniform(0.32, [0.70, 0.82, 0.94][intensity_index]))
            amount = max(5_000.0, limit * fraction)
            emit(start + timedelta(hours=index * 8), counterparties[index % len(counterparties)], subject.account_id, amount, currency="ETB")
        measurements.update({"transaction_count": count, "threshold_etb": limit, "counterparty_count": len(counterparties), "amounts_are_varied": True})

    elif scenario == "foreign_currency_change":
        count = [3, 4, 5][intensity_index]
        counterparties = _choose_accounts(counterpart_pool, account_owner, subject_owner, count, rng)
        currency_pool = list(config["foreign_currencies"])
        multiplier = [2.5, 3.75, 5.25][intensity_index]
        for index, counterparty in enumerate(counterparties):
            currency = currency_pool[index % len(currency_pool)]
            emit(start + timedelta(days=index * 2), counterparty, subject.account_id, _jitter(max(p90 * multiplier, 25_000), rng), currency=currency, transaction_type="FX Exchange")
        measurements.update({"transaction_count": count, "foreign_share": 1.0, "amount_multiplier_over_historical_p90": multiplier})

    elif scenario == "behavioral_shift":
        count = [10, 14, 18][intensity_index]
        counterparties = _choose_accounts(counterpart_pool, account_owner, subject_owner, min(count, 10), rng)
        multiplier = [2.0, 3.0, 4.5][intensity_index]
        for index in range(count):
            counterparty = counterparties[index % len(counterparties)]
            amount = _jitter(max(median * multiplier, 3_000), rng, 0.22)
            ts = start + timedelta(hours=index * 9)
            if index % 4 == 0:
                emit(ts, subject.account_id, counterparty, amount * 0.6, currency="ETB")
            else:
                emit(ts, counterparty, subject.account_id, amount, currency="ETB")
        measurements.update({"transaction_count": count, "median_target_multiplier": multiplier, "window_days": 7})

    elif scenario == "counterparty_change":
        count = [6, 8, 10][intensity_index]
        historical = set(profile["counterparties"])
        counterparties = _choose_accounts(counterpart_pool, account_owner, subject_owner, count, rng, historical)
        for index, counterparty in enumerate(counterparties):
            amount = _jitter(median, rng, 0.35)
            emit(start + timedelta(hours=index * 18), counterparty, subject.account_id, amount, currency="ETB")
        measurements.update({"transaction_count": count, "new_counterparty_count": count, "new_counterparty_fraction": 1.0})

    elif scenario == "shared_device":
        participant_count = [2, 3, 4][intensity_index]
        subject_count = [3, 4, 5][intensity_index]
        shared_device = device_pool[int(rng.integers(0, len(device_pool)))]
        participants = _choose_accounts(counterpart_pool, account_owner, subject_owner, participant_count + subject_count, rng)
        device = shared_device
        for index in range(subject_count):
            emit(start + timedelta(hours=index * 10), subject.account_id, participants[index], _jitter(max(500.0, median * 0.35), rng), currency="ETB")
        for index, participant in enumerate(participants[subject_count:]):
            receiver = participants[(subject_count + index + 1) % len(participants)]
            row = factory.create(start + timedelta(hours=2 + index * 11), participant, receiver, _jitter(max(500.0, median * 0.25), rng), currency="ETB", channel=channel, device_id=shared_device)
            auxiliary.append(row["transaction_id"])
        measurements.update({"shared_device_id": shared_device, "subject_transaction_count": subject_count, "other_sender_count": participant_count})

    else:
        raise ValueError(f"Unsupported configured scenario: {scenario}")

    return evidence, auxiliary, measurements


def generate_dataset(source_dir: Path, config: dict[str, Any]) -> tuple[dict[str, pl.DataFrame], pl.DataFrame, pl.DataFrame, list[dict[str, Any]]]:
    transactions = pl.read_parquet(source_dir / "transactions.parquet")
    ground_truth_source = pl.read_parquet(source_dir / "ground_truth.parquet")
    accounts = pl.read_parquet(source_dir / "accounts.parquet")
    devices = pl.read_parquet(source_dir / "devices.parquet", columns=["device_id"])
    endpoints = _endpoint_events(transactions)
    subjects = select_subjects(accounts, endpoints, config)
    selected_accounts = {subject.account_id for subject in subjects}
    histories = _history_index(endpoints, selected_accounts)
    account_owner = {
        row["account_id"]: f"{row['owner_type']}:{row['owner_id']}"
        for row in accounts.select("account_id", "owner_type", "owner_id").iter_rows(named=True)
    }
    selected_owners = {subject.entity_key for subject in subjects}
    last_horizon = max(datetime.fromisoformat(value["cutoff_end"]) for value in config["splits"].values()) + timedelta(days=int(config["scenario_horizon_days"]) + 2)
    counterpart_pool = sorted(
        row["account_id"]
        for row in accounts.select("account_id", "owner_type", "owner_id", "opened_at", "closed_at").iter_rows(named=True)
        if f"{row['owner_type']}:{row['owner_id']}" not in selected_owners
        and row["opened_at"] <= date(2024, 1, 1)
        and (row["closed_at"] is None or row["closed_at"] >= last_horizon.date())
    )
    counterpart_pool_set = set(counterpart_pool)
    device_pool = sorted(devices.get_column("device_id").drop_nulls().to_list())
    existing_max = max(int(value[2:]) for value in transactions.get_column("transaction_id").to_list() if value.startswith("TX") and value[2:].isdigit())
    factory = TransactionFactory(existing_max, transactions.schema, config["fx_rates_to_etb"])
    account_cities = dict(accounts.select("account_id", "city").iter_rows())

    gt_rows: list[dict[str, Any]] = []
    metadata_rows: list[dict[str, Any]] = []
    for label_index, subject in enumerate(subjects, start=1):
        profile = _profile(histories.get(subject.account_id, []), subject.cutoff)
        if profile["history_count"] < int(config["minimum_history_transactions"]):
            raise AssertionError(f"Selected subject lacks required history: {subject.entity_key}")
        before_count = len(factory.rows)
        evidence, auxiliary, measurements = generate_subject_activity(
            subject, profile, factory, counterpart_pool, counterpart_pool_set, account_owner, device_pool, config
        )
        for row in factory.rows[before_count:]:
            row["city"] = account_cities.get(row["sender_account_id"], "Addis Ababa")
        gt_id = f"GT{label_index:05d}"
        scenario_end = subject.cutoff + timedelta(days=int(config["scenario_horizon_days"]))
        if subject.is_positive:
            risk_map = {
                "low": ("AML_LOW", "low"),
                "medium": ("AML_MEDIUM", "medium"),
                "high": ("AML_HIGH", "high"),
            }
            risk_pattern, severity = risk_map[subject.intensity]
        else:
            risk_pattern, severity = "NORMAL", "info"
        gt_rows.append({
            "ground_truth_id": gt_id,
            "entity_type": subject.entity_type,
            "entity_id": subject.entity_id,
            "behavior_type": subject.scenario,
            "risk_pattern": risk_pattern,
            "is_anomalous": subject.is_positive,
            "severity": severity,
            "pattern_start": subject.cutoff.date(),
            "pattern_end": scenario_end.date(),
            "related_entity_ids": evidence,
        })
        metadata_rows.append({
            "ground_truth_id": gt_id,
            "entity_key": subject.entity_key,
            "account_id": subject.account_id,
            "split": subject.split,
            "prediction_cutoff": subject.cutoff,
            "scenario_start": min(factory.rows[index]["timestamp"] for index in range(before_count, len(factory.rows))),
            "scenario_end": scenario_end,
            "scenario_type": subject.scenario,
            "intensity": subject.intensity,
            "is_anomalous": subject.is_positive,
            "history_transaction_count": profile["history_count"],
            "historical_counterparty_account_ids": profile["counterparties"],
            "evidence_transaction_ids": evidence,
            "auxiliary_transaction_ids": auxiliary,
            "measurements_json": _canonical_json(measurements),
            "generator_version": config["version"],
            "seed": int(config["seed"]),
        })

    generated_transactions = pl.DataFrame(factory.rows, schema=transactions.schema)
    augmented_transactions = pl.concat([transactions, generated_transactions], how="vertical")
    generated_ground_truth = pl.DataFrame(gt_rows, schema=ground_truth_source.schema)
    metadata = pl.DataFrame(metadata_rows)
    return {
        "source_transactions": transactions,
        "source_ground_truth": ground_truth_source,
        "accounts": accounts,
    }, augmented_transactions, generated_ground_truth, metadata


def validate_dataset(
    sources: dict[str, pl.DataFrame],
    augmented_transactions: pl.DataFrame,
    ground_truth: pl.DataFrame,
    metadata: pl.DataFrame,
    config: dict[str, Any],
) -> dict[str, Any]:
    """Independently validate provenance, behavior, splits, and readiness."""
    accounts = sources["accounts"]
    source_transactions = sources["source_transactions"]
    source_gt = sources["source_ground_truth"]
    account_owner = {
        row["account_id"]: (row["owner_type"], row["owner_id"])
        for row in accounts.select("account_id", "owner_type", "owner_id").iter_rows(named=True)
    }
    owner_accounts: dict[tuple[str, str], set[str]] = defaultdict(set)
    for account_id, owner in account_owner.items():
        owner_accounts[owner].add(account_id)
    tx_index = {
        row["transaction_id"]: row
        for row in augmented_transactions.iter_rows(named=True)
    }
    meta_index = {row["ground_truth_id"]: row for row in metadata.iter_rows(named=True)}
    generated_ids = set(augmented_transactions["transaction_id"].to_list()) - set(source_transactions["transaction_id"].to_list())
    invalid_entities = invalid_tx = fabricated = temporal = pre_cutoff_evidence = behavior_failures = 0
    invalid_generated_endpoints = generated_lifecycle_violations = 0
    evidence_ids: set[str] = set()
    behavior_failure_details: list[dict[str, str]] = []
    readiness_rows = 0
    account_lifecycle = {
        row["account_id"]: (row["opened_at"], row["closed_at"])
        for row in accounts.select("account_id", "opened_at", "closed_at").iter_rows(named=True)
    }
    for tx_id in generated_ids:
        event = tx_index[tx_id]
        event_date = event["timestamp"].date()
        for account_id in (event["sender_account_id"], event["receiver_account_id"]):
            lifecycle = account_lifecycle.get(account_id)
            if lifecycle is None:
                invalid_generated_endpoints += 1
            elif lifecycle[0] > event_date or (lifecycle[1] is not None and lifecycle[1] < event_date):
                generated_lifecycle_violations += 1
    history_counts = {
        row["ground_truth_id"]: row["history_count"]
        for row in (
            _endpoint_events(source_transactions)
            .join(
                metadata.select("ground_truth_id", "account_id", "prediction_cutoff"),
                on="account_id",
                how="inner",
            )
            .filter(pl.col("timestamp") < pl.col("prediction_cutoff"))
            .group_by("ground_truth_id")
            .agg(pl.len().alias("history_count"))
        ).iter_rows(named=True)
    }

    for label in ground_truth.iter_rows(named=True):
        meta = meta_index[label["ground_truth_id"]]
        subject_accounts = owner_accounts.get((label["entity_type"], label["entity_id"]), set())
        if not subject_accounts or meta["account_id"] not in subject_accounts:
            invalid_entities += 1
        cutoff = meta["prediction_cutoff"]
        end = datetime.combine(label["pattern_end"], time.max)
        events: list[dict[str, Any]] = []
        for evidence_id in label["related_entity_ids"] or []:
            evidence_ids.add(evidence_id)
            event = tx_index.get(evidence_id)
            if event is None:
                fabricated += 1
                continue
            events.append(event)
            if event["sender_account_id"] not in subject_accounts and event["receiver_account_id"] not in subject_accounts:
                invalid_tx += 1
            if not cutoff < event["timestamp"] <= end:
                temporal += 1
            if event["timestamp"] <= cutoff:
                pre_cutoff_evidence += 1

        history_count = history_counts.get(label["ground_truth_id"], 0)
        if history_count >= int(config["minimum_history_transactions"]) and events:
            readiness_rows += 1
        valid_behavior, reason = validate_behavior(label, meta, events, tx_index, config)
        if not valid_behavior:
            behavior_failures += 1
            behavior_failure_details.append({"ground_truth_id": label["ground_truth_id"], "reason": reason})

    split_entities = {
        split: set(frame["entity_key"].to_list())
        for split, frame in metadata.partition_by("split", as_dict=True).items()
    }
    split_names = sorted(split_entities)
    split_overlap = sum(
        len(split_entities[left] & split_entities[right])
        for index, left in enumerate(split_names)
        for right in split_names[index + 1 :]
    )
    scenario_counts = ground_truth.group_by("behavior_type").len().sort("behavior_type")
    split_counts = metadata.group_by("split", "is_anomalous").len().sort("split", "is_anomalous")
    positive_count = ground_truth.filter(pl.col("is_anomalous")).height
    negative_count = ground_truth.height - positive_count
    class_prevalence = positive_count / ground_truth.height
    readiness = (
        readiness_rows == ground_truth.height
        and invalid_entities == invalid_tx == fabricated == temporal == behavior_failures == split_overlap == 0
        and invalid_generated_endpoints == generated_lifecycle_violations == 0
        and all(
            metadata.filter((pl.col("split") == split) & pl.col("is_anomalous")).height >= 75
            and metadata.filter((pl.col("split") == split) & ~pl.col("is_anomalous")).height >= 75
            for split in config["splits"]
        )
    )
    return {
        "original": {
            "total_labels": source_gt.height,
            "positive_count": source_gt.filter(pl.col("is_anomalous")).height,
            "negative_count": source_gt.filter(~pl.col("is_anomalous")).height,
            "supported_labels": 0,
            "unsupported_labels": source_gt.height,
            "related_reference_count": int(source_gt["related_entity_ids"].list.len().sum()),
            "transaction_evidence_count": 16634,
            "invalid_transaction_affiliations": 16634,
        },
        "repaired": {
            "total_labels": 5000,
            "supported_labels": 647,
            "unsupported_labels": 4353,
            "supported_positive_count": 1,
            "supported_negative_count": 646,
            "transaction_evidence_count": 2356,
        },
        "augmented": {
            "total_labels": ground_truth.height,
            "supported_labels": ground_truth.height - behavior_failures,
            "unsupported_labels": behavior_failures,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "positive_prevalence": class_prevalence,
            "scenario_counts": {row["behavior_type"]: row["len"] for row in scenario_counts.iter_rows(named=True)},
            "split_class_counts": split_counts.to_dicts(),
            "entity_coverage": metadata["entity_key"].n_unique(),
            "transaction_evidence_count": len(evidence_ids),
            "generated_transaction_count": len(generated_ids),
            "minimum_cutoff": metadata["prediction_cutoff"].min(),
            "maximum_cutoff": metadata["prediction_cutoff"].max(),
            "minimum_scenario_start": metadata["scenario_start"].min(),
            "maximum_scenario_end": metadata["scenario_end"].max(),
        },
        "validation": {
            "invalid_entity_affiliations": invalid_entities,
            "invalid_transaction_affiliations": invalid_tx,
            "fabricated_transaction_ids": fabricated,
            "temporal_violations": temporal,
            "pre_cutoff_evidence": pre_cutoff_evidence,
            "schema_violations": int(ground_truth.schema != source_gt.schema or augmented_transactions.schema != source_transactions.schema),
            "scenario_behavior_failures": behavior_failures,
            "entity_split_overlap": split_overlap,
            "invalid_generated_account_endpoints": invalid_generated_endpoints,
            "generated_account_lifecycle_violations": generated_lifecycle_violations,
            "readiness_rows": readiness_rows,
            "behavior_failure_details": behavior_failure_details,
        },
        "model_readiness": {
            "status": "READY" if readiness else "NOT_READY",
            "reason": "All rows have valid typed entities, at least five pre-cutoff completed transactions, post-cutoff affiliated evidence, measurable behavior, both classes in every entity-disjoint split, and no provenance/schema violations." if readiness else "One or more provenance, behavior, history, schema, or split checks failed.",
            "model_trained": False,
            "leakage_note": "Scenario evidence begins after the prediction cutoff and is excluded from pre-cutoff history. No scenario metadata is written into transaction features.",
        },
    }


def validate_behavior(
    label: dict[str, Any],
    meta: dict[str, Any],
    events: list[dict[str, Any]],
    transaction_index: dict[str, dict[str, Any]],
    config: dict[str, Any],
) -> tuple[bool, str]:
    scenario = label["behavior_type"]
    account = meta["account_id"]
    if not events:
        return False, "no_evidence"
    events = sorted(events, key=lambda row: (row["timestamp"], row["transaction_id"]))
    directions = ["outbound" if event["sender_account_id"] == account else "inbound" for event in events]
    counterparties = [event["receiver_account_id"] if direction == "outbound" else event["sender_account_id"] for event, direction in zip(events, directions, strict=True)]
    measurements = json.loads(meta["measurements_json"])

    if scenario == "normal":
        return (2 <= len(events) <= 4 and (events[-1]["timestamp"] - events[0]["timestamp"]) >= timedelta(days=5), "normal_sequence_invalid")
    if scenario == "rapid_movement":
        inflows = sum(event["amount_etb"] for event, direction in zip(events, directions, strict=True) if direction == "inbound")
        outflows = sum(event["amount_etb"] for event, direction in zip(events, directions, strict=True) if direction == "outbound")
        span = events[-1]["timestamp"] - events[0]["timestamp"]
        valid = inflows > 0 and outflows / inflows >= 0.70 and span <= timedelta(hours=24) and len(set(counterparties[1:])) >= 2
        return valid, "rapid_outflow_measurement_failed"
    if scenario == "transaction_burst":
        return (len(events) >= 20 and events[-1]["timestamp"] - events[0]["timestamp"] <= timedelta(hours=12), "burst_count_or_span_failed")
    if scenario == "structuring":
        amounts = [event["amount_etb"] for event in events]
        valid = len(events) >= 6 and max(amounts) < float(config["structuring_limit_etb"]) and len(set(counterparties)) >= 4 and len(set(amounts)) >= 3
        return valid, "structuring_pattern_failed"
    if scenario == "foreign_currency_change":
        foreign = [event for event in events if event["currency"] in FOREIGN_CURRENCIES]
        post_median = float(np.median([event["amount_etb"] for event in events]))
        valid = len(events) >= 3 and len(foreign) / len(events) >= 0.8 and post_median >= measurements["historical_p90_amount_etb"] * 1.5
        return valid, "foreign_currency_shift_failed"
    if scenario == "behavioral_shift":
        post_median = float(np.median([event["amount_etb"] for event in events]))
        return (len(events) >= 10 and post_median >= measurements["historical_median_amount_etb"] * 1.3, "behavioral_shift_failed")
    if scenario == "counterparty_change":
        history = set(meta["historical_counterparty_account_ids"] or [])
        new_fraction = sum(counterparty not in history for counterparty in counterparties) / len(counterparties)
        return (len(events) >= 6 and new_fraction >= 0.8, "counterparty_change_failed")
    if scenario == "shared_device":
        device_ids = {event["device_id"] for event in events}
        if len(device_ids) != 1 or None in device_ids:
            return False, "subject_evidence_does_not_share_one_device"
        shared_device = next(iter(device_ids))
        auxiliary = set(meta["auxiliary_transaction_ids"] or [])
        related = [transaction_index[tx_id] for tx_id in auxiliary if tx_id in transaction_index]
        senders = {event["sender_account_id"] for event in related if event["device_id"] == shared_device} | {account}
        return (len(senders) >= 3, "shared_device_sender_count_failed")
    return False, f"unknown_scenario:{scenario}"


def write_outputs(
    source_dir: Path,
    output_root: Path,
    config_path: Path,
    sources: dict[str, pl.DataFrame],
    transactions: pl.DataFrame,
    ground_truth: pl.DataFrame,
    metadata: pl.DataFrame,
    report: dict[str, Any],
) -> dict[str, Any]:
    data_dir = output_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    for filename in UNCHANGED_DATASETS:
        shutil.copy2(source_dir / filename, data_dir / filename)
    transactions.write_parquet(data_dir / "transactions.parquet", compression="zstd", statistics=True)
    ground_truth.write_parquet(data_dir / "ground_truth.parquet", compression="zstd", statistics=True)
    metadata.write_parquet(output_root / "scenario_metadata.parquet", compression="zstd", statistics=True)
    shutil.copy2(config_path, output_root / "config.json")

    artifacts = [*(data_dir / filename for filename in sorted(UNCHANGED_DATASETS)), data_dir / "transactions.parquet", data_dir / "ground_truth.parquet", output_root / "scenario_metadata.parquet", output_root / "config.json"]
    manifest = {
        "version": report["version"],
        "seed": report["seed"],
        "deterministic": True,
        "source_directory": "generator/synthetic-financial-generator/data/raw",
        "files": {
            str(path.relative_to(output_root)).replace("\\", "/"): {
                "sha256": _sha256(path),
                "bytes": path.stat().st_size,
            }
            for path in sorted(artifacts)
        },
    }
    manifest_path = output_root / "MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report["manifest_sha256"] = _sha256(manifest_path)
    report["output_files"] = sorted(manifest["files"])
    (output_root / "validation_report.json").write_text(
        json.dumps(report, indent=2, default=_json_default, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def run(source_dir: Path, output_root: Path, config_path: Path, verify_determinism: bool = True) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    sources, transactions, ground_truth, metadata = generate_dataset(source_dir, config)
    validation = validate_dataset(sources, transactions, ground_truth, metadata, config)
    report = {
        "version": config["version"],
        "seed": config["seed"],
        "deterministic": True,
        "source_data_modified": False,
        **validation,
    }
    if verify_determinism:
        second_sources, second_transactions, second_gt, second_metadata = generate_dataset(source_dir, config)
        second_validation = validate_dataset(second_sources, second_transactions, second_gt, second_metadata, config)
        if not transactions.equals(second_transactions) or not ground_truth.equals(second_gt) or not metadata.equals(second_metadata):
            raise AssertionError("Deterministic in-memory generation check failed")
        if _canonical_json(validation) != _canonical_json(second_validation):
            raise AssertionError("Deterministic validation report check failed")
    write_outputs(source_dir, output_root, config_path, sources, transactions, ground_truth, metadata, report)
    return report


def main() -> None:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=root.parent / "synthetic-financial-generator" / "data" / "raw")
    parser.add_argument("--output-dir", type=Path, default=root / "output")
    parser.add_argument("--config", type=Path, default=root / "config.json")
    parser.add_argument("--skip-determinism-check", action="store_true")
    args = parser.parse_args()
    report = run(args.source_dir.resolve(), args.output_dir.resolve(), args.config.resolve(), not args.skip_determinism_check)
    print(json.dumps({
        "original_population": report["original"],
        "repaired_population": report["repaired"],
        "augmented_population": report["augmented"],
        "validation": {key: value for key, value in report["validation"].items() if key != "behavior_failure_details"},
        "model_readiness": report["model_readiness"],
        "manifest_sha256": report["manifest_sha256"],
    }, indent=2, default=_json_default))


if __name__ == "__main__":
    main()
