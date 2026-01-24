from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from datetime import datetime
import random

from app.database import init_db, get_db
from app.api import topology, resources, costs, reports
from app.services.websocket_service import ws_manager
from app.utils.cache import cache_manager
from app.models.resource import Resource, ResourceDependency, Metric, Cost

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await cache_manager.connect()
    await init_db()
    await seed_data()
    
    # Start background tasks
    asyncio.create_task(simulate_metrics())
    
    yield
    
    # Shutdown
    await cache_manager.disconnect()

app = FastAPI(title="Infrastructure UI API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(topology.router)
app.include_router(resources.router)
app.include_router(costs.router)
app.include_router(reports.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    try:
        await ws_manager.connect(websocket, client_id)
        try:
            while True:
                data = await websocket.receive_text()
                # Echo back for demo
                await ws_manager.send_personal_message({"message": f"Received: {data}"}, websocket)
        except WebSocketDisconnect:
            ws_manager.disconnect(websocket, client_id)
        except Exception as e:
            print(f"WebSocket error for client {client_id}: {e}")
            ws_manager.disconnect(websocket, client_id)
    except Exception as e:
        print(f"Failed to accept WebSocket connection for client {client_id}: {e}")
        try:
            await websocket.close()
        except:
            pass

async def seed_data():
    """Seed initial demo data"""
    from app.database import AsyncSessionLocal
    from datetime import timedelta
    async with AsyncSessionLocal() as db:
        try:
            # Check if data exists
            from sqlalchemy import select
            result = await db.execute(select(Resource).limit(1))
            if result.scalar_one_or_none():
                return  # Data already exists
            
            # Create sample resources
            resources = []
            providers = ['aws', 'gcp', 'azure']
            types = ['ec2', 'rds', 'elb', 'compute', 'database', 'storage']
            regions = ['us-east-1', 'us-west-2', 'eu-west-1']
            
            for i in range(20):
                resource = Resource(
                    id=f"resource-{i:03d}",
                    resource_type=random.choice(types),
                    cloud_provider=random.choice(providers),
                    region=random.choice(regions),
                    name=f"resource-{i:03d}",
                    status='running',
                    tags={
                        'environment': random.choice(['production', 'staging', 'development']),
                        'owner': random.choice(['team-a', 'team-b', 'team-c']),
                        'cost_center': random.choice(['engineering', 'data', 'platform'])
                    }
                )
                resources.append(resource)
                db.add(resource)
            
            await db.flush()
            
            # Create dependencies
            for i in range(15):
                dep = ResourceDependency(
                    source_id=random.choice(resources).id,
                    target_id=random.choice(resources).id,
                    dependency_type=random.choice(['network', 'data', 'service']),
                    strength=random.uniform(0.5, 1.0)
                )
                db.add(dep)
            
            # Create metrics
            for resource in resources:
                for hour in range(24):
                    metric = Metric(
                        resource_id=resource.id,
                        timestamp=datetime.utcnow() - timedelta(hours=hour),
                        cpu_usage=random.uniform(20, 80),
                        memory_usage=random.uniform(30, 90),
                        network_in=random.uniform(100, 1000),
                        network_out=random.uniform(50, 500),
                        error_rate=random.uniform(0, 5)
                    )
                    db.add(metric)
            
            # Create costs
            for resource in resources:
                for day in range(90):
                    cost = Cost(
                        resource_id=resource.id,
                        date=datetime.utcnow() - timedelta(days=day),
                        amount=random.uniform(10, 500),
                        currency='USD',
                        service_type=resource.resource_type
                    )
                    db.add(cost)
            
            await db.commit()
            print("✓ Seed data created")
            
        except Exception as e:
            print(f"Seed data error: {e}")
            await db.rollback()
        finally:
            await db.close()

async def simulate_metrics():
    """Background task to update metrics periodically"""
    while True:
        try:
            await asyncio.sleep(5)  # Update every 5 seconds
            
            # Broadcast metric update
            message = {
                'type': 'metric_update',
                'timestamp': datetime.utcnow().isoformat(),
                'data': {
                    'cpu': random.uniform(20, 80),
                    'memory': random.uniform(30, 90)
                }
            }
            await ws_manager.broadcast(message)
            
        except Exception as e:
            print(f"Metric simulation error: {e}")
            await asyncio.sleep(5)
