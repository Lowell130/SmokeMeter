from fastapi import APIRouter, HTTPException
from ..db.mongo import get_db
from ..schemas.user import UserCreate, UserLogin, UserPublic
from ..schemas.auth import Token
from ..core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserPublic)
async def register(payload: UserCreate):
    db = get_db()
    existing = await db.users.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=409, detail="Email già registrata")
    doc = {"email": payload.email, "password": hash_password(payload.password), "created_at": 0}
    res = await db.users.insert_one(doc)
    doc["_id"] = str(res.inserted_id)
    del doc["password"]
    return doc

@router.post("/login", response_model=Token)
async def login(payload: UserLogin):
    db = get_db()
    user = await db.users.find_one({"email": payload.email})
    if not user or not verify_password(payload.password, user["password"]):
        raise HTTPException(status_code=401, detail="Credenziali non valide")
    token = create_access_token(str(user["_id"]))
    return {"access_token": token}