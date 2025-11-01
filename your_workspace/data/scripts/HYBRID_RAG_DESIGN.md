# Hybrid RAG Design: BM25 + ReAct + Vector Search

## Architecture Overview

```
User Query
    |
    v
[1] BM25 Keyword Search (grep)
    |
    v
[2] ReAct Reasoning Loop
    |-- Observation: BM25 results
    |-- Thought: LLM analyzes relevance
    |-- Action: Refine search or request vector search
    |
    v
[3] Filtered Vector Search
    |-- Vector similarity on BM25-filtered docs
    |
    v
Final Results (ranked by relevance)
```

## Why This Approach?

### Problems with Pure Vector Search:
- Misses exact keyword matches (e.g., "NLP anchoring" vs "resource anchoring")
- Can retrieve semantically similar but contextually wrong content
- No interpretability of why documents were retrieved

### Benefits of Hybrid:
1. **BM25 Layer**: Fast, exact keyword matching (grep on markdown files)
2. **ReAct Layer**: LLM reasoning about relevance, can ask clarifying questions
3. **Vector Layer**: Semantic similarity on pre-filtered, relevant documents
4. **Efficiency**: Vector search only on BM25 candidates (not entire corpus)

## Implementation Plan

### Phase 1: BM25 Search Tool
```python
def bm25_search(query: str, corpus_path: Path, top_k: int = 20):
    """
    Use grep to find documents containing query keywords.
    Returns: List of {file_path, match_lines, context}
    """
    # 1. Extract keywords from query
    # 2. Use grep with context (-C flag) to find matches
    # 3. Score by frequency + position
    # 4. Return top_k documents with snippets
```

### Phase 2: ReAct Reasoning Loop
```python
def react_retrieval(query: str, max_iterations: int = 3):
    """
    LLM-guided iterative search with reasoning.

    Loop:
        Observation: Current search results
        Thought: LLM analyzes relevance, identifies gaps
        Action: Refine query OR request vector search OR conclude
    """
    # Use Claude API with structured prompt
    # Track: queries issued, documents explored, reasoning chain
```

### Phase 3: Filtered Vector Search
```python
def filtered_vector_search(query: str, doc_filter: List[str]):
    """
    Vector similarity search restricted to filtered docs.

    Args:
        query: User query
        doc_filter: List of document IDs from BM25 results

    Returns: Top-k semantically similar chunks from filtered set
    """
    # Use existing SimpleVectorStore with metadata filter
```

### Phase 4: Hybrid Orchestrator
```python
def hybrid_rag_search(query: str):
    """
    Main entry point for hybrid search.

    1. BM25 search -> candidate documents
    2. ReAct loop -> LLM reasons about candidates
    3. Vector search -> semantic ranking within candidates
    4. Merge & rank -> final results
    """
```

## Example Execution Flow

### User Query: "How do I build confidence for public speaking using NLP anchoring?"

#### Step 1: BM25 Search (grep)
```
Query keywords: ["confidence", "public speaking", "NLP", "anchoring"]

Results:
- confidence_public_speaking.md (15 matches)
- nlp_anchoring_techniques.md (8 matches)
- performance_anxiety.md (3 matches)
```

#### Step 2: ReAct Reasoning
```
Observation 1: Found 3 documents with keyword matches.
- Document 1: "Confidence in Public Speaking" has high keyword density
- Document 2: "NLP Anchoring Techniques" mentions anchoring 8 times
- Document 3: "Performance Anxiety" peripherally related

Thought 1: Documents 1 and 2 seem most relevant. Document 1 likely has
the script structure, Document 2 has the specific NLP techniques. I should
explore both with vector search to find the exact sections on anchoring.

Action 1: VECTOR_SEARCH
  Query: "NLP anchoring confidence public speaking"
  Filter: [doc1, doc2]
```

#### Step 3: Filtered Vector Search
```
Vector search on documents 1 & 2 only (27 chunks -> 8 chunks)

Top results:
1. confidence_public_speaking.md, chunk 5 (similarity: 0.82)
   "Use kinesthetic anchoring... touch thumb to finger... confidence trigger"

2. nlp_anchoring_techniques.md, chunk 2 (similarity: 0.79)
   "Resource anchoring protocol: 1. Elicit peak state..."
```

#### Step 4: Final Reasoning
```
Thought 2: Perfect! I found the anchoring protocol in the NLP techniques
document and its application in the confidence script. These two chunks
together provide complete guidance.

Action 2: CONCLUDE
  Final results: [chunk 5 from doc1, chunk 2 from doc2]
  Reasoning: Combines theoretical NLP framework with practical application
```

## Advantages Over Pure Vector RAG

1. **Explainability**: ReAct chain shows WHY documents were retrieved
2. **Precision**: BM25 ensures exact keyword matches aren't missed
3. **Efficiency**: Vector search only on relevant subset (8 chunks vs 27)
4. **Adaptability**: LLM can request more context or different queries
5. **Debugging**: Can inspect reasoning chain when retrieval fails

## File Structure

```
your_workspace/data/scripts/
├── hybrid_rag.py              # Main orchestrator
├── bm25_search.py             # Grep-based keyword search
├── react_retriever.py         # ReAct reasoning loop
├── simple_vector_store.py     # Existing vector search (reused)
└── hybrid_query.py            # CLI interface
```

## Next Steps

1. Implement bm25_search.py (grep-based keyword search)
2. Implement react_retriever.py (LLM reasoning loop with Claude API)
3. Modify simple_vector_store.py to support document filtering
4. Create hybrid_rag.py orchestrator
5. Test with example queries
6. Integrate with Step 3 (Script Generation)

## Performance Expectations

- **BM25 search**: < 100ms (grep is very fast)
- **ReAct reasoning**: 1-3 seconds per iteration (LLM API calls)
- **Vector search (filtered)**: 10-50ms (small subset)
- **Total latency**: 2-5 seconds (depending on ReAct iterations)

## Configuration

```yaml
hybrid_rag_config:
  bm25:
    top_k: 20
    context_lines: 3  # grep -C 3
    min_score: 0.1

  react:
    max_iterations: 3
    model: "claude-sonnet-4"
    temperature: 0.3

  vector:
    similarity_threshold: 0.4
    top_k: 5
```

---

**Status**: Design complete, ready for implementation
**Estimated effort**: 3-4 hours
**Priority**: High (enables intelligent retrieval for workflow)
