"""RAG service: keyword search over intelligence reports."""
import re
from pathlib import Path
from dataclasses import dataclass

REPORT_FILES = [
    "../Match_Prediction_Intelligence.md",
    "../Player_Clustering_Intelligence.md",
    "../Scouting_Intelligence_Dashboard.md",
    "../eda_report.md",
    "../All_Models_Report.md",
    "../Model_Metrcis_Report.md",
    "../Feature_Analysis_Report.md",
]


@dataclass
class RAGResult:
    content: str
    source: str
    score: float


def _chunk_text(text: str, max_chars: int = 500) -> list[str]:
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""
    for p in paragraphs:
        if len(current) + len(p) > max_chars and current:
            chunks.append(current.strip())
            current = p
        else:
            current += "\n\n" + p
    if current.strip():
        chunks.append(current.strip())
    return chunks


def _load_reports() -> list[dict]:
    docs = []
    for rel_path in REPORT_FILES:
        path = Path(rel_path)
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        source = path.stem
        chunks = _chunk_text(text, max_chars=800)
        for i, chunk in enumerate(chunks):
            docs.append({"content": chunk, "source": f"{source}#chunk{i}", "text_lower": chunk.lower()})
    return docs


_REPORT_DOCS: list[dict] | None = None


def _get_docs() -> list[dict]:
    global _REPORT_DOCS
    if _REPORT_DOCS is None:
        _REPORT_DOCS = _load_reports()
    return _REPORT_DOCS


def search(query: str, top_k: int = 3) -> list[RAGResult]:
    query_words = set(re.findall(r"\w+", query.lower()))
    if not query_words:
        return []
    docs = _get_docs()
    scored = []
    for doc in docs:
        doc_words = set(re.findall(r"\w+", doc["text_lower"]))
        overlap = query_words & doc_words
        if not overlap:
            continue
        score = len(overlap) / (len(query_words) + len(doc_words) - len(overlap))
        scored.append(RAGResult(content=doc["content"], source=doc["source"], score=score))
    scored.sort(key=lambda r: r.score, reverse=True)
    return scored[:top_k]


async def search_with_db(query: str, top_k: int = 3) -> list[RAGResult]:
    return search(query, top_k)