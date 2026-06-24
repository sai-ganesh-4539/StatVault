import os
import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# ==========================================
# CONFIGURATION & PATHS
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"
DATA_FEATURES_DIR = BASE_DIR / "data" / "features"

# Ensure output directory exists
DATA_FEATURES_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# 1. MATCH FEATURES ENGINEERING
# ==========================================
def build_match_features(matches_df, rankings_df=None):
    """
    Builds advanced match features including form, goals, home advantage,
    historical H2H, rankings, and rolling statistics.
    """
    print("🚀 Building Match Features...")
    df = matches_df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['date']).reset_index(drop=True)
    
    # --- Basic Goal Features ---
    df['home_goals_scored'] = df['home_score']
    df['away_goals_scored'] = df['away_score']
    df['home_goals_conceded'] = df['away_score']
    df['away_goals_conceded'] = df['home_score']
    df['home_goal_diff'] = df['home_goals_scored'] - df['home_goals_conceded']
    df['away_goal_diff'] = df['away_goals_scored'] - df['away_goals_conceded']

    # --- Historical Head-to-Head (H2H) Features ---
    print("  -> Calculating Head-to-Head (H2H) History...")
    history_wins = {}
    history_draws = {}
    h2h_wins_list = []
    h2h_draws_list = []

    for row in df.itertuples():
        h = row.home_team
        a = row.away_team
        
        win_key = (h, a)
        draw_key = tuple(sorted([h, a]))
        
        h2h_wins_list.append(history_wins.get(win_key, 0))
        h2h_draws_list.append(history_draws.get(draw_key, 0))
        
        if row.home_score > row.away_score:
            history_wins[win_key] = history_wins.get(win_key, 0) + 1
        elif row.home_score == row.away_score:
            history_draws[draw_key] = history_draws.get(draw_key, 0) + 1

    df['h2h_home_wins'] = h2h_wins_list
    df['h2h_draws'] = h2h_draws_list

    # --- Team Form & Rolling Stats (Last 5 Matches) ---
    print("  -> Calculating Rolling Form & Stats...")
    def calculate_rolling_features(df):
        temp = df[['home_team', 'away_team', 'home_score', 'away_score', 'date']].copy()
        temp.columns = ['team', 'opponent', 'goals_scored', 'goals_conceded', 'date']
        
        temp_away = df[['away_team', 'home_team', 'away_score', 'home_score', 'date']].copy()
        temp_away.columns = ['team', 'opponent', 'goals_scored', 'goals_conceded', 'date']
        
        all_matches = pd.concat([temp, temp_away]).sort_values(['team', 'date'])
        
        all_matches['result'] = np.where(
            all_matches['goals_scored'] > all_matches['goals_conceded'], 3,
            np.where(all_matches['goals_scored'] == all_matches['goals_conceded'], 1, 0)
        )
        all_matches['is_win'] = (all_matches['result'] == 3).astype(int)
        all_matches['is_draw'] = (all_matches['result'] == 1).astype(int)
        all_matches['is_loss'] = (all_matches['result'] == 0).astype(int)

        rolling_cols = ['is_win', 'is_draw', 'is_loss', 'result', 'goals_scored', 'goals_conceded']
        for col in rolling_cols:
            all_matches[f'rolling_{col}'] = all_matches.groupby('team')[col].transform(
                lambda x: x.shift(1).rolling(5, min_periods=1).sum()
            )
        all_matches['rolling_ppg'] = all_matches['rolling_result'] / 5.0
        return all_matches

    form_df = calculate_rolling_features(df)

    # Rename columns for Home Team merging
    home_form = form_df.rename(columns={
        'team': 'home_team', 
        'rolling_is_win': 'home_last5_wins', 'rolling_is_draw': 'home_last5_draws', 'rolling_is_loss': 'home_last5_losses',
        'rolling_ppg': 'home_ppg', 'rolling_goals_scored': 'home_rolling_goals', 'rolling_goals_conceded': 'home_rolling_goals_conceded'
    })

    # Rename columns for Away Team merging
    away_form = form_df.rename(columns={
        'team': 'away_team', 
        'rolling_is_win': 'away_last5_wins', 'rolling_is_draw': 'away_last5_draws', 'rolling_is_loss': 'away_last5_losses',
        'rolling_ppg': 'away_ppg', 'rolling_goals_scored': 'away_rolling_goals', 'rolling_goals_conceded': 'away_rolling_goals_conceded'
    })

    # ✅ FIX: Use pd.merge to safely join rolling stats back to the main dataframe
    home_merge_cols = ['home_team', 'date', 'home_last5_wins', 'home_last5_draws', 'home_last5_losses', 
                       'home_ppg', 'home_rolling_goals', 'home_rolling_goals_conceded']
    away_merge_cols = ['away_team', 'date', 'away_last5_wins', 'away_last5_draws', 'away_last5_losses', 
                       'away_ppg', 'away_rolling_goals', 'away_rolling_goals_conceded']

    df = df.merge(home_form[home_merge_cols], on=['home_team', 'date'], how='left')
    df = df.merge(away_form[away_merge_cols], on=['away_team', 'date'], how='left')

    # Fallback for xG/xGA if not present in raw data
    df['home_rolling_xG'] = df.get('home_xG', df['home_rolling_goals']) 
    df['away_rolling_xG'] = df.get('away_xG', df['away_rolling_goals'])
    df['home_rolling_xGA'] = df.get('home_xGA', df['home_rolling_goals_conceded'])
    df['away_rolling_xGA'] = df.get('away_xGA', df['away_rolling_goals_conceded'])

    # --- Home/Away Win Rates ---
    print("  -> Calculating Home/Away Win Rates...")
    home_win_rates = df.groupby('home_team').apply(lambda x: (x['home_score'] > x['away_score']).mean()).reset_index()
    home_win_rates.columns = ['team', 'home_win_rate']
    df = df.merge(home_win_rates, left_on='home_team', right_on='team', how='left').drop('team', axis=1)

    away_win_rates = df.groupby('away_team').apply(lambda x: (x['away_score'] > x['home_score']).mean()).reset_index()
    away_win_rates.columns = ['team', 'away_win_rate']
    df = df.merge(away_win_rates, left_on='away_team', right_on='team', how='left').drop('team', axis=1)

    # --- Ranking Features ---
    if rankings_df is not None:
        print("  -> Merging FIFA Rankings & ELO...")
        df = df.merge(rankings_df[['team', 'rank', 'elo']], left_on=['home_team', 'date'], right_on=['team', 'date'], how='left')
        df = df.rename(columns={'rank': 'home_fifa_rank', 'elo': 'home_elo'}).drop('team', axis=1)
        
        df = df.merge(rankings_df[['team', 'rank', 'elo']], left_on=['away_team', 'date'], right_on=['team', 'date'], how='left')
        df = df.rename(columns={'rank': 'away_fifa_rank', 'elo': 'away_elo'}).drop('team', axis=1)
        
        df['fifa_rank_diff'] = df['away_fifa_rank'] - df['home_fifa_rank'] 
        df['elo_diff'] = df['home_elo'] - df['away_elo']
    else:
        df['home_fifa_rank'] = np.nan; df['away_fifa_rank'] = np.nan; df['fifa_rank_diff'] = np.nan
        df['home_elo'] = np.nan; df['away_elo'] = np.nan; df['elo_diff'] = np.nan

    print("✅ Match Features Built Successfully!")
    return df

