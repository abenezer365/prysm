"""Validated, immutable snapshots with physical and logical checksums."""
from __future__ import annotations

import hashlib
import json
import platform
import tempfile
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from .contract import SCHEMAS, VERSION
from .generate import generate
from .validate import require, validate

DEFAULT_CONFIG = Path(__file__).with_name("config.json")
DEFAULT_OUTPUT = Path(__file__).resolve().parents[2] / "data" / "benchmarks" / VERSION


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()


def logical_digest(table):
    payload = json.dumps(table.to_pylist(), default=lambda d: d.isoformat(), sort_keys=True,
                         separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True)+"\n", encoding="utf-8")


def read_snapshot(path):
    path = Path(path)
    manifest = json.loads((path / "MANIFEST.json").read_text(encoding="utf-8"))
    config = json.loads((path / "config.json").read_text(encoding="utf-8"))
    require(manifest["dataset_version"] == VERSION, "manifest: unsupported version")
    require(digest(path / "config.json") == manifest["config_sha256"], "manifest: configuration checksum mismatch")
    require(set(manifest["files"]) == {f"{n}.parquet" for n in SCHEMAS}, "manifest: wrong file inventory")
    require({p.name for p in path.glob("*.parquet")} == set(manifest["files"]), "manifest: unregistered/missing parquet file")
    tables = {}
    for name in SCHEMAS:
        filename = f"{name}.parquet"
        require(digest(path / filename) == manifest["files"][filename]["sha256"], f"{filename}: checksum mismatch")
        table = pq.read_table(path / filename)
        require(logical_digest(table) == manifest["files"][filename]["logical_sha256"] and len(table) == manifest["files"][filename]["rows"], f"{filename}: logical checksum/row count mismatch")
        tables[name] = table
    report = validate(tables, config)
    return tables, config, manifest, report


def build_snapshot(config, output):
    output = Path(output)
    tables = generate(config)
    report = validate(tables, config)
    code = {p.name: digest(p) for p in sorted(Path(__file__).parent.glob("*.py"))}
    if output.exists():
        old, old_config, manifest, _ = read_snapshot(output)
        require(old_config == config and all(logical_digest(old[n]) == logical_digest(tables[n]) for n in tables)
                and manifest["generator_sources"] == code,
                "Snapshot already exists with different data/config/code; choose a new --output directory")
        return report
    output.parent.mkdir(parents=True, exist_ok=True)
    # A failed build never exposes a partially written dataset at the requested path.
    with tempfile.TemporaryDirectory(prefix=".benchmark-", dir=output.parent) as temporary:
        stage = Path(temporary) / "snapshot"
        stage.mkdir()
        files = {}
        for name, table in tables.items():
            path = stage / f"{name}.parquet"
            pq.write_table(table, path, compression="zstd", row_group_size=65536)
            files[path.name] = {"rows": len(table), "sha256": digest(path), "logical_sha256": logical_digest(table)}
        write_json(stage / "config.json", config)
        write_json(stage / "validation_report.json", report)
        write_json(stage / "MANIFEST.json", {
            "dataset_version": VERSION, "generator": "python -m generator.prysm_benchmark generate",
            "generator_sources": code, "seed": config["seed"], "config_sha256": digest(stage / "config.json"),
            "environment": {"python": platform.python_version(), "pyarrow": pa.__version__},
            "files": files, "ground_truth_file": "ground_truth.parquet",
            "evaluation_scope": "synthetic retrospective detection at as_of; not future prediction or real-world fraud efficacy",
            "size_unit": "240 independent cases by default, each with 12 history and 6 observation transactions",
            "split_policy": "chronological, disjoint case people/businesses/accounts; shared institution reference nodes are not case members",
        })
        read_snapshot(stage)
        stage.rename(output)
    return report
