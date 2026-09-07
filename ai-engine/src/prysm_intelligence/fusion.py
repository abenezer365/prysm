"""Deterministic weighted attention; unavailable components reduce coverage."""


def fuse(components, config):
    available = {name: c for name, c in components.items() if c["status"] == "available" and c["strength"] is not None}
    weights = config["weights"]
    denominator = sum(weights[name] for name in available)
    breakdown = {name: {"configured_weight": weights[name], "effective_weight": weights[name]/denominator if denominator and name in available else 0.,
                        "strength": c["strength"], "weighted_contribution": weights[name]*c["strength"]/denominator if denominator and name in available else 0.}
                 for name, c in components.items()}
    score = sum(item["weighted_contribution"] for item in breakdown.values()) if denominator else None
    coverage = denominator/sum(weights.values())
    confidence = sum(weights[name]*c["confidence"] for name, c in available.items())/sum(weights.values())
    level = "unavailable" if score is None else "high" if score >= config["high"] else "moderate" if score >= config["moderate"] else "low"
    return {"type": "uncalibrated_attention_assessment", "strength": score, "risk_level": level,
            "is_fraud_probability": False, "confidence": confidence, "coverage": coverage, "breakdown": breakdown}
