"""
Ingest Documents into ChromaDB Vector Database

This script reads markdown documents from the rag_corpus directory,
extracts metadata, chunks the content, and stores it in ChromaDB with embeddings.
"""

import chromadb
from pathlib import Path
import yaml
import re
from typing import Dict, List, Tuple
import hashlib

# Get project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
VECTOR_DB_PATH = PROJECT_ROOT / "your_workspace" / "data" / "vector_db"
CORPUS_PATH = PROJECT_ROOT / "your_workspace" / "data" / "rag_corpus"

def parse_markdown_document(file_path: Path) -> Tuple[Dict, str]:
    """Parse markdown file and extract metadata and content"""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract YAML metadata block
    metadata = {}
    yaml_match = re.search(r'```yaml\n(.*?)\n```', content, re.DOTALL)
    if yaml_match:
        try:
            metadata = yaml.safe_load(yaml_match.group(1))
        except yaml.YAMLError as e:
            print(f"  Warning: Could not parse YAML metadata in {file_path.name}: {e}")

    # Remove metadata block from content
    content_without_metadata = re.sub(r'```yaml\n.*?\n```', '', content, flags=re.DOTALL)

    # Add file path to metadata
    metadata['source_file'] = str(file_path.relative_to(CORPUS_PATH))
    metadata['filename'] = file_path.name

    return metadata, content_without_metadata.strip()

def chunk_content(content: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Chunk content into smaller pieces for embedding

    For now, we'll use simple paragraph-based chunking.
    More sophisticated semantic chunking can be added later.
    """

    # Split by double newlines (paragraphs)
    sections = re.split(r'\n\n+', content)

    chunks = []
    current_chunk = ""

    for section in sections:
        # Skip empty sections
        if not section.strip():
            continue

        # If adding this section would exceed chunk size, save current chunk
        if len(current_chunk) + len(section) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            # Start new chunk with overlap (last part of previous chunk)
            current_chunk = current_chunk[-overlap:] + "\n\n" + section
        else:
            current_chunk += "\n\n" + section if current_chunk else section

    # Add final chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def ingest_collection(client: chromadb.Client, collection_name: str, directory: Path):
    """Ingest all documents from a directory into a collection"""

    # Get or create collection
    try:
        collection = client.get_collection(name=collection_name)
    except:
        collection = client.create_collection(name=collection_name)

    # Find all markdown files in directory
    md_files = list(directory.glob("*.md"))

    if not md_files:
        print(f"  No markdown files found in {directory.name}")
        return

    print(f"\n=== Ingesting {len(md_files)} documents into '{collection_name}' ===")

    total_chunks = 0

    for file_path in md_files:
        print(f"  Processing: {file_path.name}...")

        # Parse document
        metadata, content = parse_markdown_document(file_path)

        # Chunk content
        chunks = chunk_content(content)

        print(f"    - Created {len(chunks)} chunks")

        # Generate IDs for chunks
        doc_id_base = file_path.stem
        ids = [f"{doc_id_base}_chunk_{i}" for i in range(len(chunks))]

        # Create metadata for each chunk
        metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata['chunk_index'] = i
            chunk_metadata['total_chunks'] = len(chunks)
            chunk_metadata['chunk_id'] = ids[i]

            # Convert lists to strings for ChromaDB compatibility
            for key, value in chunk_metadata.items():
                if isinstance(value, list):
                    chunk_metadata[key] = ", ".join(str(v) for v in value)
                elif value is None:
                    chunk_metadata[key] = ""
                else:
                    chunk_metadata[key] = str(value)

            metadatas.append(chunk_metadata)

        # Add to collection
        try:
            collection.add(
                ids=ids,
                documents=chunks,
                metadatas=metadatas
            )
            print(f"    ✓ Added {len(chunks)} chunks")
            total_chunks += len(chunks)
        except Exception as e:
            print(f"    ✗ Error adding chunks: {e}")

    print(f"  Total chunks ingested: {total_chunks}")
    print(f"  Collection now has: {collection.count()} total chunks\n")

def ingest_all_documents(client: chromadb.Client):
    """Ingest all documents from all corpus directories"""

    # Map directories to collection names
    directory_mapping = {
        "hypnosis_scripts": "hypnosis_scripts",
        "techniques": "techniques",
        "language_patterns": "language_patterns",
        "archetypes": "archetypes",
        "neuroscience": "neuroscience",
        "best_practices": "best_practices"
    }

    print("Starting document ingestion...")
    print(f"Corpus path: {CORPUS_PATH}")

    total_docs = 0
    for dir_name, collection_name in directory_mapping.items():
        directory = CORPUS_PATH / dir_name

        if not directory.exists():
            print(f"  Warning: Directory not found: {dir_name}")
            continue

        ingest_collection(client, collection_name, directory)
        total_docs += len(list(directory.glob("*.md")))

    print("=" * 60)
    print(f"✓ Ingestion complete! Processed {total_docs} documents")
    print("=" * 60)

    # Show final collection stats
    print("\n=== Final Collection Statistics ===")
    collections = client.list_collections()
    for collection in collections:
        print(f"  {collection.name}: {collection.count()} chunks")
    print()

if __name__ == "__main__":
    import sys

    print("ChromaDB Document Ingestion")
    print("=" * 60)

    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path=str(VECTOR_DB_PATH))
    print(f"✓ Connected to ChromaDB at: {VECTOR_DB_PATH}\n")

    # Check for specific collection flag
    if len(sys.argv) > 1:
        collection_name = sys.argv[1]
        directory = CORPUS_PATH / collection_name
        if directory.exists():
            ingest_collection(client, collection_name, directory)
        else:
            print(f"Error: Directory not found: {directory}")
    else:
        # Ingest all documents
        ingest_all_documents(client)

    print("\nNext step: Run 'python query_rag.py \"your query\"' to test retrieval")
