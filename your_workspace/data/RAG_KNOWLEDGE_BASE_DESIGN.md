# RAG Knowledge Base Design - BehaviorShift Script Generation

**Purpose**: Provide high-quality reference material to inform Step 3 (Script Generation) with proven hypnosis techniques, language patterns, and therapeutic best practices.

**Created**: 2025-10-27
**Version**: 1.0

---

## Overview

The RAG knowledge base will store curated content about:
1. Clinical hypnosis techniques and scripts
2. Ericksonian language patterns
3. NLP anchoring and reframing methods
4. Neuroscience of trance and learning
5. Jungian archetypal imagery
6. Active imagination practices
7. Therapeutic best practices and ethics

This content will be:
- **Chunked** into semantically meaningful segments
- **Embedded** using sentence transformers
- **Stored** in a vector database (ChromaDB)
- **Retrieved** based on similarity to user's skill/context
- **Synthesized** into personalized scripts

---

## Knowledge Base Structure

### Collection Organization

```
vector_db/
├── hypnosis_scripts/          # Complete example scripts
│   ├── confidence_building/
│   ├── stress_management/
│   ├── performance_enhancement/
│   ├── relationship_skills/
│   └── self_compassion/
│
├── hypnosis_techniques/       # Specific techniques and methods
│   ├── induction_methods/
│   ├── deepening_techniques/
│   ├── suggestion_patterns/
│   ├── awakening_sequences/
│   └── anchoring_methods/
│
├── language_patterns/         # Therapeutic language
│   ├── ericksonian_patterns/
│   ├── nlp_reframing/
│   ├── metaphors/
│   ├── embedded_commands/
│   └── permissive_language/
│
├── neuroscience/             # Scientific foundations
│   ├── neuroplasticity/
│   ├── trance_states/
│   ├── mental_rehearsal/
│   └── subconscious_learning/
│
├── jungian_archetypes/       # Symbolic content
│   ├── archetypal_imagery/
│   ├── shadow_integration/
│   ├── active_imagination/
│   └── symbolic_metaphors/
│
└── best_practices/           # Safety and ethics
    ├── safety_protocols/
    ├── ethical_guidelines/
    ├── contraindications/
    └── grounding_techniques/
```

---

## Content Types

### 1. Complete Hypnosis Scripts (15-20 examples)

**Purpose**: Provide structural templates and proven patterns

**Content Examples**:
- "Confidence Building for Public Speaking" (complete 25-min script)
- "Deep Relaxation and Stress Release" (complete script)
- "Self-Compassion and Inner Critic Work" (complete script)
- "Performance Excellence - Flow State" (complete script)
- "Emotional Regulation and Resilience" (complete script)

**Metadata**:
```json
{
  "title": "Confidence Building for Public Speaking",
  "category": "performance",
  "target_skill": "confidence, public speaking, presentation",
  "duration": "25 minutes",
  "phases": 7,
  "learning_style": "visual",
  "archetypes": ["Leader", "Communicator"],
  "source": "Clinical Hypnotherapy Practitioner Guide",
  "safety_level": "self-guided"
}
```

---

### 2. Hypnosis Techniques (30-40 technique cards)

**Purpose**: Provide modular building blocks for script construction

**Content Examples**:

#### Induction Techniques:
- Progressive Muscle Relaxation (PMR)
- Breath-Counting Induction
- Eye-Fixation Method
- Staircase Descent
- Beach Scene Relaxation

#### Deepening Techniques:
- Countdown Deepening
- Fractionation
- Elevator Going Down
- Floating/Sinking Metaphor

#### Suggestion Patterns:
- Direct Suggestion
- Indirect (Ericksonian) Suggestion
- Compound Suggestions
- Post-Hypnotic Suggestions
- Ego-Strengthening Suggestions

**Metadata**:
```json
{
  "technique": "Progressive Muscle Relaxation",
  "category": "induction",
  "duration": "5-7 minutes",
  "difficulty": "beginner-friendly",
  "best_for": "anxiety, tension, physical stress",
  "contraindications": "none",
  "example_script": "Begin by bringing your attention to your feet..."
}
```

---

### 3. Language Patterns (50-60 pattern examples)

**Purpose**: Provide therapeutic language templates

**Content Examples**:

