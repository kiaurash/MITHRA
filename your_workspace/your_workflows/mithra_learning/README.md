# MITHRA - Personalized Research Learning Agent

**Machine Intelligence for Translating Human Research into Action**

## Purpose

MITHRA solves the problem of spending 1-5 hours struggling through dense research papers and still failing to deeply understand or apply the concepts. This workflow provides a personalized 50-75 minute learning session that produces:
- Deep comprehension tailored to your background
- Guided visualization script for learning integration
- Clear action plan for applying concepts to your specific context

## What Makes MITHRA Different

Unlike ChatGPT summaries or traditional reading:
- **Personalized to YOU:** Explanations adapt to your role, background, and learning goals
- **Modular learning:** Complex sources broken into digestible, sequenced modules
- **Guided visualization:** Includes hypnosis-informed script for deeper retention
- **Application-focused:** Connects abstract concepts to your specific problems/goals

## How to Use

### Prerequisites
- A research paper, article, webinar transcript, or conference talk you want to learn from
- 50-75 minutes of uninterrupted time
- Your learning goal (solve problem / continuous learning / explore capability)

### In an LLM CLI (like Claude Code):

```bash
Execute workflow mithra_learning
```

The agent will guide you through all 7 steps automatically.

### In a web chat (ChatGPT, Claude.ai, etc.):

Copy and paste each prompt file in sequence:

1. Copy `step1_context_collection_prompt.txt` → paste in chat → answer questions about your context
2. Copy `step2_source_analysis_prompt.txt` → paste in chat → provide your source material
3. Copy `step3_strategy_generation_prompt.txt` → paste in chat → confirm learning strategy
4. Copy `step4_module_delivery_prompt.txt` → paste in chat → engage with learning modules
5. Copy `step5_visualization_script_generation_prompt.txt` → paste in chat → receive visualization script
6. Copy `step6_script_delivery_prompt.txt` → paste in chat → get usage instructions
7. Copy `step7_reflection_prompt.txt` → paste in chat → reflect and create action plan

## Workflow Structure

**Step 1: Context Collection** (5 min)
- Gather your role, background, learning goal, and preferences
- Output: User context profile

**Step 2: Source Analysis** (5-10 min)
- Analyze your source material (paper/article/transcript/talk)
- Extract structure and key concepts
- Output: Source analysis with complexity assessment

**Step 3: Strategy Generation** (5 min)
- Create personalized learning plan using pedagogical best practices
- Design 3-5 learning modules tailored to your context
- Output: Personalized learning strategy

**Step 4: Module Delivery** (30-50 min)
- Interactive learning session through personalized modules
- Concepts explained with your background in mind
- Adapt pacing based on your engagement
- Output: Learning notes with key concepts

**Step 5: Visualization Script Generation** (5-10 min)
- Generate guided visualization script incorporating your learnings
- Personalized metaphors and imagery for your context
- Output: 15-20 minute visualization script for audio conversion

**Step 6: Script Delivery** (2-5 min)
- Provide script with usage instructions
- Guidance on converting to audio (TTS tools)
- Output: Ready-to-use script file

**Step 7: Reflection** (5-10 min)
- Reflect on learnings and identify applications
- Create concrete action plan
- Output: Reflection summary with next steps

**Total Time:** 50-75 minutes (varies by source complexity and depth preference)

## Expected Outputs

After completing the workflow, you'll have:

### Learning Materials
- `session_[timestamp]_context.md` - Your profile and preferences
- `session_[timestamp]_source_analysis.md` - Source breakdown and concepts
- `session_[timestamp]_learning_strategy.md` - Personalized learning plan
- `session_[timestamp]_learning_notes.md` - What you learned in each module

### Integration Tools
- `session_[timestamp]_visualization_script.txt` - Guided visualization for audio conversion
- Audio conversion guidance for text-to-speech tools

### Action Planning
- `session_[timestamp]_reflection_summary.md` - Key takeaways and next steps

All files saved in: `your_workspace/data/sessions/`

## Success Metrics

You'll know MITHRA worked if:

