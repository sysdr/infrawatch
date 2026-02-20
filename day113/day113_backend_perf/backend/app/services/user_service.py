import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, func
from app.models.user import User, Team
from app.services.cache import cache_service
from app.schemas.user import UserOut, PaginatedUsers
logger = logging.getLogger(__name__)
PAGE_SIZE = 25
async def get_users_paginated(db: AsyncSession, team_id: str | None, after_cursor: str | None, fields: list[str] | None) -> PaginatedUsers:
    cache_key = f"users:team:{team_id or 'all'}:cursor:{after_cursor or 'start'}"
    cached = await cache_service.get(cache_key)
    if cached:
        return PaginatedUsers(**cached, cached=True)
    stmt = select(User).order_by(User.id)
    if team_id:
        stmt = stmt.where(User.team_id == team_id, User.is_active == True)
    if after_cursor:
        stmt = stmt.where(User.id > after_cursor)
    stmt = stmt.limit(PAGE_SIZE + 1)
    result = await db.execute(stmt)
    users = result.scalars().all()
    next_cursor = None
    if len(users) > PAGE_SIZE:
        next_cursor = users[PAGE_SIZE].id
        users = users[:PAGE_SIZE]
    count_stmt = select(func.count(User.id))
    if team_id:
        count_stmt = count_stmt.where(User.team_id == team_id, User.is_active == True)
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()
    data = [UserOut.model_validate(u) for u in users]
    payload = PaginatedUsers(data=data, next_cursor=next_cursor, total=total, cached=False)
    await cache_service.set(cache_key, payload.model_dump(), ttl=300, tags=[f"team:{team_id}" if team_id else "users:all"])
    return payload
async def get_team_user_counts(db: AsyncSession) -> list[dict]:
    cache_key = "analytics:team:user_counts:v1"
    cached = await cache_service.get(cache_key)
    if cached:
        return cached
    stmt = text("""
        SELECT t.id, t.name, COUNT(u.id) AS user_count, SUM(u.login_count) AS total_logins
        FROM teams t
        LEFT JOIN users u ON u.team_id = t.id AND u.is_active = true
        GROUP BY t.id, t.name
        ORDER BY user_count DESC
    """)
    result = await db.execute(stmt)
    rows = [{"team_id": r[0], "team_name": r[1], "user_count": r[2], "total_logins": r[3] or 0} for r in result.fetchall()]
    await cache_service.set(cache_key, rows, ttl=120, tags=["teams:all"])
    return rows
