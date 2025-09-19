async def ensure_indexes(db):
    await db.users.create_index("email", unique=True)
    await db.logs.create_index([("user_id", 1), ("ts", -1)])
    await db.metrics_daily.create_index([("user_id", 1), ("date", -1)], unique=True)