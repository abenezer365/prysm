"""Verify two named benchmark identities without exposing labels to inference."""
from pathlib import Path
import json
import sys

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-engine" / "src"))
sys.path.insert(0, str(ROOT))

from prysm_intelligence.pipeline import load_engine


def main() -> None:
    dataset_path = ROOT / "data" / "benchmarks" / "prysm-benchmark-v1"
    truth = pq.read_table(dataset_path / "ground_truth.parquet").to_pandas()
    people = pq.read_table(dataset_path / "persons.parquet").to_pandas()
    engine = load_engine(
        dataset_path, ROOT / "ai-engine" / "reports" / "phase3" / "model_bundle.json"
    )
    cases = [
        truth[truth.entity_key == "Person:P00640"].iloc[0],
        truth[truth.entity_key == "Person:P01710"].iloc[0],
    ]
    results = []
    for case in cases:
        person_id = case.entity_key.split(":", 1)[1]
        person = people[people.person_id == person_id].iloc[0]
        result = engine.investigate(case.entity_key, case.as_of)
        results.append(
            {
                "ground_truth_id": case.ground_truth_id,
                "entity_key": case.entity_key,
                "name": f"{person.first_name} {person.last_name}",
                "scenario": case.scenario,
                "split": case.split,
                "expected_class": "suspicious" if case.is_suspicious else "non-suspicious",
                "cutoff": case.as_of.isoformat(),
                "attention_strength": result["assessment"]["strength"],
                "risk_level": result["assessment"]["risk_level"],
                "predicted_class": (
                    "suspicious"
                    if result["assessment"]["strength"] is not None
                    and result["assessment"]["strength"] >= engine.config["fusion"]["moderate"]
                    else "non-suspicious"
                ),
                "finding_codes": [
                    finding["code"]
                    for group in (result["findings"]["rules"], result["findings"]["network"])
                    for finding in group
                ],
                "evidence_count": len(result["evidence"]),
                "graph_nodes": len(result["graph"]["nodes"]),
                "graph_edges": len(result["graph"]["edges"]),
                "ground_truth_used_at_inference": result["provenance"][
                    "ground_truth_used_at_inference"
                ],
            }
        )
    print(json.dumps({"dataset_version": engine.dataset.version, "cases": results}, indent=2))


if __name__ == "__main__":
    main()
