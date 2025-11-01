# Evaluation Design Report - MITHRA

**Created:** 2025-10-29
**Workflow:** MITHRA - Personalized Research Learning Agent
**Status:** Proactive evaluation design (pre-testing)

---

## Participant Context

**Background:** Data science leadership with technical expertise in ML systems and building multi-agent architectures

**Sprint Status:** Week 2 of Sprint 1
- Original Sprint 1 Goal: BehaviorShift content generation pipeline
- Pivoted to: MITHRA research paper learning agent

**Recent Activity:**
- Completed full ideation workflow for MITHRA (2025-10-29)
- Generated complete 7-step workflow with all prompt files
- Designed 2-part experiment plan

---

## Current Evaluation State

**Workflow Testing Status:**
- ⏳ Workflow not yet tested (proactive evaluation design)
- ✅ Complete workflow designed and documented
- ✅ Experiment plan defined in problem_definition.md

**MITHRA Workflow Components (MVP):**
1. Context Collector - Gather user background and goals
2. Source Analyzer - Extract structure from papers/articles/transcripts/talks
3. Strategy Generator - Create personalized learning plan using RAG best practices
4. Module Generator - Deliver adaptive learning modules
5. Visualization Scripter - Generate guided visualization using RAG templates
6. Reflection Facilitator - Help user apply learnings to context

**Key Design Claims:**
- Personalized explanations tailored to user's background
- Modular learning structure (3-5 modules)
- Guided visualization for deeper integration
- 50-75 minute session vs. 1-5 hours traditional reading
- Deep comprehension enabling application to user's context

---

## Identified Quality Risks (Pre-Testing)

### Critical Risk #1: Personalization Quality
**Concern:** Will personalization be effective, seamless, engaging, and grounded in pedagogical principles and accelerated learning?

**Why This Matters:**
- Core differentiator vs. ChatGPT/Claude summaries
- If personalization feels generic, users won't see value
- Poor pedagogical grounding = wasted learning time
- Without engagement, users won't complete 50-75 min session

**Potential Failure Modes:**
- Explanations don't actually adapt to user's stated background
- Module sequencing ignores user's existing knowledge
- Teaching approach doesn't leverage accelerated learning principles
- User feels patronized (too simple) or lost (too advanced)
- Pacing doesn't match user's available time/depth preference

**Evidence Needed:**
- User reports explanations matched their background (survey)
- Comprehension depth achieved (post-session assessment)
- User engagement maintained throughout session (behavioral data)
- Pedagogical principles actually applied (qualitative analysis)

---

### Critical Risk #2: Visualization Script Effectiveness
**Concern:** Will visualization scripts truly add to personalized learning, guide users to wonderful insights and "aha moments"?

**Why This Matters:**
- Key hypothesis: visualization improves retention/application
- If scripts are generic, won't provide value beyond modules alone
- Poor quality = wasted 15-20 minutes of user time
- This is the "secret sauce" - needs to work

**Potential Failure Modes:**
- Scripts feel disconnected from learning content
- Metaphors don't resonate or feel forced
- Pacing too fast/slow for visualization experience
- Missing key concepts from the learning session
- Doesn't help user apply concepts to their context
- User feels skeptical or disengaged during visualization

**Evidence Needed:**
- Expert validation (hypnosis/visualization practitioner review)
- User retention after visualization (follow-up assessment)
- User reports insights/connections made (qualitative feedback)
- Script quality against best practices (rubric-based evaluation)

---

## Contextually Relevant Quality Vectors

Based on MITHRA's design and your technical background:

### 1. **Personalization Fidelity**
**Definition:** Degree to which system adapts explanations, examples, and pacing to user's stated context

**Why It Matters:** Core value proposition and differentiator from existing tools

**How to Measure:**
- User background → explanation complexity mapping (qualitative analysis)
- Appropriateness of analogies/examples for user's domain (expert review)
- Module depth vs. user's requested depth (alignment check)
- User perception of personalization (survey: "explanations matched my background")

---

### 2. **Pedagogical Soundness**
**Definition:** Adherence to accelerated learning principles and evidence-based teaching methods

**Why It Matters:** Claims to be grounded in learning science, not just summarization

**How to Measure:**
- Presence of scaffolding (build from known → unknown)
- Module sequencing follows cognitive load principles
- Use of multiple representations (verbal, visual, analogical)
- Active engagement vs. passive information delivery
- RAG retrieval actually incorporates best practices (if implemented)

---

### 3. **Visualization Integration Quality**
**Definition:** How well visualization scripts embed learning and facilitate application

**Why It Matters:** Hypothesis that visualization meaningfully improves retention/application

