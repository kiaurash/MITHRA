# Mock RAG Sources for Voice Validation Experiment

This folder contains markdown files that simulate what a Vector DB would return for RAG (Retrieval Augmented Generation).

## Purpose

For the **Sprint 1 Voice Validation Experiment**, these sources will be used to:
1. Test whether Claude can synthesize research in BehaviorShift's authentic voice
2. Validate the Socratic approach (guiding readers to insights)
3. Evaluate groundedness (proper citation of sources)

## How to Add Your Own Sources

### Step 1: Use the Template

Copy `_TEMPLATE.md` and rename it to something descriptive:
- `source_4_communication_patterns.md`
- `source_5_barriers_to_intimacy.md`
- `source_6_creating_rituals.md`

### Step 2: Fill in the Frontmatter

```markdown
---
title: Your Topic Here
author: Your Name
date: 2024-01-15
source_type: article
tags: [tag1, tag2, tag3]
relevance_score: 0.95
---
```

**Fields:**
- `title`: Descriptive title for this source passage
- `author`: Your name or the expert/source name
- `date`: Publication or creation date
- `source_type`: article, research, blog, book_excerpt, expert_interview, etc.
- `tags`: Keywords for organization (not used by loader, just for you)
- `relevance_score`: Optional, 0.0-1.0 (defaults to 0.9 if not provided)

### Step 3: Write Your Content

- **Length**: 300-500 words per file
- **Focus**: One specific aspect/concept per file
- **Voice**: Use your authentic BehaviorShift voice
- **Style**: Warm, introspective, Socratic (questions that invite reflection)
- **Citations**: If referencing research, include it naturally (e.g., "Gottman's research shows...")

### Step 4: Save in This Folder

Save your `.md` file in: `your_workspace/data/mock_sources/`

The loader script will automatically find and use it.

## Current Sources

- `_TEMPLATE.md` - Template for creating new sources (not loaded)
- `example_1_emotional_safety.md` - Example placeholder (replace with real content)
- `example_2_vulnerability.md` - Example placeholder (replace with real content)
- `example_3_small_gestures.md` - Example placeholder (replace with real content)

## Recommended Number of Sources

For the experiment testing topic **"Improving emotional intimacy in long-term relationships"**:

**Minimum**: 10 sources (enough to synthesize a comprehensive article)
**Optimal**: 12-15 sources (provides good coverage without overwhelming)
**Maximum**: 20 sources (beyond this, diminishing returns)

## Suggested Topics to Cover

For the intimacy topic, consider creating sources about:

1. ✓ Emotional safety (example provided)
2. ✓ Vulnerability (example provided)
3. ✓ Small daily gestures (example provided)
4. Communication patterns that foster intimacy
5. The role of listening in emotional connection
6. Navigating conflict while maintaining intimacy
7. Sexual intimacy as part of emotional connection
8. Creating rituals and traditions together
9. Barriers to intimacy (fear, past trauma, defensiveness)
10. Repair after disconnection or hurt
11. The importance of consistency over intensity
12. Making space for individual growth within the relationship

## How the Loader Works

The `load_mock_sources.py` script:
1. Reads all `.md` files in this folder (except `_TEMPLATE.md` and `README.md`)
2. Parses frontmatter metadata
3. Extracts markdown content
4. Formats as RAG results for Step 1
5. Returns them sorted by relevance score

## Tips for Writing Good Sources

**Do:**
- Write in your authentic voice (this is what AI will learn from)
- Include Socratic questions
- Use concrete examples or metaphors
- Keep each file focused on ONE concept
- Show your style of guiding readers to insights

**Don't:**
- Write generic, formal content (AI will copy that voice)
- Make files too long (>500 words becomes unfocused)
- Overlap topics too much between files
- Include content you wouldn't want AI to emulate

## Testing Your Sources

After adding your sources, test the loader:

```bash
python load_mock_sources.py
```

This will show you what the loader finds and how it formats them.

## Next Steps After Creating Sources

1. **Create 10-15 sources** using your authentic writing
2. **Run the loader** to verify they're formatted correctly
3. **Execute Step 1** with these sources to generate test article
4. **Run Gate 1** to validate voice authenticity
5. **Iterate** based on feedback

---

**Remember**: These sources are teaching the AI your voice. Write content you'd be proud to publish under your name!
