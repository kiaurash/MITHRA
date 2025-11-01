# Workflow Problem Definition: MITHRA
## Machine Intelligence for Translating Human Research into Action

## Problem Statement
Research papers are written for academic audiences with deep expertise, creating a significant barrier for practitioners who need to quickly understand novel techniques, assess their applicability, and design experiments to validate them in real-world contexts. This gap forces practitioners to spend 1-5 hours per paper struggling with dense academic content, often failing to extract actionable insights or build sufficient confidence to implement new approaches.

## Current State

### Who
**Primary users:** ML practitioners and applied researchers in industry (ML engineers, data scientists, research scientists) who are trying to:
- Find better solutions to existing problems or challenges
- Use literature research to identify new potential capabilities to build products around

**User characteristics:**
- Have technical skills but may lack specific academic background in certain domains
- Need to bridge the gap between academic research and practical implementation
- Face time pressure to stay current while delivering on project commitments

### Frequency
**Continuous and project-driven combination:**
- Specific project need: "We need to improve our recommendation system"
- Continuous learning: "I need to stay current in my field"
- Problem-solving: "Our current approach isn't working, what's new?"

### Trigger
User has identified a research paper (or set of inter-related papers) that seems relevant to their work and needs to understand it deeply enough to take action.

### How it works now

**Focus area: Stages 3-4 of the research-to-practice pipeline**

**Stage 3 - Read & Annotate:**
- Read PDFs with varying strategies (some read abstract→methodology→findings; others take different approaches)
- Highlight passages and extract claims, assumptions, datasets, and metrics
- Struggle with dense math/jargon written for academic experts
- Difficulty connecting dots due to implicit assumptions and missing context
- Figure and table details are hard to capture and interpret

**Stage 4 - Extract Implementation Details:**
- Hunt for code repositories on GitHub
- Attempt to reconcile discrepancies between paper descriptions and actual code
- Try to capture hyperparameters, implementation tricks, and data preparation steps
- Deal with out-of-date repos, missing checkpoints, and differences from paper
- Face reproducibility challenges

**Time investment:** 1-5 hours per paper

### Friction Points

**Primary friction - Academic writing barrier:**
- Papers written for academic audiences (people with deep expertise)
- Dense jargon and mathematical notation without sufficient context
- Implicit assumptions not explicitly stated
- Difficult for practitioners to connect new concepts to their existing knowledge
- Hard to distinguish how a new technique differs from related approaches
- Challenging to assess whether technique is worthwhile for their specific problem space
- Unclear how to design experiments to test efficacy in their environment

**Secondary frictions:**
- Missing hyperparameters and implementation details in papers
- Code repositories don't match paper descriptions
- Figure and table details hard to extract and understand
- Different users have different backgrounds, learning preferences, and time constraints
- One-size-fits-all summarization tools (like ChatGPT) don't account for individual context

## Desired State

### What success looks like

**Contextual Understanding achieved when:**
A practitioner (based on their own background and learning preferences) can quickly:
1. **Learn core concepts** - Understand the fundamental ideas and techniques
2. **Build conceptual connections** - See inter-relationships between new and already-known concepts/techniques
3. **Distinguish approaches** - Understand how this technique differs from other related techniques
4. **Assess applicability** - Determine whether it's worthwhile for their problem space/product idea
5. **Design experiments** - Create a plan to test the efficacy of the research paper's approach/technique in their context

### How learning is personalized

**The system understands:**
- User's professional role (ML engineer, research scientist, etc.)
- Educational background and technical depth in key AI domains
- Preferred learning style (visual diagrams, code examples, analogies, step-by-step)
- Level of desired learning depth (quick high-level overview vs. in-depth hands-on tutorial)
- User's learning purpose (solving a specific problem, expanding technical depths, designing new capability/product)
- Available time for the session

**The system provides:**
- Personalized explanations tailored to user's background
- Pedagogically-sound accelerated learning training (not just passive explanations)
- Active learning experiences that deepen understanding
- Adaptive depth based on user's time and goals
- Guidance and recommendations (while human makes final decisions)

