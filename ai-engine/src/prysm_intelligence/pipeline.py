"""Reproducible training and raw evaluation hooks; no Phase 3 metric project."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
from time import perf_counter

import numpy as np
import pandas as pd

from . import VERSION
from .anomaly import RobustAnomaly
from .data import Dataset
from .engine import IntelligenceEngine, rank_results
from .features import build_features
from .gnn import RelationalSAGE
from .graph import graph_sample

PROJECT = Path(__file__).resolve().parents[2]
REPO = PROJECT.parent
DEFAULT_CONFIG = PROJECT / "config" / "benchmark_intelligence.json"
DEFAULT_DATASET = REPO / "data" / "benchmarks" / "prysm-benchmark-v1"
DEFAULT_OUTPUT = PROJECT / "runs" / "intelligence-v2"


def json_write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+"\n", encoding="utf-8")


def checksum(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()


def load_config(path=DEFAULT_CONFIG):
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    return validate_config(config)


def validate_config(config):
    if config["version"] != VERSION:
        raise ValueError("Unsupported intelligence configuration version")
    if type(config["seed"]) is not int:
        raise ValueError("seed must be an integer")
    if not 0 < config["observation_days"] < config["history_days"]:
        raise ValueError("History window must be longer than observation window")
    for name in ("max_nodes", "max_transactions", "top_n"):
        if type(config[name]) is not int or config[name] < 1:
            raise ValueError(f"{name} must be a positive integer")
    for section in ("rules", "anomaly", "gnn"):
        if any(type(v) not in (int, float) or not np.isfinite(v) or v <= 0 for v in config[section].values()):
            raise ValueError(f"{section}: parameters must be finite and positive")
    for name in ("hidden_dim", "epochs"):
        if type(config["gnn"][name]) is not int:
            raise ValueError(f"gnn.{name} must be an integer")
    if not 0 < config["anomaly"]["threshold"] <= 1 or not 0 < config["gnn"]["threshold"] <= 1 or not 0 < config["rules"]["structuring_lower_fraction"] < 1:
        raise ValueError("Invalid model/reference threshold")
    weights = config["fusion"]["weights"]
    if set(weights) != {"rules", "anomaly", "network", "gnn"} or any(not np.isfinite(v) or v < 0 for v in weights.values()) or sum(weights.values()) <= 0:
        raise ValueError("Invalid fusion weights")
    if not 0 <= config["fusion"]["moderate"] < config["fusion"]["high"] <= 1:
        raise ValueError("Invalid fusion attention thresholds")
    return config


def train(dataset, observations, config, progress=lambda message: None):
    # This allowlist is the only model-target boundary. Scenario names and
    # evidence/member lists never enter snapshots or model features.
    train_rows = observations.loc[observations.split.eq("train"), ["ground_truth_id", "entity_key", "as_of", "is_suspicious"]].sort_values("ground_truth_id")
    if train_rows.empty or train_rows.entity_key.duplicated().any():
        raise ValueError("Training observations must be nonempty and subject-disjoint")
    progress(f"Building label-free neighborhoods for {len(train_rows)} training observations")
    snapshots = [dataset.snapshot(r.entity_key, r.as_of, config) for r in train_rows.itertuples(index=False)]
    if any(s.truncated for s in snapshots):
        raise ValueError("Cannot train on truncated neighborhoods")
    features = [build_features(s) for s in snapshots]
    labels = train_rows.is_suspicious.to_numpy(bool)
    normal = [f for f, positive in zip(features, labels) if not positive and f.values["history_count"] >= config["anomaly"]["minimum_history"]]
    anomaly = RobustAnomaly(config["anomaly"]).fit(normal)
    samples = [graph_sample(s) for s in snapshots]
    progress("Training all GNN message-passing and readout parameters on the training partition")
    gnn = RelationalSAGE(config["gnn"], config["seed"]).fit(samples, labels)
    provenance = {"training_split": "train", "training_cases": len(train_rows), "training_normal_cases": len(normal),
                  "training_positive_cases": int(labels.sum()), "training_cutoff": max(s.cutoff for s in snapshots).isoformat(),
                  "training_ground_truth_ids": train_rows.ground_truth_id.tolist(), "training_subjects": train_rows.entity_key.tolist(),
                  "labels_used": "GNN binary train labels; anomaly train-normal selection only",
                  "validation_or_test_used_for_fit": False}
    return anomaly, gnn, provenance


def load_engine(dataset_path, bundle_path):
    dataset = Dataset.load(dataset_path)
    bundle = json.loads(Path(bundle_path).read_text(encoding="utf-8"))
    if bundle["version"] != VERSION or bundle["source_manifest_sha256"] != dataset.checksum:
        raise ValueError("Model bundle belongs to a different engine or dataset snapshot")
    validate_config(bundle["config"])
    manifest_path = Path(bundle_path).with_name("MANIFEST.json")
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected = manifest.get("files", {}).get(Path(bundle_path).name, {}).get("sha256")
        if expected and expected != checksum(bundle_path):
            raise ValueError("Model bundle checksum mismatch")
    anomaly, gnn = RobustAnomaly.from_dict(bundle["anomaly"]), RelationalSAGE.from_dict(bundle["gnn"])
    if anomaly.config != bundle["config"]["anomaly"] or gnn.config != bundle["config"]["gnn"] or gnn.seed != bundle["config"]["seed"] or not gnn.fitted:
        raise ValueError("Model bundle configuration/fitted-state mismatch")
    return IntelligenceEngine(dataset, bundle["config"], anomaly, gnn, bundle["training"])


def build(dataset_path=DEFAULT_DATASET, output=DEFAULT_OUTPUT, config_path=DEFAULT_CONFIG, progress=print):
    started = perf_counter()
    output, dataset_path = Path(output), Path(dataset_path)
    if output.exists():
        raise ValueError("Run output already exists; select a fresh --output directory")
    config = load_config(config_path)
    dataset = Dataset.load(dataset_path)
    observations = pd.read_parquet(dataset_path / "ground_truth.parquet")
    training_started = perf_counter()
    anomaly, gnn, training = train(dataset, observations, config, progress)
    training_seconds = perf_counter()-training_started
    engine = IntelligenceEngine(dataset, config, anomaly, gnn, training)
    bundle = {"version": VERSION, "dataset_version": dataset.version, "source_manifest_sha256": dataset.checksum,
              "config": config, "training": training, "anomaly": anomaly.to_dict(), "gnn": gnn.to_dict()}
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".intelligence-", dir=output.parent) as temporary:
        stage = Path(temporary) / "run"
        stage.mkdir()
        json_write(stage / "model_bundle.json", bundle)
        json_write(stage / "config.json", config)
        predictions, by_split = [], {}
        inference_started = perf_counter()
        for split in ("train", "validation", "test"):
            records = observations[observations.split.eq(split)].sort_values("ground_truth_id")
            progress(f"Producing {len(records)} {split} results and evidence; no held-out fitting")
            results = []
            with (stage / f"{split}_results.jsonl").open("w", encoding="utf-8") as stream:
                for row in records.itertuples(index=False):
                    result = engine.investigate(row.entity_key, row.as_of)
                    stream.write(json.dumps(result, sort_keys=True, allow_nan=False)+"\n")
                    results.append(result)
                    predictions.append({"ground_truth_id": row.ground_truth_id, "entity_key": row.entity_key,
                                        "as_of": row.as_of, "split": split, "target": row.is_suspicious,
                                        "scenario": row.scenario, "in_sample": split == "train",
                                        "overall_strength": result["assessment"]["strength"],
                                        **{f"{name}_score": component["strength"] for name, component in result["intelligence_components"].items()}})
            by_split[split] = rank_results(results, config["top_n"])
        pd.DataFrame(predictions).to_parquet(stage / "predictions.parquet", index=False, compression="zstd")
        json_write(stage / "top_entities.json", {"population": "benchmark primary subjects, separately ranked at each split cutoff", "by_split": by_split})
        json_write(stage / "training_report.json", {
            "scope": "training sanity only; formal performance evaluation belongs to Phase 3",
            **training, "gnn_epochs": len(gnn.losses), "first_training_loss": gnn.losses[0], "last_training_loss": gnn.losses[-1],
            "all_message_weights_trained": True, "source_labels_used_in_graph_construction": False,
            "is_fraud_probability": False,
            "timings_seconds": {"training_including_features": training_seconds,
                                "all_observation_inference_and_exports": perf_counter()-inference_started,
                                "build_before_publication": perf_counter()-started},
        })
        json_write(stage / "MANIFEST.json", {"version": VERSION, "dataset_version": dataset.version, "source_manifest_sha256": dataset.checksum,
                    "source_files": {p.name: checksum(p) for p in sorted(Path(__file__).parent.glob("*.py"))},
                    "files": {p.name: {"sha256": checksum(p), "bytes": p.stat().st_size} for p in sorted(stage.iterdir())},
                    "result_contract": "prysm-intelligence-v2", "evaluation_scope": "synthetic retrospective development; formal Phase 3 metrics pending"})
        # Confirm both model reload and strict JSON before exposing the run.
        load_engine(dataset_path, stage / "model_bundle.json")
        stage.rename(output)
    progress(f"Completed {len(predictions)} observations; output: {output}")
    return {"output": str(output), "observations": len(predictions), "training": training}
