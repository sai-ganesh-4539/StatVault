"""Prediction endpoints: match outcome + market value."""
import numpy as np
from fastapi import APIRouter, HTTPException
from app.core.model_loader import ModelRegistry
from app.core.feature_encoder import MarketValueEncoder, encode_match_features
from app.models.schemas import (
    MatchPredictionRequest, MatchPredictionResponse,
    MarketValueRequest, MarketValueResponse,
)

router = APIRouter(prefix="/predict", tags=["predictions"])

LABELS = ["H", "D", "A"]  # home win, draw, away win


@router.post("/match", response_model=MatchPredictionResponse)
async def predict_match(req: MatchPredictionRequest) -> MatchPredictionResponse:
    """Predict match outcome (H/D/A) with calibrated probabilities."""
    try:
        sess = ModelRegistry.get_xgboost_match()
        features = encode_match_features(req.model_dump())
        outputs = sess.run(None, {"input": features})
        # outputs[0] = labels [None], outputs[1] = probabilities [None, 3]
        probs = outputs[1][0]  # shape (3,)
        label_idx = int(outputs[0][0])
        predicted = LABELS[label_idx] if label_idx < 3 else LABELS[int(np.argmax(probs))]
        return MatchPredictionResponse(
            home_team=req.home_team,
            away_team=req.away_team,
            predicted_label=predicted,
            probabilities={
                "H": float(probs[0]),
                "D": float(probs[1]),
                "A": float(probs[2]),
            },
            confidence=float(max(probs)),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"prediction failed: {e}")


@router.post("/market-value", response_model=MarketValueResponse)
async def predict_market_value(req: MarketValueRequest) -> MarketValueResponse:
    """Estimate player market value in EUR."""
    try:
        sess = ModelRegistry.get_market_value()
        features = MarketValueEncoder.encode(req.model_dump())
        outputs = sess.run(None, {"input": features})
        # Regression output — first scalar
        value = float(outputs[0][0][0]) if outputs[0].ndim == 2 else float(outputs[0][0])
        return MarketValueResponse(
            estimated_value_eur=int(max(0, value)),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"market value prediction failed: {e}")