### Key Metrics

**Primary metric (most important):**
- **Action:** User successfully designs an experiment to test the approach in their context

**Secondary metrics:**
- **Time saved:** Reduce paper understanding time from 1-5 hours to significantly less
- **Comprehension:** User can explain the technique and connect new concepts to related concepts

## Constraints

### Tools Available
- Full access to research papers (PDFs, arXiv links)
- Access to code repositories (GitHub)
- AI/LLM capabilities for personalized learning generation

### Human Control Requirements
- **AI should:** Guide, provide recommendations, teach concepts, suggest experiments
- **Human must:** Make final decisions on applicability and implementation
- **Philosophy:** AI as intelligent tutor and advisor, not autonomous decision-maker

### Quality Requirements
- Learning content must be pedagogically sound (not just simplified summaries)
- Explanations must be accurate and faithful to the original research
- Personalization must genuinely adapt to user's background and needs
- Recommendations must help user take action (design experiments)
- System must handle varying time constraints flexibly

### Scope for Initial Product
- **In scope:** User comes with specific paper(s) already identified
- **Out of scope (future):** Paper discovery and recommendation (Stages 1-2)
- **Focus:** Stages 3-4 (Read/Annotate + Extract Implementation Details)
- **Goal:** Enable contextual understanding and actionable experiment design

## Market Context

**Problem scale:**
- 66% of researchers report feeling swamped by volume of new publications
- ~20% spend over 5 hours per week just to stay current
- Only 22% fully trust existing AI summarization tools for scientific content
- 84% use these tools anyway due to lack of better alternatives

**Gap identified:**
Current tools provide one-size-fits-all summarization without:
- Contextual reasoning linking research to real-world use cases
- Personalized learning pathways based on user role and knowledge
- Support for translating theory into practice (the knowing-doing gap)

**Opportunity:**
Build a research-to-practice solution that bridges the gap between academic publications and practical implementation through personalized, pedagogically-sound accelerated learning.

---

## Assumptions Analysis

### Initial Assumptions Identified:
1. Users must come with specific papers already identified (discovery/recommendation out of scope)
2. Personalization requires collecting detailed upfront information (role, background, learning style, etc.)
3. System must handle both Stage 3 (Read/Annotate) and Stage 4 (Extract Implementation Details) together
4. Users need access to code repositories on GitHub as part of understanding process
5. AI should only guide and recommend, with humans making all final decisions
6. Primary success metric must be "user designs an experiment"
7. Explanations must be pedagogically sound (active learning, not passive summaries)
8. Current tools fail primarily due to lack of personalization

### Validated Constraints (Must Remain True):
- **Human maintains control of final decisions** on applicability and implementation approach
- **Explanations must be faithful to original research** - accuracy is non-negotiable
- **Pedagogical soundness required** - best practices guide already developed and ready to use
- **User's learning goal/intention must be understood** - critical for effective personalization

### Flexible Assumptions (Adjusted for MVP):
- **Paper discovery/recommendation: OUT OF SCOPE** for MVP (future capability)
- **Personalization approach: EXPLICIT UPFRONT** for MVP (adaptive inference is future enhancement)
- **Focus on Stage 3 only** - Conceptual understanding of paper (Stage 4 implementation details optional/future)
- **Code repository analysis: OUT OF SCOPE** for MVP (focus on paper content only)
- **Success metrics expanded:**
  - Primary: User designs experiment to test approach
  - Also valid: Deep understanding for continuous learning or capability exploration

### MVP Scope Definition:
**Must-Have Components:**
1. Personalized paper explanation (Stage 3 - conceptual understanding)
2. Multi-turn adaptive Q&A to deepen understanding
3. Guided visualization for learning integration (includes hypnosis/visualization scripts)
4. Socratic questioning to help user apply learnings to their specific context/problem
5. Experiment design assistance (for users with implementation intent)

