"""
Step 1: Knowledge Synthesis Implementation Example
Combines RAG (Vector DB) + Deep Research (Web Search) using Claude

This example shows how to implement the two-phase research approach:
1. Query internal Vector DB for curated content
2. Use Claude's web search to find external research
3. Claude synthesizes both into grounded article
"""

import anthropic
import chromadb
from pathlib import Path

# ============================================================================
# Configuration
# ============================================================================

ANTHROPIC_API_KEY = "your_api_key_here"
VECTOR_DB_PATH = "./your_workspace/data/vector_db"
STEP1_PROMPT_PATH = "./your_workspace/your_workflows/step1_knowledge_synthesis_prompt.txt"

# ============================================================================
# Phase 1: RAG - Query Vector DB
# ============================================================================

def query_vector_db(topic: str, user_context: dict, top_k: int = 15) -> list:
    """
    Query local Vector DB for relevant content from curated knowledge base.

    Args:
        topic: User's learning topic
        user_context: User's personal context and preferences
        top_k: Number of results to retrieve

    Returns:
        List of relevant passages with metadata
    """
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    collection = client.get_or_create_collection(
        name="behaviorshift_knowledge",
        metadata={"description": "Curated relationship and soft skills content"}
    )

    # Formulate queries (primary + variations)
    queries = [
        topic,  # Primary query
        f"{topic} research",  # Research-focused
        f"{topic} practical applications",  # Practical angle
        # Add more based on user_context if needed
    ]

    # Query with multiple search terms
    all_results = []
    for query in queries:
        results = collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        # Filter by similarity threshold (distance < 0.3 for good matches)
        for i, distance in enumerate(results['distances'][0]):
            if distance < 0.3:  # Similarity threshold
                all_results.append({
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "relevance_score": 1 - distance  # Convert distance to similarity
                })

    # Deduplicate and sort by relevance
    unique_results = {r['text']: r for r in all_results}.values()
    sorted_results = sorted(unique_results, key=lambda x: x['relevance_score'], reverse=True)

    return sorted_results[:top_k]


def format_rag_results(rag_results: list) -> str:
    """Format RAG results for inclusion in Claude prompt."""
    if not rag_results:
        return "No relevant internal sources found."

    formatted = "## Internal Knowledge Base Results:\n\n"
    for i, result in enumerate(rag_results, 1):
        metadata = result['metadata']
        formatted += f"### Source {i}: {metadata.get('title', 'Untitled')}\n"
        formatted += f"**Author**: {metadata.get('author', 'Unknown')}\n"
        formatted += f"**Relevance**: {result['relevance_score']:.2f}\n\n"
        formatted += f"{result['text']}\n\n"
        formatted += "---\n\n"

    return formatted


# ============================================================================
# Phase 2: Deep Research + Synthesis with Claude
# ============================================================================

