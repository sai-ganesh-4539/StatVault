"""Wrapper for football-data.org API with caching."""
import time
import httpx
from app.config import settings

_cache: dict[str, tuple[dict, float]] = {}
CACHE_TTL = 300  # 5 min for live, 1hr for static


async def _fetch(endpoint: str, params: dict | None = None) -> dict:
    """Fetch from football-data.org v4 API."""
    fd_key = getattr(settings, "football_data_org_key", "") or ""
    if not fd_key:
        return {"error": "FOOTBALL_DATA_ORG_KEY not configured"}

    url = f"https://api.football-data.org/v4/{endpoint}"
    cache_key = f"{url}:{params}"

    if cache_key in _cache:
        data, ts = _cache[cache_key]
        if time.time() - ts < CACHE_TTL:
            return data

    headers = {"X-Auth-Token": fd_key}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, params=params, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()

    _cache[cache_key] = (data, time.time())
    return data


async def get_live_scores() -> dict:
    """Get currently live matches."""
    return await _fetch("matches", {"status": "LIVE"})


async def get_fixtures(competition: str = "PL", limit: int = 10) -> dict:
    """Get upcoming fixtures. PL = Premier League."""
    return await _fetch(f"competitions/{competition}/matches", 
                        {"status": "SCHEDULED", "limit": limit})


async def get_team_squad(team_id: int) -> dict:
    """Get team squad/players."""
    return await _fetch(f"teams/{team_id}")


async def get_standings(competition: str = "PL") -> dict:
    """Get league standings."""
    return await _fetch(f"competitions/{competition}/standings")


async def get_scorers(competition: str = "PL", limit: int = 10) -> dict:
    """Get top scorers."""
    return await _fetch(f"competitions/{competition}/scorers", {"limit": limit})