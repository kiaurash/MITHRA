# Sprint 1 Revised Experiment Design: Voice Authenticity Validation

**Created**: 2025-10-22
**Revised Focus**: Test whether AI can generate engaging, Socratic-style content in our authentic voice before building full pipeline

---

## Core Assumption Being Tested

**Primary Hypothesis:**
"An AI pipeline combining RAG (Vector DB) + Deep Research can generate engaging, Socratic-style articles with an authentic voice that readers cannot reliably distinguish from human-written content, AND Gate 1 (LLM-as-a-Judge) can reliably validate voice authenticity and groundedness, AND Step 2 can transform validated research into quality learning objectives and lesson plans - all requiring minimal editing (<30 min per component) to match BehaviorShift's standards."

**Why This Is The Critical Risk:**
The biggest uncertainty isn't whether AI can synthesize research or create lesson plans—it's whether it can do so in a voice that feels authentic, engaging, and Socratic (not generic AI writing). We also need to validate that:
1. Gate 1 can catch voice authenticity issues (not just groundedness)
2. Step 2 can transform voice-authentic research into quality curriculum
3. The end-to-end flow (Step 1 → Gate 1 → Step 2) produces usable outputs

If we can't solve the voice problem OR validate the quality gates, the rest of the pipeline doesn't matter because the content won't be usable.

---

## Experiment Design

### Phase 1: Voice Calibration (Day 1)

**Objective:** Prepare the AI with examples of authentic BehaviorShift voice

**Tasks:**
1. **Gather Voice Samples:**
   - Collect 3-5 examples of authentic BehaviorShift writing
   - Identify what makes the voice distinctive:
     - Tone (warm, introspective, non-judgmental?)
     - Structure (questions, stories, metaphors)
     - Language patterns (word choice, sentence rhythm)
   - Note what makes content "Socratic":
     - Thought-provoking questions that invite reflection
     - Examples/stories/metaphors that guide reader to insights
     - Avoids telling, helps reader discover
     - Creates space for self-reflection

2. **Create Voice-Focused Synthesis Prompt:**
   - Incorporate voice characteristics into Step 1 prompt
   - Add explicit instructions for Socratic approach
   - Include examples of authentic voice
   - Specify what to avoid (generic AI writing, didactic tone)

3. **Setup for Testing:**
   - Choose ONE test topic: "Improving emotional intimacy in long-term relationships"
   - Prepare 10-15 curated sources in Vector DB
   - Set up Deep Research with 3-5 quality sources
   - Configure LLM API with voice-focused prompt

**Success Criteria for Phase 1:**
- Voice samples clearly identified and documented
- Synthesis prompt includes voice guidance and examples
- Test infrastructure ready (Vector DB, API, sources)

---

### Phase 2: Initial Generation and Validation Test (Days 2-3)

**Objective:** Generate first article, validate through Gate 1, and create curriculum (Step 2)

**Tasks:**

**Day 2: Generate Article and Run Gate 1**
1. Run RAG + Deep Research on test topic (Step 1)
2. Synthesize into complete article using voice-focused prompt
3. Aim for 1500-2500 words
4. Include:
   - Thought-provoking questions throughout
   - At least 2 stories/metaphors
   - Reflection prompts
   - Natural insights emergence (not prescriptive)

5. **NEW: Run Gate 1 Validation (LLM-as-a-Judge)**
   - Submit article to Gate 1 prompt
   - Evaluate: Groundedness, Relevance, Voice Authenticity, Socratic Quality
   - Record Gate 1 verdict: PASS/MARGINAL/FAIL
   - Capture specific feedback from Gate 1

6. **NEW: Generate Curriculum (Step 2)**
   - If Gate 1 PASS: Submit article to Step 2 prompt
   - Generate learning objectives using Bloom's Taxonomy
   - Create lesson plan structure
   - Design practice activities

