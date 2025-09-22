from fastapi import APIRouter, Depends, HTTPException, Query
from ..core.deps import get_current_user_id
from ..db.mongo import get_db
from ..schemas.pack import PackCreate, PackUpdate
from ..utils import now_ts, oid, to_primitive
from datetime import timezone

router = APIRouter(prefix="/packs", tags=["packs"])

@router.get("")
async def list_packs(user_id: str = Depends(get_current_user_id)):
    db = get_db()
    cur = db.packs.find({"user_id": user_id}).sort("created_at", -1)
    out = []
    async for x in cur:
        # Fallback: se manca created_at, stimiamo dal ObjectId.generation_time
        created = x.get("created_at")
        if not created:
            try:
                created = int(x["_id"].generation_time.replace(tzinfo=timezone.utc).timestamp())
                # (opzionale) backfill nel DB per avere il campo d'ora in poi
                await db.packs.update_one({"_id": x["_id"]}, {"$set": {"created_at": created}})
            except Exception:
                created = 0

        out.append({
            "_id": str(x["_id"]),
            "user_id": x.get("user_id"),
            "brand": x.get("brand"),
            "size": int(x.get("size", 0)),
            "price": float(x.get("price", 0)),
            "created_at": int(created),
        })
    return out

@router.post("")
async def create_pack(payload: PackCreate, user_id: str = Depends(get_current_user_id)):
    db = get_db()
    doc = {
        "user_id": user_id,                         # già stringa dal JWT
        "brand": payload.brand,
        "size": int(payload.size),
        "price": float(payload.price),
        "created_at": now_ts(),
    }
    res = await db.packs.insert_one(doc)
    # NON tornare l'InsertOneResult, né doc con _id ObjectId
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
    return {
        "_id": str(x["_id"]),
        "user_id": x.get("user_id"),
        "brand": x.get("brand"),
        "size": int(x.get("size", 0)),
        "price": float(x.get("price", 0)),
        "created_at": int(x.get("created_at", 0)),
    }

@router.delete("/{pack_id}")
async def delete_pack(pack_id: str, user_id: str = Depends(get_current_user_id)):
    db = get_db()
    await db.packs.delete_one({"_id": oid(pack_id), "user_id": user_id})
    return {"ok": True}


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
        # cast “pulito” per JSON
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
    pack = await db.packs.find_one({"_id": oid(pack_id), "user_id": user_id})
    if not pack:
        raise HTTPException(status_code=404, detail="Pacchetto non trovato")

    # quante smokes collegate a questo pacchetto per l'utente
    linked_filter = {"user_id": user_id, "pack_id": pack_id}
    linked_count = await db.smokes.count_documents(linked_filter)

    if mode == "block" and linked_count > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Impossibile eliminare: ci sono {linked_count} sigarette collegate al pacchetto."
        )

    if mode == "cascade":
        # elimina smokes collegate
        del_res = await db.smokes.delete_many(linked_filter)
        deleted_smokes = del_res.deleted_count
    elif mode == "loose":
        # scollega smokes -> diventano “loose”
        upd_res = await db.smokes.update_many(
            linked_filter,
            {"$unset": {"pack_id": ""}, "$set": {"source": "loose"}}
        )
        deleted_smokes = 0  # nessuna eliminata
    else:
        deleted_smokes = 0  # block o nessuna azione ulteriore

    # elimina il pack
    await db.packs.delete_one({"_id": oid(pack_id), "user_id": user_id})

    return {"ok": True, "mode": mode, "linked_smokes_before": linked_count, "deleted_smokes": deleted_smokes}