#### Ericksonian Patterns:
- **Embedded Commands**: "You can *feel completely at ease* as you continue..."
- **Presuppositions**: "When you notice that calm confidence emerging..."
- **Temporal Binding**: "As you breathe in, you can begin to relax..."
- **Metaphors**: "Like a tree rooted deeply, you stand grounded..."

#### NLP Patterns:
- **Reframing**: "What you used to call nervousness, you can now recognize as excitement..."
- **Anchoring**: "Each time you take three deep breaths, you return to this calm state..."
- **Submodalities**: "Notice how that feeling of confidence has a color... a texture..."

#### Permissive Language:
- "You might notice..."
- "You can allow..."
- "Perhaps you'll find..."
- "It's okay to..."

**Metadata**:
```json
{
  "pattern_type": "embedded_command",
  "category": "ericksonian",
  "use_case": "bypass critical faculty, deepen suggestions",
  "example": "You can *feel completely relaxed* as you continue to breathe",
  "explanation": "Embed directive within larger sentence structure"
}
```

---

### 4. Neuroscience Insights (20-30 research summaries)

**Purpose**: Ground scripts in evidence-based mechanisms

**Content Examples**:
- Mental rehearsal activates same motor cortex as physical practice
- Theta brainwave states enhance neuroplasticity
- Amygdala regulation through vagal tone breathing
- Default Mode Network (DMN) reduction in trance states
- Predictive coding and future pacing effectiveness

**Metadata**:
```json
{
  "topic": "Mental Rehearsal and Motor Learning",
  "key_finding": "Vivid mental rehearsal activates 70-80% of same neural pathways as physical practice",
  "source": "Neuroscience Journal",
  "year": 2020,
  "application": "Use detailed sensory visualization to pre-train skills",
  "relevant_for": "performance, skill acquisition, confidence"
}
```

---

### 5. Jungian Archetypal Content (15-20 archetypal profiles)

**Purpose**: Provide symbolic depth and resonance

**Content Examples**:

**Archetypes**:
- **Leader/Ruler**: Authority, decision-making, confidence
- **Sage/Teacher**: Wisdom, knowledge-sharing, mentorship
- **Warrior**: Courage, discipline, resilience
- **Caregiver**: Compassion, empathy, nurturing
- **Creator**: Innovation, expression, flow
- **Lover**: Connection, intimacy, passion

**Metaphoric Imagery**:
- Lighthouse (steady presence, guidance)
- Tree (grounded, rooted, stable)
- Mountain (unmovable, perspective)
- River (flow, adaptation, persistence)
- Phoenix (transformation, renewal)

**Metadata**:
```json
{
  "archetype": "Leader",
  "qualities": ["confidence", "authority", "decision-making", "presence"],
  "shadow": "Impostor, Tyrant",
  "metaphors": ["Lighthouse", "Mountain Peak", "King/Queen on Throne"],
  "body_posture": "Upright spine, grounded feet, open chest",
  "voice_quality": "Clear, steady, measured",
  "best_for_skills": ["leadership", "public speaking", "confidence", "decision-making"]
}
```

---

### 6. Best Practices & Safety (10-15 guidelines)

**Purpose**: Ensure safe, ethical script generation

**Content Examples**:
- Always include proper awakening sequence
- Use permissive, not coercive, language
- Avoid absolute statements ("You will always...")
- Include grounding techniques
- Respect user autonomy
- Contraindications for self-hypnosis
- When to refer to licensed professional

**Metadata**:
```json
{
  "guideline": "Always include awakening sequence",
  "category": "safety",
  "importance": "critical",
  "rationale": "Ensures user returns to alert state; prevents dissociation",
  "implementation": "Count up 1-5 with gradual re-orientation",
  "what_to_avoid": "Ending abruptly without re-orientation"
}
```

---

## Retrieval Strategy

### Query Construction

When user provides:
- **Target skill**: "confidence in presentations"
- **Personal context**: "executive presentation anxiety"
- **Learning style**: "visual"

Generate queries:
1. **Skill-specific**: "confidence public speaking hypnosis script"
2. **Technique-specific**: "anxiety reduction techniques hypnosis"
3. **Archetype-specific**: "Leader archetype confidence imagery"
4. **Language patterns**: "embedded commands confidence suggestions"
5. **Neuroscience**: "performance anxiety amygdala regulation"

### Retrieval Parameters

