from pathlib import Path

from railsafe.chunker import chunk_document, parse_front_matter
from railsafe.config import CORPUS_DIR


def test_parse_front_matter():
    raw = "---\nid: doc-1\ntitle: Some Title\n---\nbody text\n"
    meta, body = parse_front_matter(raw)
    assert meta == {"id": "doc-1", "title": "Some Title"}
    assert body.strip() == "body text"


def test_parse_front_matter_missing():
    meta, body = parse_front_matter("no front matter here")
    assert meta == {}
    assert body == "no front matter here"


def test_chunk_document_splits_on_headings(tmp_path: Path):
    doc = tmp_path / "doc.md"
    doc.write_text(
        "---\nid: t1\ntitle: T\njurisdiction: US-FRA\ncitation: c\n"
        "source_url: u\n---\n\nintro\n\n## Section A\n\naaa\n\n## Section B\n\nbbb\n"
    )
    chunks = chunk_document(doc)
    assert [c.section for c in chunks] == ["Overview", "Section A", "Section B"]
    assert chunks[1].text == "aaa"
    assert chunks[1].doc_id == "t1"
    assert chunks[0].chunk_id != chunks[1].chunk_id


def test_long_sections_are_windowed(tmp_path: Path):
    doc = tmp_path / "doc.md"
    para = "word " * 300  # ~1500 chars per paragraph
    doc.write_text(f"---\nid: t2\n---\n## Big\n\n{para}\n\n{para}\n\n{para}\n")
    chunks = chunk_document(doc)
    assert len(chunks) > 1
    assert all(c.section == "Big" for c in chunks)


def test_real_corpus_chunks():
    docs = sorted(CORPUS_DIR.glob("*.md"))
    assert len(docs) >= 10
    for doc in docs:
        chunks = chunk_document(doc)
        assert chunks, f"{doc.name} produced no chunks"
        for c in chunks:
            assert c.jurisdiction in {"US-FRA", "EU-ERA"}
            assert c.citation
            assert c.text
