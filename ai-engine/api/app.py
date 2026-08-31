from __future__ import annotations
import hmac
import os
import pandas as pd
from fastapi import Depends, FastAPI, Header, HTTPException, status
from .runtime import ENGINE_VERSION, runtime
from .schemas import AnalyzeResponse, InvestigationContext, PersonSearchResponse

app = FastAPI(title="Prysm AI Engine", version=ENGINE_VERSION, docs_url="/docs" if os.getenv("PRYSM_AI_DOCS", "1") == "1" else None)

def authorize(authorization: str | None = Header(default=None)) -> None:
    key = os.getenv("AI_ENGINE_API_KEY", "")
    if not key: return
    supplied = authorization[7:] if authorization and authorization.startswith("Bearer ") else ""
    if not hmac.compare_digest(supplied, key): raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid internal API credential")

@app.get("/health")
def health() -> dict[str, str]: return {"status": "ok", "service": "prysm-ai-engine", "version": ENGINE_VERSION}

@app.get("/ready")
def ready():
    state = runtime.state()
    if state["status"] != "ready": raise HTTPException(status_code=503, detail=state)
    return state

@app.get("/v1/people/search", response_model=PersonSearchResponse, dependencies=[Depends(authorize)])
def search_people(q: str, limit: int = 20) -> PersonSearchResponse:
    if len(q.strip()) < 2: raise HTTPException(status_code=422, detail="q must contain at least two characters")
    return runtime.search_people(q, min(max(limit, 1), 50))

@app.get("/v1/graph/{external_ref:path}", dependencies=[Depends(authorize)])
def graph(external_ref: str, cutoffAt: str, maxHops: int = 2, maxNodes: int = 100):
    try: return runtime.graph(external_ref, pd.Timestamp(cutoffAt), min(max(maxHops, 1), 3), min(max(maxNodes, 1), 250))
    except KeyError as error: raise HTTPException(status_code=404, detail=str(error)) from error

@app.post("/v1/analyze", response_model=AnalyzeResponse, dependencies=[Depends(authorize)])
def analyze(context: InvestigationContext) -> AnalyzeResponse:
    try: return runtime.analyze(context)
    except (KeyError, ValueError) as error: raise HTTPException(status_code=422, detail=str(error)) from error