**Day 3: Comprehensive Internal Evaluation**
1. **Evaluate Step 1 Output (Article):**
   - Read article yourself with critical eye
   - Compare to your authentic writing samples
   - Score on key dimensions (1-5 scale):
     - **Authentic Voice**: Does it sound like BehaviorShift? (Target: 4+)
     - **Engagement**: Would a reader stay engaged? (Target: 4+)
     - **Socratic Quality**: Does it guide vs. tell? (Target: 4+)
     - **AI Detection**: How obvious is it that AI wrote this? (Target: 2 or less)
     - **Groundedness**: Citations and evidence quality (Target: 4+)

2. **Evaluate Gate 1 Performance:**
   - Did Gate 1 catch actual voice issues? (true positives)
   - Did Gate 1 miss any obvious issues? (false negatives)
   - Were Gate 1 issues flagged accurately?
   - Is Gate 1 feedback actionable?
   - Gate 1 accuracy score (1-5): How reliable is the validation?

3. **Evaluate Step 2 Output (Curriculum):**
   - Are learning objectives clear and well-structured?
   - Do objectives follow Bloom's Taxonomy appropriately?
   - Is lesson plan structure logical and pedagogically sound?
   - Are practice activities aligned with objectives?
   - Curriculum quality score (1-5): Ready to teach from?

4. **Document specific issues across all components:**
   - **Step 1 issues**: What phrases/patterns feel "AI"? Where does Socratic approach fail?
   - **Gate 1 issues**: What did it miss? What false positives?
   - **Step 2 issues**: What curriculum elements need improvement?
   - **What actually works well** in each component?

**Success Criteria for Phase 2:**
- Complete article generated with citations (Step 1)
- Gate 1 runs successfully and provides feedback
- Curriculum generated from validated article (Step 2)
- Internal scores average 3+ across all components (baseline quality)
- Specific issues identified for iteration at each stage
- Gate 1 accuracy rated 3+ (catches major issues)

---

### Phase 3: External Blind Test (Days 4-5)

**Objective:** Get objective feedback from taste-testers on voice authenticity

**Tasks:**

**Day 4: Prepare Blind Test**
1. Select 1-2 paragraphs from AI-generated article
2. Select 1-2 comparable paragraphs from your authentic writing on similar topic
3. Create blind test document:
   - Mix AI and human samples
   - Don't label which is which
   - Ask testers to identify: "Which samples feel more authentic/engaging?"
   - Ask open-ended: "What makes certain samples better?"

4. Send to 3-4 taste-testers:
   - Good writers in your network
   - Interested in soft skills/relationship topics
   - Appreciate quality writing
   - Ask for feedback within 24 hours

**Day 5: Analyze Results**
1. Collect tester feedback
2. Calculate: How many correctly identified AI vs. human?
3. Review qualitative feedback:
   - What specific language/patterns gave it away?
   - What did testers like/dislike?
   - Did Socratic questions land well?

4. Synthesize findings:
   - Is voice issue fixable with better prompts?
   - What specific changes would improve authenticity?
   - Are there patterns in what works vs. doesn't?

**Success Criteria for Phase 3:**
- At least 3 testers provide feedback
- Testers can't reliably distinguish AI from human (>40% confusion rate acceptable)
- Specific, actionable feedback collected

---

### Phase 4: Iteration & End-to-End Validation (Days 6-7)

**Objective:** Refine prompts across all components and re-test complete pipeline

**Tasks:**

**Day 6: Refine All Prompts Based on Feedback**
1. **Refine Step 1 (Article Generation) Prompt:**
   - Add examples of authentic phrasing
   - Strengthen Socratic question guidelines
   - Remove patterns that signal "AI writing"
   - Add voice guardrails (avoid certain words/phrases)

2. **Refine Gate 1 (Validation) Prompt if needed:**
   - If Gate 1 missed issues: strengthen evaluation criteria
   - If false positives: clarify what's acceptable
   - Ensure voice authenticity criteria are clear

3. **Refine Step 2 (Curriculum) Prompt if needed:**
   - If objectives unclear: add examples
   - If lesson structure weak: strengthen pedagogical guidelines
   - Ensure alignment with BehaviorShift teaching philosophy

