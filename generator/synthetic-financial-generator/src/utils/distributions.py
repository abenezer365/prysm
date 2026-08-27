"""Statistical distribution helpers."""
from __future__ import annotations

import numpy as np


def lognormal_income(min_val: int, max_val: int, rng: np.random.Generator) -> int:
    """
    Sample income using lognormal distribution centred at 40% of the range.
    Clamped to [2000, 150_000].
    """
    mid = min_val + (max_val - min_val) * 0.4
    sigma = 0.5
    val = rng.lognormal(mean=np.log(max(mid, 1)), sigma=sigma)
    return int(np.clip(val, 2000, 150_000))


def weighted_choice(items: list, weights: list[float], size: int, rng: np.random.Generator) -> np.ndarray:
    """Vectorised weighted random choice."""
    return rng.choice(items, size=size, p=weights)


def random_date_between(start_ts: float, end_ts: float, rng: np.random.Generator) -> float:
    """Return a random Unix timestamp between start and end."""
    return rng.uniform(start_ts, end_ts)
