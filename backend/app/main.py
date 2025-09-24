from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .db.mongo import connect, disconnect
from .routers import auth, users, packs, smokes

app = FastAPI(title="Smoke Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_ORIGINS, "https://smokio.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(packs.router)
app.include_router(smokes.router)

@app.on_event("startup")
async def startup():
    await connect()

@app.on_event("shutdown")
async def shutdown():
    await disconnect()