from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import dashboard, filters, drilldown
from app.core.database import engine, Base
from app.core.redis_client import redis_client
import asyncio

app = FastAPI(title="Interactive Dashboard API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize sample data in background
    import asyncio
    async def init_data():
        from app.services.data_generator import DataGenerator
        generator = DataGenerator()
        await generator.generate_sample_data()
        print("✅ Database initialized with sample data")
    
    # Run data generation in background so server can start immediately
    asyncio.create_task(init_data())
    print("🚀 Server started, initializing data in background...")

@app.on_event("shutdown")
async def shutdown():
    await redis_client.close()

# Include routers
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(filters.router, prefix="/api/filters", tags=["filters"])
app.include_router(drilldown.router, prefix="/api/drilldown", tags=["drilldown"])

@app.get("/")
async def root():
    return {"message": "Interactive Dashboard API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
