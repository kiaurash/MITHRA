# RAG Knowledge Base Scripts

Scripts for setting up and managing the ChromaDB vector database for the BehaviorShift workflow.

---

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Usage

### Step 1: Set Up Vector Database

Initialize ChromaDB and create collections:

```bash
python setup_vector_db.py
```

This creates the vector database at `../vector_db/` with 6 collections:
- `hypnosis_scripts` - Complete session scripts
- `techniques` - Induction, deepening, awakening techniques
- `language_patterns` - Ericksonian, NLP, permissive language
- `archetypes` - Jungian archetypal profiles
- `neuroscience` - Scientific foundations
- `best_practices` - Safety protocols and guidelines

**Reset database** (if needed):
```bash
python setup_vector_db.py --reset
```

---

### Step 2: Ingest Documents

Load markdown documents from `../rag_corpus/` into the vector database:

```bash
python ingest_documents.py
```

This will:
1. Find all `.md` files in each corpus directory
2. Parse metadata from YAML frontmatter
3. Chunk content into ~1000 character pieces
4. Generate embeddings using `sentence-transformers`
5. Store in appropriate ChromaDB collection

**Ingest specific collection only**:
```bash
python ingest_documents.py hypnosis_scripts
```

---

### Step 3: Query and Test

Query the knowledge base to test retrieval:

```bash
# Interactive mode (default)
python query_rag.py

# Single query
python query_rag.py "confidence public speaking"

# Run test queries
python query_rag.py --test

# Show collection statistics
python query_rag.py --stats
```

**Example Query**:
```bash
python query_rag.py "induction techniques for anxiety"
```

**Output**:
```
================================================================================
Query: "induction techniques for anxiety"
================================================================================

📚 Collection: hypnosis_scripts
--------------------------------------------------------------------------------

  Result 1 (similarity: 0.892)
  Source: hypnosis_scripts/deep_relaxation_stress_management.md
  Title: Deep Relaxation and Stress Management
  Category: wellness
  Excerpt: Begin with a slow, deep breath... filling your lungs completely...

📚 Collection: techniques
--------------------------------------------------------------------------------

  Result 1 (similarity: 0.876)
  Source: techniques/induction_progressive_relaxation.md
  Technique: Progressive Muscle Relaxation
  Category: induction
  Excerpt: Progressive Muscle Relaxation (PMR) is one of the most effective...
```

---

## File Structure

```
scripts/
├── README.md                  (this file)
├── requirements.txt           (Python dependencies)
├── setup_vector_db.py         (Initialize ChromaDB)
├── ingest_documents.py        (Load documents into DB)
└── query_rag.py               (Query and test retrieval)

../rag_corpus/                 (Source documents)
├── hypnosis_scripts/
├── techniques/
├── language_patterns/
├── archetypes/
├── neuroscience/
└── best_practices/

../vector_db/                  (ChromaDB storage)
└── chroma.sqlite3
```

---

## Workflow Integration

These scripts prepare the RAG knowledge base. To integrate with Step 3 (Script Generation):

1. **Query RAG during script generation**:
   ```python
   from query_rag import query_all_collections
   import chromadb

   client = chromadb.PersistentClient(path="path/to/vector_db")

   # Generate queries based on user input
   queries = [
       f"{user_skill} hypnosis script",
       f"{user_skill} techniques",
       "induction deepening awakening methods"
   ]

   # Retrieve relevant content
   rag_context = []
   for query in queries:
       results = query_all_collections(client, query, n_results_per_collection=3)
       rag_context.extend(extract_documents(results))
   ```

2. **Pass RAG context to script generation**:
   ```python
   script = generate_script(
       user_context=user_input,
       research=step2_output,
       rag_context=rag_context,  # <-- From vector DB
       blueprint=seven_phase_structure
   )
   ```

---

## Maintenance

### Adding New Documents

1. Create markdown file in appropriate `rag_corpus/` subdirectory
2. Include YAML metadata frontmatter:
   ```yaml
   ```yaml
   title: "Your Document Title"
   category: "category_name"
   target_skill: ["skill1", "skill2"]
   ```
   ```
3. Run ingestion:
   ```bash
   python ingest_documents.py
   ```

### Updating Existing Documents

1. Modify the markdown file
2. Re-run ingestion (it will update existing chunks):
   ```bash
   python ingest_documents.py
   ```

### Checking What's in the Database

```bash
python query_rag.py --stats
```

---

## Troubleshooting

**"Collection not found" error**:
- Run `python setup_vector_db.py` first

**No results returned**:
- Check that documents were ingested: `python query_rag.py --stats`
- Try broader queries
- Check similarity threshold (default: returns top-k regardless of threshold)

**Import errors**:
- Install dependencies: `pip install -r requirements.txt`
- Make sure you're in correct directory

**ChromaDB version issues**:
- ChromaDB API changes between versions
- This code tested with chromadb==0.4.24

---

## Next Steps

After setting up RAG:

1. ✅ Curate more documents (target: 40-60)
2. ✅ Test retrieval quality with diverse queries
3. ✅ Integrate with Step 3 script generation prompt
4. ✅ Compare script quality with/without RAG
5. ✅ Optimize retrieval parameters based on results

---

**Created**: 2025-10-27
**For**: BehaviorShift Hypnosis Script Generator
**Status**: Ready for use
