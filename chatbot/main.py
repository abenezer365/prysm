from __future__ import annotations

import json
import math
import os
import re
import hmac
import uuid
from collections import Counter
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel, Field

load_dotenv()

APP_ROOT = Path(__file__).resolve().parent
KNOWLEDGE_DIR = APP_ROOT / "rag" / "knowledge_base"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class GeminiKeyManager:
    def __init__(self) -> None:
        self.keys = [key.strip() for key in os.getenv("GOOGLE_API_KEYS", "").split(",") if key.strip()]
        default_models = ["gemini-3.5-flash", "gemini-3.5-flash-lite"]
        self.models = [
            model.strip()
            for model in os.getenv("GEMINI_MODELS", os.getenv("GEMINI_MODEL", ",".join(default_models))).split(",")
            if model.strip()
        ]
        if not self.models:
            self.models = default_models
        self.current_index = 0
        self.model_index = 0
        self.api_base = os.getenv("GEMINI_API_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/models")

    @property
    def active_key(self) -> str:
        if not self.keys:
            raise RuntimeError("No Google API keys configured")
        return self.keys[self.current_index]

    @property
    def active_model(self) -> str:
        if not self.models:
            return "gemini-3.5-flash"
        return self.models[self.model_index % len(self.models)]

    def rotate_key(self) -> str:
        if not self.keys:
            raise RuntimeError("No Google API keys configured")
        self.current_index = (self.current_index + 1) % len(self.keys)
        self.model_index = (self.model_index + 1) % len(self.models)
        return self.active_key

    def get_request_options(self) -> dict[str, str]:
        if not self.keys:
            raise RuntimeError("No Google API keys configured")
        return {
            "api_key": self.active_key,
            "model": self.active_model,
            "base_url": self.api_base,
        }


class LightweightEmbedder:
    def __init__(self) -> None:
        self.vocab: list[str] = []
        self.index: dict[str, int] = {}

    def tokenize(self, text: str) -> list[str]:
        return re.findall(r"[a-z0-9]+", text.lower())

    def fit(self, texts: list[str]) -> None:
        tokens = sorted({token for text in texts for token in self.tokenize(text)})
        self.vocab = tokens
        self.index = {token: idx for idx, token in enumerate(tokens)}

    def encode(self, text: str) -> list[float]:
        counts = Counter(self.tokenize(text))
        vector = [0.0] * len(self.vocab)
        for token, count in counts.items():
            if token in self.index:
                vector[self.index[token]] = float(count)
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]


class DocumentIngest(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    source: str = Field(default="manual")
    category: str = Field(default="concepts")
    version: str = Field(default="1.0")
    metadata: dict[str, Any] = Field(default_factory=dict)


class AskRequest(BaseModel):
    message: str = Field(..., min_length=1)
    authenticated: bool = False
    userId: str | None = None
    subjectId: str | None = None
    investigationId: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)


