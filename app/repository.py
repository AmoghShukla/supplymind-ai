from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Shipment, User, Vendor

class UserRepository:

    @staticmethod
    async def get_user_by_email(user_email, db : AsyncSession):
        statement = select(User).where(User.email == user_email)
        user = await db.execute(statement)
        return user.scalar().first()

class VendorRepository:

    @staticmethod
    async def create_vendor(data, db : AsyncSession):
        item = Vendor(**data.model_dump())
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item

    @staticmethod
    async def get_all_vendors(db : AsyncSession):
        statement = select(Vendor)
        vendors = db.execute(statement)
        return vendors.scalars().all()

class ShipmentRepository:

    @staticmethod
    async def create_shipment(data, db : AsyncSession):
        item = Shipment(**data.model_dump())
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item

    @staticmethod
    async def get_all_shipments(db : AsyncSession):
        statement = select(Shipment)
        shipment = db.execute(statement)
        return shipment.scalars().all()

