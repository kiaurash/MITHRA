# Step 1 Implementation Guide: RAG + Deep Research Integration

## Overview

Step 1 combines two research sources:
1. **RAG (Retrieval Augmented Generation)**: Query your curated Vector DB for internal knowledge
2. **Deep Research**: Web search for external authoritative sources
3. **Synthesis**: Claude combines both into a grounded, well-researched article

---

## Architecture Options

### **Option 1: Claude Native (RECOMMENDED)**

**Best for**: MVP, simplicity, voice authenticity

```
User Input (Topic)
    ↓
[1. Query Vector DB] → RAG Results
    ↓
[2. Format RAG Context]
    ↓
[3. Send to Claude with Web Search enabled]
    ↓
Claude:
  - Reads RAG context
  - Conducts web search
  - Synthesizes both sources
  - Writes article in BehaviorShift voice
    ↓
Article Output → Gate 1
```

**Pros**:
- Single LLM call handles research + synthesis
- Claude maintains your voice throughout
- No additional APIs needed (if using Claude's web search)
- Simplest implementation

**Cons**:
- Depends on Claude having web search capability
- Less control over which websites are searched

---

### **Option 2: Exa AI + Claude**

**Best for**: Production, higher quality research

```
User Input (Topic)
    ↓
[1. Query Vector DB] → RAG Results
    ↓
[2. Query Exa AI] → Web Research Results
    ↓
[3. Combine RAG + Exa Results]
    ↓
[4. Send to Claude for Synthesis]
    ↓
Article Output → Gate 1
```

**Pros**:
- Exa specializes in research-quality sources
- More control over search quality
- Returns structured, citation-ready results

**Cons**:
- Additional API cost (Exa)
- More complex implementation
- Two separate API calls (Exa + Claude)

---

### **Option 3: Tavily + Claude**

**Best for**: AI agent workflows, good balance

```
User Input (Topic)
    ↓
[1. Query Vector DB] → RAG Results
    ↓
[2. Query Tavily] → Web Research Results
    ↓
[3. Send both to Claude for Synthesis]
    ↓
Article Output → Gate 1
```

**Pros**:
- Tavily designed for AI agents
- Good research quality
- Returns answer + sources

**Cons**:
- Additional API cost
- Similar to Exa but less research-focused

---

## Recommended Implementation: Claude Native

### Step-by-Step Implementation

#### **1. Setup Vector DB (ChromaDB for MVP)**

```python
import chromadb

# Initialize ChromaDB
client = chromadb.PersistentClient(path="./data/vector_db")
collection = client.get_or_create_collection(
    name="behaviorshift_knowledge",
    metadata={"description": "Curated relationship content"}
)

# Add documents to Vector DB (one-time setup)
collection.add(
    documents=[
        "Content from your curated sources...",
        "More content...",
    ],
    metadatas=[
        {"title": "Source 1", "author": "Author Name", "url": "..."},
        {"title": "Source 2", "author": "...", "url": "..."},
    ],
    ids=["doc1", "doc2", ...]
)
```

#### **2. Query Vector DB for RAG**

```python
def query_rag(topic: str, top_k: int = 15):
    """Get relevant content from Vector DB"""

    results = collection.query(
        query_texts=[topic],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    # Filter by relevance (distance < 0.3)
    filtered = [
        {
            "text": results['documents'][0][i],
            "metadata": results['metadatas'][0][i],
            "relevance": 1 - results['distances'][0][i]
        }
        for i in range(len(results['documents'][0]))
        if results['distances'][0][i] < 0.3
    ]

    return filtered
```

#### **3. Format RAG Results for Claude**

```python
def format_rag_context(rag_results):
    """Format RAG results as context for Claude"""

    context = "## Internal Knowledge Base (from Vector DB):\n\n"

    for i, result in enumerate(rag_results, 1):
        context += f"### Internal Source {i}\n"
        context += f"**Title**: {result['metadata']['title']}\n"
        context += f"**Author**: {result['metadata']['author']}\n"
        context += f"**Relevance**: {result['relevance']:.2f}\n\n"
        context += f"{result['text']}\n\n"
        context += "---\n\n"

    return context
```

#### **4. Call Claude with RAG Context + Web Search**

```python
import anthropic

def step1_synthesis(topic, user_context, rag_results):
    """Step 1: Complete RAG + Deep Research + Synthesis"""

    # Load Step 1 prompt template
    with open("step1_knowledge_synthesis_prompt.txt") as f:
        step1_prompt = f.read()

    # Format RAG context
    rag_context = format_rag_context(rag_results)

    # Build complete prompt
    prompt = f"""
{step1_prompt}

---

## USER INPUT:

**Topic**: {topic}
**Context**: {user_context}

---

{rag_context}

---

## YOUR TASK:

You have {len(rag_results)} relevant sources from our internal knowledge base above.

Now:

1. **Conduct web research** on: {topic}
   - Find 5-10 authoritative external sources
   - Prioritize: academic research, expert practitioners (Gottman, Psychology Today, etc.)
   - Extract key insights with citations

2. **Synthesize BOTH internal and external sources** into a comprehensive article:
   - Follow the structure in Phase 4 of the prompt
   - Cite both internal (Vector DB) and external (web) sources inline
   - Maintain BehaviorShift's warm, Socratic voice
   - 1500-2500 words

3. **Include full reference list** for both internal and external sources

Please begin your research and synthesis.
"""

    # Call Claude (with web search if available)
    client = anthropic.Anthropic(api_key="your_key")

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}]
        # TODO: Enable web search tool when available
    )

    return response.content[0].text
```

#### **5. Complete Step 1 Function**

```python
def run_step1(topic, user_context):
    """
    Complete Step 1: Knowledge Synthesis

    Returns: Article ready for Gate 1 validation
    """

    print(f"🔍 Step 1: Researching '{topic}'...")

    # Phase 1: RAG
    print("  → Querying Vector DB...")
    rag_results = query_rag(topic)
    print(f"  ✓ Found {len(rag_results)} internal sources")

    # Phase 2: Deep Research + Synthesis (Claude does both)
    print("  → Claude conducting deep research + synthesis...")
    article = step1_synthesis(topic, user_context, rag_results)
    print(f"  ✓ Article generated ({len(article.split())} words)")

    # Phase 3: Return for Gate 1
    return {
        "article": article,
        "metadata": {
            "topic": topic,
            "internal_sources": len(rag_results),
            "word_count": len(article.split())
        }
    }
```

---

## For Your Experiment (Voice Validation)

### Minimal Implementation for Testing

Since your experiment focuses on **voice authenticity**, you can start with a simplified version:

```python
# EXPERIMENT VERSION: Focus on voice, not infrastructure

def experiment_step1(topic):
    """
    Simplified Step 1 for voice validation experiment

    For the experiment, we care about:
    - Can Claude write in BehaviorShift voice?
    - Can it do Socratic questioning?
    - Can it synthesize research well?

    We DON'T need to test:
    - Vector DB infrastructure (can mock with example content)
    - Web search infrastructure (can use Claude's knowledge)
    """

    # Mock RAG results with example content
    mock_rag_results = [
        {
            "text": "Example curated content about intimacy from your knowledge base...",
            "metadata": {"title": "Understanding Intimacy", "author": "Expert Name"}
        },
        # Add 3-5 more examples
    ]

    # Format mock RAG
    rag_context = format_rag_context(mock_rag_results)

    # Load voice-focused Step 1 prompt
    # ... rest same as above

    # Claude synthesizes with focus on VOICE
    # Gate 1 will validate voice authenticity + Socratic quality
```

**Why this works for the experiment:**
- Tests the critical assumption: Can Claude write in your voice?
- Doesn't require full Vector DB setup (time sink)
- Focus on voice, not infrastructure
- Can validate synthesis quality

**After experiment succeeds:**
- Build full Vector DB with your curated content
- Add real web search integration
- Scale up

---

## Next Steps

### For Experiment (This Week):

1. **Day 1**: Create 10-15 example "curated sources" (text snippets about intimacy)
2. **Day 2**: Mock them as RAG results, run Step 1 with voice-focused prompt
3. **Day 3**: Run Gate 1 on output, evaluate voice authenticity
4. **Days 4-7**: Iterate based on feedback

### For Full Implementation (After Experiment):

1. **Week 2**: Build Vector DB with 50-100 curated sources
2. **Week 3**: Integrate real web search (Claude native or Exa)
3. **Week 4**: Test with multiple topics, refine prompts

---

## Decision Matrix

| Approach | Setup Time | Quality | Cost | Control | Recommended For |
|----------|-----------|---------|------|---------|-----------------|
| **Claude Native** | 1-2 days | Good | Low | Medium | MVP, Experiment |
| **Exa + Claude** | 3-5 days | Excellent | Medium | High | Production |
| **Tavily + Claude** | 3-5 days | Good | Medium | High | AI Agents |
| **Mock (Experiment)** | 1 day | N/A | Low | Full | Voice Testing |

---

## Key Takeaway

**For your voice validation experiment**: Use mock RAG results to test voice authenticity FIRST. Don't build full infrastructure until you know AI can write in your voice.

**For full Sprint 1 implementation**: Use Claude Native (web search) + real Vector DB for simplicity and voice control.

**For production scale**: Consider Exa AI for higher quality research retrieval.
