import os
import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# ==========================================
# 1. CONFIGURATION & PATHS
# ==========================================
PROJECT_ROOT = Path(__file__).parent.parent.parent 
INPUT_DATA_PATH = PROJECT_ROOT / "data" / "features" / "player_features.csv"
MODEL_OUTPUT_PATH = PROJECT_ROOT / "models" / "player_clusters.pkl"
REPORT_OUTPUT_PATH = PROJECT_ROOT / "reports" / "player_profiles.json"

# Ensure output directories exist
MODEL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
REPORT_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# Define the 6 target clusters/roles
TARGET_ROLES = ['Poacher', 'Playmaker', 'Winger', 'Ball Winner', 'Target Man', 'Box-to-Box']

# Define the core attributes used for clustering
CLUSTERING_FEATURES = ['pace', 'shooting', 'passing', 'dribbling', 'defending', 'physical']

# ==========================================
# 2. DATA LOADING & PREPROCESSING
# ==========================================
def load_data():
    """Loads player features. Generates mock data if the real CSV is missing."""
    if not INPUT_DATA_PATH.exists():
        print(f"⚠️ Warning: {INPUT_DATA_PATH} not found. Generating mock data for testing...")
        np.random.seed(42)
        n_players = 500
        mock_data = {
            'player_name': [f"Player_{i}" for i in range(n_players)],
            'age': np.random.randint(18, 36, n_players),
            'overall_rating': np.random.randint(50, 95, n_players),
            'pace': np.random.randint(40, 99, n_players),
            'shooting': np.random.randint(40, 99, n_players),
            'passing': np.random.randint(40, 99, n_players),
            'dribbling': np.random.randint(40, 99, n_players),
            'defending': np.random.randint(40, 99, n_players),
            'physical': np.random.randint(40, 99, n_players)
        }
        return pd.DataFrame(mock_data)
    
    print(f"✅ Loading data from {INPUT_DATA_PATH}...")
    df = pd.read_csv(INPUT_DATA_PATH)
    
    # Ensure required clustering columns exist
    missing_cols = [col for col in CLUSTERING_FEATURES if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required features in dataset: {missing_cols}")
        
    return df

# ==========================================
# 3. CLUSTER MAPPING LOGIC
# ==========================================
def map_clusters_to_roles(kmeans_model, feature_names):
    """
    Maps the unsupervised KMeans cluster IDs (0-5) to specific football roles 
    by analyzing the centroids (cluster centers).
    """
    centroids = kmeans_model.cluster_centers_
    centroid_df = pd.DataFrame(centroids, columns=feature_names)
    
    role_mapping = {}
    assigned_roles = set()
    
    # Heuristic mapping based on the primary defining attribute of each role
    role_primary_attr = {
        'Poacher': 'shooting',
        'Playmaker': 'passing',
        'Winger': 'pace',
        'Ball Winner': 'defending',
        'Target Man': 'physical',
        'Box-to-Box': 'dribbling' 
    }
    
    for role, attr in role_primary_attr.items():
        best_cluster = centroid_df[attr].idxmax()
        
        while best_cluster in assigned_roles:
            centroid_df.loc[best_cluster, attr] = -1 
            best_cluster = centroid_df[attr].idxmax()
            
        role_mapping[best_cluster] = role
        assigned_roles.add(best_cluster)
        
    return role_mapping

# ==========================================
# 4. MAIN EXECUTION PIPELINE
# ==========================================
def main():
    print("🚀 Starting Phase 6: Player Scouting Engine...")
    
    # Load Data
    df = load_data()
    
    # Filter out rows with missing core features
    df_clean = df.dropna(subset=CLUSTERING_FEATURES).copy()
    X = df_clean[CLUSTERING_FEATURES]
    
    # --- DYNAMIC COLUMN DETECTION ---
    # FIFA datasets usually use 'short_name' or 'long_name' instead of 'player_name'
    name_col = next((col for col in ['player_name', 'short_name', 'long_name', 'name'] if col in df_clean.columns), None)
    rating_col = next((col for col in ['overall_rating', 'overall', 'rating'] if col in df_clean.columns), None)
    
    if name_col is None:
        print("⚠️ Warning: No player name column found. Using index as ID.")
        df_clean['player_name'] = [f"Player_{i}" for i in range(len(df_clean))]
        name_col = 'player_name'
        
    if rating_col is None:
        print("⚠️ Warning: No overall rating column found. Will just list first 5 players per role.")
    else:
        print(f"✅ Detected Name Column: '{name_col}', Rating Column: '{rating_col}'")
    # ------------------------------------

    # Build Pipeline (Scaling + KMeans)
    print("🔧 Training KMeans Clustering Model...")
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('kmeans', KMeans(n_clusters=6, random_state=42, n_init=10))
    ])
    
    # Fit and predict
    cluster_labels = pipeline.fit_predict(X)
    df_clean['cluster_id'] = cluster_labels
    
    # Map clusters to actual football roles
    kmeans_model = pipeline.named_steps['kmeans']
    cluster_to_role = map_clusters_to_roles(kmeans_model, CLUSTERING_FEATURES)
    
    # Apply role names to dataframe
    df_clean['player_role'] = df_clean['cluster_id'].map(cluster_to_role)
    
    # ==========================================
    # 5. SAVE OUTPUTS
    # ==========================================
    # 1. Save the Model
    print(f"💾 Saving model to {MODEL_OUTPUT_PATH}...")
    joblib.dump(pipeline, MODEL_OUTPUT_PATH)
    
    # 2. Save Player Profiles Report (JSON)
    print(f"📊 Generating player profiles report to {REPORT_OUTPUT_PATH}...")
    
    profiles = {}
    for role in TARGET_ROLES:
        role_players = df_clean[df_clean['player_role'] == role]
        
        # Calculate average stats for the role profile
        avg_stats = role_players[CLUSTERING_FEATURES].mean().round(2).to_dict()
        
        # Get top 5 players in this role based on overall rating
        top_players = []
        if rating_col:
            top_players = role_players.nlargest(5, rating_col)[name_col].tolist()
        else:
            top_players = role_players[name_col].head(5).tolist()
            
        profiles[role] = {
            "average_attributes": avg_stats,
            "player_count": len(role_players),
            "top_players": top_players
        }
        
    with open(REPORT_OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(profiles, f, indent=4)
        
    print("✅ Phase 6 Completed Successfully!")
    print(f"📁 Model saved at: {MODEL_OUTPUT_PATH}")
    print(f"📁 Report saved at: {REPORT_OUTPUT_PATH}")

if __name__ == "__main__":
    main()