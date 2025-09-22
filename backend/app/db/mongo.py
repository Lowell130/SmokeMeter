from motor.motor_asyncio import AsyncIOMotorClient
from ..core.config import settings

client: AsyncIOMotorClient | None = None

def get_db():
    if client is None:
        raise RuntimeError("Mongo client non inizializzato. Hai chiamato connect() all'avvio?")
    return client[settings.MONGO_DB]     # <— usa il nome DB dal .env

async def connect():
    global client
    client = AsyncIOMotorClient(settings.MONGODB_URI)

async def disconnect():
    global client
    if client is not None:
        client.close()
        client = None
