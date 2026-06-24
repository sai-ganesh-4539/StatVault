"""
Correlation Analyzer - Generates correlation matrices.
"""
import numpy as np
import pandas as pd
from pathlib import Path


class CorrelationAnalyzer:
    """Generates correlation matrices for numerical features."""

    def __init__(self, output_dir: str = "reports/eda"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def analyze(self, datasets: dict) -> dict:
        """Generate correlation matrices for all datasets."""
        results = {}

        for ds_name, df in datasets.items():
            numeric_df = df.select_dtypes(include=[np.number])
            if numeric_df.shape[1] < 2:
                continue

            # Pearson correlation
            corr_matrix = numeric_df.corr(method="pearson")

            # Save full matrix
            output_path = self.output_dir / f"correlation_matrix_{ds_name}.csv"
            corr_matrix.to_csv(output_path)
            print(f"📊 Correlation Matrix ({ds_name}) saved to: {output_path}")

            # Find strong correlations
            strong_corrs = self._find_strong_correlations(corr_matrix)
            results[ds_name] = {
                "matrix_shape": corr_matrix.shape,
                "strong_correlations": strong_corrs,
            }

        # Save summary
        summary_path = self.output_dir / "correlation_matrix.csv"
        summary_records = []
        for ds_name, info in results.items():
            for corr in info["strong_correlations"]:
                summary_records.append({
                    "dataset": ds_name,
                    "feature_1": corr["feature_1"],
                    "feature_2": corr["feature_2"],
                    "correlation": corr["correlation"],
                })

        summary_df = pd.DataFrame(summary_records)
        summary_df.to_csv(summary_path, index=False)
        print(f"📊 Correlation Summary saved to: {summary_path}")

        return results

    @staticmethod
    def _find_strong_correlations(corr_matrix: pd.DataFrame, threshold: float = 0.7) -> list:
        """Find feature pairs with strong correlation."""
        strong = []
        cols = corr_matrix.columns
        seen = set()

        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                val = corr_matrix.iloc[i, j]
                if abs(val) >= threshold:
                    pair = tuple(sorted([cols[i], cols[j]]))
                    if pair not in seen:
                        seen.add(pair)
                        strong.append({
                            "feature_1": pair[0],
                            "feature_2": pair[1],
                            "correlation": round(val, 4),
                        })

        return sorted(strong, key=lambda x: abs(x["correlation"]), reverse=True)