# ==========================================
# 2. PLAYER FEATURES ENGINEERING
# ==========================================
def build_player_features(fifa_df):
    """
    Extracts and standardizes player features from FIFA datasets.
    """
    print("🚀 Building Player Features...")
    df = fifa_df.copy()
    
    # ✅ PRESERVE PLAYER NAME COLUMN
    name_col = None
    if 'short_name' in df.columns:
        name_col = 'short_name'
    elif 'player_name' in df.columns:
        name_col = 'player_name'
    elif 'name' in df.columns:
        name_col = 'name'
    
    col_mapping = {
        'age': 'age', 'height_cm': 'height', 'weight_kg': 'weight',
        'overall': 'overall_rating', 'potential': 'potential',
        'pace': 'pace', 'shooting': 'shooting', 'passing': 'passing',
        'dribbling': 'dribbling', 'defending': 'defending', 'physic': 'physical',
        'preferred_foot': 'preferred_foot', 'player_positions': 'position'
    }

    valid_mapping = {k: v for k, v in col_mapping.items() if k in df.columns}
    df = df[list(valid_mapping.keys())].rename(columns=valid_mapping)
    
    # ✅ ADD NAME COLUMN BACK IF IT EXISTS
    if name_col and name_col in fifa_df.columns:
        df[name_col] = fifa_df[name_col]

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())
        
    categorical_cols = ['preferred_foot', 'position']
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].fillna('Unknown')

    print("✅ Player Features Built Successfully!")
    return df

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    print("📊 STATVAULT AI - Phase 4: Feature Engineering\n")
    
    matches_path = DATA_PROCESSED_DIR / "cleaned_matches.csv"
    fifa_path = BASE_DIR / "data" / "raw" / "fifa23" / "players_23.csv" 

    if not matches_path.exists():
        print(f"⚠️ Warning: {matches_path} not found. Creating dummy match data for testing.")
        teams = ['Arsenal', 'Chelsea', 'Liverpool', 'Man Utd', 'Man City', 'Tottenham']
        matches_df = pd.DataFrame({
            'date': pd.date_range(start='2023-01-01', periods=100, freq='D'),
            'home_team': np.random.choice(teams, 100),
            'away_team': np.random.choice(teams, 100),
            'home_score': np.random.randint(0, 4, 100),
            'away_score': np.random.randint(0, 4, 100)
        })
    else:
        matches_df = pd.read_csv(matches_path)

    if not fifa_path.exists():
        print(f"⚠️ Warning: {fifa_path} not found. Creating dummy player data for testing.")
        player_df = pd.DataFrame({
            'age': np.random.randint(18, 35, 50), 'height_cm': np.random.randint(170, 195, 50),
            'weight_kg': np.random.randint(65, 90, 50), 'overall': np.random.randint(60, 95, 50),
            'potential': np.random.randint(70, 99, 50), 'pace': np.random.randint(50, 99, 50),
            'shooting': np.random.randint(50, 99, 50), 'passing': np.random.randint(50, 99, 50),
            'dribbling': np.random.randint(50, 99, 50), 'defending': np.random.randint(50, 99, 50),
            'physic': np.random.randint(50, 99, 50), 'preferred_foot': np.random.choice(['Left', 'Right'], 50),
            'player_positions': np.random.choice(['ST', 'CM', 'CB', 'LW'], 50),
            'short_name': [f"Player_{i}" for i in range(50)]  # ✅ Added name column
        })
    else:
        player_df = pd.read_csv(fifa_path)

    # Build Features
    match_features_df = build_match_features(matches_df)
    player_features_df = build_player_features(player_df)
    
    # ✅ SAVE MATCH FEATURES
    match_features_df.to_csv(DATA_FEATURES_DIR / "match_features.csv", index=False)
    print(f"✅ Match features saved to {DATA_FEATURES_DIR / 'match_features.csv'}")
    
    # ✅ SAVE PLAYER FEATURES WITH NAME COLUMN
    feature_cols = ['age', 'height', 'weight', 'overall_rating', 'potential',
                    'pace', 'shooting', 'passing', 'dribbling', 'defending',
                    'physical', 'preferred_foot', 'position']
    
    # Check which name column exists
    name_col = None
    if 'short_name' in player_features_df.columns:
        name_col = 'short_name'
    elif 'player_name' in player_features_df.columns:
        name_col = 'player_name'
    elif 'name' in player_features_df.columns:
        name_col = 'name'
    
    # Select columns to save
    if name_col:
        final_columns = [name_col] + feature_cols
    else:
        final_columns = feature_cols
    
    # Filter to only existing columns
    final_columns = [col for col in final_columns if col in player_features_df.columns]
    
    player_features_df[final_columns].to_csv(DATA_FEATURES_DIR / "player_features.csv", index=False)
    print(f"✅ Player features saved to {DATA_FEATURES_DIR / 'player_features.csv'}")
    
    print("\n🎉 Phase 4 Complete!")