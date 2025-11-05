# 🗺️ Project Roadmap — Think Spaces

## 🎯 Overview
This roadmap outlines the development milestones for the **Think Spaces** project — from concept validation to MVP release.  
Each phase builds upon the previous one, enabling iterative growth and integration of AI-driven capabilities.

---

## 🧩 Phase 1: Foundation — MVP Architecture
**Goal:** Establish a minimal viable framework.  
**Target:** Month 1  

**Tasks**
- [x] Create project charter and design document  
- [x] Set up GitHub repo and folder structure  
- [x] Implement basic FastAPI backend  
- [x] Add SQLite metadata storage  
- [x] Define `Space`, `Artifact`, and `Agent` models

---

## 🧠 Phase 2: Intelligence — Agent Integration
**Goal:** Connect LLMs and multimodal components.
**Target:** Month 2

**Tasks**
- [x] Add `/spaces`, `/artifacts`, and `/agents` API endpoints
- [x] Connect pluggable LLM providers (echo, OpenAI, Ollama)
- [x] Implement simple "context-aware thinking" agent
- [ ] Store embeddings in local vector DB (PGVector or FAISS)
  - **Note:** Embeddings are a prerequisite for Phase 6 (Bloom Features)

---

## 🪞 Phase 3: Interface — User Experience Layer
**Goal:** Build an interactive web UI.  
**Target:** Month 3  

**Tasks**
- [x] Create lightweight frontend (Jinja templates)  
- [x] Enable space creation, artifact management, file upload, and space memory  
- [x] Integrate agent chat UI with history within each space  
- [ ] Add local persistence (browser or IndexedDB)

---

## 🌍 Phase 4: Reflection — Memory and Evolution
**Goal:** Extend spaces with long-term memory and versioning.  
**Target:** Month 4  

**Tasks**
- [ ] Implement “space evolution” timeline  
- [ ] Versioning and memory summaries  
- [ ] Visual knowledge map (Mermaid or D3.js)  

---

## ✅ Phase 5: Polish & Publish
**Goal:** Prepare public release or demo.
**Target:** Month 5

**Tasks**
- [x] Refine UX/UI (dynamic chat, keyboard shortcuts, interactive elements)
- [ ] Deploy to Vercel or Azure
- [ ] Document usage and contribution guide

---

## 🌸 Phase 6: Bloom — Memory Phenomenology Layer
**Goal:** Transform spaces into living cognitive environments with temporal awareness.
**Target:** Future / Backlog
**Status:** Specification complete, pending implementation
**Detailed Spec:** [BLOOM_FEATURES.md](./BLOOM_FEATURES.md)

**Overview:**
The Bloom system adds a "memory phenomenology" layer that surfaces hidden connections, tracks temporal decay, and manifests the sensory qualities of accumulated knowledge. Inspired by obsidian glass crystallizing from heat, blooms emerge when artifacts reach critical mass and connection density.

**Core Features:**

### Phase 6.1: Temporal Foundation
- [ ] Artifact temperature tracking (hot → warm → cool → frost)
- [ ] Thermal decay algorithm based on access patterns
- [ ] Space entropy calculation (fragmentation, isolation, temporal drift)
- [ ] API endpoints for thermal mapping and frosted artifact detection

### Phase 6.2: Connection Mapping & Bloom Detection
- [ ] Semantic connection detection via vector embeddings
- [ ] ArtifactConnection database table with strength scoring
- [ ] Bloom detection algorithm (density, activity, entropy thresholds)
- [ ] Bloom database model with auto-generated insights

### Phase 6.3: Visual Manifestation
- [ ] Thermal heatmap overlay showing artifact temperature states
- [ ] Force-directed graph visualization of artifact connections
- [ ] Bloom highlighting with obsidian-like visual effects
- [ ] Animated "breathing" blooms as artifacts interact

### Phase 6.4: AI-Powered Insights
- [ ] BloomAnalyzer agent for natural language summaries
- [ ] Core insight extraction connecting bloom artifacts
- [ ] Frost recovery suggestions for dormant content
- [ ] Cross-space bloom detection for unexpected connections

### Phase 6.5: Sensory Metadata
- [ ] Emotional tagging system (curiosity, clarity, tension, urgency, nostalgia)
- [ ] Sensory notes for artifact "feel" and atmosphere
- [ ] Color-coded emotional landscape visualization
- [ ] Optional audio ambience based on space temperature

### Phase 6.6: Bloom-Driven Workflows
- [ ] Automatic space curation via bloom-based splitting
- [ ] AI-suggested reorganization when entropy > 80
- [ ] Cross-space bloom scanning and bridge suggestions
- [ ] Frost revival weekly digests with contextual prompts

**Dependencies:**
- Vector embeddings system (Phase 2)
- Background job scheduler (celery or APScheduler)
- Graph visualization library (D3.js or vis.js)
- Enhanced agent system for bloom analysis

**Success Metrics:**
- User engagement with bloom suggestions
- Reduction in space entropy scores
- Frequency of frost artifact revivals
- User-reported "unexpected discoveries"

**Open Questions:**
- Privacy: Should cross-space blooms be opt-in?
- Cognitive load: How many bloom notifications before noise?
- Customization: Per-space vs. global decay rate control?
- AI tone: Tentative suggestions vs. declarative insights?

---

**Roadmap Status:** Phases 1-3 substantially complete. Phase 4-5 in progress. Phase 6 (Bloom) in backlog pending resource allocation.