**Technical Approach:**
- Mock RAG system storing best practices guides, pedagogical principles, and visualization scripts
- Use existing RAG corpus infrastructure (`rag_corpus/best_practices/`, `rag_corpus/hypnosis_scripts/`)
- Multi-turn conversational interface with adaptive depth

**Key Differentiators (vs. ChatGPT/Claude direct prompting):**
1. **Multi-turn adaptive pedagogy** grounded in learning science principles (not just prompt engineering)
2. **Guided visualization for integration** - unique capability to help users internalize and apply learnings
3. **Future: Interactive guided problem-solving agents** - help users apply research learnings to build solutions

### Beliefs to Test Through MVP Experiment:
- Guided visualization meaningfully improves learning retention and application (vs. explanation alone)
- Personalization based on user's background/goals improves comprehension speed and depth
- Socratic questioning helps users connect research concepts to their specific problems
- Users value integration/application support over just faster summarization

---

## Solution Hypotheses

### Hypothesis 1: "Guided Learning Companion" (Level 2: Collaborator)
**Autonomy Level:** Collaborator

**What AI Does Autonomously:**
- Collects user's background, goals, and learning preferences upfront
- Analyzes the research paper and generates personalized conceptual explanation
- Retrieves relevant pedagogy best practices from RAG corpus
- Proposes multi-turn learning pathway with checkpoints
- Generates guided visualization script for integration session
- Asks Socratic questions to connect concepts to user's context

