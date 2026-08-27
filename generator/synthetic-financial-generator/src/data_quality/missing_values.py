"""Missing-value injection — applies column-specific null rates to DataFrames."""
from __future__ import annotations

import numpy as np
import polars as pl


def apply_missing_values(
    df: pl.DataFrame,
    column_rates: dict[str, float],
    rng: np.random.Generator,
) -> pl.DataFrame:
    """
    Null out cells according to per-column rates.
    Only nullable columns listed in column_rates are affected.
    """
    n = len(df)
    expressions = []
    for col_name, rate in column_rates.items():
        if col_name not in df.columns:
            continue
        mask = rng.random(n) < rate  # True = set to null
        null_indices = np.where(mask)[0].tolist()
        if not null_indices:
            continue
        # Build a series with nulls at specified positions
        series = df[col_name].to_list()
        for idx in null_indices:
            series[idx] = None
        expressions.append((col_name, series))

    if not expressions:
        return df

    # Rebuild affected columns
    result = df
    for col_name, values in expressions:
        dtype = df[col_name].dtype
        result = result.with_columns(
            pl.Series(name=col_name, values=values, dtype=dtype)
        )
    return result
