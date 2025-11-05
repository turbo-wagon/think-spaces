# Bloom Features Specification
## Think Spaces Enhancement Proposal

**Version:** 1.0  
**Date:** November 4, 2025  
**Status:** Draft for Review

---

## Executive Summary

The **Bloom** system extends Think Spaces with a "memory phenomenology" layer—turning static artifact collections into living, evolving cognitive environments that surface hidden connections, track temporal decay, and manifest the sensory qualities of accumulated knowledge.

Inspired by the "Obsidian Bloom" narrative concept, this feature set treats memory not just as stored data, but as something visceral, textured, and prone to both decay and transformation.

---

## Core Concepts

### 1. The Bloom Metaphor
A "bloom" is an emergent visualization/experience that appears when:
- Artifacts accumulate critical mass in a space
- Connections between disparate artifacts reach threshold density
- Temporal patterns reveal themselves across revision history

Like obsidian glass forming from volcanic heat, blooms crystallize understanding from the raw material of collected thoughts.

### 2. Memory States
Every artifact and space tracks four temporal-emotional states:

| State | Description | Visual/UX Metaphor |
|-------|-------------|-------------------|
| **Hot** | Recently accessed, frequently referenced | Warm colors, high contrast, immediate availability |
| **Warm** | Moderately recent, contextually relevant | Balanced palette, normal accessibility |
| **Cool** | Aging, infrequently accessed | Desaturated colors, slight transparency |
| **Frost** | Long-dormant, at risk of becoming inaccessible | Frosted glass effect, requires "thawing" to access |

### 3. Entropy Tracking
Each space maintains an **entropy score** (0-100):
- **Low entropy (0-30):** Coherent, well-organized, tightly connected
- **Medium entropy (31-70):** Normal working state with some fragmentation
- **High entropy (71-100):** Chaotic, disconnected, needs consolidation

---

## Feature Specifications

### Phase 1: Temporal Metadata System

#### 1.1 Artifact Temperature Tracking

**Database Schema Addition:**
```python
# Add to Artifact model
temperature_state: str  # 'hot', 'warm', 'cool', 'frost'
last_accessed: datetime
access_count: int
thermal_decay_rate: float  # Custom per-artifact decay speed
temperature_last_updated: datetime
```

**Thermal Decay Algorithm:**
```
Time since last access | Temperature transition
-----------------------|----------------------
< 7 days              | HOT
7-30 days             | WARM
31-90 days            | COOL
> 90 days             | FROST
```

**API Endpoints:**
```
GET  /api/spaces/{space_id}/thermal-map
     Returns temperature distribution across all artifacts

POST /api/artifacts/{artifact_id}/thaw
     "Thaws" a frosted artifact (resets temperature to WARM)

GET  /api/spaces/{space_id}/artifacts/frosted
     Returns all frosted artifacts requiring attention
```

#### 1.2 Space Entropy Calculation

**Formula:**
```
entropy = (
    fragmentation_score * 0.4 +
    isolation_score * 0.3 +
    temporal_drift_score * 0.3
)

Where:
- fragmentation_score = % of artifacts without semantic connections
- isolation_score = % of artifacts with < 2 outbound connections
- temporal_drift_score = variance in access patterns
```

**Database Schema Addition:**
```python
# Add to Space model
entropy_score: float
entropy_last_calculated: datetime
fragmentation_index: float
connection_density: float
temporal_coherence: float
```

**API Endpoints:**
```
GET  /api/spaces/{space_id}/entropy
     Returns current entropy metrics

POST /api/spaces/{space_id}/consolidate
     Triggers AI-assisted space reorganization
```

---

### Phase 2: Bloom Detection & Visualization

#### 2.1 Connection Mapping

**Semantic Connection Detection:**
- Use existing vector embeddings to find artifact relationships
- Calculate cosine similarity between artifact embeddings
- Flag connections above threshold (e.g., > 0.75 similarity)

**Database Schema Addition:**
```python
# New table: ArtifactConnection
class ArtifactConnection(Base):
    id: int
    space_id: int
    source_artifact_id: int
    target_artifact_id: int
    connection_strength: float  # 0.0 - 1.0
    connection_type: str  # 'semantic', 'temporal', 'explicit'
    discovered_at: datetime
    last_reinforced: datetime  # Updated when both artifacts accessed
```

**Connection Types:**
1. **Semantic:** High embedding similarity
2. **Temporal:** Accessed/created in close proximity
3. **Explicit:** User-defined tags/links match

#### 2.2 Bloom Event Detection

**Bloom Trigger Conditions:**
```
A bloom occurs when:
1. Connection density in region > 0.7 (70% of artifacts interconnected)
2. Minimum 5 artifacts in cluster
3. Activity spike: 3+ artifacts accessed within 7 days
4. Entropy drops by 15+ points in the cluster
```

