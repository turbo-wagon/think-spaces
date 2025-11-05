# 🧠 Think Spaces

**Think Spaces** is a personal development and creative exploration project — a system of persistent, thematic “cognitive rooms” where each space revolves around an idea, topic, or concept.  
Within each space, users can collect links, notes, images, and ideas, and connect AI agents or models to help think, create, or explore.

---

## 📄 Documentation
- [Intro](docs/INTRODUCTION.md)
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
- Pluggable LLM providers (`echo`, `openai`, `ollama`, `groq`) wired through a shared adapter interface.
- HTML UI for managing spaces, artifacts (including file uploads), and agents.
- Dynamic chat interface with keyboard shortcuts and interactive elements.

---

## ⚙️ Providers & API Keys

### Built-in Providers

| Provider | Type | Setup | Models |
|----------|------|-------|--------|
| **echo** | Testing | No setup needed | Echoes prompts back |
| **openai** | Cloud API | `export OPENAI_API_KEY="sk-..."` | GPT-4, GPT-4o-mini, etc. |
| **groq** | Cloud API (Free) | `export GROQ_API_KEY="gsk_..."` | Llama 3.1 (70B, 8B), Mixtral, Gemma 2 |
| **ollama** | Local | Install Ollama, optionally set `OLLAMA_BASE_URL` | Any Ollama model |

### Quick Start Examples

**Using .env file (Recommended):**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API keys
# GROQ_API_KEY=gsk_...
# OPENAI_API_KEY=sk_...

# Start the app (keys loaded automatically)
uvicorn app.main:app --reload
```

**Or use environment variables:**

**With Groq (Recommended for free, fast inference):**
```bash
# Get your free API key at https://console.groq.com
export GROQ_API_KEY="gsk_..."
uvicorn app.main:app --reload

# In the UI, create an agent with:
# - Provider: groq
# - Model: llama-3.1-70b-versatile
```

**With OpenAI:**
```bash
export OPENAI_API_KEY="sk-..."
uvicorn app.main:app --reload
```

**With Ollama (local):**
```bash
# Install and start Ollama
ollama serve
# In the UI, use provider: ollama, model: llama3.2
```

Additional providers can be added via the pluggable adapter pattern in `app/llm/`.

---
