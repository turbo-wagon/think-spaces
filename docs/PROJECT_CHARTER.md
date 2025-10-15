

## 🧭 Overview

**Think Spaces** is a personal cognitive platform for exploring ideas through intelligent, multimodal "rooms."  
Each space revolves around a topic or concept — a place to gather links, notes, text, images, and conversations — and to collaborate with pluggable AI agents that help you think, reflect, and create.  
The system evolves with you over time, building memory and insight unique to each space.

---

## 🎯 Purpose & Vision

- To create an environment where **human and artificial intelligence co-think**.
- To reimagine bookmarks, notes, and chats as **living cognitive ecosystems**.
- To help individuals **return to their thoughts**, not as static notes, but as spaces that continue thinking with them.
- To honor **all forms of intelligence** — human, artificial, collective, environmental — as collaborators in cognition.

---

## 🌍 Scope

### In Scope (MVP)
- A single persistent Think Space (no multi-space UI yet).
- Add and view text, links, and images (artifacts).
- One LLM-powered conversational agent (GPT-4o-mini).
- Supabase storage for artifacts and chat interactions.
- Context memory via vector embeddings (pgvector).
- Visual theming per space.
- Free-tier deploy (Vercel + Supabase + OpenAI API).

### Out of Scope (Future Phases)
- Multi-user or shared spaces.
- Multi-agent orchestration.
- Graph-based visualization.
- Environmental or sensor-based input.
- Public APIs or sharing.

---

## ✨ Design Principles

| Principle | Description |
|------------|--------------|
| **Spatial Cognition** | Each topic is a “room” of thought — not a list or folder. |
| **Intelligence Pluralism** | Human, AI, and environment all contribute to thought. |
| **Persistence of Context** | A space remembers; it accumulates meaning over time. |
| **Modular Intelligence** | Agents are plugins, not monoliths. |
| **Human Reflection** | Encourage journaling and meta-thinking over automation. |
| **Aesthetic Resonance** | Each space has mood and atmosphere. |

---

## 🧩 Core Entities

User
└── Think Spaces
├── Artifacts (inputs & outputs)
├── Agents (LLMs, image generators, critics, etc.)
└── Interactions (sessions or reasoning threads)

pgsql
Copy code

- **Artifacts:** Notes, links, images, agent outputs.  
- **Agents:** Modular reasoning tools (start with one general agent).  
- **Interactions:** Conversations and reasoning threads.  
- **Memory Graph:** Vector embeddings that connect related content.

---

## ⚙️ Functional Requirements (MVP)

### 1. Think Space Core
| ID | Requirement |
|----|--------------|
| TS-01 | Create / open a Think Space. |
| TS-02 | Load all artifacts associated with the space. |
| TS-03 | Store metadata (name, theme, mood). |

### 2. Artifact Management
| ID | Requirement |
|----|--------------|
| AR-01 | Add text artifacts (notes, ideas). |
| AR-02 | Add link artifacts with fetched previews. |
| AR-03 | Add image artifacts (upload or embed). |
| AR-04 | Display artifacts as cards or list. |
| AR-05 | Persist artifacts with embeddings. |

### 3. AI Agent Interaction
| ID | Requirement |
|----|--------------|
| AG-01 | Chat with a single agent in context. |
| AG-02 | Retrieve relevant artifacts using embeddings. |
| AG-03 | Generate responses (summaries, ideas). |
| AG-04 | Store chat messages as interactions. |
| AG-05 | Save agent outputs as artifacts (optional). |

### 4. Memory and Context
| ID | Requirement |
|----|--------------|
| ME-01 | Generate embeddings for each artifact. |
| ME-02 | Retrieve artifacts by semantic similarity. |
| ME-03 | Update embeddings on new inputs. |

### 5. User Interface
| ID | Requirement |
|----|--------------|
| UI-01 | Minimal dashboard to enter a Think Space. |
| UI-02 | Input form to add text, links, and uploads. |
| UI-03 | Chat interface with message streaming. |
| UI-04 | Visual theming per space. |
| UI-05 | Responsive design for desktop and tablet. |

---

## 🧱 Non-Functional Requirements

| Category | Requirement |
|-----------|--------------|
| **Performance** | Sub-3s agent responses for small prompts; <2s artifact load. |
| **Scalability** | Support 100 artifacts in Supabase free tier. |
| **Cost** | Stay within free usage tiers (<$5/mo typical). |
| **Security** | Supabase Auth (optional) for user isolation. |
| **Privacy** | All data private by default. |
| **Maintainability** | Modular TypeScript, minimal dependencies. |
| **Extensibility** | Easy to add artifact types or agents later. |

---

## 🧰 Technical Stack

| Layer | Tool | Notes |
|-------|------|-------|
| **Frontend** | Next.js 15 (App Router) | Modern React framework |
| **UI** | Tailwind CSS + shadcn/ui | Elegant minimal styling |
| **Database** | Supabase (Postgres + pgvector) | Data + embeddings |
| **AI API** | OpenAI GPT-4o-mini | Contextual responses |
| **Auth (Optional)** | Supabase Auth | Private user spaces |
| **Hosting** | Vercel (frontend), Supabase (backend) | Fully free-tier deploy |

---

## 🧩 Data Schema (Simplified)

spaces
├── id (uuid)
├── name
├── description
├── theme
├── created_at
└── updated_at

artifacts
├── id (uuid)
├── space_id (fk)
├── type (text/link/image)
├── content
├── metadata (jsonb)
├── embedding (vector)
├── created_at

interactions
├── id (uuid)
├── space_id (fk)
├── input
├── output
├── agent
├── created_at

yaml
Copy code

---

## 🚀 Implementation Roadmap

| Phase | Goal | Description |
|--------|------|-------------|
| **Week 1** | Setup + Schema | Create Supabase project, tables, connect to Next.js. |
| **Week 2** | Artifact Input | Add text/link/image upload + embedding logic. |
| **Week 3** | Chat Agent | Implement context retrieval + chat UI. |
| **Week 4** | Polish + Deploy | Add theme/mood layer, deploy to Vercel. |

---

## ✅ Success Criteria
- A live MVP on Vercel with Supabase backend.
- Ability to add and view artifacts.
- Chat agent that recalls previous ideas.
- Per-space memory that genuinely “feels alive.”
- System feels meditative and creative — not utilitarian.

---

## 🪞 Future Roadmap (Post-MVP)

| Phase | Feature | Description |
|--------|----------|-------------|
| **2** | Multiple Spaces | User can manage multiple topics. |
| **3** | Multi-Agent System | Add Critic, Synthesizer, Visualizer roles. |
| **4** | Graph UI | 2D or 3D spatial visualization of artifacts. |
| **5** | Shared Spaces | Collaborative co-thinking. |
| **6** | Ambient Intelligence | Time, emotion, environment integration. |
| **7** | Open API | External integrations and plugins. |

---

## 💡 Guiding Quote

> “A Think Space is not where you store ideas.  
> It’s where your ideas store *you* —  
> remembering, reflecting, and growing with your thought.”  

---

© 2025 — *Think Spaces: An experiment in inclusive cognition.*

