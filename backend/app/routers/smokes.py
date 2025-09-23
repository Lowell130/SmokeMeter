from fastapi import APIRouter, Depends, HTTPException, Query
from ..core.deps import get_current_user_id
from ..db.mongo import get_db
from ..schemas.smoke import SmokeCreate, SmokeUpdate
from ..utils import now_ts, oid, to_primitive

router = APIRouter(prefix="/smokes", tags=["smokes"])

def _serialize_smoke(x: dict) -> dict:
    return {
        "_id": str(x["_id"]),
        "user_id": x.get("user_id"),
        "pack_id": x.get("pack_id"),
        "type": x.get("type","smoked"),
        "ts": int(x.get("ts", 0)),
        "source": x.get("source"),
        "brand": x.get("brand"),
    }

@router.post("")
async def create_smoke(payload: SmokeCreate, user_id: str = Depends(get_current_user_id)):
    db = get_db()

    doc = {
        "user_id": user_id,
        "type": payload.type,
        "ts": now_ts(),
    }

    if payload.pack_id:
        _oid = oid(payload.pack_id)
        pack = await db.packs.find_one({"_id": _oid, "user_id": user_id})
        if not pack:
            raise HTTPException(status_code=404, detail="Pacchetto non trovato")
        doc["pack_id"] = str(_oid)   # normalizza come stringa
        doc["source"] = "pack"
        if pack.get("brand"):
            doc["brand"] = pack["brand"]
    else:
        doc["source"] = "loose"
        if payload.brand:
            doc["brand"] = payload.brand

    res = await db.smokes.insert_one(doc)
    return to_primitive({"_id": res.inserted_id, **doc})

@router.patch("/{smoke_id}")
async def update_smoke(smoke_id: str, payload: SmokeUpdate, user_id: str = Depends(get_current_user_id)):
    db = get_db()
    upd = {k: v for k, v in payload.model_dump().items() if v is not None}
    await db.smokes.update_one({"_id": oid(smoke_id), "user_id": user_id}, {"$set": upd})
    x = await db.smokes.find_one({"_id": oid(smoke_id)})
    return to_primitive(x)

