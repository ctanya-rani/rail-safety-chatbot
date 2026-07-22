# Deployment Guide

Get your Rail Safety Chatbot live with a public URL in **<5 minutes**. Choose your platform and follow the steps — no deep technical knowledge needed.

**TL;DR:**
1. Sign up at [railway.app](https://railway.app) with GitHub
2. Click "Deploy from GitHub" and select `ctanya-rani/rail-safety-chatbot`
3. Wait 2–3 minutes → you get a live URL
4. (Optional) Add `ANTHROPIC_API_KEY` for full Claude synthesis

---

## ⚡ One-Click Deploy: Railway

Railway is the easiest — it auto-deploys from GitHub on every push.

### 1. Click to Deploy
Use this one-click link (after signing in to Railway with GitHub):
> [Deploy to Railway](https://railway.app/new?&template=https://github.com/ctanya-rani/rail-safety-chatbot)

Or manually:
1. Go to [railway.app/new](https://railway.app/new)
2. Select "Deploy from GitHub repo"
3. Find `ctanya-rani/rail-safety-chatbot` and click "Deploy"

Railway auto-detects the `Dockerfile` and `railway.json` configuration.

### 2. Wait for Build
The build takes 2–3 minutes. You'll see:
- ✅ Build in progress
- ✅ Deployment in progress
- ✅ Live with URL like `https://rail-safety-chatbot-prod-abc123.railway.app`

### 3. Configure (Optional)
For full Claude synthesis (instead of demo mode):
1. Open the Railway project dashboard
2. Go to "Variables"
3. Add `ANTHROPIC_API_KEY` → paste your key from [console.anthropic.com](https://console.anthropic.com)
4. Click "Redeploy" from the Deployments tab

Without an API key, the app works in **demo mode** — shows retrieved regulation excerpts only, no API needed.

### 4. Test
Open your Railway URL. You should see:
- Landing page with suggested compliance questions
- Click any question → see sources panel + answer (or excerpts in demo mode)
- Change jurisdiction (All / US-FRA / EU-ERA) to filter results

**Success!** Your app is live and shareable.

---

## Demo Mode vs. Full Mode

| Feature | Demo Mode | Full Mode |
|---------|-----------|-----------|
| **Requires API key?** | No | Yes |
| **Retrieval** | ✅ Working | ✅ Working |
| **Show sources** | ✅ Yes | ✅ Yes (with synthesis) |
| **Claude synthesis** | ✗ Shows top 3 excerpts | ✅ Adaptive thinking, citations |
| **Cost** | Free | ~$0.01–0.10 per question |
| **Multi-turn memory** | ✗ | ✅ |
| **Good for demo/resume?** | ✅ Yes | ✅ Yes |

**Recommendation:** Deploy in demo mode first to verify the app works. Add your API key later if you want full Claude synthesis.

---

## Troubleshooting

**"Build failed" error**
- Check that your GitHub repo is public or that Railway has access
- Verify `Dockerfile` and `railway.json` exist in the root
- Check Railway logs for build errors (usually missing dependencies)

**"Port already in use" or service won't start**
- Railway auto-assigns a port via the `$PORT` environment variable
- The `Dockerfile` uses `$PORT`, so this shouldn't happen
- If stuck: restart the deployment from the Railway dashboard

**"API key error / Rate limited"**
- Verify your `ANTHROPIC_API_KEY` is correct in Railway Variables
- Rate limits reset after 1 minute; wait and retry
- Check your Anthropic account for quota limits at [console.anthropic.com](https://console.anthropic.com)

**"Page loads but questions don't work"**
- If demo mode: check that sources appear in the sources panel
- If full mode: check Railway logs for Claude API errors
- Verify network tab in browser dev tools for `/api/chat` response

**App shows "no chunks indexed"**
- The index is built during Docker build; if it's missing, rebuild the deployment
- From Railway dashboard: go to Deployments → "Redeploy"

---

## Monitoring & Logs

Once deployed, monitor your app from the Railway dashboard:

1. **Logs** → See real-time requests and errors
2. **Metrics** → CPU, memory, request count
3. **Variables** → Update `ANTHROPIC_API_KEY` anytime (auto-redeploys)

Each deployment is isolated; redeploy any time by clicking "Redeploy" in the Deployments tab.

---

## Cost

**Railway free tier:**
- $5/month usage credits (covers most hobby projects)
- 100 free hours/month
- Enough for ~100–500 questions/month at demo mode (free) or ~20–50 at full mode

**Anthropic API:**
- Demo mode: $0
- Full mode: ~$0.003 per question (Opus 4.8 with adaptive thinking + prompt caching)
- Free tier available; check [console.anthropic.com](https://console.anthropic.com)

**Total cost:** Free to ~$10/month depending on usage.

---

## 🔄 Auto-Update & Auto-Deploy

With Railway + GitHub:
1. Make code changes locally
2. `git push` to `claude/rag-rail-safety-chatbot-ht57az`
3. Railway auto-builds and deploys (~2–3 min)
4. Your live URL updates automatically

No manual redeploy needed. This is perfect for portfolio — you can improve the app anytime and the link always shows the latest version.

---

## Portfolio & Resume

Use your deployed URL as a portfolio link:

**LinkedIn / Resume:**
> Rail Safety Chatbot — RAG application answering compliance questions over FRA and EU rail safety regulations. [Live demo](https://rail-safety-chatbot-prod-abc123.railway.app)

**GitHub README:**
```markdown
### Rail Safety Chatbot
- **Tech**: Python (FastAPI, BM25, Claude API, prompt caching)
- **Features**: RAG with citations, demo mode (no API key needed), multi-turn memory
- **Status**: Production-ready on Railway
- [Live demo](https://your-railway-url) | [Code](https://github.com/ctanya-rani/rail-safety-chatbot)
```

**Why this is portfolio-friendly:**
- ✅ Live URL you can share and test live
- ✅ Works without API key (demo mode impressive on its own)
- ✅ Demonstrates full-stack + ML concepts (retrieval, generation, streaming, caching)
- ✅ Real regulatory corpus (shows domain knowledge)
- ✅ Production-quality deployment

---

## Alternative Platforms

If you prefer not to use Railway:

### Fly.io
```bash
flyctl launch                              # creates fly.toml
flyctl secrets set ANTHROPIC_API_KEY=...  # optional
flyctl deploy
```
URL: `https://<app-name>.fly.dev`

### Render
1. Connect GitHub at [render.com](https://render.com)
2. New → "Web Service"
3. Select repo, set name/region
4. Add env var `ANTHROPIC_API_KEY` (optional)
5. Deploy

URL: `https://<service-name>.onrender.com`

Both have free tiers. **Railway is still simplest** for GitHub integration.

---

## Local Testing (Optional)

If you want to test the Docker build before deploying:

```bash
# Build the image
docker build -t rail-safety-chatbot .

# Run in demo mode (no API key needed)
docker run -p 8000:8000 rail-safety-chatbot

# Or run with your API key for full mode
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  rail-safety-chatbot
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## Architecture

The Docker container runs a single self-contained service:

```
┌─────────────────────────────────────────┐
│  Uvicorn Server (Port 8000)             │
├─────────────────────────────────────────┤
│  FastAPI App                            │
│  ├─ GET  / → index.html (single page)   │
│  ├─ POST /api/chat → SSE stream         │
│  └─ GET  /api/health → status           │
├─────────────────────────────────────────┤
│  BM25 Retriever                         │
│  └─ Searches chunks.jsonl               │
├─────────────────────────────────────────┤
│  Static Files (CSS, JS, images)         │
└─────────────────────────────────────────┘
```

**Why it's simple:**
- No separate backend/frontend servers
- No database (search index is pre-built at image build time)
- No CORS complexity (same domain)
- Stateless (can scale horizontally)

---

## Questions?

- **Deployment not starting?** Check Railway logs or re-read the troubleshooting section
- **Want to modify the app?** Push to your branch → Railway auto-redeploys
- **Need a custom domain?** Railway supports custom domains (paid feature)
- **Want to monitor usage?** Railway dashboard shows requests, errors, CPU/memory

