"""Scouting endpoints: anomaly detection + cluster archetypes."""
import json
from fastapi import APIRouter, HTTPException
from app.core.model_loader import ModelRegistry
from app.core.feature_encoder import encode_anomaly_features
from app.models.schemas import (
    AnomalyRequest, AnomalyResponse,
    ClusterListResponse, ClusterCentroid,
)
from app.config import settings

router = APIRouter(prefix="/scout", tags=["scouting"])


@router.post("/anomaly", response_model=AnomalyResponse)
async def detect_anomaly(req: AnomalyRequest) -> AnomalyResponse:
    """Detect anomalous player performance."""
    try:
        sess = ModelRegistry.get_isolation_forest()
        features = encode_anomaly_features(req.model_dump())
        outputs = sess.run(None, {"input": features})

        # Debug: print output shapes (visible in uvicorn terminal)
        for i, out in enumerate(outputs):
            print(f"  [anomaly] output[{i}] shape={getattr(out, 'shape', 'N/A')}, value={out}")

        # IsolationForest ONNX exports typically have:
        #   output[0] = labels (0=inlier, 1=outlier) — shape (1,)
        #   output[1] = scores (negative = anomalous) — shape (1,1) or (1,)
        # But sklearn version differences make this fragile. Defensive parse:

        # Label
        label_raw = outputs[0]
        if hasattr(label_raw, 'flatten'):
            label = int(label_raw.flatten()[0])
        else:
            label = int(label_raw[0])

        # Score
        if len(outputs) >= 2:
            score_raw = outputs[1]
            if hasattr(score_raw, 'flatten'):
                score = float(score_raw.flatten()[0])
            else:
                score = float(score_raw[0])
        else:
            score = 0.0

        # sklearn convention: label=1 means inlier (normal), label=-1 means outlier (anomaly)
        # But ONNX may export as 0/1. Normalize both cases:
        is_anomaly = (label == -1) or (label == 1 and score < 0)

        return AnomalyResponse(
            is_anomaly=bool(is_anomaly),
            anomaly_score=score,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"anomaly detection failed: {e}")


@router.get("/clusters", response_model=ClusterListResponse)
async def list_clusters() -> ClusterListResponse:
    """Return the 8 player archetype clusters from cluster_profiles.json."""
    try:
        path = settings.cluster_profiles_path
        data = json.loads(path.read_text(encoding="utf-8"))
        clusters = []
        metrics = {}
        for key, value in data.items():
            if key == "metrics":
                metrics = value
                continue
            clusters.append(ClusterCentroid(
                cluster_name=key,
                cluster_id=value["cluster_id"],
                centroid_values=value["centroid_values"],
            ))
        return ClusterListResponse(clusters=clusters, metrics=metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to load clusters: {e}")