4. **Consider hybrid approach if needed:**
   - AI generates research + structure
   - Human adds voice in editing pass
   - Measure editing time per component

5. **Generate second version of complete pipeline:**
   - Run Step 1 v2 (article generation)
   - Run Gate 1 on v2 article
   - If PASS: Run Step 2 v2 (curriculum generation)

**Day 7: Final End-to-End Validation**
1. **Internal evaluation of v2 pipeline:**
   - Score Step 1 output on same 5 dimensions
   - Score Gate 1 accuracy (catching real issues)
   - Score Step 2 curriculum quality
   - Compare all scores to v1
   - Measure improvement across components

2. **Quick validation with 1-2 testers:**
   - "Does this version feel more authentic?" (Step 1)
   - "Are learning objectives clear and useful?" (Step 2)
   - Blind test if possible

3. **Calculate total editing time needed:**
   - Step 1 article: If needs <30 min to match voice → SUCCESS
   - Gate 1 validation: If accurately catches issues → SUCCESS
   - Step 2 curriculum: If needs <30 min refinement → SUCCESS
   - **Total pipeline**: If needs 30-60 min: MARGINAL (consider hybrid)
   - **Total pipeline**: If needs >60 min: FAIL (pivot needed)

4. **Test retry logic:**
   - If Gate 1 FAILS article: Can we improve and retry successfully?
   - Does feedback loop work (Gate 1 feedback → Step 1 revision)?

**Success Criteria for Phase 4:**
- v2 shows measurable improvement over v1 across all components
- Step 1 voice authenticity rated 4+/5
- Gate 1 accuracy rated 4+/5 (reliable validation)
- Step 2 curriculum quality rated 4+/5
- Total editing time <60 min for complete pipeline
- Retry logic works (failed article can be improved)
- Clear path to full pipeline implementation

---

## Success Metrics

### Primary Metrics:

**Step 1: Voice Authenticity (Most Critical):**
- Internal rating: 4+/5 on authentic voice dimension
- External blind test: >40% of testers confused about AI vs. human
- Testers can't identify specific "AI tells" in final version
- Target: Feels like BehaviorShift brand voice

**Step 1: Socratic Quality:**
- Questions provoke genuine reflection (rated 4+/5)
- Reader naturally arrives at insights (not told)
- Stories/metaphors feel purposeful, not decorative
- Target: Guides reader to self-discovery

**Gate 1: Validation Accuracy (NEW):**
- Catches actual voice issues (true positive rate >80%)
- Doesn't flag good content (false positive rate <20%)
- Feedback is specific and actionable
- Accuracy score: 4+/5 (reliable judge)
- Target: Trustworthy quality gate

**Step 2: Curriculum Quality (NEW):**
- Learning objectives clear and well-structured (4+/5)
- Follows Bloom's Taxonomy appropriately
- Lesson plan structure is pedagogically sound (4+/5)
- Practice activities align with objectives
- Target: Ready to teach from with minimal edits

**Pipeline Usability:**
- Step 1 editing time: <30 minutes per article to match voice
- Step 2 editing time: <30 minutes per curriculum
- Total pipeline editing time: <60 minutes
- Changes needed: Minor tweaks vs. major rewrites
- Groundedness maintained: 4+/5 (citations intact)
- Target: Complete pipeline output is 80%+ ready

### Secondary Metrics:

**Engagement:**
- Would reader stay engaged? (4+/5)
- Questions feel relevant, not generic
- Flow is natural, not formulaic

**Efficiency:**
- Step 1 generation time: <5 minutes for research + synthesis
- Gate 1 validation time: <2 minutes
- Step 2 generation time: <3 minutes
- Total pipeline time: <10 minutes end-to-end
- Iteration time: <1 hour per feedback cycle
- Demonstrates time savings potential

**Retry Logic:**
- Failed articles can be improved and pass on retry
- Gate 1 feedback leads to successful revisions
- Maximum 2 retries needed to achieve PASS

---

## Success Criteria

