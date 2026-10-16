"""
training/evaluate_model.py
──────────────────────────────────────────────────────────────────────────────
Mathematical Sequence Prediction System — ML Model Evaluation

Loads the pre-trained model bundle from backend/models/sequence_model.pkl,
extracts features from the generated datasets in dataset/, and computes
evaluation metrics (Accuracy, Precision, Recall, F1 Score, and Confusion Matrix).
──────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import joblib
import argparse
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

# Resolve paths
_HERE = Path(__file__).resolve().parent
_PROJECT_ROOT = _HERE.parent
_DATASET_DIR = _PROJECT_ROOT / "dataset"
_MODEL_PATH = _PROJECT_ROOT / "backend" / "models" / "sequence_model.pkl"

# Add backend directory to sys.path to allow importing utils
sys.path.insert(0, str(_PROJECT_ROOT / "backend"))

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("evaluate_model")

# All 16 datasets and their target labels
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


def load_model_bundle(model_path: Path) -> dict:
    """Load the model bundle from disk."""
    if not model_path.exists():
        raise FileNotFoundError(
            f"Trained model bundle not found at: {model_path.name}. "
            "Please run training/train_model.py first."
        )
    logger.info("Loading model bundle from %s ...", model_path.name)
    return joblib.load(model_path)


def load_features_and_labels(dataset_dir: Path) -> tuple[np.ndarray, np.ndarray]:
    """Load all 16 datasets, extract features, and return them with true labels."""
    from utils.feature_engineering import extract_features

    dfs = []
    logger.info("Loading evaluation datasets from %s ...", dataset_dir)
    for filename, label in DATASET_FILES.items():
        filepath = dataset_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Dataset file missing: {filepath.name}")
        df = pd.read_csv(filepath)
        df["pattern_type"] = label
        dfs.append(df)

    merged = pd.concat(dfs, ignore_index=True)
    logger.info("Loaded total of %d sequence rows.", len(merged))

    term_cols = [f"t_{i}" for i in range(1, 9)]
    X_list = []
    y_list = []

    for _, row in merged.iterrows():
        terms = [float(row[col]) for col in term_cols]
        X_list.append(extract_features(terms)[0])
        y_list.append(row["pattern_type"])

    return np.array(X_list, dtype=np.float64), np.array(y_list)


def evaluate_model(model_path: Path, dataset_dir: Path) -> None:
    # ── 1. Load bundle ──
    bundle = load_model_bundle(model_path)
    clf = bundle["model"]
    le = bundle["label_encoder"]
    scaler = bundle.get("scaler", None)
    version = bundle.get("version", "unknown")
    trained_at = bundle.get("trained_at", "unknown")

    # ── 2. Load dataset and extract features ──
    X, y_true_labels = load_features_and_labels(dataset_dir)

    # ── 3. Preprocess data ──
    # Transform labels using the loaded LabelEncoder
    y_true = le.transform(y_true_labels)

    # Apply scaling transformation if present
    if scaler is not None:
        X_scaled = scaler.transform(X)
    else:
        X_scaled = X

    # ── 4. Predict ──
    logger.info("Running model predictions...")
    y_pred = clf.predict(X_scaled)

    # ── 5. Evaluate metrics ──
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average="macro")
    rec = recall_score(y_true, y_pred, average="macro")
    f1 = f1_score(y_true, y_pred, average="macro")
    cm = confusion_matrix(y_true, y_pred)

    # ── 6. Display results ──
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║   SeqPredict — Model Evaluation Summary              ║")
    print("╚══════════════════════════════════════════════════════╝")
    print(f"  Model Version : {version}")
    print(f"  Trained At    : {trained_at}")
    print(f"  Test Samples  : {len(X):,}")
    print("  " + "─" * 50)
    print(f"  Accuracy      : {acc:.4f} ({acc*100:.2f}%)")
    print(f"  Precision     : {prec:.4f}")
    print(f"  Recall        : {rec:.4f}")
    print(f"  F1 Score      : {f1:.4f}")
    print("  " + "─" * 50)
    print()
    print("  Classification Report:")
    print(classification_report(y_true, y_pred, target_names=le.classes_))
    print()
    
    # Format and print the confusion matrix nicely
    print("  Confusion Matrix:")
    classes = le.classes_
    cm_df = pd.DataFrame(cm, index=classes, columns=classes)
    
    # Print the DataFrame header & rows formatted
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(cm_df)
    print()


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate a trained sequence prediction model.")
    parser.add_argument("--model", type=Path, default=_MODEL_PATH, help="Path to sequence_model.pkl.")
    parser.add_argument("--dataset", type=Path, default=_DATASET_DIR, help="Path to dataset directory.")
    args = parser.parse_args()

    try:
        evaluate_model(args.model, args.dataset)
        return 0
    except Exception as exc:
        logger.error("Evaluation aborted with error: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
