from datetime import datetime, timedelta, timezone
from typing import Optional
import secrets
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel

from backend.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

class TokenData(BaseModel):
    doctor_id: str
    exp: Optional[datetime] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        doctor_id: str = payload.get("sub")
        if doctor_id is None:
            return None
        exp = payload.get("exp")
        if exp:
            if isinstance(exp, datetime):
                exp_dt = exp.replace(tzinfo=timezone.utc) if exp.tzinfo is None else exp
            else:
                exp_dt = datetime.fromtimestamp(exp, tz=timezone.utc)
        else:
            exp_dt = None
        return TokenData(doctor_id=doctor_id, exp=exp_dt)
    except JWTError:
        return None

def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)