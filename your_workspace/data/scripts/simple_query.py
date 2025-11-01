"""
Query the Simple Python RAG Knowledge Base

Test retrieval and search the vector store.
"""

from pathlib import Path
import sys
from simple_vector_store import load_store

# Get project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
VECTOR_STORE_PATH = PROJECT_ROOT / "your_workspace" / "data" / "vector_db" / "simple_vector_store.pkl"

def print_results(results, query):
    """Pretty print query results"""

    print("\n" + "=" * 80)
    print(f"Query: \"{query}\"")
    print(f"Found: {len(results)} results")
    print("=" * 80)

    if not results:
        print("No results found")
        return

    for i, result in enumerate(results, 1):
        similarity = result['similarity']
        metadata = result['metadata']
        text = result['text']

        print(f"\nResult {i} (similarity: {similarity:.3f})")
        print("-" * 80)

        # Print relevant metadata
        if 'title' in metadata:
            print(f"  Title: {metadata['title']}")
        if 'category' in metadata:
            print(f"  Category: {metadata['category']}")
        if 'technique' in metadata:
            print(f"  Technique: {metadata['technique']}")
        if 'archetype' in metadata:
            print(f"  Archetype: {metadata['archetype']}")
        if 'source_file' in metadata:
            print(f"  Source: {metadata['source_file']}")

        # Print text excerpt
        excerpt = text[:300].replace('\n', ' ')
        print(f"\n  Excerpt:")
        print(f"  {excerpt}...")

    print("\n" + "=" * 80 + "\n")

def test_queries(store):
    """Run test queries to validate retrieval"""

    print("\n" + "=" * 80)
    print("Running Test Queries")
    print("=" * 80)

    test_queries_list = [
        "confidence public speaking presentation",
        "relaxation stress management deep breathing",
        "induction techniques hypnosis",
        "embedded commands Ericksonian language",
        "Leader archetype confidence authority",
        "safety awakening sequence grounding"
    ]

    for query in test_queries_list:
        results = store.query(query, top_k=3)
        print_results(results, query)

        if query != test_queries_list[-1]:  # Don't pause on last query
            input("Press Enter to continue...")

def get_stats(store):
    """Display statistics about the vector store"""

    print("\n" + "=" * 80)
    print("Vector Store Statistics")
    print("=" * 80 + "\n")

    stats = store.get_stats()

    print(f"Overall Statistics:")
    print(f"   Model: {stats['model_name']}")
    print(f"   Embedding dimension: {stats['embedding_dimension']}")
    print(f"   Total documents: {stats['total_documents']}")

    print(f"\nBy Category:")
    for category, count in sorted(stats['categories'].items()):
        print(f"   - {category}: {count} chunks")

    print(f"\nMetadata Keys:")
    for key in sorted(stats['metadata_keys']):
        print(f"   - {key}")

    print("\n" + "=" * 80 + "\n")

def interactive_mode(store):
    """Interactive query mode"""

    print("\n" + "=" * 80)
    print("Simple Python RAG - Interactive Query Mode")
    print("=" * 80)
    print("Commands:")
    print("  <query>     - Search for documents")
    print("  stats       - Show statistics")
    print("  test        - Run test queries")
    print("  quit        - Exit")
    print()

    while True:
        try:
            query = input("Query> ").strip()

            if not query:
                continue

            if query.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            if query.lower() == 'stats':
                get_stats(store)
                continue

            if query.lower() == 'test':
                test_queries(store)
                continue

            # Normal query
            results = store.query(query, top_k=5)
            print_results(results, query)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main query function"""

    # Check if vector store exists
    if not VECTOR_STORE_PATH.exists():
        print(f"Error: Vector store not found at: {VECTOR_STORE_PATH}")
        print("\nPlease run 'python simple_ingest.py' first to create the vector store.")
        return

    # Load vector store
    print("Loading vector store...")
    try:
        store = load_store(VECTOR_STORE_PATH)
    except Exception as e:
        print(f"Error loading vector store: {e}")
        return

    # Parse command line arguments
    if len(sys.argv) < 2:
        # No arguments - enter interactive mode
        get_stats(store)
        interactive_mode(store)

    elif sys.argv[1] == "--test":
        # Run test queries
        test_queries(store)

    elif sys.argv[1] == "--stats":
        # Show statistics only
        get_stats(store)

    else:
        # Query provided as argument
        query = " ".join(sys.argv[1:])
        results = store.query(query, top_k=5)
        print_results(results, query)

if __name__ == "__main__":
    main()