**How to Measure:**
- Best practice adherence (expert rubric evaluation)
- Content coverage (all major concepts included meaningfully)
- Personalization to user context (references their specific goal/problem)
- Metaphor appropriateness for technical concepts
- User experience quality (pacing, engagement, clarity)
- Retention improvement (before/after comparison or follow-up test)

---

### 4. **Time Efficiency**
**Definition:** Achieving deep comprehension in 50-75 minutes vs. 1-5 hours traditional

**Why It Matters:** Core efficiency claim and user value proposition

**How to Measure:**
- Actual session duration (track time spent)
- Comprehension depth achieved (post-session assessment)
- Comparison to user's typical paper reading time (self-report)
- Trade-offs: speed vs. depth (are we sacrificing quality for speed?)

---

### 5. **Comprehension → Application Transfer**
**Definition:** User's ability to connect learned concepts to their specific context/problem

**Why It Matters:** Success metric = actionable understanding, not just knowledge

**How to Measure:**
- User can articulate how concepts apply to their work (reflection dialogue)
- Quality of application ideas generated (specificity, feasibility)
- Follow-up: Did user actually apply learnings? (longitudinal)
- Socratic dialogue effectiveness (prompts meaningful connections)

---

## Evaluation Strategy Alignment with Experiments

Your 2-part experiment plan already targets these risks:

**Experiment 1: Modular Learning Effectiveness**
- Tests: Personalization fidelity, pedagogical soundness, time efficiency, comprehension depth
- Method: Within-subjects comparison (MVP vs. traditional reading)
- Sample: 3-5 ML practitioners
- Metrics: Time, comprehension score, personalization rating, user preference

**Experiment 2: Visualization Script Quality**
- Tests: Visualization integration quality, best practice adherence, content coverage
- Method: Expert review of generated scripts
- Sample: 3-5 scripts reviewed by hypnosis/visualization expert
- Metrics: Best practice rating, content coverage, personalization quality

**Gap:** Need to add measurement for **application transfer** (follow-up assessment)

---

## Next Steps

Moving from risk identification to systematic test case design:
1. Generate specific quality risk hypotheses for each area
2. Prioritize risks by impact and likelihood
3. Design test cases targeting each priority risk
4. Create measurement artifacts (evaluation matrix, rubrics)

---

## Notes

**Strengths of Current Approach:**
- Proactive evaluation design (before sunk cost of testing)
- Clear hypothesis about what makes MITHRA valuable
- Recognition that personalization and visualization are highest-risk areas
- Experiment plan already addresses core risks

**Considerations:**
- RAG best practices not yet implemented (prompts need content)
- Until RAG is populated, can't fully test "pedagogical grounding" claim
- May need to iterate on prompt design based on initial testing
- Expert review for visualization requires external coordination

---

## Quality Risk Hypotheses

### Identified Quality Risks:

**Risk 1.2 - Module Sequencing Ignores Prior Knowledge**
**Hypothesis:** Learning modules might follow generic "paper structure" rather than adapting to what user already knows, forcing them through familiar concepts before reaching novel material

- **Why it matters:** Wastes time, loses engagement, defeats "time efficiency" claim (50-75 min target)
- **Potential symptoms:** User skipping ahead, saying "I already know this," session taking >75 minutes, user disengagement
- **Domain relevance:** Experienced ML practitioners don't need introduction to basic concepts in their domain
- **Impact:** HIGH - Directly undermines personalization and efficiency value props
- **Category:** Personalization Fidelity

---

**Risk 1.3 - Pedagogical Principles Not Applied**
**Hypothesis:** Without populated RAG corpus, strategy generation might claim to use "best practices" but actually apply generic teaching patterns that don't align with accelerated learning principles

- **Why it matters:** Claiming pedagogical grounding without evidence undermines credibility; poor pedagogy = poor learning outcomes
- **Potential symptoms:** No scaffolding (jumping straight to complex concepts), passive information dump, lack of multi-modal explanations, no building from known→unknown
- **Domain relevance:** Adult learners with technical backgrounds need evidence-based pedagogy, not generic lecturing
- **Impact:** HIGH - Core differentiator; if pedagogy is weak, MITHRA is just organized summarization
- **Category:** Personalization Fidelity & Pedagogical Soundness

---

**Risk 2.2 - Missing Concept Integration**
**Hypothesis:** Visualization scripts might miss key concepts from the learning session or include them superficially without meaningful integration

- **Why it matters:** Defeats purpose of "embedding learning deeper"; if concepts missing, visualization doesn't reinforce learning
- **Potential symptoms:** Expert review identifies major concepts absent, weak connections between concepts, user doesn't recall concepts after visualization
- **Domain relevance:** Research papers have dense, interconnected concepts - missing one breaks understanding
- **Impact:** HIGH - Makes visualization ineffective; wastes 15-20 minutes; fails Experiment 2 validation
- **Category:** Visualization Integration Quality

