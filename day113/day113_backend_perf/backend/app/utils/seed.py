import asyncio
import random
import uuid
from sqlalchemy import select, func
from app.db.session import AsyncSessionLocal, engine, Base
from app.models.user import User, Team, Role
TEAM_NAMES = ["Platform Engineering", "Frontend Guild", "Data Science", "SRE", "Security"]
DOMAINS = ["acme.io", "techcorp.dev", "startup.ai"]
async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(func.count(Team.id)))
        if result.scalar_one() >= len(TEAM_NAMES):
            print("Database already seeded.")
            return
        teams = []
        for name in TEAM_NAMES:
            t = Team(id=str(uuid.uuid4()), name=name)
            db.add(t)
            teams.append(t)
        await db.flush()
        for i in range(100):
            team = random.choice(teams)
            domain = random.choice(DOMAINS)
            u = User(id=str(uuid.uuid4()), email=f"user{i:04d}@{domain}", name=f"Engineer {i:04d}", team_id=team.id, is_active=random.random() > 0.1, login_count=random.randint(0, 500))
            db.add(u)
        await db.commit()
        print(f"Seeded {len(TEAM_NAMES)} teams and 100 users.")
if __name__ == "__main__":
    asyncio.run(seed())
