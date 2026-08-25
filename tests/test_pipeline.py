import os
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_supplymind.db"
import pytest
from app.db import engine, SessionLocal
from app.models import Base
from app.seed import seed
from app.agents.orchestrator import run_pipeline
@pytest.mark.asyncio

async def test_seeded_delay_creates_approval():
    async with engine.begin() as connection: 
        await connection.run_sync(Base.metadata.create_all)
    await seed()
    async with SessionLocal() as db:
        output = await run_pipeline(db, 1)
    assert output["status"] == "awaiting_approval"
    assert [step["agent"] for step in output["steps"]] == ["watcher", "diagnostic", "planner", "critic"]
