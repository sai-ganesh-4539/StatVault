"""Team data endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.schemas import TeamResponse

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("/", response_model=list[TeamResponse])
async def list_teams(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await db.execute(
            text("SELECT team_id, name, team_type FROM dim_teams ORDER BY name LIMIT :limit"),
            {"limit": limit},
        )
        return [TeamResponse(team_id=r[0], name=r[1], team_type=r[2]) for r in result.fetchall()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))