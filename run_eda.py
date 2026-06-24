"""
STATVAULT AI - Phase 3: EDA Pipeline Runner
Run this script to generate all EDA reports in CSV and JSON formats.
"""
import sys
import os
from pathlib import Path

# --- FIX: Automatically find the true project root ---
CURRENT_DIR = Path(__file__).parent.resolve()

# If the script is inside the 'notebooks' folder, go up one level to the project root
if CURRENT_DIR.name == "notebooks":
    PROJECT_ROOT = CURRENT_DIR.parent
else:
    PROJECT_ROOT = CURRENT_DIR

# Add project root to sys.path so 'src' can be imported
sys.path.insert(0, str(PROJECT_ROOT))
# -----------------------------------------------------

from src.eda.data_loader import DataLoader
from src.eda.missing_values import MissingValueAnalyzer
from src.eda.outlier_detection import OutlierDetector
from src.eda.distributions import DistributionAnalyzer
from src.eda.correlation import CorrelationAnalyzer
from src.eda.player_analysis import PlayerAttributeAnalyzer
from src.eda.data_quality import DataQualityReporter


def main():
    print("=" * 60)
    print("  STATVAULT AI - Phase 3: Exploratory Data Analysis")
    print("=" * 60)

    # Ensure output directory exists in the project root
    output_dir = PROJECT_ROOT / "reports" / "eda"
    output_dir.mkdir(parents=True, exist_ok=True)

    # ==========================================
    # Step 1: Load Data
    # ==========================================
    print("\n📥 Step 1: Loading datasets...")
    print(f"📂 Looking for data in: {PROJECT_ROOT / 'data' / 'raw'}")
    print("-" * 60)
    
    loader = DataLoader(base_path=str(PROJECT_ROOT))
    datasets = loader.load_all()

    if not datasets:
        print("\n❌ ERROR: No datasets found!")
        print("\n💡 Please ensure your data/raw/ folders are populated.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print(f"✅ Successfully loaded {len(datasets)} dataset(s)")
    print("=" * 60)
    
    # Show what was loaded
    for name, df in datasets.items():
        print(f"  • {name:25s} -> {df.shape[0]:>8,} rows × {df.shape[1]:>3} columns")

    # ==========================================
    # Step 2: Missing Value Analysis
    # ==========================================
    print("\n📊 Step 2: Analyzing missing values...")
    try:
        mv_analyzer = MissingValueAnalyzer(output_dir=str(output_dir))
        mv_analyzer.analyze(datasets)
        print("✅ Missing value analysis complete")
    except Exception as e:
        print(f"⚠️  Missing value analysis failed: {e}")

    # ==========================================
    # Step 3: Outlier Detection
    # ==========================================
    print("\n Step 3: Detecting outliers...")
    try:
        outlier_detector = OutlierDetector(output_dir=str(output_dir))
        outlier_detector.analyze(datasets)
        print("✅ Outlier detection complete")
    except Exception as e:
        print(f"️  Outlier detection failed: {e}")

    # ==========================================
    # Step 4: Distribution Analysis
    # ==========================================
    print("\n📊 Step 4: Analyzing distributions (Teams, Goals, Rankings)...")
    try:
        dist_analyzer = DistributionAnalyzer(output_dir=str(output_dir))
        dist_analyzer.analyze(datasets)
        print("✅ Distribution analysis complete")
    except Exception as e:
        print(f"⚠️  Distribution analysis failed: {e}")

    # ==========================================
    # Step 5: Correlation Analysis
    # ==========================================
    print("\n📊 Step 5: Computing correlation matrices...")
    try:
        corr_analyzer = CorrelationAnalyzer(output_dir=str(output_dir))
        corr_analyzer.analyze(datasets)
        print("✅ Correlation analysis complete")
    except Exception as e:
        print(f"️  Correlation analysis failed: {e}")

    # ==========================================
    # Step 6: Player Attribute Analysis
    # ==========================================
    print("\n📊 Step 6: Analyzing player attributes...")
    # Filter for the exact dataset keys we loaded
    player_dataset_keys = ['fifa23_players', 'fifa22_players', 'player_stats_2024_25']
    available_player_datasets = {k: v for k, v in datasets.items() if k in player_dataset_keys}
    
    if available_player_datasets:
        try:
            player_analyzer = PlayerAttributeAnalyzer(output_dir=str(output_dir))
            player_analyzer.analyze(datasets) # Pass full datasets, it filters internally
            print("✅ Player attribute analysis complete")
        except Exception as e:
            print(f"⚠️  Player attribute analysis failed: {e}")
    else:
        print("⏭️  Skipped: No FIFA/player datasets available")

    # ==========================================
    # Step 7: Data Quality Report
    # ==========================================
    print("\n📊 Step 7: Generating comprehensive data quality report...")
    try:
        quality_reporter = DataQualityReporter(output_dir=str(output_dir))
        quality_reporter.analyze(datasets)
        print("✅ Data quality report complete")
    except Exception as e:
        print(f"⚠️  Data quality report failed: {e}")

    # ==========================================
    # Final Summary
    # ==========================================
    print("\n" + "=" * 60)
    print("  ✅ Phase 3 EDA Complete!")
    print("=" * 60)
    print(f"\n📁 All reports saved to: {output_dir}")
    print("\n📄 Generated Files:")
    
    if output_dir.exists():
        files = sorted(output_dir.iterdir())
        if files:
            for f in files:
                size_kb = f.stat().st_size / 1024
                print(f"  • {f.name:45s} ({size_kb:>8.1f} KB)")
        else:
            print("  ⚠️  No files generated")
    else:
        print("  ️  Output directory not found")

    print("\n" + "=" * 60)
    print("  Next Step: Phase 4 - Feature Engineering")
    print("=" * 60)


if __name__ == "__main__":
    main()