"""Configurable uncalibrated signal combination with separate confidence."""

from __future__ import annotations

from .contracts import SignalComponent


class SignalFusion:
    def __init__(self, config: dict):
        self.weights = config["weights"]
        self.thresholds = config["attention_thresholds"]
        self.minimum_confidence = config["minimum_confidence"]

    def combine(self, components: dict[str, SignalComponent]) -> dict:
        available = {name: item for name, item in components.items() if item.status == "available" and item.strength is not None}
        effective = {name: self.weights.get(name, 0.0) for name in available}
        denominator = sum(effective.values())
        strength = sum(effective[name] * float(item.strength) for name, item in available.items()) / denominator if denominator else None
        configured_weight = sum(self.weights.values()) or 1.0
        coverage = denominator / configured_weight
        evidence_confidence = sum(effective[name] * item.confidence for name, item in available.items()) / denominator if denominator else 0.0
        confidence = evidence_confidence * coverage
        if strength is None:
            tier = "unavailable"
        elif strength < self.thresholds["low"]:
            tier = "minimal"
        elif strength < self.thresholds["moderate"]:
            tier = "low"
        elif strength < self.thresholds["elevated"]:
            tier = "moderate"
        else:
            tier = "elevated"
        return {
            "type": "uncalibrated_attention_assessment", "strength": strength, "tier": tier,
            "is_fraud_probability": False, "weights": effective,
            "confidence": {"score": confidence, "component_coverage": coverage,
                           "status": "sufficient" if confidence >= self.minimum_confidence else "limited"},
        }

