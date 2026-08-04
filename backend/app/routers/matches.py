"""Match data endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.schemas import MatchResponse

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("/", response_model=list[MatchResponse])
async def list_matches(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await db.execute(
            text("""
                SELECT m.match_id, ht.name as home, at.name as away, m.result, m.home_goals, m.away_goals
                FROM fact_matches m
                JOIN dim_teams ht ON m.home_team_id = ht.team_id
                JOIN dim_teams at ON m.away_team_id = at.team_id
                ORDER BY m.match_id DESC LIMIT :limit OFFSET :offset
            """),
            {"limit": limit, "offset": offset},
        )
        return [MatchResponse(match_id=r[0], home_team=r[1], away_team=r[2], result=r[3], home_goals=r[4], away_goals=r[5]) for r in result.fetchall()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/live")
async def live_scores():
    from app.services.live_data import get_live_scores
    data = await get_live_scores()
    return data