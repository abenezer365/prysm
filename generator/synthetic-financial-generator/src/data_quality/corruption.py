"""Formatting corruption — random case changes, extra spaces, phone variations."""
from __future__ import annotations

import random

import numpy as np
import polars as pl


def _corrupt_value(value: str | None, rng: np.random.Generator) -> str | None:
    if value is None:
        return None
    roll = rng.integers(0, 5)
    if roll == 0:
        return value.swapcase()
    elif roll == 1:
        return value.replace(" ", "  ")
    elif roll == 2:
        return value.strip().title()
    elif roll == 3:
        return "  " + value.strip()
    else:
        return value  # no change


def apply_formatting_corruption(
    df: pl.DataFrame,
    corruption_rate: float,
    rng: np.random.Generator,
    target_columns: list[str] | None = None,
) -> pl.DataFrame:
    """
    Apply random formatting corruption to a small fraction of string values.
    """
    n = len(df)
    str_cols = target_columns or [
        c for c, t in zip(df.columns, df.dtypes) if t == pl.Utf8 or t == pl.String
    ]

    result = df
    for col in str_cols:
        if col not in result.columns:
            continue
        mask = rng.random(n) < corruption_rate
        if not mask.any():
            continue
        values = result[col].to_list()
        for i in range(n):
            if mask[i]:
                values[i] = _corrupt_value(values[i], rng)
        result = result.with_columns(
            pl.Series(name=col, values=values, dtype=pl.Utf8)
        )

    return result
