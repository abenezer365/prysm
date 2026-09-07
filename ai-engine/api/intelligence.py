"""Internal HTTP boundary for the selected Phase 3 engine; no detection logic here."""
from functools import lru_cache
from pathlib import Path
import hmac
import json
import os
import sys
from threading import Lock
from datetime import timedelta

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT.parent))
from prysm_intelligence.pipeline import load_engine, DEFAULT_DATASET
from prysm_intelligence.data import utc

app = FastAPI(title="Prysm Intelligence", version="2.0", docs_url=None, redoc_url=None)
lock = Lock()

def authorize(authorization: str | None = Header(default=None)):
    key = os.getenv("AI_ENGINE_API_KEY", "")
    if not key:
        raise HTTPException(503, "Internal credential is not configured")
    if not hmac.compare_digest(authorization or "", "Bearer " + key):
        raise HTTPException(401, "Invalid internal credential")

@lru_cache(maxsize=1)
def engine():
    return load_engine(Path(os.getenv("PRYSM_DATASET", str(DEFAULT_DATASET))),
                       Path(os.getenv("PRYSM_MODELS", str(ROOT / "reports/phase3/model_bundle.json"))))

def selected_model_path() -> Path:
    return Path(os.getenv("PRYSM_MODELS", str(ROOT / "reports/phase3/model_bundle.json")))

class Investigation(BaseModel):
    class Config:
        extra = "forbid"
    subject: str
    cutoff: str

class Ranking(BaseModel):
    class Config:
        extra = "forbid"
    cutoff: str
    limit: int = 10

def invoke(fn):
    try:
        with lock:
            return fn()
    except KeyError:
        raise HTTPException(404, "Subject does not exist at the requested cutoff")
    except ValueError:
        raise HTTPException(422, "Invalid intelligence request or artifact")
    except (OSError, RuntimeError):
        raise HTTPException(503, "Intelligence artifacts unavailable")

@app.get("/health")
def health():
    return {"status": "ok", "version": "prysm-intelligence-v2"}

@app.get("/ready", dependencies=[Depends(authorize)])
def ready():
    return invoke(lambda: {"status": "ready", "dataset_version": engine().dataset.version})

@app.post("/v2/investigate", dependencies=[Depends(authorize)])
def investigate(body: Investigation):
    def result():
        selected = engine()
        cutoff = utc(body.cutoff)
        if body.subject not in selected.dataset.entities or selected.dataset.entities[body.subject][0] > cutoff:
            raise KeyError(body.subject)
        return selected.investigate(body.subject, cutoff)
    return invoke(result)

@lru_cache(maxsize=8)
def ranked(cutoff):
    selected = engine()
    subjects = [key for key, (created, _) in selected.dataset.entities.items()
                if key.startswith("Person:") and created <= utc(cutoff)]
    return selected.rank(subjects, cutoff, max(1, len(subjects)))

@app.post("/v2/rank", dependencies=[Depends(authorize)])
def rank(body: Ranking):
    if not 1 <= body.limit <= 50:
        raise HTTPException(422, "limit must be between 1 and 50")
    return invoke(lambda: {"population": "all observed people at cutoff", "ranking": ranked(utc(body.cutoff).isoformat())[:body.limit]})

@app.get("/v2/rank/persisted", dependencies=[Depends(authorize)])
def persisted_rank(limit: int = Query(default=10, ge=1, le=50)):
    """Return the selected model run's precomputed ranking without rescoring."""
    def result():
        artifact = selected_model_path().resolve().parent / "top_entities.json"
        payload = json.loads(artifact.read_text(encoding="utf-8"))
        candidates = [row for rows in payload.get("by_split", {}).values() for row in rows]
        if not candidates:
            raise RuntimeError("Persisted ranking artifact is empty")
        latest_cutoff = max(utc(row["cutoff"]) for row in candidates)
        latest = [row for row in candidates if utc(row["cutoff"]) == latest_cutoff]
        latest.sort(key=lambda row: (int(row.get("rank", 10**9)), -float(row.get("overall_risk", 0))))
        ranking, seen = [], set()
        for row in latest:
            if row["entity_key"] in seen:
                continue
            seen.add(row["entity_key"])
            person = engine().dataset.entities.get(row["entity_key"], (None, {}))[1]
            label = " ".join(
                str(person.get(name, "")).strip()
                for name in ("first_name", "last_name")
            ).strip()
            ranking.append({**row, "display_label": label or row["entity_key"]})
            if len(ranking) == limit:
                break
        return {
            "population": payload.get("population", "selected model ranking artifact"),
            "cutoff": latest_cutoff.isoformat(),
            "dataset_version": engine().dataset.version,
            "ranking": ranking,
        }
    return invoke(result)

@app.get("/v2/people/search", dependencies=[Depends(authorize)])
def search(q: str = Query(min_length=2, max_length=200), limit: int = Query(default=20, ge=1, le=50)):
    def result():
        selected = engine()
        rows = []
        for key, (_, person) in sorted(selected.dataset.entities.items()):
            if not key.startswith("Person:"):
                continue
            # Investigation search exposes the population used by the fitted
            # models; relatives and employees remain visible inside graphs.
            if person.get("employment_status") != "Self-employed":
                continue
            label = (str(person["first_name"]) + " " + str(person["last_name"]))
            if q.casefold() in (key + " " + label).casefold():
                seen, pending, latest = {key}, [key], None
                while pending:
                    current = pending.pop()
                    for target, started, _, kind in selected.dataset.links[current]:
                        if kind == "event" and (latest is None or started > latest):
                            latest = started
                        if target not in seen:
                            seen.add(target)
                            pending.append(target)
                analysis_cutoff = None if latest is None else (latest + timedelta(hours=2)).isoformat()
                rows.append({"externalRef": key, "label": label, "status": person.get("employment_status"), "profile": {
                                 "dateOfBirth": person.get("date_of_birth").isoformat() if person.get("date_of_birth") is not None else None,
                                 "gender": person.get("gender"), "occupation": person.get("occupation"),
                                 "employmentStatus": person.get("employment_status"), "city": person.get("city"),
                                 "region": person.get("region"), "country": person.get("country")},
                             "analysisCutoffAt": analysis_cutoff})
        rows.sort(key=lambda row: (row["analysisCutoffAt"] or "", row["label"], row["externalRef"]), reverse=True)
        return {"data": rows[:limit], "total": len(rows), "datasetVersion": selected.dataset.version}
    return invoke(result)