class KnowledgeStore:
    def __init__(self, root: Path):
        self.root = root
        self.documents: list[dict[str, Any]] = []
        self.embedder = LightweightEmbedder()
        self._load_persisted()
        self._ensure_seed_data()

    def _load_persisted(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        for file_path in sorted(self.root.glob("*.json")):
            try:
                record = json.loads(file_path.read_text(encoding="utf-8"))
                record.setdefault("enabled", True)
                record.setdefault("embedding", [])
                self.documents.append(record)
            except (OSError, ValueError, TypeError):
                continue
        if self.documents:
            self._update_vocab()

    def _ensure_seed_data(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        seed_documents = [
            {
                "title": "Prysm AI",
                "content": "Prysm AI is a financial intelligence platform that combines behavioral signals, graph analysis, explainable investigation workflows, and operational data. It helps investigators understand patterns while keeping decisions anchored in evidence and transparent methodology.",
                "source": "platform",
                "category": "platform",
                "version": "1.0",
                "metadata": {"domain": "platform"},
            },
            {
                "title": "Rapid Outflow",
                "content": "Rapid outflow is a short-duration pattern of unusually fast movement of funds away from a source account or entity. It is a behavioral indicator that may require deeper review, but it is not proof of fraud or criminal conduct.",
                "source": "methodology",
                "category": "concepts",
                "version": "1.0",
                "metadata": {"domain": "financial-intelligence"},
            },
            {
                "title": "Structuring",
                "content": "Structuring involves dividing a large transaction or related activity into smaller pieces to obscure its origin or purpose. It is a compliance concern that may trigger review under applicable rules, but the system should always explain findings with evidence and restrained language.",
                "source": "methodology",
                "category": "concepts",
                "version": "1.0",
                "metadata": {"domain": "financial-intelligence"},
            },
            {
                "title": "Investigator Guidance",
                "content": "Investigators should use AI output as decision support instead of final legal conclusion. Evidence, context, and human judgment remain essential. The system should explain what triggered a rule, what evidence supports it, and what limitations exist.",
                "source": "guidance",
                "category": "limitations",
                "version": "1.0",
                "metadata": {"domain": "investigator-guidance"},
            },
        ]
        if not self.documents:
            for item in seed_documents:
                self.add_document(item, persist=False)

    def _update_vocab(self) -> None:
        texts = [doc["content"] for doc in self.documents]
        if texts:
            self.embedder.fit(texts)
            for doc in self.documents:
                doc["embedding"] = self.embedder.encode(doc["content"])

    def add_document(self, payload: dict[str, Any], persist: bool = True) -> dict[str, Any]:
        doc_id = str(uuid.uuid4())
        content = payload["content"].strip()
        record = {
            "id": doc_id,
            "title": payload["title"],
            "content": content,
            "source": payload.get("source", "manual"),
            "category": payload.get("category", "concepts"),
            "version": payload.get("version", "1.0"),
            "createdAt": _now_iso(),
            "metadata": payload.get("metadata", {}),
            "enabled": True,
            "embedding": [],
        }
        self.documents.append(record)
        self._update_vocab()
        if persist:
            self._persist_record(record)
        return record

    def _persist_record(self, record: dict[str, Any]) -> None:
        file_path = self.root / f"{record['id']}.json"
        file_path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        available = [document for document in self.documents if document.get("enabled", True)]
        if not available:
            return []

        query_text = query.lower()
        query_tokens = set(re.findall(r"[a-z0-9]+", query_text))
        if not query_tokens:
            return available[:limit]

        scored: list[tuple[float, dict[str, Any]]] = []
        for doc in available:
            text = (doc["title"] + " " + doc["content"]).lower()
            title_text = doc["title"].lower()
            title_tokens = set(re.findall(r"[a-z0-9]+", title_text))
            content_tokens = set(re.findall(r"[a-z0-9]+", doc["content"].lower()))

            overlap = len(query_tokens & content_tokens)
            title_overlap = len(query_tokens & title_tokens)
            exact_phrase_bonus = 1.0 if query_text in text else 0.0
            title_phrase_bonus = 2.0 if query_text in title_text else 0.0
            boost = title_overlap * 2.0 + title_phrase_bonus + exact_phrase_bonus

            doc_vector = doc.get("embedding") or []
            query_vector = self.embedder.encode(query)
            similarity = 0.0
            if doc_vector and query_vector:
                numerator = sum(a * b for a, b in zip(query_vector, doc_vector))
                norm_q = math.sqrt(sum(v * v for v in query_vector))
                norm_d = math.sqrt(sum(v * v for v in doc_vector))
                if norm_q and norm_d:
                    similarity = numerator / (norm_q * norm_d)

            score = boost + similarity + (overlap * 0.15)
            scored.append((score, doc))

        scored.sort(key=lambda item: item[0], reverse=True)
        top = [doc for _, doc in scored[:limit]]
        if not top:
            return available[:limit]
        return top

    def list_documents(self) -> list[dict[str, Any]]:
        return [{key: value for key, value in document.items() if key not in {"content", "embedding"}} for document in self.documents]

    def set_enabled(self, document_id: str, enabled: bool) -> dict[str, Any] | None:
        for document in self.documents:
            if document["id"] == document_id:
                document["enabled"] = enabled
                file_path = self.root / f"{document_id}.json"
                if file_path.exists():
                    self._persist_record(document)
                self._update_vocab()
                return {key: value for key, value in document.items() if key not in {"content", "embedding"}}
        return None


class GeminiClient:
    def __init__(self, key_manager: GeminiKeyManager):
        self.key_manager = key_manager
        self.provider_status = "not_configured" if not key_manager.keys else "configured_not_verified"
        self.last_failure: str | None = None

    def _fallback_answer(self, question: str, context: str, mode: str) -> str:
        if mode == "investigator":
            return (
                "The available evidence points to an investigation context that should be reviewed by the authorized team. "
                "The system detected a rule or pattern in the provided backend context, and the relevant explanation should be grounded in the supplied signals and source material."
            )

        content_matches = []
        for line in context.splitlines():
            if line.strip().lower().startswith("content:"):
                content_matches.append(line.split(":", 1)[1].strip())

        if content_matches:
            snippet = content_matches[0]
            if len(snippet) > 220:
                snippet = snippet[:217].rstrip() + "..."
            return f"Based on the retrieved knowledge, the answer is: {snippet}"

        title_matches = []
        for line in context.splitlines():
            if line.strip().lower().startswith("title:"):
                title_matches.append(line.split(":", 1)[1].strip())
        if title_matches:
            return f"Based on the retrieved knowledge, the answer is best explained by the document titled '{title_matches[0]}'."

        return "The knowledge base and available context indicate that this question should be answered using the retrieved evidence and the system's documented guidance."

    def _build_prompt(self, question: str, context: str, mode: str) -> str:
        return (
            "Use cautious, evidence-based language. Do not claim fraud, criminal guilt, or certainty beyond the provided evidence. "
            f"Mode: {mode}. Question: {question}. Context:\n{context}\n\nAnswer concisely and explain with the available sources."
        )

    def generate(self, question: str, context: str, mode: str = "public") -> str:
        if not self.key_manager.keys:
            self.provider_status = "not_configured"
            return self._fallback_answer(question, context, mode)

        try:
            import requests
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("requests package required") from exc

        max_attempts = max(1, len(self.key_manager.keys) * max(1, len(self.key_manager.models)))
        for _ in range(max_attempts):
            config = self.key_manager.get_request_options()
            url = f"{config['base_url']}/{config['model']}:generateContent?key={config['api_key']}"
            payload = {
                "contents": [{"parts": [{"text": self._build_prompt(question, context, mode)}]}],
                "generationConfig": {"maxOutputTokens": 512},
            }
            try:
                response = requests.post(url, json=payload, timeout=30)
            except requests.RequestException as exc:
                self.provider_status = "degraded"
                self.last_failure = type(exc).__name__
                self.key_manager.rotate_key()
                continue

            if response.status_code in {400, 403, 404, 429}:
                self.provider_status = "degraded"
                self.last_failure = f"HTTP_{response.status_code}"
                self.key_manager.rotate_key()
                continue

            if response.status_code != 200:
                self.provider_status = "degraded"
                self.last_failure = f"HTTP_{response.status_code}"
                self.key_manager.rotate_key()
                continue

            body = response.json()
            candidates = body.get("candidates") or []
            if not candidates:
                self.provider_status = "degraded"
                self.last_failure = "NO_CANDIDATES"
                self.key_manager.rotate_key()
                continue

            text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            if text:
                self.provider_status = "ok"
                self.last_failure = None
                return text.strip()

            return self._fallback_answer(question, context, mode)

        return self._fallback_answer(question, context, mode)


class RAGService:
    def __init__(self) -> None:
        self.store = KnowledgeStore(KNOWLEDGE_DIR)
        self.key_manager = GeminiKeyManager()
        self.llm = GeminiClient(self.key_manager)

    def classify(self, message: str) -> str:
        lowered = message.lower()
        if any(term in lowered for term in ["what is", "what does", "who is", "define", "how does", "rapid outflow", "structuring", "prysm", "aml", "graphsage"]):
            return "KNOWLEDGE"
        return "INVESTIGATION"

    def _build_context(self, message: str, context: dict[str, Any] | None = None) -> str:
        search_results = self.store.search(message, limit=5)
        if not search_results:
            context_parts = ["No local knowledge base entries matched the query."]
        else:
            context_parts = [
                f"Title: {item['title']}\nSource: {item['source']}\nCategory: {item['category']}\nContent: {item['content']}"
                for item in search_results
            ]
        if context:
            context_parts.append("Authorized backend context:\n" + json.dumps(context, ensure_ascii=False, indent=2)[:12000])
        return "\n\n---\n\n".join(context_parts)

    def answer(self, message: str, mode: str = "public", context: dict[str, Any] | None = None) -> dict[str, Any]:
        route = self.classify(message)
        content = self._build_context(message, context)
        answer = self.llm.generate(message, content, mode=mode)
        results = self.store.search(message, limit=5)
        return {
            "answer": answer,
            "mode": mode,
            "sources": [
                {"title": item["title"], "source": item["source"], "category": item["category"], "version": item["version"]}
                for item in results
            ],
            "conversationId": str(uuid.uuid4()),
            "requestId": str(uuid.uuid4()),
            "route": route,
        }

    def ingest(self, payload: DocumentIngest) -> dict[str, Any]:
        record = self.store.add_document(payload.model_dump() if hasattr(payload, "model_dump") else payload.dict())
        return {"success": True, "documentId": record["id"], "chunks": 1}


service = RAGService()

def require_internal_key(authorization: str | None = Header(default=None)) -> None:
    expected = os.getenv("RAG_API_KEY", "")
    if not expected:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "RAG_INTERNAL_KEY_NOT_CONFIGURED", "message": "Internal RAG authentication is not configured."})
    supplied = authorization[7:] if authorization and authorization.startswith("Bearer ") else ""
    if not hmac.compare_digest(supplied, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"code": "INVALID_INTERNAL_CREDENTIAL", "message": "Invalid internal service credential."})


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(title="Prysm RAG", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "prysm-rag",
        "llm": service.llm.provider_status,
        "llmLastFailure": service.llm.last_failure,
        "knowledgeBase": "ok",
    }


