from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import dashboard, widgets, templates
from app.core.database import engine, Base, AsyncSessionLocal
from app.models import Template
from sqlalchemy import select
import asyncio

app = FastAPI(title="Dashboard Grid System API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def seed_default_templates():
    """Seed default templates if they don't exist"""
    async with AsyncSessionLocal() as session:
        # Check if templates already exist
        result = await session.execute(select(Template))
        existing_templates = result.scalars().all()
        
        if len(existing_templates) == 0:
            # Create default templates
            default_templates = [
                {
                    "name": "Monitoring Dashboard",
                    "description": "A comprehensive monitoring dashboard with CPU, Memory, and Alerts",
                    "layout": [
                        {"i": "widget1", "x": 0, "y": 0, "w": 12, "h": 4},
                        {"i": "widget2", "x": 12, "y": 0, "w": 6, "h": 3},
                        {"i": "widget3", "x": 0, "y": 4, "w": 12, "h": 4},
                        {"i": "widget4", "x": 12, "y": 3, "w": 6, "h": 3},
                    ],
                    "widget_configs": [
                        {
                            "widget_type": "cpu_chart",
                            "title": "CPU Usage Chart",
                            "config": {"refreshInterval": 5000},
                            "position": {"x": 0, "y": 0, "w": 12, "h": 4}
                        },
                        {
                            "widget_type": "memory_gauge",
                            "title": "Memory Gauge",
                            "config": {"threshold": 80},
                            "position": {"x": 12, "y": 0, "w": 6, "h": 3}
                        },
                        {
                            "widget_type": "alert_list",
                            "title": "Alert List",
                            "config": {"limit": 10},
                            "position": {"x": 0, "y": 4, "w": 12, "h": 4}
                        },
                        {
                            "widget_type": "metric_card",
                            "title": "Metric Card",
                            "config": {"metric": "requests_per_second"},
                            "position": {"x": 12, "y": 3, "w": 6, "h": 3}
                        }
                    ],
                    "is_public": 1
                },
                {
                    "name": "Simple Overview",
                    "description": "A simple dashboard with CPU and Memory widgets",
                    "layout": [
                        {"i": "widget1", "x": 0, "y": 0, "w": 12, "h": 4},
                        {"i": "widget2", "x": 12, "y": 0, "w": 6, "h": 3},
                    ],
                    "widget_configs": [
                        {
                            "widget_type": "cpu_chart",
                            "title": "CPU Usage Chart",
                            "config": {"refreshInterval": 5000},
                            "position": {"x": 0, "y": 0, "w": 12, "h": 4}
                        },
                        {
                            "widget_type": "memory_gauge",
                            "title": "Memory Gauge",
                            "config": {"threshold": 80},
                            "position": {"x": 12, "y": 0, "w": 6, "h": 3}
                        }
                    ],
                    "is_public": 1
                }
            ]
            
            for template_data in default_templates:
                template = Template(**template_data)
                session.add(template)
            
            await session.commit()
            print("Default templates seeded successfully")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed default templates
    await seed_default_templates()

app.include_router(dashboard.router, prefix="/api/dashboards", tags=["dashboards"])
app.include_router(widgets.router, prefix="/api/widgets", tags=["widgets"])
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "dashboard-grid"}
