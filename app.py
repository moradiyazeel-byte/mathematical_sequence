"""
Root WSGI entrypoint for Render and other cloud deployment platforms.
Allows running `gunicorn app:app` directly from the repository root.
"""
import sys
import os
from pathlib import Path

# Ensure backend directory is on sys.path
_ROOT = Path(__file__).resolve().parent
_BACKEND = _ROOT / "backend"

if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

import importlib.util
_spec = importlib.util.spec_from_file_location("backend_main_app", str(_BACKEND / "app.py"))
_mod = importlib.util.module_from_spec(_spec)
sys.modules["backend_main_app"] = _mod
_spec.loader.exec_module(_mod)

# Expose Flask app instance for WSGI servers like Gunicorn
app = _mod.app

if __name__ == "__main__":
    port = int(os.getenv("PORT", os.getenv("FLASK_PORT", 5000)))
    app.run(host="0.0.0.0", port=port)
