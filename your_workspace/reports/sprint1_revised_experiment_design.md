# Sprint 1 Revised Experiment Design: Voice Authenticity Validation

**Created**: 2025-10-22
**Revised Focus**: Test whether AI can generate engaging, Socratic-style content in our authentic voice before building full pipeline

---

## Core Assumption Being Tested

**Primary Hypothesis:**
"An AI pipeline combining RAG (Vector DB) + Deep Research can generate engaging, Socratic-style articles with an authentic voice that readers cannot reliably distinguish from human-written content, requiring minimal editing (<30 min) to match BehaviorShift's voice and quality standards."

**Why This Is The Critical Risk:**
The biggest uncertainty isn't whether AI can synthesize research or create lesson plans—it's whether it can do so in a voice that feels authentic, engaging, and Socratic (not generic AI writing). If we can't solve the voice problem, the rest of the pipeline doesn't matter because the content won't be usable.

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

### Phase 2: Initial Generation Test (Days 2-3)

**Objective:** Generate first article and identify voice/authenticity issues

**Tasks:**

**Day 2: Generate Article**
1. Run RAG + Deep Research on test topic
2. Synthesize into complete article using voice-focused prompt
3. Aim for 1500-2500 words
4. Include:
   - Thought-provoking questions throughout
   - At least 2 stories/metaphors
   - Reflection prompts
   - Natural insights emergence (not prescriptive)

**Day 3: Internal Evaluation**
1. Read article yourself with critical eye
2. Compare to your authentic writing samples
3. Score on key dimensions (1-5 scale):
   - **Authentic Voice**: Does it sound like BehaviorShift? (Target: 4+)
   - **Engagement**: Would a reader stay engaged? (Target: 4+)
   - **Socratic Quality**: Does it guide vs. tell? (Target: 4+)
   - **AI Detection**: How obvious is it that AI wrote this? (Target: 2 or less)
   - **Groundedness**: Citations and evidence quality (Target: 4+)

4. Document specific issues:
   - What phrases/patterns feel "AI"?
   - Where does the Socratic approach fail?
   - What's missing from authentic voice?
   - What actually works well?

**Success Criteria for Phase 2:**
- Complete article generated with citations
- Internal scores average 3+ (baseline quality)
- Specific voice issues identified for iteration

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

### Phase 4: Iteration & Validation (Days 6-7)

**Objective:** Refine prompt and re-test to validate improvements

**Tasks:**

**Day 6: Refine Synthesis Approach**
1. Based on feedback, identify prompt improvements:
   - Add examples of authentic phrasing
   - Strengthen Socratic question guidelines
   - Remove patterns that signal "AI writing"
   - Add voice guardrails (avoid certain words/phrases)

2. Consider hybrid approach if needed:
   - AI generates research + structure
   - Human adds voice in editing pass
   - Measure editing time

3. Generate second version of article with refined prompt

**Day 7: Final Validation**
1. Internal evaluation of v2:
   - Score on same 5 dimensions
   - Compare to v1 scores
   - Measure improvement

2. Quick validation with 1-2 testers:
   - "Does this version feel more authentic?"
   - Blind test if possible

3. Calculate total editing time needed:
   - If AI output needs <30 min to match voice: SUCCESS
   - If needs 30-60 min: MARGINAL (consider hybrid)
   - If needs >60 min: FAIL (pivot needed)

**Success Criteria for Phase 4:**
- v2 shows measurable improvement over v1
- Voice authenticity rated 4+/5
- Editing time <30 min per article
- Clear path to full pipeline implementation

---

## Success Metrics

### Primary Metrics:

**Voice Authenticity (Most Critical):**
- Internal rating: 4+/5 on authentic voice dimension
- External blind test: >40% of testers confused about AI vs. human
- Testers can't identify specific "AI tells" in final version
- Target: Feels like BehaviorShift brand voice

**Socratic Quality:**
- Questions provoke genuine reflection (rated 4+/5)
- Reader naturally arrives at insights (not told)
- Stories/metaphors feel purposeful, not decorative
- Target: Guides reader to self-discovery

**Usability:**
- Editing time: <30 minutes per article to match voice
- Changes needed: Minor tweaks vs. major rewrites
- Groundedness maintained: 4+/5 (citations intact)
- Target: AI draft is 80%+ ready

### Secondary Metrics:

**Engagement:**
- Would reader stay engaged? (4+/5)
- Questions feel relevant, not generic
- Flow is natural, not formulaic

**Efficiency:**
- Total generation time: <5 minutes for research + synthesis
- Iteration time: <1 hour per feedback cycle
- Demonstrates time savings potential

---

## Success Criteria

### Experiment Succeeds If:
- [ ] Voice authenticity rated 4+/5 by internal team
- [ ] External testers achieve >40% confusion rate (can't distinguish AI from human)
- [ ] Socratic approach rated 4+/5 (questions guide to insights)
- [ ] Editing time is <30 minutes per article
- [ ] Specific voice issues have clear solutions (better prompts, examples)
- [ ] Team has confidence to proceed with full Sprint 1 pipeline

### Experiment Fails If:
- [ ] Voice authenticity consistently rated <3/5
- [ ] External testers reliably identify AI writing (>80% accuracy)
- [ ] Editing time exceeds 60 minutes (faster to write from scratch)
- [ ] Socratic approach doesn't work (questions feel generic/forced)
- [ ] Voice issues have no clear solution path

### Mixed Results (Requires Pivot):
- [ ] Voice is good but Socratic approach needs work → Focus on question design
- [ ] Content quality good but voice needs heavy editing → Consider hybrid model
- [ ] Some topics work, others don't → Narrow scope for MVP
- [ ] Time savings marginal → Re-evaluate ROI vs. manual creation

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
1. Research synthesis article (1500-2500 words)
2. Includes 3-5 thought-provoking reflection questions
3. Contains 2+ stories/metaphors to illustrate concepts
4. Guides reader to discover insights about their relationship
5. Maintains authentic BehaviorShift voice throughout

---

## Deliverables

### Voice Calibration Artifacts:
- [ ] 3-5 authentic BehaviorShift writing samples (documented)
- [ ] Voice characteristics guide (what makes our voice distinctive)
- [ ] Socratic approach guidelines (how we guide to insights)
- [ ] Voice-focused synthesis prompt (v1)

### Test Outputs:
- [ ] AI-generated article v1 (with internal scores)
- [ ] Blind test document for external testers
- [ ] Tester feedback summary (quantitative + qualitative)
- [ ] AI-generated article v2 (refined based on feedback)
- [ ] Final evaluation scores (comparison v1 vs. v2)

### Decision Documentation:
- [ ] Voice authenticity validation report
- [ ] Go/No-Go recommendation for full pipeline
- [ ] Specific prompt improvements identified
- [ ] Hybrid approach requirements (if needed)
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

**What We Still Need To Validate:**
- Curriculum architecture quality (Step 2) - but less risky
- LLM-as-a-Judge effectiveness (Gate 1) - technical validation
- End-to-end pipeline integration - can test after voice proven
- Multiple topic coverage - expand in full pipeline testing

---

## Key Insight

**Why This Experiment Order Matters:**

If we build the full pipeline first and THEN discover the voice problem, we've invested 2 weeks in infrastructure that produces unusable content.

By testing voice authenticity FIRST in 5-7 days, we either:
- **Succeed**: Proceed with confidence, knowing the content will be usable
- **Fail fast**: Pivot to hybrid model or different approach with minimal time lost
- **Learn**: Understand exactly what prompt/approach changes are needed

This follows the principle: **Test the riskiest assumption first.**