---

**Risk 2.3 - Poor Metaphor Quality for Technical Concepts**
**Hypothesis:** Metaphors/imagery used in visualization might be inappropriate for abstract technical concepts, feeling awkward or confusing rather than clarifying

- **Why it matters:** Bad metaphors actively hurt understanding instead of helping; creates cognitive dissonance
- **Potential symptoms:** User finds visualization confusing, metaphors don't map to technical reality, expert flags inappropriate analogies
- **Domain relevance:** Some ML/AI concepts resist simple analogies (e.g., high-dimensional spaces, backpropagation, attention mechanisms)
- **Impact:** MEDIUM-HIGH - Poor metaphors undermine visualization value; could make it worse than no visualization
- **Category:** Visualization Integration Quality

---

### Risk Categories Covered:
- [X] Input variability and edge cases (implicit in source analysis)
- [X] Output quality and consistency (module sequencing, pedagogy, visualization)
- [X] Context sensitivity and appropriateness (personalization, metaphor quality)
- [ ] Scope and boundary handling (not prioritized for MVP)
- [ ] Performance under different conditions (not prioritized for MVP)

### Priority Focus Areas:
1. **Personalization effectiveness** - Risks 1.2, 1.3
2. **Visualization quality** - Risks 2.2, 2.3

### Participant Insights:
- These four risks directly align with the two-part experiment plan
- Risks 1.2 and 1.3 will be tested in Experiment 1 (modular learning effectiveness)
- Risks 2.2 and 2.3 will be tested in Experiment 2 (visualization script expert review)
- All four risks are testable before full implementation

---

## Risk Prioritization

### Priority Evaluation Criteria:
Based on Sprint 1 context and MVP validation goals:
- **Impact on workflow usefulness** and core value proposition
- **Differentiation** - builds unique value that can't be easily replicated
- **Actionability** given current resources and timeline
- **Testability** with available evaluation methods (including LLM-as-Judge)

### Top Priority Quality Risks:

#### 1. Module Sequencing Ignores Prior Knowledge - **CRITICAL**
- **Risk Statement:** Learning modules follow generic paper structure rather than adapting to user's existing knowledge, forcing them through familiar concepts before reaching novel material
- **Why Critical:**
  - Directly undermines core personalization claim
  - Wastes user time (defeats 50-75 min efficiency goal)
  - Causes user disengagement and abandonment
  - If this fails, MITHRA = expensive paper summarizer
- **Testing Focus:**
  - Analyze module content vs. user's stated background
  - Measure time spent on concepts user already knows
  - Track user requests to "skip ahead" or expressions of boredom
  - Check if modules adapt depth/focus based on user expertise
- **Success Criteria (MVP Acceptable):**
  - 80%+ of users report modules matched their knowledge level (survey: 4/5 or higher)
  - <15% of module time spent on concepts user explicitly stated they know
  - Users can complete appropriate-depth session within 75 minutes
  - LLM-as-Judge rates personalization fidelity as "good" (4/5) or higher
- **Evaluation Method:** LLM-as-Judge + user survey + time tracking

---

#### 2. Pedagogical Principles Not Applied - **CRITICAL**
- **Risk Statement:** Strategy generation claims to use "accelerated learning best practices" but actually applies generic teaching patterns without scaffolding, multi-modal explanations, or proper cognitive load management
- **Why Critical:**
  - Core differentiator from ChatGPT/Claude summarization
  - If pedagogy is weak, MITHRA is just organized information dump
  - Undermines credibility of "grounded in learning science" claim
  - Poor pedagogy = poor learning outcomes and retention
- **Testing Focus:**
  - Check for scaffolding (building from known → unknown)
  - Verify multi-modal explanations (verbal + visual/spatial + analogical)
  - Assess cognitive load management (chunk size, sequencing)
  - Identify use of pedagogical techniques (spaced review, active recall prompts, elaboration)
- **Success Criteria (MVP Acceptable):**
  - LLM-as-Judge identifies 3+ accelerated learning principles applied per module
  - Scaffolding present: concepts build on each other logically (4/5 rating)
  - Multi-modal explanations used (not just text dump): 3/5 or higher
  - Users achieve comprehension depth targets (can explain and apply concepts)
- **Evaluation Method:** LLM-as-Judge with pedagogical rubric + comprehension assessment

---

#### 3. Missing Concept Integration (Visualization) - **HIGH PRIORITY**
- **Risk Statement:** Visualization scripts miss key concepts from learning session or include them superficially without meaningful integration
- **Why High Priority:**
  - Builds unique value that can't be easily replicated
  - If concepts missing, visualization wastes 15-20 minutes
  - Defeats purpose of "deeper learning integration"
  - Makes visualization ineffective for retention/application
