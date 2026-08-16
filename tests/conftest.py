import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# infrastructure/database/database.py requires DATABASE_URL at import time.
# The test suite never talks to that engine (integration tests point every
# repository at an in-memory SQLite session instead), so a placeholder is
# enough to let the module import cleanly when no real .env is configured.
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")