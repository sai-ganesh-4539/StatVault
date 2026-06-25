# scripts/download_datasets.py
import os
import subprocess
import sys
from pathlib import Path

# CONFIGURATION
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"

# Ensure directories exist
dirs_to_create = [
    RAW_DATA_DIR / "international",
    RAW_DATA_DIR / "fifa_rankings",
    RAW_DATA_DIR / "club_matches",
    RAW_DATA_DIR / "fifa23",
    RAW_DATA_DIR / "fifa22",
    RAW_DATA_DIR / "player_stats",
    RAW_DATA_DIR / "player_scores"
]
for d in dirs_to_create:
    d.mkdir(parents=True, exist_ok=True)

# KAGGLE DATASET COMMANDS (From Roadmap)
datasets = [
    {
        "name": "International Football Results",
        "cmd": f"kaggle datasets download -d martj42/international-football-results-from-1872-to-2017 -p {RAW_DATA_DIR / 'international'} --unzip"
    },
    {
        "name": "FIFA Rankings",
        "cmd": f"kaggle datasets download -d tadhgfitzgerald/fifa-international-soccer-mens-ranking-1993now -p {RAW_DATA_DIR / 'fifa_rankings'} --unzip"
    },
    {
        "name": "FIFA 23 Complete Dataset",
        "cmd": f"kaggle datasets download -d stefanoleone992/fifa-23-complete-player-dataset -p {RAW_DATA_DIR / 'fifa23'} --unzip"
    },
    {
        "name": "Club Football Matches",
        "cmd": f"kaggle datasets download -d adamgbor/club-football-match-data-2000-2025 -p {RAW_DATA_DIR / 'club_matches'} --unzip"
    }
]

# EXECUTION
def check_kaggle_api():
    """Check if Kaggle API is configured."""
    home = Path.home()
    kaggle_json = home / ".kaggle" / "kaggle.json"
    if not kaggle_json.exists():
        print(" ERROR: Kaggle API not configured!")
        print("1. Go to Kaggle.com -> Account -> Create New API Token")
        print(f"2. Move the downloaded kaggle.json to: {kaggle_json}")
        sys.exit(1)
    print(" Kaggle API configuration found.")

def download_data():
    print(" Starting Real Data Ingestion (Phase 1)...\n")
    check_kaggle_api()
    
    for dataset in datasets:
        print(f" Downloading: {dataset['name']}...")
        try:
            # Run the kaggle CLI command
            result = subprocess.run(dataset['cmd'], shell=True, check=True, capture_output=True, text=True)
            print(f" Success: {dataset['name']}\n")
        except subprocess.CalledProcessError as e:
            print(f" Warning: Failed to download {dataset['name']}. Error: {e.stderr}\n")

if __name__ == "__main__":
    download_data()
    print(" Phase 1 Complete! Real datasets are now in data/raw/")