- **Testing Focus:**
  - Compare concepts in learning modules vs. visualization script
  - Assess depth of concept integration (superficial mention vs. meaningful exploration)
  - Check if connections between concepts are maintained in visualization
  - Verify user's specific context/goal is incorporated
- **Success Criteria (MVP Acceptable):**
  - 85%+ of major concepts (top 3-5 from paper) included in visualization
  - LLM-as-Judge rates integration depth as "meaningful" (3/5 or higher)
  - Connections between concepts maintained (not isolated fragments)
  - User's specific goal/context referenced in script (100%)
- **Evaluation Method:** LLM-as-Judge with concept coverage rubric + expert review (if available)

---

#### 4. Poor Metaphor Quality for Technical Concepts - **HIGH PRIORITY**
- **Risk Statement:** Metaphors/imagery used in visualization are inappropriate for abstract technical concepts, feeling awkward or confusing rather than clarifying
- **Why High Priority:**
  - Builds unique value that can't be easily replicated
  - Bad metaphors actively hurt understanding (cognitive dissonance)
  - Could make visualization worse than no visualization
  - Harder to fix than content coverage (requires creativity/insight)
- **Testing Focus:**
  - Assess metaphor appropriateness for technical domain
  - Check if metaphor maps accurately to concept (no misleading analogies)
  - Verify metaphors feel natural, not forced
  - Test user understanding after metaphor (does it clarify or confuse?)
- **Success Criteria (MVP Acceptable):**
  - No "actively harmful" metaphors (0 rated 1/5 by LLM judge)
  - 70%+ of metaphors rated "appropriate" or better (3/5+)
  - LLM-as-Judge: metaphors accurately map to technical concepts (4/5)
  - User feedback: metaphors helped understanding (not neutral/negative)
- **Evaluation Method:** LLM-as-Judge with metaphor quality rubric + user survey

---

### Evaluation Method Innovation: LLM-as-Judge

**Why LLM-as-Judge for MVP:**
- Cost-effective: No need for expensive expert reviewers at MVP stage
- Scalable: Can evaluate many test cases quickly
- Consistent: Same rubric applied across all evaluations
- Fast iteration: Get feedback immediately to improve prompts

**LLM Judge Approach:**
1. **Design evaluation rubrics** for each risk (specific criteria + rating scale)
2. **Create judge prompts** that apply rubrics to workflow outputs
3. **Run workflow** → capture outputs (modules, scripts)
4. **Judge evaluates** outputs against rubric
5. **Aggregate scores** across test cases to assess risk

**When to add human expert:**
- After MVP validation, before broader release
- For visualization quality (hypnosis practitioner review)
- To validate LLM judge accuracy (spot-check sample)

---

### Priority Rationale Summary:

**Critical Risks (1.2, 1.3):**
- Must work for MITHRA to have any value
- Core differentiators from existing tools
- If these fail, pivot or redesign required

**High Priority Risks (2.2, 2.3):**
- Build defensible unique value
- Harder to replicate than basic personalization
- Can iterate on these after validating critical risks
- If these are weak, can still launch with modular learning only

### Deferred Risks (Not Prioritized for MVP):
- Source analysis accuracy (Risks 3.1, 3.2) - Can manually verify for MVP testing
- Time efficiency claims (Risks 4.1, 4.2) - Will naturally emerge from Experiment 1 data
- Background mismatch (Risk 1.1) - Covered by module sequencing tests
- Generic visualization (Risk 2.1) - Covered by concept integration + metaphor quality
- Visualization pacing (Risk 2.4) - Can address in iteration after content quality validated

### Next Steps:
Design specific test cases targeting these 4 priority risks, with LLM-as-Judge evaluation framework

---

## Test Case Design

### Test Case Generation Approach:
**Hybrid: Real-World Sampling + Failure Mode Reverse Engineering**

**Rationale:**
- Use real research papers for realistic testing
- Design user profiles to stress different personalization scenarios
- Target specific failure modes for each risk
- Efficient use of limited test cases (10-12 total)

### Test Execution Strategy:
1. Select 3 diverse research papers (complexity, domain, concept types)
2. Create 3 user profiles (varying backgrounds and goals)
3. Run MITHRA workflow 3 times (strategic paper × user combinations)
4. Capture outputs: context, strategy, modules, visualization scripts
5. Apply LLM-as-Judge evaluation with risk-specific rubrics
6. Aggregate scores against success criteria

---

## Test Cases by Risk Area

### Test Group 1: Module Sequencing (Risk 1.2)

**Purpose:** Detect if modules adapt to user's prior knowledge or follow generic paper structure

