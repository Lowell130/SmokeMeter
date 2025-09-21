from motor.motor_asyncio import AsyncIOMotorClient
from ..core.config import settings

client: AsyncIOMotorClient | None = None

def get_db():
    return client["smoketracker"]

async def connect():
    global client
    client = AsyncIOMotorClient(settings.MONGODB_URI)

async def disconnect():
    global client
    client.close()