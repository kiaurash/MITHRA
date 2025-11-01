# Sprint 1 Experiment Design: Content Generation Pipeline

**Created**: 2025-10-21
**Sprint Goal**: Validate that the core knowledge synthesis and curriculum architecture pipeline can produce high-quality, personalized learning content

---

## Hypothesis

**Primary Hypothesis**:
A pipeline combining RAG (Vector DB) + Deep Research + LLM-as-a-Judge validation + Curriculum Architecture can generate personalized, research-grounded lesson plans that meet professional quality standards for behavioral learning content.

**Sub-Hypotheses**:
1. RAG from curated Vector DB will provide sufficient domain knowledge for soft skills topics
2. LLM-as-a-Judge can reliably validate content for groundedness and relevance
3. Curriculum architecture agent can transform research into actionable learning objectives and lesson plans
4. The complete pipeline can run end-to-end in under 5 minutes per topic

---

## Experiment Overview

### What We're Testing:
The complete Sprint 1 pipeline (Steps 0 → 1 → Gate 1 → 2) with real inputs to validate:
- Technical feasibility of each component
- Quality of outputs at each stage
- Effectiveness of quality gates
- End-to-end user experience

### What Success Looks Like:
A functional prototype that internal team members can use to generate lesson plans that require minimal human editing before being ready for Sprint 2 (narrative weaving).

---

## Test Scenarios

### Scenario 1: Primary Test Case
**Topic**: "Improving emotional intimacy in long-term relationships"
**User Context**: "Married for 10 years, feeling disconnected, want to rebuild closeness"
**Learning Goals**: "Understand what creates emotional intimacy and have practical ways to rebuild it"
**Style Preference**: Story-driven and metaphorical
**Philosophical Preference**: "Secular with mindfulness influences"

**Why This Test Case**:
- Representative of target use case
- Complex enough to test system capabilities
- Clear success criteria (intimacy is well-researched topic)

### Scenario 2: Edge Case - Narrow Topic
**Topic**: "Active listening in workplace conflicts"
**User Context**: "Manager dealing with team conflicts"
**Learning Goals**: "Learn to listen better when emotions are high"
**Style Preference**: Practical and action-oriented
**Philosophical Preference**: None specified

**Why This Test Case**:
- Tests system with more specific, narrow topic
- Different style preference (practical vs. story-driven)
- Workplace context vs. personal relationship

### Scenario 3: Edge Case - Abstract Topic
**Topic**: "Building self-compassion"
**User Context**: "Struggle with self-criticism"
**Learning Goals**: "Be kinder to myself when I make mistakes"
**Style Preference**: Reflective and introspective
**Philosophical Preference**: "Buddhism and meditation"

**Why This Test Case**:
- More abstract/internal topic
- Tests philosophical preference matching
- Reflective style requires different approach

---

## Success Metrics

### 1. Technical Metrics

**Step 0: User Context Ingestion**
- ✅ **Pass**: Form captures all inputs correctly
- ✅ **Pass**: Data structured as valid JSON
- ⏱️ **Target**: < 30 seconds user input time

**Step 1: Knowledge Synthesis**
- ✅ **Pass**: RAG returns 10+ relevant sources with similarity > 0.7
- ✅ **Pass**: Deep Research finds 5+ quality external sources
- ✅ **Pass**: Article length 1500-2500 words
- ✅ **Pass**: All major claims have inline citations
- ⏱️ **Target**: < 2 minutes generation time

**Gate 1: Groundedness Judge**
- ✅ **Pass**: Judge returns structured evaluation report
- ✅ **Pass**: Groundedness score accurately reflects citation quality
- ✅ **Pass**: Relevance score aligns with human assessment
- ✅ **Pass**: Judge catches 3+ citation issues when deliberately introduced
- ⏱️ **Target**: < 30 seconds evaluation time

**Step 2: Curriculum Architecture**
- ✅ **Pass**: Generates 5-6 learning objectives across Bloom's levels
- ✅ **Pass**: Creates 4-6 lessons with complete 5-part structure
- ✅ **Pass**: Outputs valid JSON and readable markdown
- ✅ **Pass**: Adapts to user's style preference (verify different outputs for different styles)
- ⏱️ **Target**: < 90 seconds generation time

**End-to-End Pipeline**
- ✅ **Pass**: Complete run without errors
- ⏱️ **Target**: < 5 minutes total time (excluding user input)

---

### 2. Quality Metrics

