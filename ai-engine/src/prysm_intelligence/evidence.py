"""Small source-backed findings, graph references and deterministic identities."""
from dataclasses import dataclass, field
import hashlib
import json


@dataclass
class Lead:
    code: str
    source: str
    reason: str
    strength: float
    transaction_ids: list[str] = field(default_factory=list)
    relationship_ids: list[str] = field(default_factory=list)
    entity_keys: list[str] = field(default_factory=list)
    measurements: dict = field(default_factory=dict)
    # Model saliency describes score sensitivity, never a transaction fraud label.
    highlight: bool = True


def build_evidence(snapshot, leads, graph, dataset_version, source_checksum, analysis_fingerprint):
    transactions = snapshot.transactions.set_index("transaction_id")
    relationships = set(snapshot.relationships.relationship_id)
    node_ids = {n["id"] for n in graph["nodes"]}
    edge_ids = {e["id"] for e in graph["edges"]}
    evidence = []
    for lead in leads:
        tids, rids = sorted(set(lead.transaction_ids)), sorted(set(lead.relationship_ids))
        if not set(tids) <= set(transactions.index) or not set(rids) <= relationships:
            raise ValueError(f"Unresolved evidence for {lead.code}")
        entities = {snapshot.subject, *lead.entity_keys}
        for tid in tids:
            row = transactions.loc[tid]
            entities.update((f"Account:{row.sender_account_id}", f"Account:{row.receiver_account_id}"))
        if not entities <= node_ids:
            raise ValueError(f"Unresolved evidence entity for {lead.code}")
        edges = [f"TX:{i}" for i in tids]+[f"REL:{i}" for i in rids]
        if not set(edges) <= edge_ids:
            raise ValueError(f"Unresolved graph evidence for {lead.code}")
        identity = json.dumps([dataset_version, source_checksum, analysis_fingerprint, snapshot.subject, snapshot.cutoff.isoformat(), lead.source, lead.code, tids, rids], separators=(",", ":"))
        eid = "EVD:"+hashlib.sha256(identity.encode()).hexdigest()[:20]
        evidence.append({
            "evidence_id": eid, "entity_id": snapshot.subject, "signal_source": lead.source,
            "signal_type": lead.code, "description": lead.reason, "strength": float(lead.strength),
            "severity": "high" if lead.strength >= .8 else "medium", "confidence": .6 if lead.source in {"anomaly", "gnn"} else .9,
            "supporting_entity_ids": sorted(entities), "supporting_transaction_ids": tids,
            "supporting_relationship_ids": rids, "supporting_edge_ids": edges,
            "measurements": lead.measurements,
            "timestamps": sorted({transactions.loc[i, "timestamp"].isoformat() for i in tids}),
            "provenance": {"dataset_version": dataset_version, "source_manifest_sha256": source_checksum,
                           "analysis_fingerprint": analysis_fingerprint,
                           "cutoff": snapshot.cutoff.isoformat(), "source_tables": ["transactions.parquet"]+(["relationships.parquet"] if rids else [])+(["companies.parquet"] if lead.code == "BUSINESS_RECEIPTS_MISMATCH" else []),
                           "model_artifact": "model_bundle.json" if lead.source in {"anomaly", "gnn"} else None,
                           "interpretation": "investigation lead; not proof or a fraud probability"},
            "graph_highlight": lead.highlight,
        })
    return evidence


def annotate_graph(graph, evidence):
    node_evidence, edge_evidence = {}, {}
    for item in evidence:
        if not item["graph_highlight"]:
            continue
        for key in item["supporting_entity_ids"]:
            node_evidence.setdefault(key, []).append(item["evidence_id"])
        for key in item["supporting_edge_ids"]:
            edge_evidence.setdefault(key, []).append(item["evidence_id"])
    for collection, references in ((graph["nodes"], node_evidence), (graph["edges"], edge_evidence)):
        for item in collection:
            ids = sorted(set(references.get(item["id"], [])))
            item.update(attention="review" if ids else "none", evidence_ids=ids,
                        highlight_color="red" if ids else None)
    graph["highlight_semantics"] = "Red = linked to an AI investigation lead, not confirmed misconduct; unmarked = no localized lead, not certified innocent."
    return graph
