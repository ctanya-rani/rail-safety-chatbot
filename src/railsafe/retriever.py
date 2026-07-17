"""BM25 retrieval over the chunk index.

Lexical retrieval keeps the project free of embedding-API dependencies and
works well here: regulation queries are dense in distinctive vocabulary
(section numbers, defined terms like "roadway worker" or "safety management
system").
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from rank_bm25 import BM25Okapi

from .chunker import Chunk
from .config import CHUNKS_FILE, DEFAULT_TOP_K

# Words + section-number tokens like "213.9" or "402/2013"
TOKEN_RE = re.compile(r"[a-z0-9]+(?:[./][a-z0-9]+)*")

# Light domain synonym expansion so plain-English queries hit regulation terms.
SYNONYMS = {
    "speed": ["mph", "maximum", "allowable"],
    "drug": ["controlled", "substance", "alcohol"],
    "drugs": ["controlled", "substance", "alcohol"],
    "driver": ["engineer", "conductor", "certification"],
    "sms": ["safety", "management", "system"],
    "risk": ["hazard", "assessment"],
    "inspection": ["inspect", "inspected"],
    "brake": ["brakes", "braking"],
    "eu": ["era", "european"],
    "europe": ["era", "eu"],
    "us": ["fra"],
    "america": ["fra"],
}


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def expand_query(tokens: list[str]) -> list[str]:
    expanded = list(tokens)
    for tok in tokens:
        expanded.extend(SYNONYMS.get(tok, []))
    return expanded


@dataclass
class Hit:
    chunk: Chunk
    score: float


class Retriever:
    def __init__(self, chunks_file: Path = CHUNKS_FILE):
        if not chunks_file.exists():
            raise FileNotFoundError(
                f"{chunks_file} not found — run `python -m railsafe.ingest` first."
            )
        self.chunks: list[Chunk] = []
        with chunks_file.open(encoding="utf-8") as fh:
            for line in fh:
                self.chunks.append(Chunk(**json.loads(line)))
        corpus_tokens = [
            tokenize(f"{c.title} {c.citation} {c.section} {c.text}")
            for c in self.chunks
        ]
        self._bm25 = BM25Okapi(corpus_tokens)

    def search(
        self,
        query: str,
        k: int = DEFAULT_TOP_K,
        jurisdiction: str | None = None,
    ) -> list[Hit]:
        """Top-k chunks for a plain-English query.

        `jurisdiction` optionally restricts results to "US-FRA" or "EU-ERA".
        """
        scores = self._bm25.get_scores(expand_query(tokenize(query)))
        hits = [
            Hit(chunk=c, score=float(s))
            for c, s in zip(self.chunks, scores)
            if s > 0 and (jurisdiction is None or c.jurisdiction == jurisdiction)
        ]
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:k]