#### Test Case 1.2.1: Expert User + Foundational Paper
**User Profile:**
- Role: Senior ML Engineer
- Background: 10 years experience, expert in NLP and transformers
- Goal: Explore architectural variations for product feature
- Time/Depth: 60 min, moderate depth

**Paper:** "Attention Is All You Need" (Vaswani et al., 2017)
- Well-known foundational paper on Transformers
- User likely already understands attention mechanisms

**Expected Behavior:**
- Strategy should skip/minimize basic attention intro
- Focus on novel architectural choices (multi-head, positional encoding)
- Emphasize what's different from prior architectures

**Failure Indicators:**
- Modules start with "What is attention?" when user stated expertise
- Time spent on concepts user already knows
- User would need to skip ahead

**LLM-Judge Evaluation Points:**
- Does strategy acknowledge user's transformer expertise?
- Are basic concepts skipped or treated as review?
- Does content focus on novel contributions vs. background?
- Personalization fidelity rating (1-5)

---

#### Test Case 1.2.2: Domain Expert + ML Paper
**User Profile:**
- Role: Research Scientist (Biology)
- Background: PhD in molecular biology, basic Python, limited ML
- Goal: Understand technique to solve specific protein problem
- Time/Depth: 75 min, deep dive

**Paper:** "AlphaFold: Highly accurate protein structure prediction with deep learning" (Jumper et al., 2021)
- Combines biology domain + complex ML
- User knows biology deeply, needs ML concepts explained

**Expected Behavior:**
- Strategy should bridge from biology knowledge to ML concepts
- Use protein/biology analogies to teach ML ideas
- Spend time on ML fundamentals (networks, training) that biology expert lacks

**Failure Indicators:**
- Assumes ML background user doesn't have
- Fails to leverage user's biology expertise
- Generic ML explanations without domain connection

**LLM-Judge Evaluation Points:**
- Does strategy build from biology knowledge to ML?
- Are ML concepts explained appropriately for novice?
- Are biology-specific analogies used?
- Module sequencing appropriateness rating (1-5)

---

#### Test Case 1.2.3: Balanced Background + Cross-Domain Paper
**User Profile:**
- Role: ML Practitioner
- Background: Solid NLP experience, limited computer vision
- Goal: Continuous learning - staying current
- Time/Depth: 50 min, high-level overview

