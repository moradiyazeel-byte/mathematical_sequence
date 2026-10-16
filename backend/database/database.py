"""
database/database.py
──────────────────────────────────────────────────────────────────────────────
Mathematical Sequence Prediction System — Multi-Dialect (SQLite & PostgreSQL) Layer

Responsibilities:
  • Open and cache a per-request SQLite or PostgreSQL connection (Flask g)
  • Dynamically detect dialect from DATABASE_PATH / DATABASE_URL
  • Create all tables and indexes automatically for the selected dialect
  • Multi-dialect query executables and placeholder routing
──────────────────────────────────────────────────────────────────────────────
"""

import os
import json
import hashlib
import logging
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing  import Any

from flask import g, current_app
import psycopg2
from psycopg2.extras import DictCursor
from psycopg2 import Error as PGError, IntegrityError as PGIntegrityError


logger = logging.getLogger("seqpredict.database")


# ─────────────────────────────────────────────────────────────────────────────
# Connection management
# ─────────────────────────────────────────────────────────────────────────────

def _db_path() -> str:
    """Resolve the database connection DSN / file path from Flask config or environment."""
    try:
        return current_app.config["DATABASE_PATH"]
    except RuntimeError:
        # Called outside Flask app context (e.g. CLI / tests)
        return os.getenv(
            "DATABASE_URL",
            os.getenv("DATABASE_PATH", str(Path(__file__).resolve().parents[2] / "database" / "sequence.db")),
        )


def _is_postgres() -> bool:
    """Check if the resolved connection string points to a PostgreSQL database."""
    dsn = _db_path()
    return dsn.startswith("postgresql://") or dsn.startswith("postgres://")


def get_connection():
    """
    Return the database connection for the current request.
    Dynamically connects to SQLite or PostgreSQL and caches the connection.
    """
    is_pg = _is_postgres()
    
    if is_pg:
        if "db_pg" not in g:
            dsn = _db_path()
            conn = psycopg2.connect(dsn)
            g.db_pg = conn
        return g.db_pg
    else:
        if "db_sqlite" not in g:
            db_path = _db_path()
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(
                db_path,
                detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
                check_same_thread = False,
                timeout = 30,
            )
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA synchronous = NORMAL;")
            g.db_sqlite = conn
        return g.db_sqlite


def close_connection(exc=None) -> None:
    """Close the request-scoped database connection."""
    conn_sqlite = g.pop("db_sqlite", None)
    if conn_sqlite is not None:
        conn_sqlite.close()
    
    conn_pg = g.pop("db_pg", None)
    if conn_pg is not None:
        conn_pg.close()


