"""Load validated Phase 1 facts and discover bounded, cutoff-safe neighborhoods.

Ground truth is deliberately absent from Dataset and Snapshot. Labels are read
only by the training/evaluation entry point, never by an investigation.
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


def utc(value):
    result = pd.Timestamp(value)
    if pd.isna(result) or result.tzinfo is None:
        raise ValueError("A finite timezone-aware cutoff is required")
    return result.tz_convert("UTC")


@dataclass
class Snapshot:
    subject: str
    cutoff: pd.Timestamp
    window_start: pd.Timestamp
    history_start: pd.Timestamp
    persons: pd.DataFrame
    companies: pd.DataFrame
    accounts: pd.DataFrame
    relationships: pd.DataFrame
    transactions: pd.DataFrame
    institutions: pd.DataFrame
    truncated: bool = False

    @property
    def owners(self):
        return dict(zip(self.accounts.account_id, self.accounts.owner_type+":"+self.accounts.owner_id))

    def owned_accounts(self, entity=None):
        key = entity or self.subject
        if key.startswith("Account:"):
            return {key.split(":", 1)[1]}
        return {a for a, owner in self.owners.items() if owner == key}


class Dataset:
    FACTS = ("persons", "companies", "accounts", "institutions", "transactions", "relationships")

    def __init__(self, tables, version="in-memory", checksum="in-memory"):
        self.version, self.checksum = version, checksum
        self.tables = {name: tables[name].copy(deep=True).reset_index(drop=True) for name in self.FACTS}
        self.entities = {}
        self.entity_positions = {}
        for name, kind, key, created in (("persons", "Person", "person_id", "created_at"),
                                        ("companies", "Company", "company_id", "registration_date"),
                                        ("accounts", "Account", "account_id", "opened_at")):
            frame = self.tables[name]
            if frame[key].isna().any() or frame[key].duplicated().any():
                raise ValueError(f"{name}: missing/duplicate identifier")
            for position, row in enumerate(frame.to_dict("records")):
                entity_key = f"{kind}:{row[key]}"
                self.entities[entity_key] = (utc(row[created]), row)
                self.entity_positions[entity_key] = (name, position)
        self.links = defaultdict(list)
        self.account_rows = defaultdict(set)
        self.relationship_rows = defaultdict(set)
        for a in self.tables["accounts"].itertuples(index=False):
            owner, key = f"{a.owner_type}:{a.owner_id}", f"Account:{a.account_id}"
            self._link(owner, key, a.opened_at, a.closed_at, "interval")
        for i, r in enumerate(self.tables["relationships"].itertuples(index=False)):
            source, target = f"{r.source_type}:{r.source_id}", f"{r.target_type}:{r.target_id}"
            self._link(source, target, r.start_time, r.end_time, "interval")
            self.relationship_rows[source].add(i)
            self.relationship_rows[target].add(i)
        tx = self.tables["transactions"].reset_index(drop=True)
        if tx.transaction_id.duplicated().any() or tx.timestamp.isna().any():
            raise ValueError("transactions: duplicate identifier or missing timestamp")
        self.tables["transactions"] = tx
        for i, t in enumerate(tx.itertuples(index=False)):
            if not 0 < t.amount_etb < float("inf"):
                raise ValueError("transactions: invalid amount")
            self._link(f"Account:{t.sender_account_id}", f"Account:{t.receiver_account_id}", t.timestamp, None, "event")
            self.account_rows[t.sender_account_id].add(i)
            self.account_rows[t.receiver_account_id].add(i)
        for neighbors in self.links.values():
            neighbors.sort(key=lambda item: (item[0], item[1]))

    @classmethod
    def load(cls, path):
        from generator.prysm_benchmark.storage import digest, read_snapshot
        tables, _, manifest, _ = read_snapshot(Path(path))
        return cls({n: tables[n].to_pandas() for n in cls.FACTS}, manifest["dataset_version"], digest(Path(path)/"MANIFEST.json"))

    def _link(self, source, target, start, end, kind):
        if source not in self.entities or target not in self.entities:
            raise ValueError("Broken typed graph endpoint")
        entry = (utc(start), None if pd.isna(end) else utc(end), kind)
        self.links[source].append((target, *entry))
        self.links[target].append((source, *entry))

    def snapshot(self, subject, cutoff, config):
        cutoff = utc(cutoff)
        if subject not in self.entities or self.entities[subject][0] > cutoff:
            raise ValueError(f"Subject is unknown or not yet observed: {subject}")
        history = cutoff-pd.Timedelta(days=config["history_days"])
        window = cutoff-pd.Timedelta(days=config["observation_days"])
        seen, queue, truncated = {subject}, deque([subject]), False
        while queue:
            key = queue.popleft()
            for neighbor, start, end, kind in self.links[key]:
                valid = start <= cutoff and (end is None or end >= cutoff)
                if kind == "event":
                    valid &= start >= history
                if not valid or neighbor in seen or self.entities[neighbor][0] > cutoff:
                    continue
                if len(seen) >= config["max_nodes"]:
                    truncated = True
                    continue
                seen.add(neighbor)
                queue.append(neighbor)
        t = self.tables
        def entity_frame(name):
            positions = sorted(position for key in seen for table, position in [self.entity_positions[key]] if table == name)
            return t[name].iloc[positions].copy()
        accounts = entity_frame("accounts")
        aids = set(accounts.account_id)
        indices = sorted(set().union(*(self.account_rows[a] for a in aids))) if aids else []
        tx = t["transactions"].iloc[indices]
        tx = tx[tx.sender_account_id.isin(aids) & tx.receiver_account_id.isin(aids)
                & tx.timestamp.ge(history) & tx.timestamp.le(cutoff)].sort_values(["timestamp", "transaction_id"])
        if len(tx) > config["max_transactions"]:
            truncated = True
            tx = tx.tail(config["max_transactions"])
        relation_indices = sorted(set().union(*(self.relationship_rows[key] for key in seen))) if seen else []
        rel = t["relationships"].iloc[relation_indices]
        rel = rel[(rel.source_type+":"+rel.source_id).isin(seen) & (rel.target_type+":"+rel.target_id).isin(seen)
                  & rel.start_time.le(cutoff) & (rel.end_time.isna() | rel.end_time.ge(cutoff))].copy()
        people = entity_frame("persons")
        companies = entity_frame("companies")
        # A future declaration must not be exposed even in node display attributes.
        unknown = companies.sales_reported_at.gt(cutoff)
        companies.loc[unknown, "declared_sales_etb"] = float("nan")
        return Snapshot(subject, cutoff, window, history, people, companies, accounts, rel, tx.copy(),
                        t["institutions"][t["institutions"].institution_id.isin(accounts.institution_id)].copy(), truncated)
