"""Natural language Q&A endpoint."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.query_router import ask
from app.models.schemas import AskRequest, AskResponse

router = APIRouter(tags=["ask"])


@router.post("/ask", response_model=AskResponse)
async def ask_question(req: AskRequest, db: AsyncSession = Depends(get_db)):
    try:
        result = await ask(req.question, db)
        return AskResponse(
            question=req.question,
            answer=result.answer,
            source=result.source,
            data=result.data,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ask failed: {e}")