import os, sys, json, logging, pickle, warnings, re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional, Union

import numpy as np
import pandas as pd
import xgboost as xgb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from scipy.sparse import issparse
from scipy import stats

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, label_binarize, OrdinalEncoder
from sklearn.calibration import CalibratedClassifierCV

from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, precision_score, recall_score,
    f1_score, matthews_corrcoef, cohen_kappa_score, jaccard_score,
    top_k_accuracy_score, roc_auc_score, log_loss, brier_score_loss,
    confusion_matrix, classification_report
)

from sklearn.utils.class_weight import compute_sample_weight
from sklearn.inspection import permutation_importance

try:

    import shap
    SHAP_AVAILABLE = True

except ImportError:

    SHAP_AVAILABLE = False
warnings.filterwarnings("ignore")

class Config:

    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = BASE_DIR / "data" / "features"
    MODEL_DIR = BASE_DIR / "models"
    REPORTS_DIR = BASE_DIR / "reports"
    FEATURES_PATH = DATA_DIR / "match_features.parquet"

    TARGET_CANDIDATES = ["ftresult", "result", "match_result", "outcome", "winner", "target", "label"]

    LEAKAGE_PATTERNS = [
        r"result", r"ftresult", r"winner", r"outcome", r"target", r"label",
        r"goal", r"goals", r"score", r"shots", r"yellow", r"red",
        r"corner", r"possession", r"actual_xg", r"post_match",
        r"full_time", r"half_time",
        r"^ft", r"^ht", r"over", r"under", r"handi", r"^c_", r"fouls"
    ]

    TIME_COLS = ["match_date", "date", "datetime", "match_datetime", "kickoff", "season", "year", "matchday"]

    XGB_PARAMS = {
        "objective": "multi:softprob", "num_class": 3, "n_estimators": 800,
        "learning_rate": 0.03, "max_depth": 6, "min_child_weight": 5,
        "subsample": 0.85, "colsample_bytree": 0.85, "gamma": 0.1,
        "reg_alpha": 0.5, "reg_lambda": 2.0, "eval_metric": "mlogloss",
        "tree_method": "hist", "max_bin": 255, "random_state": 42, "verbosity": 0, "n_jobs": -1
    }

    EARLY_STOPPING_ROUNDS = 50
    CALIBRATION_METHOD = "isotonic"
    SHAP_SAMPLE_SIZE = 1500
    HIGH_CARDINALITY_THRESHOLD = 100
    MAX_FEATURES = 500
    MODEL_VERSION = "2.0.0"

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S", force=True)
logger = logging.getLogger(__name__)

def get_xgb_version_tuple() -> Tuple[int, int]:

    try: return tuple(map(int, xgb.__version__.split('.')[:2]))
    except Exception: return (3, 0)

XGB_VERSION = get_xgb_version_tuple()
logger.info(f"XGBoost version: {xgb.__version__} -> {XGB_VERSION}")

def ensure_directories() -> None:

    Config.MODEL_DIR.mkdir(parents=True, exist_ok=True)
    Config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def detect_target_column(df: pd.DataFrame) -> str:

    for col in df.columns:

        if col.lower() in Config.TARGET_CANDIDATES: return col
    raise KeyError(f"Target not found. Candidates: {Config.TARGET_CANDIDATES}. Available: {list(df.columns)}")

def clean_stringified_lists(df: pd.DataFrame) -> pd.DataFrame:

    for col in df.select_dtypes(include=['object']).columns:

        sample = df[col].dropna().astype(str)

        if sample.str.startswith('[').any() and sample.str.endswith(']').any():

            logger.warning(f"Detected stringified lists in '{col}'. Extracting first element.")

            df[col] = df[col].apply(lambda x: str(x).strip('[]').split(',')[0] if isinstance(x, str) and x.startswith('[') else x)
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

