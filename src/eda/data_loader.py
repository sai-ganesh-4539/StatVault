"""
Data Loader - Loads all raw CSV datasets for EDA.
"""
import os
import glob
import pandas as pd
from pathlib import Path


class DataLoader:
    """Loads raw CSV data from data/raw/ directory."""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.raw_path = self.base_path / "data" / "raw"
        self.datasets = {}

    def load_all(self) -> dict:
        """Load all available datasets from raw folder."""
        loaders = {
            "international": self._load_international,
            "fifa_rankings": self._load_fifa_rankings,
            "club_matches": self._load_club_matches,
            "fifa23_players": self._load_fifa23_players,
            "fifa22_players": self._load_fifa22_players,
            "player_stats_2024_25": self._load_player_stats_2024_25,
            "player_scores": self._load_player_scores,
        }

        for name, loader in loaders.items():
            try:
                self.datasets[name] = loader()
                print(f"✅ Loaded: {name} -> {self.datasets[name].shape}")
            except Exception as e:
                print(f"⚠️  Skipped: {name} -> {e}")

        return self.datasets

    def _find_csv(self, folder: str) -> list:
        """Find all CSV files in a given raw subfolder."""
        path = self.raw_path / folder
        if not path.exists():
            raise FileNotFoundError(f"Folder not found: {path}")
        files = glob.glob(str(path / "*.csv"))
        if not files:
            raise FileNotFoundError(f"No CSV files in {path}")
        return files

    def _load_international(self) -> pd.DataFrame:
        files = self._find_csv("international_results")
        dfs = [pd.read_csv(f, low_memory=False) for f in files]
        return pd.concat(dfs, ignore_index=True)

    def _load_fifa_rankings(self) -> pd.DataFrame:
        files = self._find_csv("fifa_rankings")
        dfs = [pd.read_csv(f, low_memory=False) for f in files]
        return pd.concat(dfs, ignore_index=True)

    def _load_club_matches(self) -> pd.DataFrame:
        files = self._find_csv("club_matches")
        dfs = [pd.read_csv(f, low_memory=False) for f in files]
        return pd.concat(dfs, ignore_index=True)

    def _load_fifa23_players(self) -> pd.DataFrame:
        files = self._find_csv("fifa23_players")
        df = pd.read_csv(files[0], low_memory=False)
        return df

    def _load_fifa22_players(self) -> pd.DataFrame:
        files = self._find_csv("fifa22_players")
        df = pd.read_csv(files[0], low_memory=False)
        return df

    def _load_player_stats_2024_25(self) -> pd.DataFrame:
        files = self._find_csv("player_stats_2024_25")
        dfs = [pd.read_csv(f, low_memory=False) for f in files]
        return pd.concat(dfs, ignore_index=True)

    def _load_player_scores(self) -> pd.DataFrame:
        files = self._find_csv("player_scores")
        dfs = [pd.read_csv(f, low_memory=False) for f in files]
        return pd.concat(dfs, ignore_index=True)

    def get(self, name: str) -> pd.DataFrame:
        if name not in self.datasets:
            raise KeyError(f"Dataset '{name}' not loaded.")
        return self.datasets[name]