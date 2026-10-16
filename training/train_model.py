"""
training/train_model.py
──────────────────────────────────────────────────────────────────────────────
Mathematical Sequence Prediction System — Model Training Pipeline

Loads all 16 generated CSV datasets from dataset/, merges them, extracts
the 53-dimensional features, fits a Random Forest Classifier, evaluates
model accuracy, and serializes the model, label encoder, and optional scaler
into backend/models/sequence_model.pkl.
──────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import csv
import time
import joblib
import argparse
import logging
import traceback
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, f1_score

# Resolve paths
_HERE = Path(__file__).resolve().parent
_PROJECT_ROOT = _HERE.parent
_DATASET_DIR = _PROJECT_ROOT / "dataset"
_MODEL_DIR = _PROJECT_ROOT / "backend" / "models"
_MODEL_PATH = _MODEL_DIR / "sequence_model.pkl"

# Add backend directory to sys.path to allow importing utils
sys.path.insert(0, str(_PROJECT_ROOT / "backend"))

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("train_model")

# All 16 datasets and their corresponding target labels
DATASET_FILES = {
    "arithmetic.csv": "arithmetic",
    "geometric.csv": "geometric",
    "prime.csv": "prime",
    "even.csv": "even",
    "odd.csv": "odd",
    "square.csv": "square",
    "cube.csv": "cube",
    "triangular.csv": "triangular",
    "factorial.csv": "factorial",
    "powers_of_2.csv": "powers_of_2",
    "powers_of_3.csv": "powers_of_3",
    "polynomial.csv": "polynomial",
    "alternating.csv": "alternating",
    "increasing.csv": "increasing",
    "decreasing.csv": "decreasing",
    "custom_dataset.csv": "custom",
}


def load_and_merge_datasets(dataset_dir: Path) -> pd.DataFrame:
    """Load all 16 CSV files from dataset_dir and merge them into one DataFrame."""
    dfs = []
    logger.info("Loading datasets from %s ...", dataset_dir)
    
    for filename, label in DATASET_FILES.items():
        filepath = dataset_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(
                f"Required dataset file not found: {filepath.name}. "
                "Please run training/generate_dataset.py first."
            )
        
        df = pd.read_csv(filepath)
        # Verify the target column matches the expected label
        df["pattern_type"] = label
        dfs.append(df)
        logger.info("  Loaded %s (%d rows)", filename, len(df))

    merged_df = pd.concat(dfs, ignore_index=True)
    logger.info("Merged datasets: total of %d rows.", len(merged_df))
    return merged_df


def preprocess_and_feature_engineering(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Clean data, run feature engineering, and return features and labels."""
    from utils.feature_engineering import extract_features

    logger.info("Running feature engineering...")
    
    # Term columns are t_1 to t_8
    term_cols = [f"t_{i}" for i in range(1, 9)]
    
    X_list = []
    y_list = []
    
    # Process row by row to leverage the 53-dimensional feature extractor
    for _, row in df.iterrows():
        terms = [float(row[col]) for col in term_cols]
        # Extract features (returns a 2D array of shape 1x53)
        features = extract_features(terms)[0]
        
        X_list.append(features)
        y_list.append(row["pattern_type"])

    X = np.array(X_list, dtype=np.float64)
    y = np.array(y_list)

    # Simple feature names list for metadata tracking
    feature_names = [f"feat_{i}" for i in range(X.shape[1])]
    
    logger.info("Feature engineering complete. Extracted shape: %s", str(X.shape))
    return X, y, feature_names


def train_and_evaluate(
    X: np.ndarray,
    y: np.ndarray,
    model_version: str,
    output_path: Path
) -> None:
    """Train a Random Forest classifier, evaluate performance, and save the bundle."""
    
    # Encode target labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Train-test split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.20, random_state=42, stratify=y_encoded
    )
    
    # Train a standard scaler
    logger.info("Training feature scaler...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train classifier
    logger.info("Training Random Forest Classifier model...")
    clf = RandomForestClassifier(n_estimators=150, random_state=42, n_jobs=-1)
    
    start_time = time.perf_counter()
    clf.fit(X_train_scaled, y_train)
    duration = time.perf_counter() - start_time
    logger.info("Model fitting complete in %.2f seconds.", duration)
    
    # Evaluate model
    y_pred = clf.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="macro")
    
    logger.info("╔══════════════════════════════════════════════════════╗")
    logger.info("║   Evaluation Metrics                                 ║")
    logger.info("╚══════════════════════════════════════════════════════╝")
    logger.info("  Test Accuracy : %.4f", acc)
    logger.info("  Test Macro F1 : %.4f", f1)
    logger.info("\n" + classification_report(y_test, y_pred, target_names=le.classes_))
    
    # Save the bundle (Model + LabelEncoder + Scaler + Metadata)
    logger.info("Saving trained model bundle to %s ...", output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    bundle = {
        "model": clf,
        "label_encoder": le,
        "scaler": scaler,
        "version": model_version,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "dataset_size": len(X),
        "metrics": {
            "accuracy": float(acc),
            "f1_macro": float(f1)
        }
    }
    joblib.dump(bundle, output_path)
    logger.info("Model bundle successfully serialized.")
    
    # Attempt logging to sqlite if inside Flask db context
    try:
        from database.database import insert_model_log
        insert_model_log(
            model_name="sequence_model",
            model_version=model_version,
            file_path=str(output_path),
            dataset_size=len(X),
            accuracy=float(acc),
            f1_score=float(f1),
            training_duration_sec=duration,
            status="active"
        )
        logger.info("Model training log successfully written to DB.")
    except Exception:
        # Not inside Flask context or DB not initialized yet
        logger.debug("Database log skipped (not inside Flask context).")


def main() -> int:
    parser = argparse.ArgumentParser(description="Train sequence prediction classification model.")
    parser.add_argument("--dataset", type=Path, default=_DATASET_DIR, help="Path to dataset directory.")
    parser.add_argument("--output", type=Path, default=_MODEL_PATH, help="Path to save sequence_model.pkl.")
    parser.add_argument("--version", type=str, default="v1.0.0", help="Version tag of the model.")
    args = parser.parse_args()

    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║   SeqPredict — Model Trainer                         ║")
    print("╚══════════════════════════════════════════════════════╝")
    print(f"  Dataset directory : {args.dataset}")
    print(f"  Output path       : {args.output}")
    print(f"  Model version     : {args.version}")
    print()

    try:
        df = load_and_merge_datasets(args.dataset)
        X, y, _ = preprocess_and_feature_engineering(df)
        train_and_evaluate(X, y, args.version, args.output)
        
        print()
        print("╔══════════════════════════════════════════════════════╗")
        print("║   Training Completed Successfully ✓                  ║")
        print("╚══════════════════════════════════════════════════════╝")
        print()
        return 0
    except Exception as exc:
        logger.error("Model training aborted: %s\n%s", exc, traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())