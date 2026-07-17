"""Build the retrieval index: chunk every corpus document into chunks.jsonl.

Usage:
    python -m railsafe.ingest
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from .chunker import chunk_document
from .config import CHUNKS_FILE, CORPUS_DIR


def build_index(corpus_dir: Path = CORPUS_DIR, out_file: Path = CHUNKS_FILE) -> int:
    docs = sorted(corpus_dir.rglob("*.md"))
    if not docs:
        raise FileNotFoundError(f"No corpus documents found under {corpus_dir}")

    out_file.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with out_file.open("w", encoding="utf-8") as fh:
        for doc in docs:
            for chunk in chunk_document(doc):
                fh.write(json.dumps(chunk.to_dict(), ensure_ascii=False) + "\n")
                count += 1
    return count


def main() -> None:
    count = build_index()
    print(f"Indexed {count} chunks -> {CHUNKS_FILE}")


if __name__ == "__main__":
    sys.exit(main())
