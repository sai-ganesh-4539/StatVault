"""
Warehouse Builder Module
Orchestrates the building of the file-based data warehouse.
Saves facts and dimensions as CSV, and schema as JSON.
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class WarehouseBuilder:
    """Builds and saves the file-based data warehouse."""

    def __init__(self, warehouse_path: str = "data/warehouse"):
        self.warehouse_path = Path(warehouse_path)
        self.facts_path = self.warehouse_path / "facts"
        self.dims_path = self.warehouse_path / "dimensions"
        self.metadata_path = self.warehouse_path / "metadata"

    def _create_directories(self):
        """Create warehouse directory structure."""
        self.facts_path.mkdir(parents=True, exist_ok=True)
        self.dims_path.mkdir(parents=True, exist_ok=True)
        self.metadata_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Warehouse directories created at {self.warehouse_path}")

    def _save_csv(self, df: pd.DataFrame, name: str, path: Path):
        """Save a DataFrame as CSV."""
        file_path = path / f"{name}.csv"
        df.to_csv(file_path, index=False, encoding="utf-8")
        logger.info(f"  Saved {file_path} ({len(df)} rows)")

    def _generate_schema(self, facts: Dict[str, pd.DataFrame],
                         dimensions: Dict[str, pd.DataFrame]) -> dict:
        """Generate warehouse schema metadata as JSON."""
        schema = {
            "warehouse_name": "StatVault AI Data Warehouse",
            "version": "2.0",
            "created_at": datetime.now().isoformat(),
            "type": "file_based_star_schema",
            "dimensions": {},
            "facts": {},
        }

        for name, df in dimensions.items():
            schema["dimensions"][name] = {
                "rows": len(df),
                "columns": list(df.columns),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "file": f"dimensions/{name}.csv",
            }

        for name, df in facts.items():
            schema["facts"][name] = {
                "rows": len(df),
                "columns": list(df.columns),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "file": f"facts/{name}.csv",
            }

        return schema

    def build(self, facts: Dict[str, pd.DataFrame],
              dimensions: Dict[str, pd.DataFrame]):
        """Build the complete warehouse."""
        logger.info("=" * 60)
        logger.info("BUILDING FILE-BASED DATA WAREHOUSE")
        logger.info("=" * 60)

        self._create_directories()

        # Save dimensions
        logger.info("\nSaving Dimension Tables...")
        for name, df in dimensions.items():
            if not df.empty:
                self._save_csv(df, name, self.dims_path)

        # Save facts
        logger.info("\nSaving Fact Tables...")
        for name, df in facts.items():
            if not df.empty:
                self._save_csv(df, name, self.facts_path)

        # Save schema metadata
        schema = self._generate_schema(facts, dimensions)
        schema_file = self.metadata_path / "warehouse_schema.json"
        with open(schema_file, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, default=str)
        logger.info(f"\n  Saved schema: {schema_file}")

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("WAREHOUSE BUILD COMPLETE")
        logger.info("=" * 60)
        logger.info(f"  Dimensions: {len(dimensions)} tables")
        logger.info(f"  Facts: {len(facts)} tables")
        logger.info(f"  Location: {self.warehouse_path.absolute()}")
        logger.info("=" * 60)

        return schema