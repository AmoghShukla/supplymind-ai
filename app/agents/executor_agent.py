from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Shipment
from .tools import PlanResult

async def execute(db: AsyncSession, shipment: Shipment, plan: PlanResult) -> dict:
    shipment.status = "expedited"
    await db.commit()
    return {
        "executed": [a.action for a in plan.actions], 
        "rollback": "Set shipment status back to delayed if carrier booking fails"
        }