**Research Article Quality** (Human Evaluation):
Rate 1-5 on each dimension:
- [ ] **Groundedness**: Claims supported by credible sources (Target: 4+)
- [ ] **Relevance**: Addresses the topic thoroughly (Target: 4+)
- [ ] **Clarity**: Easy to understand for general audience (Target: 4+)
- [ ] **Depth**: Sufficient detail without overwhelming (Target: 4+)
- [ ] **Actionability**: Practical implications clear (Target: 4+)

**Curriculum Quality** (Human Evaluation):
Rate 1-5 on each dimension:
- [ ] **Objective Clarity**: Learning objectives are specific and measurable (Target: 4+)
- [ ] **Pedagogical Soundness**: Lessons follow good instructional design (Target: 4+)
- [ ] **Progression**: Concepts build logically (Target: 4+)
- [ ] **Practical Application**: Activities are actionable (Target: 4+)
- [ ] **Personalization**: Adapted to user's style and context (Target: 4+)

**Overall Usability**:
- [ ] **Editing Required**: Minimal (< 20% of content needs changes) (Target: Yes)
- [ ] **Sprint 2 Ready**: Content suitable for adding narrative layer (Target: Yes)
- [ ] **Professional Quality**: Comparable to manually-created curriculum (Target: 4+/5)

---

### 3. Gate Effectiveness Metrics

**Gate 1 Validation**:

Test with **intentionally flawed** research articles:
- [ ] **Test 1**: Article with unsupported claims → Judge catches 100% of issues
- [ ] **Test 2**: Article with weak sources → Judge flags as "MARGINAL" or "FAIL"
- [ ] **Test 3**: Article off-topic → Judge fails relevance check
- [ ] **Test 4**: High-quality article → Judge passes without false positives

