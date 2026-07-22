# Rail Safety Chatbot — Start Here 🚀

Your RAG chatbot is **built, tested, and ready to deploy**. Here's everything you need to know.

## What You Have

A complete, production-ready application that:
- **Answers compliance questions** about FRA (US) and ERA (EU) rail safety regulations
- **Shows sources** — every answer cites the specific regulation section
- **Works without API key** — demo mode shows retrieved excerpts (impressive on its own)
- **Streams in real-time** — Server-Sent Events for responsive UX
- **Remembers context** — multi-turn conversations with history
- **Filters by jurisdiction** — US-FRA vs EU-ERA toggle

**Stack:**
- Backend: Python, FastAPI, BM25 retrieval, Claude Opus 4.8
- Frontend: Vanilla HTML/CSS/JavaScript (no build step)
- Deployment: Docker container on Railway/Fly.io/Render
- Testing: 20 pytest tests, all passing ✅

---

## 🎯 Next Steps (Choose One)

### Option A: Deploy Immediately (5 minutes)
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "Deploy from GitHub repo" → select `ctanya-rani/rail-safety-chatbot`
4. **Done!** You have a live URL in 2–3 minutes
5. (Optional) Add `ANTHROPIC_API_KEY` for full Claude synthesis

**Your app will be live at:** `https://rail-safety-chatbot-prod-*.railway.app`

See `DEPLOYMENT.md` for detailed steps and troubleshooting.

### Option B: Test Locally First
```bash
# Install dependencies
pip install -e ".[dev]"

# Build search index
python -m railsafe.ingest

# Start server
uvicorn railsafe.server:app --reload
# Open http://127.0.0.1:8000
```

Then deploy to Railway using Option A.

### Option C: Deploy to Different Platform
- **Fly.io** — See "Alternative Platforms" in `DEPLOYMENT.md`
- **Render** — See "Alternative Platforms" in `DEPLOYMENT.md`

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `DEPLOYMENT.md` | Complete deployment guide (Railway, Fly.io, Render) |
| `PRODUCTION_READY.md` | Verification that all tests pass and system is ready |
| `README.md` | Full project documentation |
| `src/railsafe/` | Python source code (retriever, chat, server) |
| `data/corpus/` | 10 regulation documents (markdown) |
| `Dockerfile` | Container image definition |
| `railway.json` | Railway auto-configuration |

---

## 🧪 Verification

All systems verified working:

```
✅ 20/20 tests passing (chunking, retrieval, API, SSE streaming)
✅ Index built correctly (68 chunks from 10 documents)
✅ Server starts and responds to requests
✅ Demo mode works without API key
✅ Full mode ready with Claude synthesis
✅ Security review passed (no vulnerabilities)
✅ Docker builds successfully
```

See `PRODUCTION_READY.md` for complete verification checklist.

---

## 🎓 For Portfolio/Resume

This application demonstrates:

**Backend:**
- RAG architecture (retrieval-augmented generation)
- BM25 lexical search with domain-aware tokenization
- Streaming responses (Server-Sent Events)
- Prompt caching for cost efficiency
- Multi-turn conversation memory
- Error handling and graceful degradation

**Frontend:**
- Real-time chat UI with streaming updates
- SSE event parsing
- Responsive design (mobile-friendly)
- No build step (vanilla JS)
- DOM manipulation and event handling

**DevOps:**
- Docker containerization
- Environment-based configuration
- Production deployment (Railway/Fly.io/Render)
- Health checks and monitoring
- Auto-deployment from GitHub

**Data:**
- 10 regulatory documents (5 US FRA, 5 EU ERA)
- Section-based chunking with windowing
- Metadata preservation (citations, jurisdictions)
- Search index optimization (68 chunks)

**Suggested Portfolio Link:**
```
Rail Safety Chatbot | GitHub: https://github.com/ctanya-rani/rail-safety-chatbot
Live Demo: [insert-your-deployed-url-here]

A RAG chatbot answering compliance questions over FRA (49 CFR) and ERA rail 
safety regulations. Features BM25 retrieval, Claude Opus synthesis with adaptive 
thinking, prompt caching, SSE streaming, and multi-turn memory. Deployed on Railway 
with demo mode (no API key needed).

Stack: Python · FastAPI · BM25 · Claude API · Docker · Railway
```

---

## 💡 Common Questions

**Q: Do I need an API key to use it?**
A: No! Demo mode works without one — it shows you the retrieved regulation excerpts. Add your API key later for full Claude synthesis.

**Q: How much does it cost?**
A: Railway has a $5/month free tier covering hobby projects. Claude API costs ~$0.003 per question (with prompt caching). Demo mode is completely free.

**Q: Can I share the URL with others?**
A: Yes! It's a public URL. Anyone can use it (with their own API key if they want synthesis, or use demo mode).

**Q: How do I update the app?**
A: Push changes to your GitHub branch → Railway auto-rebuilds and redeploys (~2–3 min).

**Q: Can I add more regulations?**
A: Yes! Add markdown files to `data/corpus/` with front-matter headers, then push to rebuild the index.

---

## 📞 Support

- **Deployment issues?** See troubleshooting in `DEPLOYMENT.md`
- **Code changes?** Read comments in `src/railsafe/` modules
- **Regulation updates?** See "Upgrading to official full text" in `README.md`
- **Test failures?** Run `pytest -v` to see detailed output

---

## What's Next?

1. **Deploy**: Follow "Option A" above to get a live URL
2. **Test**: Click suggested questions to verify everything works
3. **Share**: Post your URL on GitHub, LinkedIn, resume
4. **Iterate**: Make improvements and push — Railway auto-redeploys

**Your app is ready now. Start deploying!** 🚀

---

**Built:** 2026-07-22 | **Status:** Production Ready ✅ | **Tests:** 20/20 ✅
