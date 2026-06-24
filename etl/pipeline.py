from load_csv import (
    load_country_names,
    load_premier_league,
    load_worldcup,
    load_fifa_players,
)

if __name__ == "__main__":
    print("=" * 50)
    print("StatVault ETL Pipeline Starting")
    print("=" * 50)

    load_country_names()
    load_premier_league()
    load_worldcup()
    load_fifa_players()

    print("\n" + "=" * 50)
    print("ETL Pipeline Complete ✓")
    print("=" * 50)