from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routes import template_routes, test_routes
from app.services.template_service import TemplateService
import uvicorn

app = FastAPI(
    title="Notification Template Engine",
    description="Dynamic template system for multi-channel notifications",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize template service
template_service = TemplateService()

app.include_router(template_routes.router, prefix="/api/templates", tags=["templates"])
app.include_router(test_routes.router, prefix="/api/test", tags=["testing"])

@app.on_event("startup")
async def startup_event():
    await template_service.initialize()

@app.get("/")
async def root():
    return {"message": "Notification Template Engine API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "template-engine"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
