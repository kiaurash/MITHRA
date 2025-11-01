"""
BM25 Keyword Search using grep

Fast lexical search for initial document filtering in hybrid RAG.
"""

import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import re
import json

# Get project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
CORPUS_PATH = PROJECT_ROOT / "your_workspace" / "data" / "rag_corpus"


def extract_keywords(query: str) -> List[str]:
    """
    Extract meaningful keywords from query.

    Args:
        query: User query string

    Returns:
        List of keywords (lowercased, stopwords removed)
    """
    # Simple stopword list
    stopwords = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'will', 'with', 'how', 'do', 'i', 'can', 'should'
    }

    # Extract words, lowercase, remove stopwords
    words = re.findall(r'\b\w+\b', query.lower())
    keywords = [w for w in words if w not in stopwords and len(w) > 2]

    return keywords


def grep_search(
    keyword: str,
    path: Path,
    context_lines: int = 2,
    ignore_case: bool = True
) -> List[Dict]:
    """
    Use grep to search for keyword in markdown files.

    Args:
        keyword: Search term
        path: Directory to search
        context_lines: Number of context lines before/after match
        ignore_case: Case-insensitive search

    Returns:
        List of matches with file, line number, and context
    """
    cmd = [
        'grep',
        '-r',  # Recursive
        '-n',  # Line numbers
        f'-C{context_lines}',  # Context lines
        '--include=*.md',  # Only markdown files
    ]

    if ignore_case:
        cmd.append('-i')

    # Convert Windows path to forward slashes for grep
    path_str = str(path).replace('\\', '/')
    cmd.extend([keyword, path_str])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )

        # Check if grep succeeded
        if result.returncode not in [0, 1]:  # 0 = found, 1 = not found, >1 = error
            return []

        if not result.stdout or result.returncode == 1:
            # No matches found - this is normal
            return []

        # Parse grep output
        matches = {}  # Use dict to group by file

        for line in result.stdout.split('\n'):
            if not line.strip():
                continue

            # Skip separator lines (--) from context output
            if line.strip() == '--':
                continue

            # Check for file:line:content format (actual match)
            # or file-line-content format (context line)
            # Handle Windows absolute paths (C:/path...) by matching everything up to :NUMBER:
            match = re.match(r'(.+?)[:-](\d+)[:-](.*)$', line)
            if match:
                file_path, line_num, content = match.groups()

                # Normalize path to relative format
                file_path = file_path.replace('\\', '/')
                if CORPUS_PATH.as_posix() in file_path:
                    file_path = file_path.split(CORPUS_PATH.as_posix() + '/')[-1]

                # Initialize file entry
                if file_path not in matches:
                    matches[file_path] = {
                        'file': file_path,
                        'keyword': keyword,
                        'matches': []
                    }

                # Add line
                matches[file_path]['matches'].append({
                    'line_num': int(line_num),
                    'content': content.strip()
                })

        return list(matches.values())

    except subprocess.TimeoutExpired:
        print(f"[WARNING] Grep search timed out for keyword: {keyword}")
        return []
    except FileNotFoundError:
        # grep not available, fall back to Python search
        return python_fallback_search(keyword, path, ignore_case)


def python_fallback_search(
    keyword: str,
    path: Path,
    ignore_case: bool = True
) -> List[Dict]:
    """
    Fallback to pure Python search if grep unavailable (Windows).
    """
    matches = []
    keyword_lower = keyword.lower() if ignore_case else keyword

    for md_file in path.rglob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            file_matches = []
            for i, line in enumerate(lines, 1):
                line_to_check = line.lower() if ignore_case else line
                if keyword_lower in line_to_check:
                    file_matches.append({
                        'line_num': i,
                        'content': line.strip()
                    })

            if file_matches:
                matches.append({
                    'file': str(md_file.relative_to(CORPUS_PATH)),
                    'keyword': keyword,
                    'matches': file_matches
                })
        except Exception as e:
            continue

    return matches


def bm25_search(
    query: str,
    corpus_path: Optional[Path] = None,
    top_k: int = 20,
    context_lines: int = 2
) -> Dict:
    """
    Perform BM25-style keyword search using grep.

    Args:
        query: User query
        corpus_path: Path to corpus (default: rag_corpus/)
        top_k: Maximum documents to return
        context_lines: Context lines around matches

    Returns:
        Dict with search results and metadata
    """
    if corpus_path is None:
        corpus_path = CORPUS_PATH

    print(f"BM25 Search Query: \"{query}\"")
    print("=" * 80)

    # Extract keywords
    keywords = extract_keywords(query)
    print(f"Keywords: {', '.join(keywords)}")
    print()

    # Search for each keyword
    all_matches = {}
    for keyword in keywords:
        print(f"Searching for: {keyword}...")
        matches = grep_search(keyword, corpus_path, context_lines)

        for match in matches:
            file_path = match['file']

            # Initialize document entry
            if file_path not in all_matches:
                all_matches[file_path] = {
                    'file': file_path,
                    'score': 0,
                    'keyword_hits': {},
                    'total_matches': 0,
                    'sample_contexts': []
                }

            # Update document score
            num_matches = len(match['matches'])
            all_matches[file_path]['keyword_hits'][keyword] = num_matches
            all_matches[file_path]['total_matches'] += num_matches
            all_matches[file_path]['score'] += num_matches

            # Store sample context (first match only)
            if match['matches']:
                all_matches[file_path]['sample_contexts'].append({
                    'keyword': keyword,
                    'line': match['matches'][0]['line_num'],
                    'context': match['matches'][0]['content']
                })

    # Sort by score
    ranked_docs = sorted(
        all_matches.values(),
        key=lambda x: x['score'],
        reverse=True
    )[:top_k]

    # Print summary
    print(f"\nFound {len(ranked_docs)} documents with matches")
    print("=" * 80)
    print()

    for i, doc in enumerate(ranked_docs[:5], 1):
        print(f"{i}. {doc['file']} (score: {doc['score']}, matches: {doc['total_matches']})")
        print(f"   Keywords: {', '.join(doc['keyword_hits'].keys())}")
        if doc['sample_contexts']:
            preview = doc['sample_contexts'][0]['context'][:100]
            print(f"   Preview: {preview}...")
        print()

    return {
        'query': query,
        'keywords': keywords,
        'results': ranked_docs,
        'total_documents': len(ranked_docs)
    }


def get_document_ids(bm25_results: Dict, top_k: int = 10) -> List[str]:
    """
    Extract document IDs from BM25 results for vector filtering.

    Args:
        bm25_results: Results from bm25_search()
        top_k: Number of document IDs to return

    Returns:
        List of document file paths
    """
    return [doc['file'] for doc in bm25_results['results'][:top_k]]


if __name__ == "__main__":
    # Test BM25 search
    import sys

    if len(sys.argv) < 2:
        print("Usage: python bm25_search.py \"your query\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    results = bm25_search(query)

    # Save results to JSON
    output_file = PROJECT_ROOT / "your_workspace" / "data" / "scripts" / "bm25_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_file}")
