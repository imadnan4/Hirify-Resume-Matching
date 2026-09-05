import os
import sys
from pathlib import Path

os.environ.setdefault("EMBEDDING_BACKEND", "hash")
os.environ.setdefault("DATABASE_URL", "sqlite://")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
