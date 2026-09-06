"""Robust one-class baseline with exact additive feature contributions."""
import numpy as np

from .features import ANOMALY_FEATURES, vector


class RobustAnomaly:
    VERSION = "robust-behavior-mad-v2"

    def __init__(self, config):
        self.config = config
        self.center = self.scale = None

    def fit(self, features):
        if len(features) < 4:
            raise ValueError("Anomaly fitting needs at least four training-normal observations")
        x = np.asarray([vector(f) for f in features])
        if not np.isfinite(x).all():
            raise ValueError("Anomaly inputs must be finite")
        self.center = np.median(x, axis=0)
        self.scale = np.maximum(1.4826*np.median(abs(x-self.center), axis=0), self.config["scale_floor"])
        return self

    def predict(self, f):
        if self.center is None:
            raise RuntimeError("Anomaly model is not fitted")
        if f.values["history_count"] < self.config["minimum_history"] or not f.values["recent_count"]:
            return {"status": "unavailable", "score": None, "reason": "Insufficient historical or recent behavior", "contributions": []}
        z = np.maximum((vector(f)-self.center)/self.scale, 0.)
        contributions = 1-np.exp(-z/self.config["z_reference"])
        # Top-three average is interpretable and avoids diluting concentrated changes.
        top = np.argsort(-contributions, kind="stable")[:3]
        items = [{"feature": ANOMALY_FEATURES[i], "value": float(f.values[ANOMALY_FEATURES[i]]),
                  "baseline_log_median": float(self.center[i]), "robust_z": float(z[i]),
                  "score_contribution": float(contributions[i]/3), "transaction_ids": f.support[ANOMALY_FEATURES[i]]}
                 for i in top]
        score = sum(item["score_contribution"] for item in items)
        return {"status": "available", "score": score, "flagged": score >= self.config["threshold"],
                "reason": "Mean of three largest one-sided robust feature deviations", "contributions": items}

    def to_dict(self):
        return {"version": self.VERSION, "config": self.config, "features": list(ANOMALY_FEATURES),
                "center": self.center.tolist(), "scale": self.scale.tolist()}

    @classmethod
    def from_dict(cls, value):
        if value["version"] != cls.VERSION or value["features"] != list(ANOMALY_FEATURES):
            raise ValueError("Anomaly artifact feature/version mismatch")
        model = cls(value["config"])
        model.center, model.scale = np.asarray(value["center"]), np.asarray(value["scale"])
        if model.center.shape != (len(ANOMALY_FEATURES),) or model.scale.shape != model.center.shape or not np.isfinite(model.center).all() or not np.isfinite(model.scale).all() or (model.scale <= 0).any():
            raise ValueError("Invalid anomaly artifact parameters")
        return model