def step1_knowledge_synthesis(
    topic: str,
    user_context: dict,
    learning_goals: str = "",
    style_preference: str = "balanced"
) -> dict:
    """
    Complete Step 1: RAG + Deep Research + Synthesis

    Args:
        topic: User's learning topic
        user_context: Personal context (dict with background info)
        learning_goals: What user wants to learn (optional)
        style_preference: practical/reflective/story-driven/research-based

    Returns:
        dict with article, metadata, sources
    """

    # Step 1a: Query Vector DB (RAG)
    print(f"🔍 Querying Vector DB for: {topic}")
    rag_results = query_vector_db(topic, user_context)
    print(f"✓ Found {len(rag_results)} relevant internal sources")

    # Step 1b: Format RAG results
    rag_context = format_rag_results(rag_results)

    # Step 1c: Load Step 1 prompt template
    step1_prompt = Path(STEP1_PROMPT_PATH).read_text()

    # Step 1d: Construct complete prompt for Claude
    full_prompt = f"""
{step1_prompt}

---

## USER INPUT:

**Topic**: {topic}

**Personal Context**: {user_context.get('description', 'Not provided')}

**Learning Goals**: {learning_goals or 'Not specified'}

**Style Preference**: {style_preference}

---

{rag_context}

---

## YOUR TASK:

You have access to the Internal Knowledge Base results above (from our curated Vector DB).

Now, please:

1. **Conduct Deep Research** using web search:
   - Search for authoritative sources on: {topic}
   - Prioritize: academic research, expert practitioners (Gottman Institute, Psychology Today, etc.)
   - Find 5-10 high-quality external sources
   - Extract key insights and citations

2. **Synthesize Both Sources**:
   - Combine insights from Internal Knowledge Base (above) + your web research
   - Create a comprehensive, well-researched article following the structure in Phase 4
   - Cite BOTH internal and external sources inline
   - Maintain BehaviorShift's authentic voice (warm, introspective, Socratic)
   - Aim for 1500-2500 words

3. **Include Full References**:
   - List all internal sources (from Vector DB above)
   - List all external sources (from your web research with URLs)

Please proceed with deep research and synthesis now.
"""

    # Step 1e: Call Claude with web search enabled
    print(f"🌐 Claude conducting deep research + synthesis...")
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # NOTE: Web search via MCP or function calling
    # For production, you'd enable web search tool here
    # For now, this shows the prompt structure

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8000,
        temperature=0.7,
        messages=[
            {
                "role": "user",
                "content": full_prompt
            }
        ]
        # In production, add: tools=[web_search_tool]
    )

    article = response.content[0].text

    print(f"✓ Article generated ({len(article.split())} words)")

    # Step 1f: Extract metadata
    metadata = {
        "topic": topic,
        "word_count": len(article.split()),
        "internal_sources_count": len(rag_results),
        "style_preference": style_preference,
        "model": response.model,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        }
    }

    return {
        "article": article,
        "metadata": metadata,
        "rag_sources": rag_results,
        "raw_response": response
    }


# ============================================================================
# Alternative: Using Exa AI for Deep Research
# ============================================================================

def step1_with_exa(topic: str, user_context: dict) -> dict:
    """
    Alternative implementation using Exa AI for web research.

    Exa provides better research-quality results than generic web search.
    """
    from exa_py import Exa

    # Phase 1: RAG
    rag_results = query_vector_db(topic, user_context)

    # Phase 2: Exa web search
    exa = Exa(api_key="your_exa_key")
    web_results = exa.search_and_contents(
        f"{topic} research evidence-based",
        num_results=10,
        use_autoprompt=True,
        text=True,  # Get full text
        highlights=True,  # Get key excerpts
        category="research paper"  # Focus on quality sources
    )

    # Format Exa results
    exa_context = "## External Research (via Exa AI):\n\n"
    for result in web_results.results:
        exa_context += f"### {result.title}\n"
        exa_context += f"**URL**: {result.url}\n"
        exa_context += f"**Published**: {result.published_date}\n\n"
        if result.highlights:
            exa_context += f"{result.highlights[0]}\n\n"
        exa_context += "---\n\n"

    # Phase 3: Claude synthesis (same as above)
    # ... combine rag_context + exa_context and send to Claude

    return {
        "rag_results": rag_results,
        "web_results": web_results,
        # ... synthesized article
    }


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Example: User wants to learn about improving intimacy

    result = step1_knowledge_synthesis(
        topic="Improving emotional intimacy in long-term relationships",
        user_context={
            "description": "Married for 10 years, feeling disconnected, want to rebuild closeness",
            "age_range": "30-40",
            "relationship_status": "married"
        },
        learning_goals="Understand practical ways to deepen emotional connection and rebuild intimacy",
        style_preference="balanced"  # Mix of research + practical + reflective
    )

    print("\n" + "="*80)
    print("GENERATED ARTICLE:")
    print("="*80)
    print(result['article'])
    print("\n" + "="*80)
    print("METADATA:")
    print("="*80)
    print(f"Word count: {result['metadata']['word_count']}")
    print(f"Internal sources: {result['metadata']['internal_sources_count']}")
    print(f"Tokens used: {result['metadata']['usage']}")