### Experiment Succeeds If:
- [ ] **Step 1**: Voice authenticity rated 4+/5 by internal team
- [ ] **Step 1**: External testers achieve >40% confusion rate (can't distinguish AI from human)
- [ ] **Step 1**: Socratic approach rated 4+/5 (questions guide to insights)
- [ ] **Step 1**: Editing time is <30 minutes per article
- [ ] **Gate 1**: Validation accuracy rated 4+/5 (reliable quality gate)
- [ ] **Gate 1**: Catches >80% of voice issues, <20% false positives
- [ ] **Step 2**: Curriculum quality rated 4+/5 (clear objectives, sound pedagogy)
- [ ] **Step 2**: Editing time is <30 minutes per curriculum
- [ ] **Pipeline**: Complete flow works (Step 1 → Gate 1 → Step 2)
- [ ] **Pipeline**: Total editing time <60 minutes for all components
- [ ] **Pipeline**: Retry logic works (failed content can be improved)
- [ ] Specific voice issues have clear solutions (better prompts, examples)
- [ ] Team has confidence to proceed with full Sprint 1 implementation

### Experiment Fails If:
- [ ] **Step 1**: Voice authenticity consistently rated <3/5
- [ ] **Step 1**: External testers reliably identify AI writing (>80% accuracy)
- [ ] **Step 1**: Socratic approach doesn't work (questions feel generic/forced)
- [ ] **Gate 1**: Misses obvious issues (accuracy <3/5)
- [ ] **Gate 1**: High false positive rate (>40% flags good content)
- [ ] **Step 2**: Curriculum quality poor (<3/5)
- [ ] **Pipeline**: Total editing time exceeds 90 minutes (faster to do manually)
- [ ] **Pipeline**: Retry logic fails (can't improve failed content)
- [ ] Voice issues have no clear solution path
- [ ] Quality gates unreliable (can't trust automation)

### Mixed Results (Requires Pivot):
- [ ] **Step 1**: Voice is good but Socratic approach needs work → Focus on question design
- [ ] **Step 1**: Content quality good but voice needs heavy editing → Consider hybrid model
- [ ] **Gate 1**: Catches issues but feedback not actionable → Refine evaluation criteria
- [ ] **Gate 1**: Too strict (high false positives) → Calibrate thresholds
- [ ] **Step 2**: Objectives good but lesson structure weak → Strengthen pedagogical prompts
- [ ] **Pipeline**: Some steps work, others don't → Identify where human input needed
- [ ] Some topics work, others don't → Narrow scope for MVP
- [ ] Time savings marginal (60-90 min total) → Re-evaluate ROI vs. manual creation

---

## Test Scenario

**Topic:** "Improving emotional intimacy in long-term relationships"

**User Context:** Married for 10 years, feeling disconnected, want to rebuild closeness

**Why This Topic:**
- Representative of BehaviorShift target content
- Well-researched area (good sources available)
- You likely have authentic writing samples on similar themes
- Emotional depth tests Socratic approach

**Expected Outputs:**

**From Step 1 (Knowledge Synthesis):**
1. Research synthesis article (1500-2500 words)
2. Includes 3-5 thought-provoking reflection questions
3. Contains 2+ stories/metaphors to illustrate concepts
4. Guides reader to discover insights about their relationship
5. Maintains authentic BehaviorShift voice throughout
6. Properly cited sources (groundedness)

**From Gate 1 (Validation):**
1. Pass/Marginal/Fail verdict with reasoning
2. Groundedness assessment (source citation quality)
3. Relevance assessment (topic alignment)
4. Voice authenticity assessment (BehaviorShift voice quality)
5. Socratic quality assessment (guides vs. tells)
6. Specific, actionable feedback if FAIL or MARGINAL

**From Step 2 (Curriculum Architecture):**
1. 3-5 clear learning objectives using Bloom's Taxonomy
2. Lesson plan structure (5-part: Engage → Explore → Reflect → Apply → Integrate)
3. Practice activities aligned with objectives
4. Teaching points that maintain Socratic approach
5. JSON and Markdown formatted outputs

---

## Deliverables

### Voice Calibration Artifacts:
- [ ] 3-5 authentic BehaviorShift writing samples (documented)
- [ ] Voice characteristics guide (what makes our voice distinctive)
- [ ] Socratic approach guidelines (how we guide to insights)
- [ ] Voice-focused synthesis prompt (v1)

### Test Outputs:
- [ ] **Step 1 v1**: AI-generated article (with internal scores)
- [ ] **Gate 1 v1**: Validation report (verdict + feedback)
- [ ] **Step 2 v1**: Curriculum/lesson plan (with quality scores)
- [ ] **External Test**: Blind test document for external testers
- [ ] **Feedback**: Tester feedback summary (quantitative + qualitative)
- [ ] **Step 1 v2**: Refined article (based on all feedback)
- [ ] **Gate 1 v2**: Validation report for refined article
- [ ] **Step 2 v2**: Refined curriculum (if Gate 1 passes v2)
- [ ] **Comparison**: Final evaluation scores (v1 vs. v2 across all components)

### Pipeline Testing Artifacts:
- [ ] End-to-end flow documentation (Step 1 → Gate 1 → Step 2)
- [ ] Retry logic test results (failed article → revised → passed)
- [ ] Gate 1 accuracy analysis (true positives, false positives, false negatives)
- [ ] Editing time breakdown (per component and total)
- [ ] Component integration report (how well outputs feed into next step)

### Decision Documentation:
- [ ] Voice authenticity validation report (Step 1 quality)
- [ ] Gate 1 reliability report (validation accuracy and trustworthiness)
- [ ] Curriculum quality report (Step 2 pedagogical soundness)
- [ ] Complete pipeline evaluation (end-to-end usability)
- [ ] Go/No-Go recommendation for full Sprint 1 implementation
- [ ] Specific prompt improvements identified (all components)
- [ ] Hybrid approach requirements (if needed, per component)
- [ ] Next steps for Sprint 1 implementation

---

## Timeline

**Total Duration:** 5-7 days (1 week)

**Day 1:** Voice calibration and setup
**Days 2-3:** Generate and internally evaluate first version
**Days 4-5:** External blind test and feedback collection
**Days 6-7:** Iterate, refine, validate improvements

**Target Completion:** Week of Oct 28, 2025
**Decision Point:** End of Day 7 - Go/No-Go for full pipeline

---

## Next Steps Based on Outcomes

### If Experiment Succeeds:

**Immediate Actions:**
1. Document successful voice prompt patterns
2. Expand Vector DB with 20-30 curated sources
3. Build full Sprint 1 pipeline:
   - Step 0: User Context Ingestion (Streamlit UI)
   - Step 1: Knowledge Synthesis (validated approach)
   - Gate 1: Groundedness Judge
   - Step 2: Curriculum Architecture

4. Test full pipeline with 2 additional scenarios
5. Prepare Sprint 1 demo (Nov 3 target)

**What We've De-Risked:**
- Voice authenticity (biggest uncertainty)
- Socratic approach viability
- AI's ability to write in brand voice
- Editing time is reasonable

---

### If Experiment Fails:

**Pivot Options:**

**Option A: Hybrid Model**
- AI handles research synthesis and structure
- Human adds voice in dedicated editing pass
- Measure if this still saves time vs. full manual

**Option B: Constrained Scope**
- AI generates "research briefs" not full articles
- Human writes Socratic content from AI brief
- Reduces AI voice challenge, keeps research automation

**Option C: Focus on Later Sprints**
- Skip Sprint 1 article generation
- Focus on Sprint 2 (narrative/story selection)
- Sprint 3 (therapeutic scripting - different voice needs)
- Revisit cognitive content later

**Analysis to Conduct:**
- Was failure due to prompting, model choice, or fundamental limitation?
- Would better voice samples help?
- Is Socratic style fundamentally hard for AI?
- What CAN AI do well that we can leverage?

---

### If Mixed Results:

**Iteration Options:**

**If voice is close but not quite there:**
- Collect more voice samples
- Create "voice rubric" with specific do's/don'ts
- Test different LLM models (Claude vs. GPT-4)
- Add post-processing "voice cleanup" step

**If Socratic approach needs work:**
- Study examples of great Socratic questions
- Create question templates/frameworks
- Focus on one aspect (questions OR stories, not both)
- Consider human collaboration on question design

**If some topics work better than others:**
- Identify which topics AI handles well
- Start with those for MVP
- Build confidence before expanding scope

---

## Risk Mitigation

### Risk 1: Taste-testers too easy to please
**Mitigation:**
- Include critical readers who write well themselves
- Use blind testing methodology
- Ask specific questions about authenticity
- Compare to your best manual work, not average

### Risk 2: One week not enough for meaningful iteration
**Mitigation:**
- Front-load voice calibration (Day 1)
- Get fast feedback cycles (24hr turnaround from testers)
- Be willing to extend to 10 days if mixed results
- Prioritize learning over completion

### Risk 3: Voice issue is unfixable with prompts
**Mitigation:**
- Have hybrid model as backup plan
- Test multiple prompt approaches quickly
- Consider if different AI model would help
- Recognize early if pivot needed

### Risk 4: Experiment too narrow (only one topic)
**Mitigation:**
- Choose representative topic carefully
- If succeeds easily, test second topic in Days 6-7
- Document what makes topics work well
- Plan broader testing for full pipeline phase

---

## Notes for Full Sprint 1 Pipeline

**If Voice Validation Succeeds, We'll Know:**
1. Specific prompt patterns that preserve authentic voice
2. How much editing time is realistic per article
3. Whether Socratic approach translates to AI generation
4. What voice characteristics are easiest/hardest for AI

**Use These Learnings To:**
- Refine Step 1 prompt in full pipeline
- Set realistic quality expectations for Sprint 1 demo
- Decide if hybrid approach needed for certain content types
- Plan voice consistency across Sprint 2 (narrative) and Sprint 3 (therapeutic)

**What We've Validated in This Experiment:**
- Step 1: Voice authenticity and Socratic quality (THE critical risk)
- Gate 1: LLM-as-a-Judge effectiveness for voice validation
- Step 2: Curriculum architecture quality (learning objectives, lesson plans)
- Pipeline: End-to-end integration (Step 1 → Gate 1 → Step 2)
- Retry logic: Can failed content be improved and revalidated?

**What We Still Need To Validate (Full Pipeline Phase):**
- Multiple topic coverage (test with 2-3 additional scenarios)
- Sprint 2 components (narrative weaving, story selection)
- Sprint 3 components (therapeutic scripting, voice synthesis)
- Scale testing (can we produce 10+ modules in parallel?)
- User testing (do learners find the content effective?)

---

## Key Insight

**Why This Experiment Scope Matters:**

If we build the full pipeline first and THEN discover the voice problem OR unreliable quality gates, we've invested 2+ weeks in infrastructure that produces unusable content or can't validate quality.

By testing the complete core pipeline (Step 1 → Gate 1 → Step 2) in 5-7 days, we validate:
1. **Voice authenticity** (THE critical risk for usability)
2. **Quality gate reliability** (can we trust automated validation?)
3. **Curriculum generation** (does pipeline produce teaching-ready outputs?)
4. **End-to-end integration** (do components work together?)

We either:
- **Succeed**: Proceed with confidence to full Sprint 1 implementation
- **Fail fast**: Pivot to hybrid model or different approach with minimal time lost
- **Learn**: Understand exactly what prompt/approach changes are needed per component

This follows the principle: **Test the riskiest assumptions first, in the smallest viable end-to-end slice.**

The expanded scope (from just Step 1 to Step 1 → Gate 1 → Step 2) is still achievable in 5-7 days because:
- Gate 1 validation takes <2 minutes per run (automated)
- Step 2 generation takes <3 minutes (automated)
- We gain confidence in THREE critical components instead of just one
- We validate the FLOW, not just individual pieces
