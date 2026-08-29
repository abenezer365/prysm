"""Deterministic relation-aware GraphSAGE representation.

The encoder implements a real heterogeneous message-passing forward pass. Its
weights are seeded engineering projections, not supervised parameters; current
labels prohibit predictive training and evaluation.
"""

from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


class RelationalGraphSAGEEncoder:
    VERSION = "relational-graphsage-structural-v1"

    def __init__(self, input_dim: int, relation_count: int, type_count: int, hidden_dim: int = 16,
                 layers: int = 2, random_seed: int = 42, batch_size: int = 200_000):
        self.input_dim, self.relation_count, self.type_count = input_dim, relation_count, type_count
        self.hidden_dim, self.layers, self.random_seed, self.batch_size = hidden_dim, layers, random_seed, batch_size
        rng = np.random.default_rng(random_seed)
        self.input_weight = rng.normal(0, 1 / np.sqrt(max(input_dim, 1)), (input_dim, hidden_dim)).astype("float32")
        self.type_embedding = rng.normal(0, 0.1, (type_count, hidden_dim)).astype("float32")
        self.relation_embedding = rng.normal(0, 0.05, (relation_count, hidden_dim)).astype("float32")
        self.layer_weights = [rng.normal(0, 1 / np.sqrt(2 * hidden_dim), (2 * hidden_dim, hidden_dim)).astype("float32") for _ in range(layers)]
        self.projection = np.eye(hidden_dim, dtype="float32")

    def forward(self, x: np.ndarray, node_types: np.ndarray, source: np.ndarray, target: np.ndarray,
                relations: np.ndarray) -> np.ndarray:
        h = np.tanh(np.asarray(x, np.float32) @ self.input_weight + self.type_embedding[node_types])
        for weight in self.layer_weights:
            aggregate = np.zeros_like(h); counts = np.zeros(len(h), np.float32)
            for start in range(0, len(source), self.batch_size):
                end = min(start + self.batch_size, len(source)); src, dst, rel = source[start:end], target[start:end], relations[start:end]
                np.add.at(aggregate, dst, h[src] + self.relation_embedding[rel])
                np.add.at(aggregate, src, h[dst] + self.relation_embedding[rel])
                np.add.at(counts, dst, 1); np.add.at(counts, src, 1)
            neighbor = aggregate / np.maximum(counts[:, None], 1.0)
            h = np.tanh(np.concatenate([h, neighbor], axis=1) @ weight)
        norm = np.linalg.norm(h, axis=1, keepdims=True)
        return h / np.maximum(norm, 1e-9)

    def fit_contrastive_projection(self, h: np.ndarray, source: np.ndarray, target: np.ndarray, node_types: np.ndarray,
                                   epochs: int, learning_rate: float, batch_size: int, l2: float) -> list[float]:
        rng = np.random.default_rng(self.random_seed + 1); losses = []
        type_buckets = {kind: np.flatnonzero(node_types == kind) for kind in np.unique(node_types)}
        for _ in range(epochs):
            order = rng.permutation(len(source)); epoch_loss = 0.0; seen = 0
            for start in range(0, len(order), batch_size):
                batch = order[start:start + batch_size]; src, dst = source[batch], target[batch]
                negative = np.empty(len(batch), np.int32)
                for kind in np.unique(node_types[dst]):
                    mask = node_types[dst] == kind; bucket = type_buckets[kind]
                    negative[mask] = rng.choice(bucket, size=int(mask.sum()), replace=True)
                hs, hd, hn = h[src], h[dst], h[negative]
                zs, zd, zn = hs @ self.projection, hd @ self.projection, hn @ self.projection
                positive_score = np.clip(np.sum(zs * zd, axis=1), -20, 20); negative_score = np.clip(np.sum(zs * zn, axis=1), -20, 20)
                d_positive = 1.0 / (1.0 + np.exp(-positive_score)) - 1.0
                d_negative = 1.0 / (1.0 + np.exp(-negative_score))
                gradient = (hs.T @ (d_positive[:, None] * zd + d_negative[:, None] * zn)
                            + hd.T @ (d_positive[:, None] * zs) + hn.T @ (d_negative[:, None] * zs)) / len(batch)
                gradient += l2 * self.projection; self.projection -= learning_rate * gradient.astype("float32")
                epoch_loss += float(np.logaddexp(0, -positive_score).sum() + np.logaddexp(0, negative_score).sum()); seen += 2 * len(batch)
            losses.append(epoch_loss / max(seen, 1))
        return losses

    def project(self, h: np.ndarray) -> np.ndarray:
        result = h @ self.projection; return result / np.maximum(np.linalg.norm(result, axis=1, keepdims=True), 1e-9)

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_version": self.VERSION, "architecture": "relation-aware mean GraphSAGE",
            "input_dim": self.input_dim, "relation_count": self.relation_count, "type_count": self.type_count,
            "hidden_dim": self.hidden_dim, "layers": self.layers, "random_seed": self.random_seed, "batch_size": self.batch_size,
            "input_weight": self.input_weight.tolist(), "type_embedding": self.type_embedding.tolist(),
            "relation_embedding": self.relation_embedding.tolist(), "layer_weights": [value.tolist() for value in self.layer_weights],
            "projection": self.projection.tolist(),
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "RelationalGraphSAGEEncoder":
        result = cls(value["input_dim"], value["relation_count"], value["type_count"], value["hidden_dim"], value["layers"], value["random_seed"], value["batch_size"])
        result.input_weight = np.asarray(value["input_weight"], np.float32)
        result.type_embedding = np.asarray(value["type_embedding"], np.float32)
        result.relation_embedding = np.asarray(value["relation_embedding"], np.float32)
        result.layer_weights = [np.asarray(item, np.float32) for item in value["layer_weights"]]
        result.projection = np.asarray(value.get("projection", np.eye(result.hidden_dim)), np.float32)
        return result


