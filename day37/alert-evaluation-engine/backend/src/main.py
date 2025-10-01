from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn

from .api.evaluation import router as evaluation_router
from .config.settings import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(evaluation_router, prefix=f"{settings.API_V1_STR}/evaluation", tags=["evaluation"])

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Alert Evaluation Engine</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { color: #2c3e50; }
                .status { color: #27ae60; font-weight: bold; }
                .endpoint { background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1 class="header">🚨 Alert Evaluation Engine</h1>
            <p class="status">Status: Running</p>
            <h2>Available Endpoints:</h2>
            <div class="endpoint">
                <strong>GET /api/v1/evaluation/rules</strong> - List alert rules
            </div>
            <div class="endpoint">
                <strong>POST /api/v1/evaluation/rules</strong> - Create alert rule
            </div>
            <div class="endpoint">
                <strong>GET /api/v1/evaluation/alerts/active</strong> - Get active alerts
            </div>
            <div class="endpoint">
                <strong>POST /api/v1/evaluation/evaluate</strong> - Trigger evaluation
            </div>
            <div class="endpoint">
                <strong>GET /api/v1/evaluation/metrics/evaluation</strong> - Engine metrics
            </div>
            <p><a href="/docs">📚 Interactive API Documentation</a></p>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "alert-evaluation-engine"}

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