```python
query_config = {
    "top_k": 10,  # Retrieve top 10 most relevant chunks per query
    "similarity_threshold": 0.7,  # Minimum cosine similarity
    "diversity": True,  # Ensure diverse content types
    "rerank": True  # Re-rank by relevance to specific context
}
```

### Expected Retrieval Per Script Generation

For each script generation, retrieve:
- 2-3 **complete example scripts** (structural templates)
- 5-7 **specific techniques** (induction, deepening, awakening)
- 8-10 **language patterns** (embedded commands, metaphors)
- 2-3 **neuroscience insights** (mechanisms supporting approach)
- 1-2 **archetypal profiles** (symbolic embodiment)
- 1-2 **safety guidelines** (critical protocols)

**Total**: ~20-30 relevant chunks per script generation

---

## Vector Database Setup

### Technology Stack

**Vector DB**: ChromaDB (local, lightweight, easy to set up)
**Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (fast, good quality)
**Chunking Strategy**: Semantic chunks (by section, 200-500 tokens)
**Metadata**: Rich metadata for filtering and context

### ChromaDB Collections

```python
collections = {
    "hypnosis_scripts": {
        "embedding_model": "all-MiniLM-L6-v2",
        "distance_metric": "cosine",
        "metadata_schema": ["title", "category", "skill", "duration", "phases"]
    },
    "techniques": {
        "embedding_model": "all-MiniLM-L6-v2",
        "distance_metric": "cosine",
        "metadata_schema": ["technique", "category", "duration", "best_for"]
    },
    "language_patterns": {
        "embedding_model": "all-MiniLM-L6-v2",
        "distance_metric": "cosine",
        "metadata_schema": ["pattern_type", "category", "use_case"]
    },
    "neuroscience": {
        "embedding_model": "all-MiniLM-L6-v2",
        "distance_metric": "cosine",
        "metadata_schema": ["topic", "relevant_for"]
    },
    "archetypes": {
        "embedding_model": "all-MiniLM-L6-v2",
        "distance_metric": "cosine",
        "metadata_schema": ["archetype", "qualities", "best_for_skills"]
    },
    "best_practices": {
        "embedding_model": "all-MiniLM-L6-v2",
        "distance_metric": "cosine",
        "metadata_schema": ["category", "importance"]
    }
}
```

---

## Content Curation Strategy

### Phase 1: Initial Corpus (Sprint 1)
**Goal**: 15-20 documents minimum for MVP testing

**Priority Content**:
1. ✅ 5 complete hypnosis scripts (diverse skills)
2. ✅ 10 core techniques (induction, deepening, awakening)
3. ✅ 15 language patterns (Ericksonian, NLP, permissive)
4. ✅ 5 archetypal profiles (Leader, Sage, Warrior, Caregiver, Creator)
5. ✅ 5 safety guidelines (critical protocols)

**Total**: ~40 curated documents/chunks

### Phase 2: Expansion (Sprint 2)
**Goal**: 50-75 documents for production quality

**Additional Content**:
- 10 more complete scripts (covering more skills)
- 20 additional techniques (advanced methods)
- 25 more language patterns (metaphors, reframes)
- 10 neuroscience insights
- 5 more archetypes

### Phase 3: Continuous Enrichment (Ongoing)
**Goal**: 100+ documents for comprehensive coverage

**Sources**:
- Clinical hypnosis textbooks
- Ericksonian therapy literature
- NLP practitioner guides
- Jungian psychology books
- Neuroscience research papers
- Practitioner scripts (with permission)

---

## Quality Control

### Content Standards

All content must meet:
1. **Accuracy**: Evidence-based or clinically proven
2. **Safety**: No harmful techniques or suggestions
3. **Clarity**: Well-written and understandable
4. **Completeness**: Sufficient detail for script generation
5. **Attribution**: Properly sourced and credited

### Curation Checklist

- [ ] Content is accurate and evidence-based
- [ ] No safety concerns or contraindications
- [ ] Properly formatted and chunked
- [ ] Metadata is complete and accurate
- [ ] Source attribution included
- [ ] Tested in vector DB (retrieval works)

---

## Integration with Step 3

### Current Step 3 Prompt (excerpt):
```
### Phase 1: Query Vector DB (RAG)
Query your hypnosis/neuroscience content corpus for:
- Sample hypnosis scripts (for structure and language patterns)
- Induction and deepening techniques
- Skill-specific visualization approaches
- Awakening/integration sequences

Query examples:
- "hypnosis induction relaxation techniques"
- "confidence building guided visualization"
- "subconscious pattern installation [TARGET_SKILL]"
- "hypnosis script structure best practices"

Retrieve top 5-10 most relevant passages.
```

