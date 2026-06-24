import os
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# ==========================================
# CONFIGURATION
# ==========================================
INPUT_DATA_PATH = "data/features/match_player_features.csv" # Update with actual Phase 4 output path
MODEL_OUTPUT_PATH = "models/anomaly_detector.pkl"
SCALER_OUTPUT_PATH = "models/anomaly_scaler.pkl"
ANOMALY_REPORT_PATH = "reports/anomalies_detected.csv"

# Features used for anomaly detection (Derived from Phase 4)
# We use a mix of rolling match stats and player physical/technical stats
FEATURES_TO_USE = [
    'rolling_goals', 'rolling_xG', 'rolling_xGA', 
    'Overall', 'Pace', 'Shooting', 'Passing', 'Dribbling', 'Defending', 'Physical',
    'Age' 
]

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def load_data(filepath):
    """Loads the feature-engineered dataset."""
    print(f"Loading data from {filepath}...")
    # For demonstration, if the file doesn't exist, we generate mock data
    if not os.path.exists(filepath):
        print("Input file not found. Generating mock data for demonstration...")
        return generate_mock_data()
    
    df = pd.read_csv(filepath)
    return df

def generate_mock_data(n_samples=1000):
    """Generates mock data to ensure the script is runnable out-of-the-box."""
    np.random.seed(42)
    data = {
        'player_id': np.random.randint(1000, 9999, n_samples),
        'match_id': np.random.randint(10000, 99999, n_samples),
        'rolling_goals': np.random.poisson(0.5, n_samples),
        'rolling_xG': np.random.normal(0.6, 0.2, n_samples),
        'rolling_xGA': np.random.normal(0.4, 0.2, n_samples),
        'Overall': np.random.normal(75, 5, n_samples),
        'Pace': np.random.normal(70, 10, n_samples),
        'Shooting': np.random.normal(68, 12, n_samples),
        'Passing': np.random.normal(72, 10, n_samples),
        'Dribbling': np.random.normal(70, 11, n_samples),
        'Defending': np.random.normal(65, 15, n_samples),
        'Physical': np.random.normal(70, 8, n_samples),
        'Age': np.random.randint(18, 38, n_samples)
    }
    df = pd.DataFrame(data)
    
    # Injecting deliberate anomalies
    # 1. Sudden Form Drop / Injury-like (Low pace, physical, and goals)
    df.loc[10:15, ['Pace', 'Physical', 'rolling_goals']] = [40, 45, 0] 
    # 2. Goal Surge (Extremely high rolling goals and xG)
    df.loc[50:55, ['rolling_goals', 'rolling_xG']] = [8, 5.5]
    # 3. Unusual Stats (19 year old with 99 overall and physical)
    df.loc[100, ['Age', 'Overall', 'Physical']] = [19, 99, 99]
    
    return df

def preprocess_data(df):
    """Filters and scales the features for the Isolation Forest."""
    # Ensure all required features exist
    missing_cols = [col for col in FEATURES_TO_USE if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required features in dataset: {missing_cols}")
    
    # Drop rows with NaNs in the target features
    df_clean = df.dropna(subset=FEATURES_TO_USE).copy()
    
    X = df_clean[FEATURES_TO_USE]
    
    # Scale features (Isolation Forest is tree-based and doesn't strictly require scaling, 
    # but it's good practice for distance-based interpretations and future pipeline consistency)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    return X_scaled, scaler, df_clean

def train_anomaly_model(X):
    """Trains the Isolation Forest model."""
    print("Training Isolation Forest model...")
    # contamination='auto' lets the model decide, or set to a float like 0.05 for 5% anomalies
    model = IsolationForest(
        n_estimators=100, 
        contamination=0.05, # Assuming 5% of data points are anomalies
        max_samples='auto',
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X)
    return model

def detect_and_report(model, X_scaled, df_clean):
    """Predicts anomalies and generates a report."""
    print("Detecting anomalies...")
    # Predict: 1 for normal, -1 for anomaly
    predictions = model.predict(X_scaled)
    df_clean['anomaly_label'] = predictions
    df_clean['anomaly_score'] = model.score_samples(X_scaled) # Lower score = more anomalous
    
    # Filter only anomalies
    anomalies_df = df_clean[df_clean['anomaly_label'] == -1].copy()
    
    # Categorize anomalies based on feature thresholds (Rule-based post-processing)
    anomalies_df['anomaly_type'] = anomalies_df.apply(categorize_anomaly, axis=1)
    
    print(f"Detected {len(anomalies_df)} anomalies out of {len(df_clean)} records.")
    return anomalies_df

def categorize_anomaly(row):
    """Heuristic function to label the type of anomaly based on Phase 8 goals."""
    if row['rolling_goals'] > 3 or row['rolling_xG'] > 2.5:
        return "Goal Surge"
    elif row['Pace'] < 50 or row['Physical'] < 50:
        return "Injury-like Performance / Sudden Form Drop"
    elif row['Age'] < 21 and row['Overall'] > 89:
        return "Unusual Statistics (Wonderkid)"
    elif row['rolling_xGA'] > 2.0:
        return "Defensive Collapse"
    else:
        return "General Statistical Outlier"

def save_artifacts(model, scaler, anomalies_df):
    """Saves the model, scaler, and anomaly report to disk."""
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(MODEL_OUTPUT_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(ANOMALY_REPORT_PATH), exist_ok=True)
    
    # Save Model and Scaler
    joblib.dump(model, MODEL_OUTPUT_PATH)
    joblib.dump(scaler, SCALER_OUTPUT_PATH)
    print(f"Model saved to {MODEL_OUTPUT_PATH}")
    print(f"Scaler saved to {SCALER_OUTPUT_PATH}")
    
    # Save Anomaly Report
    anomalies_df.to_csv(ANOMALY_REPORT_PATH, index=False)
    print(f"Anomaly report saved to {ANOMALY_REPORT_PATH}")

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    print("="*50)
    print("STATVAULT AI - PHASE 8: ANOMALY DETECTION")
    print("="*50)
    
    # 1. Load Data
    df = load_data(INPUT_DATA_PATH)
    
    # 2. Preprocess
    X_scaled, scaler, df_clean = preprocess_data(df)
    
    # 3. Train Model
    model = train_anomaly_model(X_scaled)
    
    # 4. Detect & Report
    anomalies_df = detect_and_report(model, X_scaled, df_clean)
    
    # 5. Save Artifacts
    save_artifacts(model, scaler, anomalies_df)
    
    print("="*50)
    print("Phase 8 Completed Successfully!")
    print("="*50)