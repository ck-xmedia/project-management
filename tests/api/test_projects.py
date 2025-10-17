import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_and_list_projects(client: AsyncClient):
    # Register and login
    r = await client.post("/api/v1/auth/register", json={"email": "p@example.com", "password": "secret", "full_name": "Proj"})
    assert r.status_code == 201, r.text
    r = await client.post("/api/v1/auth/login", json={"email": "p@example.com", "password": "secret"})
    token = r.json()["access_token"]

    # Create project
    headers = {"Authorization": f"Bearer {token}"}
    r = await client.post("/api/v1/projects", json={"name": "Acme", "key": "ACME", "description": "demo"}, headers=headers)
    assert r.status_code == 201, r.text

    # List my projects
    r = await client.get("/api/v1/projects", headers=headers)
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) == 1 and items[0]["key"] == "ACME"
