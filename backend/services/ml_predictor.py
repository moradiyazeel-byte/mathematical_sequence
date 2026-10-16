"""
services/ml_predictor.py
──────────────────────────────────────────────────────────────────────────────
Mathematical Sequence Prediction System — ML Predictor Wrapper
──────────────────────────────────────────────────────────────────────────────
"""

import os
import joblib
import numpy as np
from typing import Dict, Any


class MLPredictor:
    """
    Service class responsible for loading the trained machine learning model
    and predicting sequence types along with confidence scores.
    """

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self.label_encoder = None
        self.version = "unknown"

    def load_model(self) -> None:
        """
        Load the Random Forest classifier model bundle from disk.
        """
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Trained model not found at: {self.model_path}")

        bundle = joblib.load(self.model_path)
        self.model = bundle["model"]
        self.label_encoder = bundle["label_encoder"]
        self.version = bundle.get("version", "unknown")

    def predict_sequence(self, features: np.ndarray) -> Dict[str, Any]:
        """
        Predict the classification probabilities of the sequence and return
        the most likely pattern type and confidence score.
        """
        if self.model is None or self.label_encoder is None:
            raise RuntimeError("Model has not been loaded. Call load_model() first.")

        # Perform inference to get probability distribution over classes
        probas = self.model.predict_proba(features)[0]
        classes = self.label_encoder.classes_

        # Get class with highest probability
        top_idx = np.argmax(probas)
        top_class = self.label_encoder.inverse_transform([top_idx])[0]
        top_prob = float(probas[top_idx])

        # Map all classes to their respective confidence scores
        class_probabilities = {classes[i]: float(probas[i]) for i in range(len(classes))}

        return {
            "pattern_type": top_class,
            "confidence": round(top_prob, 6),
            "class_probabilities": class_probabilities
        }
