import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

@pytest.mark.asyncio
async def test_version_header_v1(client):
    r = await client.get("/api/v1/users")
    assert r.status_code == 200
    assert r.headers.get("X-API-Version") == "v1"

@pytest.mark.asyncio
async def test_version_header_v2(client):
    r = await client.get("/api/v2/users")
    assert r.status_code == 200
    assert r.headers.get("X-API-Version") == "v2"

@pytest.mark.asyncio
async def test_v1_user_flat_name(client):
    r = await client.get("/api/v1/users/1")
    assert "name" in r.json()
    assert "first_name" not in r.json()

@pytest.mark.asyncio
async def test_v2_user_split_name(client):
    data = (await client.get("/api/v2/users/1")).json()["data"]
    assert "first_name" in data and "last_name" in data and "name" not in data

@pytest.mark.asyncio
async def test_v1_team_member_count(client):
    assert "member_count" in (await client.get("/api/v1/teams/1")).json()

@pytest.mark.asyncio
async def test_v2_team_member_total(client):
    data = (await client.get("/api/v2/teams/1")).json()["data"]
    assert "member_total" in data and "member_count" not in data

@pytest.mark.asyncio
async def test_v1_deprecation_headers(client):
    r = await client.get("/api/v1/users")
    assert "Sunset" in r.headers
    assert "Deprecation" in r.headers
    assert "X-Deprecation-Notice" in r.headers

@pytest.mark.asyncio
async def test_v2_no_deprecation_headers(client):
    r = await client.get("/api/v2/users")
    assert "Sunset" not in r.headers
    assert "Deprecation" not in r.headers

@pytest.mark.asyncio
async def test_versions_endpoint(client):
    data = (await client.get("/api/versions")).json()
    assert "versions" in data and data["recommended"] == "v2"

@pytest.mark.asyncio
async def test_version_detail(client):
    data = (await client.get("/api/versions/v2")).json()
    assert data["version"] == "v2" and data["status"] == "stable"

@pytest.mark.asyncio
async def test_version_not_found(client):
    assert (await client.get("/api/versions/v99")).status_code == 404

@pytest.mark.asyncio
async def test_migration_guide_v1_to_v2(client):
    data = (await client.get("/api/migration/v1/v2")).json()
    assert data["from_version"] == "v1" and len(data["steps"]) > 0

@pytest.mark.asyncio
async def test_migration_guide_not_found(client):
    assert (await client.get("/api/migration/v1/v99")).status_code == 404

@pytest.mark.asyncio
async def test_v2_cursor_pagination(client):
    data = (await client.get("/api/v2/users?per_page=2")).json()
    assert "pagination" in data and "next_cursor" in data["pagination"]

@pytest.mark.asyncio
async def test_v2_analytics(client):
    data = (await client.get("/api/v2/analytics")).json()["data"]
    assert "api_calls" in data and "version_adoption" in data

@pytest.mark.asyncio
async def test_v2_structured_error(client):
    data = (await client.get("/api/v2/users/9999")).json()
    assert "error" in data and data["error"]["code"] == "USER_NOT_FOUND"

@pytest.mark.asyncio
async def test_compat_shim_v1_shape(client):
    data = (await client.get("/api/v2/compat/v1/users")).json()
    assert "users" in data and "name" in data["users"][0] and "first_name" not in data["users"][0]

@pytest.mark.asyncio
async def test_health(client):
    assert (await client.get("/health")).json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_root_lists_versions(client):
    assert "supported_versions" in (await client.get("/")).json()
