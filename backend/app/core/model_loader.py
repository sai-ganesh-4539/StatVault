"""Loads all 3 ONNX models at startup. Holds singleton sessions."""
from pathlib import Path
import onnxruntime as ort
from app.config import settings


class ModelRegistry:
    """Holds ONNX inference sessions. Loaded once at startup."""
    _xgboost_match: ort.InferenceSession | None = None
    _market_value: ort.InferenceSession | None = None
    _isolation_forest: ort.InferenceSession | None = None

    @classmethod
    def load_all(cls) -> dict[str, bool]:
        """Load all 3 ONNX models. Returns map of model_name -> loaded_bool."""
        return {
            "xgboost_match": cls._load(cls._xgboost_match, settings.xgboost_match_path, "xgboost_match"),
            "market_value": cls._load(cls._market_value, settings.market_value_path, "market_value"),
            "isolation_forest": cls._load(cls._isolation_forest, settings.isolation_forest_path, "isolation_forest"),
        }

    @classmethod
    def _load(cls, _placeholder: object, path: Path, name: str) -> bool:
        try:
            sess = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
            setattr(cls, f"_{name}", sess)
            print(f"  [model_loader] loaded {name} from {path}")
            return True
        except Exception as e:
            print(f"  [model_loader] FAILED to load {name}: {e}")
            return False

    @classmethod
    def get_xgboost_match(cls) -> ort.InferenceSession:
        if cls._xgboost_match is None:
            raise RuntimeError("xgboost_match not loaded")
        return cls._xgboost_match

    @classmethod
    def get_market_value(cls) -> ort.InferenceSession:
        if cls._market_value is None:
            raise RuntimeError("market_value not loaded")
        return cls._market_value

    @classmethod
    def get_isolation_forest(cls) -> ort.InferenceSession:
        if cls._isolation_forest is None:
            raise RuntimeError("isolation_forest not loaded")
        return cls._isolation_forest


def load_models_on_startup() -> dict[str, bool]:
    return ModelRegistry.load_all()