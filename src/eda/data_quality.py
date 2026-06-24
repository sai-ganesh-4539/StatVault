"""
Data Quality Reporter - Generates comprehensive data quality reports.
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path


class DataQualityReporter:
    """Generates comprehensive data quality reports."""

    def __init__(self, output_dir: str = "reports/eda"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def analyze(self, datasets: dict) -> dict:
        """Generate data quality report for all datasets."""
        report = {"datasets": {}, "summary": {}}

        total_rows = 0
        total_columns = 0
        total_missing = 0
        total_duplicates = 0

        for ds_name, df in datasets.items():
            ds_report = self._analyze_dataset(df)
            report["datasets"][ds_name] = ds_report

            total_rows += ds_report["rows"]
            total_columns += ds_report["columns"]
            total_missing += ds_report["total_missing_cells"]
            total_duplicates += ds_report["duplicate_rows"]

        report["summary"] = {
            "total_datasets": len(datasets),
            "total_rows": total_rows,
            "total_columns": total_columns,
            "total_missing_cells": total_missing,
            "total_duplicates": total_duplicates,
            "overall_missing_pct": round(
                (total_missing / (total_rows * total_columns)) * 100, 2
            ) if (total_rows * total_columns) > 0 else 0,
        }

        # Save report
        output_path = self.output_dir / "data_quality_report.json"
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"📊 Data Quality Report saved to: {output_path}")

        return report

    def _analyze_dataset(self, df: pd.DataFrame) -> dict:
        """Analyze quality of a single dataset."""
        report = {
            "rows": len(df),
            "columns": len(df.columns),
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
        }

        # Missing values
        missing_per_col = df.isnull().sum()
        total_missing = int(missing_per_col.sum())
        report["total_missing_cells"] = total_missing
        report["missing_pct"] = round(
            (total_missing / (len(df) * len(df.columns))) * 100, 2
        ) if (len(df) * len(df.columns)) > 0 else 0

        # Columns with > 50% missing
        high_missing_cols = missing_per_col[missing_per_col > len(df) * 0.5].index.tolist()
        report["high_missing_columns"] = high_missing_cols

        # Duplicates
        dup_count = int(df.duplicated().sum())
        report["duplicate_rows"] = dup_count
        report["duplicate_pct"] = round((dup_count / len(df)) * 100, 2) if len(df) > 0 else 0

        # Data types
        dtype_counts = df.dtypes.value_counts().to_dict()
        report["dtype_distribution"] = {str(k): int(v) for k, v in dtype_counts.items()}

        # Constant columns (only one unique value)
        constant_cols = [col for col in df.columns if df[col].nunique() <= 1]
        report["constant_columns"] = constant_cols

        # High cardinality columns
        high_card_cols = []
        for col in df.select_dtypes(include=["object", "category"]).columns:
            nunique = df[col].nunique()
            if nunique > len(df) * 0.5:
                high_card_cols.append({
                    "column": col,
                    "unique_values": int(nunique),
                })
        report["high_cardinality_columns"] = high_card_cols

        # Numeric column stats
        numeric_stats = {}
        for col in df.select_dtypes(include=[np.number]).columns:
            series = df[col].dropna()
            if len(series) > 0:
                numeric_stats[col] = {
                    "mean": round(float(series.mean()), 4),
                    "std": round(float(series.std()), 4),
                    "min": round(float(series.min()), 4),
                    "max": round(float(series.max()), 4),
                    "zeros": int((series == 0).sum()),
                    "negatives": int((series < 0).sum()),
                }
        report["numeric_column_stats"] = numeric_stats

        return report