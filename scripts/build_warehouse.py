
import sys
from pathlib import Path

# Dynamically find the project root (D:\statvault-ml)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging
from src.warehouse.data_loader import DataLoader
from src.warehouse.data_transformer import DataTransformer
from src.warehouse.warehouse_builder import WarehouseBuilder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 60)
    logger.info("STATVAULT AI - PHASE 2: DATA WAREHOUSE")
    logger.info("=" * 60)

    #  Create absolute paths based on the project root
    raw_data_path = project_root / "data" / "raw"
    warehouse_path = project_root / "data" / "warehouse"

    # Step 1: Load raw data
    logger.info(f"\n[Step 1/3] Loading raw data from: {raw_data_path}")
    loader = DataLoader(raw_data_path=str(raw_data_path))
    datasets = loader.load_all()

    if not datasets:
        logger.error("No datasets loaded. Please ensure your unzipped folders are inside data/raw/")
        sys.exit(1)

    logger.info(f"Loaded datasets: {list(datasets.keys())}")

    # Step 2: Transform into Star Schema
    logger.info("\n[Step 2/3] Transforming data into Star Schema...")
    transformer = DataTransformer(datasets)
    facts, dimensions = transformer.transform()

    # Step 3: Build warehouse (save to CSV/JSON)
    logger.info(f"\n[Step 3/3] Saving warehouse to: {warehouse_path}")
    builder = WarehouseBuilder(warehouse_path=str(warehouse_path))
    schema = builder.build(facts, dimensions)

    logger.info("\n✅ Phase 2 Complete!")
    logger.info(f"Check {warehouse_path} for outputs.")

    return schema


if __name__ == "__main__":
    main()