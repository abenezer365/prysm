"""Leakage-safe cleaning, normalization, and as-of feature engineering."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


MODEL_FEATURES = [
    "history_tx_count", "history_inflow_etb", "history_outflow_etb",
    "history_median_amount_etb", "history_mean_amount_etb", "history_std_amount_etb",
    "tx_count_1d", "tx_count_7d", "tx_count_30d", "inflow_etb_1d", "inflow_etb_7d",
    "inflow_etb_30d", "outflow_etb_1d", "outflow_etb_7d", "outflow_etb_30d",
    "foreign_inflow_etb_30d", "foreign_inflow_count_30d", "currency_diversity_30d",
    "counterparty_count_30d", "device_count_30d", "invoice_link_rate_30d",
    "failed_rate_30d", "outflow_ratio_7d", "recent_amount_z", "recent_to_history_count_ratio",
    "foreign_recent_to_history_ratio", "relationship_degree", "company_connection_count",
    "employer_relationship_count", "shared_device_relationship_count",
    "shared_address_relationship_count", "mean_relationship_confidence",
]


def normalize_transactions(transactions: pd.DataFrame, accounts: pd.DataFrame, invoices: pd.DataFrame) -> pd.DataFrame:
    """Add safe normalized values and quality flags without discarding source rows."""
    tx = transactions.copy()
    tx["timestamp"] = pd.to_datetime(tx["timestamp"], utc=True)
    account = accounts.set_index("account_id")
    invoice = invoices.set_index("invoice_id")
    tx["amount_etb_log1p"] = np.log1p(tx["amount_etb"].clip(lower=0))
    tx["is_foreign_currency"] = tx["currency"].ne("ETB")
    tx["has_device"] = tx["device_id"].notna()
    tx["has_invoice"] = tx["invoice_id"].notna()
    tx["sender_currency_mismatch"] = tx["currency"].ne(tx["sender_account_id"].map(account["currency"]))
    sender_open = tx["sender_account_id"].map(account["opened_at"])
    receiver_open = tx["receiver_account_id"].map(account["opened_at"])
    sender_close = tx["sender_account_id"].map(account["closed_at"])
    receiver_close = tx["receiver_account_id"].map(account["closed_at"])
    tx["sender_lifecycle_valid"] = tx["timestamp"].ge(sender_open) & (sender_close.isna() | tx["timestamp"].le(sender_close))
    tx["receiver_lifecycle_valid"] = tx["timestamp"].ge(receiver_open) & (receiver_close.isna() | tx["timestamp"].le(receiver_close))
    issue = tx["invoice_id"].map(invoice["issue_date"])
    tx["invoice_chronology_valid"] = ~tx["has_invoice"] | tx["timestamp"].ge(issue)
    return tx


class AsOfFeatureBuilder:
    """Build entity snapshots using only observations available at each cutoff."""

    def __init__(self, transactions: pd.DataFrame, accounts: pd.DataFrame, relationships: pd.DataFrame, relevant_entity_keys: set[str] | None = None):
        self.tx = transactions.sort_values("timestamp").reset_index(drop=True)
        self.accounts = accounts.copy()
        self.relationships = relationships.copy()
        owner_accounts = defaultdict(list)
        for row in accounts[["owner_key", "account_id"]].itertuples(index=False):
            owner_accounts[row.owner_key].append(row.account_id)
        self.owner_accounts = dict(owner_accounts)
        relevant = relevant_entity_keys
        relationship_rows = defaultdict(list)
        for index, source_key, target_key in relationships[["source_key", "target_key"]].itertuples():
            if relevant is None or source_key in relevant:
                relationship_rows[source_key].append(index)
            if relevant is None or target_key in relevant:
                relationship_rows[target_key].append(index)
        self.entity_relationship_rows = {key: np.asarray(indices, dtype=np.int64) for key, indices in relationship_rows.items()}
        self.account_events: dict[str, pd.DataFrame] = {}
        required_accounts = None
        if relevant is not None:
            required_accounts = set()
            for key in relevant:
                required_accounts.update(self._accounts_for(key))
        outgoing_source = self.tx if required_accounts is None else self.tx[self.tx["sender_account_id"].isin(required_accounts)]
        incoming_source = self.tx if required_accounts is None else self.tx[self.tx["receiver_account_id"].isin(required_accounts)]
        outgoing = outgoing_source.assign(direction="out", counterparty_id=outgoing_source["receiver_account_id"])
        incoming = incoming_source.assign(direction="in", counterparty_id=incoming_source["sender_account_id"])
        for account_id, group in pd.concat([outgoing, incoming], ignore_index=True).groupby(
            pd.concat([outgoing["sender_account_id"], incoming["receiver_account_id"]], ignore_index=True), sort=False
        ):
            self.account_events[str(account_id)] = group.sort_values("timestamp")

    def _accounts_for(self, entity_key: str) -> list[str]:
        entity_type, entity_id = entity_key.split(":", 1)
        if entity_type == "Account":
            return [entity_id]
        return self.owner_accounts.get(entity_key, [])

    def _events_before(self, entity_key: str, as_of: pd.Timestamp) -> pd.DataFrame:
        frames = []
        for account_id in self._accounts_for(entity_key):
            events = self.account_events.get(account_id)
            if events is not None:
                end = events["timestamp"].searchsorted(as_of, side="right")
                if end:
                    frames.append(events.iloc[:end])
        return pd.concat(frames, ignore_index=True) if frames else self.tx.iloc[:0].assign(direction=pd.Series(dtype="string"), counterparty_id=pd.Series(dtype="string"))

    def _relationship_features(self, entity_key: str, as_of: pd.Timestamp) -> dict[str, float]:
        indices = self.entity_relationship_rows.get(entity_key)
        if indices is None:
            return {"relationship_degree": 0.0, "company_connection_count": 0.0,
                    "employer_relationship_count": 0.0, "shared_device_relationship_count": 0.0,
                    "shared_address_relationship_count": 0.0, "mean_relationship_confidence": 0.0}
        r = self.relationships.loc[indices]
        active = r["start_time"].le(as_of) & (r["end_time"].isna() | r["end_time"].ge(as_of))
        linked = r[active & (r["source_key"].eq(entity_key) | r["target_key"].eq(entity_key))]
        other_type = np.where(linked["source_key"].eq(entity_key), linked["target_type"], linked["source_type"])
        return {
            "relationship_degree": float(len(linked)),
            "company_connection_count": float(np.sum(other_type == "Company")),
            "employer_relationship_count": float(linked["relationship_type"].eq("employer_employee").sum()),
            "shared_device_relationship_count": float(linked["relationship_type"].eq("shared_device").sum()),
            "shared_address_relationship_count": float(linked["relationship_type"].eq("shared_address").sum()),
            "mean_relationship_confidence": float(linked["confidence"].mean()) if len(linked) else 0.0,
        }

    def build_one(self, entity_key: str, as_of: pd.Timestamp) -> dict[str, float]:
        as_of = pd.Timestamp(as_of)
        events = self._events_before(entity_key, as_of)
        amounts = events["amount_etb"]
        result: dict[str, float] = {
            "history_tx_count": float(len(events)),
            "history_inflow_etb": float(events.loc[events.direction.eq("in"), "amount_etb"].sum()),
            "history_outflow_etb": float(events.loc[events.direction.eq("out"), "amount_etb"].sum()),
            "history_median_amount_etb": float(amounts.median()) if len(events) else 0.0,
            "history_mean_amount_etb": float(amounts.mean()) if len(events) else 0.0,
            "history_std_amount_etb": float(amounts.std(ddof=0)) if len(events) else 0.0,
        }
        windows: dict[int, pd.DataFrame] = {}
        for days in (1, 7, 30):
            recent = events[events["timestamp"].gt(as_of - pd.Timedelta(days=days))]
            windows[days] = recent
            result[f"tx_count_{days}d"] = float(len(recent))
            result[f"inflow_etb_{days}d"] = float(recent.loc[recent.direction.eq("in"), "amount_etb"].sum())
            result[f"outflow_etb_{days}d"] = float(recent.loc[recent.direction.eq("out"), "amount_etb"].sum())
        recent = windows[30]
        recent_in = recent[recent.direction.eq("in")]
        foreign_in = recent_in[recent_in["is_foreign_currency"]]
        result.update({
            "foreign_inflow_etb_30d": float(foreign_in["amount_etb"].sum()),
            "foreign_inflow_count_30d": float(len(foreign_in)),
            "currency_diversity_30d": float(recent["currency"].nunique()),
            "counterparty_count_30d": float(recent["counterparty_id"].nunique()),
            "device_count_30d": float(recent["device_id"].nunique()),
            "invoice_link_rate_30d": float(recent["has_invoice"].mean()) if len(recent) else 0.0,
            "failed_rate_30d": float(recent["status"].ne("Completed").mean()) if len(recent) else 0.0,
            "invoice_invalid_count_30d": float((~recent["invoice_chronology_valid"]).sum()),
            "transaction_ids_30d": recent["transaction_id"].astype(str).tolist(),
        })
        inflow7, outflow7 = result["inflow_etb_7d"], result["outflow_etb_7d"]
        result["outflow_ratio_7d"] = float(outflow7 / max(inflow7, 1.0))
        result["recent_amount_z"] = float((recent["amount_etb"].mean() - result["history_mean_amount_etb"]) / max(result["history_std_amount_etb"], 1.0)) if len(recent) else 0.0
        history_days = max((as_of - events["timestamp"].min()).total_seconds() / 86400, 30.0) if len(events) else 30.0
        expected_30d_count = result["history_tx_count"] * 30.0 / history_days
        result["recent_to_history_count_ratio"] = float(result["tx_count_30d"] / max(expected_30d_count, 1.0))
        history_foreign_inflow = events.loc[events.direction.eq("in") & events["is_foreign_currency"], "amount_etb"].sum()
        expected_foreign_30d = float(history_foreign_inflow * 30.0 / history_days)
        result["foreign_recent_to_history_ratio"] = float(result["foreign_inflow_etb_30d"] / max(expected_foreign_30d, 1.0))
        result.update(self._relationship_features(entity_key, as_of))
        return result

    def build_labels(self, labels: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for label in labels.itertuples(index=False):
            features = self.build_one(label.entity_key, label.pattern_start)
            rows.append({
                "ground_truth_id": label.ground_truth_id, "entity_key": label.entity_key,
                "as_of": label.pattern_start, "target": bool(label.is_anomalous),
                "scenario": label.behavior_type, **features,
            })
        return pd.DataFrame(rows)


def load_phase1(processed_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    accounts = pd.read_parquet(processed_dir / "accounts.parquet")
    transactions = pd.read_parquet(processed_dir / "transaction_edges.parquet")
    invoices = pd.read_parquet(processed_dir / "invoices.parquet")
    relationships = pd.read_parquet(processed_dir / "relationship_edges.parquet")
    for frame, columns in [(accounts, ["opened_at", "closed_at"]), (transactions, ["timestamp"]), (invoices, ["issue_date"]), (relationships, ["start_time", "end_time"])]:
        for column in columns:
            frame[column] = pd.to_datetime(frame[column], utc=True)
    return accounts, transactions, invoices, relationships