@app.get("/ask")
def ask_get(
    message: str = Query(..., min_length=1),
):
    return _handle_ask({"message": message, "authenticated": False})


@app.post("/ask", dependencies=[Depends(require_internal_key)])
def ask_post(payload: AskRequest):
    return _handle_ask(payload.model_dump() if hasattr(payload, "model_dump") else payload.dict())


@app.post("/ingest", dependencies=[Depends(require_internal_key)])
def ingest(payload: DocumentIngest):
    return service.ingest(payload)


@app.get("/documents", dependencies=[Depends(require_internal_key)])
def documents():
    return {"data": service.store.list_documents()}


@app.patch("/documents/{document_id}", dependencies=[Depends(require_internal_key)])
def update_document(document_id: str, enabled: bool):
    record = service.store.set_enabled(document_id, enabled)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "DOCUMENT_NOT_FOUND", "message": "Knowledge document was not found."})
    return record


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    expected = os.getenv("RAG_API_KEY", "")
    supplied = websocket.query_params.get("api_key", "")
    if not expected:
        await websocket.close(code=1011, reason="Internal RAG authentication is not configured.")
        return
    if not hmac.compare_digest(supplied, expected):
        await websocket.close(code=4401)
        return
    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            message = data.get("message", "")
            if not message:
                await websocket.send_json({"type": "error", "message": "message is required"})
                continue
            response = _handle_ask({
                "message": message,
                "authenticated": bool(data.get("authenticated", False)),
                "userId": data.get("userId"),
                "subjectId": data.get("subjectId"),
                "investigationId": data.get("investigationId"),
                "context": data.get("context", {}),
            })
            await websocket.send_json({"type": "token", "text": response["answer"]})
            await websocket.send_json({"type": "done", "conversationId": response["conversationId"], "sources": response["sources"]})
    except WebSocketDisconnect:
        pass


