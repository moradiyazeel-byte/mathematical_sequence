"""
models/user_model.py
──────────────────────────────────────────────────────────────────────────────
Mathematical Sequence Prediction System — User Model Class
──────────────────────────────────────────────────────────────────────────────
"""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class User:
    """
    Data model representing a record in the users table.
    """
    id: Optional[int]
    username: str
    email: str
    password_hash: str
    full_name: Optional[str]
    is_active: bool
    role: str
    created_at: str
    updated_at: str
    last_login_at: Optional[str]

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        Serialize the model instance into a standard JSON-compatible dictionary.
        Safely excludes the password_hash by default.
        """
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "role": self.role,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_login_at": self.last_login_at,
        }
        if include_sensitive:
            data["password_hash"] = self.password_hash
        return data

    @classmethod
    def from_row(cls, row: Any) -> "User":
        """
        Build a User instance from a SQLite Row or dictionary.
        """
        return cls(
            id=row.get("id"),
            username=row.get("username", ""),
            email=row.get("email", ""),
            password_hash=row.get("password_hash", ""),
            full_name=row.get("full_name"),
            is_active=bool(row.get("is_active", 1)),
            role=row.get("role", "user"),
            created_at=str(row.get("created_at", "")),
            updated_at=str(row.get("updated_at", "")),
            last_login_at=str(row.get("last_login_at")) if row.get("last_login_at") else None,
        )
