"use strict";

const chatEl = document.getElementById("chat");
const emptyState = document.getElementById("empty-state");
const form = document.getElementById("composer");
const input = document.getElementById("question");
const sendBtn = document.getElementById("send");
const sourcesEl = document.getElementById("sources");
const sourcesHint = document.getElementById("sources-hint");

let jurisdiction = null;
let history = []; // [{role, content}] plain-text turns sent back to the server
let busy = false;

// ---------- helpers ----------

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

// Minimal renderer: paragraphs, **bold**, and [citation] highlighting.
function renderText(raw) {
  let html = escapeHtml(raw);
  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\[([^\]\n]{3,80}?)\]/g, '<span class="cite">[$1]</span>');
  return html
    .split(/\n{2,}/)
    .map((p) => `<p>${p.replace(/\n/g, "<br>")}</p>`)
    .join("");
}

function addMessage(cls, html) {
  if (emptyState) emptyState.remove();
  const div = document.createElement("div");
  div.className = `msg ${cls}`;
  div.innerHTML = html;
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
  return div;
}

function renderSources(sources) {
  sourcesEl.innerHTML = "";
  sourcesHint.hidden = sources.length > 0;
  const maxScore = Math.max(...sources.map((s) => s.score), 1);
  for (const s of sources) {
    const card = document.createElement("div");
    card.className = "source-card";
    const isFra = s.jurisdiction === "US-FRA";
    card.innerHTML = `
      <div class="source-head">
        <span class="jbadge ${isFra ? "jbadge-fra" : "jbadge-era"}">${isFra ? "FRA" : "ERA"}</span>
        <span class="source-cite">${escapeHtml(s.citation)}</span>
      </div>
      <div class="source-section">${escapeHtml(s.section)}</div>
      <div class="score-bar"><div class="score-fill" style="width:${Math.round((s.score / maxScore) * 100)}%"></div></div>
      <div class="source-preview">${escapeHtml(s.preview)}…</div>
      ${s.url ? `<a href="${escapeHtml(s.url)}" target="_blank" rel="noopener">official text ↗</a>` : ""}`;
    sourcesEl.appendChild(card);
  }
}

// ---------- chat flow ----------

async function ask(question) {
  if (busy || !question.trim()) return;
  busy = true;
  sendBtn.disabled = true;
  input.value = "";

  addMessage("msg-user", renderText(question));
  const botEl = addMessage("msg-bot typing", "Consulting the regulations");

  let answer = "";
  try {
    const resp = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: question, history, jurisdiction }),
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split("\n\n");
      buffer = events.pop(); // keep incomplete tail
      for (const evt of events) {
        const line = evt.trim();
        if (!line.startsWith("data:")) continue;
        let payload;
        try {
          payload = JSON.parse(line.slice(5));
        } catch (e) {
          console.error("Failed to parse SSE event:", e, line);
          continue;
        }
        if (payload.type === "sources" && payload.sources) {
          renderSources(payload.sources);
        } else if (payload.type === "delta" && payload.text !== undefined) {
          answer += payload.text;
          botEl.classList.remove("typing");
          botEl.innerHTML = renderText(answer);
          chatEl.scrollTop = chatEl.scrollHeight;
        } else if (payload.type === "error" && payload.message) {
          botEl.classList.remove("typing");
          botEl.classList.add("msg-error");
          botEl.innerHTML = renderText(payload.message);
        } else if (payload.type === "done") {
          botEl.classList.remove("typing");
        }
      }
    }
    if (answer) {
      history.push({ role: "user", content: question });
      history.push({ role: "assistant", content: answer });
    }
  } catch (err) {
    botEl.classList.remove("typing");
    botEl.classList.add("msg-error");
    botEl.textContent = `Request failed: ${err.message}`;
  } finally {
    busy = false;
    sendBtn.disabled = false;
    input.focus();
  }
}

// ---------- wiring ----------

form.addEventListener("submit", (e) => {
  e.preventDefault();
  ask(input.value);
});

document.querySelectorAll(".chip").forEach((chip) =>
  chip.addEventListener("click", () => ask(chip.textContent))
);

document.querySelectorAll(".seg").forEach((seg) =>
  seg.addEventListener("click", () => {
    document.querySelectorAll(".seg").forEach((s) => s.classList.remove("active"));
    seg.classList.add("active");
    jurisdiction = seg.dataset.j || null;
  })
);

fetch("/api/health")
  .then((r) => r.json())
  .then((h) => {
    document.getElementById("demo-badge").hidden = !h.demo_mode;
    document.getElementById("chunk-badge").textContent =
      `${h.chunks} indexed sections`;
  })
  .catch(() => {});

input.focus();
