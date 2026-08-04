"""Health check endpoint."""
from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.core.model_loader import ModelRegistry
from app.core.database import check_db_connection

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    models_loaded = {
        "xgboost_match": ModelRegistry._xgboost_match is not None,
        "market_value": ModelRegistry._market_value is not None,
        "isolation_forest": ModelRegistry._isolation_forest is not None,
    }
    db_ok = await check_db_connection()
    all_ok = all(models_loaded.values()) and db_ok
    return HealthResponse(
        status="ok" if all_ok else "degraded",
        app="StatVault API",
        models_loaded=models_loaded,
        db_connected=db_ok,
    )