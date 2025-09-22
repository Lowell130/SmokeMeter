from fastapi import APIRouter, Depends
from ..core.deps import get_current_user_id
from ..db.mongo import get_db
from ..schemas.smoke import SmokeCreate
from ..schemas.smoke import SmokeUpdate
from ..utils import now_ts, oid, to_primitive
from fastapi import HTTPException
from fastapi import APIRouter, Depends, HTTPException, Query



router = APIRouter(prefix="/smokes", tags=["smokes"])

@router.post("")
async def create_smoke(payload: SmokeCreate, user_id: str = Depends(get_current_user_id)):
    db = get_db()

    doc = {
        "user_id": user_id,
        "type": payload.type,
        "ts": now_ts(),
    }

    if payload.pack_id:
        # verifica esistenza pack dell’utente
        pack = await db.packs.find_one({"_id": oid(payload.pack_id), "user_id": user_id})
        if not pack:
            raise HTTPException(status_code=404, detail="Pacchetto non trovato")
        doc["pack_id"] = payload.pack_id
        doc["source"] = "pack"
        doc["brand"] = pack.get("brand")  # opzionale: copia brand del pack, utile nelle viste
    else:
        # smoke “loose” (senza pacchetto)
        doc["source"] = "loose"
        if payload.brand:
            doc["brand"] = payload.brand

    res = await db.smokes.insert_one(doc)
    return to_primitive({"_id": res.inserted_id, **doc})

# POST /smokes – aggiungi evento con type
@router.post("")
async def add_smoke(payload: SmokeCreate, user_id: str = Depends(get_current_user_id)):
    db = get_db()
    doc = {"user_id": user_id, "pack_id": payload.pack_id, "type": payload.type, "ts": now_ts()}
    res = await db.smokes.insert_one(doc)
    return to_primitive({"_id": res.inserted_id, **doc})

# PATCH /smokes/{smoke_id} – cambia tipo (smoked/wasted/gifted)
@router.patch("/{smoke_id}")
async def update_smoke(smoke_id: str, payload: SmokeUpdate, user_id: str = Depends(get_current_user_id)):
    db = get_db()
    upd = {k: v for k, v in payload.model_dump().items() if v is not None}
    await db.smokes.update_one({"_id": oid(smoke_id), "user_id": user_id}, {"$set": upd})
    x = await db.smokes.find_one({"_id": oid(smoke_id)})
    return to_primitive(x)

# GET /smokes – includi il type
@router.get("")
async def list_smokes(user_id: str = Depends(get_current_user_id)):
    db = get_db()
    cur = db.smokes.find({"user_id": user_id}).sort("ts", -1)
    out = []
    async for x in cur:
        out.append({
            "_id": str(x["_id"]),
            "user_id": x.get("user_id"),
            "pack_id": x.get("pack_id"),
            "type": x.get("type","smoked"),
            "ts": int(x.get("ts", 0)),
        })
    return out

# GET /smokes/stats/overview – conta solo 'smoked'
@router.get("/stats/overview")
async def stats_overview(user_id: str = Depends(get_current_user_id)):
    db = get_db()
    total_smokes = await db.smokes.count_documents({"user_id": user_id, "type": "smoked"})
    # somma spesa come prima (lookup sui packs); la spesa è a pacchetto, non per singola sigaretta
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$addFields": {"pack_oid": {"$toObjectId": "$pack_id"}}},
        {"$lookup": {"from": "packs", "localField": "pack_oid", "foreignField": "_id", "as": "pack"}},
        {"$unwind": {"path": "$pack", "preserveNullAndEmptyArrays": True}},
        {"$group": {"_id": "$pack._id", "price": {"$max": "$pack.price"}}},  # evita somma multipla dello stesso pack
        {"$group": {"_id": None, "spesa": {"$sum": {"$ifNull": ["$price", 0]}}}},
    ]
    spesa = 0
    async for row in db.smokes.aggregate(pipeline):
        spesa = row.get("spesa", 0)
    return {"total_smokes": total_smokes, "total_spent": spesa}



@router.get("/stats/by-hour")
async def stats_by_hour(
    days: int = Query(7, ge=1, le=90, description="Intervallo in giorni (default 7)"),
    user_id: str = Depends(get_current_user_id),
):
    """
    Conteggio sigarette 'smoked' per ogni ora (0..23) nelle ultime 'days' giornate.
    Timezone: Europe/Rome
    """
    db = get_db()
    to_ts = now_ts()
    from_ts = to_ts - days * 24 * 3600

    pipeline = [
        {"$match": {"user_id": user_id, "type": "smoked", "ts": {"$gte": from_ts, "$lte": to_ts}}},
        {"$addFields": {"dt": {"$toDate": {"$multiply": ["$ts", 1000]}}}},
        {
            "$group": {
                "_id": {
                    "$hour": {"date": "$dt", "timezone": "Europe/Rome"}
                },
                "count": {"$sum": 1}
            }
        },
        {"$project": {"_id": 0, "hour": "$_id", "count": 1}},
        {"$sort": {"hour": 1}},
    ]

    # inizializza tutte le ore a 0
    result = [{"hour": h, "count": 0} for h in range(24)]
    async for row in db.smokes.aggregate(pipeline):
        h = int(row.get("hour", 0))
        if 0 <= h <= 23:
            result[h]["count"] = int(row.get("count", 0))

    # risposta compatibile col frontend
    return {
        "days": days,
        "timezone": "Europe/Rome",
        "hours": [f"{h:02d}" for h in range(24)],
        "data": [x["count"] for x in result],
        "total": sum(x["count"] for x in result),
    }