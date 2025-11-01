"""
Simple Python Vector Store for RAG Knowledge Base

A lightweight, pure-Python implementation of vector similarity search
that doesn't require ChromaDB or C++ compilation.

Perfect for small to medium document collections (< 500 documents).
"""

from sentence_transformers import SentenceTransformer
import numpy as np
import pickle
from pathlib import Path
from typing import Dict, List, Optional
import json

class SimpleVectorStore:
    """
    A simple vector store using sentence transformers for embeddings
    and numpy for similarity calculations.
    """

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the vector store with an embedding model.

        Args:
            model_name: HuggingFace model name for embeddings
                       Default: all-MiniLM-L6-v2 (fast, good quality, 384 dims)
        """
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.documents = {}  # {doc_id: {text, vector, metadata}}
        self.model_name = model_name
        print(f"[OK] Model loaded (embedding dimension: {self.model.get_sentence_embedding_dimension()})")

    def add_document(
        self,
        doc_id: str,
        text: str,
        metadata: Optional[Dict] = None
    ):
        """
        Add a single document to the store.

        Args:
            doc_id: Unique identifier for the document
            text: Document text to embed
            metadata: Optional metadata dictionary
        """
        # Generate embedding
        vector = self.model.encode(text, convert_to_numpy=True)

        # Store document
        self.documents[doc_id] = {
            'text': text,
            'vector': vector,
            'metadata': metadata or {}
        }

    def add_documents(self, documents: List[Dict]):
        """
        Add multiple documents in batch (more efficient).

        Args:
            documents: List of dicts with keys: doc_id, text, metadata
        """
        print(f"Adding {len(documents)} documents...")

        # Extract texts for batch encoding
        doc_ids = [doc['doc_id'] for doc in documents]
        texts = [doc['text'] for doc in documents]
        metadatas = [doc.get('metadata', {}) for doc in documents]

        # Batch encode (much faster than one-by-one)
        print("  Generating embeddings...")
        vectors = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)

        # Store all documents
        print("  Storing documents...")
        for doc_id, text, vector, metadata in zip(doc_ids, texts, vectors, metadatas):
            self.documents[doc_id] = {
                'text': text,
                'vector': vector,
                'metadata': metadata
            }

        print(f"[OK] Added {len(documents)} documents (total: {len(self.documents)})")

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict] = None,
        min_similarity: float = 0.0
    ) -> List[Dict]:
        """
        Find most similar documents to query.

        Args:
            query_text: Text to search for
            top_k: Number of results to return
            filter_metadata: Optional metadata filters (e.g., {"category": "performance"})
            min_similarity: Minimum similarity threshold (0-1)

        Returns:
            List of dicts with: doc_id, similarity, text, metadata
        """
        if not self.documents:
            return []

        # Generate query embedding
        query_vector = self.model.encode(query_text, convert_to_numpy=True)

        # Calculate similarities
        similarities = []
        for doc_id, doc_data in self.documents.items():
            # Apply metadata filters if provided
            if filter_metadata:
                match = all(
                    doc_data['metadata'].get(key) == value
                    for key, value in filter_metadata.items()
                )
                if not match:
                    continue

            # Calculate cosine similarity
            similarity = self._cosine_similarity(query_vector, doc_data['vector'])

            # Apply minimum similarity threshold
            if similarity < min_similarity:
                continue

            similarities.append({
                'doc_id': doc_id,
                'similarity': float(similarity),  # Convert numpy to Python float
                'text': doc_data['text'],
                'metadata': doc_data['metadata']
            })

        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x['similarity'], reverse=True)

        # Return top k
        return similarities[:top_k]

    def query_multiple(
        self,
        queries: List[str],
        top_k_per_query: int = 3
    ) -> Dict[str, List[Dict]]:
        """
        Run multiple queries and return aggregated results.

        Args:
            queries: List of query strings
            top_k_per_query: Results per query

        Returns:
            Dict mapping query to results
        """
        results = {}
        for query in queries:
            results[query] = self.query(query, top_k=top_k_per_query)
        return results

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.

        Returns value between -1 and 1, where:
        - 1 = identical vectors
        - 0 = orthogonal (no similarity)
        - -1 = opposite vectors
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        # Avoid division by zero
        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def save(self, filepath: Path):
        """
        Save vector store to disk.

        Args:
            filepath: Path to save pickle file
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Save everything
        data = {
            'documents': self.documents,
            'model_name': self.model_name,
            'count': len(self.documents)
        }

        with open(filepath, 'wb') as f:
            pickle.dump(data, f)

        print(f"[OK] Saved {len(self.documents)} documents to {filepath}")

    def load(self, filepath: Path):
        """
        Load vector store from disk.

        Args:
            filepath: Path to pickle file
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"Vector store not found: {filepath}")

        with open(filepath, 'rb') as f:
            data = pickle.load(f)

        self.documents = data['documents']

        # Verify model matches
        if data['model_name'] != self.model_name:
            print(f"[WARNING] Saved model ({data['model_name']}) differs from current model ({self.model_name})")

        print(f"[OK] Loaded {len(self.documents)} documents from {filepath}")

    def get_stats(self) -> Dict:
        """Get statistics about the vector store."""
        if not self.documents:
            return {
                'total_documents': 0,
                'collections': {},
                'metadata_keys': set()
            }

        # Aggregate statistics
        stats = {
            'total_documents': len(self.documents),
            'model_name': self.model_name,
            'embedding_dimension': self.model.get_sentence_embedding_dimension()
        }

        # Count by category/collection
        categories = {}
        all_metadata_keys = set()

        for doc_data in self.documents.values():
            metadata = doc_data['metadata']

            # Track metadata keys
            all_metadata_keys.update(metadata.keys())

            # Count categories
            category = metadata.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1

        stats['categories'] = categories
        stats['metadata_keys'] = list(all_metadata_keys)

        return stats

    def export_metadata(self, filepath: Path):
        """Export all metadata to JSON for inspection."""
        metadata_list = []
        for doc_id, doc_data in self.documents.items():
            metadata_list.append({
                'doc_id': doc_id,
                'metadata': doc_data['metadata'],
                'text_preview': doc_data['text'][:200]
            })

        with open(filepath, 'w') as f:
            json.dump(metadata_list, f, indent=2)

        print(f"[OK] Exported metadata for {len(metadata_list)} documents to {filepath}")

    def clear(self):
        """Clear all documents from the store."""
        self.documents = {}
        print("[OK] Cleared all documents")

    def __len__(self):
        """Return number of documents in store."""
        return len(self.documents)

    def __repr__(self):
        """String representation."""
        return f"SimpleVectorStore(model={self.model_name}, documents={len(self.documents)})"


# Convenience functions for common operations

def create_store(model_name: str = 'all-MiniLM-L6-v2') -> SimpleVectorStore:
    """Create a new vector store."""
    return SimpleVectorStore(model_name=model_name)

def load_store(filepath: Path, model_name: str = 'all-MiniLM-L6-v2') -> SimpleVectorStore:
    """Load an existing vector store."""
    store = SimpleVectorStore(model_name=model_name)
    store.load(filepath)
    return store


if __name__ == "__main__":
    # Example usage
    print("=" * 60)
    print("Simple Vector Store - Example Usage")
    print("=" * 60)

    # Create store
    store = create_store()

    # Add some example documents
    store.add_document(
        doc_id="doc1",
        text="Progressive muscle relaxation is a technique for reducing stress by tensing and relaxing muscle groups.",
        metadata={"category": "technique", "type": "relaxation"}
    )

    store.add_document(
        doc_id="doc2",
        text="Confidence in public speaking can be developed through mental rehearsal and visualization.",
        metadata={"category": "script", "type": "confidence"}
    )

    store.add_document(
        doc_id="doc3",
        text="Deep breathing activates the parasympathetic nervous system, promoting calm.",
        metadata={"category": "neuroscience", "type": "breathing"}
    )

    # Query
    print("\nQuerying: 'stress reduction techniques'")
    results = store.query("stress reduction techniques", top_k=2)

    for i, result in enumerate(results, 1):
        print(f"\n  Result {i} (similarity: {result['similarity']:.3f})")
        print(f"  Text: {result['text'][:80]}...")
        print(f"  Category: {result['metadata']['category']}")

    # Save
    print("\nSaving store...")
    store.save(Path("example_vector_store.pkl"))

    # Load
    print("\nLoading store...")
    loaded_store = load_store(Path("example_vector_store.pkl"))

    print(f"\n[OK] Example complete! Store has {len(loaded_store)} documents")