**Human Touchpoints:**
- User provides initial context (role, goal, time available, learning depth desired)
- User controls pace - can deep-dive, skip ahead, or request clarification
- User reflects during guided visualization
- User decides if/when to design experiment (AI assists but doesn't force)

**Interaction Pattern:**
Conversational, user-paced flow. AI leads the learning journey but user controls navigation.

**Scope Boundaries:**
- **Does:** Personalized explanation, Q&A, visualization, experiment design support
- **Doesn't:** Paper discovery, code analysis, autonomous experiment execution

---

### Hypothesis 2 (SELECTED FOR MVP): "Adaptive Tutor with Checkpoints" (Level 2-3: Collaborative Agent)
**Autonomy Level:** Collaborative Agent

**What AI Does Autonomously:**
- **Collects user context upfront** (one-time per session):
  - Professional role (ML engineer, research scientist, etc.)
  - Background/expertise relevant to paper topic
  - Learning goal (solve specific problem, continuous learning, explore capability)
  - Time available & desired depth
- **Generates personalized learning strategy** using RAG best practices + user context
- **Breaks paper into learning modules** (e.g., motivation → core technique → results → application)
- **After each module:** Comprehension check + adaptive path adjustment based on responses
- **Retrieves relevant pedagogy/visualization scripts** from RAG corpus
- **Delivers guided visualization** after conceptual learning complete
- **Proactively generates experiment design template** tailored to user's goal (user reviews/modifies)

**Human Touchpoints:**
- Provide initial context (role, background, goal, time/depth)
- Engage in comprehension checks (AI adapts based on answers)
- Accept/modify suggested learning path adjustments
- Participate in guided visualization
- Review and refine experiment design

**Interaction Pattern:**
Structured conversational flow. AI leads with personalized modules, checks understanding, adapts pacing. User controls depth at checkpoints.

**Scope Boundaries:**
- **Does:** Upfront personalization, modular learning, comprehension checks, adaptive pacing, guided visualization, experiment design support
- **Doesn't:** Persistent profiles across sessions (future), paper discovery, code analysis, asynchronous execution

**Why Selected:**
- Structured modules enable systematic evaluation
- Comprehension checks generate data on learning effectiveness
- Proactive experiment generation tests key differentiator
- Balances autonomy with human oversight for safe testing
- Achievable within 6-week timeline
- User context informs all outputs for personalization testing

---

### Hypothesis 3: "Learning Path Orchestrator" (Level 3: Agent)
**Autonomy Level:** Agent

**What AI Does Autonomously:**
- Collects user context once, stores profile for future sessions
- Analyzes paper complexity and user's background to auto-generate optimal learning strategy
- Executes full learning session asynchronously (user can start/stop)
- Creates comprehensive learning artifact (summary + connections + visualization script + experiment plan)
- Flags specific sections that need user attention ("This assumption may not hold in your domain")

**Human Touchpoints:**
- Initial profile setup (one-time)
- Review complete learning artifact package
- Deep-dive on flagged areas requiring attention
- Final decision on experiment approach

**Interaction Pattern:**
AI works more autonomously. User kicks off session, AI generates complete learning package, user reviews and engages with specific elements.

**Scope Boundaries:**
- **Does:** Full autonomous learning package generation with smart flagging
- **Doesn't:** Force synchronous interaction, make implementation decisions

**Future Enhancement:**
Potential evolution target for Sprint 2-3 with asynchronous execution, smart flagging, and persistent profiles.

---

## Chosen Solution

### Solution Name: Adaptive Tutor with Checkpoints (Personalized Research Learning Agent)

### Solution Logic (MVP Scope)
"If we implement an **Adaptive Tutor that personalizes research paper learning through modular instruction and guided visualization**, it will produce **faster comprehension, deeper retention, and ability to apply learnings to user's context** because:

1. **Personalization** (using user context + RAG best practices) matches explanations to the user's background, reducing cognitive load
2. **Modular structure** breaks complex papers into digestible chunks with clear learning objectives
3. **Guided visualization** embeds learning at a subconscious level for better retention and application

*(Note: Comprehension checks and adaptive pacing moved to future enhancements for MVP scope simplification)*"

### Trade-offs Accepted
- **Autonomy level chosen:** Collaborative Agent (Level 2-3)
- **What we're optimizing for:** Balance of impact (testing all key differentiators) and feasibility (achievable in 6 weeks with existing infrastructure)
- **What we're accepting:**
  - Session-based context (not persistent profiles across sessions - future enhancement)
  - Synchronous interaction (not asynchronous execution - future enhancement)
  - Manual paper input (not automated paper discovery - future enhancement)
  - No experiment design guidance in MVP (future enhancement)

### Detailed Design

**Agent Autonomous Capabilities (MVP Scope):**
- Collect user context upfront (role, background, learning goal, time/depth preferences)
- Analyze research paper and determine optimal modular breakdown based on user context
- Query RAG corpus for relevant pedagogical best practices and learning strategies
- Generate personalized explanations for each module tailored to user's background
- Query RAG corpus for appropriate guided visualization scripts
- Generate personalized visualization script incorporating paper concepts and user's application context
- Guide user through visualization session with appropriate pacing

**Agent Autonomous Capabilities (Future Enhancements):**
- Create comprehension check questions after each module
- Analyze user responses and adapt pacing/depth for subsequent modules (adaptive pacer)
- Proactive experiment design generation and guidance

**Human-in-the-Loop Touchpoints:**
- **Session initiation:** Provide context (role, background, goal, time/depth)
- **During modules:** Ask questions, request clarification, or pause for reflection as needed
- **Path adjustment points:** Request modification to depth/pacing at any time
- **Visualization session:** Participate actively in guided visualization experience
- **Session reflection:** Share insights on what resonated and what to apply

**Interaction Pattern:**
Structured conversational flow with clear phases:
1. **Context Collection** (5 min) - AI asks targeted questions to understand user
2. **Learning Strategy Preview** (2 min) - AI shares proposed module structure, user confirms/adjusts
3. **Modular Learning** (30-50 min) - AI teaches concepts through personalized modules → user can ask questions or request adjustments
4. **Visualization Integration** (10-15 min) - AI guides user through personalized visualization session
5. **Wrap-up** (5 min) - AI helps user identify key takeaways and potential applications

Total session: 50-75 minutes depending on user's time preference and depth selected

**Success Metrics:**

*Primary Metrics (What we're testing in MVP):*
- **Comprehension depth:** User can explain core concepts and connect to related techniques (measured via reflection dialogue and post-session assessment)
- **Perceived personalization value:** User reports explanations matched their background (post-session survey)
- **Retention improvement:** User can recall key concepts after visualization (follow-up assessment)
- **Application connection:** User can articulate how learnings apply to their context (reflection dialogue)

*Secondary Metrics:*
- **Time efficiency:** Achieve deep understanding in 45-75 min (vs. 1-5 hours traditional reading)
- **User satisfaction:** Would user choose this over traditional paper reading or ChatGPT summarization?

*Future Metrics (post-MVP):*
- Experiment design quality and implementation success
- Learning transfer across multiple papers
- Long-term retention (1 week, 1 month follow-ups)

### Scope Boundaries

**What this MVP solution does:**
- Accept research paper (PDF or text input) from user
- Collect user context and learning goals
- Generate personalized, modular learning experience
- Provide comprehension checks and adaptive pacing
- Deliver guided visualization for learning integration
- Help user connect concepts to their specific context through Socratic dialogue

**What this MVP solution doesn't do (Future Enhancements):**
- Paper discovery or recommendation (user must provide paper)
- Code repository analysis or implementation details extraction
- Persistent user profiles across sessions
- Proactive experiment design generation and guidance
- Asynchronous learning package generation
- Multi-paper synthesis or comparative analysis
- Automated follow-up assessments for retention tracking

### Technical Architecture (High-Level)

**Components (MVP Scope):**
1. **Context Collector** - Structured dialogue to gather user info
2. **Paper Analyzer** - Extract structure and key concepts from paper
3. **Strategy Generator** - Use RAG + user context to create learning plan
4. **Module Generator** - Create personalized explanations for each learning module
5. **Visualization Scripter** - Generate personalized guided visualization from RAG templates
6. **Reflection Facilitator** - Socratic dialogue to help user apply learnings

**Components (Future Enhancements):**
7. **Comprehension Assessor** - Generate questions and evaluate responses
8. **Adaptive Pacer** - Adjust depth/speed based on comprehension check results
9. **Experiment Design Guide** - Help user design validation experiments

**Data Sources:**
- User-provided research paper (PDF/text)
- RAG corpus: best_practices/, hypnosis_scripts/, techniques/
- Session context (stored in memory for duration of session)

**Integration Points:**
- Mock RAG system (existing infrastructure in `your_workspace/data/mock_rag/`)
- LLM for generation and adaptation (Claude/GPT)
- Session state management (in-memory for MVP)

---

## Experiment Plan

### Overview
Two separate experiments to validate key assumptions:
1. **Experiment 1:** Personalized modular learning effectiveness (time + comprehension)
2. **Experiment 2:** Guided visualization script quality (expert review)

---

### Experiment 1: Personalized Modular Learning - Time & Comprehension Validation

#### Core Assumption Being Tested
"Personalized modular instruction (without visualization) enables users to achieve deep comprehension in 50-75 minutes, faster than traditional paper reading (1-5 hours) while maintaining or improving comprehension quality."

#### Experiment Design

**What we're testing:**
- MVP components: Context Collector + Paper Analyzer + Strategy Generator + Module Generator + Reflection Facilitator (NO Visualization Scripter yet)
- Comparison: MVP modular approach vs. traditional paper reading

**How we'll test it:**
- **Participants:** 3-5 ML practitioners with varying backgrounds
- **Method:** Within-subjects comparison
  - Each participant processes 2 research papers (matched for complexity)
  - **Paper A (Control):** Traditional reading approach (their normal method - PDF reading, note-taking, ChatGPT if they use it)
  - **Paper B (Treatment):** Full MVP modular learning session (Context → Strategy → Modules → Reflection)
  - Counterbalanced order (half do A first, half do B first)

**Sample size:** 3-5 participants × 2 papers each = 6-10 data points

**Duration:** 2 weeks
- Week 1: Recruit participants, prepare 2 research papers
- Week 2: Run sessions, collect data

#### Success Metrics

**Primary Metrics:**
1. **Time efficiency:** Time to achieve "comprehension threshold" (can explain core concepts)
   - Target: MVP session ≤ 75 min vs. traditional ≥ 90 min
2. **Comprehension depth:** Post-session assessment (standardized questions about concepts, connections, applicability)
   - Target: MVP score ≥ traditional score (at minimum equal, ideally better)

**Secondary Metrics:**
3. **Perceived personalization value:** Rating (1-5) on "explanations matched my background"
4. **Application readiness:** Can participant articulate how to apply concepts to their context?
5. **User preference:** Which method would they choose for future papers?

#### Success Criteria

**Experiment succeeds if:**
- MVP time ≤ 75 minutes AND comprehension score ≥ 80% of traditional method score
- At least 3 out of 5 participants prefer MVP over traditional method
- Users report high personalization value (avg ≥ 4/5)

**Experiment fails if:**
- MVP takes longer than traditional method OR comprehension drops significantly (< 70% of traditional score)
- MVP requires more than 90 minutes on average
- Users find MVP confusing or not worth the time investment

---

### Experiment 2: Guided Visualization Script - Expert Quality Review

#### Core Assumption Being Tested
"The AI-generated visualization scripts adhere to best practices for guided visualization and effectively cover the learning topics from the research paper."

#### Experiment Design

**What we're testing:**
- Visualization Scripter component: Quality of RAG-generated personalized visualization scripts

**How we'll test it:**
- Generate 3-5 visualization scripts from different research papers and user contexts
- Submit scripts to hypnosis/guided visualization expert for structured review

**Sample size:** 3-5 generated scripts (varying paper topics and user contexts)

**Duration:** 1 week
- Generate scripts using Visualization Scripter
- Expert review (can be async, allow 3-5 days for feedback)

#### Success Metrics

**Primary Metrics:**
1. **Best practice adherence:** Expert rating on how well scripts follow guided visualization principles
   - Target: ≥ 4/5 on average across evaluation criteria
2. **Content coverage:** Expert assessment of how well script covers key learning concepts from paper
   - Target: All major concepts incorporated meaningfully

**Secondary Metrics:**
3. **Personalization quality:** Does script adapt appropriately to user context?
4. **Usability concerns:** Expert flags any issues that could confuse or disengage users
5. **Improvement recommendations:** Expert provides specific guidance for enhancement

**Evaluation Rubric for Expert:**
- Induction quality (relaxation, focus-building)
- Metaphor/imagery appropriateness for technical concepts
- Pacing and flow
- Integration of learning objectives
- Personalization to user context
- Suggestions phase (application to user's goals)
- Overall effectiveness rating

#### Success Criteria

**Experiment succeeds if:**
- Expert rates scripts ≥ 4/5 on best practice adherence
- All major paper concepts are covered in visualization
- No critical issues flagged (safety, confusion, inappropriate techniques)
- Expert confirms scripts are "production-ready" or "ready with minor edits"

**Experiment fails if:**
- Scripts rated < 3/5 on best practices
- Major learning concepts missing from visualization
- Expert identifies fundamental approach problems requiring redesign
- Scripts would need significant rewriting to be usable

---

### Next Steps Based on Outcomes

**If both experiments succeed:**
- Combine validated components (modular learning + expert-approved visualization)
- Build integrated MVP with full workflow (Context → Modules → Visualization → Reflection)
- Test integrated experience with 2-3 users to validate the complete flow

**If Experiment 1 succeeds but Experiment 2 has issues:**
- Launch MVP with modular learning only
- Work with expert to refine Visualization Scripter
- Add visualization in Sprint 2 after improvements

**If Experiment 1 fails:**
- Analyze bottlenecks (module generation quality? personalization not working? time too long?)
- Iterate on module generation approach
- Consider simplifying to single explanation (not modular) as fallback

**If Experiment 2 fails:**
- Work closely with expert to rebuild visualization script generation logic
- May need to enhance RAG corpus with more detailed hypnosis best practices
- Consider manual script creation for MVP, automate in Sprint 2

**If both experiments have mixed results:**
- Prioritize fixing the component with clearer path to success
- De-risk the more uncertain component through additional iteration
- Consider phased rollout (launch validated component first, add second component later)
