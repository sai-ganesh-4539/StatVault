"""
Outlier Detector - Detects outliers using IQR and Z-score methods.
"""
import numpy as np
import pandas as pd
from pathlib import Path


class OutlierDetector:
    """Detects outliers in numerical columns using IQR method."""

    def __init__(self, output_dir: str = "reports/eda"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def analyze(self, datasets: dict) -> pd.DataFrame:
        """Detect outliers in all numerical columns."""
        records = []

        for ds_name, df in datasets.items():
            numeric_cols = df.select_dtypes(include=[np.number]).columns

            for col in numeric_cols:
                series = df[col].dropna()
                if len(series) < 10:
                    continue

                q1 = series.quantile(0.25)
                q3 = series.quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr

                outliers = series[(series < lower_bound) | (series > upper_bound)]
                outlier_count = len(outliers)

                if outlier_count > 0:
                    records.append({
                        "dataset": ds_name,
                        "column": col,
                        "mean": round(series.mean(), 4),
                        "median": round(series.median(), 4),
                        "std": round(series.std(), 4),
                        "q1": round(q1, 4),
                        "q3": round(q3, 4),
                        "iqr": round(iqr, 4),
                        "lower_bound": round(lower_bound, 4),
                        "upper_bound": round(upper_bound, 4),
                        "outlier_count": outlier_count,
                        "outlier_pct": round((outlier_count / len(series)) * 100, 2),
                        "min_outlier": round(outliers.min(), 4) if len(outliers) > 0 else None,
                        "max_outlier": round(outliers.max(), 4) if len(outliers) > 0 else None,
                    })

        report = pd.DataFrame(records)
        output_path = self.output_dir / "outlier_report.csv"
        report.to_csv(output_path, index=False)
        print(f"📊 Outlier Report saved to: {output_path}")
        return report