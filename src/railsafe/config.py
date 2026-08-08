"""Paths and defaults shared across the package."""

import os
from pathlib import Path


def _str_env(name: str, default: str) -> str:
    # Hosting dashboards happily create set-but-empty variables, so treat
    # those as unset rather than letting "" through as a real value.
    return os.environ.get(name, "").strip() or default


def _int_env(name: str, default: int) -> int:
    return int(_str_env(name, str(default)))


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORPUS_DIR = PROJECT_ROOT / "data" / "corpus"
INDEX_DIR = PROJECT_ROOT / "data" / "index"
CHUNKS_FILE = INDEX_DIR / "chunks.jsonl"

MODEL = _str_env("RAILSAFE_MODEL", "claude-opus-4-8")
MAX_TOKENS = _int_env("RAILSAFE_MAX_TOKENS", 16000)
DEFAULT_TOP_K = _int_env("RAILSAFE_TOP_K", 6)

# Chunking
MAX_CHUNK_CHARS = 2400
CHUNK_OVERLAP_CHARS = 200
