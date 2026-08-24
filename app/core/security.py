from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import settings

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"
def hash_password(password: str) -> str: return pwd.hash(password)
def verify_password(password: str, hashed: str) -> bool: return pwd.verify(password, hashed)
def create_token(subject: str, role: str) -> str:
    payload = {"sub": subject, "role": role, "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)
def decode_token(token: str) -> dict:
    try: return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError as exc: raise ValueError("Invalid or expired token") from exc
