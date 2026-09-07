"""Phase 3: validation-only selection, then a frozen synthetic test evaluation.

Run through run_intelligence.py evaluate. Labels live in this module's reports,
never in the investigation response or source-derived graph construction.
"""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
from time import perf_counter

import numpy as np
import pandas as pd

from .gnn import RelationalSAGE
from .graph import graph_sample
from .metrics import classification, ranking
from .pipeline import DEFAULT_DATASET, DEFAULT_OUTPUT, PROJECT, checksum, json_write, load_engine
from .engine import IntelligenceEngine, rank_results

DEFAULT_EVALUATION = PROJECT / "runs" / "evaluation-v3"
DEFAULT_EXPERIMENTS = PROJECT / "config" / "evaluation.json"
SCORES = {"rules": "rules_score", "anomaly": "anomaly_score", "network": "network_score", "gnn": "gnn_score", "fusion": "overall_strength"}


def thresholds(config):
    return {"rules": .5, "network": .5, "anomaly": config["anomaly"]["threshold"],
            "gnn": config["gnn"]["threshold"], "fusion": config["fusion"]["moderate"]}


def measure(frame, config):
    limits = thresholds(config)
    result = {}
    for name, column in SCORES.items():
        result[name] = classification(frame.target, frame[column], limits[name])
        result[name]["ranking"] = ranking(frame.target, frame[column], frame.entity_key, tuple(sorted({1, 5, 8, 10, 20, config["top_n"]})))
    result["fusion_high_tier"] = classification(frame.target, frame.overall_strength, config["fusion"]["high"])
    # Specialists evaluated against their own target plus ALL normal controls.
    for name, scenario in (("family", "family"), ("circular_network", "network")):
        subset = frame[~frame.target | frame.scenario.eq(scenario)]
        result[name] = classification(subset.target, subset[f"{name}_score"], .5)
        result[name]["task"] = f"{scenario} versus all normal controls; other suspicious types excluded"
    result["rules_or_network"] = classification(frame.target, np.maximum(frame.rules_score, frame.network_score), .5)
    # Diagnostic ablation: recompute weighted scores with the remaining weights.
    weights = config["fusion"]["weights"]
    for removed in weights:
        remaining = {k: w for k, w in weights.items() if k != removed}
        score = sum(frame[SCORES[k]].fillna(0)*w for k, w in remaining.items())
        denominator = sum(frame[SCORES[k]].notna()*w for k, w in remaining.items())
        result[f"fusion_without_{removed}"] = classification(frame.target, score/denominator.replace(0, np.nan), limits["fusion"])
    return result


def verify_observations(observations):
    if observations.ground_truth_id.duplicated().any() or observations.entity_key.duplicated().any():
        raise ValueError("Evaluation cases must have unique labels and disjoint subjects")
    if set(observations.split) != {"train", "validation", "test"}:
        raise ValueError("Expected train, validation and test partitions")
    windows = []
    for split in ("train", "validation", "test"):
        rows = observations[observations.split.eq(split)]
        if set(rows.is_suspicious) != {False, True}:
            raise ValueError("Each split must contain both classes")
        windows.append((pd.to_datetime(rows.as_of).min(), pd.to_datetime(rows.as_of).max()))
    if not windows[0][1] < windows[1][0] or not windows[1][1] < windows[2][0]:
        raise ValueError("Partition cutoffs must be chronological and nonoverlapping")


def frame_from_results(rows, results):
    records = []
    for row, result in zip(rows.itertuples(index=False), results):
        if result["subject"]["entity_key"] != row.entity_key or pd.Timestamp(result["investigation_window"]["cutoff"]) != pd.Timestamp(row.as_of):
            raise ValueError("Prediction/ground truth identity or cutoff mismatch")
        leads = result["findings"]["network"]
        records.append({"ground_truth_id": row.ground_truth_id, "entity_key": row.entity_key, "as_of": row.as_of,
                        "split": row.split, "target": bool(row.is_suspicious), "scenario": row.scenario,
                        "overall_strength": result["assessment"]["strength"],
                        **{f"{name}_score": c["strength"] for name, c in result["intelligence_components"].items()},
                        "family_score": max((v["strength"] for v in leads if v["code"] == "FAMILY_PASS_THROUGH"), default=0.) if result["intelligence_components"]["network"]["status"] == "available" else None,
                        "circular_network_score": max((v["strength"] for v in leads if v["code"] == "RAPID_CIRCULAR_FLOW"), default=0.) if result["intelligence_components"]["network"]["status"] == "available" else None})
    if len(records) != len(rows) or len(results) != len(rows):
        raise ValueError("Missing or duplicate predictions")
    return pd.DataFrame(records)


