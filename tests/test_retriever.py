import pytest

from railsafe.config import CHUNKS_FILE
from railsafe.ingest import build_index
from railsafe.retriever import Retriever, tokenize


@pytest.fixture(scope="module")
def retriever() -> Retriever:
    build_index()  # rebuild so tests never depend on a stale index
    return Retriever(CHUNKS_FILE)


def test_tokenize_keeps_section_numbers():
    assert "213.9" in tokenize("What does 213.9 say?")
    assert "402/2013" in tokenize("Regulation 402/2013")


@pytest.mark.parametrize(
    ("query", "expected_doc"),
    [
        ("What is the maximum speed on class 3 track?", "fra-49cfr-213"),
        ("How often must a locomotive be inspected?", "fra-49cfr-229"),
        ("blue signal protection for workers servicing equipment", "fra-49cfr-217-218"),
        ("random drug and alcohol testing requirements", "fra-49cfr-219"),
        ("What percentage of brakes must be operative at initial terminal?", "fra-49cfr-232"),
        ("Do we need a safety management system to operate trains in the EU?", "era-2016-798"),
        ("When is a change significant under the CSM risk assessment?", "era-402-2013"),
        ("roadway worker fouling the track protection", "fra-49cfr-214"),
    ],
)
def test_retrieval_finds_right_document(retriever, query, expected_doc):
    hits = retriever.search(query, k=5)
    assert hits, f"no hits for {query!r}"
    assert expected_doc in [h.chunk.doc_id for h in hits], (
        f"{expected_doc} not in top-5 for {query!r}: "
        f"{[h.chunk.doc_id for h in hits]}"
    )


def test_jurisdiction_filter(retriever):
    hits = retriever.search("safety management system requirements", k=8,
                            jurisdiction="EU-ERA")
    assert hits
    assert all(h.chunk.jurisdiction == "EU-ERA" for h in hits)


def test_top_k_respected(retriever):
    assert len(retriever.search("track inspection", k=3)) <= 3
