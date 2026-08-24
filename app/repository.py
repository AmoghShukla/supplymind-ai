from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import User

class UserRepository:

    @staticmethod
    async def get_user_by_email(user_email, db : AsyncSession):
        statement = select(User).where(User.email == user_email)
        user = await db.execute(statement)
        return user.scalar().first()

