"""
Missing Value Analyzer - Generates missing value reports.
"""
import pandas as pd
from pathlib import Path


class MissingValueAnalyzer:
    """Analyzes missing values across all datasets."""

    def __init__(self, output_dir: str = "reports/eda"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def analyze(self, datasets: dict) -> pd.DataFrame:
        """Generate missing value report for all datasets."""
        records = []

        for ds_name, df in datasets.items():
            total_cells = df.shape[0] * df.shape[1]
            missing_cells = df.isnull().sum().sum()

            # Per-column missing values
            for col in df.columns:
                missing_count = df[col].isnull().sum()
                if missing_count > 0:
                    records.append({
                        "dataset": ds_name,
                        "column": col,
                        "dtype": str(df[col].dtype),
                        "missing_count": int(missing_count),
                        "missing_pct": round((missing_count / len(df)) * 100, 2),
                        "total_rows": len(df),
                    })

            # Dataset-level summary
            records.append({
                "dataset": ds_name,
                "column": "__DATASET_TOTAL__",
                "dtype": "-",
                "missing_count": int(missing_cells),
                "missing_pct": round((missing_cells / total_cells) * 100, 2) if total_cells > 0 else 0,
                "total_rows": len(df),
            })

        report = pd.DataFrame(records)
        output_path = self.output_dir / "missing_value_report.csv"
        report.to_csv(output_path, index=False)
        print(f"📊 Missing Value Report saved to: {output_path}")
        return report