import os
import glob
import json
import pickle
import joblib
from pathlib import Path
import numpy as np
import onnxruntime as ort

import xgboost as xgb
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder, OneHotEncoder
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
from onnxmltools import convert_xgboost
from onnxmltools.convert.common.data_types import FloatTensorType as OnnxFloatTensorType

# Helper
def get_n_features(model):
    if hasattr(model, "n_features_in_"):
        return model.n_features_in_
    if hasattr(model, "n_features_"):
        return model.n_features_
    if hasattr(model, "num_features"):
        return model.num_features()
    if isinstance(model, xgb.Booster):
        return model.num_features()
    if hasattr(model, "feature_importances_"):
        return len(model.feature_importances_)
    if isinstance(model, (StandardScaler, MinMaxScaler)):
        if hasattr(model, "scale_"):
            return len(model.scale_)
        if hasattr(model, "mean_"):
            return len(model.mean_)
    return None

# XGBoost Conversion
def convert_xgb_model(model, n_features, onnx_path):
    print(f"✅ Detected XGBoost model ({n_features} features)")
    booster = model.get_booster() if hasattr(model, "get_booster") else model
    try:
        booster.feature_types = None
    except Exception:
        pass
    booster.feature_names = [f"f{i}" for i in range(n_features)]
    initial_types = [("float_input", OnnxFloatTensorType([None, n_features]))]
    onnx_model = convert_xgboost(booster, initial_types=initial_types, target_opset=12)
    with open(onnx_path, "wb") as f:
        f.write(onnx_model.SerializeToString())

# Scikit-Learn Conversion
def convert_sklearn_model(model, n_features, onnx_path):
    initial_types = [("float_input", FloatTensorType([None, n_features]))]
    onnx_model = convert_sklearn(model, initial_types=initial_types, target_opset={"": 12, "ai.onnx.ml": 3})
    with open(onnx_path, "wb") as f:
        f.write(onnx_model.SerializeToString())
# ONNX Runtime Verification
def verify_onnx(onnx_path, n_features):
    try:
        sess = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
        dummy_input = {sess.get_inputs()[0].name: np.random.randn(1, n_features).astype(np.float32)}
        sess.run(None, dummy_input)
        print("   ONNX runtime verification: PASSED")
        return True
    except Exception as e:
        print(f"   ONNX runtime verification: FAILED -> {e}")
        return False

# Main Conversion
def convert_model_to_onnx(pkl_path, output_dir, registry):
    model_name = Path(pkl_path).stem
    onnx_path = os.path.join(output_dir, f"{model_name}.onnx")
    print(f"\n Processing: {model_name}.pkl ---")

    try:
        model = joblib.load(pkl_path)
    except Exception:
        with open(pkl_path, "rb") as f:
            model = pickle.load(f)

    if isinstance(model, (LabelEncoder, OneHotEncoder)):
        print(" Encoder detected. Skipping.")
        registry[model_name] = {"type": "encoder", "status": "skipped"}
        return

    if isinstance(model, (list, tuple, dict)):
        print("️ Raw data object. Skipping.")
        registry[model_name] = {"type": "lookup_data", "status": "skipped"}
        return

    n_features = get_n_features(model)
    if n_features is None:
        print(" Could not infer input features. Skipping.")
        registry[model_name] = {"type": "unknown", "status": "skipped"}
        return

    try:
        if isinstance(model, (xgb.XGBClassifier, xgb.XGBRegressor, xgb.Booster)):
            convert_xgb_model(model, n_features, onnx_path)
        elif isinstance(model, (StandardScaler, MinMaxScaler)):
            print(f" Detected Scaler ({n_features} features)")
            convert_sklearn_model(model, n_features, onnx_path)
        elif hasattr(model, "predict"):
            print(f" Detected Scikit-Learn model ({n_features} features)")
            convert_sklearn_model(model, n_features, onnx_path)
        else:
            print(" Unsupported object. Skipping.")
            registry[model_name] = {"type": "unsupported", "status": "skipped"}
            return

        if verify_onnx(onnx_path, n_features):
            print(f" Saved -> {onnx_path}")
            registry[model_name] = {
                "type": type(model).__name__,
                "status": "converted",
                "features": n_features,
                "onnx_path": onnx_path
            }
    except Exception as e:
        print(f" Conversion failed: {type(e).__name__} -> {e}")
        registry[model_name] = {"type": "error", "status": "failed", "error": str(e)}

# Main
def main():
    base_dir = Path(__file__).resolve().parent.parent
    models_dir = base_dir / "models"
    if not models_dir.exists():
        print("Models folder not found.")
        return

    pkl_files = sorted(glob.glob(str(models_dir / "*.pkl")))
    print(f"Found {len(pkl_files)} .pkl files.")

    registry = {}
    for pkl in pkl_files:
        convert_model_to_onnx(pkl, models_dir, registry)

    registry_path = models_dir / "onnx_model_registry.json"
    with open(registry_path, "w") as f:
        json.dump(registry, f, indent=2)
    print(f"\n Model registry saved to: {registry_path}")
    print("\n Finished.")

if __name__ == "__main__":
    main()