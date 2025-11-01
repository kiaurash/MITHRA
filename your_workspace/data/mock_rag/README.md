# Mock RAG Infrastructure for Sprint 1 Testing

## Overview

This directory contains a **mock RAG (Retrieval-Augmented Generation)** system for testing the Sprint 1 content generation pipeline without needing to set up a full vector database.

**Purpose**: Enable rapid experimentation and validation of the knowledge synthesis workflow by simulating RAG functionality using structured metadata and keyword matching.

## What's Inside

```
mock_rag/
├── README.md                          # This file
├── metadata_index.json                # Source metadata and indexing
├── query_mock_rag.py                  # Python script to query sources
└── sources/                           # Source documents
    ├── oneness_philosophical_foundations.md
    ├── oneness_separation_journey.md
    ├── oneness_relationship_ecology.md
    ├── oneness_crisis_breakthroughs.md
    ├── oneness_daily_practices.md
    └── oneness_leadership.md
```

## Source Documents

All sources are extracted from **"The Oneness Paradox"** research article, covering:

1. **Philosophical Foundations** - What is oneness, scientific evidence, neuroscience of connection
2. **Separation Journey** - How we forget oneness, ego development, socialization
3. **Relationship Ecology** - Systems thinking, interdependence, circle dynamics
4. **Crisis & Breakthroughs** - Barriers to connection, how crisis creates breakthrough
5. **Daily Practices** - Practical exercises for dwelling in oneness
6. **Leadership** - Leading from connection, distributed leadership, ubuntu

**Topics covered**: Relationships, emotional intimacy, connection, personal growth, leadership, mindfulness, community building, trauma healing, vulnerability

## How It Works

### Real RAG vs. Mock RAG

**Real RAG System:**
- Uses semantic embeddings (e.g., OpenAI embeddings, sentence transformers)
- Stores vectors in vector database (ChromaDB, Pinecone, Weaviate)
- Performs similarity search using cosine similarity
- Returns semantically similar content even if keywords don't match

**This Mock RAG:**
- Uses structured metadata with topics, key concepts, and query patterns
- Performs keyword/concept matching with weighted scoring
- Returns relevant sources based on metadata alignment
- **Good enough for MVP testing** without infrastructure overhead

### Querying the Mock RAG

#### Using Python

```python
from query_mock_rag import MockRAG

# Initialize
rag = MockRAG()

# Query for relevant sources
results = rag.query("improving emotional intimacy", top_k=3)

for result in results:
    print(f"Title: {result['source']['title']}")
    print(f"Relevance: {result['relevance_score']}")

# Retrieve full content
results_with_content = rag.query_and_retrieve("building connection", top_k=2)
```

#### From Command Line

```bash
cd your_workspace/data/mock_rag
python query_mock_rag.py
```

This runs demo queries and shows how the system matches topics.

### Scoring Algorithm

The mock RAG scores sources based on matches in:

- **Title** (10 points) - Highest weight for title matches
- **Topics** (5 points each) - Core topic matches
- **Use for queries** (4 points) - Specific query pattern matches
- **Key concepts** (3 points each) - Concept-level matches
- **Query word overlap** (2 points) - Individual word matches in patterns
- **Relevance tags** (1 point each) - General relevance indicators

Higher scores = more relevant sources.

## Integration with Sprint 1 Pipeline

### Step 1: Knowledge Synthesis

In your Step 1 prompt (`step1_knowledge_synthesis_prompt.txt`), you can now reference this mock RAG:

**Example workflow:**
1. User provides topic: "improving emotional intimacy in long-term relationships"
2. Query mock RAG: `rag.query(user_topic, top_k=3)`
3. Retrieve top 3 most relevant sources
4. Combine with Deep Research (web search results)
5. Synthesize into research article with citations

**Benefits:**
- No need for vector DB setup during Sprint 1
- Fast iteration on prompt engineering
- Real sources with rich, well-researched content
- Easy to add more sources by creating new .md files and updating metadata

## Example Queries and Expected Results

### Query: "improving emotional intimacy"
**Expected top results:**
- The Ecology of Connection (relationship focus)
- Daily Practices (vulnerability, connection exercises)

