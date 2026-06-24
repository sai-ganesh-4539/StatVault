"""
Data Loader Module
Reads raw CSV files from Phase 1 into pandas DataFrames.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """Loads raw datasets from data/raw/ directory."""

    def __init__(self, raw_data_path: str = "data/raw"):
        self.raw_path = Path(raw_data_path)
        self.datasets: Dict[str, pd.DataFrame] = {}

    def load_csv(self, dataset_name: str, file_pattern: str = "*.csv") -> Optional[pd.DataFrame]:
        """Load a CSV file or merge multiple CSVs from a folder."""
        dataset_path = self.raw_path / dataset_name

        if not dataset_path.exists():
            logger.warning(f"Dataset path not found: {dataset_path}")
            return None

        # If it's a single file
        if dataset_path.is_file() and dataset_path.suffix == ".csv":
            df = pd.read_csv(dataset_path, low_memory=False)
            logger.info(f"Loaded {dataset_name}: {df.shape}")
            return df

        # If it's a folder with CSVs
        csv_files = list(dataset_path.glob(file_pattern))
        if not csv_files:
            logger.warning(f"No CSV files found in {dataset_path}")
            return None

        dfs = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file, low_memory=False)
                dfs.append(df)
                logger.info(f"  Loaded {csv_file.name}: {df.shape}")
            except Exception as e:
                logger.error(f"Error loading {csv_file.name}: {e}")

        if dfs:
            combined = pd.concat(dfs, ignore_index=True)
            logger.info(f"Combined {dataset_name}: {combined.shape}")
            return combined
        return None

    def load_all(self) -> Dict[str, pd.DataFrame]:
        """Load all raw datasets."""
        dataset_names = [
            "international_results",
            "fifa_rankings",
            "club_matches",
            "fifa22_players",
            "fifa23_players",
            "player_stats_2024_25",
            "player_scores",
        ]

        for name in dataset_names:
            df = self.load_csv(name)
            if df is not None:
                self.datasets[name] = df

        logger.info(f"Loaded {len(self.datasets)} datasets successfully.")
        return self.datasets

    def get(self, name: str) -> Optional[pd.DataFrame]:
        """Get a specific loaded dataset."""
        return self.datasets.get(name)