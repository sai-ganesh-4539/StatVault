"""Shared fixtures for StatVault test suite."""
import pytest
import pytest_asyncio
from unittest.mock import MagicMock
import numpy as np
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core import model_loader

# In-memory SQLite for fast tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_statvault.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


class FakeSession:
    """Mimics onnxruntime.InferenceSession with correct output shapes."""
    def run(self, output_names, inputs):
        feed = list(inputs.values())[0]
        # Match model: outputs[0] = labels [1], outputs[1] = probs [1, 3]
        if feed.shape[1] == 55:  # match prediction
            return [
                np.array([0]),           # label index (H)
                np.array([[0.5, 0.25, 0.25]])  # probabilities
            ]
        elif feed.shape[1] == 687:  # market value
            return [np.array([[50_000_000.0]])]  # 50M EUR
        else:  # anomaly (7 features)
            return [np.array([[-0.5]])]  # anomaly score


@pytest_asyncio.fixture
async def setup_db():
    # Patch model registry with fake sessions
    model_loader.ModelRegistry._xgboost_match = FakeSession()
    model_loader.ModelRegistry._market_value = FakeSession()
    model_loader.ModelRegistry._isolation_forest = FakeSession()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def client(setup_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac