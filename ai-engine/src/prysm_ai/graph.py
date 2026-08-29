"""Canonical typed, temporal financial graph construction and bounded views."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd


EDGE_COLUMNS = [
    "edge_id", "source_key", "target_key", "edge_type", "temporal_kind",
    "event_time", "end_time", "confidence", "amount_etb", "currency",
    "transaction_id", "relationship_id", "invoice_id", "source_table",
]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _edge_frame(**values: Any) -> pd.DataFrame:
    frame = pd.DataFrame(values)
    for column in EDGE_COLUMNS:
        if column not in frame:
            frame[column] = pd.NA
    frame["event_time"] = pd.to_datetime(frame["event_time"], utc=True)
    frame["end_time"] = pd.to_datetime(frame["end_time"], utc=True)
    frame["confidence"] = pd.to_numeric(frame["confidence"], errors="coerce").astype("float32")
    frame["amount_etb"] = pd.to_numeric(frame["amount_etb"], errors="coerce")
    return frame[EDGE_COLUMNS]


class CanonicalGraphBuilder:
    VERSION = "prysm-financial-graph-v1"

    def __init__(self, processed_dir: Path, graph_dir: Path):
        self.processed_dir, self.graph_dir = processed_dir, graph_dir

    def _load(self) -> dict[str, pd.DataFrame]:
        names = ["persons", "accounts", "invoices", "relationship_edges", "transaction_edges"]
        return {name: pd.read_parquet(self.processed_dir / f"{name}.parquet") for name in names}

    @staticmethod
    def _nodes(t: dict[str, pd.DataFrame]) -> pd.DataFrame:
        persons, accounts, invoices, rel, tx = (t[name] for name in ["persons", "accounts", "invoices", "relationship_edges", "transaction_edges"])
        company_ids = set(accounts.loc[accounts.owner_type.eq("Company"), "owner_id"])
        company_ids.update(invoices.loc[invoices.issuer_type.eq("Company"), "issuer_id"])
        company_ids.update(invoices.loc[invoices.recipient_type.eq("Company"), "recipient_id"])
        company_ids.update(rel.loc[rel.source_type.eq("Company"), "source_id"])
        company_ids.update(rel.loc[rel.target_type.eq("Company"), "target_id"])
        frames = [
            pd.DataFrame({"node_key": "Person:" + persons.person_id.astype(str), "node_type": "Person", "source_id": persons.person_id, "status": persons.employment_status, "currency": persons.income_currency, "event_time": persons.created_at, "provenance": "persons.parquet"}),
            pd.DataFrame({"node_key": "Company:" + pd.Series(sorted(company_ids), dtype="string"), "node_type": "Company", "source_id": pd.Series(sorted(company_ids), dtype="string"), "provenance": "canonical_link_inference"}),
            pd.DataFrame({"node_key": "Account:" + accounts.account_id.astype(str), "node_type": "Account", "source_id": accounts.account_id, "status": accounts.status, "currency": accounts.currency, "event_time": accounts.opened_at, "provenance": "accounts.parquet"}),
            pd.DataFrame({"node_key": "Bank:" + accounts.institution_id.drop_duplicates().sort_values().astype(str), "node_type": "Bank", "source_id": accounts.institution_id.drop_duplicates().sort_values().astype(str), "provenance": "accounts.institution_id"}),
            pd.DataFrame({"node_key": "Device:" + tx.device_id.dropna().drop_duplicates().sort_values().astype(str), "node_type": "Device", "source_id": tx.device_id.dropna().drop_duplicates().sort_values().astype(str), "provenance": "transaction_edges.device_id"}),
            pd.DataFrame({"node_key": "Invoice:" + invoices.invoice_id.astype(str), "node_type": "Invoice", "source_id": invoices.invoice_id, "status": invoices.status, "currency": invoices.currency, "event_time": invoices.issue_date, "provenance": "invoices.parquet"}),
        ]
        nodes = pd.concat(frames, ignore_index=True, sort=False)
        nodes["event_time"] = pd.to_datetime(nodes.get("event_time"), utc=True)
        return nodes.drop_duplicates("node_key", keep="first").sort_values("node_key", kind="stable").reset_index(drop=True)

    @staticmethod
    def _edges(t: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        accounts, invoices, rel, tx = (t[name] for name in ["accounts", "invoices", "relationship_edges", "transaction_edges"])
        ownership = _edge_frame(
            edge_id="OWN:" + accounts.account_id.astype(str), source_key=accounts.owner_key,
            target_key="Account:" + accounts.account_id.astype(str), edge_type="owns", temporal_kind="interval",
            event_time=accounts.opened_at, end_time=accounts.closed_at, confidence=1.0, source_table="accounts.parquet",
        )
        held_at = _edge_frame(
            edge_id="BANK:" + accounts.account_id.astype(str), source_key="Account:" + accounts.account_id.astype(str),
            target_key="Bank:" + accounts.institution_id.astype(str), edge_type="held_at", temporal_kind="interval",
            event_time=accounts.opened_at, end_time=accounts.closed_at, confidence=1.0, source_table="accounts.parquet",
        )
        transfers = _edge_frame(
            edge_id="TX:" + tx.transaction_id.astype(str), source_key=tx.sender_key, target_key=tx.receiver_key,
            edge_type="transfers", temporal_kind="event", event_time=tx.timestamp, confidence=1.0,
            amount_etb=tx.amount_etb, currency=tx.currency, transaction_id=tx.transaction_id,
            invoice_id=tx.invoice_id, source_table="transaction_edges.parquet",
        )
        device_tx = tx[tx.device_id.notna()]
        uses_device = _edge_frame(
            edge_id="DEV:" + device_tx.transaction_id.astype(str), source_key=device_tx.sender_key,
            target_key="Device:" + device_tx.device_id.astype(str), edge_type="uses_device", temporal_kind="event",
            event_time=device_tx.timestamp, confidence=1.0, transaction_id=device_tx.transaction_id,
            source_table="transaction_edges.parquet",
        )
        invoice_tx = tx[tx.invoice_id.notna()]
        linked_invoice = _edge_frame(
            edge_id="INVTX:" + invoice_tx.transaction_id.astype(str), source_key=invoice_tx.sender_key,
            target_key="Invoice:" + invoice_tx.invoice_id.astype(str), edge_type="transaction_linked_invoice",
            temporal_kind="event", event_time=invoice_tx.timestamp, confidence=1.0,
            amount_etb=invoice_tx.amount_etb, currency=invoice_tx.currency,
            transaction_id=invoice_tx.transaction_id, invoice_id=invoice_tx.invoice_id,
            source_table="transaction_edges.parquet",
        )
        issuer = _edge_frame(
            edge_id="ISSUER:" + invoices.invoice_id.astype(str), source_key=invoices.issuer_key,
            target_key="Invoice:" + invoices.invoice_id.astype(str), edge_type="issued_invoice",
            temporal_kind="event", event_time=invoices.issue_date, confidence=1.0,
            currency=invoices.currency, invoice_id=invoices.invoice_id, source_table="invoices.parquet",
        )
        recipient = _edge_frame(
            edge_id="RECIPIENT:" + invoices.invoice_id.astype(str), source_key=invoices.recipient_key,
            target_key="Invoice:" + invoices.invoice_id.astype(str), edge_type="received_invoice",
            temporal_kind="event", event_time=invoices.issue_date, confidence=1.0,
            currency=invoices.currency, invoice_id=invoices.invoice_id, source_table="invoices.parquet",
        )
        relationships = _edge_frame(
            edge_id="REL:" + rel.relationship_id.astype(str), source_key=rel.source_key, target_key=rel.target_key,
            edge_type="relationship:" + rel.relationship_type.astype(str), temporal_kind="interval",
            event_time=rel.start_time, end_time=rel.end_time, confidence=rel.confidence,
            relationship_id=rel.relationship_id, source_table="relationship_edges.parquet",
        )
        return {"ownership": ownership, "held_at": held_at, "transfers": transfers, "uses_device": uses_device,
                "linked_invoice": linked_invoice, "invoice_issuer": issuer, "invoice_recipient": recipient,
                "relationships": relationships}

    def build(self) -> dict[str, Any]:
        self.graph_dir.mkdir(parents=True, exist_ok=True)
        edge_dir = self.graph_dir / "edges"
        edge_dir.mkdir(parents=True, exist_ok=True)
        tables = self._load()
        nodes = self._nodes(tables)
        nodes.to_parquet(self.graph_dir / "nodes.parquet", index=False)
        families = self._edges(tables)
        for name, frame in families.items():
            frame.to_parquet(edge_dir / f"{name}.parquet", index=False)
        node_keys = set(nodes.node_key)
        invalid = sum((~frame.source_key.isin(node_keys) | ~frame.target_key.isin(node_keys)).sum() for frame in families.values())
        manifest = {
            "graph_version": self.VERSION, "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "nodes": {"rows": int(len(nodes)), "sha256": _sha256(self.graph_dir / "nodes.parquet"), "by_type": {str(k): int(v) for k, v in nodes.node_type.value_counts().items()}},
            "edges": {name: {"rows": int(len(frame)), "sha256": _sha256(edge_dir / f"{name}.parquet"), "by_type": {str(k): int(v) for k, v in frame.edge_type.value_counts().items()}} for name, frame in families.items()},
            "invalid_endpoints": int(invalid), "source_labels_used": False,
        }
        with (self.graph_dir / "MANIFEST.json").open("w", encoding="utf-8") as handle:
            json.dump(manifest, handle, indent=2, sort_keys=True)
        return manifest


def temporal_filter(edges: pd.DataFrame, cutoff: pd.Timestamp, lookback_days: int | None = None, mode: str = "predictive") -> pd.DataFrame:
    cutoff = pd.Timestamp(cutoff)
    if mode not in {"predictive", "retrospective"}:
        raise ValueError("mode must be predictive or retrospective")
    if mode == "retrospective":
        return edges.copy()
    event_time = pd.to_datetime(edges.event_time, utc=True)
    end_time = pd.to_datetime(edges.end_time, utc=True)
    event = edges.temporal_kind.eq("event") & event_time.le(cutoff)
    if lookback_days is not None:
        event &= event_time.gt(cutoff - pd.Timedelta(days=lookback_days))
    interval = edges.temporal_kind.eq("interval") & event_time.le(cutoff) & (end_time.isna() | end_time.ge(cutoff))
    return edges[event | interval].copy()


class GraphStore:
    """Disk-backed deterministic bounded neighborhood access."""

    def __init__(self, graph_dir: Path):
        self.graph_dir = graph_dir
        self.nodes = pd.read_parquet(graph_dir / "nodes.parquet").set_index("node_key", drop=False)
        self.edge_paths = sorted((graph_dir / "edges").glob("*.parquet"))

    def incident(self, keys: set[str], cutoff: pd.Timestamp, lookback_days: int | None, mode: str,
                 edge_types: set[str] | None = None, minimum_confidence: float = 0.0) -> pd.DataFrame:
        frames = []
        for path in self.edge_paths:
            frame = pd.read_parquet(path)
            frame = frame[frame.source_key.isin(keys) | frame.target_key.isin(keys)]
            if edge_types:
                frame = frame[frame.edge_type.isin(edge_types)]
            frame = frame[frame.confidence.fillna(1.0).ge(minimum_confidence)]
            frame = temporal_filter(frame, cutoff, lookback_days, mode)
            if len(frame):
                frames.append(frame)
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=EDGE_COLUMNS)

    def subgraph(self, subject: str, cutoff: pd.Timestamp, max_hops: int = 2, max_nodes: int = 200,
                 lookback_days: int | None = 365, mode: str = "predictive", edge_types: set[str] | None = None,
                 minimum_confidence: float = 0.3) -> tuple[pd.DataFrame, pd.DataFrame]:
        if subject not in self.nodes.index:
            raise KeyError(f"Unknown typed node: {subject}")
        visited, frontier, selected_edges = {subject}, {subject}, {}
        for _ in range(max_hops):
            if not frontier or len(visited) >= max_nodes:
                break
            incident = self.incident(frontier, cutoff, lookback_days, mode, edge_types, minimum_confidence)
            incident = incident.sort_values(["event_time", "edge_id"], ascending=[False, True], kind="stable")
            next_frontier = set()
            for row in incident.itertuples(index=False):
                candidates = [row.source_key, row.target_key]
                new_nodes = [key for key in candidates if key not in visited]
                if len(visited) + len(new_nodes) > max_nodes:
                    continue
                selected_edges[row.edge_id] = row
                for key in new_nodes:
                    visited.add(key); next_frontier.add(key)
            frontier = next_frontier
        node_frame = self.nodes.loc[sorted(visited)].reset_index(drop=True)
        edge_frame = pd.DataFrame([row._asdict() for row in selected_edges.values()], columns=EDGE_COLUMNS)
        return node_frame, edge_frame.sort_values("edge_id", kind="stable").reset_index(drop=True) if len(edge_frame) else edge_frame

