# Prysm Backend

Production-oriented Node.js/Express orchestration boundary between the future frontend, PostgreSQL, the existing Python AI Engine, and the independently deployed RAG service.

## Local setup

1. Copy `.env.example` to `.env` and replace every secret.
2. Start PostgreSQL and create the configured database.
3. Run `npm install`.
4. Run `npm run db:generate` and `npm run db:migrate`.
5. Optionally set `SEED_ADMIN_EMAIL` and `SEED_ADMIN_PASSWORD`, then run `npm run db:seed`.
6. Run `npm run dev`.

Start the AI Engine with `python -m uvicorn api.app:app --host 127.0.0.1 --port 8100` from `ai-engine/`. Build and start the backend with `npm run build` then `npm start`. Validation commands are `npm run build`, `npm test`, and `npx prisma validate`.

To ingest a bounded canonical slice without copying the raw dataset:

```text
python scripts/export_operational_slice.py --subject Company:C04166 --cutoff 2025-06-16T00:00:00Z --output ../server/data/operational-slice.json --max-hops 3 --max-nodes 250
npm run ingest:slice -- data/operational-slice.json
```

The liveness endpoint does not require dependencies. Readiness requires PostgreSQL. AI analysis calls the separately running FastAPI boundary; failures return sanitized `503` errors. RAG remains a future integration. API contracts are documented in `docs/openapi.yaml` and `docs/API.md`.

## Security and scientific boundaries

- Authorization combines verified JWT identity, a live PostgreSQL session/current-user lookup, current role permissions, clearance rank, and resource ownership. Revocation, disabling, and access changes therefore take effect on the next request.
- Public chat cannot receive subject or investigation context. Authorized chat reconstructs bounded context server-side.
- Graph traversal is cutoff-aware and bounded to three hops and 250 nodes.
- Refresh tokens are stored only as SHA-256 hashes; passwords use Argon2id.
- API DTOs never expose password hashes or raw model artifacts.
- AI output is an `uncalibrated_attention_assessment`, not a fraud probability. Synthetic benchmark results remain labeled as synthetic.

## Data ingestion

The schema is the operational target. This step intentionally does not duplicate the large Parquet datasets. Build an explicit, idempotent ingestion/mapping job after the deployment PostgreSQL topology and source ownership are confirmed.
