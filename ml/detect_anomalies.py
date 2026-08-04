
import json
import logging
from pathlib import Path
from typing import List
import joblib

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

BASE = Path(__file__).parent.resolve()
INPUT = BASE / "data" / "features" / "anomaly_features.parquet"
MODEL_PATH = BASE / "models" / "isolation_forest.pkl"
OUTPUT = BASE / "outputs" / "anomaly_scores.json"
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

def load_data() -> pd.DataFrame:

    if not INPUT.exists():

        raise FileNotFoundError(
            f"{INPUT} not found. Run build_features.py (Phase 3) first."
        )
    
    df = pd.read_parquet(INPUT)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    return df

def get_feature_columns(df: pd.DataFrame) -> List[str]:

    expected = [
        "goals", "assists", "minutes_played", "pass_accuracy",
        "cards", "xg", "rolling_mean", "rolling_std", "performance_trend",
    ]

    available = [c for c in expected if c in df.columns]

    if not available:

        available = df.select_dtypes(include=[np.number]).columns.tolist()
        available = [c for c in available if "id" not in c]
        logger.warning(f"Expected features not found, using fallback: {available}")

    return available

def main():

    try:

        df = load_data()
        features = get_feature_columns(df)

        if not features:

            raise ValueError("No numeric features found.")
        
        X = df[features].fillna(df[features].median().fillna(0))
        logger.info(f"Loaded {len(df)} rows, {len(features)} features: {features}")

        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("iforest", IsolationForest(
                n_estimators=100,
                contamination=0.05,
                random_state=42,
                n_jobs=-1,
            )),
        ])

        pipeline.fit(X)
        logger.info("Model trained.")
        scores = pipeline.decision_function(X)
        preds = pipeline.predict(X)
        id_col = "player_id" if "player_id" in df.columns else None
        results = []

        for i in range(len(df)):

            player_id = str(df[id_col].iloc[i]).strip() if id_col else f"P{i:04d}"

            results.append({
                "id": player_id,
                "anomaly_score": round(float(scores[i]), 4),
                "is_anomaly": bool(preds[i] == -1),
            })

        joblib.dump(pipeline, MODEL_PATH)
        logger.info(f"Model saved -> {MODEL_PATH}")

        with open(OUTPUT, "w", encoding="utf-8") as f:

            json.dump(results, f, indent=4, ensure_ascii=False)

        logger.info(f"Scores saved -> {OUTPUT}")
        n_anomalies = sum(1 for r in results if r["is_anomaly"])
        logger.info(f"Phase 7 complete: {n_anomalies}/{len(results)} anomalies detected.")

    except Exception as e:
        
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    main()