def _robust_by_type(features: pd.DataFrame, columns: list[str]) -> tuple[np.ndarray, dict[str, Any]]:
    result = np.zeros((len(features), len(columns)), np.float32)
    stats = {}
    for node_type, group in features.groupby("node_type", sort=False):
        values = np.log1p(np.maximum(group[columns].to_numpy(float), 0))
        median = np.median(values, axis=0); q25, q75 = np.percentile(values, [25, 75], axis=0)
        scale = np.where(q75 - q25 > 1e-9, q75 - q25, 1.0)
        result[group.index] = np.clip((values - median) / scale, -10, 10)
        stats[str(node_type)] = {"median": median.tolist(), "scale": scale.tolist()}
    return result, stats


def subgraph_raw_features(nodes: pd.DataFrame, edges: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Compute the GNN input contract using only a supplied temporal subgraph."""
    nodes = nodes.reset_index(drop=True); index = pd.Index(nodes.node_key.astype(str)); n = len(nodes)
    values = {name: np.zeros(n, float) for name in columns}
    if not len(edges):
        values["component_size"][:] = 1
        return pd.DataFrame({"node_key": nodes.node_key, "node_type": nodes.node_type, **values})
    src = index.get_indexer(edges.source_key.astype(str)); dst = index.get_indexer(edges.target_key.astype(str)); valid = (src >= 0) & (dst >= 0)
    src, dst = src[valid], dst[valid]; edge = edges.loc[valid].reset_index(drop=True)
    for target, source_values in [(values["degree"], np.concatenate([src, dst])), (values["out_degree"], src), (values["in_degree"], dst)]:
        np.add.at(target, source_values, 1)
    diversity = [set() for _ in range(n)]; neighbors = [set() for _ in range(n)]
    account_neighbors = [set() for _ in range(n)]; company_neighbors = [set() for _ in range(n)]
    for s, d, relation in zip(src, dst, edge.edge_type.astype(str)):
        diversity[s].add(relation); diversity[d].add(relation); neighbors[s].add(d); neighbors[d].add(s)
        if nodes.iloc[d].node_type == "Account": account_neighbors[s].add(d)
        if nodes.iloc[s].node_type == "Account": account_neighbors[d].add(s)
        if nodes.iloc[d].node_type == "Company": company_neighbors[s].add(d)
        if nodes.iloc[s].node_type == "Company": company_neighbors[d].add(s)
    values["edge_type_diversity"] = np.asarray([len(item) for item in diversity], float)
    values["connected_account_count"] = np.asarray([len(item) for item in account_neighbors], float)
    values["connected_company_count"] = np.asarray([len(item) for item in company_neighbors], float)
    values["component_size"][:] = n
    for relation, name in [("relationship:shared_device", "shared_device_count"), ("relationship:shared_address", "shared_address_count")]:
        mask = edge.edge_type.eq(relation).to_numpy(); np.add.at(values[name], src[mask], 1); np.add.at(values[name], dst[mask], 1)
    transfers = edge.edge_type.eq("transfers").to_numpy(); amount = edge.amount_etb.fillna(0).to_numpy(float)
    np.add.at(values["network_transaction_count"], src[transfers], 1); np.add.at(values["network_transaction_count"], dst[transfers], 1)
    np.add.at(values["network_transaction_volume_etb"], src[transfers], amount[transfers]); np.add.at(values["network_transaction_volume_etb"], dst[transfers], amount[transfers])
    counterparties = [set() for _ in range(n)]
    for s, d in zip(src[transfers], dst[transfers]): counterparties[s].add(d); counterparties[d].add(s)
    ownership = edge.edge_type.eq("owns").to_numpy()
    for owner, account in zip(src[ownership], dst[ownership]):
        values["network_transaction_count"][owner] += values["network_transaction_count"][account]
        values["network_transaction_volume_etb"][owner] += values["network_transaction_volume_etb"][account]
        counterparties[owner].update(counterparties[account])
    values["network_unique_counterparties"] = np.asarray([len(item) for item in counterparties], float)
    return pd.DataFrame({"node_key": nodes.node_key, "node_type": nodes.node_type, **values})


def encode_temporal_subgraph(nodes: pd.DataFrame, edges: pd.DataFrame, artifact: dict[str, Any]) -> tuple[np.ndarray, pd.DataFrame]:
    columns = artifact["feature_contract"]; raw = subgraph_raw_features(nodes, edges, columns)
    x = np.zeros((len(raw), len(columns)), np.float32)
    for node_type, group in raw.groupby("node_type", sort=False):
        stats = artifact["preprocessing_by_node_type"][str(node_type)]
        values = np.log1p(np.maximum(group[columns].to_numpy(float), 0))
        x[group.index] = np.clip((values - np.asarray(stats["median"])) / np.asarray(stats["scale"]), -10, 10)
    key_index = pd.Index(raw.node_key.astype(str)); src = key_index.get_indexer(edges.source_key.astype(str)); dst = key_index.get_indexer(edges.target_key.astype(str))
    relation_map = {name: i for i, name in enumerate(artifact["relation_types"])}
    rel = edges.edge_type.map(relation_map).fillna(-1).to_numpy(int); valid = (src >= 0) & (dst >= 0) & (rel >= 0)
    type_map = {name: i for i, name in enumerate(artifact["node_types"])}; node_types = raw.node_type.map(type_map).to_numpy(int)
    encoder = RelationalGraphSAGEEncoder.from_dict(artifact)
    base = encoder.forward(x, node_types, src[valid].astype(np.int32), dst[valid].astype(np.int32), rel[valid].astype(np.int32))
    return encoder.project(base), raw


def _auc(positive: np.ndarray, negative: np.ndarray) -> float:
    score = np.concatenate([positive, negative]); target = np.concatenate([np.ones(len(positive), bool), np.zeros(len(negative), bool)])
    order = np.argsort(score, kind="stable"); ranks = np.empty(len(order), float); ranks[order] = np.arange(1, len(order) + 1)
    return float((ranks[target].sum() - len(positive) * (len(positive) + 1) / 2) / max(len(positive) * len(negative), 1))


def build_embeddings(graph_dir: Path, artifact_path: Path, config: dict[str, Any]) -> dict[str, Any]:
    features = pd.read_parquet(graph_dir / "node_features.parquet").reset_index(drop=True)
    connectivity = np.load(graph_dir / "connectivity.npz")
    columns = list(config["input_features"]); x, preprocessing = _robust_by_type(features, columns)
    type_names = sorted(features.node_type.unique()); type_map = {name: i for i, name in enumerate(type_names)}
    type_ids = features.node_type.map(type_map).to_numpy(np.int32)
    relation_names = connectivity["relation_names"].astype(str).tolist()
    encoder = RelationalGraphSAGEEncoder(len(columns), len(relation_names), len(type_names), config["embedding_size"], config["layers"], config["random_seed"], config["batch_size"])
    base_embedding = encoder.forward(x, type_ids, connectivity["source"], connectivity["target"], connectivity["relation"])
    rng = np.random.default_rng(config["random_seed"]); total = len(connectivity["source"])
    selected = rng.choice(total, size=min(config["contrastive_training_edges"] + config["contrastive_validation_edges"], total), replace=False)
    train_size = min(config["contrastive_training_edges"], len(selected)); train, validation = selected[:train_size], selected[train_size:]
    losses = encoder.fit_contrastive_projection(base_embedding, connectivity["source"][train], connectivity["target"][train], type_ids,
                                                config["epochs"], config["learning_rate"], config["contrastive_batch_size"], config["l2"])
    embedding = encoder.project(base_embedding)
    validation_auc = None
    if len(validation):
        src, dst = connectivity["source"][validation], connectivity["target"][validation]
        negative = np.empty(len(validation), np.int32)
        for kind in np.unique(type_ids[dst]):
            mask = type_ids[dst] == kind; bucket = np.flatnonzero(type_ids == kind); negative[mask] = rng.choice(bucket, size=int(mask.sum()))
        validation_auc = _auc(np.sum(embedding[src] * embedding[dst], axis=1), np.sum(embedding[src] * embedding[negative], axis=1))
    output = features[["node_key", "node_type"]].copy(); output["embedding"] = list(embedding)
    novelty = np.zeros(len(output), float)
    for _, group in output.groupby("node_type", sort=False):
        values = embedding[group.index]; distance = np.linalg.norm(values - values.mean(axis=0), axis=1)
        novelty[group.index] = pd.Series(distance).rank(method="average", pct=True).to_numpy()
    output["gnn_neighborhood_novelty"] = novelty
    output.to_parquet(graph_dir / "node_embeddings.parquet", index=False)
    artifact = {
        **encoder.to_dict(), "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "feature_contract": columns, "node_types": type_names, "relation_types": relation_names,
        "preprocessing_by_node_type": preprocessing,
        "training": {"method": "self-supervised link contrastive projection over GraphSAGE representations", "epochs": config["epochs"], "labels_used": False, "training_edges": int(len(train)), "loss_by_epoch": losses},
        "evaluation": {"task": "held-out edge versus type-matched negative reconstruction", "validation_edges": int(len(validation)), "roc_auc": validation_auc, "predictive_risk_meaning": False},
        "evaluation_status": "valid for structural link reconstruction only; NOT VALID FOR PREDICTIVE RISK CLAIMS",
        "validity_status": "unsupervised_structural_signal",
        "graph_version": "prysm-financial-graph-v1",
        "data_checksums": {"node_features_sha256": hashlib.sha256((graph_dir / "node_features.parquet").read_bytes()).hexdigest(), "connectivity_sha256": hashlib.sha256((graph_dir / "connectivity.npz").read_bytes()).hexdigest()},
        "configured_parameters": config,
    }
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    with artifact_path.open("w", encoding="utf-8") as handle:
        json.dump(artifact, handle, indent=2, sort_keys=True)
    return {"rows": len(output), "embedding_size": embedding.shape[1], "model_version": encoder.VERSION,
            "labels_used": False, "link_reconstruction_roc_auc": validation_auc, "evaluation_status": artifact["evaluation_status"]}
