import logging
import sys
from pathlib import Path
import joblib

import numpy as np
import pandas as pd

import xgboost as xgb
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s", handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "features" / "player_features.parquet"
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "market_value.pkl"
FEATURE_NAMES_PATH = MODEL_DIR / "market_value_feature_names.txt"

TARGET_COL = "market_value"
NUMERIC_COLS = ["age", "overall_rating", "potential", "pace", "shooting", "passing", "dribbling", "defending", "physical", "height", "weight"]
CATEGORICAL_COLS = ["preferred_foot", "position"]
HIGH_CARDINALITY_COLS = ["player_name", "short_name", "club", "nationality", "name", "player_id"]

def calculate_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:

    mask = y_true != 0

    if not np.any(mask): return 0.0

    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

def main():

    logger.info("Starting Phase 5: Market Value Prediction Training")

    if not DATA_PATH.exists():

        logger.error(f"Input data not found at {DATA_PATH}. Run Phase 3 first.")
        sys.exit(1)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(DATA_PATH)
    df = df.drop(columns=[c for c in HIGH_CARDINALITY_COLS if c in df.columns], errors="ignore")

    avail_numeric = [c for c in NUMERIC_COLS if c in df.columns]
    avail_categorical = [c for c in CATEGORICAL_COLS if c in df.columns]

    if TARGET_COL not in df.columns:

        logger.error(f"Target column '{TARGET_COL}' not found.")
        sys.exit(1)

    df = df.dropna(subset=[TARGET_COL])
    feature_cols = avail_numeric + avail_categorical

    X = df[feature_cols].copy()
    y = df[TARGET_COL]

    for col in avail_numeric: X[col] = X[col].fillna(X[col].median())
    for col in avail_categorical: X[col] = X[col].fillna("Unknown")

    if avail_categorical:

        X = pd.get_dummies(X, columns=avail_categorical, drop_first=False)
    X = X.astype(float)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    logger.info(f"Split complete -> Train: {X_train.shape[0]} | Test: {X_test.shape[0]}")
    logger.info(f"Total features after encoding: {X_train.shape[1]}")
    logger.info("Training XGBoost Regressor...")

    model = xgb.XGBRegressor(
        n_estimators=200, max_depth=6, learning_rate=0.05, subsample=0.8,
        colsample_bytree=0.8, random_state=42, n_jobs=-1, tree_method="hist"
    )

    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

    logger.info("Evaluating model performance...")

    y_pred = model.predict(X_test)

    r2 = r2_score(y_test, y_pred)

    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    mae = mean_absolute_error(y_test, y_pred)

    mape = calculate_mape(y_test.values, y_pred)

    logger.info(" Evaluation Metrics ")
    logger.info(f"R² Score  : {r2:.4f}")
    logger.info(f"RMSE      : {rmse:,.2f} €")
    logger.info(f"MAE       : {mae:,.2f} €")
    logger.info(f"MAPE      : {mape:.2f}%")
    logger.info(f"Saving model to {MODEL_PATH}")

    joblib.dump(model, MODEL_PATH)

    with open(FEATURE_NAMES_PATH, "w") as f:

        f.write("\n".join(X.columns))

    logger.info("Phase 5 completed successfully.")

if __name__ == "__main__":
    
    main()