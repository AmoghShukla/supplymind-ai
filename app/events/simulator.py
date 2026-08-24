import json
from datetime import datetime
from redis.asyncio import from_url
from ..core.config import settings
async def publish_delay(shipment_id: int = 1) -> dict:
    event = {"type": "shipment_delay", "shipment_id": shipment_id, "occurred_at": datetime.utcnow().isoformat()}
    redis = from_url(settings.redis_url)
    await redis.xadd("supplymind.events", {"payload": json.dumps(event)})
    await redis.aclose()
    return event
