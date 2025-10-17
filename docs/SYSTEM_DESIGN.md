# 🧩 SYSTEM_DESIGN.md — Think Spaces (MVP)

> **Goal:** A minimal-yet-magical personal "Think Space" you can enter, drop artifacts (text, links, images), and converse with an agent that remembers and builds on your thoughts — all on free tiers.

---

## 1) Architecture Overview

### 1.1 High-Level Diagram

```
[Browser / Next.js UI]
   ├─ Add Artifact (text/link/image)
   ├─ View Artifacts (cards/list)
   └─ Chat with Agent (streaming)
        │
        ▼
[Vercel-hosted Next.js App]
   ├─ Server Actions / Route Handlers (Edge/Node)
   │   ├─ /api/artifacts  (create, list)
   │   ├─ /api/ingest     (scrape + embed link)
   │   ├─ /api/chat       (RAG: retrieve + generate)
   │   └─ /api/upload     (signed URLs to Supabase Storage)
   └─ Services Layer
       ├─ Supabase Client (Postgres + pgvector + Storage)
       ├─ Embedding Client (provider adapter)
       └─ LLM Client (pluggable provider adapter)
        │
        ▼
[Supabase]
   ├─ Postgres (tables: spaces, artifacts, interactions)
   ├─ pgvector (semantic memory per space)
   ├─ Storage (images)
   └─ (Optional) Auth + RLS
```

### 1.2 Key Design Tenets

- **Spatial Cognition:** Per-space context and mood.
    
- **RAG Core:** Artifacts → embeddings → top‑k retrieval for agent context.
    
- **Minimal Surface Area:** 3–4 API routes + server actions.
    
- **Future‑Proofing:** Clean seams for agents, scraping, generation, and visualization.
    

---

## 2) Components

### 2.1 Frontend (Next.js 15, App Router)

- **Pages**
    
    - `/` — Landing (“Enter your Think Space”).
        
    - `/space/[id]` — Main interface for one space.
        
- **Core UI**
    
    - **ArtifactList** (cards w/ type badges: text/link/image).
        
    - **AddArtifactModal** (text input, URL input, image upload).
        
    - **ChatWindow** (history + prompt + streaming responses).
        
    - **ThemeBar** (title, description, color/mood).
        
- **State**
    
    - Space metadata, artifacts list, chat messages (client cache), optimistic updates.
        
- **Styling**
    
    - Tailwind + shadcn/ui; focus on clarity, calm, and keyboard-first flow.
        

### 2.2 Backend (Route Handlers / Server Actions)

- **/api/artifacts**
    
    - `POST` create (text/link metadata only — image uses /api/upload)
        
    - `GET` list (paged by created_at desc)
        
- **/api/ingest**
    
    - `POST` with `{ url }` → fetch HTML (simple readability scrape) → summarize → embed → upsert artifact.
        
- **/api/upload**
    
    - `POST` returns signed URL for Supabase Storage; client `PUT` binary → create artifact row.
        
- **/api/chat**
    
    - `POST` with `{ space_id, prompt }` → retrieve top‑k artifacts by embeddings → compose system+context → stream LLM → persist interaction + optional insight artifact.
        

### 2.3 Services

- **SupabaseService** — typed queries, RLS‑aware.
    
- **EmbeddingService** — provider-agnostic wrapper (initial adapter: OpenAI `text-embedding-3-small`; extend to Azure, Anthropic, or local models).
    
- **LLMService** — agent abstraction supporting multiple providers (echo, OpenAI, Ollama) behind a common interface. OpenAI adapters expect `OPENAI_API_KEY`; Ollama uses `OLLAMA_BASE_URL` (default `http://localhost:11434`).
- **NLPService** — lightweight summariser/keyword extractor to enrich artifact metadata for retrieval and space memory.
- **NLPService** — lightweight summariser/keyword extractor to enrich artifact metadata for retrieval.
    
- **ScraperService** — lightweight readability extraction (server-side fetch); guards for CORS/robots.
    

---

## 3) Data Model

### 3.1 Tables (Postgres)

