# Prysm Intelligence

Prysm is a financial-intelligence platform combining controlled investigations, transaction and behavioral analysis, bounded relationship graphs, evidence, and retrieval-grounded explanation. Model output is decision support, not a finding of guilt or a calibrated fraud probability.

## Local development setup

### 1. Install prerequisites and dependencies

Install Node.js 22+, Python 3.11+, and PostgreSQL. The coordinated Windows script expects a PostgreSQL Windows service named `postgresql*`.

```powershell
cd server; npm install
cd ../client; npm install
cd ../ai-engine; python -m pip install -e .
cd ../chatbot; python -m pip install -r requirements.txt
```

### 2. Create and migrate the database

Create a PostgreSQL database named `prysm` using pgAdmin or `CREATE DATABASE prysm;`. Copy `server/.env.example` to `server/.env` and set `DATABASE_URL` to the real PostgreSQL credentials and `prysm` database.

```powershell
cd server
npm run db:generate
npm run db:migrate
npm run db:seed
```

To create or reset a development administrator, provide `SEED_ADMIN_EMAIL` and `SEED_ADMIN_PASSWORD` only to the seed process, then remove them from the shell. No bootstrap HTTP route exists.

### 3. Configure RAG

Copy `chatbot/.env.example` to `chatbot/.env`. Generate one strong internal `RAG_API_KEY` and place the same value in `server/.env` and `chatbot/.env`. Protected ingestion and authorized chat fail closed when these values are blank or different.

Set `GOOGLE_API_KEYS` in `chatbot/.env` for Gemini generation. Without a reachable valid provider key, RAG uses its local evidence-grounded fallback and dependency health remains `degraded`, although public knowledge answers can still succeed.

Never commit `.env` files or service keys.

### 4. Start the stack in dependency order

The supported Windows command starts PostgreSQL, AI Engine, RAG, and backend with readiness checks:

```powershell
cd server
npm run dev:stack
```

The equivalent manual commands, each in its own terminal, are:

```powershell
# AI Engine
cd ai-engine
python -m uvicorn api.app:app --host 127.0.0.1 --port 8100

# RAG
cd chatbot
python -m uvicorn main:app --host 127.0.0.1 --port 8200

# Backend
cd server
npm run build
npm start

# Frontend
cd client
npm run dev -- --host 127.0.0.1
```

Open the URL printed by Vite, normally `http://127.0.0.1:5173`. The browser calls only `http://127.0.0.1:4000/api/v1`; it never calls AI Engine or RAG directly.

### 5. Verify

```powershell
Invoke-RestMethod http://127.0.0.1:8100/ready
Invoke-RestMethod http://127.0.0.1:8200/health
Invoke-RestMethod http://127.0.0.1:4000/api/v1/health/ready

cd server; npm run verify:integration; npm test
cd ../client; npm run build
cd ../chatbot; python -m pytest -q
```

## Boundaries

- React/Vite presents data and interaction.
- Express owns authentication, authorization, trusted context, orchestration, persistence, and auditing.
- PostgreSQL stores operational facts and workflow state.
- AI Engine performs rule, anomaly, supervised, graph, and GNN analysis.
- RAG retrieves knowledge and produces grounded explanations.

See `ARCHITECTURE.md` and `BACKEND_API.md` for the authoritative design and browser contract.

## Known limitations

- Gemini requires external connectivity and valid provider keys; the local grounded fallback remains available when degraded.
- Analysis persists a durable run but currently waits for the AI adapter before returning.
- Export artifact workers, model-ticket redemption, multipart RAG upload, malware scanning, and OCR are not implemented.
- Production deployment, TLS, secret management, backups, monitoring, and load validation remain environment-specific work.
