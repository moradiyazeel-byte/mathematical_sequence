"""
training/test_model.py
──────────────────────────────────────────────────────────────────────────────
Mathematical Sequence Prediction System — Interactive ML Model Tester

Loads the trained Random Forest model bundle from backend/models/sequence_model.pkl,
evaluates a selection of representative mathematical sequence test cases,
and prints the predictions, classified sequence types, and confidence scores.
──────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import joblib
import argparse
from pathlib import Path

import numpy as np

# Resolve paths
_HERE = Path(__file__).resolve().parent
_PROJECT_ROOT = _HERE.parent
_MODEL_PATH = _PROJECT_ROOT / "backend" / "models" / "sequence_model.pkl"

# Add backend directory to sys.path to allow importing utils
sys.path.insert(0, str(_PROJECT_ROOT / "backend"))

# Logging setup
import logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("test_model")


# Representative test cases representing different mathematical categories
DEFAULT_TEST_CASES = [
    # Arithmetic
    [3.0, 7.0, 11.0, 15.0, 19.0],
    # Geometric
    [2.0, 6.0, 18.0, 54.0],
    # Square
    [4.0, 9.0, 16.0, 25.0],
    # Cube
    [8.0, 27.0, 64.0, 125.0],
    # Triangular
    [1.0, 3.0, 6.0, 10.0, 15.0],
    # Prime
    [2.0, 3.0, 5.0, 7.0, 11.0, 13.0],
    # Factorial
    [1.0, 2.0, 6.0, 24.0, 120.0],
    # Powers of 2
    [4.0, 8.0, 16.0, 32.0, 64.0],
    # Powers of 3
    [9.0, 27.0, 81.0, 243.0],
    # Even
    [12.0, 14.0, 16.0, 18.0, 20.0],
    # Odd
    [23.0, 25.0, 27.0, 29.0, 31.0],
    # Alternating
    [5.0, -5.0, 5.0, -5.0, 5.0],
    # Polynomial (Quadratic: n^2 - n + 2)
    [2.0, 4.0, 8.0, 14.0, 22.0],
]


def test_sequences(model_path: Path, input_seq: list[float] | None) -> None:
    # ── 1. Load model bundle ──
    if not model_path.exists():
        raise FileNotFoundError(
            f"Trained model bundle not found: {model_path.name}. "
            "Please run training/train_model.py first."
        )
    
    bundle = joblib.load(model_path)
    clf = bundle["model"]
    le = bundle["label_encoder"]
    scaler = bundle.get("scaler", None)
    version = bundle.get("version", "unknown")

    # Import utilities from backend
    from utils.feature_engineering import extract_features
    from services.predictor import _compute_next_term

    # Determine sequences to evaluate
    if input_seq:
        sequences = [input_seq]
    else:
        sequences = DEFAULT_TEST_CASES

    print()
    print("╔═════════════════════════════════════════════════════════════════════════════╗")
    print(f"║   SeqPredict — Model Tester (Version: {version:<8})                            ║")
    print("╚═════════════════════════════════════════════════════════════════════════════╝")
    print(f"  {'Input Sequence':<35}  {'Predicted Next':<14}  {'Family Type':<15}  {'Conf':<6}")
    print("  " + "─" * 75)

    for seq in sequences:
        # Extract features (shape: 1x53)
        features = extract_features(seq)

        # Apply scaling if present
        if scaler is not None:
            features_scaled = scaler.transform(features)
        else:
            features_scaled = features

        # Predict class probabilities
        probas = clf.predict_proba(features_scaled)[0]
        top_idx = np.argmax(probas)
        top_class = le.inverse_transform([top_idx])[0]
        top_prob = float(probas[top_idx])

        # Compute next term based on predicted class
        next_val = _compute_next_term(top_class, seq, {})

        # Format outputs
        seq_str = str(seq)
        if len(seq_str) > 35:
            seq_str = seq_str[:32] + "..."
            
        next_str = "N/A"
        if next_val is not None:
            if isinstance(next_val, float) and next_val.is_integer():
                next_str = str(int(next_val))
            else:
                next_str = f"{next_val:.4f}"

        print(f"  {seq_str:<35}  {next_str:<14}  {top_class:<15}  {top_prob:>5.2%}")
    print("  " + "─" * 75)
    print()


def main() -> int:
    parser = argparse.ArgumentParser(description="Test model predictions on sample sequences.")
    parser.add_argument("--model", type=Path, default=_MODEL_PATH, help="Path to sequence_model.pkl.")
    parser.add_argument("--sequence", type=str, default="", help="Custom comma-separated sequence to test.")
    args = parser.parse_args()

    input_seq = None
    if args.sequence:
        try:
            input_seq = [float(x.strip()) for x in args.sequence.split(",") if x.strip()]
            if len(input_seq) < 3:
                print("Error: Test sequence must contain at least 3 numbers.")
                return 1
        except ValueError:
            print("Error: All terms in the sequence must be numeric.")
            return 1

    try:
        test_sequences(args.model, input_seq)
        return 0
    except Exception as exc:
        print(f"Test run aborted with error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
