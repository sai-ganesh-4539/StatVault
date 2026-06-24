import logging
from pathlib import Path
import sys

try:

    from kaggle.api.kaggle_api_extended import KaggleApi

except ImportError:

    logging.error("Please install kaggle: pip install kaggle")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"

DATASETS = [
    {
        "name": "FIFA 24 Player Stats",
        "kaggle_id": "rehandl23/fifa-24-player-stats-dataset",
        "target_dir": RAW_DIR / "fifa24-25",
        "files": ["fifa24_players.csv"]
    },
    {
        "name": "FIFA 22 Complete Dataset",
        "kaggle_id": "stefanoleone992/fifa-22-complete-player-dataset",
        "target_dir": RAW_DIR / "fifa22",
        "files": ["players_22.csv"]
    },
    {
        "name": "Football Players Stats 2024-2025",
        "kaggle_id": "hubertsidorowicz/football-players-stats-2024-2025",
        "target_dir": RAW_DIR / "fifa24-25",
        "files": ["fbref_players.csv"]
    },
    {
        "name": "All Football Players Stats in Top 5 Leagues 23/24",
        "kaggle_id": "orkunaktas/all-football-players-stats-in-top-5-leagues-2324",
        "target_dir": RAW_DIR / "fifa24-25",
        "files": ["top5_leagues_stats.csv"]
    },
    {
        "name": "Player Scores (Transfermarkt)",
        "kaggle_id": "davidcariboo/player-scores",
        "target_dir": RAW_DIR / "player_scores",
        "files": ["players.csv", "clubs.csv", "games.csv", "player_valuations.csv"]
    },
    {
        "name": "Club Football Match Data 2000-2025",
        "kaggle_id": "adamgbor/club-football-match-data-2000-2025",
        "target_dir": RAW_DIR / "matches",
        "files": ["matches.csv"]
    }
]

def download_dataset(dataset_info):

    logger.info(f"\n{'='*60}")
    logger.info(f"Downloading: {dataset_info['name']}")
    logger.info(f"{'='*60}")

    try:

        api = KaggleApi()
        api.authenticate()
        target_dir = dataset_info['target_dir']
        target_dir.mkdir(parents=True, exist_ok=True)
        api.dataset_download_files(
            dataset=dataset_info['kaggle_id'],
            path=str(target_dir),
            unzip=True
        )

        logger.info(f"✓ Downloaded to {target_dir}")

    except Exception as e:

        logger.error(f"✗ Failed to download {dataset_info['name']}: {str(e)}")

def main():

    logger.info("Starting Dataset Download for StatVault ML")
    logger.info("Make sure you have Kaggle API credentials configured:")
    logger.info("  - Set KAGGLE_USERNAME and KAGGLE_KEY environment variables")
    logger.info("  - Or place kaggle.json in ~/.kaggle/\n")

    for dataset in DATASETS:

        download_dataset(dataset)

    logger.info("\n" + "="*60)
    logger.info("Download Complete!")
    logger.info("="*60)
    logger.info("\nNext steps:")
    logger.info("1. Run: python build_features.py")
    logger.info("2. Run: python train_market_value.py")

if __name__ == "__main__":
    
    main()