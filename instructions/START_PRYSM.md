# Start Prysm

PostgreSQL must be running first. Then open four PowerShell terminals from the project root and run:

## 1. Chatbot / RAG

```powershell
cd chatbot
..\.venv\Scripts\python.exe main.py
```

The chatbot reads `chatbot/.env` directly, so values inherited from another shell no longer override its local configuration.

## 2. AI Engine

```powershell
cd ai-engine
..\.venv\Scripts\python.exe start.py
```

## 3. Backend

```powershell
cd server
npm.cmd run dev
```

## 4. Frontend

```powershell
cd client
npm.cmd run dev -- --host 127.0.0.1
```

Open **http://127.0.0.1:5173**. Keep all four terminals open while using Prysm.
