"""Streaming graph validation, structural features, and sparse connectivity."""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


class UnionFind:
    def __init__(self, size: int):
        self.parent = np.arange(size, dtype=np.int32)
        self.rank = np.zeros(size, dtype=np.int8)

    def find(self, value: int) -> int:
        parent = self.parent
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = int(parent[value])
        return value

    def union(self, left: int, right: int) -> None:
        a, b = self.find(left), self.find(right)
        if a == b:
            return
        if self.rank[a] < self.rank[b]:
            a, b = b, a
        self.parent[b] = a
        if self.rank[a] == self.rank[b]:
            self.rank[a] += 1

    def roots(self) -> np.ndarray:
        return np.fromiter((self.find(i) for i in range(len(self.parent))), dtype=np.int32)


def _assign_count(target: np.ndarray, node_index: pd.Index, values: pd.Series) -> None:
    positions = node_index.get_indexer(values.index.astype(str))
    valid = positions >= 0
    target[positions[valid]] = values.to_numpy()[valid]


def build_graph_features(graph_dir: Path, report_path: Path) -> dict[str, Any]:
    nodes = pd.read_parquet(graph_dir / "nodes.parquet")
    keys = pd.Index(nodes.node_key.astype(str))
    n = len(nodes)
    degree = np.zeros(n, np.int64); in_degree = np.zeros(n, np.int64); out_degree = np.zeros(n, np.int64)
    type_mask = np.zeros(n, np.uint64); tx_count = np.zeros(n, np.int64); tx_volume = np.zeros(n, float)
    tx_in_count = np.zeros(n, np.int64); tx_out_count = np.zeros(n, np.int64)
    tx_in_volume = np.zeros(n, float); tx_out_volume = np.zeros(n, float)
    unique_sources = np.zeros(n, np.int64); unique_destinations = np.zeros(n, np.int64)
    unique_counterparties = np.zeros(n, np.int64); concentration = np.zeros(n, float)
    shared_device = np.zeros(n, np.int64); shared_address = np.zeros(n, np.int64)
    account_pairs: list[np.ndarray] = []; company_pairs: list[np.ndarray] = []
    source_arrays: list[np.ndarray] = []; target_arrays: list[np.ndarray] = []; relation_arrays: list[np.ndarray] = []
    relation_names: dict[str, int] = {}; uf = UnionFind(n)
    self_loops = invalid_endpoints = duplicate_ids = duplicate_semantic = temporal_invalid = 0
    confidence_min, confidence_max = 1.0, 0.0
    edge_counts: Counter[str] = Counter(); total_edges = 0
    node_types = nodes.node_type.astype(str).to_numpy()
    ownership_src: np.ndarray | None = None; ownership_dst: np.ndarray | None = None

    for path in sorted((graph_dir / "edges").glob("*.parquet")):
        edge = pd.read_parquet(path)
        src = keys.get_indexer(edge.source_key.astype(str)); dst = keys.get_indexer(edge.target_key.astype(str))
        valid = (src >= 0) & (dst >= 0)
        invalid_endpoints += int((~valid).sum()); src, dst = src[valid].astype(np.int32), dst[valid].astype(np.int32)
        edge = edge.loc[valid].reset_index(drop=True); total_edges += len(edge)
        duplicate_ids += int(edge.edge_id.duplicated(keep=False).sum()); self_loops += int(np.sum(src == dst))
        semantic_columns = ["source_key", "target_key", "edge_type", "event_time", "end_time", "transaction_id", "relationship_id", "invoice_id"]
        duplicate_semantic += int(edge.duplicated(semantic_columns, keep=False).sum())
        start, end = pd.to_datetime(edge.event_time, utc=True), pd.to_datetime(edge.end_time, utc=True)
        temporal_invalid += int((end.notna() & end.lt(start)).sum())
        confidence = edge.confidence.dropna()
        if len(confidence):
            confidence_min = min(confidence_min, float(confidence.min())); confidence_max = max(confidence_max, float(confidence.max()))
        np.add.at(out_degree, src, 1); np.add.at(in_degree, dst, 1); np.add.at(degree, src, 1); np.add.at(degree, dst, 1)
        for relation, group_index in edge.groupby("edge_type", sort=True).groups.items():
            relation = str(relation); relation_id = relation_names.setdefault(relation, len(relation_names))
            positions = np.asarray(list(group_index), dtype=np.int64)
            bit = np.uint64(1) << np.uint64(relation_id)
            np.bitwise_or.at(type_mask, src[positions], bit); np.bitwise_or.at(type_mask, dst[positions], bit)
            edge_counts[relation] += len(positions)
        relation_arrays.append(edge.edge_type.map(relation_names).to_numpy(np.int32))
        source_arrays.append(src); target_arrays.append(dst)
        for left, right in zip(src, dst):
            uf.union(int(left), int(right))

        src_neighbor_type, dst_neighbor_type = node_types[dst], node_types[src]
        if np.any(src_neighbor_type == "Account"):
            account_pairs.append(src[src_neighbor_type == "Account"].astype(np.int64) * n + dst[src_neighbor_type == "Account"])
        if np.any(dst_neighbor_type == "Account"):
            account_pairs.append(dst[dst_neighbor_type == "Account"].astype(np.int64) * n + src[dst_neighbor_type == "Account"])
        if np.any(src_neighbor_type == "Company"):
            company_pairs.append(src[src_neighbor_type == "Company"].astype(np.int64) * n + dst[src_neighbor_type == "Company"])
        if np.any(dst_neighbor_type == "Company"):
            company_pairs.append(dst[dst_neighbor_type == "Company"].astype(np.int64) * n + src[dst_neighbor_type == "Company"])

        if path.stem == "transfers":
            amount = edge.amount_etb.fillna(0).to_numpy(float)
            np.add.at(tx_count, src, 1); np.add.at(tx_count, dst, 1)
            np.add.at(tx_volume, src, amount); np.add.at(tx_volume, dst, amount)
            np.add.at(tx_out_count, src, 1); np.add.at(tx_in_count, dst, 1)
            np.add.at(tx_out_volume, src, amount); np.add.at(tx_in_volume, dst, amount)
            directed_node = np.concatenate([src, dst]); directed_neighbor = np.concatenate([dst, src])
            pair = pd.DataFrame({"node": directed_node, "neighbor": directed_neighbor, "amount": np.concatenate([amount, amount])})
            unique_pair = pair.drop_duplicates(["node", "neighbor"])
            counts = unique_pair.groupby("node").size()
            unique_counterparties[counts.index.to_numpy(int)] = counts.to_numpy(int)
            destination_counts = edge.groupby("source_key").target_key.nunique(); source_counts = edge.groupby("target_key").source_key.nunique()
            _assign_count(unique_destinations, keys, destination_counts); _assign_count(unique_sources, keys, source_counts)
            maximum = pair.groupby(["node", "neighbor"]).amount.sum().groupby(level=0).max()
            concentration[maximum.index.to_numpy(int)] = maximum.to_numpy(float) / np.maximum(tx_volume[maximum.index.to_numpy(int)], 1.0)
        if path.stem == "ownership":
            ownership_src, ownership_dst = src.copy(), dst.copy()
        if "relationship_type" in edge.columns:
            pass
        for relation, target in [("relationship:shared_device", shared_device), ("relationship:shared_address", shared_address)]:
            mask = edge.edge_type.eq(relation).to_numpy()
            np.add.at(target, src[mask], 1); np.add.at(target, dst[mask], 1)

    all_src, all_dst = np.concatenate(source_arrays), np.concatenate(target_arrays)
    all_rel = np.concatenate(relation_arrays)
    relation_order = [name for name, _ in sorted(relation_names.items(), key=lambda item: item[1])]
    np.savez_compressed(graph_dir / "connectivity.npz", source=all_src, target=all_dst, relation=all_rel, relation_names=np.asarray(relation_order))

    def pair_counts(parts: list[np.ndarray]) -> np.ndarray:
        result = np.zeros(n, np.int64)
        if parts:
            unique = np.unique(np.concatenate(parts)); np.add.at(result, (unique // n).astype(np.int64), 1)
        return result

    connected_accounts, connected_companies = pair_counts(account_pairs), pair_counts(company_pairs)
    network_count, network_volume = tx_count.copy(), tx_volume.copy()
    network_in_count, network_out_count = tx_in_count.copy(), tx_out_count.copy()
    network_in_volume, network_out_volume = tx_in_volume.copy(), tx_out_volume.copy()
    network_counterparties = unique_counterparties.copy()
    network_sources, network_destinations = unique_sources.copy(), unique_destinations.copy()
    if ownership_src is not None and ownership_dst is not None:
        np.add.at(network_count, ownership_src, tx_count[ownership_dst]); np.add.at(network_volume, ownership_src, tx_volume[ownership_dst])
        np.add.at(network_in_count, ownership_src, tx_in_count[ownership_dst]); np.add.at(network_out_count, ownership_src, tx_out_count[ownership_dst])
        np.add.at(network_in_volume, ownership_src, tx_in_volume[ownership_dst]); np.add.at(network_out_volume, ownership_src, tx_out_volume[ownership_dst])
        account_owner = np.full(n, -1, np.int32); account_owner[ownership_dst] = ownership_src
        transfer_relation = relation_names["transfers"]; transfer_mask = all_rel == transfer_relation
        transfer_src, transfer_dst = all_src[transfer_mask], all_dst[transfer_mask]
        out_owner, in_owner = account_owner[transfer_src], account_owner[transfer_dst]
        owner_pair_parts = []
        valid = out_owner >= 0; owner_pair_parts.append(out_owner[valid].astype(np.int64) * n + transfer_dst[valid])
        valid = in_owner >= 0; owner_pair_parts.append(in_owner[valid].astype(np.int64) * n + transfer_src[valid])
        owner_pairs = np.unique(np.concatenate(owner_pair_parts)); owner_counts = pd.Series(owner_pairs // n).value_counts()
        network_counterparties[owner_counts.index.to_numpy(int)] = owner_counts.to_numpy(int)
        valid = out_owner >= 0; dest_pairs = np.unique(out_owner[valid].astype(np.int64) * n + transfer_dst[valid]); dest_counts = pd.Series(dest_pairs // n).value_counts()
        network_destinations[dest_counts.index.to_numpy(int)] = dest_counts.to_numpy(int)
        valid = in_owner >= 0; source_pairs = np.unique(in_owner[valid].astype(np.int64) * n + transfer_src[valid]); source_counts = pd.Series(source_pairs // n).value_counts()
        network_sources[source_counts.index.to_numpy(int)] = source_counts.to_numpy(int)
    roots = uf.roots(); _, component_id = np.unique(roots, return_inverse=True)
    component_sizes = np.bincount(component_id); node_component_size = component_sizes[component_id]
    two_hop_paths = np.zeros(n, np.int64)
    np.add.at(two_hop_paths, all_src, np.maximum(degree[all_dst] - 1, 0)); np.add.at(two_hop_paths, all_dst, np.maximum(degree[all_src] - 1, 0))
    two_hop_paths = np.minimum(two_hop_paths, 1_000_000)
    diversity = np.fromiter((int(value).bit_count() for value in type_mask), dtype=np.int16)
    features = pd.DataFrame({
        "node_key": nodes.node_key, "node_type": nodes.node_type, "degree": degree, "in_degree": in_degree,
        "out_degree": out_degree, "edge_type_diversity": diversity, "transaction_count": tx_count,
        "transaction_volume_etb": tx_volume, "unique_counterparties": unique_counterparties,
        "network_transaction_count": network_count, "network_transaction_volume_etb": network_volume,
        "network_incoming_count": network_in_count, "network_outgoing_count": network_out_count,
        "network_incoming_volume_etb": network_in_volume, "network_outgoing_volume_etb": network_out_volume,
        "network_outflow_ratio": network_out_volume / np.maximum(network_in_volume, 1.0),
        "network_unique_counterparties": network_counterparties, "network_unique_sources": network_sources,
        "network_unique_destinations": network_destinations,
        "counterparty_concentration": concentration, "connected_account_count": connected_accounts,
        "connected_company_count": connected_companies, "shared_device_count": shared_device,
        "shared_address_count": shared_address, "two_hop_path_count_capped": two_hop_paths,
        "component_id": component_id, "component_size": node_component_size,
    })
    anomaly_parts = []
    for _, group in features.groupby("node_type", sort=False):
        values = np.log1p(group[["degree", "edge_type_diversity", "network_transaction_count", "network_transaction_volume_etb", "two_hop_path_count_capped"]].to_numpy(float))
        median = np.median(values, axis=0); mad = np.median(np.abs(values - median), axis=0)
        z = np.abs(values - median) / np.where(mad > 1e-9, 1.4826 * mad, 1.0)
        anomaly_parts.append(pd.Series(1.0 - np.exp(-np.mean(np.clip(z, 0, 10), axis=1) / 3.0), index=group.index))
    features["structural_anomaly_score"] = pd.concat(anomaly_parts).sort_index().to_numpy()
    features.to_parquet(graph_dir / "node_features.parquet", index=False)
    top = features.nlargest(20, "degree")[["node_key", "node_type", "degree", "transaction_volume_etb"]].to_dict("records")
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(), "graph_version": "prysm-financial-graph-v1",
        "node_count": n, "edge_count": int(total_edges), "node_counts": {str(k): int(v) for k, v in nodes.node_type.value_counts().items()},
        "edge_counts": dict(edge_counts), "invalid_endpoints": invalid_endpoints, "duplicate_edge_id_rows": duplicate_ids,
        "duplicate_semantic_edge_rows": duplicate_semantic,
        "self_loops": self_loops, "temporal_end_before_start": temporal_invalid,
        "confidence_range": [confidence_min, confidence_max], "orphan_nodes": int(np.sum(degree == 0)),
        "connected_components": int(len(component_sizes)), "largest_component": int(component_sizes.max()),
        "ownership_edge_count": int(edge_counts["owns"]), "expected_account_ownership_edges": int((nodes.node_type == "Account").sum()),
        "dense_entities_are_context_not_risk": top, "supervised_labels_used": False,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
    return report
