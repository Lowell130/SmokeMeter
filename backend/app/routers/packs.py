from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import timezone
from ..core.deps import get_current_user_id
from ..db.mongo import get_db
from ..schemas.pack import PackCreate, PackUpdate
from ..utils import now_ts, oid, to_primitive

router = APIRouter(prefix="/packs", tags=["packs"])

def _serialize_pack(x: dict) -> dict:
    return {
        "_id": str(x["_id"]),
        "user_id": x.get("user_id"),
        "brand": x.get("brand"),
        "size": int(x.get("size", 0)),
        "price": float(x.get("price", 0)),
        "created_at": int(x.get("created_at", 0)),
    }

@router.get("")
async def list_packs(
    user_id: str = Depends(get_current_user_id),
    skip: int | None = Query(None, ge=0),
    limit: int | None = Query(None, ge=1, le=200),
):
    """
    Senza skip/limit -> lista flat (compatibile dashboard).
    Con skip/limit    -> oggetto paginato { items, total, skip, limit } (per /packs.vue).
    """
    db = get_db()
    q = {"user_id": user_id}

    base_cur = db.packs.find(q).sort("created_at", -1)

    # modalità dashboard (flat)
    if skip is None or limit is None:
        out = []
        async for x in base_cur:
            # backfill created_at se assente
            if not x.get("created_at"):
                try:
                    created = int(x["_id"].generation_time.replace(tzinfo=timezone.utc).timestamp())
                    await db.packs.update_one({"_id": x["_id"]}, {"$set": {"created_at": created}})
                    x["created_at"] = created
                except Exception:
                    x["created_at"] = 0
            out.append(_serialize_pack(x))
        return out

    # modalità paginata
    total = await db.packs.count_documents(q)
    cur = base_cur.skip(skip).limit(limit)
    items = []
    async for x in cur:
        if not x.get("created_at"):
            try:
                created = int(x["_id"].generation_time.replace(tzinfo=timezone.utc).timestamp())
                await db.packs.update_one({"_id": x["_id"]}, {"$set": {"created_at": created}})
                x["created_at"] = created
            except Exception:
                x["created_at"] = 0
        items.append(_serialize_pack(x))
    return {"items": items, "total": total, "skip": skip, "limit": limit}

@router.post("")
async def create_pack(payload: PackCreate, user_id: str = Depends(get_current_user_id)):
    db = get_db()
    doc = {
        "user_id": user_id,
        "brand": payload.brand,
        "size": int(payload.size),
        "price": float(payload.price),
        "created_at": now_ts(),
    }
    res = await db.packs.insert_one(doc)
    return to_primitive({"_id": res.inserted_id, **doc})

@router.patch("/{pack_id}")
async def update_pack(pack_id: str, payload: PackUpdate, user_id: str = Depends(get_current_user_id)):
    db = get_db()
    upd = {k: v for k, v in payload.model_dump().items() if v is not None}
    if "size" in upd:  upd["size"]  = int(upd["size"])
    if "price" in upd: upd["price"] = float(upd["price"])

    res = await db.packs.update_one({"_id": oid(pack_id), "user_id": user_id}, {"$set": upd})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Pacchetto non trovato")

    x = await db.packs.find_one({"_id": oid(pack_id)})
    return _serialize_pack(x)

@router.get("/stats/overview")
async def packs_overview(user_id: str = Depends(get_current_user_id)):
    """
    Totali lato pacchetti: numero pacchetti, spesa totale, timestamp ultimo pacchetto.
    """
    db = get_db()
    pipeline = [
        {"$match": {"user_id": user_id}},
        {
            "$group": {
                "_id": None,
                "total_packs": {"$sum": 1},
                "total_spent": {"$sum": {"$ifNull": ["$price", 0]}},
                "last_pack_at": {"$max": {"$ifNull": ["$created_at", 0]}},
            }
        }
    ]
    res = {"total_packs": 0, "total_spent": 0.0, "last_pack_at": 0}
    async for row in db.packs.aggregate(pipeline):
        res["total_packs"] = int(row.get("total_packs") or 0)
        res["total_spent"] = float(row.get("total_spent") or 0)
        res["last_pack_at"] = int(row.get("last_pack_at") or 0)
    return res

@router.get("/stats/durata")
async def packs_duration_stats(
    user_id: str = Depends(get_current_user_id),
    days_window: int = Query(180, ge=1, le=365, description="Considera pacchetti creati negli ultimi N giorni (default 180)")
):
    """
    Durata dei pacchetti (in giorni).
    Per ogni pacchetto: created_at -> ultimo smoke collegato (o now se nessuno).
    Ritorna media e mediana.
    """
    db = get_db()
    now = now_ts()
    from_ts = now - days_window * 24 * 3600

    packs_cur = db.packs.find({"user_id": user_id, "created_at": {"$gte": from_ts}})
    durations = []

    async for p in packs_cur:
        pid_str = str(p["_id"])
        created = int(p.get("created_at", now))
        last_smoke = await db.smokes.find_one(
            {"user_id": user_id, "pack_id": pid_str},
            sort=[("ts", -1)]
        )
        end_ts = int(last_smoke["ts"]) if last_smoke else now
        days = max((end_ts - created) / 86400.0, 0.0)
        durations.append(days)

    def mean(xs): return (sum(xs) / len(xs)) if xs else 0.0
    def median(xs):
        n = len(xs)
        if n == 0: return 0.0
        ys = sorted(xs)
        mid = n // 2
        return (ys[mid] if n % 2 == 1 else (ys[mid - 1] + ys[mid]) / 2)

    return {
        "count": len(durations),
        "avg_days": round(mean(durations), 2),
        "median_days": round(median(durations), 2),
    }