**False Positive Rate**: Target < 10% (doesn't fail good content)
**False Negative Rate**: Target < 5% (catches bad content)

---

## Experiment Procedure

### Phase 1: Setup (Week 1, Days 1-2)
1. **Vector DB Setup**:
   - Choose Vector DB: ChromaDB (local, easy for MVP)
   - Create collection: "relationship_soft_skills"
   - Embed 20-30 curated articles on intimacy, communication, emotional intelligence
   - Test retrieval with sample queries

2. **Deep Research Setup**:
   - Create curated website list (5-10 sources)
   - Test web scraping/API access
   - Verify content extraction works

3. **LLM API Setup**:
   - Configure API keys (Anthropic Claude or OpenAI GPT-4)
   - Test basic prompts
   - Set up error handling

4. **Streamlit UI Setup**:
   - Create basic form for Step 0
   - Test data capture and validation

### Phase 2: Component Testing (Week 1, Days 3-4)
1. **Test Step 0** with all 3 scenarios
2. **Test Step 1** (Knowledge Synthesis):
   - Run RAG agent standalone
   - Run Deep Research agent standalone
   - Test synthesis with combined inputs
   - Verify citation format
3. **Test Gate 1** with sample articles (good and intentionally bad)
4. **Test Step 2** with validated research article from Step 1

**Success Criteria for Phase 2**: Each component works in isolation with target metrics

### Phase 3: Integration Testing (Week 1, Day 5)
1. **End-to-End Test** with Scenario 1:
   - User inputs topic → full pipeline → final curriculum
   - Time each step
   - Record any errors or issues
2. **Human Evaluation**:
   - Review research article quality
   - Review curriculum quality
   - Note what works well and what needs improvement

### Phase 4: Edge Case Testing (Week 2, Days 1-2)
1. Run Scenario 2 (narrow topic) through pipeline
2. Run Scenario 3 (abstract topic) through pipeline
3. Compare outputs across different style preferences
4. Test Gate 1 with intentionally flawed content

### Phase 5: Iteration (Week 2, Days 3-4)
1. Address issues found in testing
2. Refine prompts based on output quality
3. Adjust quality gate thresholds if needed
4. Re-test with updated system

### Phase 6: Demo Preparation (Week 2, Day 5)
1. Polish UI for demo
2. Prepare 1-2 successful test runs
3. Document limitations and next steps
4. Create demo script

---

## Evaluation Method

### Quantitative Evaluation:
- **Automated Metrics**: Track technical metrics (timing, source counts, output lengths)
- **Gate Performance**: Test with 10 good + 10 bad articles, calculate precision/recall
- **Consistency**: Run same scenario 3 times, compare outputs for consistency

### Qualitative Evaluation:
- **Human Review Panel**: 2-3 internal team members
- **Rubric Scoring**: Use 1-5 scale for quality dimensions
- **Comparative Analysis**: Compare to manually-created curriculum on same topic
- **Think-Aloud Protocol**: Have team member use UI and speak their thoughts

### Documentation:
- **Testing Log**: Track all test runs, results, issues
- **Iteration Notes**: Document what changed and why
- **Final Report**: Summarize findings, metrics, recommendations

---

## Success Criteria

### Minimum Viable Success (MVP):
- [ ] All 3 test scenarios complete end-to-end without errors
- [ ] Technical metrics meet targets (timing, source counts)
- [ ] Quality ratings average 3.5+/5 across dimensions
- [ ] Gate 1 catches 80%+ of intentionally bad content
- [ ] Less than 30% of curriculum requires editing

### Stretch Goals:
- [ ] Quality ratings average 4+/5
- [ ] Gate 1 catches 95%+ of bad content with <10% false positives
- [ ] Less than 20% editing required
- [ ] System handles 5+ different topics successfully
- [ ] Processing time < 3 minutes end-to-end

### Go/No-Go Decision for Sprint 2:
**GO** if:
- MVP success criteria met
- Team confidence in foundation for Sprint 2
- No major technical blockers identified

**NO-GO** (iterate on Sprint 1) if:
- Significant quality issues (< 3.5 average rating)
- Gate 1 ineffective (>20% false negatives)
- Major technical failures or instability

---

## Risks and Mitigations

### Risk 1: Vector DB has insufficient content
**Impact**: RAG returns poor results
**Likelihood**: Medium
**Mitigation**:
- Start with 30+ high-quality curated articles
- Test retrieval before full experiment
- Fall back to Deep Research if RAG weak
- Plan to expand DB if successful

### Risk 2: LLM-as-a-Judge is inconsistent
**Impact**: Gate 1 lets bad content through or fails good content
**Likelihood**: Medium
**Mitigation**:
- Test judge with known good/bad examples
- Iterate on judge prompt for consistency
- Consider using Claude 3.5 Sonnet (strong at evaluation)
- Add manual review for Sprint 1 demos

### Risk 3: Curriculum quality varies by topic
**Impact**: Some topics work great, others poor
**Likelihood**: Medium-High
**Mitigation**:
- Test diverse topics (3 scenarios)
- Identify which types of topics work best
- Document scope limitations
- Plan to expand coverage in Sprint 2

### Risk 4: Processing time exceeds 5 minutes
**Impact**: Poor user experience
**Likelihood**: Low-Medium
**Mitigation**:
- Use streaming/progress indicators
- Optimize prompts for efficiency
- Consider async processing for production
- Acceptable for MVP if < 10 minutes

### Risk 5: Style personalization insufficient
**Impact**: All outputs feel similar regardless of preference
**Likelihood**: Medium
**Mitigation**:
- Test with all 4 style preferences
- Compare outputs side-by-side
- Iterate on Step 2 prompt if needed
- May defer deeper personalization to Sprint 2/3

---

## Timeline

**Week 1 (Days 1-5)**:
- Days 1-2: Setup and environment configuration
- Days 3-4: Component testing
- Day 5: Integration testing with Scenario 1

**Week 2 (Days 1-5)**:
- Days 1-2: Edge case testing (Scenarios 2-3)
- Days 3-4: Iteration and refinement
- Day 5: Demo preparation

**Target Demo Date**: End of Week 2 (Nov 3, 2025)

---

## Deliverables

### Experiment Artifacts:
1. **Test Results Log** (CSV or spreadsheet):
   - Test scenario, timestamp, metrics, pass/fail, notes
2. **Sample Outputs** (for each scenario):
   - User input JSON
   - Research article
   - Gate 1 evaluation report
   - Final curriculum (JSON + markdown)
3. **Human Evaluation Scores** (rubric scores for each scenario)
4. **Gate Performance Report** (precision/recall with test articles)

### Final Report:
1. **Executive Summary**: Key findings, go/no-go recommendation
2. **Metrics Dashboard**: All quantitative metrics
3. **Qualitative Findings**: What works, what needs improvement
4. **Lessons Learned**: Surprises, challenges, insights
5. **Recommendations for Sprint 2**: Specific improvements to make

### Demo Deliverable:
- Live demonstration with 1-2 successful end-to-end runs
- Streamlit UI showing full pipeline
- Commentary on quality and next steps

---

## Notes for Sprint 2 Planning

Based on this experiment, we'll learn:
- Which topics work best (informs content strategy)
- How much editing curricula need (informs Sprint 2 scope)
- Whether quality gates are effective (informs Gates 2-3 design)
- Processing time bottlenecks (informs architecture decisions)
- User experience pain points (informs UI improvements)

**Use this experiment to inform**:
- Sprint 2 narrative requirements
- Sprint 3 personalization depth
- Vector DB expansion needs
- Production architecture design