def failures(frame, config, results):
    by_key = {r["subject"]["entity_key"]: r for r in results}
    records = []
    explanations = {
        "rules": "Six explicit checks do not cover family/circular routing; network analysis supplies that evidence.",
        "network": "Temporal paths target circular/family flows; individual amount, geography, tax and device cases need other components.",
        "anomaly": "Generic deviation is not suspicious intent: normal controls overlap; top-three averaging can dilute a single strong feature.",
        "gnn": "Only eight positive training cases. Aggregate graph features omit rule-specific transaction-purpose, declaration and travel semantics.",
        "fusion": "Weighted averaging and the review threshold can dilute a specialist signal; inspect the complete breakdown."}
    for row in frame.itertuples(index=False):
        result = by_key[row.entity_key]
        for name, column in SCORES.items():
            score, threshold = getattr(row, column), thresholds(config)[name]
            if not pd.notna(score):
                kind = "unavailable"
                score = None
            elif bool(score >= threshold) == row.target:
                continue
            else:
                kind = "false_negative" if row.target else "false_positive"
            interpretation = explanations[name]
            if name == "gnn" and row.scenario == "asset_sale" and kind == "false_positive":
                interpretation = (f"Normal asset-sale context: amount/history ratio {result['features']['amount_to_history']:.1f}; "
                                  "the graph encodes amount and history but not transaction purpose. The explicit amount rule uses that purpose and does not flag this case.")
            records.append({"split": row.split, "entity_key": row.entity_key, "scenario": row.scenario,
                            "target": row.target, "component": name, "error": kind, "score": score, "threshold": threshold,
                            "interpretation": result["intelligence_components"].get(name, {}).get("reason", "No available component scores") if kind == "unavailable" else interpretation, "interpretation_status": "feature/coverage diagnosis, not causal proof",
                            "features": result["features"], "score_breakdown": result["assessment"]["breakdown"],
                            "evidence_ids": [e["evidence_id"] for e in result["evidence"]]})
    return records


def select_trial(trials):
    """No test argument: F1, average precision, then fewer parameters/epochs."""
    if not trials:
        raise ValueError("No validation trials")
    return max(trials, key=lambda t: (t["validation"]["f1"], t["validation"]["average_precision"],
                                      -t["parameters"], -t["config"]["epochs"], -abs(t["threshold"]-.65), t["name"]))


