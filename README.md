# SupplyMind AI

Runnable supply-chain disruption orchestration backend. It uses SQLite by default for a zero-config demo and PostgreSQL/Redis in Docker. Seeded credentials: `admin@demo.com` / `changeme`.

```bash
cp .env.example .env
docker compose up --build
```

Open `http://localhost:8000/docs`, log in at `POST /auth/login`, then use the returned bearer token to call `POST /agents/run` with `{ "shipment_id": 1 }`.

The agent pipeline has a deterministic local mode by default, so it remains demonstrable without an LLM key. Set `AI_PROVIDER` and `AI_MODEL` for a future Pydantic AI provider integration.
