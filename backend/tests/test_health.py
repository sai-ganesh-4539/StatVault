"""Tests for /health and / endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_200(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["app"] == "StatVault API"
    assert data["status"] in ("ok", "degraded")


@pytest.mark.asyncio
async def test_root_returns_endpoints(client: AsyncClient):
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert "endpoints" in data
    assert "predictions" in data["endpoints"]