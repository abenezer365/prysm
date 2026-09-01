"""Start the Prysm AI Engine with sensible local defaults."""
import os
import uvicorn

if __name__ == "__main__":
    uvicorn.run("api.app:app", host=os.getenv("AI_HOST", "127.0.0.1"), port=int(os.getenv("AI_PORT", "8100")))
