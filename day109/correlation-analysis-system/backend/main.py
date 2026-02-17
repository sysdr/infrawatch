from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.database import init_db
from app.routes import correlation_routes
import uvicorn

app = FastAPI(title="Correlation Analysis System", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database (optional: app starts even if PostgreSQL is down)
try:
    init_db()
except Exception as e:
    import logging
    logging.getLogger("uvicorn.error").warning("Database not available: %s. API will run with limited functionality.", e)

# Include routes
app.include_router(correlation_routes.router)


@app.get("/")
def root():
    return {"message": "Correlation Analysis System API", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
