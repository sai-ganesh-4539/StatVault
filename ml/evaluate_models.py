import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import joblib

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    r2_score, mean_squared_error, silhouette_score
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
FEATURES_DIR = BASE_DIR / "data" / "features"
REPORTS_DIR = BASE_DIR / "reports"

def load_artifact(path: Path):

    if not path.exists():

        logger.warning(f"Artifact not found: {path}")

        return None
    
    artifact = joblib.load(path) if path.suffix == '.pkl' else pd.read_parquet(path)

    if isinstance(artifact, dict):

        if 'model' in artifact and hasattr(artifact['model'], 'predict'):

            return artifact['model']
        
        for value in artifact.values():

            if hasattr(value, 'predict'):

                return value
            
    return artifact

def prepare_and_align(X: pd.DataFrame, model):

    X_num = X.select_dtypes(include=[np.number, 'bool'])
    expected_n = None

    if hasattr(model, 'n_features_in_'):

        expected_n = model.n_features_in_

    elif hasattr(model, 'get_booster'):

        expected_n = model.get_booster().num_features()

    data = X_num.values

    if expected_n is not None:

        current_n = data.shape[1]

        if current_n < expected_n:

            pad_width = expected_n - current_n
            padding = np.zeros((data.shape[0], pad_width), dtype=data.dtype)
            data = np.hstack([data, padding])

        elif current_n > expected_n:

            data = data[:, :expected_n]
            

    return data

def clean_and_split(df: pd.DataFrame, has_target: bool = True):

    if has_target:

        y = df.iloc[:, -1]
        X_raw = df.iloc[:, :-1]
        # Remove rows where target is NaN
        mask = y.notna()
        return X_raw[mask], y[mask]
    
    else:

        return df, None
    
def encode_match_target(y: pd.Series) -> pd.Series:

    if pd.api.types.is_numeric_dtype(y):
        return y.astype(int)
    
    mapping = {
        "H": 0, "D": 1, "A": 2, "h": 0, "d": 1, "a": 2,
        "home": 0, "draw": 1, "away": 2, "Home": 0, "Draw": 1, "Away": 2,
        "HOME": 0, "DRAW": 1, "AWAY": 2, "W": 0, "L": 2
    }

    y_mapped = y.map(mapping)

    if y_mapped.isna().any():

        y_numeric = pd.to_numeric(y, errors='coerce')
        y_mapped = y_mapped.fillna(y_numeric)

    if y_mapped.isna().any():

        y_mapped, _ = pd.factorize(y)
        y_mapped = pd.Series(y_mapped, index=y.index)

    return y_mapped.astype(int)

def evaluate_match_model():

    model = load_artifact(MODELS_DIR / "xgboost_match.pkl")
    df = load_artifact(FEATURES_DIR / "match_features.parquet")
        
    if not model or df is None or df.empty: 

        return {"status": "skipped", "reason": "Model or data missing"}
    
    X_raw, y = clean_and_split(df, has_target=True)

    if len(y) == 0:

        return {"status": "skipped", "reason": "No valid data after cleaning NaNs"}
    
    y = encode_match_target(y)
    X = prepare_and_align(X_raw, model)
    y_pred = model.predict(X)

    return {
        "accuracy": float(accuracy_score(y, y_pred)),
        "precision": float(precision_score(y, y_pred, average='weighted', zero_division=0)),
        "recall": float(recall_score(y, y_pred, average='weighted', zero_division=0)),
        "f1": float(f1_score(y, y_pred, average='weighted', zero_division=0))
    }

def evaluate_market_value():

    model = load_artifact(MODELS_DIR / "market_value.pkl")
    df = load_artifact(FEATURES_DIR / "player_features.parquet")

    if not model or df is None or df.empty: 

        return {"status": "skipped", "reason": "Model or data missing"}
    
    X_raw, y = clean_and_split(df, has_target=True)

    if len(y) == 0:

        return {"status": "skipped", "reason": "No valid data after cleaning NaNs"}
    
    X = prepare_and_align(X_raw, model)

    y_pred = model.predict(X)

    return {
        "r2": float(r2_score(y, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y, y_pred)))
    }

def evaluate_clustering():

    model = load_artifact(MODELS_DIR / "kmeans_clusters.pkl")
    df = load_artifact(FEATURES_DIR / "clustering_features.parquet")

    if not model or df is None or df.empty: 

        return {"status": "skipped", "reason": "Model or data missing"}
    
    X_raw, _ = clean_and_split(df, has_target=False)

    if X_raw.empty:

        return {"status": "skipped", "reason": "No valid data available"}
    
    X = prepare_and_align(X_raw, model)
    labels = model.predict(X)

    return {"silhouette_score": float(silhouette_score(X, labels))}

def evaluate_anomalies():

    model = load_artifact(MODELS_DIR / "isolation_forest.pkl")
    df = load_artifact(FEATURES_DIR / "anomaly_features.parquet")

    if not model or df is None or df.empty: 

        return {"status": "skipped", "reason": "Model or data missing"}
    
    X_raw, _ = clean_and_split(df, has_target=False)

    if X_raw.empty:

        return {"status": "skipped", "reason": "No valid data available"}
    
    X = prepare_and_align(X_raw, model)
    preds = model.predict(X)
    anomaly_pct = float((preds == -1).sum() / len(preds) * 100)

    return {"anomaly_percentage": anomaly_pct}

def save_reports(metrics: dict):

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = REPORTS_DIR / "model_metrics.json"

    with open(json_path, "w") as f:

        json.dump(metrics, f, indent=4)

    logger.info(f"Saved JSON metrics to {json_path}")
    md_path = REPORTS_DIR / "model_metrics.md"

    with open(md_path, "w") as f:

        f.write("# StatVault Model Evaluation Metrics\n\n")

        for name, vals in metrics.items():

            f.write(f"## {name.replace('_', ' ').title()}\n\n")

            if vals.get("status") == "skipped":

                f.write(f"*Status: Skipped - {vals.get('reason', 'Unknown')}*\n\n")

            else:

                for k, v in vals.items():

                    val_str = f"{v:.4f}" if isinstance(v, float) else str(v)
                    f.write(f"- **{k.replace('_', ' ').title()}**: {val_str}\n")

                f.write("\n")

    logger.info(f"Saved Markdown metrics to {md_path}")

def main():

    logger.info("Starting Phase 9: Model Evaluation")

    metrics = {
        "match_model": evaluate_match_model(),
        "market_value_model": evaluate_market_value(),
        "clustering": evaluate_clustering(),
        "anomaly_detection": evaluate_anomalies()
    }

    save_reports(metrics)
    logger.info("Phase 9 completed successfully. Reports saved to 'reports/'")
    
if __name__ == "__main__":
    main()