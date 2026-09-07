"""Start the Prysm AI Engine with the active local dataset and model."""
import os
from pathlib import Path
import uvicorn


ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent


def read_env_value(path: Path, name: str) -> str:
    if not path.is_file():
        return ""
    prefix = name + "="
    for raw_line in reversed(path.read_text(encoding="utf-8-sig").splitlines()):
        if raw_line.startswith(prefix):
            return raw_line[len(prefix):].strip().strip('"').strip("'")
    return ""


def configure_local_environment() -> None:
    if not os.getenv("AI_ENGINE_API_KEY", "").strip():
        key = read_env_value(PROJECT_ROOT / "server" / ".env", "AI_ENGINE_API_KEY")
        if key:
            os.environ["AI_ENGINE_API_KEY"] = key
    if not os.getenv("AI_ENGINE_API_KEY", "").strip():
        raise RuntimeError("AI_ENGINE_API_KEY is missing from server/.env")

    demo_dataset = PROJECT_ROOT / "data" / "prysm-demo-v2"
    demo_models = ROOT / "runs" / "demo-v2-build" / "model_bundle.json"
    if demo_dataset.is_dir() and demo_models.is_file():
        os.environ.setdefault("PRYSM_DATASET", str(demo_dataset))
        os.environ.setdefault("PRYSM_MODELS", str(demo_models))


if __name__ == "__main__":
    configure_local_environment()
    uvicorn.run(
        "api.intelligence:app",
        host=os.getenv("AI_HOST", "127.0.0.1"),
        port=int(os.getenv("AI_PORT", "8100")),
        access_log=False,
    )
