"""Historical baseline excludes the observation window; IDs only locate evidence."""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
import pandas as pd


ANOMALY_FEATURES = ("amount_to_history", "burst_15m", "frequency_ratio", "new_counterparty_fraction",
                    "new_device_fraction", "max_branch_speed_kmh", "outflow_to_income")


def distance_km(a, b):
    lat1, lat2 = math.radians(a["latitude"]), math.radians(b["latitude"])
    dlat = lat2-lat1
    dlon = math.radians(b["longitude"]-a["longitude"])
    h = math.sin(dlat/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 6371*2*math.asin(math.sqrt(min(1., max(0., h))))


def densest(events, minutes):
    """Linear sliding window after sort, including both boundary timestamps."""
    records = events.sort_values(["timestamp", "transaction_id"]).to_dict("records")
    left, best = 0, []
    for right, row in enumerate(records):
        while (row["timestamp"]-records[left]["timestamp"]).total_seconds() > minutes*60:
            left += 1
        if right-left+1 > len(best):
            best = records[left:right+1]
    return best


@dataclass
class Features:
    values: dict
    support: dict
    recent: pd.DataFrame
    history: pd.DataFrame
    own_accounts: set
    income: float | None
    travel_pairs: list


def build_features(snapshot, entity=None):
    key = entity or snapshot.subject
    aids = snapshot.owned_accounts(key)
    tx = snapshot.transactions
    own = tx[tx.sender_account_id.isin(aids) | tx.receiver_account_id.isin(aids)]
    history = own[own.timestamp.lt(snapshot.window_start)]
    recent = own[own.timestamp.ge(snapshot.window_start)]
    baseline = float(history.amount_etb.median()) if len(history) else None
    people = snapshot.persons[snapshot.persons.person_id.eq(key.split(":", 1)[1])] if key.startswith("Person:") else snapshot.persons.iloc[:0]
    income = None
    if len(people) and people.iloc[0].income_currency == "ETB":
        income = float(people.iloc[0].declared_monthly_income)
    outgoing = recent[recent.sender_account_id.isin(aids)]
    prior_devices = set(history.loc[history.sender_account_id.isin(aids), "device_id"].dropna())
    new_device = outgoing[outgoing.device_id.notna() & ~outgoing.device_id.isin(prior_devices)]
    counterparties = lambda frame: (set(frame.sender_account_id) | set(frame.receiver_account_id))-aids
    prior_counterparties = counterparties(history)-aids
    changed = recent[~recent.sender_account_id.isin(prior_counterparties | aids) | ~recent.receiver_account_id.isin(prior_counterparties | aids)]
    burst = densest(recent, 15)
    # Presence is attributable to the initiating account only, not its receiver.
    branch = outgoing[outgoing.channel.eq("Branch")].sort_values(["timestamp", "transaction_id"])
    travel = []
    for a, b in zip(branch.to_dict("records"), branch.to_dict("records")[1:]):
        km = distance_km(a, b)
        hours = max((b["timestamp"]-a["timestamp"]).total_seconds()/3600, 1/3600)
        travel.append({"distance_km": km, "speed_kmh": km/hours,
                       "transaction_ids": [a["transaction_id"], b["transaction_id"]]})
    worst = max(travel, key=lambda pair: pair["speed_kmh"], default={"speed_kmh": 0., "transaction_ids": []})
    amount_row = recent.sort_values(["amount_etb", "transaction_id"], ascending=[False, True]).head(1)
    observed_days = max((snapshot.window_start-history.timestamp.min()).total_seconds()/86400, 1) if len(history) else 1
    expected = len(history)/observed_days * (snapshot.cutoff-snapshot.window_start).total_seconds()/86400
    values = {
        "history_count": len(history), "recent_count": len(recent), "history_median_etb": baseline,
        "amount_to_history": float(recent.amount_etb.max()/max(baseline, 1)) if len(recent) and baseline is not None else 0.,
        "burst_15m": len(burst), "frequency_ratio": len(recent)/max(expected, 1),
        "new_counterparty_fraction": len(changed)/max(len(recent), 1),
        "new_device_fraction": len(new_device)/max(len(outgoing), 1),
        "max_branch_speed_kmh": worst["speed_kmh"],
        "outflow_to_income": float(outgoing.amount_etb.sum()/max(income, 1)) if income is not None else 0.,
    }
    support = {
        "amount_to_history": amount_row.transaction_id.tolist(),
        "burst_15m": [t["transaction_id"] for t in burst],
        "frequency_ratio": recent.transaction_id.tolist(),
        "new_counterparty_fraction": changed.transaction_id.tolist(),
        "new_device_fraction": new_device.transaction_id.tolist(),
        "max_branch_speed_kmh": worst["transaction_ids"],
        "outflow_to_income": outgoing.transaction_id.tolist(),
    }
    return Features(values, support, recent, history, aids, income, travel)


def vector(features):
    return np.log1p(np.asarray([features.values[name] for name in ANOMALY_FEATURES], dtype=float))
