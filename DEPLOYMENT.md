# Deployment

The whole app — API, UI, and retrieval index — is one container. Any host
that runs a Dockerfile will serve it.

## Railway

1. Sign in at [railway.app](https://railway.app) with GitHub.
2. **New Project → Deploy from GitHub repo →** `rail-safety-chatbot`.
3. Railway reads `railway.json`, builds the `Dockerfile`, and assigns a URL.
4. Optional: **Variables → New Variable →** `ANTHROPIC_API_KEY`. Adding it
   triggers a redeploy and switches the app out of demo mode.

## Fly.io

```bash
flyctl launch --no-deploy          # generates fly.toml; keep the Dockerfile
flyctl secrets set ANTHROPIC_API_KEY=sk-ant-...   # optional
flyctl deploy
```

Set `internal_port = 8000` in `fly.toml`, or leave `PORT` unset — the
container binds `$PORT` and defaults to 8000.

## Render

New → **Web Service** → connect the repo → Runtime **Docker**. Add
`ANTHROPIC_API_KEY` under Environment if you want synthesis. Render injects
`$PORT`, which the container already honours.

## Local

```bash
pip install -e ".[dev]"
python -m railsafe.ingest
uvicorn railsafe.server:app --reload   # http://127.0.0.1:8000
```

With Docker:

```bash
docker build -t rail-safety-chatbot .
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=sk-ant-... rail-safety-chatbot
```

## Demo mode vs. full mode

Demo mode is the default and needs no credentials: retrieval runs normally
and the top excerpts stream back verbatim, so the UI is fully usable. Set
`ANTHROPIC_API_KEY` to have Claude synthesise a cited answer from those same
excerpts. Everything else — sources panel, jurisdiction filter, multi-turn
history — behaves identically in both modes.

## Configuration

All optional; see `.env.example`. Nothing auto-loads a `.env` file, so export
these or set them in your host's variables UI.

| Variable | Default | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | unset | Enables synthesis; unset ⇒ demo mode |
| `RAILSAFE_MODEL` | `claude-opus-4-8` | Model used for synthesis |
| `RAILSAFE_TOP_K` | `6` | Excerpts retrieved per question |
| `RAILSAFE_MAX_TOKENS` | `16000` | Cap on answer length |
| `PORT` | `8000` | Bind port; set for you by all three hosts |

Blank values are treated as unset, so an empty variable left behind in a
dashboard won't crash the container.

## Cost

Demo mode costs nothing beyond hosting. Railway, Fly, and Render all have
free or trial tiers that comfortably cover a portfolio app.

In full mode each question sends the retrieved excerpts plus your
conversation so far, and the system prompt is cached across turns. For
current per-token rates see
[Anthropic pricing](https://www.anthropic.com/pricing); a smaller model via
`RAILSAFE_MODEL` cuts the cost substantially if traffic grows.

## Troubleshooting

**Build fails.** Check the host's build log first. Confirm `Dockerfile` and
`railway.json` are at the repo root and that the host has access to the repo.

**Container starts then exits, or the URL 502s.** Almost always a port
mismatch — the process must bind the host's `$PORT`. The bundled Dockerfile
does this via shell-form `CMD`; if you replaced it with an exec-form `CMD`,
`$PORT` will not be expanded.

**"No corpus documents found".** The index is built during `docker build` by
`RUN python -m railsafe.ingest`. If you changed the Dockerfile so `data/` is
copied after that step, or added `data/` to `.dockerignore`, the build has
nothing to index.

**Answers are excerpts, not prose.** That is demo mode — `ANTHROPIC_API_KEY`
isn't reaching the process. Confirm it's set on the service (not just
locally) and that the deploy restarted afterwards; `/api/health` reports
`demo_mode`.

**Rate limited / API errors.** Surfaced in the chat as an error message and
in the service logs. Check quota at
[console.anthropic.com](https://console.anthropic.com).

## Updating

Push to the branch the host is watching; Railway, Render, and Fly (with
GitHub integration) rebuild automatically. Corpus edits under `data/corpus/`
are picked up on the next build, since the index is rebuilt in the image.
