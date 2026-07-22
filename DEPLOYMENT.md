# Deployment Guide

Deploy the Rail Safety Chatbot to a public URL using Railway, Fly.io, or Render. The entire application (backend + frontend + search index) is containerized and runs on Python.

## Quick Start: Railway

Railway is the simplest option — just connect your GitHub repository and Railway auto-deploys on every push.

### 1. Create a Railway Account
Visit [railway.app](https://railway.app) and sign up with your GitHub account.

### 2. Deploy from GitHub
1. Go to [railway.app/new](https://railway.app/new)
2. Select "Deploy from GitHub repo"
3. Search for and select `ctanya-rani/rail-safety-chatbot`
4. Click "Deploy"

Railway automatically detects the Dockerfile and builds the image.

### 3. Set Environment Variables
Once deployed, go to the project settings and add:
- `ANTHROPIC_API_KEY`: Your Anthropic API key (optional; without it, the app runs in demo mode showing retrieved excerpts only)

The app will be live at a auto-generated URL like `https://rail-safety-chatbot-prod-abc123.railway.app`.

### 4. Test the Deployment
Open the URL in your browser. The landing page should show suggested compliance questions as clickable chips. Click one to see the chat in action.

---

## Demo Mode vs. Full Mode

- **Demo mode** (no API key): Shows the top 3 retrieved regulation excerpts without Claude synthesis. Fully functional offline and demonstrable without credentials.
- **Full mode** (with API key): Uses Claude Opus 4.8 to synthesize answers from retrieved excerpts with inline citations, adaptive thinking, and multi-turn memory.

---

## Alternative: Fly.io

1. Install the [Fly CLI](https://fly.io/docs/getting-started/installing-flyctl/)
2. Sign up: `flyctl auth signup`
3. In the repo root: `flyctl launch`
4. Follow the prompts (app name, region, etc.)
5. Set the secret: `flyctl secrets set ANTHROPIC_API_KEY=sk-ant-...`
6. Deploy: `git push` or manually via `flyctl deploy`

Your app will be live at `https://<app-name>.fly.dev`.

---

## Alternative: Render

1. Connect your GitHub account at [render.com](https://render.com)
2. New → "Web Service"
3. Select the `rail-safety-chatbot` repo
4. Set name and region
5. Build command: (leave blank; Render auto-detects Dockerfile)
6. Start command: (leave blank; Render auto-detects)
7. Add environment variable `ANTHROPIC_API_KEY` in the "Environment" section
8. Deploy

Your app will be live at `https://<service-name>.onrender.com`.

---

## Local Testing

Before deploying, test the Docker build locally:

```bash
docker build -t rail-safety-chatbot .
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  rail-safety-chatbot
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) to test.

Omit the `-e ANTHROPIC_API_KEY=...` line to test demo mode.

---

## How It Works

The Dockerfile:
1. Starts from a lightweight Python 3.11 image
2. Installs dependencies from `pyproject.toml`
3. Copies corpus documents and source code
4. **Builds the search index** at build time (so startup is instant)
5. Starts a uvicorn server on port 8000

The server serves:
- `/` → Single-page chat UI (HTML)
- `/api/health` → Server status and index size
- `/api/chat` → Streams answers over Server-Sent Events
- `/static/*` → CSS, JavaScript, images

All traffic is on the same domain, so no CORS setup needed.

---

## Portfolio & Resume Links

Use the deployed URL as a portfolio link:
- **GitHub**: Add to your profile README or project links
- **Resume**: Link to the public app under "Projects" or "Portfolio"
- **Demo**: The default demo mode works without an API key — you can safely link to others without exposing credentials

Example portfolio entry:
> **Rail Safety Chatbot** — RAG application answering plain-English compliance questions over FRA (49 CFR) and EU rail safety regulations using BM25 retrieval and Claude. [Live demo](https://rail-safety-chatbot-prod.railway.app)

