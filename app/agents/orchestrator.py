from sqlalchemy.ext.asyncio import AsyncSession
from ..models import AgentRun, Approval, Shipment
from .watcher_agent import assess
from .diagnostic_agent import diagnose
from .planner_agent import plan
from .critic_agent import critique
from .executor_agent import execute
from sqlalchemy.orm.attributes import flag_modified

async def run_pipeline(db: AsyncSession, shipment_id: int, auto_execute: bool = False) -> dict:
    shipment = await db.get(Shipment, shipment_id)
    if not shipment: raise ValueError(f"Shipment {shipment_id} not found")

    run = AgentRun(scenario=f"shipment:{shipment.po_number}", steps=[]); db.add(run); await db.flush()
    watcher = await assess(shipment); run.steps.append({"agent": "watcher", "result": watcher})
    if not watcher["action_needed"]:
        run.status = "no_action"; flag_modified(run, "steps"); await db.commit(); return {"run_id": run.id, "status": run.status, "steps": run.steps}

    diagnosis = await diagnose(db, shipment); run.steps.append({"agent": "diagnostic", "result": diagnosis.model_dump()})
    proposal = await plan(diagnosis); run.steps.append({"agent": "planner", "result": proposal.model_dump()})

    review = await critique(proposal); run.steps.append({"agent": "critic", "result": review.model_dump()})
    if review.approved and auto_execute:
        run.steps.append({"agent": "executor", "result": await execute(db, shipment, proposal)}); run.status = "executed"
    else:
        db.add(Approval(agent_run_id=run.id, proposed_action=proposal.model_dump(), risk_score=review.risk_score, status="pending" if review.approved else "rejected")); run.status = "awaiting_approval" if review.approved else "blocked"
    flag_modified(run, "steps")
    await db.commit()
    return {
        "run_id": run.id, 
        "status": run.status, 
        "steps": run.steps
    }
