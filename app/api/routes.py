from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.deps import current_user, require_roles
from ..core.security import create_token, verify_password
from ..db import get_session
from ..models import Approval, Incident, Shipment, User, Vendor
from ..schemas.common import ApprovalDecision, IncidentCreate, Login, RunRequest, ShipmentCreate, Token, VendorCreate
from ..agents.orchestrator import run_pipeline
from ..models import AgentRun
from ..repository import UserRepository, VendorRepository

router = APIRouter()

@router.post("/auth/login", response_model=Token)
async def login(payload: Login, db: AsyncSession = Depends(get_session)):
    user = await UserRepository.get_user_by_email(payload.email, db)
    if not user or not verify_password(payload.password, user.hashed_password): 
        raise HTTPException(401, "Incorrect email or password")
    return Token(access_token=create_token(user.email, user.role))

@router.get("/vendors")
async def vendors(_: User = Depends(current_user), db: AsyncSession = Depends(get_session)): 
    return await VendorRepository.get_all_vendors(db)

@router.post("/vendors")
async def create_vendor(data: VendorCreate, _: User = Depends(require_roles("admin", "analyst")), db: AsyncSession = Depends(get_session)):
    item = Vendor(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

@router.get("/shipments")
async def shipments(_: User = Depends(current_user), db: AsyncSession = Depends(get_session)): 
    return (await db.scalars(select(Shipment))).all()

@router.post("/shipments")
async def create_shipment(data: ShipmentCreate, _: User = Depends(require_roles("admin", "analyst")), db: AsyncSession = Depends(get_session)):
    item = Shipment(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

@router.get("/incidents")
async def incidents(q: str | None = None, _: User = Depends(current_user), db: AsyncSession = Depends(get_session)):
    statement = select(Incident)
    if q: statement = statement.where(Incident.description.ilike(f"%{q}%"))
    return (await db.scalars(statement)).all()

@router.post("/incidents")
async def create_incident(data: IncidentCreate, _: User = Depends(require_roles("admin", "analyst")), db: AsyncSession = Depends(get_session)):
    item = Incident(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

@router.post("/agents/run")
async def agent_run(data: RunRequest, _: User = Depends(require_roles("admin", "analyst")), db: AsyncSession = Depends(get_session)): 
    return await run_pipeline(db, data.shipment_id, data.auto_execute)

@router.get("/agents/runs/{run_id}")
async def get_run(run_id: int, _: User = Depends(current_user), db: AsyncSession = Depends(get_session)):
    item = await db.get(AgentRun, run_id)
    if not item: raise HTTPException(404, "Run not found")
    return item

@router.get("/approvals")
async def approvals(_: User = Depends(current_user), db: AsyncSession = Depends(get_session)): 
    return (await db.scalars(select(Approval))).all()

@router.post("/approvals/{approval_id}")
async def decide(approval_id: int, data: ApprovalDecision, user: User = Depends(require_roles("admin")), db: AsyncSession = Depends(get_session)):
    item = await db.get(Approval, approval_id)
    if not item: raise HTTPException(404, "Approval not found")
    item.status, item.approved_by = ("approved" if data.approved else "rejected"), user.email; await db.commit(); return item
