"""
Distribution Analyzer - Team, Goal, and Ranking distributions.
"""
import numpy as np
import pandas as pd
from pathlib import Path


class DistributionAnalyzer:
    """Analyzes distributions for teams, goals, and rankings."""

    def __init__(self, output_dir: str = "reports/eda"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def analyze(self, datasets: dict) -> dict:
        """Run all distribution analyses."""
        results = {}
        results["team_distribution"] = self._team_distribution(datasets)
        results["goal_distribution"] = self._goal_distribution(datasets)
        results["ranking_distribution"] = self._ranking_distribution(datasets)
        return results

    def _team_distribution(self, datasets: dict) -> pd.DataFrame:
        """Analyze team appearance distribution across matches."""
        records = []

        # From international matches
        if "international" in datasets:
            df = datasets["international"]
            home_col = self._find_col(df, ["home_team", "Home Team", "home"])
            away_col = self._find_col(df, ["away_team", "Away Team", "away"])

            if home_col and away_col:
                all_teams = pd.concat([df[home_col], df[away_col]])
                team_counts = all_teams.value_counts().reset_index()
                team_counts.columns = ["team", "match_count"]
                team_counts["source"] = "international"
                records.append(team_counts)

        # From club matches
        if "club_matches" in datasets:
            df = datasets["club_matches"]
            home_col = self._find_col(df, ["home_team", "Home Team", "home"])
            away_col = self._find_col(df, ["away_team", "Away Team", "away"])

            if home_col and away_col:
                all_teams = pd.concat([df[home_col], df[away_col]])
                team_counts = all_teams.value_counts().reset_index()
                team_counts.columns = ["team", "match_count"]
                team_counts["source"] = "club"
                records.append(team_counts)

        if records:
            report = pd.concat(records, ignore_index=True)
        else:
            report = pd.DataFrame(columns=["team", "match_count", "source"])

        output_path = self.output_dir / "team_distribution.csv"
        report.to_csv(output_path, index=False)
        print(f"📊 Team Distribution saved to: {output_path}")
        return report

    def _goal_distribution(self, datasets: dict) -> pd.DataFrame:
        """Analyze goal scoring distributions."""
        records = []

        for ds_name in ["international", "club_matches"]:
            if ds_name not in datasets:
                continue
            df = datasets[ds_name]

            home_goal_col = self._find_col(df, ["home_score", "Home Score", "home_goals", "FTHG"])
            away_goal_col = self._find_col(df, ["away_score", "Away Score", "away_goals", "FTAG"])

            if home_goal_col and away_goal_col:
                df = df.copy()
                df["total_goals"] = df[home_goal_col].fillna(0) + df[away_goal_col].fillna(0)
                df["goal_diff"] = abs(df[home_goal_col].fillna(0) - df[away_goal_col].fillna(0))

                goal_stats = {
                    "source": ds_name,
                    "total_matches": len(df),
                    "avg_home_goals": round(df[home_goal_col].mean(), 2),
                    "avg_away_goals": round(df[away_goal_col].mean(), 2),
                    "avg_total_goals": round(df["total_goals"].mean(), 2),
                    "median_total_goals": round(df["total_goals"].median(), 2),
                    "max_total_goals": int(df["total_goals"].max()),
                    "min_total_goals": int(df["total_goals"].min()),
                    "avg_goal_diff": round(df["goal_diff"].mean(), 2),
                    "zero_zero_pct": round((df["total_goals"] == 0).mean() * 100, 2),
                    "over_2_5_pct": round((df["total_goals"] > 2.5).mean() * 100, 2),
                    "over_3_5_pct": round((df["total_goals"] > 3.5).mean() * 100, 2),
                }

                # Goal frequency distribution
                goal_freq = df["total_goals"].value_counts().sort_index()
                for goals, count in goal_freq.items():
                    records.append({
                        **goal_stats,
                        "total_goals_bucket": int(goals),
                        "frequency": int(count),
                        "frequency_pct": round((count / len(df)) * 100, 2),
                    })

        report = pd.DataFrame(records)
        output_path = self.output_dir / "goal_distribution.csv"
        report.to_csv(output_path, index=False)
        print(f"📊 Goal Distribution saved to: {output_path}")
        return report

    def _ranking_distribution(self, datasets: dict) -> pd.DataFrame:
        """Analyze FIFA ranking distributions."""
        if "fifa_rankings" not in datasets:
            report = pd.DataFrame()
            output_path = self.output_dir / "ranking_distribution.csv"
            report.to_csv(output_path, index=False)
            return report

        df = datasets["fifa_rankings"]
        rank_col = self._find_col(df, ["rank", "Rank", "ranking", "total_points"])
        country_col = self._find_col(df, ["country_full", "Country", "country", "team"])

        if not rank_col:
            report = pd.DataFrame()
        else:
            report = df[[country_col, rank_col]].dropna() if country_col else df[[rank_col]].dropna()
            report.columns = ["country", "rank"] if country_col else ["rank"]

            if "country" in report.columns:
                # Latest rank per country
                report = report.groupby("country")["rank"].mean().reset_index()
                report = report.sort_values("rank")

        output_path = self.output_dir / "ranking_distribution.csv"
        report.to_csv(output_path, index=False)
        print(f"📊 Ranking Distribution saved to: {output_path}")
        return report

    @staticmethod
    def _find_col(df: pd.DataFrame, candidates: list) -> str | None:
        """Find the first matching column name from candidates."""
        cols_lower = {c.lower().strip(): c for c in df.columns}
        for candidate in candidates:
            if candidate.lower().strip() in cols_lower:
                return cols_lower[candidate.lower().strip()]
        return None