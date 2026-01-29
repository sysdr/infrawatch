from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import settings
from app.core.database import engine
from app.models.log import Base

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Include routes
app.include_router(router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "log-search-engine"}
