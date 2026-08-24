# SupplyMind AI

**SupplyMind AI** is a runnable supply-chain disruption orchestration backend. It detects shipment exceptions, finds relevant historical incidents, creates a remediation plan, applies budget guardrails, and either executes an approved plan or sends it to a human approval queue.

It is deliberately useful without an external LLM: the shipped pipeline runs deterministically with realistic seeded data. The configuration also reserves `AI_PROVIDER` and `AI_MODEL` for a provider-backed agent implementation.

## What it does

```text
Shipment exception → Watcher → Diagnostic → Planner → Critic → Executor
                                                        └────→ Human approval queue
```

- **Watcher** detects actionable shipment statuses such as `delayed`, `exception`, and `customs_hold`.
- **Diagnostic** retrieves similar incident reports and identifies a probable root cause.
- **Planner** builds a multi-step recovery plan with estimated costs.
- **Critic** checks the plan against the expedited-freight budget guardrail.
- **Executor** applies an approved plan to the mocked shipment workflow.

## Features

- FastAPI async REST API with interactive OpenAPI documentation
- JWT login and role-based access (`admin`, `analyst`, `viewer`)
- SQLAlchemy async data model with Alembic migration entrypoint
- PostgreSQL + pgvector-ready Docker environment and Redis Streams worker
- SQLite fallback for zero-config local development
- Incident ingestion and portable hybrid keyword retrieval
- Repeatability evaluation harness for seeded agent scenarios
- Safe demo seed data, including suppliers, inventory, shipments, historical incidents, and users

## Quick start

### Docker (recommended)

```bash
git clone https://github.com/AmoghShukla/supplymind-ai.git
cd supplymind-ai
cp .env.example .env
docker compose up --build
```

On Windows PowerShell, use `Copy-Item .env.example .env`. Then open [http://localhost:8000/docs](http://localhost:8000/docs).

### Local development

The app defaults to SQLite when `DATABASE_URL` is not defined.

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The application creates its tables and loads seed data on first startup.

## Seeded demo

| Account | Password | Role |
| --- | --- | --- |
| `admin@demo.com` | `changeme` | `admin` |
| `analyst@demo.com` | `changeme` | `analyst` |

The seed set includes a delayed Shenzhen-to-Chicago shipment at `shipment_id: 1`.

```bash
# Log in, then copy access_token from the response.
curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"email":"admin@demo.com","password":"changeme"}'

# Trigger the human-approval flow.
curl -X POST http://localhost:8000/agents/run -H "Authorization: Bearer <access_token>" -H "Content-Type: application/json" -d '{"shipment_id":1,"auto_execute":false}'
```

The response contains an auditable sequence of agent steps and creates an approval item. Set `auto_execute` to `true` to demonstrate execution of a plan within the guardrail.

## API overview

All routes other than login and health require a bearer token.

| Method | Endpoint | Purpose | Minimum role |
| --- | --- | --- | --- |
| `GET` | `/health` | Service health and configured AI provider | Public |
| `POST` | `/auth/login` | Receive JWT access token | Public |
| `GET/POST` | `/vendors` | List or create vendors | Viewer / Analyst |
| `GET/POST` | `/shipments` | List or create shipments | Viewer / Analyst |
| `GET/POST` | `/incidents` | Search or add the incident corpus | Viewer / Analyst |
| `POST` | `/agents/run` | Run the orchestration pipeline | Analyst |
| `GET` | `/agents/runs/{run_id}` | Inspect an agent run and its step log | Viewer |
| `GET` | `/approvals` | View pending decisions | Viewer |
| `POST` | `/approvals/{approval_id}` | Approve or reject a plan | Admin |

## Architecture

```text
FastAPI API ──► SQLAlchemy ──► PostgreSQL + pgvector (Docker)
     │                     └► SQLite (local demo)
     └► Agent run log + approval queue

Redis Stream event ──► Worker ──► Orchestrator ──► Agent pipeline
```

The Docker stack uses PostgreSQL with pgvector and Redis. Local development can use SQLite; embeddings are presently stored in a portable JSON column and retrieval uses term-overlap ranking, so the demo does not require an embedding API.

## Configuration

Copy `.env.example` and adjust as needed.

| Variable | Default / Docker value | Meaning |
| --- | --- | --- |
| `DATABASE_URL` | PostgreSQL in Docker; SQLite locally | Async SQLAlchemy connection string |
| `REDIS_URL` | `redis://redis:6379/0` | Redis Streams connection |
| `SECRET_KEY` | Development value | JWT signing secret; replace in production |
| `AI_PROVIDER` | `local` | Selected agent-provider label |
| `AI_MODEL` | `deterministic` | Selected model label |
| `AUTO_SEED` | `true` | Load demo records on first boot |

Never commit a real `.env` file or production secrets.

## Events and evaluations

Publish a simulated delayed-shipment event from an async Python session:

```python
from app.events.simulator import publish_delay

await publish_delay(shipment_id=1)
```

The worker consumes `supplymind.events` from Redis and begins the same orchestration flow.

```bash
python -m app.eval.harness
pytest -q
```

## Project layout

```text
app/
  agents/       # Watcher, diagnostic, planner, critic, executor, orchestrator
  api/          # FastAPI route definitions
  core/         # Settings, authentication, RBAC dependencies
  eval/         # Golden scenario and consistency harness
  events/       # Redis Stream simulator and worker consumer
  models/       # SQLAlchemy entities
  rag/          # Incident ingestion and retrieval
  schemas/      # Pydantic request/response contracts
  seed.py       # Demo data loader
alembic/        # Migration environment and initial schema
tests/          # Seeded pipeline test
```

## Production notes

This repository is a demo/reference backend. Before production use, replace the development JWT secret, set explicit CORS and rate-limit policies, use managed Postgres and Redis, introduce an embedding provider with true vector search, secure mocked ERP/WMS actions behind authenticated integrations, and run Alembic migrations as part of deployment.

## License

Add the license appropriate for your organization before public distribution.
