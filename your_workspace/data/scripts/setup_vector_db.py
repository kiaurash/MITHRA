"""
Setup ChromaDB Vector Database for BehaviorShift RAG Knowledge Base

This script initializes the ChromaDB vector database and creates collections
for different content types (scripts, techniques, patterns, etc.)
"""

import chromadb
from chromadb.config import Settings
import os
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
VECTOR_DB_PATH = PROJECT_ROOT / "your_workspace" / "data" / "vector_db"

def setup_chromadb():
    """Initialize ChromaDB and create collections"""

    print(f"Setting up ChromaDB at: {VECTOR_DB_PATH}")

    # Create directory if it doesn't exist
    VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)

    # Initialize ChromaDB client
    client = chromadb.PersistentClient(
        path=str(VECTOR_DB_PATH),
        settings=Settings(
            anonymized_telemetry=False,
            allow_reset=True
        )
    )

    print("✓ ChromaDB client initialized")

    # Define collections
    collections_config = {
        "hypnosis_scripts": {
            "description": "Complete hypnosis session scripts",
            "metadata": ["title", "category", "target_skill", "duration", "archetypes", "learning_style"]
        },
        "techniques": {
            "description": "Specific hypnosis techniques (induction, deepening, awakening)",
            "metadata": ["technique", "category", "duration", "best_for", "difficulty"]
        },
        "language_patterns": {
            "description": "Therapeutic language patterns (Ericksonian, NLP, permissive)",
            "metadata": ["pattern_type", "category", "use_case"]
        },
        "archetypes": {
            "description": "Jungian archetypal profiles and imagery",
            "metadata": ["archetype", "qualities", "best_for_skills", "shadow"]
        },
        "neuroscience": {
            "description": "Neuroscience insights supporting hypnosis",
            "metadata": ["topic", "relevant_for", "mechanism"]
        },
        "best_practices": {
            "description": "Safety protocols and ethical guidelines",
            "metadata": ["category", "importance", "guideline_type"]
        }
    }

    # Create or get collections
    for collection_name, config in collections_config.items():
        try:
            # Try to get existing collection
            collection = client.get_collection(name=collection_name)
            print(f"✓ Found existing collection: {collection_name} ({collection.count()} documents)")
        except:
            # Create new collection
            collection = client.create_collection(
                name=collection_name,
                metadata={"description": config["description"]}
            )
            print(f"✓ Created new collection: {collection_name}")

    print("\n✓ ChromaDB setup complete!")
    print(f"  Database location: {VECTOR_DB_PATH}")
    print(f"  Collections created: {len(collections_config)}")

    return client

def list_collections(client):
    """List all collections and their document counts"""
    print("\n=== Current Collections ===")
    collections = client.list_collections()
    for collection in collections:
        print(f"  - {collection.name}: {collection.count()} documents")
    print()

def reset_database():
    """Reset the entire database (use with caution!)"""
    response = input("⚠️  Are you sure you want to reset the entire database? (yes/no): ")
    if response.lower() == "yes":
        client = chromadb.PersistentClient(path=str(VECTOR_DB_PATH))
        client.reset()
        print("✓ Database reset complete")
    else:
        print("Reset cancelled")

if __name__ == "__main__":
    import sys

    # Check for reset flag
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        reset_database()

    # Setup database
    client = setup_chromadb()

    # List collections
    list_collections(client)

    print("Next step: Run 'python ingest_documents.py' to add documents to the database")
