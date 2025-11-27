from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import templates_router, reports_router
from app.database import init_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Report Templates API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
def startup():
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized")

# Include routers
app.include_router(templates_router)
app.include_router(reports_router)

@app.get("/")
def read_root():
    return {"message": "Report Templates API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
