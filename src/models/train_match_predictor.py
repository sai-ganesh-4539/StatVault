import os
import sys
import logging
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score, classification_report
)
import xgboost as xgb

# ==========================================
# CONFIGURATION & LOGGING
# ==========================================
# Set up project root path (assuming script is in src/models/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "features" / "match_features.csv"
MODEL_OUTPUT_DIR = PROJECT_ROOT / "models"
MODEL_OUTPUT_PATH = MODEL_OUTPUT_DIR / "match_predictor.pkl"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Target accuracy threshold as per Phase 5 requirements
TARGET_ACCURACY = 0.60 

def load_data():
    """Loads the engineered match features from Phase 4."""
    logger.info(f"Loading data from {DATA_PATH}...")
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Data file not found at {DATA_PATH}. Please ensure Phase 4 is completed.")
    
    df = pd.read_csv(DATA_PATH)
    logger.info(f"Data loaded successfully. Shape: {df.shape}")
    return df

def preprocess_data(df):
    """Separates features and target, encodes target, and splits data."""
    logger.info("Preprocessing data...")
    
    # 1. Identify or Create Target Column
    target_col = None
    if 'result' in df.columns:
        target_col = 'result'
    elif 'match_outcome' in df.columns:
        target_col = 'match_outcome'
    elif 'home_score' in df.columns and 'away_score' in df.columns:
        logger.info("Target column not found. Deriving 'match_outcome' from 'home_score' and 'away_score'...")
        
        # Ensure scores are strictly numeric and drop any rows with missing scores
        df['home_score'] = pd.to_numeric(df['home_score'], errors='coerce')
        df['away_score'] = pd.to_numeric(df['away_score'], errors='coerce')
        df = df.dropna(subset=['home_score', 'away_score'])
        
        # Create H, D, A based on scores
        conditions = [
            df['home_score'] > df['away_score'],
            df['home_score'] == df['away_score'],
            df['home_score'] < df['away_score']
        ]
        choices = ['H', 'D', 'A']
        
        # FIX: Use a string default ('Unknown') instead of np.nan to prevent dtype mismatch
        df['match_outcome'] = np.select(conditions, choices, default='Unknown')
        
        # Drop any rows that didn't match the conditions (should be none now, but safe to keep)
        df = df[df['match_outcome'] != 'Unknown']
        
        target_col = 'match_outcome'
    else:
        raise ValueError("Target column not found and cannot be derived from scores.")

    # 2. Drop non-feature columns 
    # IMPORTANT: 'home_score' and 'away_score' MUST be dropped to prevent data leakage!
        # 2. Drop non-feature columns 
    # IMPORTANT: Drop final scores AND current match stats to prevent data leakage!
    drop_cols = [
        'date', 'home_team', 'away_team', 'tournament', 'city', 'country', 'neutral', 
        'home_score', 'away_score',
        # --- ADDED TO PREVENT LEAKAGE ---
        'home_goals_scored', 'away_goals_scored', 
        'home_goals_conceded', 'away_goals_conceded', 
        'home_goal_diff', 'away_goal_diff'
    ]
    cols_to_drop = [col for col in drop_cols if col in df.columns]
    cols_to_drop = [col for col in drop_cols if col in df.columns]
    
    X = df.drop(columns=cols_to_drop + [target_col])
    y = df[target_col]

    # Ensure all features are numeric (XGBoost requirement)
    X = X.select_dtypes(include=[np.number])
    
    # 3. Encode target variable (H, D, A -> 0, 1, 2)
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # 4. Train-test split 
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42
    )
    
    logger.info(f"Features shape: {X.shape}, Target classes: {le.classes_}")
    return X_train, X_test, y_train, y_test, le

def train_and_evaluate(X_train, X_test, y_train, y_test):
    """Trains the XGBoost model and evaluates performance."""
    logger.info("Initializing and training XGBoost Classifier...")
    
    # Initialize XGBoost with parameters optimized for multi-class football prediction
    model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective='multi:softprob',
        num_class=3,
        eval_metric='mlogloss',
        use_label_encoder=False,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    logger.info("Model training completed.")
    
    # Predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)
    
    # Calculate Metrics
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    # ROC-AUC for multi-class requires One-vs-Rest (ovr)
    roc_auc = roc_auc_score(y_test, y_pred_proba, multi_class='ovr', average='weighted')
    
    logger.info("========== MODEL METRICS ==========")
    logger.info(f"Accuracy  : {acc:.4f} (Target: > {TARGET_ACCURACY})")
    logger.info(f"Precision : {prec:.4f}")
    logger.info(f"Recall    : {rec:.4f}")
    logger.info(f"F1-Score  : {f1:.4f}")
    logger.info(f"ROC-AUC   : {roc_auc:.4f}")
    logger.info("===================================")
    
    logger.info("\nDetailed Classification Report:\n" + classification_report(y_test, y_pred))
    
    # Check Accuracy Goal
    if acc < TARGET_ACCURACY:
        logger.warning(f"⚠️ WARNING: Accuracy ({acc:.2%}) is below the target threshold of {TARGET_ACCURACY:.0%}!")
    else:
        logger.info(f"✅ SUCCESS: Accuracy target of {TARGET_ACCURACY:.0%} achieved!")
        
    return model, acc

def save_model(model, label_encoder):
    """Saves the trained model and label encoder to disk."""
    MODEL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save model
    joblib.dump(model, MODEL_OUTPUT_PATH)
    logger.info(f"Model saved successfully to {MODEL_OUTPUT_PATH}")
    
    # Save label encoder to decode predictions later
    encoder_path = MODEL_OUTPUT_DIR / "match_target_encoder.pkl"
    joblib.dump(label_encoder, encoder_path)
    logger.info(f"Label encoder saved to {encoder_path}")

def main():
    try:
        # 1. Load Data
        df = load_data()
        
        # 2. Preprocess
        X_train, X_test, y_train, y_test, le = preprocess_data(df)
        
        # 3. Train & Evaluate
        model, accuracy = train_and_evaluate(X_train, X_test, y_train, y_test)
        
        # 4. Save Artifacts
        save_model(model, le)
        
        logger.info("🎉 Phase 5: Match Prediction Model pipeline completed successfully!")
        
    except Exception as e:
        logger.error(f"An error occurred during Phase 5 execution: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()