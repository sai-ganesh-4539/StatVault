import json
import logging
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = DATA_DIR / "reports"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)
MODEL_NAME = "all-MiniLM-L6-v2"
def load_json_data(filepath: Path, mock_data_func) -> list:
    if filepath.exists():
        logger.info(f"Loading data from {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    logger.warning(f"File {filepath.name} not found. Generating mock data for pipeline continuity.")
    mock_data = mock_data_func()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(mock_data, f, indent=4)
    return mock_data
def get_mock_player_profiles():
    return [
        {"id": "P1", "Name": "Lionel Messi", "Position": "Forward", "Strengths": "Dribbling, Passing", "Weaknesses": "Physicality", "Playing Style": "Playmaker"},
        {"id": "P2", "Name": "Cristiano Ronaldo", "Position": "Forward", "Strengths": "Shooting, Heading", "Weaknesses": "Pace", "Playing Style": "Finisher"}
    ]
def get_mock_scout_reports():
    return [
        {"id": "S1", "Cluster Reports": "Playmakers", "Performance Reports": "High creativity and passing accuracy."},
        {"id": "S2", "Cluster Reports": "Finishers", "Performance Reports": "Excellent positioning and shot conversion."}
    ]
def get_mock_match_reports():
    return [
        {"id": "M1", "Match Summaries": "2-1 win", "Narratives": "Comeback victory", "Insights": "Strong second half."},
        {"id": "M2", "Match Summaries": "0-0 draw", "Narratives": "Defensive stalemate", "Insights": "Lack of creativity."}
    ]
def format_player_text(profile: dict) -> str:
    return (
        f"Name: {profile.get('Name', 'Unknown')}. "
        f"Position: {profile.get('Position', 'Unknown')}. "
        f"Strengths: {profile.get('Strengths', 'None')}. "
        f"Weaknesses: {profile.get('Weaknesses', 'None')}. "
        f"Playing Style: {profile.get('Playing Style', 'Unknown')}."
    )
def format_report_text(report: dict, report_type: str) -> str:
    if report_type == "scout":
        return f"Cluster Report: {report.get('Cluster Reports', 'N/A')}. Performance Report: {report.get('Performance Reports', 'N/A')}."
    return f"Match Summary: {report.get('Match Summaries', 'N/A')}. Narrative: {report.get('Narratives', 'N/A')}. Insights: {report.get('Insights', 'N/A')}."
def generate_and_save_embeddings(model: SentenceTransformer, texts: list, ids: list, output_path: Path, metadata_path: Path):
    if not texts:
        logger.warning(f"No texts provided for {output_path.name}. Saving empty array.")
        np.save(output_path, np.array([]))
        return
    logger.info(f"Generating embeddings for {len(texts)} items using {model[0].auto_model.config.name_or_path}...")
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    np.save(output_path, embeddings)
    logger.info(f"Successfully saved embeddings to {output_path}")
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(ids, f)
    logger.info(f"Successfully saved metadata to {metadata_path}")
def main():
    logger.info("Initializing SentenceTransformer model...")
    model = SentenceTransformer(MODEL_NAME)
    player_data = load_json_data(REPORTS_DIR / "player_profiles.json", get_mock_player_profiles)
    player_texts = [format_player_text(p) for p in player_data]
    player_ids = [p.get("id", "") for p in player_data]
    generate_and_save_embeddings(
        model, player_texts, player_ids, 
        EMBEDDINGS_DIR / "player_embeddings.npy",
        EMBEDDINGS_DIR / "player_embeddings_metadata.json"
    )
    scout_data = load_json_data(REPORTS_DIR / "scout_reports.json", get_mock_scout_reports)
    match_data = load_json_data(REPORTS_DIR / "match_reports.json", get_mock_match_reports)
    all_reports = scout_data + match_data
    report_texts = [format_report_text(r, "scout" if r in scout_data else "match") for r in all_reports]
    report_ids = [r.get("id", "") for r in all_reports]
    generate_and_save_embeddings(
        model, report_texts, report_ids,
        EMBEDDINGS_DIR / "report_embeddings.npy",
        EMBEDDINGS_DIR / "report_embeddings_metadata.json"
    )
    logger.info("Phase 8: Embedding Generation completed successfully.")
if __name__ == "__main__":
    main()