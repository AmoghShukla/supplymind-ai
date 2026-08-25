from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository import UserRepository
from ..db import get_session
from ..models import User
from .security import decode_token

oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def current_user(token: str = Depends(oauth2), db: AsyncSession = Depends(get_session)) -> User:
    try: 
        email = decode_token(token)["sub"]
    except (ValueError, KeyError): 
        raise HTTPException(401, "Invalid credentials")
    user = await UserRepository.get_user_by_email(email, db)
    if not user: 
        raise HTTPException(401, "User not found")
    return user

def require_roles(*roles):
    async def checker(user: User = Depends(current_user)):
        if user.role not in roles: 
            raise HTTPException(403, "Insufficient role")
        return user
    return checker
