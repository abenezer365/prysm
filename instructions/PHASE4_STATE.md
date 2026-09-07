# Phase 4 state — requested scope complete

Evidence-grounded explanations and RAG improvements are implemented. **Local-model download, connection and inference testing are deferred at the user's request.** Gemini supports general-knowledge assistance; private case summaries work locally without an LLM. The original local-LLM acceptance criterion is therefore explicitly deferred.

## Implementation

- `chatbot/reasoning.py` validates Phase 2/3 results, unique evidence IDs and matching analysis fingerprints. Its structured response separates unchanged `detected` evidence/assessment from `explanation` (findings, knowledge, uncertainty, review direction) and `provenance`.
- Protected `POST /explain` accepts `{"intelligence": <engine result>, "question": "..."}`. It summarizes detector evidence locally and never recalculates risk.
- Gemini receives only allowlisted methodology topics and explicitly cloud-approved general references. Structured output selects up to three known reference IDs. Unknown citations, extra fields, malformed output, missing keys and provider failures fall back to local retrieval. Gemini cannot insert case prose into this response.
- Existing `/ask`, ingestion, document management and WebSocket interfaces remain. Legacy investigator context is now summarized locally rather than exported to Gemini. Public questions can use Gemini when all retrieved documents are cloud-approved; otherwise local extracts are returned.
- Ten reviewed methodology documents cover rules, anomaly and graph/network signals. Retrieval reuses the existing local lexical/vector search, computes the query vector once and breaks ties by document ID. No embedding download or vector database was added. Unused sentence-transformers and NumPy dependencies were removed from chatbot requirements.

## Data flow and sovereignty

```text
Phase 3 result → local validation → local evidence summary
                       ↓ allowlisted signal topics
                local knowledge retrieval
                       ↓ approved general references only
                optional Gemini reference selection
                       ↓ validated reference IDs
                structured explanation + unchanged evidence
```

Previously, `chatbot/main.py` appended authorized backend context to the cloud prompt. That path was removed. `server/src/integrations/rag/adapter.ts` still uses the compatible existing API; no backend migration was performed.

For `/explain`, private questions, subjects, transactions, evidence IDs and scores stay local. Generic signal topics can leave the process: this is not zero-egress inference. Documents need `metadata.cloud_approved: true` to enter cloud context. The ten new methodology documents are approved; existing documents were not silently approved.

Internal bearer authentication remains mandatory for protected endpoints. Gemini keys use headers, not URLs; redirects are disabled. Requests have 3-second connect and 8-second read timeouts, with at most two attempts. No private prompt logging or conversation persistence was added. Existing backend retention and WebSocket query-key behavior remain outside this change.

Ingestion is a trusted administrative operation. Known investigation JSON markers are rejected, but this is not comprehensive personal-data detection. Administrators must review knowledge and cloud approval. Public questions themselves may reach Gemini; private questions belong in the protected workflow. Local processing does not establish legal compliance.

## Knowledge and context

Knowledge remains in `chatbot/rag/knowledge_base/*.json`, one small document per retrieval unit. Ingestion records source, version, creation/update time and content SHA-256. Matching title/source updates the current record rather than retaining revision history. Retrieval is reproducible for a fixed corpus; citations expose source, version, IDs and hashes. `/explain` uses at most three references, each capped at 1,800 characters.

The question field is bounded and kept private. Current explanations are extracts of detector findings, not arbitrary conversational reasoning. The response retains an analysis fingerprint for traceability, but that is not a cryptographic authorization check; the backend must provide trusted input.

## Verification

**23 focused tests passed in 9.27 seconds.** Coverage includes health, public/private asks, ingestion, document disabling, WebSocket compatibility, authentication, malformed model output, timeout fallback and captured cloud-payload checks.

The suite sends **all 80 saved Phase 3 test investigations** through `/explain`, covering all eight deterministic suspicious signal types and normal cases. Evidence and assessments remain identical; empty evidence does not manufacture findings. A saved real Phase 2 example supports portable testing; the 80-case check is explicitly skipped if the complete local Phase 3 run is absent.

Gemini success/failure paths were checked with mocked HTTP responses. No live-key validity, local-model inference or hardware performance is claimed. Tests isolate the knowledge directory and internal credential and send no real credentials or cases to a provider.

## Commands and files

From the repository root:

```powershell
python -B -m pytest chatbot/tests -q --tb=short
python chatbot/main.py
```

Configure the existing `chatbot/.env` with `RAG_API_KEY` and your Gemini key/model, using `.env.example`. Default binding is `127.0.0.1:8200`. `/health` reports actual provider state and `localLLM: deferred_by_request`. Read [RAG_INTEGRATION.md](chatbot/RAG_INTEGRATION.md) for the request contract.

Important files: `chatbot/reasoning.py`, `chatbot/main.py`, `chatbot/tests/test_phase4.py`, `chatbot/tests/conftest.py`, and the ten `prysm-method-*.json` knowledge documents.

## Local model later and Phase 5

Follow [the local setup guide](chatbot/local_llm/README.md). Downloaded compatible GGUF **weights** belong at `chatbot/local_llm/weights/model.gguf`, not in the knowledge base. The weights directory is Git-ignored. `Modelfile.example` documents an Ollama import; copying weights does not connect Prysm to that runtime. Hardware inspection was unavailable, so model-size selection and RAM/VRAM verification remain pending. No download or installation was performed.

Continue with `P5_Backend_Cleanup_Finalization.md`: authorize the user/resource, obtain a trusted Phase 3 result, then call `/explain` using the internal credential. Never pass evaluation ground truth or scenario rationales as evidence. The existing AI HTTP service remains on its prior integration until explicitly migrated. No Phase 5/6 work was implemented; Phase 1–3 datasets and models are unchanged.
