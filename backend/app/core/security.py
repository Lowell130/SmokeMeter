# backend/app/core/security.py
from datetime import datetime, timedelta, timezone
from jose import jwt
from ..core.config import settings

ALGO = settings.JWT_ALGORITHM

def _now_utc():
    return datetime.now(timezone.utc)

def create_access_token(sub: str) -> str:
    exp = _now_utc() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": sub, "type": "access", "exp": exp}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGO)

def create_refresh_token(sub: str) -> str:
    exp = _now_utc() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": sub, "type": "refresh", "exp": exp}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGO)
