from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis.asyncio as redis
import os
from dotenv import load_dotenv

from app.api import auth_router
from app.security import security_router

load_dotenv()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Password Security System", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Global Redis connection
redis_client = None

@app.on_event("startup")
async def startup_event():
    global redis_client
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_client = redis.from_url(redis_url, decode_responses=True)
    app.state.redis = redis_client

@app.on_event("shutdown")
async def shutdown_event():
    if redis_client:
        await redis_client.close()

# Include routers
app.include_router(auth_router.router, prefix="/api/auth", tags=["authentication"])
app.include_router(security_router.router, prefix="/api/security", tags=["security"])

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
