from __future__ import annotations
import hmac
import os
from fastapi import Depends, FastAPI, Header, HTTPException, status
from .runtime import ENGINE_VERSION, runtime
from .schemas import AnalyzeResponse, InvestigationContext

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

@app.post("/v1/analyze", response_model=AnalyzeResponse, dependencies=[Depends(authorize)])
def analyze(context: InvestigationContext) -> AnalyzeResponse:
    try: return runtime.analyze(context)
    except (KeyError, ValueError) as error: raise HTTPException(status_code=422, detail=str(error)) from error
