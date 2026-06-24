"""
Player Attribute Analyzer - Analyzes player attributes from FIFA datasets.
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path


class PlayerAttributeAnalyzer:
    """Analyzes player attributes from FIFA datasets."""

    def __init__(self, output_dir: str = "reports/eda"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def analyze(self, datasets: dict) -> dict:
        """Run player attribute analysis."""
        results = {}

        for ds_name in ["fifa23", "fifa22", "player_stats"]:
            if ds_name not in datasets:
                continue

            df = datasets[ds_name]
            results[ds_name] = self._analyze_dataset(ds_name, df)

        # Save combined report
        output_path = self.output_dir / "player_attribute_analysis.json"
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"📊 Player Attribute Analysis saved to: {output_path}")

        return results

    def _analyze_dataset(self, ds_name: str, df: pd.DataFrame) -> dict:
        """Analyze a single player dataset."""
        analysis = {
            "total_players": len(df),
            "total_columns": len(df.columns),
        }

        # Key attribute columns to look for
        attr_candidates = {
            "overall": ["overall", "overall_rating", "ovr"],
            "potential": ["potential"],
            "age": ["age"],
            "height": ["height_cm", "height"],
            "weight": ["weight_kg", "weight"],
            "pace": ["pace"],
            "shooting": ["shooting"],
            "passing": ["passing"],
            "dribbling": ["dribbling"],
            "defending": ["defending", "defense"],
            "physical": ["physical"],
            "value": ["value_eur", "value"],
            "wage": ["wage_eur", "wage"],
        }

        # Attribute statistics
        attr_stats = {}
        for attr_name, candidates in attr_candidates.items():
            col = self._find_col(df, candidates)
            if col:
                series = df[col].dropna()
                if len(series) > 0 and series.dtype in [np.float64, np.int64, float, int]:
                    attr_stats[attr_name] = {
                        "column": col,
                        "count": int(series.count()),
                        "mean": round(float(series.mean()), 2),
                        "median": round(float(series.median()), 2),
                        "std": round(float(series.std()), 2),
                        "min": round(float(series.min()), 2),
                        "max": round(float(series.max()), 2),
                        "q25": round(float(series.quantile(0.25)), 2),
                        "q75": round(float(series.quantile(0.75)), 2),
                    }

        analysis["attribute_statistics"] = attr_stats

        # Position distribution
        pos_col = self._find_col(df, ["player_positions", "position", "preferred_position"])
        if pos_col:
            pos_counts = df[pos_col].value_counts().head(20).to_dict()
            analysis["position_distribution"] = {str(k): int(v) for k, v in pos_counts.items()}

        # Preferred foot distribution
        foot_col = self._find_col(df, ["preferred_foot", "foot"])
        if foot_col:
            foot_counts = df[foot_col].value_counts().to_dict()
            analysis["preferred_foot_distribution"] = {str(k): int(v) for k, v in foot_counts.items()}

        # Top 10 players by overall
        overall_col = self._find_col(df, ["overall", "overall_rating", "ovr"])
        name_col = self._find_col(df, ["short_name", "long_name", "player_name", "name"])
        if overall_col and name_col:
            top_players = df.nlargest(10, overall_col)[[name_col, overall_col]]
            analysis["top_10_players"] = [
                {"name": str(row[name_col]), "overall": float(row[overall_col])}
                for _, row in top_players.iterrows()
            ]

        return analysis

    @staticmethod
    def _find_col(df: pd.DataFrame, candidates: list) -> str | None:
        """Find the first matching column name from candidates."""
        cols_lower = {c.lower().strip(): c for c in df.columns}
        for candidate in candidates:
            if candidate.lower().strip() in cols_lower:
                return cols_lower[candidate.lower().strip()]
        return None