### Enhanced Integration:
```python
# In script generation step
rag_context = retrieve_from_knowledgebase(
    queries=[
        f"{user_skill} hypnosis script",
        f"{user_skill} techniques",
        f"{archetype} imagery metaphors",
        "induction deepening awakening methods",
        "hypnotic language patterns"
    ],
    top_k=10,
    filters={
        "learning_style": user_learning_style,
        "safety_level": "self-guided"
    }
)

# Combine with research from Step 2
script = generate_script(
    user_context=user_input,
    research=step2_research,
    rag_context=rag_context,
    blueprint=seven_phase_structure
)
```

---

## Success Metrics

### Retrieval Quality
- **Relevance**: Retrieved chunks score ≥0.7 similarity
- **Diversity**: Retrieved content spans multiple categories
- **Coverage**: All critical elements represented (induction, core work, awakening)

### Script Quality Impact
- **Improvement**: Scripts with RAG score higher than without
- **Consistency**: Multiple runs with same input produce similar quality
- **Personalization**: RAG content successfully adapts to context

### User Satisfaction
- **Editing required**: < 10% with RAG (vs. < 20% without)
- **Safety gate pass rate**: ≥ 95% with RAG
- **User ratings**: ≥ 4.5/5 for scripts using RAG

---

## Implementation Phases

### Phase 1: Setup (This Sprint)
1. Create directory structure for knowledge base
2. Set up ChromaDB locally
3. Curate initial 15-20 documents
4. Test embedding and retrieval
5. Integrate with Step 3 prompt

### Phase 2: Testing (This Sprint)
1. Generate scripts with RAG
2. Compare quality with/without RAG
3. Validate retrieval relevance
4. Refine queries and filters

### Phase 3: Expansion (Sprint 2)
1. Add 30-50 more documents
2. Expand coverage across skill types
3. Add neuroscience insights
4. Refine metadata and filtering

---

## File Structure

```
your_workspace/data/
├── RAG_KNOWLEDGE_BASE_DESIGN.md  (this file)
├── rag_corpus/
│   ├── hypnosis_scripts/
│   │   ├── confidence_public_speaking.md
│   │   ├── stress_management.md
│   │   ├── self_compassion.md
│   │   ├── performance_flow.md
│   │   └── emotional_regulation.md
│   │
│   ├── techniques/
│   │   ├── induction_progressive_relaxation.md
│   │   ├── induction_breath_counting.md
│   │   ├── deepening_staircase.md
│   │   ├── deepening_countdown.md
│   │   └── awakening_count_up.md
│   │
│   ├── language_patterns/
│   │   ├── ericksonian_embedded_commands.md
│   │   ├── ericksonian_metaphors.md
│   │   ├── nlp_anchoring.md
│   │   ├── nlp_reframing.md
│   │   └── permissive_language.md
│   │
│   ├── archetypes/
│   │   ├── leader_archetype.md
│   │   ├── sage_archetype.md
│   │   ├── warrior_archetype.md
│   │   ├── caregiver_archetype.md
│   │   └── creator_archetype.md
│   │
│   └── best_practices/
│       ├── safety_protocols.md
│       ├── awakening_requirements.md
│       ├── permissive_language_guide.md
│       └── contraindications.md
│
├── vector_db/  (ChromaDB storage)
│   └── chroma.sqlite3
│
└── scripts/
    ├── setup_vector_db.py
    ├── ingest_documents.py
    ├── query_rag.py
    └── test_retrieval.py
```

---

## Next Steps

1. ✅ Create directory structure
2. ⏭️ Curate initial 5 hypnosis scripts
3. ⏭️ Write 10 technique cards
4. ⏭️ Compile 15 language patterns
5. ⏭️ Create 5 archetypal profiles
6. ⏭️ Write 5 safety guidelines
7. ⏭️ Set up ChromaDB
8. ⏭️ Test retrieval
9. ⏭️ Integrate with Step 3
10. ⏭️ Validate improvement in script quality

---

**Status**: Design Complete - Ready for Implementation
**Priority**: HIGH (enhances Step 3 significantly)
**Effort**: Medium (2-3 days for MVP, ongoing for expansion)
