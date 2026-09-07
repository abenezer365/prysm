"""Source-backed graph DTO and label-free tensors for learned message passing."""
from dataclasses import dataclass
import numpy as np
import pandas as pd

from .features import build_features

NODE_FEATURES = ("is_person", "is_company", "is_account", "recent_in_count", "recent_out_count",
                 "recent_in_etb", "recent_out_etb", "historical_median_etb", "burst_15m", "foreign_fraction", "new_device_fraction")
RELATIONS = ("ownership", "family", "business", "incoming_transfer", "outgoing_transfer")


def graph_dto(snapshot):
    nodes, edges = [], []
    for p in snapshot.persons.itertuples(index=False):
        details = p._asdict()
        optional = {key: details.get(key) for key in (
            "date_of_birth", "gender", "nationality", "occupation", "employment_status",
            "declared_monthly_income", "income_currency", "region", "country"
        ) if details.get(key) is not None and not pd.isna(details.get(key))}
        if "date_of_birth" in optional:
            optional["date_of_birth"] = optional["date_of_birth"].isoformat()
        nodes.append({"id": f"Person:{p.person_id}", "type": "Person", "label": f"{p.first_name} {p.last_name}",
                      "person_id": p.person_id, **optional, "city": p.city,
                      "latitude": p.latitude, "longitude": p.longitude})
    for c in snapshot.companies.itertuples(index=False):
        nodes.append({"id": f"Company:{c.company_id}", "type": "Company", "label": c.company_name,
                      "industry": c.industry, "city": c.city, "latitude": c.latitude, "longitude": c.longitude})
    for b in snapshot.institutions.itertuples(index=False):
        nodes.append({"id": f"Institution:{b.institution_id}", "type": "Institution", "label": b.institution_name})
    for a in snapshot.accounts.itertuples(index=False):
        key = f"Account:{a.account_id}"
        nodes.append({"id": key, "type": "Account", "label": a.account_id, "currency": a.currency})
        edges.extend([
            {"id": f"OWN:{a.account_id}", "source": f"{a.owner_type}:{a.owner_id}", "target": key,
             "type": "owns", "source_table": "accounts.parquet", "source_id": a.account_id, "timestamp": a.opened_at.isoformat()},
            {"id": f"BANK:{a.account_id}", "source": key, "target": f"Institution:{a.institution_id}",
             "type": "held_at", "source_table": "accounts.parquet", "source_id": a.account_id, "timestamp": a.opened_at.isoformat()},
        ])
    for r in snapshot.relationships.itertuples(index=False):
        edges.append({"id": f"REL:{r.relationship_id}", "source": f"{r.source_type}:{r.source_id}",
                      "target": f"{r.target_type}:{r.target_id}", "type": r.relationship_type, "confidence": r.confidence,
                      "relationship_id": r.relationship_id, "source_table": "relationships.parquet", "source_id": r.relationship_id,
                      "timestamp": r.start_time.isoformat(), "end_time": None if pd.isna(r.end_time) else r.end_time.isoformat()})
    devices = set()
    for t in snapshot.transactions.itertuples(index=False):
        edges.append({"id": f"TX:{t.transaction_id}", "source": f"Account:{t.sender_account_id}", "target": f"Account:{t.receiver_account_id}",
                      "type": "transfers", "timestamp": t.timestamp.isoformat(), "amount_etb": t.amount_etb, "currency": t.currency,
                      "channel": t.channel, "city": t.city, "latitude": t.latitude, "longitude": t.longitude,
                      "transaction_id": t.transaction_id, "source_table": "transactions.parquet", "source_id": t.transaction_id})
        if isinstance(t.device_id, str):
            devices.add(t.device_id)
            edges.append({"id": f"DEV:{t.transaction_id}", "source": f"Account:{t.sender_account_id}", "target": f"Device:{t.device_id}",
                          "type": "uses_device", "timestamp": t.timestamp.isoformat(), "transaction_id": t.transaction_id,
                          "source_table": "transactions.parquet", "source_id": t.transaction_id})
    nodes.extend({"id": f"Device:{d}", "type": "Device", "label": d,
                  "description": "Device observed on a transaction in this cutoff-valid neighborhood"} for d in sorted(devices))
    ids = {n["id"] for n in nodes}
    if snapshot.truncated:
        edges = [e for e in edges if e["source"] in ids and e["target"] in ids]
    elif any(e["source"] not in ids or e["target"] not in ids for e in edges):
        raise ValueError("Graph contains unresolved endpoints")
    for n in nodes:
        n["is_subject"] = n["id"] == snapshot.subject
    return {"version": "prysm-graph-evidence-v2", "subject": snapshot.subject, "cutoff": snapshot.cutoff.isoformat(),
            "truncated": snapshot.truncated, "nodes": sorted(nodes, key=lambda n: n["id"]), "edges": sorted(edges, key=lambda e: e["id"])}


@dataclass
class GraphSample:
    x: np.ndarray
    adjacency: np.ndarray
    root: int
    node_keys: list[str]
    # For counterfactual localization, not features or labels.
    transaction_channels: dict


def graph_sample(snapshot):
    keys = sorted([f"Person:{p}" for p in snapshot.persons.person_id]+[f"Company:{c}" for c in snapshot.companies.company_id]+[f"Account:{a}" for a in snapshot.accounts.account_id])
    index = {key: i for i, key in enumerate(keys)}
    x = []
    for key in keys:
        f = build_features(snapshot, key)
        incoming = f.recent[f.recent.receiver_account_id.isin(f.own_accounts)]
        outgoing = f.recent[f.recent.sender_account_id.isin(f.own_accounts)]
        kind = key.split(":", 1)[0]
        row = [float(kind == k) for k in ("Person", "Company", "Account")]
        row += [len(incoming), len(outgoing), float(incoming.amount_etb.sum()), float(outgoing.amount_etb.sum()),
                f.values["history_median_etb"] or 0., f.values["burst_15m"],
                float(f.recent.currency.ne("ETB").mean()) if len(f.recent) else 0., f.values["new_device_fraction"]]
        x.append(row)
    adjacency = np.zeros((len(RELATIONS), len(keys), len(keys)), dtype=float)

    def both(channel, a, b):
        if a in index and b in index:
            adjacency[channel, index[a], index[b]] += 1
            adjacency[channel, index[b], index[a]] += 1

    for a in snapshot.accounts.itertuples(index=False):
        both(0, f"{a.owner_type}:{a.owner_id}", f"Account:{a.account_id}")
    for r in snapshot.relationships.itertuples(index=False):
        both(1 if r.relationship_type == "family" else 2, f"{r.source_type}:{r.source_id}", f"{r.target_type}:{r.target_id}")
    channels = {}
    for t in snapshot.transactions[snapshot.transactions.timestamp.ge(snapshot.window_start)].itertuples(index=False):
        a, b = index[f"Account:{t.sender_account_id}"], index[f"Account:{t.receiver_account_id}"]
        adjacency[3, b, a] += 1
        adjacency[4, a, b] += 1
        channels[t.transaction_id] = [(3, b, a), (4, a, b)]
    # Institutions and device IDs are display/evidence nodes only. Shared banks
    # cannot connect train and held-out cases through message passing.
    return GraphSample(np.log1p(np.asarray(x, float)), adjacency, index[snapshot.subject], keys, channels)
