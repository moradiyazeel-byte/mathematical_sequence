"""
models/prediction_model.py
──────────────────────────────────────────────────────────────────────────────
Mathematical Sequence Prediction System — Prediction History Model Class
──────────────────────────────────────────────────────────────────────────────
"""

import json
from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class PredictionHistory:
    """
    Data model representing a record in the prediction_history table.
    """
    id: Optional[int]
    user_id: Optional[int]
    input_sequence: List[float]
    sequence_hash: str
    predicted_next: float
    pattern_type: Optional[str]
    method_used: str
    confidence: float
    sequence_length: int
    is_correct: Optional[bool]
    feedback_notes: Optional[str]
    created_at: str

    def to_dict(self) -> dict:
        """
        Serialize the model instance into a standard JSON-compatible dictionary.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "input_sequence": self.input_sequence,
            "sequence_hash": self.sequence_hash,
            "predicted_next": self.predicted_next,
            "pattern_type": self.pattern_type,
            "method_used": self.method_used,
            "confidence": round(self.confidence, 6),
            "sequence_length": self.sequence_length,
            "is_correct": self.is_correct,
            "feedback_notes": self.feedback_notes,
            "created_at": self.created_at,
        }

    @classmethod
    def from_row(cls, row: Any) -> "PredictionHistory":
        """
        Build a PredictionHistory instance from a SQLite Row or dictionary.
        """
        # Parse stored JSON sequence back into a list of floats
        seq_raw = row.get("input_sequence")
        if isinstance(seq_raw, str):
            try:
                sequence = json.loads(seq_raw)
            except (json.JSONDecodeError, TypeError):
                # Fallback splitting by comma if stored as plain string
                sequence = [float(x.strip()) for x in seq_raw.split(",") if x.strip()]
        else:
            sequence = list(seq_raw) if seq_raw else []

        # Parse next term to float/int
        next_raw = row.get("predicted_next")
        try:
            val = float(next_raw)
            next_val = int(val) if val.is_integer() else val
        except (ValueError, TypeError):
            next_val = next_raw

        return cls(
            id=row.get("id"),
            user_id=row.get("user_id"),
            input_sequence=sequence,
            sequence_hash=row.get("sequence_hash", ""),
            predicted_next=next_val,
            pattern_type=row.get("pattern_type"),
            method_used=row.get("method_used", "rule"),
            confidence=float(row.get("confidence") or 0.0),
            sequence_length=row.get("sequence_length") or len(sequence),
            is_correct=bool(row.get("is_correct")) if row.get("is_correct") is not None else None,
            feedback_notes=row.get("feedback_notes"),
            created_at=str(row.get("created_at", "")),
        )
