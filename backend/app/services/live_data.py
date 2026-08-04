"""Wrapper for api-football.com with caching."""
import time
import httpx
from app.config import settings

_cache: dict[str, tuple[dict, float]] = {}
CACHE_TTL = 3600


async def _fetch(endpoint: str, params: dict | None = None) -> dict:
    if not settings.api_football_key:
        return {"error": "API_FOOTBALL_KEY not configured"}
    url = f"{settings.api_football_base_url}/{endpoint}"
    cache_key = f"{url}:{params}"
    if cache_key in _cache:
        data, ts = _cache[cache_key]
        if time.time() - ts < CACHE_TTL:
            return data
    headers = {
        "X-RapidAPI-Key": settings.api_football_key,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, params=params, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
    _cache[cache_key] = (data, time.time())
    return data


async def get_fixtures(league: int = 39, season: int = 2025) -> dict:
    return await _fetch("fixtures", {"league": league, "season": season, "next": 10})


async def get_live_scores() -> dict:
    return await _fetch("fixtures", {"live": "all"})


async def get_team_squad(team_id: int) -> dict:
    return await _fetch("players/squads", {"team": team_id})