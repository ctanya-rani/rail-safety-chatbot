"""Web front end for the rail safety chatbot.

FastAPI backend that serves the static chat UI and streams answers over
Server-Sent Events. Each response begins with a `sources` event carrying the
retrieved excerpts (rendered as citation cards in the UI), followed by
`delta` text events and a final `done` event.

If no Anthropic credential is configured the server runs in demo mode:
retrieval still works and the top excerpts are streamed back verbatim, so
the UI is fully demoable without an API key.

Usage:
    uvicorn railsafe.server:app --reload      # http://127.0.0.1:8000
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import anthropic
from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .chat import SYSTEM_PROMPT, build_user_turn
from .config import DEFAULT_TOP_K, MAX_TOKENS, MODEL
from .retriever import Hit, Retriever

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Rail Safety Chatbot")

_retriever: Retriever | None = None


def get_retriever() -> Retriever:
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever


def demo_mode() -> bool:
    return not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = Field(default_factory=list)  # [{role, content}] plain text
    jurisdiction: str | None = None  # "US-FRA" | "EU-ERA" | None
    k: int = DEFAULT_TOP_K


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _source_payload(hits: list[Hit]) -> dict:
    return {
        "type": "sources",
        "sources": [
            {
                "doc_id": h.chunk.doc_id,
                "citation": h.chunk.citation,
                "jurisdiction": h.chunk.jurisdiction,
                "section": h.chunk.section,
                "url": h.chunk.source_url,
                "score": round(h.score, 2),
                "preview": h.chunk.text[:280],
            }
            for h in hits
        ],
    }


def _demo_answer(hits: list[Hit]):
    yield _sse(
        {
            "type": "delta",
            "text": (
                "**Demo mode** — no Anthropic API key is configured, so here are "
                "the most relevant regulation excerpts the retriever found. "
                "Set `ANTHROPIC_API_KEY` to get synthesized answers.\n\n"
            ),
        }
    )
    for h in hits[:3]:
        c = h.chunk
        yield _sse(
            {
                "type": "delta",
                "text": f"**[{c.doc_id} — {c.section}]** ({c.citation})\n{c.text}\n\n",
            }
        )
    yield _sse({"type": "done", "demo": True})


def _model_answer(req: ChatRequest, hits: list[Hit]):
    client = anthropic.Anthropic()
    messages = [
        {"role": m["role"], "content": m["content"]}
        for m in req.history
        if m.get("role") in ("user", "assistant") and m.get("content")
    ]
    messages.append(build_user_turn(req.message, hits))
    try:
        with client.messages.stream(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            thinking={"type": "adaptive"},
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                yield _sse({"type": "delta", "text": text})
            response = stream.get_final_message()
        if response.stop_reason == "refusal":
            yield _sse({"type": "delta", "text": "\n[The model declined to answer this question.]"})
        yield _sse({"type": "done", "demo": False})
    except anthropic.APIConnectionError:
        yield _sse({"type": "error", "message": "Could not reach the Claude API — check connectivity."})
    except anthropic.RateLimitError:
        yield _sse({"type": "error", "message": "Rate limited — wait a moment and retry."})
    except anthropic.APIStatusError as exc:
        yield _sse({"type": "error", "message": f"API error {exc.status_code}: {exc.message}"})


@app.get("/api/health")
def health() -> dict:
    retriever = get_retriever()
    return {
        "status": "ok",
        "demo_mode": demo_mode(),
        "chunks": len(retriever.chunks),
        "model": MODEL,
    }


@app.post("/api/chat")
def chat(req: ChatRequest) -> StreamingResponse:
    retriever = get_retriever()
    hits = retriever.search(req.message, k=req.k, jurisdiction=req.jurisdiction)

    def event_stream():
        yield _sse(_source_payload(hits))
        if not hits:
            yield _sse(
                {
                    "type": "delta",
                    "text": "I couldn't find anything relevant in the indexed "
                    "regulations for that question. Try rephrasing, or ask about "
                    "FRA (49 CFR) or EU railway safety topics.",
                }
            )
            yield _sse({"type": "done", "demo": demo_mode()})
            return
        if demo_mode():
            yield from _demo_answer(hits)
        else:
            yield from _model_answer(req, hits)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
