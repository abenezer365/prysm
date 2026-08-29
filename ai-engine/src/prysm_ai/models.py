"""Dependency-light, deterministic intelligence baselines."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class RobustPreprocessor:
    log_columns: tuple[int, ...] = ()
    median_: np.ndarray | None = None
    scale_: np.ndarray | None = None
    fill_: np.ndarray | None = None

    def _prepare(self, x: np.ndarray) -> np.ndarray:
        values = np.asarray(x, dtype=float).copy()
        for column in self.log_columns:
            values[:, column] = np.sign(values[:, column]) * np.log1p(np.abs(values[:, column]))
        return values

    def fit(self, x: np.ndarray) -> "RobustPreprocessor":
        values = self._prepare(x)
        self.fill_ = np.nanmedian(values, axis=0)
        values = np.where(np.isfinite(values), values, self.fill_)
        self.median_ = np.median(values, axis=0)
        q25, q75 = np.percentile(values, [25, 75], axis=0)
        self.scale_ = np.where(q75 - q25 > 1e-9, q75 - q25, 1.0)
        return self

    def transform(self, x: np.ndarray) -> np.ndarray:
        if self.median_ is None or self.scale_ is None or self.fill_ is None:
            raise RuntimeError("Preprocessor is not fitted")
        values = self._prepare(x)
        values = np.where(np.isfinite(values), values, self.fill_)
        return np.clip((values - self.median_) / self.scale_, -20.0, 20.0)

    def to_dict(self) -> dict[str, Any]:
        return {"log_columns": list(self.log_columns), "median": self.median_.tolist(), "scale": self.scale_.tolist(), "fill": self.fill_.tolist()}

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "RobustPreprocessor":
        result = cls(tuple(value["log_columns"]))
        result.median_, result.scale_, result.fill_ = (np.asarray(value[name], float) for name in ("median", "scale", "fill"))
        return result


class LogisticBaseline:
    def __init__(self, learning_rate: float = 0.05, iterations: int = 800, l2: float = 0.01):
        self.learning_rate, self.iterations, self.l2 = learning_rate, iterations, l2
        self.coef_: np.ndarray | None = None
        self.intercept_ = 0.0

    def fit(self, x: np.ndarray, y: np.ndarray) -> "LogisticBaseline":
        x, y = np.asarray(x, float), np.asarray(y, float)
        self.coef_ = np.zeros(x.shape[1])
        positives, negatives = max(y.sum(), 1.0), max(len(y) - y.sum(), 1.0)
        weights = np.where(y == 1, len(y) / (2 * positives), len(y) / (2 * negatives))
        for _ in range(self.iterations):
            logits = np.clip(x @ self.coef_ + self.intercept_, -30, 30)
            error = (1.0 / (1.0 + np.exp(-logits)) - y) * weights
            self.coef_ -= self.learning_rate * ((x.T @ error) / len(y) + self.l2 * self.coef_)
            self.intercept_ -= self.learning_rate * float(error.mean())
        return self

    def predict_proba(self, x: np.ndarray) -> np.ndarray:
        if self.coef_ is None:
            raise RuntimeError("Model is not fitted")
        logits = np.clip(np.asarray(x) @ self.coef_ + self.intercept_, -30, 30)
        return 1.0 / (1.0 + np.exp(-logits))

    def to_dict(self) -> dict[str, Any]:
        return {"algorithm": "regularized_logistic_regression", "learning_rate": self.learning_rate, "iterations": self.iterations, "l2": self.l2, "coef": self.coef_.tolist(), "intercept": self.intercept_}

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "LogisticBaseline":
        result = cls(value["learning_rate"], value["iterations"], value["l2"])
        result.coef_, result.intercept_ = np.asarray(value["coef"], float), float(value["intercept"])
        return result


def _average_path_length(n: int) -> float:
    if n <= 1:
        return 0.0
    if n == 2:
        return 1.0
    return 2.0 * (math.log(n - 1) + 0.5772156649) - 2.0 * (n - 1) / n


class IsolationForestBaseline:
    def __init__(self, trees: int = 64, sample_size: int = 256, contamination: float = 0.1, random_seed: int = 42):
        self.n_trees, self.sample_size, self.contamination, self.random_seed = trees, sample_size, contamination, random_seed
        self.trees_: list[dict[str, Any]] = []
        self.threshold_: float | None = None
        self.fit_sample_size_: int | None = None

    def _tree(self, x: np.ndarray, depth: int, max_depth: int, rng: np.random.Generator) -> dict[str, Any]:
        if depth >= max_depth or len(x) <= 1:
            return {"n": int(len(x))}
        ranges = np.ptp(x, axis=0)
        candidates = np.flatnonzero(ranges > 0)
        if not len(candidates):
            return {"n": int(len(x))}
        feature = int(rng.choice(candidates))
        split = float(rng.uniform(x[:, feature].min(), x[:, feature].max()))
        left = x[:, feature] < split
        if left.all() or (~left).all():
            return {"n": int(len(x))}
        return {"f": feature, "s": split, "l": self._tree(x[left], depth + 1, max_depth, rng), "r": self._tree(x[~left], depth + 1, max_depth, rng)}

    def fit(self, x: np.ndarray) -> "IsolationForestBaseline":
        x = np.asarray(x, float)
        rng = np.random.default_rng(self.random_seed)
        size = min(self.sample_size, len(x))
        self.fit_sample_size_ = size
        max_depth = int(math.ceil(math.log2(max(size, 2))))
        self.trees_ = [self._tree(x[rng.choice(len(x), size=size, replace=False)], 0, max_depth, rng) for _ in range(self.n_trees)]
        self.threshold_ = float(np.quantile(self.score_samples(x), 1.0 - self.contamination))
        return self

    def _path(self, row: np.ndarray, node: dict[str, Any], depth: int = 0) -> float:
        if "f" not in node:
            return depth + _average_path_length(node["n"])
        branch = node["l"] if row[node["f"]] < node["s"] else node["r"]
        return self._path(row, branch, depth + 1)

    def score_samples(self, x: np.ndarray) -> np.ndarray:
        if not self.trees_:
            raise RuntimeError("Model is not fitted")
        normalizer = _average_path_length(self.fit_sample_size_ or self.sample_size) or 1.0
        paths = np.array([[self._path(row, tree) for tree in self.trees_] for row in np.asarray(x, float)])
        return np.power(2.0, -paths.mean(axis=1) / normalizer)

    def predict(self, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        scores = self.score_samples(x)
        return scores, scores >= float(self.threshold_)

    def to_dict(self) -> dict[str, Any]:
        return {"algorithm": "isolation_forest", "trees": self.trees_, "sample_size": self.sample_size, "contamination": self.contamination, "random_seed": self.random_seed, "threshold": self.threshold_}

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "IsolationForestBaseline":
        result = cls(len(value["trees"]), value["sample_size"], value["contamination"], value["random_seed"])
        result.trees_, result.threshold_ = value["trees"], float(value["threshold"])
        result.fit_sample_size_ = value["sample_size"]
        return result
