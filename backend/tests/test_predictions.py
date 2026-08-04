"""Tests for /predict/* endpoints."""
import pytest
from httpx import AsyncClient


MOCK_MATCH = {
    "home_team": "Arsenal",
    "away_team": "Chelsea",
    "home_form_wins": 3,
    "home_form_draws": 1,
    "home_form_losses": 1,
    "away_form_wins": 2,
    "away_form_draws": 1,
    "away_form_losses": 2,
    "home_goals_avg": 1.8,
    "away_goals_avg": 1.2,
    "home_xg_avg": 1.6,
    "away_xg_avg": 1.1,
    "home_win_rate": 0.6,
    "away_win_rate": 0.4,
    "home_odds": 2.0,
    "draw_odds": 3.3,
    "away_odds": 2.5,
    "h2h_home_wins": 3,
    "h2h_away_wins": 2,
}

MOCK_MARKET = {
    "age": 23,
    "overall_rating": 85,
    "potential": 90,
    "pace": 88,
    "shooting": 80,
    "passing": 82,
    "dribbling": 86,
    "defending": 40,
    "physical": 75,
    "height_cm": 178,
    "weight_kg": 70,
    "preferred_foot": "Right",
    "position": "RW,CAM",
}


@pytest.mark.asyncio
async def test_predict_match_returns_200(client: AsyncClient):
    resp = await client.post("/predict/match", json=MOCK_MATCH)
    assert resp.status_code == 200
    data = resp.json()
    assert "predicted_label" in data
    assert data["predicted_label"] in ("H", "D", "A")
    assert "probabilities" in data
    assert "confidence" in data


@pytest.mark.asyncio
async def test_predict_match_invalid(client: AsyncClient):
    resp = await client.post("/predict/match", json={"home_team": "Arsenal"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_predict_market_value_returns_200(client: AsyncClient):
    resp = await client.post("/predict/market-value", json=MOCK_MARKET)
    assert resp.status_code == 200
    data = resp.json()
    assert "estimated_value_eur" in data


@pytest.mark.asyncio
async def test_predict_market_value_invalid(client: AsyncClient):
    resp = await client.post("/predict/market-value", json={"age": 23})
    assert resp.status_code == 422