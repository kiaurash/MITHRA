# RAG Knowledge Base - Implementation Plan

**Sprint 1 Demo Date**: November 3, 2025
**Days Available**: 6 days (Oct 28 - Nov 2)
**Status**: In Progress

---

## Revised Timeline

### Day 1: October 28 (TODAY)
**Goal**: Complete content curation (40 documents minimum)

**Tasks**:
- [x] Design RAG architecture ✅
- [x] Create directory structure ✅
- [x] Create first example script ✅
- [ ] Create 4 more complete hypnosis scripts (5 total)
- [ ] Create 10 technique cards
- [ ] Create 15 language pattern examples
- [ ] Create 5 archetypal profiles
- [ ] Create 5 best practice guidelines
- [ ] Create 5 neuroscience insights

**Output**: 45 curated documents ready for embedding

---

### Day 2: October 29
**Goal**: Set up vector database and test retrieval

**Tasks**:
- [ ] Install ChromaDB and dependencies
- [ ] Create setup script (setup_vector_db.py)
- [ ] Create ingestion script (ingest_documents.py)
- [ ] Embed all 45 documents into vector DB
- [ ] Create query script (query_rag.py)
- [ ] Test retrieval with sample queries
- [ ] Validate retrieval quality (relevance, diversity)

**Output**: Working vector DB with test retrieval examples

---

### Day 3: October 30
**Goal**: Integrate RAG with Step 3 and test

**Tasks**:
- [ ] Update step3_script_generation_prompt.txt to use RAG context
- [ ] Create RAG query templates for different skills
- [ ] Test script generation WITH RAG
- [ ] Compare scripts with/without RAG (quality assessment)
- [ ] Refine retrieval parameters if needed
- [ ] Document integration approach

**Output**: Step 3 successfully using RAG knowledge base

---

### Day 4: October 31
**Goal**: Test workflow end-to-end with RAG

**Tasks**:
- [ ] Run Test Scenario 1 (confidence presentations) WITH RAG
- [ ] Run Test Scenario 2 (interpersonal skills) WITH RAG
- [ ] Run Test Scenario 3 (self-development) WITH RAG
- [ ] Compare quality metrics with original tests
- [ ] Document improvements
- [ ] Fix any issues discovered

**Output**: 3 test runs showing RAG improvement

---

### Day 5: November 1
**Goal**: Expand corpus and optimize

**Tasks**:
- [ ] Add 15-20 more documents (total: 60-65)
- [ ] Test with edge cases
- [ ] Optimize retrieval parameters
- [ ] Add any missing critical content
- [ ] Create RAG metrics dashboard
- [ ] Update documentation

**Output**: Production-ready RAG system with metrics

---

### Day 6: November 2
**Goal**: Demo preparation and final polish

**Tasks**:
- [ ] Create demo narrative showing RAG impact
- [ ] Prepare before/after comparison (scripts with/without RAG)
- [ ] Polish all documentation
- [ ] Create visual diagrams of RAG architecture
- [ ] Practice demo flow
- [ ] Prepare Q&A responses

**Output**: Demo-ready presentation materials

---

### Day 7: November 3
**Goal**: Sprint 1 Demo! 🎉

**Demo Flow**:
1. Show workflow architecture (4 steps)
2. Demonstrate user intake (live or recorded)
3. Show research synthesis output
4. **Highlight RAG integration** - explain knowledge base
5. Show generated script (with RAG-informed techniques)
6. Show safety gate evaluation (5.0/5)
7. Discuss metrics and quality improvements
8. Preview Sprint 2 (voice synthesis)

---

## Content Curation Priority (Day 1)

### Phase 1: Complete Scripts (Target: 5 total)
1. ✅ Confidence in Public Speaking
2. ⏭️ Deep Relaxation and Stress Management
3. ⏭️ Self-Compassion and Inner Critic Work
4. ⏭️ Performance Excellence - Flow State
5. ⏭️ Emotional Regulation and Resilience

### Phase 2: Core Techniques (Target: 10)
**Induction Methods** (3):
1. ⏭️ Progressive Muscle Relaxation (PMR)
2. ⏭️ Breath-Counting Induction
3. ⏭️ Staircase Descent Visualization

**Deepening Methods** (3):
4. ⏭️ Countdown Deepening (10→1)
5. ⏭️ Fractionation Technique
6. ⏭️ Elevator/Escalator Going Down

