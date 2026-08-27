"""Polars-based Parquet / CSV I/O helpers."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import polars as pl
import pyarrow as pa
import pyarrow.parquet as pq


def write_parquet(
    df: pl.DataFrame,
    path: Path,
    compression: str = "zstd",
    row_group_size: int = 100_000,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    table = df.to_arrow()
    pq.write_table(
        table,
        str(path),
        compression=compression,
        row_group_size=row_group_size,
    )


def write_parquet_batches(
    records: list[dict],
    path: Path,
    schema: pa.Schema,
    batch_size: int = 10_000,
    compression: str = "zstd",
    row_group_size: int = 100_000,
) -> None:
    """Write records to Parquet in batches to avoid OOM."""
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = None
    try:
        for start in range(0, len(records), batch_size):
            chunk = records[start : start + batch_size]
            batch = pa.RecordBatch.from_pylist(chunk, schema=schema)
            if writer is None:
                writer = pq.ParquetWriter(str(path), schema, compression=compression)
            writer.write_batch(batch)
    finally:
        if writer:
            writer.close()


def write_csv_sample(df: pl.DataFrame, path: Path, n: int = 1000) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sample = df.head(n)
    # Convert list/nested columns to pipe-delimited strings for CSV compatibility
    cast_exprs = []
    for col_name, dtype in zip(sample.columns, sample.dtypes):
        if isinstance(dtype, pl.List):
            # Cast inner elements to str then join with |
            cast_exprs.append(
                pl.col(col_name)
                .list.eval(pl.element().cast(pl.Utf8))
                .list.join("|")
                .alias(col_name)
            )
        elif isinstance(dtype, (pl.Array, pl.Struct)):
            cast_exprs.append(pl.col(col_name).cast(pl.Utf8).alias(col_name))
    if cast_exprs:
        sample = sample.with_columns(cast_exprs)
    sample.write_csv(str(path))


def write_json_report(data: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
