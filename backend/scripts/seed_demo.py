import os
import random
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from pymongo import MongoClient

# ---- config ----
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGO_DB    = os.getenv("MONGO_DB", "smokemeter")
USER_EMAIL  = os.getenv("SEED_USER_EMAIL", "demo@example.com")

# quanta roba generare
NUM_PACKS            = 10    # numero pacchetti da generare
DAYS_BACK_MAX        = 60    # i pacchetti saranno inseriti negli ultimi N giorni
LOOSE_SMOKES_COUNT   = 25    # quante “loose” aggiungere
EXTRA_RECENT_SMOKED  = 12    # <-- nuovo: fumate 'smoked' nelle ultime 24h per popolare la card "intervallo"
CLEAR_EXISTING_DATA  = True  # se True, cancella packs/smokes dell'utente prima

BRANDS = [
    ("Camel", 7.00), ("Marlboro", 7.20), ("Winston", 6.50), ("Philip Morris", 7.10),
    ("Chesterfield", 6.80), ("Lucky Strike", 7.00)
]

SIZES = [20, 20, 20, 10]  # più probabilità per 20

# mix di tipi — fumate vere prevalenti
TYPES = ["smoked"] * 85 + ["wasted"] * 8 + ["gifted"] * 7


def now_ts_utc() -> int:
    return int(datetime.now(timezone.utc).timestamp())


def rand_ts_in_range(ts_from: int, ts_to: int) -> int:
    if ts_to <= ts_from:
        return ts_from
    return random.randint(ts_from, ts_to)


def mean(xs):
    return (sum(xs) / len(xs)) if xs else 0.0


def median(xs):
    n = len(xs)
    if n == 0:
        return 0.0
    ys = sorted(xs)
    mid = n // 2
    return ys[mid] if n % 2 == 1 else (ys[mid - 1] + ys[mid]) / 2


def sanity_check_intervals(db, user_id_str, limit=200):
    """
    Calcola gli intervalli (in minuti) tra fumate consecutive type='smoked'
    come fa l'endpoint /smokes/stats/intervallo e stampa il risultato.
    """
    cur = db.smokes.find({"user_id": user_id_str, "type": "smoked"}).sort("ts", -1).limit(limit)
    ts_list = []
    for x in cur:
        ts_list.append(int(x["ts"]))
    ts_list.sort()  # ascendente

    deltas = []
    for i in range(1, len(ts_list)):
        deltas.append((ts_list[i] - ts_list[i - 1]) / 60.0)  # minuti

    m = mean(deltas)
    md = median(deltas)
    print(f"[CHECK] Intervalli 'smoked': sample={len(deltas)}, mean={m:.1f} min, median={md:.1f} min")
    return len(deltas), m, md


def main():
    assert MONGODB_URI, "MONGODB_URI mancante nel .env"
    client = MongoClient(MONGODB_URI)
    db = client[MONGO_DB]

    # 1) trova utente
    user_doc = db.users.find_one({"email": USER_EMAIL})
    if not user_doc:
        print(f"[ERRORE] Utente {USER_EMAIL} non trovato. Crea prima l’utente via /auth/register.")
        return

    user_id_str = str(user_doc["_id"])
    print(f"[OK] User: {USER_EMAIL}  id={user_id_str}")

    # 2) pulizia opzionale
    if CLEAR_EXISTING_DATA:
        res1 = db.packs.delete_many({"user_id": user_id_str})
        res2 = db.smokes.delete_many({"user_id": user_id_str})
        print(f"[CLEAN] packs: {res1.deleted_count}, smokes: {res2.deleted_count}")

    # 3) genera pacchetti + smokes collegate
    now = now_ts_utc()
    packs_inserted = []
    total_smokes_generated = 0

    for _ in range(NUM_PACKS):
        brand, base_price = random.choice(BRANDS)
        size = random.choice(SIZES)
        # variazione prezzo piccola
        price = round(base_price + random.uniform(-0.3, 0.3), 2)

        # created_at tra oggi e N giorni fa
        created_at = now - random.randint(0, DAYS_BACK_MAX) * 24 * 3600
        pack_doc = {
            "user_id": user_id_str,
            "brand": brand,
            "size": size,
            "price": float(price),
            "created_at": created_at
        }
        res = db.packs.insert_one(pack_doc)
        pack_id_str = str(res.inserted_id)

        packs_inserted.append({**pack_doc, "_id": res.inserted_id})

        # quante sigarette registrare (non superare size; lasciamo 0-5 come “resto” possibile)
        to_consume = max(0, size - random.randint(0, 5))

        # distribuisci le smokes tra created_at e (created_at + ~3-7 giorni)
        span_days = random.randint(3, 7)
        ts_to = created_at + span_days * 24 * 3600

        used = 0
        while used < to_consume:
            t = random.choice(TYPES)
            ts = rand_ts_in_range(created_at, ts_to)
            smoke = {
                "user_id": user_id_str,
                "pack_id": pack_id_str,
                "type": t,
                "ts": ts,
                "source": "pack",
                "brand": brand  # comodità per stats per brand
            }
            db.smokes.insert_one(smoke)
            used += 1
            total_smokes_generated += 1

    print(f"[OK] Inserted packs: {len(packs_inserted)}  | generated smokes from packs: {total_smokes_generated}")

    # 4) aggiungi alcune “loose” senza pacchetto (anche non-smoked, ma spesso smoked)
    loose_added = 0
    for _ in range(LOOSE_SMOKES_COUNT):
        brand = random.choice(BRANDS)[0] if random.random() < 0.7 else None
        # nelle ultime 2 settimane (random ore/minuti)
        ts = now - random.randint(0, 14) * 24 * 3600 - random.randint(0, 23) * 3600 - random.randint(0, 59) * 60
        t = random.choice(TYPES)
        doc = {
            "user_id": user_id_str,
            "type": t,
            "ts": ts,
            "source": "loose"
        }
        if brand:
            doc["brand"] = brand
        db.smokes.insert_one(doc)
        loose_added += 1

    print(f"[OK] Added loose smokes: {loose_added}")

    # 5) NEW: batch di fumate 'smoked' recenti per popolare "intervallo"
    #    Le spaziature sono random nelle ultime 24 ore → garantisce sample > 0 nel widget.
    recent_added = 0
    last_24h_from = now - 24 * 3600
    # scegliamo un brand qualsiasi per uniformità (non serve il pack_id, sono loose "smoked")
    recent_brand = random.choice(BRANDS)[0]
    # generiamo timestamp random crescenti nell’ultima giornata
    offsets = sorted(random.sample(range(1, 24 * 3600 - 1), k=EXTRA_RECENT_SMOKED))
    for off in offsets:
        ts = last_24h_from + off
        doc = {
            "user_id": user_id_str,
            "type": "smoked",
            "ts": ts,
            "source": "loose",
            "brand": recent_brand
        }
        db.smokes.insert_one(doc)
        recent_added += 1

    print(f"[OK] Added recent 'smoked' (last 24h): {recent_added}")

    # 6) Sanity check: calcola media/mediana intervalli come fa l'endpoint
    sanity_check_intervals(db, user_id_str, limit=200)

    print("[DONE] Seeding terminato con successo.")


if __name__ == "__main__":
    main()