**Database Schema Addition:**
```python
# New table: Bloom
class Bloom(Base):
    id: int
    space_id: int
    name: str  # Auto-generated or user-named
    artifact_ids: JSON  # List of artifact IDs in bloom
    center_point: JSON  # {"x": float, "y": float} for visualization
    strength: float  # 0.0 - 1.0
    bloom_type: str  # 'connection', 'insight', 'pattern'
    first_detected: datetime
    last_active: datetime
    description: str  # AI-generated summary of bloom theme
```

**API Endpoints:**
```
GET  /api/spaces/{space_id}/blooms
     Returns all active blooms in space

GET  /api/blooms/{bloom_id}
     Returns detailed bloom information

POST /api/blooms/{bloom_id}/name
     Allows user to name/annotate bloom

DELETE /api/blooms/{bloom_id}
     Dismisses bloom (marks as acknowledged)
```

#### 2.3 Bloom Visualization

**UI Components:**

1. **Thermal Heatmap View**
   - Canvas overlay showing artifact temperature
   - Hot artifacts: red/orange glow
   - Cool artifacts: blue/purple fade
   - Frost artifacts: crystalline edges, semi-transparent

2. **Connection Graph View**
   - Force-directed graph of artifact relationships
   - Edge thickness = connection strength
   - Node clustering shows potential blooms
   - Animated "pulse" when new connections form

3. **Bloom Highlight**
   - Radial gradient emanating from bloom center
   - Obsidian-like visual: dark center with iridescent edges
   - Subtle animation: "breathing" effect as artifacts interact

---

### Phase 3: AI-Powered Bloom Insights

#### 3.1 Bloom Summarization Agent

**New Agent Type: `BloomAnalyzer`**

**Capabilities:**
- Generates natural language summary of bloom theme
- Identifies the "core insight" connecting artifacts
- Suggests new artifacts to add to bloom
- Flags contradictions or tensions within bloom

**Implementation:**
```python
# New LLM prompt template
bloom_analysis_prompt = """
You are analyzing a "bloom" - a cluster of related ideas in a cognitive space.

Artifacts in bloom:
{artifact_summaries}

Connection strengths:
{connection_data}

Task: Provide a 2-3 sentence summary capturing the central insight or theme 
that connects these artifacts. Then suggest 1-2 questions that could deepen 
understanding of this bloom.

Format:
INSIGHT: [your summary]
QUESTIONS: 
- [question 1]
- [question 2]
"""
```

**API Endpoints:**
```
POST /api/blooms/{bloom_id}/analyze
     Generates AI insight for bloom

GET  /api/blooms/{bloom_id}/insights
     Returns cached insights for bloom
```

#### 3.2 Frost Recovery Suggestions

**Frost Revival Agent:**
- Scans frosted artifacts weekly
- Identifies frosted artifacts with high connection potential
- Generates "memory prompts" to re-engage with dormant content

**Example Prompt:**
```
"Your artifact 'Quantum Entanglement Notes' has been dormant for 120 days. 
It connects to your recent work on 'Information Theory'. 
Would you like to revisit this connection?"
```

**API Endpoints:**
```
GET  /api/spaces/{space_id}/frost-recovery-suggestions
     Returns prioritized list of frosted artifacts to revisit

POST /api/artifacts/{artifact_id}/frost-prompt
     Triggers agent to generate custom re-engagement prompt
```

---

### Phase 4: Sensory Metadata Layer

#### 4.1 Emotional Tags

**Artifact Emotional Tagging:**
Allow users (and AI) to tag artifacts with emotional qualities:

```python
# Add to Artifact model
emotional_tags: JSON  # {"curiosity": 0.8, "urgency": 0.3, "doubt": 0.5}
sensory_notes: str    # Free-form user notes about "feel" of artifact
```

**Predefined Emotional Dimensions:**
- **Curiosity** (exploratory, open-ended)
- **Clarity** (well-understood, resolved)
- **Tension** (unresolved, conflicting)
- **Urgency** (action-required, time-sensitive)
- **Nostalgia** (historical, reflective)

**UI Elements:**
- Color-code artifacts by dominant emotion
- Filter spaces by emotional landscape
- Track emotional evolution over time

#### 4.2 Olfactory/Auditory Metaphors

**Advanced Feature (Optional):**
Map artifact states to non-visual cues:

| State | Sound Metaphor | Scent Metaphor |
|-------|----------------|----------------|
| Hot | Crackling fire | Fresh coffee, sharp mint |
| Warm | Gentle rustling | Warm bread, vanilla |
| Cool | Distant chimes | Rain on leaves, aged paper |
| Frost | Crystalline silence | Cold metal, fresh snow |

**Implementation:**
- Optional audio ambience based on space temperature distribution
- Descriptive text in UI: "This space feels like... [metaphor]"

---

### Phase 5: Bloom-Driven Workflows

#### 5.1 Automatic Space Curation

**Bloom-Based Space Splitting:**
When a space becomes too chaotic (entropy > 80):
- Detect major bloom clusters
- Suggest creating new sub-spaces for each bloom
- Auto-migrate artifacts to new spaces (with user approval)

**API Endpoint:**
```
POST /api/spaces/{space_id}/split-by-blooms
     Analyzes space and proposes split plan
```

#### 5.2 Cross-Space Bloom Detection