def _get_conn():
    """Return a database connection whether inside or outside request context."""
    try:
        return get_connection()
    except RuntimeError:
        dsn = _db_path()
        if dsn.startswith("postgresql://") or dsn.startswith("postgres://"):
            return psycopg2.connect(dsn)
        else:
            Path(dsn).parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(dsn, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn


def _execute(sql: str, params: tuple | list | None = None, fetch: str | None = None) -> Any:
    """Helper to execute SQL queries dynamically converting placeholders and tracking commit/rollback."""
    conn = _get_conn()
    is_pg = _is_postgres()
    
    if is_pg:
        sql = sql.replace("?", "%s")
    else:
        sql = sql.replace("%s", "?")
        
    try:
        if is_pg:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(sql, params or ())
                res = _fetch_results(cur, fetch)
                conn.commit()
                return res
        else:
            cur = conn.cursor()
            cur.execute(sql, params or ())
            res = _fetch_results(cur, fetch)
            conn.commit()
            return res
    except Exception as exc:
        conn.rollback()
        raise exc


def _fetch_results(cur, fetch: str | None) -> Any:
    if fetch == "one":
        row = cur.fetchone()
        return dict(row) if row else None
    elif fetch == "all":
        rows = cur.fetchall()
        return [dict(r) for r in rows] if rows else []
    elif fetch == "scalar":
        row = cur.fetchone()
        return row[0] if row else None
    elif fetch == "rowcount":
        return cur.rowcount
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Schema — DDL (Dual Dialect definitions)
# ─────────────────────────────────────────────────────────────────────────────

_CREATE_USERS_SQLITE = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    email         TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    full_name     TEXT,
    is_active     INTEGER NOT NULL DEFAULT 1,
    role          TEXT    NOT NULL DEFAULT 'user',
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);
"""

_CREATE_USERS_POSTGRES = """
CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    username      TEXT    NOT NULL UNIQUE,
    email         TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    full_name     TEXT,
    is_active     INTEGER NOT NULL DEFAULT 1,
    role          TEXT    NOT NULL DEFAULT 'user',
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);
"""

_CREATE_PREDICTION_HISTORY_SQLITE = """
CREATE TABLE IF NOT EXISTS prediction_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER,
    input_sequence  TEXT    NOT NULL,
    sequence_hash   TEXT    NOT NULL,
    predicted_next  TEXT    NOT NULL,
    pattern_type    TEXT,
    method_used     TEXT    NOT NULL DEFAULT 'rule',
    confidence      REAL,
    sequence_length INTEGER,
    is_correct      INTEGER,
    feedback_notes  TEXT,
    ip_address      TEXT,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
);
"""

_CREATE_PREDICTION_HISTORY_POSTGRES = """
CREATE TABLE IF NOT EXISTS prediction_history (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER,
    input_sequence  TEXT    NOT NULL,
    sequence_hash   TEXT    NOT NULL,
    predicted_next  TEXT    NOT NULL,
    pattern_type    TEXT,
    method_used     TEXT    NOT NULL DEFAULT 'rule',
    confidence      REAL,
    sequence_length INTEGER,
    is_correct      INTEGER,
    feedback_notes  TEXT,
    ip_address      TEXT,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
);
"""

_CREATE_MODEL_LOGS_SQLITE = """
CREATE TABLE IF NOT EXISTS model_logs (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name            TEXT    NOT NULL DEFAULT 'sequence_model',
    model_version         TEXT    NOT NULL,
    file_path             TEXT    NOT NULL,
    training_date         TIMESTAMP,
    dataset_size          INTEGER,
    accuracy              REAL,
    precision_score       REAL,
    recall_score          REAL,
    f1_score              REAL,
    training_duration_sec REAL,
    status                TEXT    NOT NULL DEFAULT 'active',
    notes                 TEXT,
    created_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

_CREATE_MODEL_LOGS_POSTGRES = """
CREATE TABLE IF NOT EXISTS model_logs (
    id                    SERIAL PRIMARY KEY,
    model_name            TEXT    NOT NULL DEFAULT 'sequence_model',
    model_version         TEXT    NOT NULL,
    file_path             TEXT    NOT NULL,
    training_date         TIMESTAMP,
    dataset_size          INTEGER,
    accuracy              REAL,
    precision_score       REAL,
    recall_score          REAL,
    f1_score              REAL,
    training_duration_sec REAL,
    status                TEXT    NOT NULL DEFAULT 'active',
    notes                 TEXT,
    created_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

_CREATE_SYSTEM_LOGS_SQLITE = """
CREATE TABLE IF NOT EXISTS system_logs (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    log_level      TEXT    NOT NULL DEFAULT 'INFO',
    source         TEXT,
    message        TEXT    NOT NULL,
    endpoint       TEXT,
    request_method TEXT,
    status_code    INTEGER,
    ip_address     TEXT,
    user_id        INTEGER,
    created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
);
"""

_CREATE_SYSTEM_LOGS_POSTGRES = """
CREATE TABLE IF NOT EXISTS system_logs (
    id             SERIAL PRIMARY KEY,
    log_level      TEXT    NOT NULL DEFAULT 'INFO',
    source         TEXT,
    message        TEXT    NOT NULL,
    endpoint       TEXT,
    request_method TEXT,
    status_code    INTEGER,
    ip_address     TEXT,
    user_id        INTEGER,
    created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
);
"""

_CREATE_SETTINGS_SQLITE = """
CREATE TABLE IF NOT EXISTS settings (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key   TEXT    NOT NULL UNIQUE,
    setting_value TEXT    NOT NULL,
    value_type    TEXT    NOT NULL DEFAULT 'string',
    description   TEXT,
    updated_by    INTEGER,
    updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (updated_by) REFERENCES users (id) ON DELETE SET NULL
);
"""

_CREATE_SETTINGS_POSTGRES = """
CREATE TABLE IF NOT EXISTS settings (
    id            SERIAL PRIMARY KEY,
    setting_key   TEXT    NOT NULL UNIQUE,
    setting_value TEXT    NOT NULL,
    value_type    TEXT    NOT NULL DEFAULT 'string',
    description   TEXT,
    updated_by    INTEGER,
    updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (updated_by) REFERENCES users (id) ON DELETE SET NULL
);
"""

_CREATE_OEIS_CACHE = """
CREATE TABLE IF NOT EXISTS oeis_cache (
    sequence_hash TEXT PRIMARY KEY,
    oeis_id       TEXT NOT NULL,
    name          TEXT NOT NULL,
    comments      TEXT,
    formulas      TEXT,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

_CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_prediction_history_user_id   ON prediction_history (user_id);",
    "CREATE INDEX IF NOT EXISTS idx_prediction_history_created_at ON prediction_history (created_at);",
    "CREATE INDEX IF NOT EXISTS idx_prediction_history_hash       ON prediction_history (sequence_hash);",
    "CREATE INDEX IF NOT EXISTS idx_prediction_history_pattern    ON prediction_history (pattern_type);",
    "CREATE INDEX IF NOT EXISTS idx_model_logs_status             ON model_logs (status);",
    "CREATE INDEX IF NOT EXISTS idx_system_logs_level             ON system_logs (log_level);",
    "CREATE INDEX IF NOT EXISTS idx_system_logs_created_at        ON system_logs (created_at);",
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_settings_key           ON settings (setting_key);",
]

_DEFAULT_SETTINGS = [
    ("active_model_version",   "v1.0.0",  "string",  "Currently active ML model version"),
    ("max_sequence_length",    "50",       "integer", "Maximum number of terms accepted per prediction"),
    ("min_sequence_length",    "3",        "integer", "Minimum number of terms required"),
    ("confidence_threshold",   "0.95",     "float",   "Minimum rule confidence to skip ML fallback"),
    ("prediction_cache_ttl_h", "24",       "integer", "Prediction cache TTL in hours"),
    ("allow_guest_predict",    "true",     "boolean", "Allow unauthenticated prediction requests"),
    ("ml_fallback_enabled",    "true",     "boolean", "Enable ML model fallback when rules fail"),
    ("system_version",         "1.0.0",   "string",  "Application version"),
]


def init_db() -> None:
    """Create all tables, indexes, and seed default settings for SQLite or PostgreSQL."""
    conn = _get_conn()
    is_pg = _is_postgres()
    try:
        if is_pg:
            with conn.cursor() as cur:
                # Tables
                for ddl in [
                    _CREATE_USERS_POSTGRES,
                    _CREATE_PREDICTION_HISTORY_POSTGRES,
                    _CREATE_MODEL_LOGS_POSTGRES,
                    _CREATE_SYSTEM_LOGS_POSTGRES,
                    _CREATE_SETTINGS_POSTGRES,
                    _CREATE_OEIS_CACHE,
                ]:
                    cur.execute(ddl)

                # Indexes
                for idx_sql in _CREATE_INDEXES:
                    cur.execute(idx_sql)

                # Seed settings
                for key, value, vtype, desc in _DEFAULT_SETTINGS:
                    cur.execute(
                        """
                        INSERT INTO settings (setting_key, setting_value, value_type, description)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (setting_key) DO NOTHING
                        """,
                        (key, value, vtype, desc),
                    )

                conn.commit()
                logger.info("PostgreSQL database schema initialised successfully.")
        else:
            with conn as cur:
                # Tables
                for ddl in [
                    _CREATE_USERS_SQLITE,
                    _CREATE_PREDICTION_HISTORY_SQLITE,
                    _CREATE_MODEL_LOGS_SQLITE,
                    _CREATE_SYSTEM_LOGS_SQLITE,
                    _CREATE_SETTINGS_SQLITE,
                    _CREATE_OEIS_CACHE,
                ]:
                    cur.execute(ddl)

                # Indexes
                for idx_sql in _CREATE_INDEXES:
                    cur.execute(idx_sql)

                # Seed settings
                for key, value, vtype, desc in _DEFAULT_SETTINGS:
                    cur.execute(
                        """
                        INSERT OR IGNORE INTO settings (setting_key, setting_value, value_type, description)
                        VALUES (?, ?, ?, ?)
                        """,
                        (key, value, vtype, desc),
                    )

                conn.commit()
                logger.info("SQLite database schema initialised successfully.")

    except Exception as exc:
        conn.rollback()
        logger.error("init_db failed: %s", exc)
        raise


# ─────────────────────────────────────────────────────────────────────────────
# Helper — timestamp and hash
# ─────────────────────────────────────────────────────────────────────────────

def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")


def make_sequence_hash(terms: list[float]) -> str:
    """
    Deterministic MD5 hash of a normalised sequence.
    Used as a cache key in prediction_history.
    """
    normalised = ",".join(str(float(t)) for t in terms)
    return hashlib.md5(normalised.encode()).hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# prediction_history CRUD
# ─────────────────────────────────────────────────────────────────────────────

def insert_prediction(
    input_sequence  : list[float],
    predicted_next  : float | int | None,
    pattern_type    : str | None,
    method_used     : str,
    confidence      : float,
    user_id         : int | None = None,
    ip_address      : str | None = None,
) -> int:
    """Insert a new prediction record and return the generated row id."""
    seq_str = json.dumps(input_sequence)
    seq_hash = make_sequence_hash(input_sequence)
    next_str = str(predicted_next) if predicted_next is not None else None
    is_pg = _is_postgres()

    if is_pg:
        sql = """
            INSERT INTO prediction_history
                (user_id, input_sequence, sequence_hash, predicted_next,
                 pattern_type, method_used, confidence, sequence_length, ip_address, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """
        prediction_id = _execute(
            sql,
            (
                user_id,
                seq_str,
                seq_hash,
                next_str,
                pattern_type,
                method_used,
                round(confidence, 6),
                len(input_sequence),
                ip_address,
                _now_utc(),
            ),
            fetch="scalar"
        )
    else:
        sql = """
            INSERT INTO prediction_history
                (user_id, input_sequence, sequence_hash, predicted_next,
                 pattern_type, method_used, confidence, sequence_length, ip_address, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        conn = _get_conn()
        cur = conn.execute(
            sql,
            (
                user_id,
                seq_str,
                seq_hash,
                next_str,
                pattern_type,
                method_used,
                round(confidence, 6),
                len(input_sequence),
                ip_address,
                _now_utc(),
            ),
        )
        conn.commit()
        prediction_id = cur.lastrowid

    logger.debug("Prediction inserted — id=%s  pattern=%s", prediction_id, pattern_type)
    return prediction_id


def count_guest_predictions(ip_address: str) -> int:
    """Count predictions made by a guest user from the given IP address."""
    sql = """
        SELECT COUNT(*) FROM prediction_history 
        WHERE user_id IS NULL AND ip_address = %s
    """
    val = _execute(sql, (ip_address,), fetch="scalar")
    return val if val is not None else 0


def get_prediction_by_id(prediction_id: int) -> dict | None:
    """Fetch a single prediction by primary key."""
    return _execute("SELECT * FROM prediction_history WHERE id = %s", (prediction_id,), fetch="one")


def get_cached_prediction(
    terms: list[float],
    ttl_hours: int = 24,
) -> dict | None:
    """Return a recent prediction for an identical sequence, if one exists."""
    seq_hash  = make_sequence_hash(terms)
    is_pg = _is_postgres()
    
    if is_pg:
        threshold = datetime.now(timezone.utc) - timedelta(hours=ttl_hours)
    else:
        threshold = (datetime.now(timezone.utc) - timedelta(hours=ttl_hours)).isoformat()
        
    sql = """
        SELECT * FROM prediction_history
        WHERE  sequence_hash = %s
        AND    created_at    > %s
        ORDER  BY created_at DESC
        LIMIT  1
    """
    return _execute(sql, (seq_hash, threshold), fetch="one")


def get_cached_oeis(sequence_hash: str) -> dict | None:
    """Look up and return cached OEIS info for a sequence hash."""
    row = _execute("SELECT * FROM oeis_cache WHERE sequence_hash = %s", (sequence_hash,), fetch="one")
    if row:
        res = dict(row)
        try:
            res["comments"] = json.loads(res["comments"])
        except (json.JSONDecodeError, TypeError):
            res["comments"] = []
        try:
            res["formulas"] = json.loads(res["formulas"])
        except (json.JSONDecodeError, TypeError):
            res["formulas"] = []
        return res
    return None


def insert_oeis_cache(
    sequence_hash : str,
    oeis_id       : str,
    name          : str,
    comments      : list[str],
    formulas      : list[str],
) -> None:
    """Cache the retrieved OEIS details."""
    is_pg = _is_postgres()
    
    if is_pg:
        sql = """
            INSERT INTO oeis_cache (sequence_hash, oeis_id, name, comments, formulas, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (sequence_hash) DO UPDATE SET
                oeis_id = EXCLUDED.oeis_id,
                name = EXCLUDED.name,
                comments = EXCLUDED.comments,
                formulas = EXCLUDED.formulas,
                created_at = EXCLUDED.created_at
        """
        _execute(sql, (sequence_hash, oeis_id, name, json.dumps(comments), json.dumps(formulas), _now_utc()))
    else:
        sql = """
            INSERT OR REPLACE INTO oeis_cache (sequence_hash, oeis_id, name, comments, formulas, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        _execute(sql, (sequence_hash, oeis_id, name, json.dumps(comments), json.dumps(formulas), _now_utc()))
        
    logger.debug("OEIS result cached for sequence_hash=%s", sequence_hash)


def get_history(
    user_id    : int | None = None,
    ip_address : str | None = None,
    page       : int        = 1,
    limit      : int        = 20,
    pattern    : str | None = None,
    method     : str | None = None,
    search     : str | None = None,
    sort_by    : str        = "newest",
) -> dict:
    """Paginated, filtered prediction history."""
    if user_id is None:
        return {
            "records": [],
            "total_records": 0,
            "page": page,
            "limit": limit,
        }

    params = []
    where  = ["user_id = %s"]
    params.append(user_id)

    if pattern:
        where.append("pattern_type = %s")
        params.append(pattern.lower())

    if method:
        where.append("method_used = %s")
        params.append(method.lower())

    if search:
        where.append("(input_sequence ILIKE %s OR pattern_type ILIKE %s OR predicted_next ILIKE %s)")
        like = f"%{search}%"
        params.extend([like, like, like])

    where_sql = "WHERE " + " AND ".join(where)

    order_map = {
        "newest"    : "created_at DESC",
        "oldest"    : "created_at ASC",
        "conf-high" : "confidence DESC",
        "conf-low"  : "confidence ASC",
    }
    order_sql = order_map.get(sort_by, "created_at DESC")

    # Total count
    total_sql = f"SELECT COUNT(*) FROM prediction_history {where_sql}"
    total = _execute(total_sql, params, fetch="scalar") or 0

    # Page slice
    offset  = (max(page, 1) - 1) * limit
    records_sql = f"""
        SELECT * FROM prediction_history
        {where_sql}
        ORDER BY {order_sql}
        LIMIT %s OFFSET %s
    """
    records = _execute(records_sql, params + [limit, offset], fetch="all")

    return {
        "records"      : records,
        "total_records": total,
        "page"         : page,
        "limit"        : limit,
        "total_pages"  : max(1, -(-total // limit)),
    }


def update_feedback(
    prediction_id  : int,
    is_correct     : bool,
    feedback_notes : str | None = None,
) -> bool:
    """Set the is_correct flag and optional notes on a prediction record."""
    sql = """
        UPDATE prediction_history
        SET    is_correct = %s, feedback_notes = %s
        WHERE  id = %s
    """
    rowcount = _execute(sql, (1 if is_correct else 0, feedback_notes, prediction_id), fetch="rowcount")
    return rowcount > 0


def delete_prediction(prediction_id: int, user_id: int | None = None, ip_address: str | None = None) -> bool:
    """Delete a single prediction record."""
    if user_id is None:
        return False

    sql = "DELETE FROM prediction_history WHERE id = %s AND user_id = %s"
    rowcount = _execute(sql, [prediction_id, user_id], fetch="rowcount")
    return rowcount > 0


def delete_all_predictions(user_id: int | None = None, ip_address: str | None = None) -> int:
    """Delete all prediction records."""
    if user_id is None:
        return 0

    sql = "DELETE FROM prediction_history WHERE user_id = %s"
    rowcount = _execute(sql, (user_id,), fetch="rowcount")
    return rowcount


def get_history_stats(user_id: int | None = None, ip_address: str | None = None) -> dict:
    """Return aggregated statistics for the history dashboard."""
    if user_id is None:
        return {
            "total_predictions"     : 0,
            "rule_based_predictions": 0,
            "ml_predictions"        : 0,
            "average_confidence"    : 0.0,
        }

    sql = """
        SELECT
            COUNT(*)                                AS total,
            SUM(CASE WHEN method_used='rule' THEN 1 ELSE 0 END) AS rule_count,
            SUM(CASE WHEN method_used='ml'   THEN 1 ELSE 0 END) AS ml_count,
            AVG(confidence)                         AS avg_confidence
        FROM prediction_history WHERE user_id = %s
    """
    row = _execute(sql, (user_id,), fetch="one")

    return {
        "total_predictions"     : row["total"]        or 0,
        "rule_based_predictions": row["rule_count"]   or 0,
        "ml_predictions"        : row["ml_count"]     or 0,
        "average_confidence"    : round(row["avg_confidence"] or 0.0, 4),
    }


# ─────────────────────────────────────────────────────────────────────────────
# users CRUD
# ─────────────────────────────────────────────────────────────────────────────

def create_user(
    username     : str,
    email        : str,
    password_hash: str,
    full_name    : str | None = None,
    role         : str        = "user",
) -> int:
    """Insert a new user and return the generated user id."""
    is_pg = _is_postgres()
    if is_pg:
        sql = """
            INSERT INTO users (username, email, password_hash, full_name, role, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
        """
        try:
            user_id = _execute(sql, (username, email, password_hash, full_name, role, _now_utc(), _now_utc()), fetch="scalar")
            return user_id
        except PGIntegrityError as exc:
            raise ValueError(str(exc)) from exc
    else:
        sql = """
            INSERT INTO users (username, email, password_hash, full_name, role, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        try:
            conn = _get_conn()
            cur = conn.execute(sql, (username, email, password_hash, full_name, role, _now_utc(), _now_utc()))
            conn.commit()
            return cur.lastrowid
        except sqlite3.IntegrityError as exc:
            conn.rollback()
            raise ValueError(str(exc)) from exc


def get_user_by_id(user_id: int) -> dict | None:
    return _execute("SELECT * FROM users WHERE id = %s", (user_id,), fetch="one")


def get_user_by_email(email: str) -> dict | None:
    if _is_postgres():
        return _execute("SELECT * FROM users WHERE LOWER(email) = LOWER(%s)", (email,), fetch="one")
    else:
        return _execute("SELECT * FROM users WHERE email = ? COLLATE NOCASE", (email,), fetch="one")


def get_user_by_username(username: str) -> dict | None:
    if _is_postgres():
        return _execute("SELECT * FROM users WHERE LOWER(username) = LOWER(%s)", (username,), fetch="one")
    else:
        return _execute("SELECT * FROM users WHERE username = ? COLLATE NOCASE", (username,), fetch="one")


def update_user(user_id: int, **fields) -> bool:
    """Update arbitrary user fields by keyword argument."""
    allowed = {"username", "email", "full_name", "is_active", "role", "password_hash"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return False

    updates["updated_at"] = _now_utc()
    set_sql  = ", ".join(f"{k} = %s" for k in updates)
    values   = list(updates.values()) + [user_id]

    sql = f"UPDATE users SET {set_sql} WHERE id = %s"
    rowcount = _execute(sql, values, fetch="rowcount")
    return rowcount > 0


def update_last_login(user_id: int) -> None:
    _execute("UPDATE users SET last_login_at = %s WHERE id = %s", (_now_utc(), user_id))


def delete_user(user_id: int) -> bool:
    rowcount = _execute("DELETE FROM users WHERE id = %s", (user_id,), fetch="rowcount")
    return rowcount > 0


def list_users(page: int = 1, limit: int = 20) -> dict:
    total  = _execute("SELECT COUNT(*) FROM users", fetch="scalar") or 0
    offset = (max(page, 1) - 1) * limit
    sql = """
        SELECT id, username, email, full_name, role, is_active, created_at, last_login_at 
        FROM users ORDER BY created_at DESC LIMIT %s OFFSET %s
    """
    rows = _execute(sql, (limit, offset), fetch="all")
    return {
        "users"      : rows,
        "total_users": total,
        "page"       : page,
        "limit"      : limit,
    }


def set_user_status(user_id: int, is_active: bool) -> bool:
    sql = "UPDATE users SET is_active = %s, updated_at = %s WHERE id = %s"
    rowcount = _execute(sql, (1 if is_active else 0, _now_utc(), user_id), fetch="rowcount")
    return rowcount > 0


# ─────────────────────────────────────────────────────────────────────────────
# model_logs CRUD
# ─────────────────────────────────────────────────────────────────────────────

def insert_model_log(
    model_name            : str,
    model_version         : str,
    file_path             : str,
    training_date         : str | None  = None,
    dataset_size          : int | None  = None,
    accuracy              : float | None= None,
    precision_score       : float | None= None,
    recall_score          : float | None= None,
    f1_score              : float | None= None,
    training_duration_sec : float | None= None,
    status                : str         = "active",
    notes                 : str | None  = None,
) -> int:
    """Insert a model training run record. Deprecates any previous active model."""
    _execute("UPDATE model_logs SET status = 'deprecated' WHERE status = 'active' AND model_name = %s", (model_name,))
    is_pg = _is_postgres()

    if is_pg:
        sql = """
            INSERT INTO model_logs
                (model_name, model_version, file_path, training_date, dataset_size,
                 accuracy, precision_score, recall_score, f1_score,
                 training_duration_sec, status, notes, created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
        """
        log_id = _execute(
            sql,
            (
                model_name, model_version, file_path,
                training_date or _now_utc(), dataset_size,
                accuracy, precision_score, recall_score, f1_score,
                training_duration_sec, status, notes, _now_utc(),
            ),
            fetch="scalar"
        )
    else:
        sql = """
            INSERT INTO model_logs
                (model_name, model_version, file_path, training_date, dataset_size,
                 accuracy, precision_score, recall_score, f1_score,
                 training_duration_sec, status, notes, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """
        conn = _get_conn()
        cur = conn.execute(
            sql,
            (
                model_name, model_version, file_path,
                training_date or _now_utc(), dataset_size,
                accuracy, precision_score, recall_score, f1_score,
                training_duration_sec, status, notes, _now_utc(),
            ),
        )
        conn.commit()
        log_id = cur.lastrowid

    return log_id


def get_active_model_log() -> dict | None:
    sql = "SELECT * FROM model_logs WHERE status = 'active' ORDER BY created_at DESC LIMIT 1"
    return _execute(sql, fetch="one")


def list_model_logs(limit: int = 20) -> list[dict]:
    sql = "SELECT * FROM model_logs ORDER BY created_at DESC LIMIT %s"
    return _execute(sql, (limit,), fetch="all")


# ─────────────────────────────────────────────────────────────────────────────
# system_logs CRUD
# ─────────────────────────────────────────────────────────────────────────────

def log_system_event(
    message        : str,
    log_level      : str        = "INFO",
    source         : str | None = None,
    endpoint       : str | None = None,
    request_method : str | None = None,
    status_code    : int | None = None,
    ip_address     : str | None = None,
    user_id        : int | None = None,
) -> None:
    """Write a system log entry."""
    try:
        sql = """
            INSERT INTO system_logs
                (log_level, source, message, endpoint, request_method,
                 status_code, ip_address, user_id, created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        _execute(
            sql,
            (
                log_level.upper(),
                source,
                message[:1000],
                endpoint,
                request_method,
                status_code,
                ip_address,
                user_id,
                _now_utc(),
            ),
        )
    except Exception as exc:
        logger.error("log_system_event failed silently: %s", exc)


def get_system_logs(
    level  : str | None = None,
    source : str | None = None,
    page   : int        = 1,
    limit  : int        = 50,
) -> dict:
    where  = []
    params = []

    if level:
        where.append("log_level = %s")
        params.append(level.upper())
    if source:
        where.append("source = %s")
        params.append(source)

    where_sql = "WHERE " + " AND ".join(where) if where else ""
    
    total_sql = f"SELECT COUNT(*) FROM system_logs {where_sql}"
    total = _execute(total_sql, params, fetch="scalar") or 0

    offset = (max(page, 1) - 1) * limit
    sql = f"SELECT * FROM system_logs {where_sql} ORDER BY created_at DESC LIMIT %s OFFSET %s"
    rows = _execute(sql, params + [limit, offset], fetch="all")

    return {
        "logs"       : rows,
        "total_logs" : total,
        "page"       : page,
        "limit"      : limit,
    }


# ─────────────────────────────────────────────────────────────────────────────
# settings CRUD
# ─────────────────────────────────────────────────────────────────────────────

def get_setting(key: str, default: Any = None) -> Any:
    """Retrieve a setting value by key, cast to the stored value_type."""
    row = _execute("SELECT setting_value, value_type FROM settings WHERE setting_key = %s", (key,), fetch="one")
    if not row:
        return default

    raw   = row["setting_value"]
    vtype = row["value_type"]

    try:
        if vtype == "integer": return int(raw)
        if vtype == "float":   return float(raw)
        if vtype == "boolean": return raw.lower() in ("true", "1", "yes")
        if vtype == "json":    return json.loads(raw)
        return raw
    except (ValueError, json.JSONDecodeError):
        return raw


def set_setting(
    key        : str,
    value      : Any,
    updated_by : int | None = None,
) -> bool:
    """Create or update a setting by key."""
    if isinstance(value, bool):
        str_value = "true" if value else "false"
        vtype     = "boolean"
    elif isinstance(value, int):
        str_value = str(value)
        vtype     = "integer"
    elif isinstance(value, float):
        str_value = str(value)
        vtype     = "float"
    elif isinstance(value, (dict, list)):
        str_value = json.dumps(value)
        vtype     = "json"
    else:
        str_value = str(value)
        vtype     = "string"

    sql = """
        INSERT INTO settings (setting_key, setting_value, value_type, updated_by, updated_at)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (setting_key) DO UPDATE SET
            setting_value = EXCLUDED.setting_value,
            value_type    = EXCLUDED.value_type,
            updated_by    = EXCLUDED.updated_by,
            updated_at    = EXCLUDED.updated_at
    """
    _execute(sql, (key, str_value, vtype, updated_by, _now_utc()))
    return True


def list_settings() -> list[dict]:
    return _execute("SELECT * FROM settings ORDER BY setting_key ASC", fetch="all")


# ─────────────────────────────────────────────────────────────────────────────
# Admin dashboard aggregates
# ─────────────────────────────────────────────────────────────────────────────

def get_admin_stats() -> dict:
    """Aggregate statistics for the admin dashboard endpoint."""
    pred_row = _execute(
        """
        SELECT
            COUNT(*)                                            AS total,
            SUM(CASE WHEN method_used='rule' THEN 1 ELSE 0 END) AS rule_n,
            SUM(CASE WHEN method_used='ml'   THEN 1 ELSE 0 END) AS ml_n,
            AVG(confidence)                                     AS avg_conf
        FROM prediction_history
        """,
        fetch="one"
    )

    user_row  = _execute("SELECT COUNT(*) AS n FROM users", fetch="one")
    model_row = get_active_model_log()

    return {
        "total_users"            : user_row["n"]          if user_row  else 0,
        "total_predictions"      : pred_row["total"]      or 0,
        "rule_based_predictions" : pred_row["rule_n"]     or 0,
        "ml_predictions"         : pred_row["ml_n"]       or 0,
        "average_confidence"     : round(pred_row["avg_conf"] or 0.0, 4),
        "active_model_version"   : model_row["model_version"] if model_row else "N/A",
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLI — initialise database from the command line
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    dsn = (
        sys.argv[1]
        if len(sys.argv) > 1
        else os.getenv("DATABASE_URL", os.getenv("DATABASE_PATH", str(Path(__file__).resolve().parents[2] / "database" / "sequence.db")))
    )
    if dsn.startswith("postgresql://") or dsn.startswith("postgres://"):
        os.environ["DATABASE_URL"] = dsn
    else:
        os.environ["DATABASE_PATH"] = dsn

    print(f"Initialising database ({'PostgreSQL' if _is_postgres() else 'SQLite'})...")
    init_db()
    print("Done — all tables and indexes created.")