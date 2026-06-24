import pandas as pd
from sqlalchemy import create_engine, text
from transform import (
    clean_premier_league,
    clean_worldcup,
    clean_fifa_players,
    clean_country_names,
)
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = (
    f"postgresql+psycopg2://"
    f"{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
    f"/{os.getenv('DB_NAME')}"
)
engine = create_engine(DB_URL)

DATA_DIR = r"C:\Users\DELL\Desktop\statvault\data"

def log_run(source, fetched, loaded, rejected, status, error=None):
    """Write one row to etl_ingestion_log so every run is on record."""
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO etl_ingestion_log
                (source, records_fetched, records_loaded, records_rejected, status, error_message)
            VALUES
                (:source, :fetched, :loaded, :rejected, :status, :error)
        """), dict(source=source, fetched=fetched, loaded=loaded,
                   rejected=rejected, status=status, error=error))


def get_or_create_team(conn, name, team_type):

    row = conn.execute(
        text("SELECT team_id FROM dim_teams WHERE name = :name"), {"name": name}
    ).fetchone()
    if row:
        return row[0]
    result = conn.execute(
        text("INSERT INTO dim_teams (name, team_type) VALUES (:name, :type) RETURNING team_id"),
        {"name": name, "type": team_type}
    )
    return result.fetchone()[0]


def get_or_create_competition(conn, name, comp_type):
    row = conn.execute(
        text("SELECT competition_id FROM dim_competitions WHERE name = :name"), {"name": name}
    ).fetchone()
    if row:
        return row[0]
    result = conn.execute(
        text("INSERT INTO dim_competitions (name, competition_type) VALUES (:name, :type) RETURNING competition_id"),
        {"name": name, "type": comp_type}
    )
    return result.fetchone()[0]


def get_or_create_date(conn, season=None, year=None, month=None):

    row = conn.execute(
        text("SELECT date_id FROM dim_dates WHERE season = :season AND year IS NOT DISTINCT FROM :year"),
        {"season": season, "year": year}
    ).fetchone()
    if row:
        return row[0]
    result = conn.execute(
        text("""
            INSERT INTO dim_dates (season, year, month)
            VALUES (:season, :year, :month)
            RETURNING date_id
        """),
        {"season": season, "year": year, "month": month}
    )
    return result.fetchone()[0]


def load_premier_league():
    print("\n── Loading Premier League results ──")
    raw = pd.read_csv(f"{DATA_DIR}/results.csv")
    good, bad = clean_premier_league(raw)
    print(f"  Raw: {len(raw)} rows  |  Good: {len(good)}  |  Rejected: {len(bad)}")
    if len(bad):
        print("  Rejected samples:\n", bad[["home_team","away_team","reject_reason"]].head())

    loaded = 0
    try:
        with engine.begin() as conn:
            comp_id = get_or_create_competition(conn, "Premier League", "league")

            for _, row in good.iterrows():
                home_id = get_or_create_team(conn, row["home_team"], "club")
                away_id = get_or_create_team(conn, row["away_team"], "club")
                date_id = get_or_create_date(conn, season=row["season"])

                conn.execute(text("""
                    INSERT INTO fact_matches
                        (competition_id, home_team_id, away_team_id, date_id,
                         home_goals, away_goals, result, source)
                    VALUES
                        (:comp, :home, :away, :date,
                         :hg, :ag, :result, 'premier_league_csv')
                """), dict(comp=comp_id, home=home_id, away=away_id, date=date_id,
                           hg=row["home_goals"], ag=row["away_goals"], result=row["result"]))
                loaded += 1

        log_run("premier_league_csv", len(raw), loaded, len(bad), "success")
        print(f"  ✓ Loaded {loaded} matches")
    except Exception as e:
        log_run("premier_league_csv", len(raw), loaded, len(bad), "failed", str(e))
        print(f"  ✗ Error: {e}")
        raise


def load_worldcup():
    print("\n── Loading World Cup matches ──")
    raw = pd.read_csv(f"{DATA_DIR}/WorldCupMatches.csv")
    good, bad = clean_worldcup(raw)
    print(f"  Raw: {len(raw)} rows  |  Good: {len(good)}  |  Rejected: {len(bad)}")

    loaded = 0
    try:
        with engine.begin() as conn:
            comp_id = get_or_create_competition(conn, "FIFA World Cup", "tournament")

            for _, row in good.iterrows():
                home_id = get_or_create_team(conn, row["Home Team Name"], "national")
                away_id = get_or_create_team(conn, row["Away Team Name"], "national")
                date_id = get_or_create_date(conn, year=int(row["Year"]))

                
                ht_home = int(row["Half-time Home Goals"]) if pd.notna(row.get("Half-time Home Goals")) else None
                ht_away = int(row["Half-time Away Goals"]) if pd.notna(row.get("Half-time Away Goals")) else None

                conn.execute(text("""
                    INSERT INTO fact_matches
                        (competition_id, home_team_id, away_team_id, date_id,
                         home_goals, away_goals, result,
                         stage, stadium, city, attendance,
                         ht_home_goals, ht_away_goals, source)
                    VALUES
                        (:comp, :home, :away, :date,
                         :hg, :ag, :result,
                         :stage, :stadium, :city, :att,
                         :ht_hg, :ht_ag, 'worldcup_csv')
                """), dict(comp=comp_id, home=home_id, away=away_id, date=date_id,
                           hg=row["Home Team Goals"], ag=row["Away Team Goals"],
                           result=row["result"],
                           stage=row.get("Stage"), stadium=row.get("Stadium"),
                           city=row.get("City"), att=int(row["Attendance"]),
                           ht_hg=ht_home, ht_ag=ht_away))
                loaded += 1

        log_run("worldcup_csv", len(raw), loaded, len(bad), "success")
        print(f"  ✓ Loaded {loaded} matches")
    except Exception as e:
        log_run("worldcup_csv", len(raw), loaded, len(bad), "failed", str(e))
        print(f"  ✗ Error: {e}")
        raise


def load_fifa_players():
    print("\n── Loading FIFA Career Mode players ──")
    xlsx_path = f"{DATA_DIR}/Career Mode player datasets - FIFA 15-21.xlsx"
    sheets = {
        "FIFA 15": 15, "FIFA 16": 16, "FIFA 17": 17,
        "FIFA 18": 18, "FIFA 19": 19, "FIFA 20": 20, "FIFA 21": 21,
    }

    total_loaded = 0
    for sheet_name, edition in sheets.items():
        print(f"\n  Sheet: {sheet_name}")
        df = pd.read_excel(xlsx_path, sheet_name=sheet_name)
        good, bad = clean_fifa_players(df, edition)
        print(f"    Raw: {len(df)}  |  Good: {len(good)}  |  Rejected: {len(bad)}")

        loaded = 0
        try:
            with engine.begin() as conn:
                for _, row in good.iterrows():
                    sid = int(row["sofifa_id"])

                    conn.execute(text("""
                        INSERT INTO dim_players
                            (sofifa_id, short_name, long_name, nationality,
                             preferred_foot, player_positions, height_cm, weight_kg)
                        VALUES
                            (:sid, :sname, :lname, :nat, :foot, :pos, :h, :w)
                        ON CONFLICT (sofifa_id) DO UPDATE SET
                            short_name  = EXCLUDED.short_name,
                            nationality = EXCLUDED.nationality
                    """), dict(
                        sid=sid,
                        sname=row.get("short_name"),
                        lname=row.get("long_name"),
                        nat=row.get("nationality"),
                        foot=row.get("preferred_foot"),
                        pos=row.get("player_positions"),
                        h=_int(row.get("height_cm")),
                        w=_int(row.get("weight_kg")),
                    ))

                    player_id = conn.execute(
                        text("SELECT player_id FROM dim_players WHERE sofifa_id = :sid"),
                        {"sid": sid}
                    ).fetchone()[0]

                    conn.execute(text("""
                        INSERT INTO fact_player_season_stats
                            (player_id, fifa_edition, club_name, league_name,
                             overall, potential, value_eur, wage_eur, age,
                             pace, shooting, passing, dribbling, defending, physic,
                             gk_diving, gk_handling, gk_kicking,
                             gk_reflexes, gk_speed, gk_positioning)
                        VALUES
                            (:pid, :edition, :club, :league,
                             :overall, :potential, :value, :wage, :age,
                             :pace, :shooting, :passing, :dribbling, :defending, :physic,
                             :gkd, :gkh, :gkk, :gkr, :gks, :gkp)
                        ON CONFLICT (player_id, fifa_edition) DO NOTHING
                    """), dict(
                        pid=player_id, edition=edition,
                        club=row.get("club_name"), league=row.get("league_name"),
                        overall=_int(row.get("overall")), potential=_int(row.get("potential")),
                        value=_int(row.get("value_eur")), wage=_int(row.get("wage_eur")),
                        age=_int(row.get("age")),
                        pace=_int(row.get("pace")), shooting=_int(row.get("shooting")),
                        passing=_int(row.get("passing")), dribbling=_int(row.get("dribbling")),
                        defending=_int(row.get("defending")), physic=_int(row.get("physic")),
                        gkd=_int(row.get("gk_diving")), gkh=_int(row.get("gk_handling")),
                        gkk=_int(row.get("gk_kicking")), gkr=_int(row.get("gk_reflexes")),
                        gks=_int(row.get("gk_speed")), gkp=_int(row.get("gk_positioning")),
                    ))
                    loaded += 1

            log_run(f"fifa_{edition}_csv", len(df), loaded, len(bad), "success")
            total_loaded += loaded
            print(f"    ✓ Loaded {loaded} players")
        except Exception as e:
            log_run(f"fifa_{edition}_csv", len(df), loaded, len(bad), "failed", str(e))
            print(f"    ✗ Error: {e}")
            raise

    print(f"\n  ✓ Total FIFA players loaded across all editions: {total_loaded}")


def load_country_names():
    print("\n── Loading country name mappings ──")
    raw = pd.read_csv(f"{DATA_DIR}/former_names.csv")
    good, bad = clean_country_names(raw)
    print(f"  Raw: {len(raw)}  |  Good: {len(good)}  |  Rejected: {len(bad)}")

    try:
        with engine.begin() as conn:
            for _, row in good.iterrows():
                conn.execute(text("""
                    INSERT INTO dim_country_names (current, former, valid_from, valid_to)
                    VALUES (:current, :former, :from_, :to_)
                    ON CONFLICT DO NOTHING
                """), dict(current=row["current"], former=row["former"],
                           from_=row.get("start_date"), to_=row.get("end_date")))
        log_run("former_names_csv", len(raw), len(good), len(bad), "success")
        print(f"  ✓ Loaded {len(good)} country name mappings")
    except Exception as e:
        log_run("former_names_csv", len(raw), 0, len(bad), "failed", str(e))
        print(f"  ✗ Error: {e}")
        raise


def _int(val):
    try:
        if pd.isna(val):
            return None
        return int(val)
    except (TypeError, ValueError):
        return None