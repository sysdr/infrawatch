import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import router as v1_router
from app.api.v2 import router as v2_router
from app.middleware.versioning import VersioningMiddleware, DeprecationMiddleware
from app.core.registry import version_registry
from app.core.config import settings

app = FastAPI(title="Infrastructure Management API", description="API Versioning Demo - Day 120", version="2.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000","http://127.0.0.1:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"], expose_headers=["Sunset","Deprecation","X-API-Version","Link"])
app.add_middleware(VersioningMiddleware)
app.add_middleware(DeprecationMiddleware)

@app.middleware("http")
async def add_timing(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Response-Time"] = f"{(time.time()-start)*1000:.2f}ms"
    return response

app.include_router(v1_router, prefix="/api/v1", tags=["v1"])
app.include_router(v2_router, prefix="/api/v2", tags=["v2"])

@app.get("/")
async def root():
    return {"service":"Infrastructure Management API","current_version":"v2","supported_versions":version_registry.get_active_versions(),"docs":"/docs"}

@app.get("/api/versions")
async def list_versions():
    return {"versions":version_registry.get_all_versions(),"recommended":"v2","deprecated":version_registry.get_deprecated_versions()}

@app.get("/api/versions/{version}")
async def get_version_info(version: str):
    info = version_registry.get_version(version)
    if not info:
        return JSONResponse(status_code=404, content={"error":f"Version {version} not found"})
    return info

@app.get("/api/migration/{from_version}/{to_version}")
async def get_migration_guide(from_version: str, to_version: str):
    guide = version_registry.get_migration_guide(from_version, to_version)
    if not guide:
        return JSONResponse(status_code=404, content={"error":f"No migration guide from {from_version} to {to_version}"})
    return guide

@app.get("/health")
async def health():
    return {"status":"healthy","api_version":"2.0.0"}
