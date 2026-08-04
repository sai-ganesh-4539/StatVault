#IMPORTATIONS

#logging helps in recording information messages,warnings,errors
import logging
#sys provides acess to interpreter features
import sys
#used for managing paths
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

#FUNCTION HELPS IN CONFIGUR OF LOGGING 
logging.basicConfig(
    #sets minimum security level to display
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    #decides where logs should go 
    handlers=[logging.StreamHandler(sys.stdout)]
)
#helps in retrieving the logger
logger = logging.getLogger(__name__)

#RELATED TO PATHS
BASE_DIR = Path(__file__).resolve().parent
#paths for datset directories
RAW_DIR = BASE_DIR / "data" / "raw"
FEATURE_DIR = BASE_DIR / "data" / "features"
#mkdir creates folders
FEATURE_DIR.mkdir(parents=True, exist_ok=True)

PATHS = {
    "fifa22": RAW_DIR / "fifa22" / "players_22.csv",
    "fifa24": RAW_DIR / "fifa24-25" / "players_data-2024_2025.csv",
    "matches": RAW_DIR / "matches" / "matches.csv",
    "player_scores": RAW_DIR / "player_scores" / "appearances.csv", 
}

COLUMN_MAP = {
    "age": "age", "overall": "overall_rating", "potential": "potential",
    "pace": "pace", "shooting": "shooting", "passing": "passing",
    "dribbling": "dribbling", "defending": "defending", "physic": "physical",
    "physical": "physical", "preferred_foot": "preferred_foot",
    "player_positions": "position", "position": "position",
    "height_cm": "height", "weight_kg": "weight", "height": "height", "weight": "weight",
    "value_eur": "market_value", "market_value": "market_value",
    "goals": "goals", "assists": "assists", "minutes_played": "minutes_played",
    "minutes": "minutes_played", "pass_accuracy": "pass_accuracy",
    "yellow_cards": "cards", "red_cards": "cards", "cards": "cards",
    "expected_goals": "xg", "xg": "xg",
    "ftr": "ftresult", "res": "result", "match_result": "match_result", 
    "home_team": "home_team", "away_team": "away_team", "div": "division", "division": "division",
    "date": "date", "match_date": "date", "season": "season",
    "fthg": "home_goals", "ftag": "away_goals", "hthg": "ht_home_goals", "htag": "ht_away_goals",
    "hs": "home_shots", "as_": "away_shots", "hst": "home_shots_target", "ast": "away_shots_target",
    "hf": "home_fouls", "af": "away_fouls", "hc": "home_corners", "ac": "away_corners",
    "hy": "home_yellow", "ay": "away_yellow", "hr": "home_red", "ar": "away_red",
    "b365h": "odds_home", "b365d": "odds_draw", "b365a": "odds_away",
}

#HELPS IN FINDING DATASETS
def find_available_datasets() -> Dict[str, Path]:
    #creates a dictinory to store available datsets
    available = {}
    for key, path in PATHS.items():
        #if dataste is avilable it pushes to avialable dictinary
        if path.exists():
            available[key] = path
        #otherwise checks the datset of format csv
        else:
            parent = path.parent
            if parent.exists():
                csvs = list(parent.glob("*.csv"))
                if csvs:
                    available[key] = csvs[0]
    #otherwise checks the datset of format csv
    if not available:
        all_csvs = list(RAW_DIR.rglob("*.csv"))
        if all_csvs:
            for i, csv in enumerate(all_csvs):
                available[f"fallback_{i}"] = csv
        else:
            raise FileNotFoundError(f"NO CSV FILES FOUND in {RAW_DIR}")
        
    return available

#HELPS IN CLEANING THE DATASTET
def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    #strips all leading spaces and converts column names to lowercase
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    if 'as' in df.columns:
        df = df.rename(columns={'as': 'as_'})
    #identifies and staores all columns of string typw
    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()

    return df

#STANDARDIZES COLUMNS BY REMOVING DUPLICATE COLUMNS

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    #creates a dictionary
    valid_map = {k: v for k, v in COLUMN_MAP.items() if k in df.columns}
    df = df.rename(columns=valid_map)
    #drops the duplicate
    df = df.loc[:, ~df.columns.duplicated()]

    return df

#BUILDS A FEATURE ENGINEERRED DATAFRAME FOR DATA ANALYSIS
def build_player_features(df: pd.DataFrame) -> pd.DataFrame:

    numeric_cols = ["age", "overall_rating", "potential", "pace", "shooting",
                    "passing", "dribbling", "defending", "physical", "height", "weight"]
    
    categorical_cols = ["preferred_foot", "position"]

    target_col = "market_value"

    all_required = numeric_cols + categorical_cols + [target_col]
    available = [c for c in all_required if c in df.columns]

    if target_col not in df.columns:

        return pd.DataFrame()
    
    #copies the whole dataframe 
    df_clean = df[available].copy()
    #converts to numeric
    df_clean[target_col] = pd.to_numeric(df_clean[target_col], errors="coerce")
    #removes rows with missing target value 
    df_clean = df_clean.dropna(subset=[target_col])
    df_clean = df_clean[df_clean[target_col] > 0]

    for col in numeric_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
            #fills the misisnf values with median for overcoming loss of accuracy
            df_clean[col] = df_clean[col].fillna(df_clean[col].median())

    for col in categorical_cols:
        if col in df_clean.columns:
            #fills missing categorical rows with unkown
            df_clean[col] = df_clean[col].fillna("Unknown")
    final_cols = [c for c in all_required if c in df_clean.columns]

    return df_clean[final_cols]