@router.delete("/{smoke_id}")
async def delete_smoke(smoke_id: str, user_id: str = Depends(get_current_user_id)):
    db = get_db()
    res = await db.smokes.delete_one({"_id": oid(smoke_id), "user_id": user_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Record non trovato")
    return {"ok": True}

@router.get("")
async def list_smokes(
    user_id: str = Depends(get_current_user_id),
    loose_only: bool | None = Query(None, description="Se true solo smokes senza pacchetto"),
    skip: int | None = Query(None, ge=0),
    limit: int | None = Query(None, ge=1, le=200),
):
    """
    Senza skip/limit -> lista flat (compatibile dashboard).
    Con skip/limit    -> oggetto paginato { items, total, skip, limit } (per /smokes.vue).
    Filtro opzionale loose_only=true/false.
    """
    db = get_db()
    q = {"user_id": user_id}
    if loose_only is True:
        q["pack_id"] = {"$exists": False}
    elif loose_only is False:
        q["pack_id"] = {"$exists": True}

    base_cur = db.smokes.find(q).sort("ts", -1)

    # modalità dashboard (flat)
    if skip is None or limit is None:
        out = []
        async for x in base_cur:
            out.append(_serialize_smoke(x))
        return out

    # modalità paginata
    total = await db.smokes.count_documents(q)
    cur = base_cur.skip(skip).limit(limit)
    items = []
    async for x in cur:
        items.append(_serialize_smoke(x))
    return {"items": items, "total": total, "skip": skip, "limit": limit}

@router.get("/stats/overview")
async def stats_overview(user_id: str = Depends(get_current_user_id)):
    db = get_db()
    total_smokes = await db.smokes.count_documents({"user_id": user_id, "type": "smoked"})
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$addFields": {"pack_oid": {"$toObjectId": "$pack_id"}}},
        {"$lookup": {"from": "packs", "localField": "pack_oid", "foreignField": "_id", "as": "pack"}},
        {"$unwind": {"path": "$pack", "preserveNullAndEmptyArrays": True}},
        {"$group": {"_id": "$pack._id", "price": {"$max": "$pack.price"}}},
        {"$group": {"_id": None, "spesa": {"$sum": {"$ifNull": ["$price", 0]}}}},
    ]
    spesa = 0
    async for row in db.smokes.aggregate(pipeline):
        spesa = row.get("spesa", 0)
    return {"total_smokes": total_smokes, "total_spent": spesa}

@router.get("/stats/summary")
async def smokes_summary(
    user_id: str = Depends(get_current_user_id),
    days: int = Query(30, ge=1, le=365)
):
    db = get_db()
    to_ts = now_ts()
    from_ts = to_ts - days * 24 * 3600

    pipeline = [
        {"$match": {"user_id": user_id, "ts": {"$gte": from_ts, "$lte": to_ts}}},
        {"$group": {"_id": "$type", "count": {"$sum": 1}}}
    ]
    counts = {"smoked": 0, "wasted": 0, "gifted": 0, "loose": 0}
    total_all = 0

    async for row in db.smokes.aggregate(pipeline):
        t = row.get("_id") or "smoked"
        c = int(row.get("count", 0))
        total_all += c
        if t in counts:
            counts[t] += c

    avg_per_day = counts["smoked"] / days if days else 0.0
    avg_per_week = counts["smoked"] / (days / 7.0) if days else 0.0

    return {
        "days": days,
        "total_all": total_all,
        "counts_by_type": counts,
        "avg_per_day": round(avg_per_day, 2),
        "avg_per_week": round(avg_per_week, 2),
    }

@router.get("/stats/intervallo")
async def smokes_intervals(
    user_id: str = Depends(get_current_user_id),
    limit: int = Query(200, ge=10, le=2000)
):
    """
    Intervalli (minuti) tra fumate consecutive (solo type='smoked'), ultimi N eventi.
    Ritorna media e mediana (minuti).
    """
    db = get_db()
    cur = db.smokes.find({"user_id": user_id, "type": "smoked"}).sort("ts", -1).limit(limit)
    ts_list = []
    async for x in cur:
        ts_list.append(int(x["ts"]))
    ts_list.sort()

    deltas = []
    for i in range(1, len(ts_list)):
        deltas.append((ts_list[i] - ts_list[i-1]) / 60.0)

    def mean(xs): return (sum(xs) / len(xs)) if xs else 0.0
    def median(xs):
        n = len(xs)
        if n == 0: return 0.0
        ys = sorted(xs)
        mid = n // 2
        return (ys[mid] if n % 2 == 1 else (ys[mid - 1] + ys[mid]) / 2)

    return {
        "sample": len(deltas),
        "mean_minutes": round(mean(deltas), 1),
        "median_minutes": round(median(deltas), 1)
    }

@router.get("/stats/brand-top")
async def smokes_brand_top(
    user_id: str = Depends(get_current_user_id),
    limit: int = Query(5, ge=1, le=20),
    days: int = Query(90, ge=1, le=365)
):
    db = get_db()
    to_ts = now_ts()
    from_ts = to_ts - days * 24 * 3600
    pipeline = [
        {"$match": {"user_id": user_id, "type": "smoked", "ts": {"$gte": from_ts, "$lte": to_ts}}},
        {"$group": {"_id": {"$ifNull": ["$brand", ""]}, "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit},
        {"$project": {"_id": 0, "brand": "$_id", "count": 1}}
    ]
    out = []
    async for row in db.smokes.aggregate(pipeline):
        out.append({"brand": row.get("brand") or "—", "count": int(row.get("count", 0))})
    return out

@router.get("/stats/heatmap")
async def smokes_heatmap(
    user_id: str = Depends(get_current_user_id),
    days: int = Query(30, ge=1, le=180)
):
    db = get_db()
    to_ts = now_ts()
    from_ts = to_ts - days * 24 * 3600

    pipeline = [
        {"$match": {"user_id": user_id, "type": "smoked", "ts": {"$gte": from_ts, "$lte": to_ts}}},
        {"$addFields": {"dt": {"$toDate": {"$multiply": ["$ts", 1000]}}}},
        {"$group": {
            "_id": {
                "dow": {"$dayOfWeek": {"date": "$dt", "timezone": "Europe/Rome"}},
                "hour": {"$hour": {"date": "$dt", "timezone": "Europe/Rome"}},
            },
            "count": {"$sum": 1}
        }},
        {"$project": {"_id": 0, "dow": "$_id.dow", "hour": "$_id.hour", "count": 1}}
    ]

    def dow_to_monday_first(dow):
        # Mongo: 1=Sun..7=Sat -> vogliamo 0=Mon..6=Sun
        if dow == 1: return 6
        return dow - 2

    matrix = [[0 for _ in range(24)] for _ in range(7)]
    async for row in db.smokes.aggregate(pipeline):
        r = dow_to_monday_first(int(row["dow"]))
        c = int(row["hour"])
        if 0 <= r < 7 and 0 <= c < 24:
            matrix[r][c] = int(row.get("count", 0))

    return {
        "days": days,
        "timezone": "Europe/Rome",
        "rows": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
        "cols": [f"{h:02d}" for h in range(24)],
        "matrix": matrix
    }

@router.get("/stats/by-hour")
async def stats_by_hour(
    days: int = Query(7, ge=1, le=90, description="Intervallo in giorni (default 7)"),
    user_id: str = Depends(get_current_user_id),
):
    db = get_db()
    to_ts = now_ts()
    from_ts = to_ts - days * 24 * 3600

    pipeline = [
        {"$match": {"user_id": user_id, "type": "smoked", "ts": {"$gte": from_ts, "$lte": to_ts}}},
        {"$addFields": {"dt": {"$toDate": {"$multiply": ["$ts", 1000]}}}},
        {
            "$group": {
                "_id": {"$hour": {"date": "$dt", "timezone": "Europe/Rome"}},
                "count": {"$sum": 1}
            }
        },
        {"$project": {"_id": 0, "hour": "$_id", "count": 1}},
        {"$sort": {"hour": 1}},
    ]

    result = [{"hour": h, "count": 0} for h in range(24)]
    async for row in db.smokes.aggregate(pipeline):
        h = int(row.get("hour", 0))
        if 0 <= h <= 23:
            result[h]["count"] = int(row.get("count", 0))

    return {
        "days": days,
        "timezone": "Europe/Rome",
        "hours": [f"{h:02d}" for h in range(24)],
        "data": [x["count"] for x in result],
        "total": sum(x["count"] for x in result),
    }