def detect_leakage_columns(df: pd.DataFrame, target_col: str, target_encoded: pd.Series) -> Tuple[List[str], List[Dict]]:

    leakage_info = []

    for col in df.columns:

        if col == target_col:

            leakage_info.append({"column": col, "reason": "Target column", "correlation": 1.0})
            continue

        if any(re.search(pattern, col.lower()) for pattern in Config.LEAKAGE_PATTERNS):

            leakage_info.append({"column": col, "reason": "Pattern match", "correlation": None})
            continue

        if df[col].dtype in [np.number, np.int64, np.float64]:

            try:

                corr = abs(df[col].corr(target_encoded))

                if corr > 0.999:

                    leakage_info.append({"column": col, "reason": f"High correlation: {corr:.4f}", "correlation": round(corr, 4)})
            except Exception: pass

    return [item["column"] for item in leakage_info], leakage_info

def time_based_split(df: pd.DataFrame, target_col: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:

    time_col = next((col for col in Config.TIME_COLS if col in df.columns), None)

    if time_col:

        df = df.sort_values(by=time_col)

    else:

        logger.warning("No time column found. Falling back to index-based split.")
        df = df.sort_index()

    n = len(df)

    train_end, val_end = int(n * 0.8), int(n * 0.9)
    train_df, val_df, test_df = df.iloc[:train_end].copy(), df.iloc[train_end:val_end].copy(), df.iloc[val_end:].copy()
    logger.info(f"Split: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}")

    return train_df, val_df, test_df

def build_preprocessor(X_train: pd.DataFrame) -> Tuple[ColumnTransformer, List[str]]:

    numeric_cols = X_train.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = X_train.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
    transformers = []
    feature_names = []

    if numeric_cols:

        transformers.append(('num', Pipeline([('imputer', SimpleImputer(strategy='median')), ('scaler', StandardScaler())]), numeric_cols))
        feature_names.extend(numeric_cols)

    if categorical_cols:

        low_card = [c for c in categorical_cols if X_train[c].nunique() <= Config.HIGH_CARDINALITY_THRESHOLD]
        high_card = [c for c in categorical_cols if X_train[c].nunique() > Config.HIGH_CARDINALITY_THRESHOLD]

        if low_card:

            transformers.append(('cat_onehot', Pipeline([('imputer', SimpleImputer(strategy='most_frequent')), ('encoder', OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), low_card))
        
        if high_card:

            transformers.append(('cat_ordinal', Pipeline([('imputer', SimpleImputer(strategy='most_frequent')), ('encoder', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1))]), high_card))
        feature_names.extend(low_card + high_card)

    return ColumnTransformer(transformers=transformers, remainder='drop'), feature_names

def train_model(X_train, y_train, X_val, y_val, sw_train, sw_val):

    logger.info("Training XGBoost model...")
    eval_set = [(X_val, y_val)]

    if XGB_VERSION >= (1, 6):

        model = xgb.XGBClassifier(**Config.XGB_PARAMS, early_stopping_rounds=Config.EARLY_STOPPING_ROUNDS)
        model.fit(X_train, y_train, sample_weight=sw_train, eval_set=eval_set, sample_weight_eval_set=[sw_val], verbose=False)

    else:

        model = xgb.XGBClassifier(**Config.XGB_PARAMS)
        model.fit(X_train, y_train, sample_weight=sw_train, eval_set=eval_set, sample_weight_eval_set=[sw_val], early_stopping_rounds=Config.EARLY_STOPPING_ROUNDS, verbose=False)
    logger.info(f"Training complete. Best iteration: {getattr(model, 'best_iteration', 'N/A')}")

    return model

def compute_all_metrics(y_true, y_pred, y_prob) -> Dict:

    metrics = {"accuracy": round(accuracy_score(y_true, y_pred), 4), "balanced_accuracy": round(balanced_accuracy_score(y_true, y_pred), 4)}

    for avg in ["macro", "micro", "weighted"]:

        metrics[f"precision_{avg}"] = round(precision_score(y_true, y_pred, average=avg, zero_division=0), 4)
        metrics[f"recall_{avg}"] = round(recall_score(y_true, y_pred, average=avg, zero_division=0), 4)
        metrics[f"f1_{avg}"] = round(f1_score(y_true, y_pred, average=avg, zero_division=0), 4)

    metrics["roc_auc_ovr"] = round(roc_auc_score(y_true, y_prob, multi_class="ovr", average="macro"), 4)
    metrics["log_loss"] = round(log_loss(y_true, y_prob), 4)

    return metrics

def main():

    logger.info("="*60)
    logger.info("StatVault-ML: Match Prediction Pipeline v2.0")
    logger.info("="*60)
    ensure_directories()

    if not Config.FEATURES_PATH.exists():

        raise FileNotFoundError(f"Features not found: {Config.FEATURES_PATH}")
    
    logger.info("Loading data...")

    df = pd.read_parquet(Config.FEATURES_PATH)
    df = clean_stringified_lists(df)
    target_col = detect_target_column(df)
    logger.info(f"Target: {target_col}")

    target_map = {"H": 0, "D": 1, "A": 2, "home": 0, "draw": 1, "away": 2}

    y = df[target_col].copy()

    if y.dtype == 'object':

        y = y.map(target_map)
    y = y.dropna().astype(int)

    df = df.loc[y.index]

    leakage_cols, _ = detect_leakage_columns(df, target_col, y)

    logger.info(f"Removed {len(leakage_cols)} leakage columns")

    df = df.drop(columns=leakage_cols + [target_col], errors='ignore')

    train_df, val_df, test_df = time_based_split(pd.concat([df, y.rename('target')], axis=1), 'target')
    X_train_raw, y_train = train_df.drop(columns=['target']), train_df['target']
    X_val_raw, y_val = val_df.drop(columns=['target']), val_df['target']
    X_test_raw, y_test = test_df.drop(columns=['target']), test_df['target']

    logger.info("Building preprocessor")

    preprocessor, feature_names = build_preprocessor(X_train_raw)

    X_train = preprocessor.fit_transform(X_train_raw).astype(np.float32)
    X_val = preprocessor.transform(X_val_raw).astype(np.float32)
    X_test = preprocessor.transform(X_test_raw).astype(np.float32)

    logger.info(f"Features: {X_train.shape[1]}")

    sw_train = compute_sample_weight(class_weight='balanced', y=y_train)
    sw_val = compute_sample_weight(class_weight='balanced', y=y_val)
    base_model = train_model(X_train, y_train, X_val, y_val, sw_train, sw_val)

    logger.info("Calibrating...")

    calibrated_model = CalibratedClassifierCV(estimator=base_model, method=Config.CALIBRATION_METHOD, cv='prefit')
    calibrated_model.fit(X_val, y_val, sample_weight=sw_val)

    logger.info("Saving models...")

    with open(Config.MODEL_DIR / "xgboost_match.pkl", "wb") as f:

        pickle.dump({"model": base_model, "preprocessor": preprocessor, "features": feature_names}, f)

    y_pred = calibrated_model.predict(X_test)
    y_prob = calibrated_model.predict_proba(X_test)
    metrics = compute_all_metrics(y_test, y_pred, y_prob)

    with open(Config.REPORTS_DIR / "match_model_metrics.json", "w") as f:

        json.dump(metrics, f, indent=2)

    logger.info("="*60)
    logger.info("TRAINING COMPLETE")
    logger.info(f"Accuracy: {metrics['accuracy']*100:.2f}%")
    logger.info(f"ROC-AUC: {metrics['roc_auc_ovr']:.4f}")
    logger.info(f"F1-Macro: {metrics['f1_macro']:.4f}")
    logger.info("="*60)
if __name__ == "__main__":
    main()