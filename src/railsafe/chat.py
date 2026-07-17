"""Interactive RAG chatbot over FRA / ERA rail safety regulations.

Usage:
    python -m railsafe.chat                       # interactive session
    python -m railsafe.chat --ask "question"      # one-shot question
    python -m railsafe.chat --retrieve-only ...   # show retrieval, skip the LLM

Requires ANTHROPIC_API_KEY (or an `ant auth login` profile) unless
--retrieve-only is used.
"""

from __future__ import annotations

import argparse
import sys

import anthropic

from .config import DEFAULT_TOP_K, MAX_TOKENS, MODEL
from .retriever import Hit, Retriever

SYSTEM_PROMPT = """\
You are a rail safety regulatory assistant. You answer compliance questions
about United States federal railroad regulations (FRA, Title 49 CFR) and
European Union railway safety law (ERA framework: the Railway Safety
Directive, common safety methods, and TSIs), using ONLY the regulation
excerpts provided in each question's <context> block.

Rules:
- Ground every substantive claim in the provided context and cite it inline
  using the bracketed source markers, e.g. [fra-49cfr-213 § 213.9] or
  [era-2016-798 Art. 9]. Cite the specific section, not just the document.
- If the context does not contain enough information to answer, say so
  plainly and name the regulation part that likely covers it rather than
  guessing at requirements.
- The US and EU regimes are structured differently; when a question spans
  both, answer each jurisdiction separately and note that the frameworks are
  not interchangeable.
- The corpus contains condensed summaries, not official legal text. End
  answers that state specific regulatory requirements with a one-line
  reminder to verify against the official source (eCFR / EUR-Lex) before
  making compliance decisions.
- You provide regulatory information, not legal advice.
- Answer in plain English, concise and directly responsive to the question.
"""


def format_context(hits: list[Hit]) -> str:
    blocks = []
    for hit in hits:
        c = hit.chunk
        blocks.append(
            f'<excerpt source="{c.doc_id}" citation="{c.citation}" '
            f'jurisdiction="{c.jurisdiction}" section="{c.section}" '
            f'url="{c.source_url}">\n{c.text}\n</excerpt>'
        )
    return "<context>\n" + "\n\n".join(blocks) + "\n</context>"


def build_user_turn(question: str, hits: list[Hit]) -> dict:
    return {
        "role": "user",
        "content": [
            {"type": "text", "text": format_context(hits)},
            {"type": "text", "text": f"Question: {question}"},
        ],
    }


def _move_cache_marker(messages: list[dict]) -> None:
    """Keep a single cache breakpoint on the newest user turn.

    The conversation prefix is cached incrementally across turns; older
    markers are stripped so we never exceed the 4-breakpoint limit.
    """
    for msg in messages:
        if isinstance(msg.get("content"), list):
            for block in msg["content"]:
                block.pop("cache_control", None)
    last = messages[-1]
    if isinstance(last.get("content"), list):
        last["content"][-1]["cache_control"] = {"type": "ephemeral"}


class RailSafetyChat:
    def __init__(
        self,
        model: str = MODEL,
        top_k: int = DEFAULT_TOP_K,
        jurisdiction: str | None = None,
    ):
        self.client = anthropic.Anthropic()
        self.retriever = Retriever()
        self.model = model
        self.top_k = top_k
        self.jurisdiction = jurisdiction
        self.messages: list[dict] = []

    def ask(self, question: str, stream_to=sys.stdout) -> str:
        hits = self.retriever.search(
            question, k=self.top_k, jurisdiction=self.jurisdiction
        )
        self.messages.append(build_user_turn(question, hits))
        _move_cache_marker(self.messages)

        with self.client.messages.stream(
            model=self.model,
            max_tokens=MAX_TOKENS,
            thinking={"type": "adaptive"},
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=self.messages,
        ) as stream:
            for text in stream.text_stream:
                if stream_to:
                    stream_to.write(text)
                    stream_to.flush()
            response = stream.get_final_message()

        if response.stop_reason == "refusal":
            self.messages.pop()  # don't poison the history
            notice = "\n[The model declined to answer this question.]\n"
            if stream_to:
                stream_to.write(notice)
            return notice

        answer = "".join(b.text for b in response.content if b.type == "text")
        # Keep only the text in history: thinking blocks from prior turns
        # don't need to be replayed for this conversational use, and the
        # context stays smaller.
        self.messages.append({"role": "assistant", "content": answer})
        return answer


def print_hits(hits: list[Hit]) -> None:
    if not hits:
        print("  (no matching chunks)")
        return
    for hit in hits:
        c = hit.chunk
        print(f"  {hit.score:6.2f}  [{c.jurisdiction}] {c.citation} — {c.section}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ask", help="ask a single question and exit")
    parser.add_argument("--k", type=int, default=DEFAULT_TOP_K, help="chunks to retrieve")
    parser.add_argument(
        "--jurisdiction",
        choices=["US-FRA", "EU-ERA"],
        help="restrict retrieval to one regulatory regime",
    )
    parser.add_argument("--model", default=MODEL)
    parser.add_argument(
        "--retrieve-only",
        action="store_true",
        help="print retrieved chunks without calling the model (no API key needed)",
    )
    args = parser.parse_args()

    if args.retrieve_only:
        retriever = Retriever()

        def handle(q: str) -> None:
            print_hits(retriever.search(q, k=args.k, jurisdiction=args.jurisdiction))

    else:
        chat = RailSafetyChat(
            model=args.model, top_k=args.k, jurisdiction=args.jurisdiction
        )

        def handle(q: str) -> None:
            chat.ask(q)
            print()

    if args.ask:
        handle(args.ask)
        return 0

    print("Rail safety compliance chatbot — FRA (49 CFR) & ERA (EU railway safety law)")
    print("Ask a question in plain English. Ctrl-D or 'quit' to exit.\n")
    while True:
        try:
            question = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not question:
            continue
        if question.lower() in {"quit", "exit"}:
            return 0
        try:
            handle(question)
        except anthropic.APIConnectionError:
            print("[network error reaching the Claude API — check connectivity and retry]")
        except anthropic.RateLimitError:
            print("[rate limited — wait a moment and retry]")
        except anthropic.APIStatusError as exc:
            print(f"[API error {exc.status_code}: {exc.message}]")


if __name__ == "__main__":
    sys.exit(main())
