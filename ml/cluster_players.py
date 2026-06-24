#IMPORTATIONS

import json
#tracks execution
import logging
#helps in managing paths
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
#helps in chaining mutiple preprocessing steps
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

logging.basicConfig(

    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",

)

logger = logging.getLogger(__name__)

BASE = Path(".")
INPUT = BASE / "data" / "features" / "clustering_features.parquet"
OUTPUT = BASE / "outputs" / "scouting_profiles.json"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

ROLE_DEFINITIONS: Dict[str, List[str]] = {
    "Playmakers": ["passing", "dribbling", "pace"],
    "Finishers": ["shooting", "pace", "dribbling"],
    "Wingers": ["pace", "dribbling", "passing"],
    "Ball Winners": ["defending", "physical", "pace"],
    "Defenders": ["defending", "physical", "height"],
    "Box-to-Box Midfielders": ["passing", "physical", "defending"],
    "Target Forwards": ["shooting", "physical", "height"],
    "Deep-Lying Playmakers": ["passing", "defending", "dribbling"],
}

#LOADS THE DATA FROM PARQUET FILES

def load_data() -> pd.DataFrame:

    if not INPUT.exists():

        raise FileNotFoundError(
            f"{INPUT} not found. Run build_features.py (Phase 3) first."
        )
    #reads input from parquet files
    df = pd.read_parquet(INPUT)
    #removes all the trailing spaces and lowercasses all the letters of colimsns
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    return df

#GETS THE COLUMNS OF REQUIRED FEATURES 

def get_feature_columns(df: pd.DataFrame) -> List[str]:

    candidates = [
        "pace", "shooting", "passing", "dribbling", "defending",
        "physical", "height", "weight", "age",
    ]

    available = [c for c in candidates if c in df.columns]

    if len(available) < 3:

        #selects only numeric columns
        num_cols = df.select_dtypes(include=[np.number]).columns
        available = [c for c in num_cols if c not in ("player_id",)]

    return available

#CATEGORIZES DATA POINTS BASED ON CLUSTERS

def match_clusters_to_roles(centroids: np.ndarray, features: List[str]) -> Dict[int, str]:

    #axis=0 means selects rows
    c_min = centroids.min(axis=0, keepdims=True)
    c_max = centroids.max(axis=0, keepdims=True)

    #maps all the points in rnage of [0,1]
    norm_centroids = np.where(c_max - c_min > 0, (centroids - c_min) / (c_max - c_min), 0.5)
    #creates a directory mapping
    feature_to_idx = {f: i for i, f in enumerate(features)}
    assignment = {}
    used_roles = set()

    for cluster_id in range(len(norm_centroids)):

        best_role = None
        best_score = -1

        for role, key_attrs in ROLE_DEFINITIONS.items():

            if role in used_roles:

                continue

            scores = []
            for attr in key_attrs:

                if attr in feature_to_idx:

                    scores.append(norm_centroids[cluster_id, feature_to_idx[attr]])
            avg_score = np.mean(scores) if scores else 0

            if avg_score > best_score:

                best_score = avg_score
                best_role = role

        if best_role is None:

            best_role = f"Cluster_{cluster_id}"
        assignment[cluster_id] = best_role
        used_roles.add(best_role)

    return assignment

def build_profiles(
    df: pd.DataFrame,
    labels: np.ndarray,
    features: List[str],
    role_map: Dict[int, str],
) -> Dict[str, Dict]:
    
    profiles = {}

    for cluster_id, role_name in role_map.items():

        mask = labels == cluster_id
        cluster_data = df.loc[mask, features]

        if cluster_data.empty:
            continue

        means = cluster_data.mean()
        top_traits = means.nlargest(min(3, len(means))).index.tolist()
        top_traits = [t.strip() for t in top_traits]

        profiles[role_name] = {
            "cluster_id": int(cluster_id),
            "player_count": int(mask.sum()),
            "dominant_traits": top_traits,
            "description": f"Players in this cluster excel in {', '.join(top_traits)}.",
        }

    return profiles

def main():

    try:

        df = load_data()
        features = get_feature_columns(df)
        logger.info(f"Clustering on {len(df)} players using features: {features}")

        X = df[features].fillna(df[features].median().fillna(0))
        n_clusters = min(8, max(4, len(df) // 100))

        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("kmeans", KMeans(n_clusters=n_clusters, random_state=42, n_init=10)),
        ])

        labels = pipeline.fit_predict(X)
        centroids = pipeline.named_steps["kmeans"].cluster_centers_

        scaler = pipeline.named_steps["scaler"]
        original_centroids = scaler.inverse_transform(centroids)
        role_map = match_clusters_to_roles(original_centroids, features)

        logger.info(f"Cluster → Role mapping: {role_map}")
        profiles = build_profiles(df, labels, features, role_map)

        with open(OUTPUT, "w", encoding="utf-8") as f:

            json.dump(profiles, f, indent=4, ensure_ascii=False)
        logger.info(f"✅ Saved {len(profiles)} scouting profiles → {OUTPUT}")

    except Exception as e:

        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise
    
if __name__ == "__main__":
    main()