from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, get_db
from app.models.analytics import Base
from app.routers import analytics, ml, reports
from app.services.data_generator import seed_database

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Day 112 Analytics Integration API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(ml.router,        prefix="/api/ml",        tags=["ml"])
app.include_router(reports.router,   prefix="/api/reports",   tags=["reports"])

@app.on_event("startup")
def startup():
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        count = seed_database(db)
        print(f"[startup] Database seeded: {count} hourly metric rows")
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "healthy", "service": "analytics-integration", "version": "1.0.0"}
