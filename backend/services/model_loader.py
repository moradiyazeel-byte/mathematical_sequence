"""
services/model_loader.py
──────────────────────────────────────────────────────────────────────────────
Mathematical Sequence Prediction System — ML Model Loader
──────────────────────────────────────────────────────────────────────────────
"""

import os
import joblib
import numpy as np


class ModelLoader:
    """
    Manages loading, holding, and running predictions on the trained Random
    Forest model bundle.
    """

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self.label_encoder = None
        self.scaler = None
        self.version = "unknown"
        self.trained_at = None
        self.dataset_size = None
        self.metrics = None
        self.feature_names = []

    def load(self) -> None:
        """
        Load the joblib model bundle from disk.

        Raises
        ------
        FileNotFoundError
            If the model file does not exist.
        """
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found at: {self.model_path}")

        # Load the serialized bundle
        bundle = joblib.load(self.model_path)
        
        self.model = bundle["model"]
        self.label_encoder = bundle["label_encoder"]
        self.scaler = bundle.get("scaler", None)  # Load scaler if exists in bundle
        self.version = bundle.get("version", "unknown")
        self.trained_at = bundle.get("trained_at")
        self.dataset_size = bundle.get("dataset_size")
        self.metrics = bundle.get("metrics")
        self.feature_names = bundle.get("feature_names", [])

    def predict(self, features: np.ndarray) -> dict:
        """
        Predict the sequence classification probabilities and return
        the most likely pattern type and confidence score.
        """
        if self.model is None or self.label_encoder is None:
            raise RuntimeError("ML model has not been loaded yet. Call load() first.")

        # Apply scaler transformation if it is configured
        if self.scaler is not None:
            features = self.scaler.transform(features)

        # Get class probabilities
        probas = self.model.predict_proba(features)[0]
        classes = self.label_encoder.classes_

        # Sort indices by probability descending
        sorted_indices = np.argsort(probas)[::-1]

        # Highest probability class
        top_idx = sorted_indices[0]
        top_class = self.label_encoder.inverse_transform([top_idx])[0]
        top_prob = float(probas[top_idx])

        # All class probabilities mapping
        class_probabilities = {classes[i]: float(probas[i]) for i in range(len(classes))}

        # Second highest probability class (alternative)
        top_alternative = {}
        if len(sorted_indices) > 1:
            alt_idx = sorted_indices[1]
            alt_class = self.label_encoder.inverse_transform([alt_idx])[0]
            alt_prob = float(probas[alt_idx])
            top_alternative = {
                "pattern_type": alt_class,
                "confidence": round(alt_prob, 6)
            }

        return {
            "pattern_type": top_class,
            "confidence": round(top_prob, 6),
            "class_probabilities": class_probabilities,
            "top_alternative": top_alternative
        }
