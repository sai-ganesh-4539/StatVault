"""Pydantic request/response schemas for all endpoints."""
from typing import Literal
from pydantic import BaseModel, Field


# ============ HEALTH ============

class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    app: str
    models_loaded: dict[str, bool]
    db_connected: bool = False


# ============ MATCH PREDICTION ============

class MatchPredictionRequest(BaseModel):
    home_team: str = Field(..., example="Manchester City")
    away_team: str = Field(..., example="Liverpool")
    home_form_wins: int = Field(0, ge=0, le=5)
    home_form_draws: int = Field(0, ge=0, le=5)
    home_form_losses: int = Field(0, ge=0, le=5)
    away_form_wins: int = Field(0, ge=0, le=5)
    away_form_draws: int = Field(0, ge=0, le=5)
    away_form_losses: int = Field(0, ge=0, le=5)
    home_goals_avg: float = Field(0.0, ge=0)
    away_goals_avg: float = Field(0.0, ge=0)
    home_xg_avg: float = Field(0.0, ge=0)
    away_xg_avg: float = Field(0.0, ge=0)
    home_win_rate: float = Field(0.0, ge=0, le=1)
    away_win_rate: float = Field(0.0, ge=0, le=1)
    home_odds: float = Field(2.0, gt=1)
    draw_odds: float = Field(3.0, gt=1)
    away_odds: float = Field(2.5, gt=1)
    h2h_home_wins: int = Field(0, ge=0)
    h2h_away_wins: int = Field(0, ge=0)


class MatchPredictionResponse(BaseModel):
    home_team: str
    away_team: str
    predicted_label: Literal["H", "D", "A"]
    probabilities: dict[str, float]
    confidence: float
    model: str = "xgboost_match.onnx"


# ============ MARKET VALUE ============

class MarketValueRequest(BaseModel):
    age: int = Field(..., ge=15, le=50)
    overall_rating: int = Field(..., ge=0, le=99)
    potential: int = Field(..., ge=0, le=99)
    pace: int = Field(..., ge=0, le=99)
    shooting: int = Field(..., ge=0, le=99)
    passing: int = Field(..., ge=0, le=99)
    dribbling: int = Field(..., ge=0, le=99)
    defending: int = Field(..., ge=0, le=99)
    physical: int = Field(..., ge=0, le=99)
    height_cm: int = Field(..., ge=150, le=220)
    weight_kg: int = Field(..., ge=50, le=120)
    preferred_foot: Literal["Left", "Right"]
    position: str = Field(..., example="CAM,CF,LW")


class MarketValueResponse(BaseModel):
    estimated_value_eur: int
    model: str = "market_value.onnx"


# ============ ANOMALY DETECTION ============

class AnomalyRequest(BaseModel):
    goals: int = Field(0, ge=0)
    assists: int = Field(0, ge=0)
    minutes_played: int = Field(0, ge=0)
    pass_accuracy: float = Field(0.0, ge=0, le=1)
    cards: int = Field(0, ge=0)
    xg: float = Field(0.0, ge=0)
    performance_trend: float = Field(0.0)


class AnomalyResponse(BaseModel):
    is_anomaly: bool
    anomaly_score: float
    model: str = "isolation_forest.onnx"


# ============ SCOUTING CLUSTERS ============

class ClusterCentroid(BaseModel):
    cluster_name: str
    cluster_id: int
    centroid_values: dict[str, float]


class ClusterListResponse(BaseModel):
    clusters: list[ClusterCentroid]
    metrics: dict


# ============ ASK (NL Q&A) ============

class AskRequest(BaseModel):
    question: str = Field(..., example="Who are the top 10 most valuable players?")


class AskResponse(BaseModel):
    question: str
    answer: str
    source: Literal["sql", "rag", "none"]
    data: list[dict] | None = None


# ============ GENERIC LIST RESPONSES ============

class PlayerResponse(BaseModel):
    player_id: int
    name: str | None = None
    nationality: str | None = None
    position: str | None = None


class TeamResponse(BaseModel):
    team_id: int
    name: str
    team_type: str | None = None


class MatchResponse(BaseModel):
    match_id: int
    home_team: str | None = None
    away_team: str | None = None
    result: str | None = None
    home_goals: int | None = None
    away_goals: int | None = None


# ============ LIVE DATA ============

class FixturesResponse(BaseModel):
    fixtures: list[dict]
    source: str = "api-football"