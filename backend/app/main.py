from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .db.mongodb import connect_db, close_db
from .routers import auth, users, logs, metrics




app = FastAPI(title="SmokeMetric API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",              # sviluppo locale
       
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
async def startup():
    await connect_db()


@app.on_event("shutdown")
async def shutdown():
    await close_db()


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(logs.router)
app.include_router(metrics.router)


@app.get("/")
async def root():
    return {"ok": True, "name": "SmokeMetric API"}