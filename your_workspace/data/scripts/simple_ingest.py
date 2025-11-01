"""
Ingest Documents into Simple Python Vector Store

Reads markdown documents from rag_corpus/ and adds them to the vector store.
"""

from pathlib import Path
import yaml
import re
from typing import Dict, Tuple, List
from simple_vector_store import SimpleVectorStore

# Get project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
CORPUS_PATH = PROJECT_ROOT / "your_workspace" / "data" / "rag_corpus"
VECTOR_STORE_PATH = PROJECT_ROOT / "your_workspace" / "data" / "vector_db" / "simple_vector_store.pkl"

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
    metadata['collection'] = file_path.parent.name

    # Convert lists to strings for easier filtering
    for key, value in metadata.items():
        if isinstance(value, list):
            metadata[key] = ", ".join(str(v) for v in value)

    return metadata, content_without_metadata.strip()

def chunk_content(content: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """
    Chunk content into smaller pieces for embedding.

    Args:
        content: Full document text
        chunk_size: Target size in characters
        overlap: Overlap between chunks

    Returns:
        List of text chunks
    """
    # Split by headers and double newlines
    sections = re.split(r'\n(?:##|###|####)', content)

    chunks = []
    current_chunk = ""

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # If section is small enough, add it whole
        if len(section) <= chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            chunks.append(section)
            continue

        # If adding this section would exceed chunk size, save current chunk
        if len(current_chunk) + len(section) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            # Start new chunk with overlap
            current_chunk = current_chunk[-overlap:] if len(current_chunk) > overlap else ""

        current_chunk += "\n\n" + section if current_chunk else section

    # Add final chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    return [chunk for chunk in chunks if len(chunk) > 50]  # Filter tiny chunks

def ingest_directory(store: SimpleVectorStore, directory: Path, category: str):
    """Ingest all markdown files from a directory"""

    # Find all markdown files
    md_files = list(directory.glob("*.md"))

    if not md_files:
        print(f"  No markdown files found in {directory.name}")
        return 0

    print(f"\nProcessing {len(md_files)} files from {category}/")

    documents = []
    total_chunks = 0

    for file_path in md_files:
        print(f"  - {file_path.name}...")

        # Parse document
        metadata, content = parse_markdown_document(file_path)

        # Chunk content
        chunks = chunk_content(content)

        print(f"    -> {len(chunks)} chunks")

        # Create document entries for each chunk
        doc_id_base = file_path.stem
        for i, chunk in enumerate(chunks):
            doc_id = f"{category}_{doc_id_base}_chunk_{i}"

            chunk_metadata = metadata.copy()
            chunk_metadata['chunk_index'] = str(i)
            chunk_metadata['total_chunks'] = str(len(chunks))

            documents.append({
                'doc_id': doc_id,
                'text': chunk,
                'metadata': chunk_metadata
            })

        total_chunks += len(chunks)

    # Batch add all documents from this directory
    if documents:
        store.add_documents(documents)

    print(f"  [OK] Added {total_chunks} chunks from {len(md_files)} files")
    return total_chunks

def ingest_all(store: SimpleVectorStore):
    """Ingest all documents from all corpus directories"""

    categories = [
        "hypnosis_scripts",
        "techniques",
        "language_patterns",
        "archetypes",
        "neuroscience",
        "best_practices"
    ]

    print("=" * 60)
    print("Starting Document Ingestion")
    print("=" * 60)
    print(f"Corpus path: {CORPUS_PATH}")
    print()

    total_chunks = 0

    for category in categories:
        directory = CORPUS_PATH / category

        if not directory.exists():
            print(f"  [WARNING] Directory not found: {category}")
            continue

        chunks = ingest_directory(store, directory, category)
        total_chunks += chunks

    print("\n" + "=" * 60)
    print(f"[OK] Ingestion complete!")
    print(f"  Total chunks: {total_chunks}")
    print(f"  Total documents in store: {len(store)}")
    print("=" * 60)

    return total_chunks

def main():
    """Main ingestion function"""

    print("\nSimple Python RAG - Document Ingestion")
    print("=" * 60)

    # Check if corpus exists
    if not CORPUS_PATH.exists():
        print(f"Error: Corpus directory not found: {CORPUS_PATH}")
        print("Please ensure documents are in your_workspace/data/rag_corpus/")
        return

    # Create or load vector store
    if VECTOR_STORE_PATH.exists():
        print(f"\n[WARNING] Vector store already exists at: {VECTOR_STORE_PATH}")
        response = input("Overwrite? (yes/no): ")
        if response.lower() != 'yes':
            print("Ingestion cancelled")
            return

    print("\nInitializing vector store...")
    store = SimpleVectorStore()

    # Ingest all documents
    total_chunks = ingest_all(store)

    if total_chunks == 0:
        print("\n[WARNING] No documents were ingested. Check that your rag_corpus/ has .md files.")
        return

    # Save vector store
    print(f"\nSaving vector store to: {VECTOR_STORE_PATH}")
    store.save(VECTOR_STORE_PATH)

    # Show statistics
    print("\n" + "=" * 60)
    print("Vector Store Statistics")
    print("=" * 60)
    stats = store.get_stats()
    print(f"  Model: {stats['model_name']}")
    print(f"  Embedding dimension: {stats['embedding_dimension']}")
    print(f"  Total documents: {stats['total_documents']}")
    print(f"\n  By category:")
    for category, count in stats['categories'].items():
        print(f"    - {category}: {count} chunks")

    print("\n[OK] Done! Next step: python simple_query.py \"your query\"")

if __name__ == "__main__":
    main()
