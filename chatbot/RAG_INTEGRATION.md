# Prysm RAG integration

Read [PHASE4_STATE.md](../PHASE4_STATE.md) for verification and limitations. The service produces local evidence summaries with optional Gemini selection of general methodology references. Local LLM installation and connection are deferred.

## Run

```powershell
# Repository root, using the existing environment
python chatbot/main.py
python -B -m pytest chatbot/tests -q --tb=short
```

Set `RAG_API_KEY` and `GOOGLE_API_KEYS` (or `GEMINI_API_KEY`) in `chatbot/.env`. `GEMINI_MODEL` / `GEMINI_MODELS` select provider models. No configured key means local fallback. Default binding is `127.0.0.1:8200`. Gemini has at most two attempts with 3-second connect and 8-second read timeouts; these are fixed in the client, not controlled by the old example timeout variable.

## Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /health` | Process, knowledge and provider status; no provider probe |
| `POST /explain` | Internal bearer key; structured Phase 2/3 explanation |
| `GET /ask?message=...` | Public general knowledge |
| `POST /ask` | Internal bearer key; compatible public/investigator interface |
| `POST /ingest` | Internal bearer key; reviewed general knowledge |
| `GET /documents` | Internal bearer key; document metadata |
| `PATCH /documents/{id}?enabled=false` | Internal bearer key; disable retrieval |
| `WS /ws/chat?api_key=...` | Existing internal chat; never expose its key to browsers |

The backend remains responsible for user authorization, resource access and conversation persistence.

## Explain a real result

```python
import json
from pathlib import Path
import requests
from dotenv import dotenv_values

settings = dotenv_values("chatbot/.env")
with Path("ai-engine/runs/evaluation-v3/test_results.jsonl").open(encoding="utf-8") as stream:
    intelligence = json.loads(next(stream))
response = requests.post(
    "http://127.0.0.1:8200/explain",
    headers={"Authorization": "Bearer " + settings["RAG_API_KEY"]},
    json={"intelligence": intelligence, "question": "Explain these findings."},
    timeout=30,
)
response.raise_for_status()
print(response.json()["summary"])
```

Output contains `summary`, unchanged `detected` evidence/assessment, structured `explanation`, and `provenance`. Invalid or mixed-analysis evidence returns 422. Keep the response inside the authorized investigation workflow.

## Knowledge and privacy

Ingest small factual documents with title, content, source, category and version. Source timestamps and SHA-256 hashes make retrieval inspectable. Only reviewed documents explicitly marked `metadata.cloud_approved: true` enter cloud prompts. Do not ingest cases, chat histories, credentials or personal data; marker checks supplement administrative review.

Private evidence and questions stay local in `/explain`. Gemini sees only allowlisted topics and approved general references and returns validated reference IDs. Public questions may go to Gemini and must not contain private investigation data.

[Local setup instructions](local_llm/README.md) explain where weights go and how to import them later. The REST client uses the documented [Gemini generateContent API](https://ai.google.dev/api/generate-content); configured key/model availability remains to be verified live.
