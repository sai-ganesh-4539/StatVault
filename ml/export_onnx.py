import logging
import json
import re
from pathlib import Path
import joblib

import xgboost as xgb
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
from onnxmltools.convert import convert_xgboost
from onnxmltools.convert.common.data_types import FloatTensorType as XGBFloatTensorType

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

def get_feature_count(model) -> int:

    for attr in ["n_features_in_", "n_features_"]:

        if hasattr(model, attr):

            val = getattr(model, attr)

            if val is not None and val > 0:

                return val   
            
    if hasattr(model, "feature_names_in_") and model.feature_names_in_ is not None:

        return len(model.feature_names_in_)
    
    booster = None

    if isinstance(model, xgb.Booster):

        booster = model

    elif hasattr(model, "get_booster"):

        booster = model.get_booster()

    if booster:

        if hasattr(booster, "feature_names") and booster.feature_names:

            return len(booster.feature_names)
        
        if hasattr(booster, "num_features"):

            try:

                nf = booster.num_features()
                if nf and nf > 0: return nf

            except Exception: pass  

        try:

            config = json.loads(booster.save_config())

            def find_num_feature(d):

                if isinstance(d, dict):

                    for k, v in d.items():

                        if k in ("num_feature", "num_features", "num_columns"):

                            try: return int(v)
                            except: pass

                        res = find_num_feature(v)

                        if res: return res
                elif isinstance(d, list):

                    for item in d:

                        res = find_num_feature(item)
                        if res: return res

                return None
            
            nf = find_num_feature(config)
            if nf and nf > 0: return nf

        except Exception: pass

        try:

            dump = booster.get_dump()
            features = set()

            for tree in dump:

                matches = re.findall(r'\d+:\[([^<>=\]]+)', tree)
                features.update(matches)

            if features: return len(features)
        except Exception: pass

    logger.warning("Dynamic feature detection failed. Using roadmap default of 20 features for match model.")
    return 20 

def export_xgboost(pkl_path: Path, onnx_path: Path) -> None:

    logger.info(f"Loading XGBoost model: {pkl_path.name}")
    model = joblib.load(pkl_path)

    if isinstance(model, dict):

        logger.info("Loaded object is a dictionary. Extracting model...")

        if "model" in model:

            model = model["model"]

        elif "xgb_model" in model:

            model = model["xgb_model"]

        elif "booster" in model:

            model = model["booster"]

        else:

            for k, v in model.items():

                if hasattr(v, "get_booster") or isinstance(v, xgb.Booster):

                    model = v
                    break    

    n_features = get_feature_count(model)
    logger.info(f"Detected {n_features} features. Converting to ONNX...")
    booster = model if isinstance(model, xgb.Booster) else model.get_booster()

    if booster:

        booster.feature_names = [f"f{i}" for i in range(n_features)]

    initial_types = [("input", XGBFloatTensorType([None, n_features]))]
    onnx_model = convert_xgboost(model, initial_types=initial_types)

    with open(onnx_path, "wb") as f:

        f.write(onnx_model.SerializeToString())

    logger.info(f"Successfully exported: {onnx_path.name}")

def export_sklearn(pkl_path: Path, onnx_path: Path) -> None:

    logger.info(f"Loading Sklearn model: {pkl_path.name}")
    model = joblib.load(pkl_path)
    n_features = get_feature_count(model)
    logger.info(f"Detected {n_features} features. Converting to ONNX...")
    initial_types = [("input", FloatTensorType([None, n_features]))]

    onnx_model = convert_sklearn(
        model, 
        initial_types=initial_types,
        target_opset={'': 15, 'ai.onnx.ml': 3}
    )

    with open(onnx_path, "wb") as f:

        f.write(onnx_model.SerializeToString())

    logger.info(f"Successfully exported: {onnx_path.name}")

def main() -> None:

    base_dir = Path(__file__).parent.resolve()
    models_dir = base_dir / "models"

    if not models_dir.exists():

        logger.error(f"Models directory not found at: {models_dir}")
        return
    
    models_to_convert = [
        ("xgboost_match.pkl", "xgboost_match.onnx", "xgboost"),
        ("market_value.pkl", "market_value.onnx", "xgboost"),
        ("isolation_forest.pkl", "isolation_forest.onnx", "sklearn")
    ]

    success_count = 0

    for pkl_name, onnx_name, framework in models_to_convert:

        pkl_path = models_dir / pkl_name
        onnx_path = models_dir / onnx_name

        if not pkl_path.exists():

            logger.warning(f"Source model not found: {pkl_path}. Skipping.")
            continue

        try:

            if framework == "xgboost":

                export_xgboost(pkl_path, onnx_path)

            else:

                export_sklearn(pkl_path, onnx_path)

            success_count += 1

        except Exception as e:

            logger.error(f"Failed to convert {pkl_name}: {e}")

    logger.info(f"ONNX Export Complete. {success_count}/{len(models_to_convert)} models successfully converted.")
    
if __name__ == "__main__":
    main()