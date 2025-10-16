# 🧠 Think Spaces

**Think Spaces** is a personal development and creative exploration project — a system of persistent, thematic “cognitive rooms” where each space revolves around an idea, topic, or concept.  
Within each space, users can collect links, notes, images, and ideas, and connect AI agents or models to help think, create, or explore.

---

## 📄 Documentation
- [Project Charter](docs/CHARTER.md)
- [System Design](docs/SYSTEM_DESIGN.md)
- [Roadmap](docs/ROADMAP.md)
- [Requirements](docs/REQUIREMENTS.md)

---

## 🚀 Vision
Build a framework that combines **human intelligence** and **machine intelligence** within immersive, topic-based environments — “spaces to think”.

---

## ✨ Current Capabilities
- FastAPI backend with SQLite persistence for spaces, artifacts, and agents.
- Automatic artifact summaries and keyword tags to enrich agent context.
- Pluggable LLM providers (`echo`, `openai`, `ollama`) wired through a shared adapter interface.
- HTML UI for managing spaces, artifacts (including file uploads), and agents.

---

## ⚙️ Providers & API Keys
- The backend ships with an `echo` provider for local testing (no external calls).
- To enable OpenAI models, set `OPENAI_API_KEY` in your environment before starting the app:

```bash
export OPENAI_API_KEY="sk-..."
uvicorn app.main:app --reload
```

- To use Ollama locally, install it and start the service (defaults to `http://localhost:11434`). You can override the endpoint with `OLLAMA_BASE_URL`.

- Additional providers can be added via the pluggable adapter pattern in `app/llm/`.

---
