"""Split corpus documents into retrieval chunks.

Documents are markdown files with YAML-ish front matter (simple key: value
lines between --- delimiters). Chunks are cut on `##` headings so each chunk
maps to a regulation section; oversized sections are further split into
overlapping paragraph windows.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from pathlib import Path

from .config import MAX_CHUNK_CHARS, CHUNK_OVERLAP_CHARS

FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    jurisdiction: str
    citation: str
    source_url: str
    section: str
    text: str

    def to_dict(self) -> dict:
        return asdict(self)


def parse_front_matter(raw: str) -> tuple[dict, str]:
    """Return (metadata, body). Metadata keys are simple `key: value` lines."""
    match = FRONT_MATTER_RE.match(raw)
    if not match:
        return {}, raw
    meta = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip().strip('"')
    return meta, raw[match.end():]


def _split_long(text: str) -> list[str]:
    """Split text into overlapping windows on paragraph boundaries."""
    if len(text) <= MAX_CHUNK_CHARS:
        return [text]
    paragraphs = [p for p in re.split(r"\n\n+", text) if p.strip()]
    windows: list[str] = []
    current = ""
    for para in paragraphs:
        if current and len(current) + len(para) + 2 > MAX_CHUNK_CHARS:
            windows.append(current)
            # carry a tail of the previous window forward for context
            current = current[-CHUNK_OVERLAP_CHARS:] + "\n\n" + para
        else:
            current = f"{current}\n\n{para}" if current else para
    if current.strip():
        windows.append(current)
    return windows


def chunk_document(path: Path) -> list[Chunk]:
    meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
    doc_id = meta.get("id", path.stem)
    sections: list[tuple[str, str]] = []  # (heading, text)

    heading = "Overview"
    buf: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            if "".join(buf).strip():
                sections.append((heading, "\n".join(buf).strip()))
            heading = line[3:].strip()
            buf = []
        else:
            buf.append(line)
    if "".join(buf).strip():
        sections.append((heading, "\n".join(buf).strip()))

    chunks: list[Chunk] = []
    for heading, text in sections:
        for i, window in enumerate(_split_long(text)):
            suffix = f"-{i}" if i else ""
            chunks.append(
                Chunk(
                    chunk_id=f"{doc_id}::{_slug(heading)}{suffix}",
                    doc_id=doc_id,
                    title=meta.get("title", path.stem),
                    jurisdiction=meta.get("jurisdiction", ""),
                    citation=meta.get("citation", ""),
                    source_url=meta.get("source_url", ""),
                    section=heading,
                    text=window.strip(),
                )
            )
    return chunks


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]
