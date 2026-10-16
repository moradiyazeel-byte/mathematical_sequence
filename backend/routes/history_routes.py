"""
routes/history_routes.py
──────────────────────────────────────────────────────────────────────────────
Mathematical Sequence Prediction System — History Blueprint

Endpoints:
    GET     /api/history                  Get paginated, filtered prediction history
    DELETE  /api/history/<prediction_id>  Delete a single prediction history record
    DELETE  /api/history                  Clear prediction history
──────────────────────────────────────────────────────────────────────────────
"""

import json
import logging
from flask import Blueprint, request, jsonify, g

from database.database import (
    get_history,
    delete_prediction,
    delete_all_predictions,
)
from utils.auth import optional_auth, _ok, _err

logger = logging.getLogger("seqpredict.history_routes")

history_bp = Blueprint("history", __name__)


def _process_records(records: list[dict]) -> list[dict]:
    """Helper to deserialize stored JSON input_sequence and parse predicted_next."""
    for r in records:
        # Parse input_sequence from JSON string to list of numbers
        if isinstance(r.get("input_sequence"), str):
            try:
                r["input_sequence"] = json.loads(r["input_sequence"])
            except (json.JSONDecodeError, TypeError):
                # Fallback: split by comma if saved as plain string
                if "," in r["input_sequence"]:
                    try:
                        r["input_sequence"] = [float(x.strip()) for x in r["input_sequence"].split(",") if x.strip()]
                    except ValueError:
                        pass

        # Convert predicted_next from string to float/int
        if r.get("predicted_next") is not None:
            try:
                val = float(r["predicted_next"])
                r["predicted_next"] = int(val) if val.is_integer() else val
            except (ValueError, TypeError):
                pass
                
    return records


@history_bp.route("/history", methods=["GET"])
@optional_auth
def history():
    """
    Retrieve paginated, filtered prediction history records.
    
    Query Parameters:
        page (int): Page number (default 1)
        limit (int): Records per page (default 20, max 200)
        pattern (str): Filter by pattern type (e.g. "arithmetic")
        method (str): Filter by method used ("rule" or "ml")
        search (str): Search query for input_sequence or pattern_type
        sort_by (str): Sort order ("newest", "oldest", "conf-high", "conf-low")
    """
    try:
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 20, type=int)
        pattern = request.args.get("pattern", None)
        method = request.args.get("method", None)
        search = request.args.get("search", None)
        sort_by = request.args.get("sort_by", "newest")

        # Cap limit to prevent server overload
        limit = min(max(limit, 1), 200)
        page = max(page, 1)

        user_id = g.get("user_id")

        logger.debug(
            "Fetching history — user=%s page=%d limit=%d pattern=%s method=%s",
            user_id or "guest", page, limit, pattern, method
        )

        result = get_history(
            user_id=user_id,
            page=page,
            limit=limit,
            pattern=pattern,
            method=method,
            search=search,
            sort_by=sort_by,
        )

        # Deserialize sequence columns and parse next terms
        result["records"] = _process_records(result["records"])

        return _ok(result)

    except Exception as exc:
        logger.error("Error retrieving prediction history: %s", exc, exc_info=True)
        return _err("An unexpected error occurred retrieving history.", 500, "SERVER_ERROR")


@history_bp.route("/history/<int:prediction_id>", methods=["DELETE"])
@optional_auth
def delete_history_record(prediction_id: int):
    """Delete a single prediction history record by ID."""
    try:
        user_id = g.get("user_id")
        if not user_id:
            return _err("Authentication required.", 401, "UNAUTHORISED")
        
        # Calls database operation, respecting ownership
        success = delete_prediction(prediction_id, user_id=user_id)
        
        if not success:
            logger.warning(
                "Failed to delete prediction #%d — user=%s (not found or unauthorized)",
                prediction_id, user_id
            )
            return _err("Record not found or unauthorized.", 404, "NOT_FOUND")

        logger.info("Deleted prediction record #%d — user=%s", prediction_id, user_id)
        return _ok({"message": "Record deleted", "id": prediction_id})

    except Exception as exc:
        logger.error("Error deleting prediction #%d: %s", prediction_id, exc, exc_info=True)
        return _err("An unexpected error occurred deleting record.", 500, "SERVER_ERROR")


@history_bp.route("/history", methods=["DELETE"])
@optional_auth
def clear_history():
    """Clear all prediction history records (for current user)."""
    try:
        user_id = g.get("user_id")
        if not user_id:
            return _err("Authentication required.", 401, "UNAUTHORISED")
        
        deleted_count = delete_all_predictions(user_id=user_id)
        
        logger.info("Cleared history — deleted %d records — user=%s", deleted_count, user_id or "guest")
        return _ok({
            "message": "History cleared successfully.",
            "deleted_count": deleted_count
        })

    except Exception as exc:
        logger.error("Error clearing prediction history: %s", exc, exc_info=True)
        return _err("An unexpected error occurred clearing history.", 500, "SERVER_ERROR")