**Global Bloom Scanning:**
- Periodic scan across ALL spaces for inter-space connections
- Detect when artifacts in separate spaces form unexpected bloom
- Suggest creating "bridge" space or merging related spaces

**Database Schema Addition:**
```python
# New table: CrossSpaceBloom
class CrossSpaceBloom(Base):
    id: int
    space_ids: JSON  # List of involved space IDs
    bridge_artifact_ids: JSON
    strength: float
    suggested_action: str  # 'merge', 'create_bridge', 'link'
```

---

## Technical Implementation Notes

### Vector Embeddings
- Use existing embedding system for semantic similarity
- Recommended model: `text-embedding-3-small` (OpenAI) or `all-MiniLM-L6-v2` (local)
- Store embeddings with artifacts for fast similarity calculations

### Performance Considerations
- **Entropy calculation:** Run as background job, cache results
- **Bloom detection:** Trigger on artifact add/edit, debounce by 5 minutes
- **Temperature decay:** Daily cron job, batch update all artifacts
- **Connection mapping:** Lazy-load on space view, cache for 1 hour

### UI/UX Guidelines
- **Bloom notifications:** Non-intrusive, bottom-right toast
- **Temperature visualization:** Subtle, opt-in overlay (not default)
- **Entropy warnings:** Only show when > 75, suggest consolidation
- **Frost alerts:** Weekly digest email, not real-time interruptions

---

## User Stories

### Story 1: Rediscovering Connections
> "As a researcher, I want to see unexpected connections between my old reading notes and current project ideas, so I can synthesize insights I wouldn't have noticed manually."

**Solution:** Bloom detection surfaces semantic connections across time, with AI summaries highlighting the core insight.

---

### Story 2: Managing Information Overload
> "As a prolific note-taker, I want to know when my spaces are becoming too chaotic, so I can reorganize before losing track of important content."

**Solution:** Entropy tracking provides early warning, with AI-suggested consolidation strategies.

---

### Story 3: Reviving Dormant Ideas
> "As a creative, I want to be reminded of interesting ideas I captured months ago but haven't revisited, especially when they relate to my current work."

**Solution:** Frost recovery suggestions use connection mapping to prioritize which dormant artifacts to revisit.

---

## Rollout Plan

### Phase 1: Foundation (Week 1-2)
- Implement temperature tracking
- Add entropy calculation
- Basic API endpoints

### Phase 2: Visualization (Week 3-4)
- Connection mapping database
- Bloom detection algorithm
- UI thermal heatmap

### Phase 3: AI Integration (Week 5-6)
- Bloom analyzer agent
- Frost recovery prompts
- Cross-space scanning

### Phase 4: Polish (Week 7-8)
- Sensory metadata UI
- Workflow automation
- Performance optimization

---

## Success Metrics

1. **User Engagement:**
   - % of users who interact with bloom suggestions
   - Frequency of frost artifact revivals
   - Time spent in spaces with active blooms

2. **System Health:**
   - Average space entropy (target: < 60)
   - Connection density (target: > 0.4)
   - Artifact access frequency distribution

3. **Qualitative:**
   - User testimonials about "unexpected discoveries"
   - Reduction in "I know I saved this somewhere..." frustration
   - Self-reported value of bloom insights

---

## Open Questions for Discussion

1. **Privacy:** Should cross-space blooms be opt-in? (Some users may want spaces isolated)
2. **Cognitive Load:** How many bloom notifications before it becomes noise?
3. **Customization:** Should users control decay rates per space or globally?
4. **AI Tone:** How "confident" should bloom insights be? (Tentative suggestions vs. declarative insights)

---

## Appendix: Example Bloom

**Space:** "Quantum Computing Research"  
**Bloom Detected:** November 3, 2025  
**Artifacts in Bloom:**
- "Shor's Algorithm Overview" (Hot)
- "RSA Encryption Vulnerability" (Warm)
- "Post-Quantum Cryptography Standards" (Warm)
- "NIST PQC Competition Results" (Cool)
- "Timeline for Quantum Threat" (Hot)

**AI-Generated Insight:**
> "This bloom reveals the tension between quantum computing's potential to break current encryption and the urgent development of quantum-resistant standards. Your recent activity suggests you're tracking the timeline for when cryptographic migration becomes critical."

**Suggested Questions:**
- What's the current state of PQC adoption in your organization?
- Which legacy systems are most vulnerable in the quantum transition?

**Entropy Before Bloom:** 68 (Medium)  
**Entropy After Recognition:** 45 (Low) — User engaged with bloom, added clarifying notes

---

## License & Attribution

This specification draws inspiration from:
- The "Obsidian Bloom" narrative concept (sensory memory phenomenology)
- Zettelkasten principles (connection-based knowledge management)
- Cognitive load theory (entropy as cognitive burden metric)

Designed for **Think Spaces** by Claude (Anthropic) in collaboration with the project maintainer.

---

**Document Status:** Ready for review and technical feasibility assessment.  
**Next Steps:** Review with Claude Code instance, adjust to actual codebase structure, prioritize features for MVP.