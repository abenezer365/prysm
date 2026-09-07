"""Small, explicit binary and ranking metrics; ties share an operating point."""
import numpy as np


def classification(labels, scores, threshold=.5):
    y, s = np.asarray(labels), np.asarray(scores, dtype=float)
    if y.ndim != 1 or s.shape != y.shape or not np.isin(y, [0, 1]).all():
        raise ValueError("Expected equally sized binary labels and scores")
    if not np.isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError("Threshold must be between zero and one")
    if np.isinf(s).any() or ((s[np.isfinite(s)] < 0) | (s[np.isfinite(s)] > 1)).any():
        raise ValueError("Scores must be unavailable (NaN) or between zero and one")
    available = np.isfinite(s)
    y, s = y[available].astype(bool), s[available]
    pred = s >= threshold
    tp, fp = int((pred & y).sum()), int((pred & ~y).sum())
    fn, tn = int((~pred & y).sum()), int((~pred & ~y).sum())
    precision = tp/(tp+fp) if tp+fp else 0.
    recall = tp/(tp+fn) if tp+fn else 0.
    # Group tied scores once: O(n log n), without a quadratic pair matrix.
    positive_count, negative_count = int(y.sum()), int((~y).sum())
    _, groups = np.unique(s, return_inverse=True)
    group_size = np.bincount(groups)
    group_positive = np.bincount(groups, weights=y)
    group_negative = group_size-group_positive
    wins = np.sum(group_positive*(np.cumsum(group_negative)-.5*group_negative))
    auc = float(wins/(positive_count*negative_count)) if positive_count and negative_count else None
    cumulative_precision = np.cumsum(group_positive[::-1])/np.maximum(np.cumsum(group_size[::-1]), 1)
    ap = float(np.sum(group_positive[::-1]*cumulative_precision)/positive_count) if positive_count else None
    return {"threshold": float(threshold), "support": len(y), "unavailable": int((~available).sum()),
            "positives": int(y.sum()), "negatives": int((~y).sum()),
            "confusion": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
            "precision": precision, "recall": recall, "f1": 2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0.,
            "roc_auc": auc, "average_precision": ap}


def ranking(labels, scores, keys, ks=(1, 5, 8, 10, 20)):
    classification(labels, scores)  # Same input contract; no missing-score imputation.
    if len(keys) != len(labels) or len(set(keys)) != len(keys):
        raise ValueError("Ranking requires unique keys matching labels")
    if any(type(k) is not int or k < 1 for k in ks):
        raise ValueError("K must be a positive integer")
    rows = sorted(((float(s), str(key), bool(y)) for y, s, key in zip(labels, scores, keys) if s is not None and np.isfinite(s)), key=lambda r: (-r[0], r[1]))
    positives = int(np.asarray(labels).sum())
    return {str(k): {"returned": min(k, len(rows)), "true_positives": sum(r[2] for r in rows[:k]),
                     "precision": sum(r[2] for r in rows[:k])/min(k, len(rows)) if rows else 0.,
                     "recall": sum(r[2] for r in rows[:k])/positives if positives else 0.} for k in ks}