def evaluate(dataset_path=DEFAULT_DATASET, baseline=DEFAULT_OUTPUT, output=DEFAULT_EVALUATION,
             experiments_path=DEFAULT_EXPERIMENTS, top_n=10, progress=print):
    started = perf_counter()
    dataset_path, baseline, output = Path(dataset_path), Path(baseline), Path(output)
    if output.exists():
        raise ValueError("Evaluation output exists; select a fresh --output")
    if type(top_n) is not int or top_n < 1:
        raise ValueError("top_n must be a positive integer")
    plan = json.loads(Path(experiments_path).read_text(encoding="utf-8"))
    if not plan["candidates"] or len({c["name"] for c in plan["candidates"]}) != len(plan["candidates"]):
        raise ValueError("Experiment names must be unique and nonempty")
    if any(not 0 < t <= 1 for t in plan["gnn_thresholds"]):
        raise ValueError("Invalid experiment threshold")
    engine = load_engine(dataset_path, baseline / "model_bundle.json")
    observations = pd.read_parquet(dataset_path / "ground_truth.parquet")
    verify_observations(observations)
    partitions = {s: observations[observations.split.eq(s)].sort_values("ground_truth_id") for s in ("train", "validation", "test")}
    if set(engine.model_provenance["training_ground_truth_ids"]) != set(partitions["train"].ground_truth_id):
        raise ValueError("Baseline was not fitted on exactly this training partition")
    # Verify the prior run before using any stored validation results.
    manifest = json.loads((baseline / "MANIFEST.json").read_text(encoding="utf-8"))
    for filename in ("model_bundle.json", "validation_results.jsonl"):
        if checksum(baseline / filename) != manifest["files"][filename]["sha256"]:
            raise ValueError(f"Baseline checksum mismatch: {filename}")
    baseline_results = [json.loads(line) for line in (baseline / "validation_results.jsonl").read_text(encoding="utf-8").splitlines()]
    baseline_frame = frame_from_results(partitions["validation"], baseline_results)
    baseline_metrics = measure(baseline_frame, engine.config)
    progress("Baseline validation measured; caching source-only train/validation graphs once")
    samples = {split: [graph_sample(engine.dataset.snapshot(r.entity_key, r.as_of, engine.config)) for r in partitions[split].itertuples(index=False)] for split in ("train", "validation")}
    labels = {s: partitions[s].is_suspicious.to_numpy(bool) for s in samples}
    curves, trials, models = [], [], {}
    for candidate in plan["candidates"]:
        config = {**engine.config["gnn"], **candidate["changes"]}
        from .pipeline import validate_config
        validate_config({**engine.config, "gnn": config})
        progress(f"Training {candidate['name']}: {config}")
        def observe(model, epoch):
            for split in ("train", "validation"):
                logits = np.asarray([model._forward(s)[0] for s in samples[split]])
                scores = 1/(1+np.exp(-np.clip(logits, -40, 40)))
                m = classification(labels[split], scores, config["threshold"])
                curves.append({"experiment": candidate["name"], "epoch": epoch, "split": split,
                               "bce": float(np.mean(np.logaddexp(0, logits)-labels[split]*logits)),
                               **{k: m[k] for k in ("precision", "recall", "f1")}})
        fit_start = perf_counter()
        model = RelationalSAGE(config, engine.config["seed"]).fit(samples["train"], labels["train"], observe)
        seconds = perf_counter()-fit_start
        models[candidate["name"]] = model
        scores = [model.predict(s) for s in samples["validation"]]
        for threshold in plan["gnn_thresholds"]:
            trials.append({"name": candidate["name"], "config": config, "threshold": threshold,
                           "parameters": sum(v.size for v in model.parameters.values()), "fit_seconds": seconds,
                           "validation": classification(labels["validation"], scores, threshold)})
    selected = select_trial(trials)
    config = deepcopy(engine.config)
    config["gnn"] = {**selected["config"], "threshold": selected["threshold"]}
    config["top_n"] = top_n
    model = models[selected["name"]]
    model.config = config["gnn"]
    progress(f"Selected {selected['name']} at threshold {selected['threshold']}; checking a second training seed on validation")
    stability = RelationalSAGE(config["gnn"], engine.config["seed"]+1).fit(samples["train"], labels["train"])
    stability_metrics = classification(labels["validation"], [stability.predict(s) for s in samples["validation"]], config["gnn"]["threshold"])
    training = {**engine.model_provenance, "selection_split": "validation", "evaluation_phase": 3,
                "test_used_for_selection": False, "selected_experiment": selected["name"]}
    selected_engine = IntelligenceEngine(engine.dataset, config, engine.anomaly, model, training)
    bundle = {"version": engine.config["version"], "dataset_version": engine.dataset.version,
              "source_manifest_sha256": engine.dataset.checksum, "config": config, "training": training,
              "anomaly": engine.anomaly.to_dict(), "gnn": model.to_dict()}
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".evaluation-", dir=output.parent) as temporary:
        stage = Path(temporary) / "run"
        stage.mkdir()
        json_write(stage / "selection.json", {"policy": "Validation F1, then AP, then fewer parameters/epochs; threshold tie nearest original .65. Test is excluded.",
                   "selected": selected, "trials": trials, "seed_stability": {"seed": engine.config["seed"]+1, "validation": stability_metrics},
                   "fixed_components": "Rule/network logic, anomaly fit/threshold and fusion weights unchanged. Graph-activity availability fixes quiet personal accounts with active business neighborhoods."})
        json_write(stage / "experiment_plan.json", plan)
        json_write(stage / "model_bundle.json", bundle)
        json_write(stage / "config.json", config)
        json_write(stage / "baseline_validation.json", baseline_metrics)
        all_failures = failures(baseline_frame, engine.config, baseline_results)
        for f in all_failures:
            f["run"] = "baseline"
        metrics, rankings, frames = {}, {}, []
        latencies = []
        for split, rows in partitions.items():
            progress(f"Frozen configuration: scoring {len(rows)} {split} cases with full evidence")
            results = []
            with (stage / f"{split}_results.jsonl").open("w", encoding="utf-8") as stream:
                for row in rows.itertuples(index=False):
                    t = perf_counter()
                    result = selected_engine.investigate(row.entity_key, row.as_of)
                    latencies.append(perf_counter()-t)
                    results.append(result)
                    stream.write(json.dumps(result, allow_nan=False, sort_keys=True)+"\n")
            frame = frame_from_results(rows, results)
            frames.append(frame)
            metrics[split] = measure(frame, config)
            metrics[split]["by_scenario"] = {s: {name: classification(g.target, g[column], thresholds(config)[name]) for name, column in SCORES.items()} for s, g in frame.groupby("scenario")}
            errors = failures(frame, config, results)
            for f in errors:
                f["run"] = "selected"
            all_failures.extend(errors)
            by_key = {r["subject"]["entity_key"]: r for r in results}
            truth = frame.set_index("entity_key")
            rankings[split] = [{**r, "ground_truth": {"suspicious": bool(truth.loc[r["entity_key"], "target"]), "scenario": truth.loc[r["entity_key"], "scenario"]},
                                "supporting_evidence": by_key[r["entity_key"]]["evidence"]} for r in rank_results(results, top_n)]
        frame = pd.concat(frames, ignore_index=True)
        frame.to_parquet(stage / "predictions.parquet", index=False)
        json_write(stage / "metrics.json", metrics)
        json_write(stage / "failures.json", all_failures)
        pd.DataFrame([{k: v for k, v in f.items() if k not in {"features", "score_breakdown", "evidence_ids"}} for f in all_failures]).to_csv(stage / "failures.csv", index=False)
        json_write(stage / "rankings.json", {"evaluation_only": True, "population": "80 benchmark primary subjects per split, not all people", "top_n": top_n, "by_split": rankings})
        pd.DataFrame(curves).to_csv(stage / "training_curves.csv", index=False)
        timing = {"end_to_end_seconds_before_plots": perf_counter()-started, "investigation_median_ms": float(np.median(latencies)*1000),
                  "investigation_p95_ms": float(np.percentile(latencies, 95)*1000), "observations": len(frame), "includes_evidence": True}
        json_write(stage / "timings.json", timing)
        from .evaluation_plots import plot_evaluation
        plot_evaluation(stage, frame, pd.DataFrame(curves), metrics, selected)
        write_report(stage, metrics, baseline_metrics, selected, stability_metrics, timing)
        json_write(stage / "MANIFEST.json", {"phase": 3, "source_manifest_sha256": engine.dataset.checksum,
                   "baseline_bundle_sha256": checksum(baseline / "model_bundle.json"), "experiment_plan_sha256": checksum(experiments_path),
                   "source_files": {p.name: checksum(p) for p in sorted(Path(__file__).parent.glob("*.py"))},
                   "files": {p.relative_to(stage).as_posix(): {"sha256": checksum(p), "bytes": p.stat().st_size} for p in sorted(stage.rglob("*")) if p.is_file()},
                   "reproducibility": "Fixed seed and inputs reproduce scores; wall-clock timings vary.",
                   "limitations": "Synthetic development benchmark reused during Phase 2; this is not a pristine external holdout or national-scale proof."})
        reloaded = load_engine(dataset_path, stage / "model_bundle.json")
        if reloaded.gnn.predict(samples["validation"][0]) != model.predict(samples["validation"][0]):
            raise ValueError("Model reload changed predictions")
        stage.rename(output)
    progress(f"Phase 3 complete: {output}")
    return {"output": str(output), "selected": selected["name"], "test": metrics["test"]}


