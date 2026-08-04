"""Seed the database with demo data so /ask and data endpoints work immediately."""
import asyncio
import asyncpg


async def main():
    conn = await asyncpg.connect("postgresql://statvault:statvault@localhost:5433/statvault")
    print("Connected to DB, seeding demo data...")

    # Teams
    teams = [
        ("Manchester City", "club"), ("Liverpool", "club"), ("Arsenal", "club"),
        ("Chelsea", "club"), ("Manchester United", "club"), ("Tottenham", "club"),
        ("Real Madrid", "club"), ("Barcelona", "club"), ("Bayern Munich", "club"),
        ("PSG", "club"),
    ]
    for name, ttype in teams:
        await conn.execute(
            "INSERT INTO dim_teams (name, team_type) VALUES ($1, $2) ON CONFLICT (name) DO NOTHING",
            name, ttype,
        )
    print(f"  seeded {len(teams)} teams")

    # Competitions
    comps = [("Premier League", "league"), ("La Liga", "league"), ("Bundesliga", "league"), ("Champions League", "cup")]
    for name, ctype in comps:
        await conn.execute(
            "INSERT INTO dim_competitions (name, competition_type) VALUES ($1, $2) ON CONFLICT (name) DO NOTHING",
            name, ctype,
        )
    print(f"  seeded {len(comps)} competitions")

    # Players
    players = [
        (1, "Erling Haaland", "Erling Haaland", "Norway", "Left", "ST", 194, 88),
        (2, "Kevin De Bruyne", "Kevin De Bruyne", "Belgium", "Right", "CAM,CM", 181, 68),
        (3, "Mohamed Salah", "Mohamed Salah", "Egypt", "Left", "RW,RM", 175, 71),
        (4, "Bukayo Saka", "Bukayo Saka", "England", "Right", "RW,RM", 178, 70),
        (5, "Vinicius Jr", "Vinicius Jose", "Brazil", "Right", "LW,LS", 176, 73),
        (6, "Jude Bellingham", "Jude Bellingham", "England", "Right", "CAM,CM", 186, 75),
        (7, "Lamine Yamal", "Lamine Yamal", "Spain", "Left", "RW,RM", 180, 70),
        (8, "Kylian Mbappe", "Kylian Mbappe", "France", "Right", "ST,LW", 178, 73),
        (9, "Rodri", "Rodrigo Hernandez", "Spain", "Right", "CDM,CM", 191, 82),
        (10, "Florian Wirtz", "Florian Wirtz", "Germany", "Right", "CAM,CF", 176, 69),
    ]
    for sofifa, short, long, nation, foot, pos, h, w in players:
        await conn.execute(
            "INSERT INTO dim_players (sofifa_id, short_name, long_name, nationality, preferred_foot, player_positions, height_cm, weight_kg) VALUES ($1,$2,$3,$4,$5,$6,$7,$8) ON CONFLICT (sofifa_id) DO NOTHING",
            sofifa, short, long, nation, foot, pos, h, w,
        )
    print(f"  seeded {len(players)} players")

    # Player stats
    stats = [
        (1, 24, 91, 93, 89, 85, 80, 88, 42, 80, 200000000, 300000),
        (2, 33, 91, 91, 72, 86, 93, 88, 64, 78, 50000000, 400000),
        (3, 32, 87, 87, 90, 87, 80, 90, 42, 75, 50000000, 350000),
        (4, 23, 86, 91, 86, 76, 82, 88, 56, 72, 120000000, 200000),
        (5, 23, 90, 93, 95, 82, 80, 93, 30, 68, 180000000, 250000),
        (6, 21, 90, 94, 80, 82, 89, 88, 72, 82, 150000000, 350000),
        (7, 17, 86, 94, 93, 72, 82, 92, 34, 65, 150000000, 100000),
        (8, 26, 91, 91, 97, 90, 80, 92, 36, 78, 180000000, 500000),
        (9, 28, 91, 91, 62, 64, 86, 68, 86, 82, 100000000, 250000),
        (10, 21, 86, 92, 80, 82, 88, 88, 38, 62, 130000000, 150000),
    ]
    for pid, age, ovr, pot, pace, sht, pas, dri, dfn, phy, val, wage in stats:
        await conn.execute(
            "INSERT INTO fact_player_season_stats (player_id, fifa_edition, age, overall, potential, pace, shooting, passing, dribbling, defending, physic, value_eur, wage_eur) VALUES ($1,25,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12) ON CONFLICT DO NOTHING",
            pid, age, ovr, pot, pace, sht, pas, dri, dfn, phy, val, wage,
        )
    print(f"  seeded {len(stats)} player stats")

    # Demo matches
    demo_matches = [
        (1, 1, 2, "H", 3, 1), (1, 1, 3, "H", 2, 0), (1, 1, 4, "D", 1, 1),
        (1, 2, 3, "A", 0, 2), (1, 2, 5, "H", 2, 1), (1, 3, 4, "H", 3, 2),
        (1, 7, 8, "D", 1, 1), (1, 8, 5, "H", 3, 1), (4, 7, 8, "A", 1, 2),
    ]
    for comp, home, away, result, hg, ag in demo_matches:
        await conn.execute(
            "INSERT INTO fact_matches (competition_id, home_team_id, away_team_id, result, home_goals, away_goals, source) VALUES ($1,$2,$3,$4,$5,$6,'demo')",
            comp, home, away, result, hg, ag,
        )
    print(f"  seeded {len(demo_matches)} demo matches")

    await conn.close()
    print("Done! Database seeded with demo data.")


if __name__ == "__main__":
    asyncio.run(main())