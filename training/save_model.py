"""
training/save_model.py
──────────────────────────────────────────────────────────────────────────────
Mathematical Sequence Prediction System — Model Serialization Utility

Helper module containing functions to serialize and save trained Random Forest
models, label encoders, and feature scalers to disk using Joblib.
──────────────────────────────────────────────────────────────────────────────
"""

import os
import joblib
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger("save_model")


def save_model_bundle(
    model: Any,
    label_encoder: Any,
    scaler: Optional[Any],
    output_path: Path,
    version: str = "v1.0.0",
    dataset_size: int = 0,
    metrics: Optional[Dict[str, float]] = None,
) -> bool:
    """
    Package and save the machine learning assets into a single serialized bundle file.

    Parameters
    ----------
    model : scikit-learn Classifier
        The trained Random Forest Classifier model.
    label_encoder : scikit-learn LabelEncoder
        The fitted label encoder mapping target classes.
    scaler : scikit-learn StandardScaler or None
        The fitted feature scaler.
    output_path : Path
        Absolute file path where the bundle .pkl will be saved.
    version : str
        Version label string of the model.
    dataset_size : int
        Number of samples used in training.
    metrics : dict or None
        Evaluation metrics dict (e.g. {"accuracy": 0.95, "f1_macro": 0.94}).

    Returns
    -------
    bool
        True on successful serialization, False otherwise.
    """
    try:
        # Ensure parent directories exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        bundle = {
            "model": model,
            "label_encoder": label_encoder,
            "scaler": scaler,
            "version": version,
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "dataset_size": dataset_size,
            "metrics": metrics or {}
        }

        # Save to disk
        joblib.dump(bundle, output_path)
        logger.info("Successfully saved model bundle to %s", output_path)
        return True

    except Exception as exc:
        logger.error("Failed to save model bundle: %s", exc)
        return False


if __name__ == "__main__":
    # Standard output setup for standalone check
    import sys
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    
    print("\n  Save model utility module initialized successfully.")
    print("  To use this, import save_model_bundle inside your training pipeline.")
    print()
    sys.exit(0)