### Query: "what is oneness"
**Expected top results:**
- Philosophical Foundations (definition, evidence)
- Crisis & Breakthroughs (barriers to awareness)

### Query: "leadership from connection"
**Expected top results:**
- Leadership (distributed leadership, ubuntu)
- Relationship Ecology (systems thinking)

### Query: "overcoming loneliness"
**Expected top results:**
- Crisis & Breakthroughs (barriers, isolation)
- Philosophical Foundations (loneliness as physical condition)

## Adding More Sources

To expand the mock RAG with additional sources:

### 1. Create new markdown file

```bash
touch sources/new_topic.md
```

### 2. Structure your content

```markdown
# Title of Source

**Source**: Author/Publication, Year
**Topics**: topic1, topic2, topic3
**Relevance**: use_case1, use_case2

## Section 1
Content here...

## Section 2
More content...
```

### 3. Add to metadata_index.json

```json
{
  "id": "new_topic",
  "file": "new_topic.md",
  "title": "Title of Source",
  "topics": ["topic1", "topic2"],
  "relevance_tags": ["use_case1"],
  "key_concepts": ["concept1", "concept2"],
  "use_for_queries_about": ["query pattern 1"]
}
```

### 4. Test the new source

```python
rag = MockRAG()
results = rag.query("topic related to new source")
```

## Limitations

This mock RAG has some limitations compared to a real RAG system:

1. **No semantic understanding** - Matches keywords, not meaning
   - Query "building trust" won't match "fostering confidence" (a real RAG would)

2. **No contextual relevance** - Scoring is rule-based, not learned
   - Real RAG learns what's relevant through embeddings

3. **No chunk-level retrieval** - Returns whole documents
   - Real RAG retrieves specific passages most relevant to query

4. **Manual metadata** - Requires hand-crafting topics and concepts
   - Real RAG generates embeddings automatically

5. **Limited scale** - Works for dozens of sources, not thousands
   - Real RAG scales to millions of documents

**But for Sprint 1 MVP**: These limitations don't matter. You need to test the pipeline logic, not optimize vector search.

## Migration Path to Real RAG

When ready to move from mock to real RAG:

### Option 1: ChromaDB (Local)
```python
import chromadb

# Create client
client = chromadb.Client()

# Create collection
collection = client.create_collection("relationship_content")

# Add documents
collection.add(
    documents=["content here"],
    metadatas=[{"source": "file.md"}],
    ids=["doc1"]
)

# Query
results = collection.query(
    query_texts=["emotional intimacy"],
    n_results=3
)
```

### Option 2: Cloud Vector DB
- Pinecone (managed, easy)
- Weaviate (open source)
- Qdrant (high performance)

### Option 3: LangChain Integration
```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(documents, embeddings)
retriever = vectorstore.as_retriever()
```

## Testing Checklist

- [x] Mock RAG returns results for various query types
- [x] Relevance scores make sense (higher = more relevant)
- [x] Can retrieve full source content
- [x] Metadata index is valid JSON
- [x] All source files exist and are readable
- [ ] Integrate with Step 1 Knowledge Synthesis prompt
- [ ] Test end-to-end with user input → RAG → synthesis
- [ ] Validate citations reference correct sources

## Next Steps for Sprint 1

1. **Test with Step 1 prompt**: Feed RAG results into knowledge synthesis
2. **Create Gate 1 prompt**: Groundedness judge to validate research
3. **Build simple orchestration**: Python script tying Step 0 → 1 → Gate 1 → 2
4. **Run test scenarios**: The 3 scenarios from experiment design
5. **Iterate based on output quality**: Refine prompts, add sources as needed

## Questions or Issues?

- **Query not returning expected sources?** Check metadata_index.json and add relevant topics/concepts
- **Need more sources?** Add markdown files and update metadata
- **Want semantic search?** See "Migration Path to Real RAG" section above

---

**Created**: 2025-10-27
**Sprint**: Sprint 1 - Content Generation Pipeline
**Status**: Ready for testing
**Owner**: Kia (BehaviorShift project)
