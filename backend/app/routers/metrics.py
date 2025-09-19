from fastapi import APIRouter, Depends
from datetime import datetime, timedelta

from ..utils.deps import get_current_user_id
from ..db.mongodb import get_db


router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/summary")
async def summary(range: str = "7d", uid: str = Depends(get_current_user_id)):
    db = get_db()
    days = int(range.rstrip("d"))

    end = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    start = end - timedelta(days=days)

    cursor = db.logs.find(
        {"user_id": uid, "type": "cigarette", "ts": {"$gte": start, "$lt": end}},
        {"ts": 1},
    )

    buckets = [0] * days
    async for d in cursor:
        idx = (d["ts"].date() - (end - timedelta(days=days)).date()).days
        if 0 <= idx < days:
            buckets[idx] += 1

    total = sum(buckets)

    # spesa stimata grezza (se disponibile price_per_pack nel profilo possiamo raffinare)
    return {
        "range": range,
        "total_cigs": total,
        "total_spend": 0.0,
        "daily_series": buckets,
    }


@router.get("/hourly")
async def hourly(range: str = "30d", uid: str = Depends(get_current_user_id)):
    db = get_db()
    days = int(range.rstrip("d"))
    end = datetime.utcnow()
    start = end - timedelta(days=days)

    hist = [0] * 24
    cursor = db.logs.find(
        {"user_id": uid, "type": "cigarette", "ts": {"$gte": start, "$lt": end}},
        {"ts": 1},
    )

    async for d in cursor:
        hist[d["ts"].hour] += 1

    return {"range": range, "hist": hist}
