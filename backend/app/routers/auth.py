# backend/app/routers/auth.py
from fastapi import APIRouter, HTTPException
from passlib.hash import bcrypt
from jose import jwt, JWTError, ExpiredSignatureError
from ..db.mongodb import get_db
from ..core.config import settings
from ..core.security import create_access_token, create_refresh_token, ALGO
from ..schemas.auth import RegisterIn, LoginIn, TokenPairOut, RefreshIn

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenPairOut)
async def register(data: RegisterIn):
    db = get_db()
    exists = await db.users.find_one({"email": data.email})
    if exists:
        raise HTTPException(400, "Email already registered")
    pwd = bcrypt.hash(data.password)
    res = await db.users.insert_one({"email": data.email, "password_hash": pwd})
    uid = str(res.inserted_id)
    return TokenPairOut(
        access_token=create_access_token(uid),
        refresh_token=create_refresh_token(uid),
    )

@router.post("/login", response_model=TokenPairOut)
async def login(data: LoginIn):
    db = get_db()
    user = await db.users.find_one({"email": data.email})
    if not user or not bcrypt.verify(data.password, user["password_hash"]):
        raise HTTPException(401, "Invalid credentials")
    uid = str(user["_id"])
    return TokenPairOut(
        access_token=create_access_token(uid),
        refresh_token=create_refresh_token(uid),
    )

@router.post("/refresh", response_model=TokenPairOut)
async def refresh(data: RefreshIn):
    """
    Minimal refresh: verifica il refresh token e rilascia un nuovo access token.
    (N.B. in produzione è consigliata rotazione e revoca server-side)
    """
    try:
        payload = jwt.decode(data.refresh_token, settings.SECRET_KEY, algorithms=[ALGO])
        if payload.get("type") != "refresh":
            raise HTTPException(401, "Invalid token type")
        uid = payload.get("sub")
        if not uid:
            raise HTTPException(401, "Invalid token payload")
        # qui potresti fare rotazione generando un NUOVO refresh token
        # per semplicità restituiamo lo stesso refresh token
        return TokenPairOut(
            access_token=create_access_token(uid),
            refresh_token=data.refresh_token,
        )
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
