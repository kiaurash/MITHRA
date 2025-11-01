#!/usr/bin/env python3
"""
Mock RAG Query Script for Sprint 1 Testing

This script simulates RAG (Retrieval-Augmented Generation) functionality by:
1. Loading the metadata index
2. Matching user queries against source metadata
3. Returning the most relevant source documents

In a real RAG system, this would use:
- Vector embeddings (e.g., with OpenAI, Cohere, or local models)
- Vector database (e.g., ChromaDB, Pinecone, Weaviate)
- Semantic similarity search

This mock version uses simple keyword matching as a proxy for demonstration.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Tuple


class MockRAG:
    """Mock RAG system for testing content generation pipeline"""

    def __init__(self, base_path: str = None):
        """Initialize the mock RAG system

        Args:
            base_path: Base directory containing mock_rag folder.
                      Defaults to script's parent directory.
        """
        if base_path is None:
            base_path = Path(__file__).parent

        self.base_path = Path(base_path)
        self.sources_path = self.base_path / "sources"
        self.metadata_path = self.base_path / "metadata_index.json"

        # Load metadata index
        with open(self.metadata_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)

        self.sources = self.metadata['sources']

    def query(self, query_text: str, top_k: int = 3) -> List[Dict]:
        """Query the mock RAG system

        Args:
            query_text: The search query (topic, question, or keywords)
            top_k: Number of top results to return

        Returns:
            List of source metadata dictionaries with relevance scores
        """
        query_lower = query_text.lower()
        query_words = set(query_lower.split())

        scored_sources = []

        for source in self.sources:
            score = self._calculate_relevance(query_lower, query_words, source)
            scored_sources.append({
                'source': source,
                'relevance_score': score
            })

        # Sort by relevance score (descending)
        scored_sources.sort(key=lambda x: x['relevance_score'], reverse=True)

        return scored_sources[:top_k]

    def _calculate_relevance(self, query_lower: str, query_words: set, source: Dict) -> float:
        """Calculate relevance score for a source

        This is a simplified scoring algorithm. A real RAG would use
        semantic similarity between vector embeddings.
        """
        score = 0.0

        # Check title (highest weight)
        if any(word in source['title'].lower() for word in query_words):
            score += 10.0

        # Check topics (high weight)
        for topic in source['topics']:
            if topic in query_lower or any(word in topic for word in query_words):
                score += 5.0

        # Check key concepts (medium weight)
        for concept in source['key_concepts']:
            if concept in query_lower or any(word in concept for word in query_words):
                score += 3.0

        # Check use_for_queries_about (medium-high weight)
        for query_pattern in source['use_for_queries_about']:
            if query_pattern in query_lower:
                score += 4.0
            elif any(word in query_pattern for word in query_words):
                score += 2.0

        # Check relevance tags (lower weight)
        for tag in source['relevance_tags']:
            if tag in query_lower or any(word in tag for word in query_words):
                score += 1.0

        return score

    def retrieve_source_content(self, source_id: str) -> str:
        """Retrieve the full content of a source document

        Args:
            source_id: The ID of the source to retrieve

        Returns:
            Full text content of the source
        """
        # Find the source in metadata
        source = next((s for s in self.sources if s['id'] == source_id), None)

        if source is None:
            raise ValueError(f"Source ID '{source_id}' not found")

        # Load the file content
        file_path = self.sources_path / source['file']
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return content

    def query_and_retrieve(self, query_text: str, top_k: int = 3) -> List[Dict]:
        """Query and retrieve full content of top results

        Args:
            query_text: The search query
            top_k: Number of top results to return

        Returns:
            List of dictionaries with metadata and full content
        """
        results = self.query(query_text, top_k)

        for result in results:
            source_id = result['source']['id']
            result['content'] = self.retrieve_source_content(source_id)

        return results


def main():
    """Demo usage of the mock RAG system"""

    print("=" * 70)
    print("Mock RAG System - Sprint 1 Testing")
    print("=" * 70)
    print()

    # Initialize the mock RAG
    rag = MockRAG()

    # Example queries
    test_queries = [
        "improving emotional intimacy in long-term relationships",
        "what is oneness and connection",
        "leadership and collaboration",
        "daily practices for mindfulness",
        "overcoming loneliness and isolation"
    ]

    for query in test_queries:
        print(f"\n{'=' * 70}")
        print(f"QUERY: {query}")
        print('=' * 70)

        results = rag.query(query, top_k=2)

        for i, result in enumerate(results, 1):
            source = result['source']
            score = result['relevance_score']

            print(f"\nResult #{i} (Relevance: {score:.1f})")
            print(f"  Title: {source['title']}")
            print(f"  Topics: {', '.join(source['topics'][:5])}")
            print(f"  File: {source['file']}")

    print("\n" + "=" * 70)
    print("Mock RAG system ready for Sprint 1 pipeline testing!")
    print("=" * 70)


if __name__ == "__main__":
    main()