@router.get("/consumption")
async def packs_consumption(user_id: str = Depends(get_current_user_id)):
    db = get_db()
    pipeline = [
        {"$match": {"user_id": user_id}},
        {
            "$lookup": {
                "from": "smokes",
                "let": {"pid": {"$toString": "$_id"}, "uid": "$user_id"},
                "pipeline": [
                    {"$match": {"$expr": {"$and": [
                        {"$eq": ["$user_id", "$$uid"]},
                        {"$eq": ["$pack_id", "$$pid"]}
                    ]}}},
                    {"$count": "count"}
                ],
                "as": "smokes_info"
            }
        },
        {"$addFields": {"smokes_count": {"$ifNull": [{"$arrayElemAt": ["$smokes_info.count", 0]}, 0]}}},
        {"$addFields": {
            "remaining": {"$max": [{"$subtract": ["$size", "$smokes_count"]}, 0]},
            "finished": {"$lte": ["$size", "$smokes_count"]}
        }},
        {"$project": {
            "_id": {"$toString": "$_id"},
            "user_id": 1, "brand": 1, "size": 1, "price": 1, "created_at": 1,
            "smokes_count": 1, "remaining": 1, "finished": 1
        }},
        {"$sort": {"created_at": -1}}
    ]
    out = []
    async for x in db.packs.aggregate(pipeline):
        out.append({
            "_id": x["_id"],
            "user_id": x.get("user_id"),
            "brand": x.get("brand"),
            "size": int(x.get("size", 0)),
            "price": float(x.get("price", 0)),
            "created_at": int(x.get("created_at", 0)),
            "smokes_count": int(x.get("smokes_count", 0)),
            "remaining": int(x.get("remaining", 0)),
            "finished": bool(x.get("finished", False)),
        })
    return out

@router.get("/consumption/summary")
async def packs_consumption_summary(user_id: str = Depends(get_current_user_id)):
    db = get_db()
    pipeline = [
        {"$match": {"user_id": user_id}},
        {
            "$lookup": {
                "from": "smokes",
                "let": {"pid": {"$toString": "$_id"}, "uid": "$user_id"},
                "pipeline": [
                    {"$match": {"$expr": {"$and": [
                        {"$eq": ["$user_id", "$$uid"]},
                        {"$eq": ["$pack_id", "$$pid"]}
                    ]}}},
                    {"$count": "count"}
                ],
                "as": "smokes_info"
            }
        },
        {"$addFields": {"smokes_count": {"$ifNull": [{"$arrayElemAt": ["$smokes_info.count", 0]}, 0]}}},
        {"$group": {
            "_id": "$brand",
            "packs": {"$sum": 1},
            "total_size": {"$sum": "$size"},
            "total_smoked": {"$sum": "$smokes_count"},
            "avg_price": {"$avg": "$price"}
        }},
        {"$addFields": {"remaining": {"$max": [{"$subtract": ["$total_size", "$total_smoked"]}, 0]}}},
        {"$project": {
            "brand": "$_id", "_id": 0,
            "packs": 1, "total_size": 1, "total_smoked": 1, "remaining": 1, "avg_price": 1
        }},
        {"$sort": {"brand": 1}}
    ]
    out = []
    async for x in db.packs.aggregate(pipeline):
        out.append({
            "brand": x["brand"],
            "packs": int(x["packs"]),
            "total_size": int(x["total_size"]),
            "total_smoked": int(x["total_smoked"]),
            "remaining": int(x["remaining"]),
            "avg_price": float(x["avg_price"]) if x.get("avg_price") is not None else None
        })
    return out

@router.delete("/{pack_id}")
async def delete_pack(
    pack_id: str,
    user_id: str = Depends(get_current_user_id),
    mode: str = Query("cascade", regex="^(cascade|block|loose)$")
):
    """
    Elimina un pacchetto.
    - mode=cascade (default): elimina anche le smokes collegate.
    - mode=block: se esistono smokes collegate -> 409 Conflict.
    - mode=loose: scollega le smokes (rimuove pack_id, imposta source='loose').
    """
    db = get_db()
    _oid = oid(pack_id)

    pack = await db.packs.find_one({"_id": _oid, "user_id": user_id})
    if not pack:
        raise HTTPException(status_code=404, detail="Pacchetto non trovato")

    linked_filter = {
        "user_id": user_id,
        "$or": [
            {"pack_id": pack_id},            # string
            {"pack_id": str(_oid)},          # string uguale all'OID
            {"pack_id": _oid},               # (vecchi dati eventuali)
        ],
    }
    linked_count = await db.smokes.count_documents(linked_filter)

    if mode == "block" and linked_count > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Impossibile eliminare: ci sono {linked_count} sigarette collegate al pacchetto."
        )

    deleted_smokes = 0
    if mode == "cascade":
        del_res = await db.smokes.delete_many(linked_filter)
        deleted_smokes = del_res.deleted_count
    elif mode == "loose":
        await db.smokes.update_many(
            linked_filter,
            {"$unset": {"pack_id": ""}, "$set": {"source": "loose"}}
        )

    await db.packs.delete_one({"_id": _oid, "user_id": user_id})

    return {"ok": True, "mode": mode, "linked_smokes_before": linked_count, "deleted_smokes": deleted_smokes}
