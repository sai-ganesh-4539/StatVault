"""Player data endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.schemas import PlayerResponse

router = APIRouter(prefix="/players", tags=["players"])


@router.get("/", response_model=list[PlayerResponse])
async def list_players(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await db.execute(
            text("SELECT player_id, short_name as name, nationality, player_positions as position FROM dim_players ORDER BY player_id LIMIT :limit OFFSET :offset"),
            {"limit": limit, "offset": offset},
        )
        return [PlayerResponse(player_id=r[0], name=r[1], nationality=r[2], position=r[3]) for r in result.fetchall()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{player_id}", response_model=PlayerResponse)
async def get_player(player_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            text("SELECT player_id, short_name as name, nationality, player_positions as position FROM dim_players WHERE player_id = :id"),
            {"id": player_id},
        )
        row = result.first()
        if not row:
            raise HTTPException(status_code=404, detail="Player not found")
        return PlayerResponse(player_id=row[0], name=row[1], nationality=row[2], position=row[3])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))