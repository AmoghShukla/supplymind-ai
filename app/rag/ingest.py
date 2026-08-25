from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Incident
from app.repository import IncidentRepository
from ..models import Incident

async def ingest_document(db: AsyncSession, text: str, incident_type: str = "reference") -> Incident:
    incident = Incident(type=incident_type, description=text, resolution="Reference document", embedding=[])
    await IncidentRepository.create_incident(incident, db)
