"""Tests for /scout/* endpoints."""
import pytest
from httpx import AsyncClient


MOCK_ANOMALY = {
    "goals": 27,
    "assists": 5,
    "minutes_played": 2600,
    "pass_accuracy": 0.82,
    "cards": 2,
    "xg": 22.5,
    "performance_trend": 1.3,
}


@pytest.mark.asyncio
async def test_scout_anomaly_returns_200(client: AsyncClient):
    resp = await client.post("/scout/anomaly", json=MOCK_ANOMALY)
    assert resp.status_code == 200
    data = resp.json()
    assert "is_anomaly" in data
    assert "anomaly_score" in data


@pytest.mark.asyncio
async def test_scout_clusters_returns_200(client: AsyncClient):
    resp = await client.get("/scout/clusters")
    assert resp.status_code == 200
    data = resp.json()
    assert "clusters" in data