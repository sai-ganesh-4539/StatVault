"""Centralized configuration."""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "StatVault API"
    app_env: str = "development"
    app_port: int = 8000

    # Database
    database_url: str = "postgresql+asyncpg://statvault:statvault@localhost:5432/statvault"

    # Model paths - support both old (ml/models/) and new (models/) layouts
    ml_models_dir: Path = Path("../ml/models")
    cluster_profiles_path: Path = Path("../ml/models/cluster_profiles.json")
    market_value_features_path: Path = Path("../ml/models/market_value_feature_names.txt")

    # External API
    football_data_org_key: str = ""

    @property
    def xgboost_match_path(self) -> Path:
        return self.ml_models_dir / "xgboost_match.onnx"

    @property
    def market_value_path(self) -> Path:
        return self.ml_models_dir / "market_value.onnx"

    @property
    def isolation_forest_path(self) -> Path:
        return self.ml_models_dir / "isolation_forest.onnx"


settings = Settings()