from fastapi import APIRouter, Depends
from datetime import datetime, timedelta

from ..utils.deps import get_current_user_id
from ..db.mongodb import get_db


router = APIRouter(prefix="/log", tags=["log"])


@router.post("/cigarette")
async def add_cig(meta: dict | None = None, uid: str = Depends(get_current_user_id)):
    db = get_db()
    doc = {
        "user_id": uid,
        "type": "cigarette",
        "ts": datetime.utcnow(),
        "meta": meta,
    }
    await db.logs.insert_one(doc)
    return {"ok": True}


@router.post("/purchase")
async def add_purchase(meta: dict, uid: str = Depends(get_current_user_id)):
    db = get_db()
    doc = {
        "user_id": uid,
        "type": "purchase",
        "ts": datetime.utcnow(),
        "meta": meta,
    }
    await db.logs.insert_one(doc)
    return {"ok": True}


@router.get("/today")
async def today(uid: str = Depends(get_current_user_id)):
    db = get_db()
    start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    count = await db.logs.count_documents(
        {
            "user_id": uid,
            "type": "cigarette",
            "ts": {"$gte": start, "$lt": end},
        }
    )
    return {"cigs_today": count}
