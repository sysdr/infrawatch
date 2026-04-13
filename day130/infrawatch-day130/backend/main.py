from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db
from app.api import subscriptions, notifications, users, vapid
from app.services.scheduler_service import start_scheduler, stop_scheduler
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    start_scheduler()
    yield
    stop_scheduler()

app = FastAPI(title="InfraWatch Push Notifications API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:3130","http://localhost:5173","http://localhost:3000"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(subscriptions.router)
app.include_router(notifications.router)
app.include_router(users.router)
app.include_router(vapid.router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "infrawatch-push-notifications", "day": 130}
