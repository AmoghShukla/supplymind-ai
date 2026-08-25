from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import User, Vendor

class UserRepository:

    @staticmethod
    async def get_user_by_email(user_email, db : AsyncSession):
        statement = select(User).where(User.email == user_email)
        user = await db.execute(statement)
        return user.scalar().first()

class VendorRepository:

    @staticmethod
    async def get_all_vendors(db : AsyncSession):
        statement = select(Vendor)
        vendors = db.execute(statement)
        return vendors.scalars().all()

