import re
import pandas as pd
from datetime import date


def clean_premier_league(df):
    df = df.copy()
    reasons = [_check_pl_row(row) for _, row in df.iterrows()]
    df["reject_reason"] = reasons

    good = df[df["reject_reason"].isna()].drop(columns=["reject_reason"]).copy()
    bad  = df[df["reject_reason"].notna()].copy()

    good["home_goals"] = good["home_goals"].astype(int)
    good["away_goals"] = good["away_goals"].astype(int)

    # Normalise result to H/D/A just in case
    result_map = {"H": "H", "A": "A", "D": "D",
                  "home": "H", "away": "A", "draw": "D"}
    good["result"] = good["result"].map(result_map)

    return good.reset_index(drop=True), bad.reset_index(drop=True)


def _check_pl_row(row):
    for field in ["home_team", "away_team", "home_goals", "away_goals", "season"]:
        if pd.isna(row.get(field)):
            return f"null in required field: {field}"
    try:
        hg, ag = float(row["home_goals"]), float(row["away_goals"])
    except (ValueError, TypeError):
        return "goals not numeric"
    if hg < 0 or ag < 0:
        return f"negative goals: {hg}-{ag}"
    if not re.match(r"^\d{4}-\d{4}$", str(row.get("season", ""))):
        return f"bad season format: {row.get('season')!r}"
    return None



def clean_worldcup(df):
    df = df.dropna(subset=["Home Team Name", "Away Team Name",
                            "Home Team Goals", "Away Team Goals"]).copy()

    reasons = [_check_wc_row(row) for _, row in df.iterrows()]
    df["reject_reason"] = reasons

    good = df[df["reject_reason"].isna()].drop(columns=["reject_reason"]).copy()
    bad  = df[df["reject_reason"].notna()].copy()

    good["Home Team Goals"] = good["Home Team Goals"].astype(int)
    good["Away Team Goals"] = good["Away Team Goals"].astype(int)
    good["Year"]            = good["Year"].astype(int)
    good["Attendance"]      = pd.to_numeric(good["Attendance"], errors="coerce").fillna(0).astype(int)

    # Derive H/D/A result from goals
    good["result"] = good.apply(
        lambda r: "H" if r["Home Team Goals"] > r["Away Team Goals"]
                  else ("A" if r["Home Team Goals"] < r["Away Team Goals"] else "D"),
        axis=1,
    )
    return good.reset_index(drop=True), bad.reset_index(drop=True)


def _check_wc_row(row):
    try:
        hg, ag = float(row["Home Team Goals"]), float(row["Away Team Goals"])
    except (ValueError, TypeError):
        return "goals not numeric"
    if hg < 0 or ag < 0:
        return f"negative goals: {hg}-{ag}"
    if pd.isna(row.get("Year")):
        return "null Year"
    try:
        yr = int(float(row["Year"]))
        if yr < 1900 or yr > date.today().year:
            return f"Year out of range: {yr}"
    except (ValueError, TypeError):
        return f"Year not numeric: {row.get('Year')}"
    return None


def clean_fifa_players(df, edition):
    df = df.copy()
    reasons = [_check_player_row(row) for _, row in df.iterrows()]
    df["reject_reason"] = reasons

    good = df[df["reject_reason"].isna()].drop(columns=["reject_reason"]).copy()
    bad  = df[df["reject_reason"].notna()].copy()

    # Cast numeric columns
    for col in ["sofifa_id", "age", "height_cm", "weight_kg",
                "overall", "potential", "wage_eur", "value_eur"]:
        if col in good.columns:
            good[col] = pd.to_numeric(good[col], errors="coerce")

    attr_cols = ["pace", "shooting", "passing", "dribbling", "defending", "physic",
                 "gk_diving", "gk_handling", "gk_kicking",
                 "gk_reflexes", "gk_speed", "gk_positioning"]
    for col in attr_cols:
        if col in good.columns:
            good[col] = pd.to_numeric(good[col], errors="coerce").clip(0, 99)

    for col in ["overall", "potential"]:
        if col in good.columns:
            good[col] = good[col].clip(0, 99)

    # Remove duplicate players within this edition
    before = len(good)
    good = good.drop_duplicates(subset=["sofifa_id"], keep="first")
    removed = before - len(good)
    if removed:
        print(f"  [FIFA {edition}] Removed {removed} duplicate sofifa_id rows")

    good["fifa_edition"] = edition
    return good.reset_index(drop=True), bad.reset_index(drop=True)


def _check_player_row(row):
    if pd.isna(row.get("sofifa_id")):
        return "null sofifa_id"
    if pd.isna(row.get("short_name")) and pd.isna(row.get("long_name")):
        return "no player name"
    age = row.get("age")
    if not pd.isna(age):
        try:
            if not (15 <= float(age) <= 50):
                return f"age out of range: {age}"
        except (ValueError, TypeError):
            return f"age not numeric: {age}"
    return None


def clean_country_names(df):
    df = df.copy()
    df["reject_reason"] = df.apply(
        lambda r: "null current or former"
                  if pd.isna(r["current"]) or pd.isna(r["former"]) else None,
        axis=1,
    )
    good = df[df["reject_reason"].isna()].drop(columns=["reject_reason"]).copy()
    bad  = df[df["reject_reason"].notna()].copy()

    for col in ["start_date", "end_date"]:
        good[col] = pd.to_datetime(good[col], errors="coerce").dt.date

    return good.reset_index(drop=True), bad.reset_index(drop=True)