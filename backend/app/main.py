"""StatVault FastAPI entrypoint."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.model_loader import load_models_on_startup
from app.core.database import engine, Base
from app.routers import health, predictions, scouting, ask, players, teams, matches


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("[startup] loading ONNX models...")
    loaded = load_models_on_startup()
    print(f"[startup] models loaded: {loaded}")
    print("[startup] StatVault API ready")
    yield
    # Shutdown
    await engine.dispose()
    print("[shutdown] bye")


app = FastAPI(
    title="StatVault API",
    description="Football Intelligence Platform — Predictions, Scouting, RAG, Live Data",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# All routers
app.include_router(health.router)
app.include_router(predictions.router)
app.include_router(scouting.router)
app.include_router(ask.router)
app.include_router(players.router)
app.include_router(teams.router)
app.include_router(matches.router)


@app.get("/")
async def root():
    return {
        "app": "StatVault API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "predictions": "/predict/match, /predict/market-value",
            "scouting": "/scout/anomaly, /scout/clusters",
            "ask": "/ask",
            "data": "/players, /teams, /matches",
            "live": "/matches/live",
        },
    }