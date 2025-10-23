# Workflow Problem Definition: BehaviorShift Learning Platform

## Problem Statement
People struggle to change their behavior even when they intellectually understand what they should do differently (the "knowing-doing gap"). Traditional educational content provides cognitive understanding but fails to create lasting behavioral change because it doesn't address the emotional and subconscious dimensions of human psychology. Manual creation of multi-modal learning content (cognitive + narrative + therapeutic) is time-intensive and requires expertise across multiple domains (instructional design, storytelling, therapeutic scripting, voice production).

## Current State
**Who:** Internal content creation team / Kia as founder
**Frequency:** Per learning module creation (ongoing, multiple modules needed)
**Trigger:** Need to create new soft skills learning content for behavioral change

**How it works now (Manual Process):**
1. Research topic from multiple sources (books, academic papers, expert content)
2. Synthesize research into key insights and learning objectives
3. Design curriculum with lesson structure and activities
4. Separately identify relevant teaching stories and metaphors
5. Craft narrative arc that weaves stories with lessons
6. Write newsletter/article version of content
7. Create personalized therapeutic script for hypnosis/meditation
8. Record or generate voice audio from script
9. Quality check each component for safety and effectiveness
10. Iterate based on feedback

**Friction Points:**
- Research synthesis is time-consuming and requires deep domain knowledge
- Ensuring content is grounded in credible sources requires meticulous citation tracking
- Creating coherent narrative that integrates cognitive learning with emotional storytelling requires creative expertise
- Therapeutic script writing requires safety considerations and personalization
- Voice production adds significant time and cost
- Maintaining consistency across cognitive, narrative, and therapeutic dimensions is challenging
- Each module can take weeks to produce manually
- Quality validation at each stage requires expert review

## Desired State
**What success looks like:**
An automated pipeline where a team member can input a soft skills topic (e.g., "improving intimacy") and their personal context, and receive:
- A well-researched, validated set of learning objectives and lesson plans
- Relevant teaching stories woven into a cohesive narrative arc
- An engaging newsletter article synthesizing the content
- A personalized, safe hypnosis/meditation audio file

All components should be professionally produced, validated for quality and safety, and ready for minimal human review before delivery to end users.

**Key metrics:**
- Time to create complete learning module: From weeks → days
- Content quality: Maintains professional standards (4+/5 rating from expert reviewers)
- Safety validation: 100% pass rate on therapeutic safety checks
- Personalization: Content adapts to user's style preferences and context
- Scalability: Ability to produce multiple modules in parallel

**What would change:**
The team could scale content production 10x, test more learning topics, personalize content for individual users, and focus creative energy on innovation rather than repetitive production tasks.

## Constraints

**Tools Available:**
- Vector DB for curated knowledge base (relationship/soft skills content, teaching stories)
- LLM APIs (for research synthesis, curriculum design, narrative weaving, script generation)
- Web research capabilities for current sources
- Voice synthesis API (e.g., ElevenLabs)
- Development tools (Python, Streamlit for UI)

**Human Control Requirements:**
- **Research validation:** LLM-as-a-Judge can validate groundedness, but humans review final content
- **Narrative quality:** Humans validate that stories are thematically appropriate
- **Therapeutic safety:** CRITICAL - Humans must review therapeutic scripts for safety before audio generation
- **Strategic decisions:** Which topics to prioritize, how to position content
- **Edge cases:** Unusual topics or contexts may require human guidance