```sql
create table public.spaces (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  description text,
  theme text default 'calm',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create type artifact_type as enum ('text','link','image','ai_insight');

create table public.artifacts (
  id uuid primary key default gen_random_uuid(),
  space_id uuid not null references public.spaces(id) on delete cascade,
  type artifact_type not null,
  content text,                     -- raw text or URL
  metadata jsonb default '{}'::jsonb, -- title, source, storage_path, etc.
  embedding vector(1536),           -- pgvector (match model dims)
  created_by text default 'user',   -- 'user' | 'agent'
  created_at timestamptz not null default now()
);

create table public.interactions (
  id uuid primary key default gen_random_uuid(),
  space_id uuid not null references public.spaces(id) on delete cascade,
  agent text not null default 'general',
  input text not null,
  output text,
  related_artifact_ids uuid[] default '{}',
  created_at timestamptz not null default now()
);

-- Indexes for performance
create index on public.artifacts (space_id, created_at desc);
create index on public.interactions (space_id, created_at desc);
create index artifacts_embedding_idx on public.artifacts using ivfflat (embedding vector_cosine_ops);
```

> **Note:** Set `vector` dimension to match the chosen embedding model.

### 3.2 Minimal ER Diagram (text)

```
spaces (1) ──< artifacts (n)
spaces (1) ──< interactions (n)
artifacts (embedding) used by /api/chat retrieval
```

---

## 4) Security & Access

### 4.1 Auth Options

- **MVP (Personal):** No auth; single default `space_id` configured in env.
    
- **Optional:** Supabase Auth; user‑scoped RLS policies.
    

### 4.2 Row‑Level Security (if Auth enabled)

```sql
alter table public.spaces enable row level security;
alter table public.artifacts enable row level security;
alter table public.interactions enable row level security;

create policy spaces_owner on public.spaces
  for select using (auth.uid() = metadata->>'owner');
-- Alternative: add owner_id uuid column and compare directly

create policy artifacts_owner on public.artifacts
  for select using (
    exists (
      select 1 from public.spaces s
      where s.id = space_id and s.metadata->>'owner' = auth.uid()::text
    )
  );

create policy interactions_owner on public.interactions
  for select using (
    exists (
      select 1 from public.spaces s
      where s.id = space_id and s.metadata->>'owner' = auth.uid()::text
    )
  );
```

> For simplicity, MVP can skip RLS and rely on single‑user, private project settings.

---

## 5) Data Flow & Sequences

### 5.1 Add Text Artifact

```
User → UI:AddArtifact → POST /api/artifacts
  → DB: insert (type='text', content)
  → NLPService: summarise + keywords for metadata
  → EmbeddingService: embed(content)
  → DB: update embedding
  → UI: optimistic card render
```

### 5.2 Add Link Artifact

```
User → UI:AddLink → POST /api/ingest { url }
  → ScraperService: fetch + extract title/summary
  → NLPService: keywords + summary post-processing
  → EmbeddingService: embed(summary || text)
  → DB: insert artifact {type='link', content=url, metadata:{title,summary}}
  → UI: show preview card
```

### 5.3 Image Upload

```
User → UI:Upload → POST /api/upload → { signedUrl }
  → Browser: PUT binary to Storage
  → Server: create artifact {type='image', metadata:{storage_path}}
  → (Optional) OCR then embed caption or alt text
```

### 5.4 Chat (RAG)

```
User → UI:Chat prompt → POST /api/chat { space_id, prompt }
  → Retrieve top‑k artifacts via cosine similarity
  → Compose system prompt + context window
  → LLMService: stream GPT‑4o‑mini
  → DB: insert interaction (input, output, related_artifact_ids)
  → (Optional) Save output as artifact (type='ai_insight')
```

---

## 6) Prompting Strategy

### 6.1 System Prompt (General Agent)

```
You are the General Agent for a personal Think Space. Your goals:
1) Use only the space's artifacts as primary context unless explicitly asked to web-search.
2) Synthesize concisely, cite artifact titles, and propose next reflective questions.
3) Preserve the user's voice; avoid overconfident invention.
```

### 6.2 Context Packaging

- Top‑k (e.g., 5) artifacts by cosine similarity.
    
- Include: title (from metadata), brief excerpt/summary, and URL for links.
    
- Truncate to fit token budget; prefer diverse sources.
    

### 6.3 Output Conventions

- Return **final answer** + short bullet **“What to do next”**.
    
- Optionally tag outputs with a `role` (insight/plan/summary) to store as `ai_insight` artifacts.
    

---

## 7) API Contract (Draft)

### POST `/api/artifacts`

- **Body**: `{ space_id, type: 'text'|'link'|'image'|'ai_insight', content?, metadata? }`
    
- **Returns**: `{ artifact }`
    
- **Notes**: For `link`, prefer `/api/ingest`; for `image`, prefer `/api/upload`.
    

### GET `/api/artifacts?space_id=...&limit=50&cursor=...`

