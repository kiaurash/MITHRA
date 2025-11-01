# Workflow Problem Definition

## Problem Statement
Weekly LinkedIn content performance analysis requires manual context-switching between multiple tools (LinkedIn API, Excel, ChatGPT) to gather data, calculate engagement scores, analyze sentiment, and generate comparative reports with recommendations. This process is time-consuming and creates friction in deriving actionable insights for campaign improvements.

## Current Workflow
**Who:** Marketing team working on marketing strategy improvements
**Frequency:** Weekly (to review previous week's posts and plan upcoming content)
**Trigger:** Scheduled weekly review cycle

**Current Steps:**
1. Extract post data from LinkedIn using LinkedIn APIs
2. Import data into Excel for engagement score calculations
3. Manually review comments for sentiment analysis (using gut feeling and occasionally ChatGPT)
4. Manually compile analysis across tools
5. Generate comparison report between recent campaigns
6. Create recommendations for improvement
7. Compare current performance against previous recommendations

**Friction Points:**
- Constant context-switching between LinkedIn API, Excel, and ChatGPT
- Manual sentiment analysis is inconsistent (gut feeling vs. ChatGPT)
- Manual compilation of data from different sources is time-consuming
- Tracking historical recommendations and their outcomes requires manual cross-referencing

## Desired Outcome
**Success looks like:** An automated report that:
- Compares performance across recent marketing campaigns
- Provides engagement scores and sentiment analysis
- Offers recommendations for campaign improvements
- Contrasts current performance against previous recommendations and their outcomes
- Reduces context-switching and manual data compilation

**Key metrics:**
- Time saved per weekly analysis (target: 2x faster)
- Consistency in sentiment analysis methodology
- Accuracy of performance predictions vs. actual results
- Quality and actionability of recommendations (as judged by human reviewers)

## Constraints
**Tools Available:**
- LinkedIn API credentials
- Excel for calculations
- ChatGPT/LLM access

**Human Control Requirements:**
- Human judgment required for interpreting why posts performed well/poorly
- Agent can suggest interpretations but must ask for human clarification/verification
- Sentiment analysis needs human oversight for contextually relevant information
- Human must validate quality of report components

**Quality Requirements:**
- Report must contain all essential components (engagement scores, sentiment analysis, shares, comparisons, recommendations)
- Predicted performance should be close to actual results
- Recommendations must be actionable and based on validated insights

## Assumptions Analysis

### Initial Assumptions Identified:
1. Sentiment analysis requires human judgment due to contextual information
2. Excel is necessary for engagement score calculations
3. Human must judge why posts performed well/poorly
4. The entire workflow must be completed in the same weekly session
5. LinkedIn API data extraction is a separate manual step
6. Historical recommendation tracking requires manual cross-referencing
7. Performance predictions must be numerically accurate to be useful

### Validated Constraints:
- Human judgment required for interpreting why posts performed well/poorly (agent can suggest, must ask for verification)
- Sentiment analysis needs human oversight for contextually relevant information
- Human must validate quality of report components

### Flexible Assumptions:
- Excel is not necessary - calculations can be automated within the workflow
- LinkedIn API extraction can be automated with a simple wrapper
- Historical recommendation tracking can start manual but should be automated with collected data over time
- Numerical accuracy of predictions is less critical than providing good arguments about performance drivers to help marketing team strategize

### Beliefs to Test:
- Can AI perform initial sentiment analysis and flag ambiguous cases for human review?
- What level of context does AI consistently miss in sentiment analysis?
- How much time can be saved by automating data collection and calculation steps?
- What format of performance arguments (vs. numerical predictions) is most useful for marketing strategy?

## Solution Hypotheses

### Hypothesis 1: AI Collaborator - Full Draft with Review (SELECTED STARTER)
**Autonomy Level:** Collaborator (Level 2)

**What AI Does Autonomously:**
- Fetches LinkedIn data via API wrapper
- Calculates engagement scores
- Performs sentiment analysis on comments
- Drafts complete comparative report with recommendations
- Flags ambiguous sentiment cases for human attention

**Human Touchpoints:**
- Reviews entire draft report
- Validates sentiment analysis (especially flagged cases)
- Adjusts or approves AI's performance interpretations
- Edits recommendations before sharing with team

**Interaction Pattern:**
AI works asynchronously to generate weekly draft report; human reviews in weekly session and makes final adjustments before distribution.

**Scope Boundaries:**
- **Does:** Data collection, metric calculation, sentiment analysis, draft generation
- **Doesn't:** Make final strategic decisions, publish reports without review, access systems beyond LinkedIn API

**Evolution Path:** This solution sets up infrastructure for Solutions 2 & 3 with higher autonomy levels.

---

### Hypothesis 2: AI Agent - Routine Analysis with Collaborative Edge Cases
**Autonomy Level:** Agent (Level 2.5 → 3)

**What AI Does Autonomously:**
- Runs weekly analysis automatically (data fetch, calculations, sentiment)
- Generates complete report for "normal" weeks (performance within expected ranges)
- Stores report and makes it available to marketing team

**Human Touchpoints (Exception-Triggered):**
- AI flags when: sentiment is ambiguous, performance deviates significantly from predictions, or conflicting patterns emerge
- Human reviews flagged items and provides guidance
- Human validates recommendations before they're added to historical tracking

**Interaction Pattern:**
AI runs on schedule; human notified only when judgment is needed.

**Scope Boundaries:**
- **Does:** Autonomous routine reporting, exception detection, historical tracking
- **Doesn't:** Handle edge cases without human input, make strategic pivots independently

**Evolution Path:** Implements A/B testing capability to validate against Solution 1 performance.

---

### Hypothesis 3: AI Agent - Autonomous Data Pipeline + Collaborative Strategy Layer
**Autonomy Level:** Hybrid (Level 3 for data, Level 2 for strategy)

**What AI Does Autonomously:**
- Automated data collection and metric calculation (runs on schedule)
- Sentiment analysis with confidence scores
- Historical tracking and trend identification
- Generates data-rich performance dashboards automatically

**What AI Collaborates On:**
- Presents insights and asks strategic questions ("Post X outperformed despite lower reach - what context should I consider?")
- Co-creates recommendations through dialogue with human
- Learns from human feedback to improve future interpretations

**Human Touchpoints:**
- Weekly strategy session where AI presents data and facilitates discussion
- Human provides context and validates AI's strategic interpretations
- Human approves final recommendations

**Interaction Pattern:**
AI acts as thought partner in structured strategy sessions; data work runs continuously in background.

**Scope Boundaries:**
- **Does:** Full data automation, strategic facilitation, learning from human input
- **Doesn't:** Make strategic recommendations without collaborative dialogue

## Chosen Solution

### Solution Name: AI Collaborator - Full Draft with Review

### Solution Logic
"If we implement **an AI collaborator that autonomously fetches LinkedIn data, calculates metrics, analyzes sentiment, and drafts complete weekly performance reports**, it will produce **50% time savings (from ~4 hours to ~2 hours per week) and more consistent analysis methodology** because **the AI eliminates manual context-switching between tools, automates repetitive data gathering and calculation tasks, and applies standardized sentiment analysis—while humans retain control over strategic interpretations and final recommendations**."

### Trade-offs Accepted
- **Autonomy level chosen:** Collaborator (Level 2)
- **What we're optimizing for:** Time savings and consistency while building confidence in AI-driven analysis
- **What we're accepting:** Human still reviews full report (higher time investment than Level 3 solutions), but this provides learning opportunity and validation path toward higher autonomy

### Detailed Design

**Agent Autonomous Capabilities:**
- Fetches all LinkedIn post data via API wrapper (posts, engagement metrics, comments, shares)
- Calculates engagement scores using defined formulas
- Performs sentiment analysis on all comments with confidence scoring
- Identifies and flags ambiguous sentiment cases (conflicting signals, sarcasm detection, context-dependent language)
- Generates comparative analysis across campaign periods
- Drafts performance interpretations with supporting evidence
- Proposes recommendations based on historical patterns
- Creates structured report in markdown format

**Human-in-the-Loop Touchpoints:**
- Weekly review session: Human receives complete draft report
- Validates AI's sentiment analysis, especially flagged ambiguous cases
- Reviews and adjusts AI's performance interpretations ("Why did this post succeed?")
- Edits, approves, or rewrites recommendations based on strategic context AI might lack
- Adds contextual information AI couldn't access (internal campaigns, market events, etc.)
- Approves final report before distribution to marketing team

**Interaction Pattern:**
AI works asynchronously throughout the week. Human triggers report generation (or runs on schedule), receives draft within minutes, conducts review session (30-60 min), and finalizes for team distribution. Over time, human feedback helps AI improve interpretation quality.

**Success Metrics:**
- **Time saved:** 50% reduction (from 4 hours to 2 hours per week)
- **Quality improvement:** Consistent sentiment analysis methodology, reduced errors in metric calculations
- **Other benefits:** Faster turnaround enables more timely strategic adjustments, historical tracking becomes feasible

### Scope Boundaries
**What this solution does:**
- Complete automation of data collection and metric calculation
- Standardized sentiment analysis with flagging system
- Draft report generation with comparative analysis
- Foundation for future automation (Solutions 2 & 3)

**What this solution doesn't do:**
- Doesn't publish reports without human review
- Doesn't access data beyond LinkedIn API scope
- Doesn't make final strategic decisions independently
- Doesn't automatically track historical recommendations (manual for now, automated later)

## Experiment Plan

### Core Assumption Being Tested
"An AI agent can fetch LinkedIn data, calculate engagement scores, analyze sentiment, and draft weekly performance reports that require minimal editing (< 30 min review time), saving the marketing team 2+ hours per week compared to the current manual 4-hour process."

### Experiment Design
**What we're testing:** AI's ability to autonomously generate draft weekly LinkedIn performance reports with accurate data collection, metric calculation, sentiment analysis, and actionable recommendations

**How we'll test it:**
- Week 1 (Validation): AI generates draft report in parallel with manual process; compare outputs for accuracy and quality
- Week 2 (Adoption): AI generates draft report as primary source; human validates and adjusts as needed

**Sample size:** 2 weekly reports

**Duration:** 2 weeks

### Success Metrics

**Primary Metric:**
- Time saved: Target 50% reduction (from 4 hours to < 2 hours per weekly report)

**Secondary Metrics:**
- Sentiment analysis accuracy: >80% agreement with human judgment
- Engagement score calculation: 100% accuracy (deterministic calculation)
- Report draft quality: Requires < 30 minutes of human editing/validation
- Usability: Marketing team finds AI-generated insights actionable

### Success Criteria

**Experiment succeeds if:**
- Time spent on report generation reduces to < 2 hours per week by Week 2
- AI sentiment analysis agrees with human judgment in >80% of cases
- Human editing/validation time is < 30 minutes per report
- Marketing team can use the report for strategic decisions with confidence

**Experiment fails if:**
- AI outputs require more time to fix/validate than doing it manually (> 4 hours total)
- Sentiment analysis accuracy is < 60% (too many errors to trust)
- Critical data or metrics are missing/incorrect in more than 10% of cases
- Report structure or insights are not actionable for strategy discussions

### Next Steps

**If successful:**
- Build full workflow implementation with YAML structure and prompt files
- Deploy as standard weekly process for marketing team
- Begin collecting data for future automation (toward Solution 2)

**If it fails:**
- Analyze failure mode: Was it data collection, sentiment analysis, or report generation?
- Consider pivoting to Solution 3 (separate data automation from strategic collaboration)
- Adjust scope: Perhaps start with data collection + sentiment analysis only, manual report writing

**If mixed results:**
- Identify which components worked well (keep those) vs. which need improvement
- Iterate on weak areas (e.g., improve sentiment analysis prompts, refine engagement score formula)
- Run second 2-week experiment with adjustments