**Paper:** "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale" (ViT) (Dosovitskiy et al., 2021)
- Applies transformers (user knows) to vision (user doesn't know well)
- Perfect for testing knowledge transfer

**Expected Behavior:**
- Strategy should leverage user's NLP transformer knowledge
- Build from "transformers you know" to "vision-specific adaptations"
- Skip transformer basics, focus on vision patch processing

**Failure Indicators:**
- Re-explains transformers from scratch
- Doesn't build bridge from NLP to vision
- Treats as entirely new concept

**LLM-Judge Evaluation Points:**
- Does strategy explicitly connect to user's NLP knowledge?
- Is transformer knowledge assumed/leveraged?
- Are vision-specific concepts the focus?
- Knowledge transfer effectiveness rating (1-5)

---

### Test Group 2: Pedagogical Principles (Risk 1.3)

**Purpose:** Detect if teaching approach applies accelerated learning principles or uses generic patterns

**Note:** Uses same 3 test cases (1.2.1, 1.2.2, 1.2.3) but evaluates pedagogy instead of sequencing

#### LLM-as-Judge Pedagogical Rubric (Applied to All 3 Cases):

**Criterion 1: Scaffolding (Building from Known → Unknown)**
- **5:** Clear progression, each concept builds on previous, prerequisites identified
- **4:** Good sequencing, mostly builds on prior knowledge
- **3:** Adequate sequencing, some logical progression
- **2:** Weak scaffolding, jumps to complex concepts too quickly
- **1:** No scaffolding, concepts presented in arbitrary order

**Criterion 2: Multi-Modal Explanations**
- **5:** Concepts explained through 3+ modalities (verbal, visual/spatial, analogical, code examples)
- **4:** 2-3 modalities consistently used
- **3:** 2 modalities present
- **2:** Mostly single modality (text only)
- **1:** Purely text-based information dump

**Criterion 3: Cognitive Load Management**
- **5:** Perfect chunk sizing, appropriate complexity progression, clear segmentation
- **4:** Good chunking, manageable complexity
- **3:** Adequate chunking, some overwhelming sections
- **2:** Poor chunking, information overload
- **1:** No chunking, massive cognitive load

**Criterion 4: Active Engagement (Count Instances)**
- Comprehension check questions: __
- Reflection prompts: __
- "Pause and consider..." moments: __
- Connections to user's context: __
- Total engagement points: __
- **Target:** ≥5 active engagement points per module

**Criterion 5: Accelerated Learning Techniques Present (Checklist)**
- [ ] Spaced repetition (concepts revisited)
- [ ] Elaboration (connecting to existing knowledge)
- [ ] Concrete examples before abstract principles
- [ ] Active recall prompts (not just passive reading)
- [ ] Interleaving (mixing related concepts)
- **Target:** ≥3 techniques identified per session

**Overall Pedagogical Soundness:** (1-5) __

---

### Test Group 3: Concept Integration in Visualization (Risk 2.2)

**Purpose:** Detect if visualization scripts include all major concepts with meaningful integration

#### Test Case 2.2.1: Algorithm-Focused Paper
**Paper:** "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding" (Devlin et al., 2019)

**Major Concepts Identified:**
1. Masked Language Modeling (MLM)
2. Bidirectional context encoding
3. Pre-training + Fine-tuning paradigm
4. WordPiece tokenization
5. Next Sentence Prediction (NSP)

**User Context:** ML engineer building text classification system

**LLM-Judge Evaluation:**
- **Concept Coverage:** Which of 5 concepts appear in visualization? (__ / 5)
- **Integration Depth:** Are concepts mentioned superficially or explored meaningfully? (1-5 each)
- **Concept Connections:** Are relationships between concepts maintained? (e.g., MLM enables bidirectional understanding)
- **User Context Integration:** Does script reference user's text classification goal? (Yes/No)
- **Overall Integration Quality:** (1-5)

**Success Threshold:** 4+ concepts with depth ≥3, connections maintained, user context referenced

---

#### Test Case 2.2.2: Theoretical/Abstract Paper
**Paper:** "Understanding Deep Learning Requires Rethinking Generalization" (Zhang et al., 2017)

**Major Concepts Identified:**
1. Generalization gap phenomenon
2. Memorization vs. learning distinction
3. Implicit regularization in neural networks
4. Model capacity vs. generalization trade-off
5. Rethinking traditional learning theory

**User Context:** Research scientist investigating model behavior

**LLM-Judge Evaluation:**
- **Concept Coverage:** Which of 5 abstract concepts appear? (__ / 5)
- **Abstraction Handling:** Are abstract ideas made concrete through visualization? (1-5 each)
- **Concept Connections:** Are theoretical relationships preserved?
- **User Context Integration:** Does script connect to user's research questions?
- **Challenge Assessment:** Abstract concepts harder to visualize - did it succeed? (1-5)

**Success Threshold:** 4+ concepts with depth ≥3 (harder than algorithms), connections preserved

---

#### Test Case 2.2.3: Applied/Architectural Paper
**Paper:** "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (Lewis et al., 2020)

**Major Concepts Identified:**
1. RAG architecture (retrieval + generation)
2. Dense retrieval component (DPR)
3. Generator component (seq2seq)
4. Knowledge grounding through retrieval
5. Parametric vs. non-parametric memory

**User Context:** Engineer building question-answering system

**LLM-Judge Evaluation:**
- **Concept Coverage:** Which of 5 concepts appear? (__ / 5)
- **Architectural Understanding:** Does script convey system architecture? (1-5)
- **Component Relationships:** Are retrieval-generation connections clear?
- **User Context Integration:** Does script reference QA system building?
- **Application Clarity:** Does user understand how to apply RAG? (1-5)

**Success Threshold:** All 5 concepts present (applied papers easier to visualize), strong connections

---

### Test Group 4: Metaphor Quality (Risk 2.3)

**Purpose:** Detect if metaphors are appropriate, accurate, and helpful for technical concepts

**Note:** Uses same 3 papers (2.2.1, 2.2.2, 2.2.3) but evaluates metaphor quality

#### LLM-as-Judge Metaphor Quality Rubric:

**For Each Metaphor/Analogy in Visualization Script:**

**Technical Accuracy (Does metaphor accurately represent the concept?)**
- **5:** Perfect mapping, all key aspects represented
- **4:** Good mapping, minor aspects missing
- **3:** Adequate mapping, captures main idea
- **2:** Weak mapping, misleading in some ways
- **1:** Inaccurate, creates misconceptions

**Appropriateness (Is metaphor natural for this domain/user?)**
- **5:** Highly appropriate, resonates with user's background
- **4:** Good fit for domain and user
- **3:** Adequate, not perfect but workable
- **2:** Awkward, forced metaphor
- **1:** Inappropriate or confusing for context

**Clarity (Does metaphor clarify or confuse?)**
- **5:** Significantly clarifies complex concept
- **4:** Helpful, makes concept more accessible
- **3:** Neutral, doesn't help or hurt
- **2:** Somewhat confusing, needs explanation
- **1:** Actively confusing, worse than no metaphor

**Harmful Analogies Check:**
- Does metaphor create any misleading associations? (Yes/No + explanation)
- Could metaphor lead to misunderstanding of concept? (Yes/No + explanation)
- Is metaphor culturally appropriate and accessible? (Yes/No)

**Overall Metaphor Quality:** (1-5 average across all metaphors)

**Expected Challenging Concepts:**
- BERT Masked Language Modeling → appropriate metaphor?
- High-dimensional embeddings → spatial analogy works?
- Attention mechanisms → what imagery clarifies?
- Generalization vs. memorization → how to visualize abstract distinction?

**Success Threshold:**
- Zero "actively harmful" metaphors (none rated 1/5)
- 70%+ of metaphors rated ≥3/5
- Average technical accuracy ≥4/5

---

## Test Case Summary Matrix

| Test Case | Risk(s) Tested | Paper | User Profile | Key Challenge |
|-----------|----------------|-------|--------------|---------------|
| 1.2.1 | Module Sequencing | Transformers | Expert NLP | Skip known concepts |
| 1.2.2 | Module Sequencing | AlphaFold | Biology → ML | Bridge domains |
| 1.2.3 | Module Sequencing | ViT | NLP → Vision | Transfer knowledge |
| 1.3.x | Pedagogy | (Same 3) | (Same 3) | Apply learning principles |
| 2.2.1 | Concept Integration | BERT | ML Engineer | Algorithm concepts |
| 2.2.2 | Concept Integration | Generalization | Researcher | Abstract concepts |
| 2.2.3 | Concept Integration | RAG | QA Engineer | Architecture |
| 2.3.x | Metaphor Quality | (Same 3) | (Same 3) | Appropriate analogies |

**Total Test Cases:** 12 evaluation points (3 papers × 4 risks)
**Unique Workflow Runs:** 3 (efficient reuse of outputs for multiple risk evaluations)

---

---

## Learning Objectives by Test Group

### Test Group 1: Module Sequencing (Risk 1.2)

**What We're Learning:**
Understanding how well MITHRA adapts module content and sequencing to user's prior knowledge

**Behavioral Questions:**
- Does strategy generation actually parse and use user's stated background?
- Do modules skip/minimize concepts user explicitly stated they know?
- Does sequencing build from user's existing knowledge to new material?
- Is there a pattern in how well personalization works across different user types?

**Quality Boundaries:**
- How much time spent on already-known concepts is acceptable? (<15% target)
- What user satisfaction threshold indicates "good enough" personalization? (4/5 or higher)
- At what point does poor sequencing cause user abandonment?

**Failure Modes:**
- Generic paper-structure sequencing (intro → method → results) regardless of user
- Treating all users as novices despite stated expertise
- Over-personalizing (skipping too much, leaving gaps)
- Inability to bridge between domains (e.g., biology expert learning ML)

**Improvement Insights:**
If personalization fails, we'll learn:
- Does `step3_strategy_generation_prompt.txt` need stronger emphasis on user context?
- Is RAG retrieval (when implemented) critical, or can prompt engineering suffice?
- Do we need explicit user knowledge modeling vs. implicit inference?
- Which user profile types are hardest to personalize for?

**Actionable Outcomes:**
- Identify specific prompt refinements in strategy generation
- Determine if user context collection needs more depth
- Validate whether personalization works without RAG (or if RAG is essential)
- Understand trade-offs between personalization accuracy and development effort

---

### Test Group 2: Pedagogical Principles (Risk 1.3)

**What We're Learning:**
Assessing whether teaching approach applies accelerated learning principles or defaults to generic summarization

**Behavioral Questions:**
- Do modules demonstrate scaffolding (building from known → unknown)?
- Are multiple modalities (verbal, visual/spatial, analogical) consistently used?
- Is cognitive load managed through appropriate chunking?
- How many active engagement points naturally emerge from current prompts?
- Which accelerated learning techniques appear without explicit prompting?

**Quality Boundaries:**
- Minimum threshold: 3+ learning principles applied per session
- Target: 4/5 pedagogical soundness rating from LLM-Judge
- Acceptable: 5+ active engagement points per module
- Critical: No pure information dumps (must have some interactivity)

**Failure Modes:**
- Text-only passive information delivery (no multi-modal)
- Jumping to complex concepts without scaffolding
- No active recall or reflection prompts
- Generic teaching patterns not grounded in learning science
- Overwhelming cognitive load (too much info too fast)

**Improvement Insights:**
If pedagogy is weak, we'll learn:
- Is inline best practice guidance in prompts sufficient, or is RAG essential?
- Which pedagogical principles are hardest to implement via prompting?
- Do current prompts in `step4_module_delivery_prompt.txt` need explicit pedagogical structure?
- Can LLM naturally apply learning principles, or do they need detailed scaffolding?

**Actionable Outcomes:**
- Prioritize which pedagogical best practices to embed in prompts first
- Determine necessity of RAG vs. inline guidance
- Identify prompt patterns that elicit good pedagogy
- Assess whether current MVP can differentiate from ChatGPT, or if more work needed

---

### Test Group 3: Concept Integration (Risk 2.2)

**What We're Learning:**
Evaluating whether visualization scripts include all major concepts with meaningful depth

**Behavioral Questions:**
- What percentage of major concepts (identified in modules) appear in visualization?
- Are concepts integrated meaningfully or just mentioned superficially?
- Do connections between concepts transfer from modules to visualization?
- Does user's specific context/goal get incorporated into script?
- Is there a pattern in which concept types (concrete vs. abstract) transfer better?

**Quality Boundaries:**
- Minimum threshold: 85% of major concepts (4 out of 5) included
- Target: All concepts with depth rating ≥3/5
- Critical: Connections between concepts must be preserved
- Required: User context explicitly referenced (100%)

**Failure Modes:**
- Concepts from modules missing entirely in visualization
- Superficial mention without exploration
- Isolated concept fragments (no connections)
- Generic script that could apply to any paper
- Abstract concepts dropped because "hard to visualize"

**Improvement Insights:**
If concept coverage fails, we'll learn:
- Does `step5_visualization_script_generation_prompt.txt` need explicit concept checklist?
- Is there a handoff issue between Step 4 (modules) and Step 5 (visualization)?
- Do we need to explicitly pass concept list to visualization generation?
- Which types of concepts (algorithm, theory, architecture) are hardest to integrate?

**Actionable Outcomes:**
- Refine visualization generation to ensure concept transfer
- Add explicit concept tracking mechanism if needed
- Identify whether RAG templates help with concept integration
- Determine if human review/editing needed for complex papers

---

### Test Group 4: Metaphor Quality (Risk 2.3)

**What We're Learning:**
Assessing whether metaphors/analogies are appropriate, accurate, and helpful for technical concepts

**Behavioral Questions:**
- What types of metaphors does the system generate (spatial, process-based, everyday objects)?
- Are metaphors appropriate for user's domain and background?
- Do metaphors accurately map to technical concepts without misleading?
- Are there patterns in which concepts get good vs. poor metaphors?
- Does metaphor quality vary by paper complexity or concept abstractness?

**Quality Boundaries:**
- Critical: Zero actively harmful metaphors (rating 1/5)
- Minimum: 70% of metaphors rated ≥3/5 (adequate or better)
- Target: Average technical accuracy ≥4/5
- Aspirational: Metaphors that genuinely create "aha moments"

**Failure Modes:**
- Inappropriate metaphors for technical domain (overly simplistic)
- Inaccurate mappings that create misconceptions
- Forced/awkward analogies that feel unnatural
- Generic metaphors not tailored to user's background
- Missing metaphors for most complex concepts (avoidance)

**Improvement Insights:**
If metaphor quality is poor, we'll learn:
- Does visualization script generation need examples of good metaphors in prompts?
- Is RAG with metaphor templates essential for quality?
- Can LLM generate appropriate metaphors without explicit guidance?
- Do we need user's background more explicitly referenced in visualization prompts?
- Are some concepts fundamentally unmappable to metaphor (accept limitation)?

**Actionable Outcomes:**
- Identify patterns in good vs. bad metaphor generation
- Build library of effective metaphor patterns for common ML concepts
- Determine if human review/curation needed for metaphors
- Assess trade-off: generic accurate vs. creative potentially-flawed
- Validate whether visualization adds value or should be simplified

---

## Cross-Test Group Learning

**Integration Questions Across All Risks:**
- Is there correlation between personalization quality (1.2) and pedagogical soundness (1.3)?
- Does good module design (1.2, 1.3) predict good visualization integration (2.2, 2.3)?
- Are certain user profile types consistently harder across all risks?
- Do specific paper types (algorithm vs. theory) show patterns across risks?

**Resource Allocation Insights:**
- Which risks can be addressed through prompt refinement alone?
- Which risks require RAG implementation to resolve?
- Which risks might need architectural changes (not just prompt tweaks)?
- What's the minimum viable quality bar for MVP launch?

**Prioritization Insights:**
- If we can only fix 1-2 risks before launch, which should it be?
- Can we launch with strong personalization but weaker visualization? Or vice versa?
- What known limitations should be documented vs. must be fixed?

---

## Next Steps:
Create measurement artifacts: LLM-Judge prompt templates and evaluation CSV matrix
