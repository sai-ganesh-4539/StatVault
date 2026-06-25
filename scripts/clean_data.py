# scripts/clean_data.py
import os
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def clean_international_matches():
    print(" Cleaning International Matches...")
    raw_path = RAW_DIR / "international" / "results.csv"
    
    if not raw_path.exists():
        print(f" Warning: {raw_path} not found. Skipping international matches.")
        return None

    df = pd.read_csv(raw_path, parse_dates=['date'])
    
    # Standardize column names to match build_features.py expectations
    df = df.rename(columns={
        'home_team': 'home_team',
        'away_team': 'away_team',
        'home_score': 'home_score',
        'away_score': 'away_score'
    })
    
    # Drop rows where score is missing (e.g., upcoming matches or data errors)
    df = df.dropna(subset=['home_score', 'away_score'])
    
    # Convert scores to integers
    df['home_score'] = df['home_score'].astype(int)
    df['away_score'] = df['away_score'].astype(int)
    
    # Keep only necessary columns for the feature builder
    cols_to_keep = ['date', 'home_team', 'away_team', 'home_score', 'away_score']
    df = df[[col for col in cols_to_keep if col in df.columns]]
    
    print(f" Processed {len(df)} international matches.")
    return df

def main():
    print(" STATVAULT AI - Phase 2/3: Data Cleaning & Processing\n")
    
    # 1. Process Matches
    matches_df = clean_international_matches()
    
    if matches_df is not None and not matches_df.empty:
        # Sort by date
        matches_df = matches_df.sort_values('date')
        
        # Save to processed folder
        output_path = PROCESSED_DIR / "cleaned_matches.csv"
        matches_df.to_csv(output_path, index=False)
        print(f" Saved cleaned matches to {output_path}")
    else:
        print(" No match data was processed. Check your data/raw/international folder.")

if __name__ == "__main__":
    main()