**Quality Requirements:**
- All research must be grounded in credible sources with citations
- Learning objectives must follow sound pedagogical principles (Bloom's Taxonomy)
- Teaching stories must be thematically aligned with lessons
- Therapeutic content must pass rigorous safety checks (no harmful suggestions, appropriate for therapeutic context)
- Voice audio must be natural-sounding and properly paced
- Content must be personalized to user's style preference (practical, reflective, story-driven, research-based)

**Compliance/Safety:**
- Therapeutic content requires safety validation before production
- Must not make medical or psychological claims beyond scope
- User privacy: Personal context must be handled appropriately
- Content must be inclusive and avoid harmful stereotypes

## Assumptions Analysis

### Initial Assumptions Identified:
1. AI can synthesize research from RAG + web sources into coherent learning content
2. LLM-as-a-Judge can reliably validate content for groundedness and relevance
3. AI can identify relevant teaching stories from a curated database
4. AI can weave narrative arcs using storytelling structures
5. AI can generate safe therapeutic scripts with proper SSML formatting
6. Voice synthesis quality is sufficient for guided meditation/hypnosis
7. Quality gates can catch safety issues before content reaches users
8. Personalization can be achieved through style adaptation prompts
9. The complete pipeline can run in < 10 minutes per module
10. Internal team can curate sufficient Vector DB content to start

### Validated Constraints:
- Human review required for therapeutic safety (non-negotiable)
- LLM-as-a-Judge effectiveness needs validation with test cases
- Voice synthesis quality acceptable for MVP (validated through testing)
- Content quality dependent on Vector DB coverage (needs curation)

### Flexible Assumptions:
- Processing time can be longer if quality is maintained (< 30 min acceptable for MVP)
- Personalization depth can start simple and improve over time
- Not all components need to be perfect in Sprint 1 - focus on foundation

### Beliefs to Test:
- Can RAG + Deep Research generate research articles that meet professional standards?
- Will LLM-as-a-Judge catch >80% of groundedness/relevance issues?
- Can AI identify thematically appropriate teaching stories from Vector DB?
- How much human editing will completed modules require (<20% target)?
- What is the false positive/negative rate for safety validation?
- Can narrative weaving create emotionally resonant story arcs?
- Will users perceive synthesized voice as credible for therapeutic content?

## Solution Design: Three-Sprint Progressive Build

### Sprint 1: Core Knowledge and Curriculum Engine (CURRENT)
**Autonomy Level:** Collaborator (Level 2)

**What AI Does Autonomously:**
- Fetches knowledge from Vector DB (RAG agent)
- Conducts deep research from curated websites
- Synthesizes research into structured article with citations
- Validates content for groundedness and relevance (Gate 1)
- Generates learning objectives and lesson plans
- Adapts to user's style preference

**Human Touchpoints:**
- Reviews validated curriculum for quality
- Provides feedback if Gate 1 fails content
- Validates that lessons meet professional standards

**Sprint 1 Deliverable:** Functional application producing validated lesson plans in JSON/text format

---

### Sprint 2: Narrative Weaving Engine
**Autonomy Level:** Collaborator (Level 2)

**What AI Does Autonomously:**
- Queries Vector DB for teaching stories based on learning objectives
- Validates stories for thematic relevance (Gate 2)
- Weaves stories into overarching narrative arc
- Synthesizes content into newsletter article format

**Human Touchpoints:**
- Reviews narrative coherence
- Validates story selection appropriateness
- Approves newsletter for distribution

**Sprint 2 Deliverable:** Curriculum augmented with stories and shareable newsletter article

---

### Sprint 3: Multi-Modal and Therapeutic Delivery
**Autonomy Level:** Hybrid (Level 3 for synthesis, Level 2 for therapeutic)

**What AI Does Autonomously:**
- Generates newsletter from curriculum + narrative
- Creates personalized therapeutic script with SSML tags
- **CRITICAL:** Validates therapeutic safety (Gate 3)
- Synthesizes voice audio via API
- Presents complete package for review

**Human Touchpoints:**
- **CRITICAL:** Reviews therapeutic script if Gate 3 flags issues
- **MANDATORY:** Approves therapeutic content before voice generation (workflow halts on Gate 3 failure)
- Validates voice audio quality
- Approves complete module for user delivery

**Sprint 3 Deliverable:** Complete end-to-end prototype with all deliverables (lesson plan, narrative, newsletter, audio)

---

## Scope Boundaries

**What this solution does:**
- Automates research synthesis and curriculum design (Sprint 1)
- Adds narrative layer with teaching stories (Sprint 2)
- Generates multi-modal outputs including therapeutic audio (Sprint 3)
- Validates quality at each stage with LLM-as-a-Judge gates
- Personalizes content based on user style and context
- Creates foundation for scalable content production

**What this solution doesn't do:**
- Doesn't replace human expertise in therapeutic design (collaboration model)
- Doesn't publish content without safety validation
- Doesn't make strategic decisions about which topics to prioritize
- Doesn't handle highly specialized or medical topics (initial scope: soft skills/relationships)
- Doesn't provide real-time coaching or interaction (future enhancement)

## Success Criteria for MVP

**Sprint 1 succeeds if:**
- 3 test scenarios complete end-to-end without errors
- Quality ratings average 3.5+/5
- Gate 1 catches 80%+ of bad content
- <30% of curriculum requires editing

**Sprint 2 succeeds if:**
- Teaching stories are thematically appropriate (4+/5 rating)
- Narrative arc creates emotional resonance
- Newsletter is ready for distribution with minimal editing

**Sprint 3 succeeds if:**
- Gate 3 safety validation is 100% effective (no unsafe content passes)
- Voice audio is natural and therapeutic-quality
- Complete module is production-ready with <20% editing

**Overall MVP success:**
- Time to create module: < 1 day (vs. weeks manually)
- Quality maintains professional standards (4+/5)
- Safety validation is robust (100% on therapeutic content)
- Team can scale to 10+ modules

## Next Steps

**Completed:**
✅ Problem framing and solution design
✅ Experiment design for Sprint 1
✅ YAML workflow generation
✅ Prompt files for Sprint 1 (steps 0, 1, gate 1, step 2)

**In Progress:**
- Sprint 1 implementation (Vector DB setup, Streamlit UI, agents)

**Coming Next:**
- Sprint 1 testing with 3 scenarios
- Sprint 1 demo (Nov 3 target)
- Sprint 2 planning and implementation