- **Returns**: `{ artifacts: [...], nextCursor }`
    

### POST `/api/ingest`

- **Body**: `{ space_id, url }`
    
- **Returns**: `{ artifact }` (with scraped title/summary in metadata)
    

### POST `/api/upload`

- **Body**: `{ space_id, filename, contentType }`
    
- **Returns**: `{ signedUrl, storagePath }`
    

### POST `/api/chat`

- **Body**: `{ space_id, prompt, saveOutputAsArtifact?: boolean }`
    
- **Returns**: **Stream** of tokens + final `{ interaction, artifact? }`
    

---

## 8) Performance & Costs

- **Embedding**: whichever adapter is configured (default OpenAI `text-embedding-3-small`; alternatives include Azure, Anthropic, local models).
    
- **LLM**: provider chosen per agent (default GPT‑4o‑mini; supports Azure, Anthropic, or local GGUF models via adapter).
    
- **DB**: Index `embedding` with `ivfflat` and `vector_cosine_ops`.
    
- **Caching**: Memoize link ingest results by URL hash.
    
- **Target**: p50 chat < 2.5s (warmed), link ingest < 4s.
    

---

## 9) Observability

- **Client**: lightweight telemetry (page views, actions) via PostHog (optional).
    
- **Server**: structured logs per route (duration, status, token usage).
    
- **DB**: slow query log in Supabase; monitor `ivfflat` index health.
    

---

## 10) Security & Privacy

- **Transport**: HTTPS only, secure cookies if auth enabled.
    
- **Storage**: Private buckets for images; signed URLs for access.
    
- **Secrets**: Vercel env vars; keep provider keys (OpenAI, Anthropic, Azure, local) server-side only.
    
- **PII**: Avoid storing sensitive personal data in artifacts for MVP.
    

---

## 11) Testing Plan

- **Unit**: services (embedding, retrieval composition, prompt packer).
    
- **Integration**: /api/chat end‑to‑end with seeded artifacts.
    
- **UX**: manual “golden path” — add text → chat → recall → insight saved.
    
- **Regression**: seed snapshots to validate retrieval stability after schema changes.
    

---

## 12) Risks & Mitigations

|Risk|Mitigation|
|---|---|
|Hallucination on thin context|Strict system prompt; surface sources; allow user to mark wrong outputs.|
|Token overrun|Aggressive truncation; summarize long artifacts at ingest.|
|Scraper fragility|Fallback to URL-only artifact; add manual title/summary edit.|
|Cost spikes|Use mini models; cap artifacts per space; batch embeddings.|
|RLS complexity|Start single-user; add Auth/RLS in Phase 2.|

---

## 13) Extensibility (Phase 2+)

- **Multiple Spaces**: add `owner_id`, list view, quick switcher.
    
- **Agents as Plugins**: table `agents` + `space_agents` mapping; UI to enable/disable roles.
    
- **Graph View**: force-directed canvas (React Flow) over embeddings similarity.
    
- **Image Gen**: Visualizer agent → call image API, store into `artifacts(type='image')`.
    
- **Collaboration**: invited users; per‑space ACLs; comment threads.
    
- **Web Search Tooling**: gated external retrieval agent with explicit opt‑in.
    

---

## 14) Developer Setup

1. **Create Supabase project**; enable pgvector extension.
    

```sql
create extension if not exists vector;
```

2. **Apply schema** from §3.
    
3. **Create Storage bucket** `thinkspace-images` (private).
    
4. **Env Vars (Vercel)**
    

```
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=  # used only on server for embeddings writes
OPENAI_API_KEY=
DEFAULT_SPACE_ID=
```

5. **Run local**: `pnpm dev` (or npm/yarn). Use edge runtime where safe; Node for scraping.
    

---

## 15) Acceptance Criteria (MVP)

- Add text and link artifacts; see cards render immediately.
    
- Chat answers reference relevant artifacts from memory.
    
- Option to save an answer as an `ai_insight` artifact.
    
- Theme/mood visible on space page.
    
- Deployed on Vercel; Supabase hosts data; simple privacy respected.
    

---

## 16) Appendix — Example Prompts

**Summarize Space**

> “Synthesize the 5 most important ideas across artifacts in this space and propose 3 reflective questions.”

**Plan Next Steps**

> “Based on my artifacts, propose a 3‑step micro‑plan for what to explore next.”

**Create Insight**

> “Write a concise, quotable insight (≤40 words) capturing the essence of this space today.”

---

**End of SYSTEM_DESIGN.md**
