import pytest
from app.schemas.user import PaginatedUsers, UserOut
def test_paginated_users_schema():
    user = UserOut(id="u1", email="test@example.com", name="Test User", team_id="t1", is_active=True, login_count=10)
    page = PaginatedUsers(data=[user], next_cursor="u1", total=50, cached=False)
    assert page.total == 50
    assert len(page.data) == 1
def test_paginated_users_cached_flag():
    page = PaginatedUsers(data=[], total=0, cached=True)
    assert page.cached is True
