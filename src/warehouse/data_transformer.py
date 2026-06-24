"""
Data Transformer Module
Transforms raw data into Star Schema (Facts + Dimensions).
Optimized for memory efficiency with large datasets.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class DataTransformer:
    """Transforms raw datasets into fact and dimension tables."""

    def __init__(self, datasets: Dict[str, pd.DataFrame]):
        self.datasets = datasets
        self.facts: Dict[str, pd.DataFrame] = {}
        self.dimensions: Dict[str, pd.DataFrame] = {}

    def build_dimensions(self):
        """Build all dimension tables."""
        logger.info("Building dimension tables...")

        self._build_dim_teams()
        self._build_dim_players()
        self._build_dim_competitions()
        self._build_dim_countries()
        self._build_dim_seasons()

        logger.info(f"Built {len(self.dimensions)} dimension tables.")

    def build_facts(self):
        """Build all fact tables."""
        logger.info("Building fact tables...")

        self._build_fact_matches()
        self._build_fact_players()
        self._build_fact_team_stats()
        self._build_fact_player_stats()

        logger.info(f"Built {len(self.facts)} fact tables.")

    def _build_dim_teams(self):
        """Extract unique teams from match data."""
        teams = set()
        team_cols = ["home_team", "away_team", "HomeTeam", "AwayTeam", "Home", "Away", "home", "away", "Team"]

        if "international" in self.datasets:
            df = self.datasets["international"]
            for col in team_cols:
                if col in df.columns:
                    teams.update(df[col].dropna().astype(str).str.strip().unique())

        if "club_matches" in self.datasets:
            df = self.datasets["club_matches"]
            for col in team_cols:
                if col in df.columns:
                    teams.update(df[col].dropna().astype(str).str.strip().unique())

        teams_list = sorted(list(teams))
        dim_teams = pd.DataFrame({
            "team_id": range(1, len(teams_list) + 1),
            "team_name": teams_list,
        })

        self.dimensions["dim_teams"] = dim_teams
        logger.info(f"  dim_teams: {dim_teams.shape}")

    def _build_dim_players(self):
        """Extract unique players from FIFA/player datasets."""
        players = []
        name_cols = ["short_name", "long_name", "Name", "player_name", "Player", "player"]

        for dataset_name in ["fifa22", "fifa23", "player_stats", "player_scores"]:
            if dataset_name in self.datasets:
                df = self.datasets[dataset_name]
                for col in name_cols:
                    if col in df.columns:
                        # Only extract the name column to save memory
                        player_df = df[[col]].drop_duplicates()
                        player_df.columns = ["player_name"]
                        players.append(player_df)
                        break 

        if players:
            all_players = pd.concat(players, ignore_index=True).drop_duplicates()
            all_players = all_players.dropna(subset=["player_name"])
            all_players["player_name"] = all_players["player_name"].astype(str).str.strip()
            all_players = all_players[all_players["player_name"] != ""]
            all_players = all_players.reset_index(drop=True)
            all_players["player_id"] = range(1, len(all_players) + 1)
            all_players = all_players[["player_id", "player_name"]]
            self.dimensions["dim_players"] = all_players
            logger.info(f"  dim_players: {all_players.shape}")
        else:
            self.dimensions["dim_players"] = pd.DataFrame(columns=["player_id", "player_name"])

    def _build_dim_competitions(self):
        """Extract unique competitions/tournaments."""
        competitions = set()
        # Added Div, Comp, country which are common in football-data.co.uk datasets
        comp_cols = ["tournament", "League", "league", "Competition", "competition", "Div", "Comp", "country"]

        if "international" in self.datasets:
            df = self.datasets["international"]
            for col in comp_cols:
                if col in df.columns:
                    competitions.update(df[col].dropna().astype(str).str.strip().unique())

        if "club_matches" in self.datasets:
            df = self.datasets["club_matches"]
            for col in comp_cols:
                if col in df.columns:
                    competitions.update(df[col].dropna().astype(str).str.strip().unique())

        comp_list = sorted(list(competitions))
        dim_competitions = pd.DataFrame({
            "competition_id": range(1, len(comp_list) + 1),
            "competition_name": comp_list,
        })

        self.dimensions["dim_competitions"] = dim_competitions
        logger.info(f"  dim_competitions: {dim_competitions.shape}")

    def _build_dim_countries(self):
        """Extract unique countries."""
        countries = set()
        country_cols = ["home_team", "away_team", "country", "country_full", "Country"]

        if "international" in self.datasets:
            df = self.datasets["international"]
            for col in country_cols:
                if col in df.columns:
                    countries.update(df[col].dropna().astype(str).str.strip().unique())

        if "fifa_rankings" in self.datasets:
            df = self.datasets["fifa_rankings"]
            for col in country_cols:
                if col in df.columns:
                    countries.update(df[col].dropna().astype(str).str.strip().unique())

        country_list = sorted(list(countries))
        dim_countries = pd.DataFrame({
            "country_id": range(1, len(country_list) + 1),
            "country_name": country_list,
        })

        self.dimensions["dim_countries"] = dim_countries
        logger.info(f"  dim_countries: {dim_countries.shape}")

    def _build_dim_seasons(self):
        """Extract unique seasons/years."""
        seasons = set()

        for dataset_name in self.datasets:
            df = self.datasets[dataset_name]
            for col in ["date", "Date", "Season", "season", "Year"]:
                if col in df.columns:
                    if "date" in col.lower():
                        try:
                            dates = pd.to_datetime(df[col], errors="coerce")
                            years = dates.dt.year.dropna().unique()
                            seasons.update(years.astype(int))
                        except Exception:
                            pass
                    else:
                        seasons.update(df[col].dropna().unique())

        season_list = sorted(list(seasons))
        dim_seasons = pd.DataFrame({
            "season_id": range(1, len(season_list) + 1),
            "season_name": season_list,
        })

        self.dimensions["dim_seasons"] = dim_seasons
        logger.info(f"  dim_seasons: {dim_seasons.shape}")

    def _build_fact_matches(self):
        """Build fact_matches from match data."""
        fact_rows = []
        
        dim_teams = self.dimensions["dim_teams"]
        team_map = dict(zip(dim_teams["team_name"], dim_teams["team_id"]))
        
        dim_comp = self.dimensions["dim_competitions"]
        comp_map = dict(zip(dim_comp["competition_name"], dim_comp["competition_id"]))

        # International matches
        if "international" in self.datasets:
            df = self.datasets["international"].copy()
            if all(col in df.columns for col in ["date", "home_team", "away_team", "home_score", "away_score"]):
                df["date"] = pd.to_datetime(df["date"], errors="coerce")
                df = df.dropna(subset=["date"])
                
                df["home_team"] = df["home_team"].astype(str).str.strip()
                df["away_team"] = df["away_team"].astype(str).str.strip()

                fact_df = pd.DataFrame({
                    "match_id": range(1, len(df) + 1),
                    "date": df["date"],
                    "home_team_id": df["home_team"].map(team_map),
                    "away_team_id": df["away_team"].map(team_map),
                    "home_score": pd.to_numeric(df["home_score"], errors="coerce").fillna(0).astype(int),
                    "away_score": pd.to_numeric(df["away_score"], errors="coerce").fillna(0).astype(int),
                    "competition_id": df["tournament"].map(comp_map) if "tournament" in df.columns else np.nan,
                    "is_neutral": df["neutral"] if "neutral" in df.columns else False,
                    "source": "international",
                })
                fact_rows.append(fact_df)

        # Club matches
        if "club_matches" in self.datasets:
            df = self.datasets["club_matches"].copy()
            
            # Expanded column name matching for football-data.co.uk format
            home_col = next((c for c in ["HomeTeam", "home_team", "Home", "home"] if c in df.columns), None)
            away_col = next((c for c in ["AwayTeam", "away_team", "Away", "away"] if c in df.columns), None)
            date_col = next((c for c in ["Date", "date"] if c in df.columns), None)
            fthg_col = next((c for c in ["FTHG", "home_score", "HG", "home_goals"] if c in df.columns), None)
            ftag_col = next((c for c in ["FTAG", "away_score", "AG", "away_goals"] if c in df.columns), None)
            league_col = next((c for c in ["League", "league", "Div", "competition", "Comp", "country"] if c in df.columns), None)

            if home_col and away_col and date_col:
                df["date"] = pd.to_datetime(df[date_col], errors="coerce")
                df = df.dropna(subset=["date"])
                
                df[home_col] = df[home_col].astype(str).str.strip()
                df[away_col] = df[away_col].astype(str).str.strip()

                offset = len(fact_rows[0]) if fact_rows else 0

                fact_df = pd.DataFrame({
                    "match_id": range(offset + 1, offset + len(df) + 1),
                    "date": df["date"],
                    "home_team_id": df[home_col].map(team_map),
                    "away_team_id": df[away_col].map(team_map),
                    "home_score": pd.to_numeric(df[fthg_col], errors="coerce").fillna(0).astype(int) if fthg_col else 0,
                    "away_score": pd.to_numeric(df[ftag_col], errors="coerce").fillna(0).astype(int) if ftag_col else 0,
                    "competition_id": df[league_col].map(comp_map) if league_col else np.nan,
                    "is_neutral": False,
                    "source": "club",
                })
                fact_rows.append(fact_df)

        if fact_rows:
            fact_matches = pd.concat(fact_rows, ignore_index=True)
            self.facts["fact_matches"] = fact_matches
            logger.info(f"  fact_matches: {fact_matches.shape}")
        else:
            self.facts["fact_matches"] = pd.DataFrame()

    def _build_fact_players(self):
        """Build fact_players from FIFA datasets."""
        fact_rows = []
        name_cols = ["short_name", "long_name", "Name"]
        
        dim_players = self.dimensions["dim_players"]
        player_map = dict(zip(dim_players["player_name"], dim_players["player_id"]))

        for dataset_name in ["fifa22", "fifa23"]:
            if dataset_name in self.datasets:
                df_raw = self.datasets[dataset_name]
                name_col = next((c for c in name_cols if c in df_raw.columns), None)
                if not name_col:
                    continue

                # Memory optimization: only keep needed columns
                cols_to_keep = [name_col]
                for attr in ["overall", "potential", "pace", "shooting", "passing",
                             "dribbling", "defending", "physic", "age", "height_cm", "weight_kg"]:
                    col = next((c for c in [attr, attr.capitalize(), attr.upper()] if c in df_raw.columns), None)
                    if col:
                        cols_to_keep.append(col)
                
                df = df_raw[cols_to_keep].copy()
                df[name_col] = df[name_col].astype(str).str.strip()

                fact_df = pd.DataFrame({"player_id": df[name_col].map(player_map)})
                for col in cols_to_keep[1:]:
                    fact_df[col] = pd.to_numeric(df[col], errors="coerce")

                fact_df["source"] = dataset_name
                fact_df = fact_df.dropna(subset=["player_id"])
                fact_rows.append(fact_df)

        if fact_rows:
            fact_players = pd.concat(fact_rows, ignore_index=True)
            self.facts["fact_players"] = fact_players
            logger.info(f"  fact_players: {fact_players.shape}")
        else:
            self.facts["fact_players"] = pd.DataFrame()

    def _build_fact_team_stats(self):
        """Build fact_team_stats (aggregated team performance per season)."""
        if "fact_matches" not in self.facts or self.facts["fact_matches"].empty:
            self.facts["fact_team_stats"] = pd.DataFrame()
            return

        matches = self.facts["fact_matches"].copy()
        
        # Drop rows where team IDs are missing
        matches = matches.dropna(subset=["home_team_id", "away_team_id"])
        matches["home_team_id"] = matches["home_team_id"].astype(int)
        matches["away_team_id"] = matches["away_team_id"].astype(int)
        
        matches["season"] = pd.to_datetime(matches["date"]).dt.year

        # Calculate match outcomes vectorized (much faster than loops)
        matches["home_win"] = (matches["home_score"] > matches["away_score"]).astype(int)
        matches["away_win"] = (matches["away_score"] > matches["home_score"]).astype(int)
        matches["draw"] = (matches["home_score"] == matches["away_score"]).astype(int)

        # Aggregate Home Stats
        home_agg = matches.groupby(["home_team_id", "season"]).agg(
            home_played=("match_id", "count"),
            home_wins=("home_win", "sum"),
            home_draws=("draw", "sum"),
            home_goals_for=("home_score", "sum"),
            home_goals_against=("away_score", "sum")
        ).reset_index()

        # Aggregate Away Stats
        away_agg = matches.groupby(["away_team_id", "season"]).agg(
            away_played=("match_id", "count"),
            away_wins=("away_win", "sum"),
            away_draws=("draw", "sum"),
            away_goals_for=("away_score", "sum"),
            away_goals_against=("home_score", "sum")
        ).reset_index().rename(columns={"away_team_id": "home_team_id"})

        # Combine home and away
        combined = pd.merge(home_agg, away_agg, on=["home_team_id", "season"], how="outer").fillna(0)
        
        for col in ["home_played", "away_played", "home_wins", "away_wins", "home_draws", "away_draws", 
                    "home_goals_for", "away_goals_for", "home_goals_against", "away_goals_against"]:
            combined[col] = combined[col].astype(int)

        combined["matches_played"] = combined["home_played"] + combined["away_played"]
        combined["wins"] = combined["home_wins"] + combined["away_wins"]
        combined["draws"] = combined["home_draws"] + combined["away_draws"]
        combined["losses"] = combined["matches_played"] - combined["wins"] - combined["draws"]
        combined["goals_for"] = combined["home_goals_for"] + combined["away_goals_for"]
        combined["goals_against"] = combined["home_goals_against"] + combined["away_goals_against"]
        combined["goal_difference"] = combined["goals_for"] - combined["goals_against"]
        combined["points"] = combined["wins"] * 3 + combined["draws"]

        fact_team_stats = combined[["home_team_id", "season", "matches_played", "wins", "draws", "losses", 
                                    "goals_for", "goals_against", "goal_difference", "points"]].rename(
                                        columns={"home_team_id": "team_id"})
        
        self.facts["fact_team_stats"] = fact_team_stats
        logger.info(f"  fact_team_stats: {fact_team_stats.shape}")

    def _build_fact_player_stats(self):
        """Build fact_player_stats from player stats datasets."""
        fact_rows = []
        name_cols = ["player_name", "Player", "Name", "player"]

        dim_players = self.dimensions["dim_players"]
        player_map = dict(zip(dim_players["player_name"], dim_players["player_id"]))

        for dataset_name in ["player_stats", "player_scores"]:
            if dataset_name in self.datasets:
                df_raw = self.datasets[dataset_name]
                name_col = next((c for c in name_cols if c in df_raw.columns), None)
                if not name_col:
                    continue

                # 🚨 MEMORY FIX: Only copy the columns we actually need to avoid OOM on 7M+ rows
                cols_to_keep = [name_col]
                numeric_cols = df_raw.select_dtypes(include=[np.number]).columns
                cols_to_keep.extend(numeric_cols[:15].tolist())
                
                df = df_raw[cols_to_keep].copy()
                df[name_col] = df[name_col].astype(str).str.strip()
                
                # Filter to only known players to reduce size and processing time
                df = df[df[name_col].isin(player_map.keys())]

                fact_df = pd.DataFrame({"player_id": df[name_col].map(player_map)})
                for col in cols_to_keep[1:]:
                    fact_df[col] = pd.to_numeric(df[col], errors="coerce")

                fact_df = fact_df.dropna(subset=["player_id"])
                fact_rows.append(fact_df)
                logger.info(f"  Processed {dataset_name} for fact_player_stats")
        
                # Club matches
        if "club_matches" in self.datasets:
            df = self.datasets["club_matches"].copy()
            
            # Expanded column name matching
            home_col = next((c for c in ["HomeTeam", "home_team", "Home", "home"] if c in df.columns), None)
            away_col = next((c for c in ["AwayTeam", "away_team", "Away", "away"] if c in df.columns), None)
            date_col = next((c for c in ["Date", "date"] if c in df.columns), None)
            fthg_col = next((c for c in ["FTHG", "home_score", "HG", "home_goals"] if c in df.columns), None)
            ftag_col = next((c for c in ["FTAG", "away_score", "AG", "away_goals"] if c in df.columns), None)
            league_col = next((c for c in ["League", "league", "Div", "competition", "Comp", "country"] if c in df.columns), None)

            if home_col and away_col and date_col:
                
                # ✅ FIX: Fill missing values from alternative column names 
                # (e.g., EloRatings uses 'Home', Matches uses 'HomeTeam')
                for alt in ["HomeTeam", "home_team", "Home", "home"]:
                    if alt in df.columns and alt != home_col:
                        df[home_col] = df[home_col].fillna(df[alt])
                for alt in ["AwayTeam", "away_team", "Away", "away"]:
                    if alt in df.columns and alt != away_col:
                        df[away_col] = df[away_col].fillna(df[alt])
                # ---------------------------------------------------------

                df["date"] = pd.to_datetime(df[date_col], errors="coerce")
                df = df.dropna(subset=["date"])
                
                df[home_col] = df[home_col].astype(str).str.strip()
                df[away_col] = df[away_col].astype(str).str.strip()

        if fact_rows:
            fact_player_stats = pd.concat(fact_rows, ignore_index=True)
            self.facts["fact_player_stats"] = fact_player_stats
            logger.info(f"  fact_player_stats: {fact_player_stats.shape}")
        else:
            self.facts["fact_player_stats"] = pd.DataFrame()

    def transform(self) -> Tuple[Dict[str, pd.DataFrame], Dict[str, pd.DataFrame]]:
        """Run full transformation pipeline."""
        self.build_dimensions()
        self.build_facts()
        return self.facts, self.dimensions