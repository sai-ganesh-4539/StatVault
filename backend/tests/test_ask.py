"""Tests for /ask endpoint."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ask_sql_question(client: AsyncClient):
    resp = await client.post("/ask", json={"question": "Who are the top 5 scorers?"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["source"] in ("sql", "rag", "none")
    assert data["answer"] != ""


@pytest.mark.asyncio
async def test_ask_rag_question(client: AsyncClient):
    resp = await client.post("/ask", json={"question": "How does xG affect match outcomes?"})
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data


@pytest.mark.asyncio
async def test_ask_empty_question(client: AsyncClient):
    resp = await client.post("/ask", json={"question": ""})
    assert resp.status_code in (200, 400, 422)