#FRORMATS THE DATSET FOR MODEL SO NO MISSINFG VALUES OR ANYTHING OCCURS
def build_match_features(df: pd.DataFrame) -> pd.DataFrame:

    target_candidates = ["ftresult", "result", "match_result", "outcome", "winner"]
    time_candidates = ["date", "match_date", "kickoff", "season"]

    actual_target = next((c for c in target_candidates if c in df.columns), None)
    actual_time = next((c for c in time_candidates if c in df.columns), None)
    
    if not actual_target:
        return pd.DataFrame()
    df_clean = df.copy()

    if actual_time:
        #converts the time column to datetime format
        df_clean[actual_time] = pd.to_datetime(df_clean[actual_time], errors="coerce")
        df_clean = df_clean.dropna(subset=[actual_time])
        df_clean = df_clean.sort_values(by=actual_time)

    return df_clean.dropna(subset=[actual_target])

#SELECTS RELEVANT ATTRIBURES IN DATSET FOR CLUSTERING

def build_clustering_features(df: pd.DataFrame) -> pd.DataFrame:

    cluster_cols = ["pace", "shooting", "passing", "dribbling", "defending",
                    "physical", "age", "height", "weight"]
    
    available = [c for c in cluster_cols if c in df.columns]

    if len(available) < 4:
        return pd.DataFrame()
    df_cluster = df[available].copy()

    for col in available:
        df_cluster[col] = pd.to_numeric(df_cluster[col], errors="coerce")
    df_cluster = df_cluster.dropna()

    if df_cluster.empty:
        return pd.DataFrame()
    #standardizes eac featue so all can come in same range
    scaler = StandardScaler()
    df_cluster[available] = scaler.fit_transform(df_cluster[available])

    return df_cluster

#BUILDS DATSFRAME FOR ANAMOLY DETECTION

def build_anomaly_features(df: pd.DataFrame) -> pd.DataFrame:

    anomaly_base = ["goals", "assists", "minutes_played", "pass_accuracy", "cards", "xg"]
    available = [c for c in anomaly_base if c in df.columns]

    if not available:
        return pd.DataFrame()
    
    df_anom = df[available].copy()
    #removes duplicate columns
    df_anom = df_anom.loc[:, ~df_anom.columns.duplicated()]

    for col in df_anom.columns:
        df_anom[col] = pd.to_numeric(df_anom[col], errors="coerce")
        median_val = df_anom[col].median()
        #fills missing values with median if median is less than 0 fills iwth 0
        df_anom[col] = df_anom[col].fillna(median_val if median_val > 0 else 0)
    
    if "goals" in df_anom.columns:
        #gets averagegoals for last 5 games
        df_anom["rolling_mean"] = df_anom["goals"].rolling(5, min_periods=1).mean()
        #gets stanfdard deviation for last 5 games
        df_anom["rolling_std"] = df_anom["goals"].rolling(5, min_periods=1).std().fillna(0)
        df_anom["performance_trend"] = df_anom["goals"].diff().fillna(0) 

    return df_anom

#GETS COMPLETE FEATURE ENGINEERING PIPELINE OF WHOLE FILE

def main():

    logger.info("Starting Phase 3: Feature Engineering")
    datasets = find_available_datasets()
    logger.info(f"Found datasets: {list(datasets.keys())}")
    #creates 3 lists by category
    match_dfs, player_dfs, stats_dfs = [], [], []

    for name, path in datasets.items():

        logger.info(f"Loading {name} from {path}")

        #low_memory=false avoids dtype warnings
        df = pd.read_csv(path, low_memory=False) 
        df = clean_dataframe(df)
        df = standardize_columns(df)
        df["source_dataset"] = name

        #concats all match dataframes
        if "ftresult" in df.columns or "home_team" in df.columns or "away_team" in df.columns:
            match_dfs.append(df)
        elif "goals" in df.columns or "assists" in df.columns:
            stats_dfs.append(df) 
        else:
            player_dfs.append(df)
    
    #concates all player dataframe
    if match_dfs:

        df_match_feat = build_match_features(pd.concat(match_dfs, ignore_index=True))

        if not df_match_feat.empty:

            df_match_feat.to_parquet(FEATURE_DIR / "match_features.parquet", index=False)
            logger.info(f"Saved match features -> {FEATURE_DIR / 'match_features.parquet'}")

    if player_dfs:

        df_players_raw = pd.concat(player_dfs, ignore_index=True)
        df_players = build_player_features(df_players_raw)

        if not df_players.empty:

            df_players.to_parquet(FEATURE_DIR / "player_features.parquet", index=False)
            logger.info(f"Saved player features -> {FEATURE_DIR / 'player_features.parquet'}")
        df_cluster = build_clustering_features(df_players_raw)

        if not df_cluster.empty:

            df_cluster.to_parquet(FEATURE_DIR / "clustering_features.parquet", index=False)
            logger.info(f"Saved clustering features -> {FEATURE_DIR / 'clustering_features.parquet'}")

    if stats_dfs:

        df_stats = pd.concat(stats_dfs, ignore_index=True)
        df_anom = build_anomaly_features(df_stats)

        if not df_anom.empty:

            df_anom.to_parquet(FEATURE_DIR / "anomaly_features.parquet", index=False)
            logger.info(f"Saved anomaly features -> Columns: {list(df_anom.columns)}")

    else:
        
        logger.warning("No match statistics (goals/assists) found for anomaly detection.")
    logger.info("Phase 3: Feature Engineering completed successfully.")

if __name__ == "__main__":
    main()