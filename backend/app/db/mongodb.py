# backend/app/db/mongodb.py
from motor.motor_asyncio import AsyncIOMotorClient
from . import indexes
from ..core.config import settings

client: AsyncIOMotorClient | None = None

def get_db():
    return client[settings.MONGO_DB]

async def connect_db():
    global client
    client = AsyncIOMotorClient(settings.MONGO_URI)
    await indexes.ensure_indexes(get_db())

async def close_db():
    if client:
        client.close()
