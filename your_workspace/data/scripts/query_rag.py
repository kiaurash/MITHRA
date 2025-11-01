"""
Query the RAG Knowledge Base

This script allows you to query the ChromaDB vector database
and see what relevant content is retrieved.
"""

import chromadb
from pathlib import Path
import sys
from typing import List, Dict

# Get project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
VECTOR_DB_PATH = PROJECT_ROOT / "your_workspace" / "data" / "vector_db"

def query_collection(
    client: chromadb.Client,
    collection_name: str,
    query: str,
    n_results: int = 5
) -> Dict:
    """Query a specific collection"""

    try:
        collection = client.get_collection(name=collection_name)
    except:
        print(f"Collection '{collection_name}' not found")
        return None

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    return results

def query_all_collections(
    client: chromadb.Client,
    query: str,
    n_results_per_collection: int = 3
) -> Dict[str, Dict]:
    """Query all collections and return aggregated results"""

    collections = client.list_collections()

    all_results = {}

    for collection in collections:
        results = query_collection(
            client,
            collection.name,
            query,
            n_results_per_collection
        )

        if results and results['documents'][0]:  # Has results
            all_results[collection.name] = results

    return all_results

def print_results(results: Dict, query: str):
    """Pretty print query results"""

    print("\n" + "=" * 80)
    print(f"Query: \"{query}\"")
    print("=" * 80)

    if not results:
        print("No results found")
        return

    for collection_name, collection_results in results.items():
        print(f"\n📚 Collection: {collection_name}")
        print("-" * 80)

        documents = collection_results['documents'][0]
        metadatas = collection_results['metadatas'][0]
        distances = collection_results['distances'][0]

        for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
            similarity = 1 - distance  # Convert distance to similarity
            print(f"\n  Result {i+1} (similarity: {similarity:.3f})")
            print(f"  Source: {metadata.get('source_file', 'unknown')}")

            # Print relevant metadata
            if 'title' in metadata:
                print(f"  Title: {metadata['title']}")
            if 'category' in metadata:
                print(f"  Category: {metadata['category']}")
            if 'technique' in metadata:
                print(f"  Technique: {metadata['technique']}")
            if 'archetype' in metadata:
                print(f"  Archetype: {metadata['archetype']}")

            # Print document excerpt (first 200 chars)
            excerpt = doc[:200].replace('\n', ' ')
            print(f"  Excerpt: {excerpt}...")
            print()

    print("=" * 80 + "\n")

def interactive_mode(client: chromadb.Client):
    """Interactive query mode"""

    print("\n" + "=" * 80)
    print("RAG Knowledge Base - Interactive Query Mode")
    print("=" * 80)
    print("Enter your queries (or 'quit' to exit)")
    print()

    while True:
        try:
            query = input("Query: ").strip()

            if not query:
                continue

            if query.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            # Query all collections
            results = query_all_collections(client, query, n_results_per_collection=3)

            # Print results
            print_results(results, query)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def test_queries(client: chromadb.Client):
    """Run some test queries to validate the RAG system"""

    print("\n" + "=" * 80)
    print("Running Test Queries")
    print("=" * 80 + "\n")

    test_queries_list = [
        "confidence public speaking presentation",
        "relaxation stress management",
        "induction techniques hypnosis",
        "embedded commands Ericksonian",
        "Leader archetype confidence",
        "safety awakening sequence"
    ]

    for query in test_queries_list:
        results = query_all_collections(client, query, n_results_per_collection=2)
        print_results(results, query)
        input("Press Enter to continue...")

def get_collection_stats(client: chromadb.Client):
    """Display statistics about all collections"""

    print("\n" + "=" * 80)
    print("Collection Statistics")
    print("=" * 80 + "\n")

    collections = client.list_collections()

    for collection in collections:
        count = collection.count()
        print(f"📚 {collection.name}:")
        print(f"   Documents: {count}")

        if count > 0:
            # Get a sample to show metadata keys
            sample = collection.get(limit=1)
            if sample['metadatas']:
                metadata_keys = sample['metadatas'][0].keys()
                print(f"   Metadata keys: {', '.join(metadata_keys)}")

        print()

if __name__ == "__main__":
    # Initialize ChromaDB client
    try:
        client = chromadb.PersistentClient(path=str(VECTOR_DB_PATH))
        print(f"✓ Connected to ChromaDB at: {VECTOR_DB_PATH}")
    except Exception as e:
        print(f"Error connecting to ChromaDB: {e}")
        print(f"Have you run 'python setup_vector_db.py' yet?")
        sys.exit(1)

    # Parse command line arguments
    if len(sys.argv) < 2:
        # No arguments - show stats and enter interactive mode
        get_collection_stats(client)
        interactive_mode(client)

    elif sys.argv[1] == "--test":
        # Run test queries
        test_queries(client)

    elif sys.argv[1] == "--stats":
        # Show statistics
        get_collection_stats(client)

    else:
        # Query provided as argument
        query = " ".join(sys.argv[1:])
        results = query_all_collections(client, query, n_results_per_collection=5)
        print_results(results, query)
