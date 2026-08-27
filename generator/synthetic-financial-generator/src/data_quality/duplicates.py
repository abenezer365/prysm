"""Duplicate/near-duplicate injection — approximately 1% of rows."""
from __future__ import annotations

import numpy as np
import polars as pl


def _vary_string(value: str | None, rng: np.random.Generator) -> str | None:
    """Apply minor variations to a string: case change, extra space, etc."""
    if value is None:
        return None
    roll = rng.integers(0, 4)
    if roll == 0:
        return value.upper()
    elif roll == 1:
        return value.lower()
    elif roll == 2:
        return " " + value
    else:
        return value + " "


def inject_duplicates(
    df: pl.DataFrame,
    duplicate_rate: float,
    rng: np.random.Generator,
    string_columns: list[str] | None = None,
) -> pl.DataFrame:
    """
    Select ~duplicate_rate fraction of rows, apply minor string variations,
    and append them to the DataFrame.
    """
    n = len(df)
    n_dups = max(1, int(n * duplicate_rate))
    dup_indices = rng.choice(n, size=n_dups, replace=False).tolist()

    dup_rows = df[dup_indices].to_dicts()

    str_cols = string_columns or [
        c for c, t in zip(df.columns, df.dtypes) if t == pl.Utf8 or t == pl.String
    ]

    for row in dup_rows:
        for col in str_cols:
            if col in row:
                row[col] = _vary_string(row[col], rng)

    dup_df = pl.DataFrame(dup_rows, schema=df.schema)
    return pl.concat([df, dup_df])
