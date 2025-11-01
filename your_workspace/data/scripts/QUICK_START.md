# Quick Start - Simple Python RAG

Get your RAG knowledge base up and running in 3 steps!

---

## Step 1: Install Dependencies

```bash
cd your_workspace/data/scripts
pip install -r simple_requirements.txt
```

This will install:
- `sentence-transformers` - For text embeddings
- `numpy` - For vector math
- `pyyaml` - For parsing document metadata
- `tqdm` - For progress bars

**Note**: First time will take 2-3 minutes as it downloads the embedding model (~80MB).

---

## Step 2: Ingest Documents

```bash
python simple_ingest.py
```

This will:
1. Find all `.md` files in `../rag_corpus/`
2. Parse metadata from YAML frontmatter
3. Chunk content into ~800 character pieces
4. Generate embeddings for each chunk
5. Save to `../vector_db/simple_vector_store.pkl`

**Expected output**:
```
Loading embedding model: all-MiniLM-L6-v2...
✓ Model loaded (embedding dimension: 384)

Starting Document Ingestion
============================================================

📚 Processing 2 files from hypnosis_scripts/
  • confidence_public_speaking.md...
    → 12 chunks
  • deep_relaxation_stress_management.md...
    → 10 chunks
  ✓ Added 22 chunks from 2 files

============================================================
✓ Ingestion complete!
  Total chunks: 22
  Total documents in store: 22
============================================================

Saving vector store to: .../vector_db/simple_vector_store.pkl
✓ Saved 22 documents

Vector Store Statistics
============================================================
  Model: all-MiniLM-L6-v2
  Embedding dimension: 384
  Total documents: 22

  By category:
    • hypnosis_scripts: 22 chunks

✓ Done! Next step: python simple_query.py "your query"
```

---

## Step 3: Query and Test

```bash
# Interactive mode
python simple_query.py

# Single query
python simple_query.py "confidence public speaking"

# Test queries
python simple_query.py --test

# Show statistics
python simple_query.py --stats
```

**Example query**:
```bash
python simple_query.py "relaxation breathing techniques"
```

**Expected output**:
```
Loading vector store...
✓ Loaded 22 documents

================================================================================
Query: "relaxation breathing techniques"
Found: 5 results
================================================================================

📄 Result 1 (similarity: 0.876)
--------------------------------------------------------------------------------
  Title: Deep Relaxation and Stress Management
  Category: wellness
  Source: hypnosis_scripts/deep_relaxation_stress_management.md

  Excerpt:
  Begin with a slow, deep breath... filling your lungs completely... and
  releasing it slowly through your mouth... And again... breathing in calm...
  breathing out stress...

📄 Result 2 (similarity: 0.823)
...
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'sentence_transformers'"
- Run: `pip install -r simple_requirements.txt`

### "FileNotFoundError: Vector store not found"
- Run: `python simple_ingest.py` first

### "No markdown files found"
- Check that you have `.md` files in `your_workspace/data/rag_corpus/`
- Documents should have YAML metadata frontmatter

### Ingestion is slow
- First run downloads the embedding model (~80MB) - this is one-time
- After that, ~50 documents should take 30-60 seconds

---

## What's Next?

Once your RAG is working:

1. ✅ Add more documents to `rag_corpus/` directories
2. ✅ Re-run `python simple_ingest.py` to add them
3. ✅ Test retrieval with different queries
4. ✅ Integrate with Step 3 (Script Generation) in your workflow

---

## File Locations

```
your_workspace/data/
├── rag_corpus/                    ← Put your .md files here
│   ├── hypnosis_scripts/
│   ├── techniques/
│   ├── language_patterns/
│   ├── archetypes/
│   ├── neuroscience/
│   └── best_practices/
│
├── vector_db/                     ← RAG database stored here
│   └── simple_vector_store.pkl    (created by ingest)
│
└── scripts/                       ← Scripts to run
    ├── simple_ingest.py           (Step 2)
    ├── simple_query.py            (Step 3)
    └── simple_vector_store.py     (Core library)
```

---

**Status**: Ready to use!
**Time to set up**: ~5 minutes
**Works on**: Windows, Mac, Linux (no C++ compiler needed!)
