"""Leakage controls and dependency-light evaluation metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd


def temporal_entity_split(features: pd.DataFrame) -> dict[str, np.ndarray]:
    """Forward 60/20/20 split; later repeated-entity rows are purged."""
    ordered = features.sort_values("as_of")
    cut1, cut2 = ordered["as_of"].quantile([0.6, 0.8])
    provisional = np.where(features["as_of"] <= cut1, "train", np.where(features["as_of"] <= cut2, "validation", "test"))
    train = np.flatnonzero(provisional == "train")
    train_entities = set(features.iloc[train]["entity_key"])
    validation = np.flatnonzero((provisional == "validation") & ~features["entity_key"].isin(train_entities).to_numpy())
    prior_entities = train_entities | set(features.iloc[validation]["entity_key"])
    test = np.flatnonzero((provisional == "test") & ~features["entity_key"].isin(prior_entities).to_numpy())
    return {"train": train, "validation": validation, "test": test}


def binary_metrics(y_true: np.ndarray, score: np.ndarray, threshold: float = 0.5) -> dict:
    y = np.asarray(y_true, bool)
    score = np.asarray(score, float)
    pred = score >= threshold
    tp, tn = int(np.sum(y & pred)), int(np.sum(~y & ~pred))
    fp, fn = int(np.sum(~y & pred)), int(np.sum(y & ~pred))
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-15)
    order = np.argsort(-score, kind="stable")
    sy = y[order]
    tps, fps = np.cumsum(sy), np.cumsum(~sy)
    tpr, fpr = tps / max(y.sum(), 1), fps / max((~y).sum(), 1)
    roc_auc = float(np.trapezoid(np.r_[0, tpr, 1], np.r_[0, fpr, 1])) if y.any() and (~y).any() else None
    precision_curve = tps / np.arange(1, len(y) + 1)
    pr_auc = float(np.sum(precision_curve[sy]) / max(y.sum(), 1))
    prevalence = float(y.mean()) if len(y) else 0.0
    return {"rows": len(y), "prevalence": prevalence, "accuracy": (tp + tn) / max(len(y), 1), "precision": precision, "recall": recall, "f1": f1, "roc_auc": roc_auc, "pr_auc": pr_auc, "pr_auc_lift_over_prevalence": pr_auc - prevalence, "confusion_matrix": {"tn": tn, "fp": fp, "fn": fn, "tp": tp}}


def scenario_metrics(scenarios: pd.Series, y_true: np.ndarray, prediction: np.ndarray) -> dict:
    return {
        str(name): {"rows": int(len(group)), "detected": int(np.asarray(prediction)[group.index].sum()), "detection_rate": float(np.asarray(prediction)[group.index].mean())}
        for name, group in pd.DataFrame({"scenario": scenarios.reset_index(drop=True), "target": y_true}).groupby("scenario")
    }
