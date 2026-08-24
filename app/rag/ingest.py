from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Incident
async def ingest_document(db: AsyncSession, text: str, incident_type: str = "reference") -> Incident:
    """Stores a RAG document. Embedding is intentionally simple and provider-neutral for local demos."""
    incident = Incident(type=incident_type, description=text, resolution="Reference document", embedding=[])
    db.add(incident); await db.commit(); await db.refresh(incident); return incident
