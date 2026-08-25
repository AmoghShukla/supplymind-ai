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
from ..repository import IncidentRepository, ShipmentRepository, UserRepository, VendorRepository

router = APIRouter()

@router.post("/auth/login", response_model=Token)
async def login(payload: Login, db: AsyncSession = Depends(get_session)):
    user = await UserRepository.get_user_by_email(payload.email, db)
    if not user or not verify_password(payload.password, user.hashed_password): 
        raise HTTPException(401, "Incorrect email or password")
    return Token(access_token=create_token(user.email, user.role))

@router.post("/vendors")
async def create_vendor(data: VendorCreate, _: User = Depends(require_roles("admin", "analyst")), db: AsyncSession = Depends(get_session)):
    return await VendorRepository.create_vendor(data, db)

@router.get("/vendors")
async def vendors(_: User = Depends(current_user), db: AsyncSession = Depends(get_session)): 
    return await VendorRepository.get_all_vendors(db)

@router.post("/shipments")
async def create_shipment(data: ShipmentCreate, _: User = Depends(require_roles("admin", "analyst")), db: AsyncSession = Depends(get_session)):
    return await ShipmentRepository.create_shipment(data, db)
    
@router.get("/shipments")
async def shipments(_: User = Depends(current_user), db: AsyncSession = Depends(get_session)): 
    return await ShipmentRepository.get_all_shipments(db)

@router.post("/incidents")
async def create_incident(data: IncidentCreate, _: User = Depends(require_roles("admin", "analyst")), db: AsyncSession = Depends(get_session)):
    return await IncidentRepository.create_incident(data, db)

@router.get("/incidents")
async def incidents(descriptions: str | None = None, _: User = Depends(current_user), db: AsyncSession = Depends(get_session)):
    statement = select(Incident)
    if descriptions: 
        statement = statement.where(Incident.description.ilike(f"%{q}%"))
    return await IncidentRepository.get_all_incidents(statement, db)


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
