import re
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Incident

async def hybrid_search(db: AsyncSession, query: str, limit: int = 5) -> list[dict]:
    terms = set(re.findall(r"[a-z0-9]+", query.lower()))
    rows = (await db.scalars(select(Incident))).all()
    scored = []
    for row in rows:
        words = set(re.findall(r"[a-z0-9]+", f"{row.type} {row.description} {row.resolution}".lower()))
        score = len(terms & words) / max(1, len(terms))
        if score: scored.append((score, row))
    return [{"id": r.id, "type": r.type, "description": r.description, "resolution": r.resolution, "score": round(s, 3)} for s, r in sorted(scored, reverse=True, key=lambda x: x[0])[:limit]]