def write_report(stage, metrics, baseline, selected, stability, timing):
    lines = ["# Phase 3 measured evaluation", "", "Synthetic retrospective primary-subject classification: 80 cases per split, 72 normal and 8 suspicious. Train fits models; validation selects configuration; the frozen configuration then scores test. The benchmark was already used during Phase 2 development, so test is not a pristine external holdout.", "",
             "## Results", "", "| Split | Component | Scored / 80 | Unavailable | Precision | Recall | F1 | FP | FN | ROC AUC | Average precision |", "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for split in ("validation", "test"):
        for name in SCORES:
            m = metrics[split][name]
            lines.append(f"| {split} | {name} | {m['support']} | {m['unavailable']} | {m['precision']:.3f} | {m['recall']:.3f} | {m['f1']:.3f} | {m['confusion']['fp']} | {m['confusion']['fn']} | {m['roc_auc']:.3f} | {m['average_precision']:.3f} |")
    lines += ["", "## Selection and limitations", "", f"Selected **{selected['name']}**, {selected['parameters']} parameters, {selected['config']['epochs']} epochs, learning rate {selected['config']['learning_rate']}, GNN threshold {selected['threshold']}. Baseline validation GNN F1 was {baseline['gnn']['f1']:.3f}; selected F1 is {selected['validation']['f1']:.3f}. Second-seed validation F1 is {stability['f1']:.3f}; inspect selection.json before claiming stability.", "",
              "Rule/network detection logic, anomaly fitting/threshold and fusion weights remain unchanged. A measured availability bug was fixed: nine normal business-trading cases per split have recent business activity but quiet personal accounts. Rules/network/GNN now use graph activity for availability; personal-behavior anomaly correctly remains unavailable for those nine cases. Previous stored Phase 2 results excluded them from all component scores.", "",
              "Family/circular specialists each detect their one positive against 72 normal controls. Rules OR network also matches fusion on this designed benchmark. Removing the GNN from the fixed weighted fusion misses two cases, but that does not establish incremental value over a simpler rules-OR-network decision. Keep these two comparisons distinct.", "",
              "See failures.csv for exact errors and failures.json for their features and evidence. All selected validation/test GNN false positives are normal asset sales: graph aggregates capture their large amounts but omit transaction purpose. The amount rule already uses that purpose and correctly stays quiet. Generic anomaly deviation overlaps normal behavior and averaging dilutes isolated changes; seven suspicious cases per split remain below its conservative threshold. Feature diagnoses are interpretations, not causal experiments. Eight positive training cases are too few to establish broad generalization. No new model or label-derived feature was added.", "",
              "Fusion moderate threshold is the review operating point; the high tier is a separate stricter queue, not the sole positive prediction. Scores and confidence are uncalibrated and do not establish guilt. Each suspicious scenario has only one validation and one test example; one error changes overall recall by 12.5 percentage points.", "",
              "## Reading the artifacts", "", "- metrics.json: all components, specialist tasks, per-scenario results, removal ablations and precision/recall@K.", "- selection.json / experiment_plan.json: fixed controlled trials and validation-only selection.", "- training_curves.csv / figures/: post-update unweighted train/validation BCE and classification metrics every 10 epochs (plus first/last); fitting itself uses balanced BCE plus L2, full batch of 80.", "- rankings.json: configurable Top N with evaluation-only ground truth and complete supporting evidence. Raw *_results.jsonl contain no ground truth.", "- model_bundle.json / config.json / MANIFEST.json: reloadable selected model, provenance and checksums.", "",
              f"Measured full-investigation latency: median {timing['investigation_median_ms']:.1f} ms, p95 {timing['investigation_p95_ms']:.1f} ms on this local run; includes graph/evidence and is not a production throughput claim. Graph samples are cached across experiments to avoid repeated feature extraction.", "",
              "ROC AUC counts tied positive/negative pairs as half. Average precision uses recall increments at grouped score thresholds (not trapezoidal PR area). Undefined AUC/AP is null; no-prediction precision is zero. Missing component scores are excluded from component metrics and counted as unavailable. Ranking breaks ties by entity key; precision@K divides by returned count, recall@K includes all target positives.", "",
              "## Phase 4 boundary", "", "Load this model bundle through prysm_intelligence.pipeline.load_engine, then call investigate(subject, cutoff). Pass the evidence-backed result to later explanation work. Do not pass ground-truth labels, evaluation ranks or scenario rationales to an LLM. Existing API remains on the archived v1 integration until explicitly migrated. No Phase 4 implementation is included.", ""]
    (stage / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
