"""Fast offline endpoint tests: isolated knowledge and no real provider calls."""
from pathlib import Path
import shutil
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def isolated_service(monkeypatch, tmp_path):
    import main
    monkeypatch.setenv("RAG_API_KEY", "test-internal-key")
    knowledge = tmp_path / "knowledge"
    shutil.copytree(ROOT / "rag/knowledge_base", knowledge)
    monkeypatch.setattr(main.service, "store", main.KnowledgeStore(knowledge))
    monkeypatch.setattr(main.service.key_manager, "keys", [])
