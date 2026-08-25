from datetime import datetime, timedelta
from sqlalchemy import select
from .core.security import hash_password
from .db import SessionLocal
from .models import User, Vendor, Shipment, Inventory, Incident

async def seed():
    async with SessionLocal() as db:
        if await db.scalar(select(User.id).limit(1)): 
            return

        admin = User(email="admin@demo.com", hashed_password=hash_password("changeme"), role="admin")
        analyst = User(email="analyst@demo.com", hashed_password=hash_password("changeme"), role="analyst")
        acme = Vendor(name="Acme Components", region="Shenzhen, CN", reliability_score=.62, contract_terms="72-hour delay SLA; expedited freight allowed up to $5,000.")
        north = Vendor(name="Northstar Logistics", region="Rotterdam, NL", reliability_score=.91, contract_terms="Priority capacity for approved reroutes.")

        db.add_all([admin, analyst, acme, north])
        await db.flush()

        late = Shipment(po_number="PO-2026-0042", vendor_id=acme.id, status="delayed", eta=datetime.utcnow()-timedelta(days=2), origin="Shenzhen", destination="Chicago")
        normal = Shipment(po_number="PO-2026-0043", vendor_id=north.id, status="in_transit", eta=datetime.utcnow()+timedelta(days=5), origin="Rotterdam", destination="Chicago")

        db.add_all([late, normal])
        await db.flush()

        db.add_all([Inventory(sku="MCU-8X", warehouse_id="CHI-01", quantity=120, reorder_point=300), Inventory(sku="SENSOR-4", warehouse_id="CHI-01", quantity=780, reorder_point=250), Incident(shipment_id=late.id, type="port_congestion", description="Shenzhen container delayed by port congestion; MCU-8X stock below reorder point.", resolution="Split shipment and book air freight for critical pallets."), Incident(shipment_id=None, type="customs_hold", description="Import documentation mismatch caused customs hold.", resolution="Correct commercial invoice and submit broker escalation.")])
        await db.commit()
