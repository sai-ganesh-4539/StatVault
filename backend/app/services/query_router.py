"""Routes natural language questions to SQL or RAG."""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.rag_service import search_with_db, RAGResult
from dataclasses import dataclass


@dataclass
class AskResult:
    answer: str
    source: str
    data: list[dict] | None = None
    rag_results: list[RAGResult] | None = None


_SQL_PATTERNS = [
    {
        "keywords": {"top", "scorer", "scorers", "goals"},
        "sql": "SELECT p.short_name, ps.overall as rating FROM dim_players p JOIN fact_player_season_stats ps ON p.player_id=ps.player_id GROUP BY p.short_name, ps.overall ORDER BY rating DESC LIMIT 10",
        "display": "Top 10 players by overall rating",
    },
    {
        "keywords": {"top", "player", "players", "rating"},
        "sql": "SELECT p.short_name, ps.overall, ps.potential FROM dim_players p JOIN fact_player_season_stats ps ON p.player_id=ps.player_id ORDER BY ps.overall DESC LIMIT 10",
        "display": "Top 10 players by rating",
    },
    {
        "keywords": {"match", "matches", "total", "count"},
        "sql": "SELECT COUNT(*) as total_matches FROM fact_matches",
        "display": "Total matches in database",
    },
    {
        "keywords": {"team", "teams", "count"},
        "sql": "SELECT COUNT(*) as total_teams FROM dim_teams",
        "display": "Total teams in database",
    },
    {
        "keywords": {"player", "players", "count", "total"},
        "sql": "SELECT COUNT(*) as total_players FROM dim_players",
        "display": "Total players in database",
    },
    {
        "keywords": {"cluster", "clusters", "archetype"},
        "sql": "SELECT cluster_label, COUNT(*) as count FROM fact_player_season_stats WHERE cluster_label IS NOT NULL GROUP BY cluster_label ORDER BY count DESC",
        "display": "Player cluster distribution",
    },
    {
        "keywords": {"anomaly", "anomalies", "outlier"},
        "sql": "SELECT p.short_name, ps.anomaly_score FROM dim_players p JOIN fact_player_season_stats ps ON p.player_id=ps.player_id WHERE ps.anomaly_score IS NOT NULL ORDER BY ps.anomaly_score DESC LIMIT 10",
        "display": "Top 10 anomalous players",
    },
    {
        "keywords": {"expensive", "valuable", "market", "value", "transfer"},
        "sql": "SELECT p.short_name, ps.value_eur FROM dim_players p JOIN fact_player_season_stats ps ON p.player_id=ps.player_id WHERE ps.value_eur IS NOT NULL ORDER BY ps.value_eur DESC LIMIT 10",
        "display": "Top 10 most valuable players",
    },
    {
        "keywords": {"competition", "competitions", "league"},
        "sql": "SELECT name, competition_type FROM dim_competitions ORDER BY name",
        "display": "All competitions",
    },
        {
        "keywords": {"most", "valuable", "players", "expensive", "top"},
        "sql": "SELECT p.short_name, ps.value_eur FROM dim_players p JOIN fact_player_season_stats ps ON p.player_id=ps.player_id WHERE ps.value_eur IS NOT NULL ORDER BY ps.value_eur DESC LIMIT 10",
        "display": "Top 10 most valuable players",
    },
    {
        "keywords": {"highest", "rating", "best", "players", "overall"},
        "sql": "SELECT p.short_name, ps.overall, ps.potential FROM dim_players p JOIN fact_player_season_stats ps ON p.player_id=ps.player_id ORDER BY ps.overall DESC LIMIT 10",
        "display": "Top 10 best rated players",
    },
]


def _match_sql(query: str) -> dict | None:
    import re
    # Strip punctuation and split into words
    query_words = set(re.findall(r"\w+", query.lower()))
    best = None
    best_score = 0
    for pattern in _SQL_PATTERNS:
        overlap = query_words & pattern["keywords"]
        score = len(overlap) / len(pattern["keywords"])
        if score > best_score and score >= 0.2:  # lowered from 0.3
            best = pattern
            best_score = score
    return best


async def ask(question: str, db: AsyncSession) -> AskResult:
    pattern = _match_sql(question)
    if pattern:
        try:
            result = await db.execute(text(pattern["sql"]))
            rows = [dict(row._mapping) for row in result.fetchall()]
            return AskResult(answer=pattern["display"], source="sql", data=rows)
        except Exception:
            pass
    rag_results = await search_with_db(question, top_k=3)
    if rag_results:
        top = rag_results[0]
        return AskResult(answer=top.content[:500], source="rag", rag_results=rag_results)
    return AskResult(answer="I couldn't find relevant information.", source="none")