"""Encodes raw API input -> ONNX-ready numpy arrays.

Critical for market_value: 13 raw fields -> 687-dim one-hot vector.
Reads the actual feature names from market_value_feature_names.txt so the
encoding stays correct even if Avinash changes the feature set tomorrow.
"""
import json
from pathlib import Path
import numpy as np
from app.config import settings


class MarketValueEncoder:
    """Encodes 13 raw player attributes into the 687-dim feature vector
    that market_value.onnx expects."""
    _feature_names: list[str] | None = None
    _name_to_index: dict[str, int] = {}

    NUMERIC_FIELDS = [
        "age", "overall_rating", "potential", "pace", "shooting",
        "passing", "dribbling", "defending", "physical", "height", "weight",
    ]
    # Map our API field names -> the names in the .txt feature file
    FIELD_TO_FEATURE = {
        "age": "age",
        "overall_rating": "overall_rating",
        "potential": "potential",
        "pace": "pace",
        "shooting": "shooting",
        "passing": "passing",
        "dribbling": "dribbling",
        "defending": "defending",
        "physical": "physical",
        "height_cm": "height",
        "weight_kg": "weight",
    }

    @classmethod
    def _ensure_loaded(cls) -> None:
        if cls._feature_names is not None:
            return
        path: Path = settings.market_value_features_path
        if not path.exists():
            raise FileNotFoundError(f"Feature names file not found: {path}")
        text = path.read_text(encoding="utf-8")
        # The file has 687 lines (or 686 + missing trailing newline). Split on newlines,
        # drop empty trailing entries.
        names = [line.strip() for line in text.split("\n") if line.strip()]
        if len(names) != 687:
            print(f"  [encoder] WARNING: expected 687 features, found {len(names)}")
        cls._feature_names = names
        cls._name_to_index = {name: i for i, name in enumerate(names)}
        print(f"  [encoder] loaded {len(names)} market_value feature names")

    @classmethod
    def encode(cls, payload: dict) -> np.ndarray:
        """Convert raw API payload -> shape (1, 687) float32 array."""
        cls._ensure_loaded()
        vec = np.zeros((1, len(cls._feature_names)), dtype=np.float32)

        # 1. Numeric features
        for api_field, feature_name in cls.FIELD_TO_FEATURE.items():
            idx = cls._name_to_index.get(feature_name)
            if idx is not None:
                vec[0, idx] = float(payload.get(api_field, 0))

        # 2. Preferred foot (one-hot)
        foot = payload.get("preferred_foot")
        if foot in ("Left", "Right"):
            col = f"preferred_foot_{foot}"
            idx = cls._name_to_index.get(col)
            if idx is not None:
                vec[0, idx] = 1.0

        # 3. Position (one-hot — match the exact comma-joined string)
        position = payload.get("position", "").strip()
        if position:
            col = f"position_{position}"
            idx = cls._name_to_index.get(col)
            if idx is not None:
                vec[0, idx] = 1.0
            else:
                print(f"  [encoder] WARNING: position '{position}' not in feature set; no one-hot set")

        return vec


def encode_match_features(payload: dict) -> np.ndarray:
    """Encode 18 form features -> 55-dim array.
    TODO: replace with actual feature mapping from Avinash's train_xgboost.py tomorrow.
    For now: place the 18 features in the first 18 slots, zero-pad the rest.
    """
    order = [
        "home_form_wins", "home_form_draws", "home_form_losses",
        "away_form_wins", "away_form_draws", "away_form_losses",
        "home_goals_avg", "away_goals_avg",
        "home_xg_avg", "away_xg_avg",
        "home_win_rate", "away_win_rate",
        "home_odds", "draw_odds", "away_odds",
        "h2h_home_wins", "h2h_away_wins",
    ]
    # Add 1 extra to make 18 (home possession stub)
    vec = np.zeros((1, 55), dtype=np.float32)
    for i, key in enumerate(order):
        if i >= 55:
            break
        vec[0, i] = float(payload.get(key, 0))
    return vec


def encode_anomaly_features(payload: dict) -> np.ndarray:
    """Encode 7 anomaly features -> 7-dim array.
    TODO: verify exact feature order with Avinash tomorrow.
    """
    order = [
        "goals", "assists", "minutes_played",
        "pass_accuracy", "cards", "xg", "performance_trend",
    ]
    vec = np.zeros((1, 7), dtype=np.float32)
    for i, key in enumerate(order):
        vec[0, i] = float(payload.get(key, 0))
    return vec