import asyncio, json
from redis.asyncio import from_url
from ..core.config import settings
from ..db import SessionLocal
from ..agents.orchestrator import run_pipeline

async def consume():
    redis = from_url(settings.redis_url); last_id = "0-0"
    while True:
        records = await redis.xread({"supplymind.events": last_id}, block=3000, count=10)
        for _, entries in records:
            for event_id, fields in entries:
                last_id = event_id.decode() if isinstance(event_id, bytes) else event_id
                payload = json.loads(fields[b"payload"] if b"payload" in fields else fields["payload"])
                if payload.get("type") == "shipment_delay":
                    async with SessionLocal() as db: await run_pipeline(db, int(payload["shipment_id"]))

if __name__ == "__main__": asyncio.run(consume())
