from fastapi import APIRouter, Depends
from ..core.deps import get_current_user_id
from ..db.mongo import get_db
from ..utils import oid

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me")
async def me(user_id: str = Depends(get_current_user_id)):
    db = get_db()
    user = await db.users.find_one({"_id": oid(user_id)})
    if not user:
        return {"_id": user_id, "email": None}
    return {"_id": str(user["_id"]), "email": user["email"]}