**Core Work Methods** (2):
7. ⏭️ Mental Rehearsal and Future Pacing
8. ⏭️ Resource State Anchoring

**Awakening Methods** (2):
9. ⏭️ Count-Up Awakening (1→5)
10. ⏭️ Grounding and Re-orientation

### Phase 3: Language Patterns (Target: 15)
**Ericksonian Patterns** (5):
1. ⏭️ Embedded Commands
2. ⏭️ Presuppositions
3. ⏭️ Metaphoric Language
4. ⏭️ Temporal Binding
5. ⏭️ Pacing and Leading

**NLP Patterns** (5):
6. ⏭️ Reframing Techniques
7. ⏭️ Anchoring Methods
8. ⏭️ Submodality Shifts
9. ⏭️ Meta-Model Language
10. ⏭️ Sensory Predicates (V-A-K)

**Permissive Language** (5):
11. ⏭️ Permission-Based Suggestions
12. ⏭️ "You Can" Patterns
13. ⏭️ "You Might Notice" Patterns
14. ⏭️ "Perhaps/Maybe" Softeners
15. ⏭️ Open-Ended Invitations

### Phase 4: Archetypes (Target: 5)
1. ⏭️ Leader/Ruler Archetype
2. ⏭️ Sage/Teacher Archetype
3. ⏭️ Warrior Archetype
4. ⏭️ Caregiver/Healer Archetype
5. ⏭️ Creator/Artist Archetype

### Phase 5: Best Practices (Target: 5)
1. ⏭️ Safety Protocols and Awakening Requirements
2. ⏭️ Permissive vs. Authoritarian Language
3. ⏭️ Contraindications for Self-Hypnosis
4. ⏭️ Grounding and Emotional Containment
5. ⏭️ Ethical Guidelines for Suggestions

### Phase 6: Neuroscience (Target: 5)
1. ⏭️ Mental Rehearsal and Motor Cortex Activation
2. ⏭️ Theta States and Neuroplasticity
3. ⏭️ Amygdala Regulation and Vagal Tone
4. ⏭️ Default Mode Network in Trance
5. ⏭️ Predictive Coding and Future Pacing

**Total**: 45 documents

---

## Success Criteria

### Minimum Viable RAG (for demo):
- [x] 40+ curated documents ✅
- [ ] Working ChromaDB with embeddings
- [ ] Retrieval returns relevant content (similarity >0.7)
- [ ] Step 3 successfully integrates RAG context
- [ ] At least 1 test showing quality improvement with RAG

### Stretch Goals:
- [ ] 60+ documents
- [ ] All 3 test scenarios re-run with RAG
- [ ] Quantified improvement metrics (before/after)
- [ ] RAG query optimization for different skill types
- [ ] Visual dashboard showing retrieval

---

## Technical Stack

**Vector Database**: ChromaDB (local, Python)
**Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`
**Python Dependencies**:
```
chromadb==0.4.15
sentence-transformers==2.2.2
```

**Integration Point**: Step 3 script generation prompt receives RAG context as additional input alongside research from Step 2.

---

## Risk Mitigation

**Risk 1**: Content curation takes longer than expected
- **Mitigation**: Prioritize quality over quantity; 40 documents sufficient for MVP

**Risk 2**: Retrieval quality poor (irrelevant results)
- **Mitigation**: Test early (Day 2), refine queries and metadata

**Risk 3**: Integration breaks existing workflow
- **Mitigation**: Keep RAG optional; workflow works with or without it

**Risk 4**: Time runs out before demo
- **Mitigation**: Clear daily milestones; each day produces usable increment

---

## Day 1 Action Plan (TODAY)

**Session 1 (2-3 hours)**: Complete Scripts
- Create 4 more complete hypnosis scripts
- Rich metadata for each
- Tested for safety and quality

**Session 2 (2-3 hours)**: Techniques and Patterns
- Write 10 technique cards
- Write 15 language pattern examples
- Clear, actionable formats

**Session 3 (1-2 hours)**: Archetypes and Guidelines
- Create 5 archetypal profiles
- Write 5 best practice guidelines
- Write 5 neuroscience insights

**End of Day 1 Target**: 45 curated documents ready for embedding

---

**Status**: Day 1 in progress
**Next Immediate Task**: Continue curating content (scripts, techniques, patterns)
