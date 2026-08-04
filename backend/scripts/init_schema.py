"""Load etl/schema.sql into the database."""
import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect("postgresql://statvault:statvault@localhost:5433/statvault")
    sql = open("../etl/schema.sql", encoding="utf-8").read()
    await conn.execute(sql)
    print("Schema loaded from etl/schema.sql")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())