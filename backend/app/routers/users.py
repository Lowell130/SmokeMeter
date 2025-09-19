from fastapi import APIRouter, Depends
from bson import ObjectId

from ..utils.deps import get_current_user_id
from ..db.mongodb import get_db
from ..schemas.user import UserOut, UserUpdate


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def me(uid: str = Depends(get_current_user_id)):
    db = get_db()
    u = await db.users.find_one({"_id": {"$eq": ObjectId(uid)}})
    return UserOut(
        id=uid,
        email=u["email"],
        baseline_cigs_per_day=u.get("baseline_cigs_per_day"),
        price_per_pack=u.get("price_per_pack"),
    )


@router.patch("/me", response_model=UserOut)
async def update_me(payload: UserUpdate, uid: str = Depends(get_current_user_id)):
    db = get_db()
    await db.users.update_one(
        {"_id": ObjectId(uid)},
        {"$set": payload.model_dump(exclude_none=True)},
    )
    u = await db.users.find_one({"_id": ObjectId(uid)})
    return UserOut(
        id=uid,
        email=u["email"],
        baseline_cigs_per_day=u.get("baseline_cigs_per_day"),
        price_per_pack=u.get("price_per_pack"),
    )
