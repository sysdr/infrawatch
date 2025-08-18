from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.metrics_api import router as metrics_router
from config.database import init_db
import uvicorn
import time

app = FastAPI(title="Metrics Data Models API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database with retry logic
def initialize_database():
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            print(f"🔄 Attempting to initialize database (attempt {attempt + 1}/{max_retries})")
            init_db()
            print("✅ Database initialized successfully!")
            return True
        except Exception as e:
            print(f"❌ Database initialization failed (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("💥 Failed to initialize database after all retries")
                raise
    
    return False

# Initialize database
initialize_database()

# Include routers
app.include_router(metrics_router)

@app.get("/")
async def root():
    return {"message": "Metrics Data Models API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "metrics-api"}

if __name__ == "__main__":
    print("🚀 Starting Metrics Data Models API...")
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )
