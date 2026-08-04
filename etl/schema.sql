CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS dim_teams (
    team_id     SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    team_type   VARCHAR(20)  NOT NULL  
);

CREATE TABLE IF NOT EXISTS dim_competitions (
    competition_id   SERIAL PRIMARY KEY,
    name             VARCHAR(100) NOT NULL UNIQUE,
    competition_type VARCHAR(20)  NOT NULL 
);

CREATE TABLE IF NOT EXISTS dim_dates (
    date_id     SERIAL PRIMARY KEY,
    full_date   DATE    UNIQUE,
    season      VARCHAR(20),
    year        INTEGER,
    month       INTEGER,
    day_of_week INTEGER,
    is_weekend  BOOLEAN
);

CREATE TABLE IF NOT EXISTS dim_players (
    player_id        SERIAL PRIMARY KEY,
    sofifa_id        INTEGER     NOT NULL UNIQUE,
    short_name       VARCHAR(100),
    long_name        VARCHAR(200),
    nationality      VARCHAR(100),
    preferred_foot   VARCHAR(10),
    player_positions VARCHAR(50),
    height_cm        INTEGER,
    weight_kg        INTEGER
);

CREATE TABLE IF NOT EXISTS dim_country_names (
    id         SERIAL PRIMARY KEY,
    current    VARCHAR(100) NOT NULL,
    former     VARCHAR(100) NOT NULL,
    valid_from DATE,
    valid_to   DATE
);

CREATE TABLE IF NOT EXISTS dim_scouting_vectors (
    player_id  INTEGER PRIMARY KEY REFERENCES dim_players(player_id),
    embedding  vector(384)
);

-- FACT TABLES

CREATE TABLE IF NOT EXISTS fact_matches (
    match_id       SERIAL PRIMARY KEY,
    competition_id INTEGER NOT NULL REFERENCES dim_competitions(competition_id),
    home_team_id   INTEGER NOT NULL REFERENCES dim_teams(team_id),
    away_team_id   INTEGER NOT NULL REFERENCES dim_teams(team_id),
    date_id        INTEGER REFERENCES dim_dates(date_id),
    home_goals     INTEGER NOT NULL,
    away_goals     INTEGER NOT NULL,
    result         CHAR(1) NOT NULL CHECK (result IN ('H','D','A')),
    stage          VARCHAR(50),
    stadium        VARCHAR(100),
    city           VARCHAR(100),
    attendance     INTEGER,
    ht_home_goals  INTEGER,
    ht_away_goals  INTEGER,
    source         VARCHAR(30) NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_player_season_stats (
    stat_id      SERIAL PRIMARY KEY,
    player_id    INTEGER NOT NULL REFERENCES dim_players(player_id),
    fifa_edition SMALLINT NOT NULL,
    club_name    VARCHAR(100),
    league_name  VARCHAR(100),
    overall      SMALLINT,
    potential    SMALLINT,
    value_eur    BIGINT,
    wage_eur     INTEGER,
    age          SMALLINT,
    pace         SMALLINT,
    shooting     SMALLINT,
    passing      SMALLINT,
    dribbling    SMALLINT,
    defending    SMALLINT,
    physic       SMALLINT,
    gk_diving    SMALLINT,
    gk_handling  SMALLINT,
    gk_kicking   SMALLINT,
    gk_reflexes  SMALLINT,
    gk_speed     SMALLINT,
    gk_positioning SMALLINT,
    cluster_label  VARCHAR(50),
    anomaly_score  FLOAT,
    UNIQUE (player_id, fifa_edition)
);


CREATE TABLE IF NOT EXISTS etl_ingestion_log (
    log_id           SERIAL PRIMARY KEY,
    source           VARCHAR(50) NOT NULL,
    records_fetched  INTEGER,
    records_loaded   INTEGER,
    records_rejected INTEGER,
    status           VARCHAR(20) NOT NULL CHECK (status IN ('success','failed','partial')),
    error_message    TEXT,
    run_timestamp    TIMESTAMPTZ NOT NULL DEFAULT now()
);



CREATE INDEX IF NOT EXISTS idx_teams_name          ON dim_teams(name);
CREATE INDEX IF NOT EXISTS idx_matches_date        ON fact_matches(date_id);
CREATE INDEX IF NOT EXISTS idx_matches_competition ON fact_matches(competition_id);
CREATE INDEX IF NOT EXISTS idx_matches_home_team   ON fact_matches(home_team_id);
CREATE INDEX IF NOT EXISTS idx_matches_away_team   ON fact_matches(away_team_id);
CREATE INDEX IF NOT EXISTS idx_stats_player        ON fact_player_season_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_stats_edition       ON fact_player_season_stats(fifa_edition);
CREATE INDEX IF NOT EXISTS idx_stats_overall       ON fact_player_season_stats(overall);
CREATE INDEX IF NOT EXISTS idx_scouting_vectors
    ON dim_scouting_vectors USING hnsw (embedding vector_cosine_ops);