def _handle_ask(payload: dict[str, Any]) -> dict[str, Any]:
    message = str(payload.get("message") or "").strip()
    if not message:
        raise HTTPException(status_code=400, detail={"code": "INVALID_QUESTION", "message": "A message is required."})

    authenticated = bool(payload.get("authenticated"))
    if authenticated:
        context = payload.get("context") or {}
        if not isinstance(context, dict):
            raise HTTPException(status_code=401, detail={"code": "UNAUTHORIZED_CONTEXT", "message": "Context must be a JSON object."})
        response = service.answer(message, mode="investigator", context=context)
        findings = context.get("findings", []) if isinstance(context.get("findings"), list) else []
        evidence = [
            {
                "findingId": finding.get("id"),
                "findingType": finding.get("type"),
                "title": finding.get("title"),
                "summary": finding.get("summary"),
                "references": finding.get("evidence", []),
            }
            for finding in findings[:10]
            if isinstance(finding, dict)
        ]
        return {
            "answer": response["answer"],
            "mode": "investigator",
            "sources": response["sources"],
            "evidence": evidence,
            "conversationId": response["conversationId"],
            "requestId": response["requestId"],
        }

    response = service.answer(message, mode="public")
    return {
        "answer": response["answer"],
        "mode": "public",
        "sources": response["sources"],
        "conversationId": response["conversationId"],
        "requestId": response["requestId"],
    }
