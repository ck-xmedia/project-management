import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_register_and_login(client: AsyncClient):
    r = await client.post("/api/v1/auth/register", json={"email": "a@example.com", "password": "secret", "full_name": "Alice"})
    assert r.status_code == 201, r.text
    r = await client.post("/api/v1/auth/login", json={"email": "a@example.com", "password": "secret"})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data and data["token_type"] == "bearer"
