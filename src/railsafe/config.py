"""Paths and defaults shared across the package."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORPUS_DIR = PROJECT_ROOT / "data" / "corpus"
INDEX_DIR = PROJECT_ROOT / "data" / "index"
CHUNKS_FILE = INDEX_DIR / "chunks.jsonl"

MODEL = "claude-opus-4-8"
MAX_TOKENS = 16000
DEFAULT_TOP_K = 6

# Chunking
MAX_CHUNK_CHARS = 2400
CHUNK_OVERLAP_CHARS = 200
