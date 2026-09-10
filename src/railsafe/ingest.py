"""Build the retrieval index: chunk every corpus document into chunks.jsonl.

Usage:
    python -m railsafe.ingest
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

from .chunker import chunk_document
from .config import CHUNKS_FILE, CORPUS_DIR
from .logging_config import setup_logging

logger = logging.getLogger(__name__)


def build_index(corpus_dir: Path = CORPUS_DIR, out_file: Path = CHUNKS_FILE) -> int:
    """Build BM25 search index from corpus markdown files.

    Args:
        corpus_dir: Directory containing regulation documents (*.md).
        out_file: Output path for chunks.jsonl (one JSON object per line).

    Returns:
        Number of chunks indexed.

    Raises:
        FileNotFoundError: If corpus_dir contains no markdown files.
    """
    docs = sorted(corpus_dir.rglob("*.md"))
    if not docs:
        msg = f"No corpus documents found under {corpus_dir}"
        logger.error(msg)
        raise FileNotFoundError(msg)

    logger.info(f"Indexing {len(docs)} documents from {corpus_dir}")

    out_file.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with out_file.open("w", encoding="utf-8") as fh:
        for doc in docs:
            logger.debug(f"Chunking {doc.name}")
            for chunk in chunk_document(doc):
                fh.write(json.dumps(chunk.to_dict(), ensure_ascii=False) + "\n")
                count += 1

    logger.info(f"Indexed {count} chunks -> {out_file}")
    return count


def main() -> None:
    """CLI entry point for building the index."""
    setup_logging(logging.INFO)
    count = build_index()
    print(f"Indexed {count} chunks -> {CHUNKS_FILE}")


if __name__ == "__main__":
    sys.exit(main())