**Comprehension:** You can explain core concepts and connect them to related techniques

**Time Efficiency:** You achieved deep understanding in 50-75 minutes (vs. 1-5 hours traditional reading)

**Personalization:** Explanations matched your background (you didn't get lost in jargon or bored with basic content)

**Application:** You can articulate how concepts apply to your specific context/problem

**Retention:** After using visualization audio, you can recall concepts more easily

## Using Your Visualization Script

### Converting to Audio
Recommended TTS tools:
- **ElevenLabs** - Highest quality, natural voices (paid)
- **Google Cloud TTS** - Professional quality (free tier available)
- **Natural Reader** - Easy to use (free/paid)
- **Amazon Polly** - AWS service (paid)

### Practice Schedule
- **First listen:** Within 24-48 hours of session
- **Reinforcement:** 2-3 times during week 1
- **Maintenance:** Weekly for first month
- **As needed:** When working on related topics

### Why Visualization Works
- Engages multiple brain regions (visual, spatial, conceptual)
- Creates stronger memory traces than passive review
- Makes abstract concepts concrete through metaphor
- Rehearses application in advance
- Improves recall when you need the knowledge

## Tips for Best Results

### Before the Session
- Have your source material ready (PDF, link, or text)
- Block 50-75 minutes of uninterrupted time
- Be clear on why you're learning this (your goal)

### During the Session
- Engage actively - ask questions when concepts are unclear
- Request examples that relate to your work
- Pause to reflect when needed
- Be honest about your background (don't pretend expertise you don't have)

### After the Session
- Convert visualization script to audio promptly
- Listen to audio within 24-48 hours
- Follow through on your action plan
- Keep session notes for future reference

## Troubleshooting

**"The session is taking longer than expected"**
- You can request to condense remaining modules
- Or adjust depth preference mid-session

**"I'm not understanding a concept"**
- Ask for different explanation or analogy
- Request examples from your domain
- Ask to slow down or break into smaller pieces

**"I don't have time for the full session"**
- Consider stopping after module delivery (you'll still have learning notes)
- Return later to complete visualization and reflection steps

**"The visualization script feels generic"**
- It should include your specific goal and context
- If not, request revision with more personalization

## Future Enhancements

This MVP includes core components. Future versions will add:
- Comprehension checks after each module
- Adaptive pacing based on your responses
- Proactive experiment design assistance
- Code repository analysis for papers with implementations
- Persistent user profiles across sessions
- Multi-paper synthesis and comparison

## Feedback

MITHRA is under active development. Your feedback helps improve the experience:
- What worked well?
- What could be improved?
- Would you use MITHRA for future papers/articles?

Please share feedback in your reflection summary or reach out directly.

---

## Technical Notes

### Components
1. **Context Collector** - Gathers user background and preferences
2. **Source Analyzer** - Extracts structure from papers/articles/transcripts/talks
3. **Strategy Generator** - Creates personalized learning plan using RAG best practices
4. **Module Generator** - Delivers adaptive learning modules
5. **Visualization Scripter** - Generates guided visualization using RAG templates
6. **Reflection Facilitator** - Helps user connect learning to context

### Data Sources
- User-provided source material (PDF/text/link)
- RAG corpus: `best_practices/`, `hypnosis_scripts/`, `techniques/`
- Session context stored in memory during workflow

### Current Scope (MVP)
- ✅ Context collection and personalization
- ✅ Flexible source analysis (papers/articles/transcripts/talks)
- ✅ RAG-powered strategy generation
- ✅ Modular learning delivery
- ✅ Guided visualization script generation
- ✅ Reflection and action planning
- ⏭️ Audio generation (user handles with TTS tools)

### Out of Scope (Future)
- Paper discovery/recommendation
- Code repository analysis
- Automated comprehension checks
- Adaptive pacing algorithms
- Experiment design guidance
- Persistent cross-session profiles
- Audio generation automation

---

**Version:** 1.0 (MVP)
**Last Updated:** 2025-10-29
**License:** [Your License]
**Contact:** [Your Contact Info]
