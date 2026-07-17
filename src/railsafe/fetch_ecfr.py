"""Fetch full FRA regulation text from the eCFR API into the corpus.

The bundled corpus contains condensed summaries. This script downloads the
official, current full text of 49 CFR parts from the public eCFR API and
writes one markdown document per part into data/corpus/fetched/, section by
section. Re-run `python -m railsafe.ingest` afterwards to reindex.

Usage:
    python -m railsafe.fetch_ecfr 213 214 229        # specific parts
    python -m railsafe.fetch_ecfr                    # default safety parts
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

from .config import CORPUS_DIR

ECFR_API = "https://www.ecfr.gov/api/versioner/v1"
DEFAULT_PARTS = [213, 214, 217, 218, 219, 229, 232, 240, 242]
FETCHED_DIR = CORPUS_DIR / "fetched"


def latest_issue_date(session: requests.Session) -> str:
    resp = session.get(f"{ECFR_API}/titles.json", timeout=60)
    resp.raise_for_status()
    for title in resp.json()["titles"]:
        if title["number"] == 49:
            return title["up_to_date_as_of"]
    raise RuntimeError("Title 49 not found in eCFR titles listing")


def fetch_part_xml(session: requests.Session, date: str, part: int) -> ET.Element:
    resp = session.get(
        f"{ECFR_API}/full/{date}/title-49.xml",
        params={"part": str(part)},
        timeout=120,
    )
    resp.raise_for_status()
    return ET.fromstring(resp.content)


def _text_of(node: ET.Element) -> str:
    return re.sub(r"\s+", " ", "".join(node.itertext())).strip()


def part_to_markdown(root: ET.Element, part: int, date: str) -> str:
    part_div = root.find(f".//DIV5[@N='{part}']")
    if part_div is None:
        raise RuntimeError(f"Part {part} not present in response")
    head = part_div.find("HEAD")
    part_title = _text_of(head) if head is not None else f"Part {part}"

    lines = [
        "---",
        f"id: fra-49cfr-{part}-full",
        f"title: {part_title} (49 CFR Part {part}, official text)",
        "jurisdiction: US-FRA",
        f"citation: 49 CFR Part {part}",
        f"source_url: https://www.ecfr.gov/current/title-49/part-{part}",
        "doc_type: official",
        "---",
        "",
        f"> Official eCFR text as of {date}.",
        "",
    ]
    for section in part_div.iter("DIV8"):  # DIV8 nodes are individual sections
        head = section.find("HEAD")
        heading = _text_of(head) if head is not None else section.get("N", "")
        lines.append(f"## {heading}")
        lines.append("")
        for para in section.findall("P"):
            text = _text_of(para)
            if text:
                lines.append(text)
                lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    parts = [int(a) for a in argv] if argv else DEFAULT_PARTS

    FETCHED_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    try:
        date = latest_issue_date(session)
    except requests.RequestException as exc:
        print(f"Cannot reach the eCFR API ({exc}).", file=sys.stderr)
        print("Check network access to www.ecfr.gov and retry.", file=sys.stderr)
        return 1
    print(f"eCFR title 49 current as of {date}")

    for part in parts:
        print(f"Fetching 49 CFR part {part} ...", end=" ", flush=True)
        try:
            root = fetch_part_xml(session, date, part)
            markdown = part_to_markdown(root, part, date)
        except (requests.RequestException, RuntimeError, ET.ParseError) as exc:
            print(f"FAILED ({exc})")
            continue
        out = FETCHED_DIR / f"fra-49cfr-{part}-full.md"
        out.write_text(markdown, encoding="utf-8")
        print(f"wrote {out.relative_to(CORPUS_DIR.parent.parent)}")

    print("Done. Re-run `python -m railsafe.ingest` to rebuild the index.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
