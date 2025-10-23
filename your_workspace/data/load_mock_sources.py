"""
Mock RAG Source Loader

Reads markdown files from mock_sources/ folder and formats them
as if they came from a Vector DB query (simulates RAG for experiment).

Usage:
    from load_mock_sources import get_mock_sources

    sources = get_mock_sources()
    # Returns list of formatted sources ready for Step 1
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
import re


def parse_frontmatter(content: str) -> tuple[Dict, str]:
    """
    Parse YAML frontmatter from markdown file.

    Returns:
        (metadata_dict, markdown_content)
    """
    # Check if file starts with frontmatter delimiter
    if not content.startswith('---'):
        return {}, content

    # Find the closing delimiter
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content

    frontmatter = parts[1].strip()
    markdown = parts[2].strip()

    # Parse frontmatter (simple YAML parsing)
    metadata = {}
    for line in frontmatter.split('\n'):
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]

            # Parse lists [tag1, tag2]
            if value.startswith('[') and value.endswith(']'):
                value = [v.strip().strip('"').strip("'")
                        for v in value[1:-1].split(',')]
            else:
                # Parse numbers (only if not a list)
                try:
                    if '.' in value:
                        value = float(value)
                    else:
                        value = int(value)
                except (ValueError, AttributeError, TypeError):
                    pass

            metadata[key] = value

    return metadata, markdown


def load_markdown_file(file_path: Path) -> Optional[Dict]:
    """
    Load a single markdown file and return formatted source.

    Returns:
        Dict with 'text', 'metadata', 'relevance_score' or None if skip
    """
    # Skip certain files
    if file_path.name.startswith('_') or file_path.name == 'README.md':
        return None

    if file_path.suffix != '.md':
        return None

    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Warning: Could not read {file_path.name}: {e}")
        return None

    # Parse frontmatter and content
    metadata, markdown_content = parse_frontmatter(content)

    # Default values if not in frontmatter
    if 'title' not in metadata:
        metadata['title'] = file_path.stem.replace('_', ' ').title()
    if 'author' not in metadata:
        metadata['author'] = 'Unknown'
    if 'source_type' not in metadata:
        metadata['source_type'] = 'article'

    relevance_score = metadata.pop('relevance_score', 0.9)

    return {
        'text': markdown_content,
        'metadata': metadata,
        'relevance_score': float(relevance_score)
    }


def get_mock_sources(
    sources_dir: Optional[str] = None,
    min_relevance: float = 0.0
) -> List[Dict]:
    """
    Load all mock RAG sources from markdown files.

    Args:
        sources_dir: Path to mock_sources directory (defaults to this script's location)
        min_relevance: Minimum relevance score to include (0.0-1.0)

    Returns:
        List of source dicts with 'text', 'metadata', 'relevance_score'
        Sorted by relevance_score descending
    """
    # Default to mock_sources folder next to this script
    if sources_dir is None:
        sources_dir = Path(__file__).parent / 'mock_sources'
    else:
        sources_dir = Path(sources_dir)

    if not sources_dir.exists():
        print(f"Warning: Sources directory not found: {sources_dir}")
        return []

    sources = []

    # Load all markdown files
    for file_path in sources_dir.glob('*.md'):
        source = load_markdown_file(file_path)
        if source and source['relevance_score'] >= min_relevance:
            sources.append(source)

    # Sort by relevance (highest first)
    sources.sort(key=lambda x: x['relevance_score'], reverse=True)

    return sources


def format_sources_for_step1(sources: List[Dict]) -> str:
    """
    Format sources as text for inclusion in Step 1 prompt.

    Returns:
        Formatted string ready to insert into Claude prompt
    """
    if not sources:
        return "No relevant internal sources found."

    formatted = "## Internal Knowledge Base Results (from Vector DB):\n\n"
    formatted += f"Found {len(sources)} relevant sources:\n\n"
    formatted += "---\n\n"

    for i, source in enumerate(sources, 1):
        metadata = source['metadata']

        formatted += f"### Internal Source {i}: {metadata.get('title', 'Untitled')}\n\n"
        formatted += f"**Author**: {metadata.get('author', 'Unknown')}\n"
        formatted += f"**Type**: {metadata.get('source_type', 'article')}\n"
        formatted += f"**Date**: {metadata.get('date', 'N/A')}\n"
        formatted += f"**Relevance Score**: {source['relevance_score']:.2f}\n\n"

        if 'tags' in metadata:
            formatted += f"**Tags**: {', '.join(metadata['tags'])}\n\n"

        formatted += f"{source['text']}\n\n"
        formatted += "---\n\n"

    return formatted


def display_sources_summary(sources: List[Dict]) -> None:
    """Print a summary of loaded sources."""
    print(f"\n{'='*80}")
    print(f"MOCK RAG SOURCES LOADED")
    print(f"{'='*80}\n")
    print(f"Total sources: {len(sources)}\n")

    for i, source in enumerate(sources, 1):
        metadata = source['metadata']
        word_count = len(source['text'].split())
        print(f"{i}. {metadata.get('title', 'Untitled')}")
        print(f"   Author: {metadata.get('author', 'Unknown')}")
        print(f"   Relevance: {source['relevance_score']:.2f}")
        print(f"   Words: {word_count}")
        print()


# ============================================================================
# Command-line testing
# ============================================================================

if __name__ == "__main__":
    print("Testing Mock RAG Source Loader...\n")

    # Load sources
    sources = get_mock_sources()

    # Display summary
    display_sources_summary(sources)

    # Show formatted output
    print(f"{'='*80}")
    print("FORMATTED FOR STEP 1 PROMPT:")
    print(f"{'='*80}\n")

    formatted = format_sources_for_step1(sources)
    print(formatted)

    # Stats
    total_words = sum(len(s['text'].split()) for s in sources)
    print(f"{'='*80}")
    print(f"STATISTICS:")
    print(f"{'='*80}")
    print(f"Total sources: {len(sources)}")
    print(f"Total words: {total_words:,}")
    print(f"Average words per source: {total_words/len(sources) if sources else 0:.0f}")
    print(f"Relevance scores range: {min(s['relevance_score'] for s in sources):.2f} - {max(s['relevance_score'] for s in sources):.2f}")
