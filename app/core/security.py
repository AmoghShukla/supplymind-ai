from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from pwdlib import PasswordHash
from .config import settings

password_context: PasswordHash = PasswordHash.recommended()
ALGORITHM = "HS256"
def hash_password(password: str) -> str: return password_context.hash(password)
def verify_password(password: str, hashed: str) -> bool: return password_context.verify(password, hashed)
def create_token(subject: str, role: str) -> str:
    payload = {"sub": subject, "role": role, "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)
def decode_token(token: str) -> dict:
    try: return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError as exc: raise ValueError("Invalid or expired token") from exc
