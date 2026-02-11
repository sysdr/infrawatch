import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse

from .api import api_router
from .core.config import settings
from .models.remediation import Base
from .core.database import engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "error": "internal_error"}
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Simple HTML dashboard (no build required) - always at /dashboard
DASHBOARD_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Remediation Dashboard</title>
<style>body{font-family:system-ui;max-width:900px;margin:2rem auto;padding:1rem;background:#f5f5f5}
h1{color:#1a237e}.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin:2rem 0}
.card{background:white;padding:1.5rem;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,.1)}
.card h3{margin:0 0 .5rem;font-size:.9rem;color:#666}.card .val{font-size:2rem;font-weight:bold}
.err{color:#c62828;padding:1rem;background:#ffebee;border-radius:8px}a{color:#1a237e}</style></head>
<body><h1>Remediation Actions System</h1><div id="content"><p>Loading...</p></div>
<script>fetch('/api/v1/remediation/stats').then(r=>r.ok?r.json():Promise.reject(r.status))
.then(d=>{document.getElementById('content').innerHTML='<div class="cards">'+
'<div class="card"><h3>Total Actions</h3><div class="val">'+d.total_actions+'</div></div>'+
'<div class="card"><h3>Pending</h3><div class="val">'+d.pending+'</div></div>'+
'<div class="card"><h3>Completed</h3><div class="val">'+d.completed+'</div></div>'+
'<div class="card"><h3>Success Rate</h3><div class="val">'+d.success_rate+'%</div></div>'+
'</div><p><a href="/docs">API Docs</a> | Run ./demo.sh to populate data</p>';})
.catch(e=>{document.getElementById('content').innerHTML='<div class="err">Cannot load stats. Is the backend running?</div>';});</script>
</body></html>"""

@app.get("/dashboard", response_class=HTMLResponse)
async def simple_dashboard():
    return DASHBOARD_HTML

# Serve frontend static files when dist exists (single-server mode)
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")
    @app.get("/")
    async def root_spa():
        return FileResponse(FRONTEND_DIST / "index.html")
    @app.get("/favicon.ico")
    async def favicon():
        path = FRONTEND_DIST / "favicon.ico"
        return FileResponse(path) if path.exists() else JSONResponse(status_code=204)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api"):
            return JSONResponse(status_code=404, content={"detail": "Not found"})
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")
else:
    @app.get("/")
    async def root():
        return {"message": "Remediation Actions System API", "version": settings.VERSION, "docs": "/docs"}
