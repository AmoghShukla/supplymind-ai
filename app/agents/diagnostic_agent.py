from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Shipment
from ..rag.retriever import hybrid_search
from .tools import DiagnosisResult

async def diagnose(db: AsyncSession, shipment: Shipment) -> DiagnosisResult:
    matches = await hybrid_search(db, f"{shipment.status} {shipment.origin} shipment delay")
    cause = matches[0]["type"].replace("_", " ") if matches else "carrier schedule disruption"
    return DiagnosisResult(
        root_cause=cause, 
        confidence=.84 if matches else .55, 
        supporting_incident_ids=[m["id"] for m in matches]
        )
