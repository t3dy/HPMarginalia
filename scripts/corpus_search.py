"""Corpus search utilities: search across markdown chunks and full documents.

Provides keyword-based search across the /chunks/ and /md/ directories
with provenance tracking. No embeddings required.

Functions:
    search_chunks(query, top_n=20) -> list of match dicts
    search_by_term(term_slug, synonyms=None) -> list of match dicts
    search_documents(query, doc_filter=None) -> list of match dicts
"""

import re
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CHUNKS_DIR = BASE_DIR / "chunks"
MD_DIR = BASE_DIR / "md"


def _parse_chunk_frontmatter(text):
    """Extract YAML frontmatter from a chunk file."""
    meta = {}
    if text.startswith('---'):
        end = text.find('---', 3)
        if end > 0:
            for line in text[3:end].strip().split('\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    val = val.strip().strip('"').strip("'")
                    meta[key.strip()] = val
    return meta


def _extract_page_refs(text):
    """Extract page markers from chunk text."""
    return re.findall(r'<!-- Page (\d+) -->', text)


def _score_match(text, query_terms):
    """Score a text block by frequency and proximity of query terms."""
    text_lower = text.lower()
    score = 0
    for term in query_terms:
        count = text_lower.count(term.lower())
        score += count
    return score


def _context_window(text, query_terms, window=300):
    """Extract the best context window around the query terms."""
    text_lower = text.lower()
    best_pos = -1
    best_score = 0

    for term in query_terms:
        pos = text_lower.find(term.lower())
        if pos >= 0:
            # Score this position by counting nearby term occurrences
            start = max(0, pos - window)
            end = min(len(text), pos + window)
            snippet = text_lower[start:end]
            score = sum(snippet.count(t.lower()) for t in query_terms)
            if score > best_score:
                best_score = score
                best_pos = pos

    if best_pos < 0:
        return text[:window * 2] if len(text) > window * 2 else text

    start = max(0, best_pos - window)
    end = min(len(text), best_pos + window)
    snippet = text[start:end].strip()

    # Clean up snippet boundaries
    if start > 0:
        first_space = snippet.find(' ')
        if first_space > 0:
            snippet = '...' + snippet[first_space:]
    if end < len(text):
        last_space = snippet.rfind(' ')
        if last_space > 0:
            snippet = snippet[:last_space] + '...'

    return snippet


def search_chunks(query, top_n=20):
    """Search across all chunk files for passages matching query.

    Args:
        query: Search string (can be multiple words)
        top_n: Maximum results to return

    Returns:
        List of dicts: {chunk_path, source_doc, section, page_refs,
                        matched_text, relevance_score, word_count}
    """
    if not CHUNKS_DIR.exists():
        return []

    query_terms = [t for t in query.lower().split() if len(t) > 2]
    if not query_terms:
        return []

    results = []

    for doc_dir in sorted(CHUNKS_DIR.iterdir()):
        if not doc_dir.is_dir():
            continue
        for chunk_file in sorted(doc_dir.glob('chunk_*.md')):
            text = chunk_file.read_text(encoding='utf-8', errors='replace')
            meta = _parse_chunk_frontmatter(text)

            # Strip frontmatter for content search
            body_start = text.find('---', 3)
            body = text[body_start + 3:].strip() if body_start > 0 else text

            score = _score_match(body, query_terms)
            if score == 0:
                continue

            page_refs = _extract_page_refs(body)
            context = _context_window(body, query_terms)

            results.append({
                'chunk_path': str(chunk_file.relative_to(BASE_DIR)),
                'source_doc': meta.get('source', str(doc_dir.name)),
                'section': meta.get('section', ''),
                'page_refs': page_refs,
                'matched_text': context,
                'relevance_score': score,
                'word_count': int(meta.get('word_count', 0)),
            })

    results.sort(key=lambda x: x['relevance_score'], reverse=True)
    return results[:top_n]


def search_by_term(term_label, synonyms=None):
    """Search for a dictionary term across all chunks.

    Args:
        term_label: The term label (e.g. "Signature")
        synonyms: Optional list of alternative forms to search

    Returns:
        List of match dicts (same format as search_chunks)
    """
    search_terms = [term_label]
    if synonyms:
        search_terms.extend(synonyms)

    all_results = []
    seen_paths = set()

    for term in search_terms:
        results = search_chunks(term, top_n=30)
        for r in results:
            if r['chunk_path'] not in seen_paths:
                seen_paths.add(r['chunk_path'])
                all_results.append(r)

    all_results.sort(key=lambda x: x['relevance_score'], reverse=True)
    return all_results[:20]


def search_documents(query, doc_filter=None):
    """Search across full markdown documents (not chunks).

    Args:
        query: Search string
        doc_filter: Optional substring to filter document filenames

    Returns:
        List of dicts: {doc_path, page_refs, matched_text, relevance_score}
    """
    if not MD_DIR.exists():
        return []

    query_terms = [t for t in query.lower().split() if len(t) > 2]
    if not query_terms:
        return []

    results = []

    for md_file in sorted(MD_DIR.glob('*.md')):
        if doc_filter and doc_filter.lower() not in md_file.name.lower():
            continue

        text = md_file.read_text(encoding='utf-8', errors='replace')
        score = _score_match(text, query_terms)
        if score == 0:
            continue

        page_refs = _extract_page_refs(text)
        context = _context_window(text, query_terms)

        results.append({
            'doc_path': str(md_file.relative_to(BASE_DIR)),
            'page_refs': page_refs,
            'matched_text': context,
            'relevance_score': score,
        })

    results.sort(key=lambda x: x['relevance_score'], reverse=True)
    return results


if __name__ == "__main__":
    import sys
    query = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else "alchemical mercury"
    print(f"Searching chunks for: '{query}'\n")
    results = search_chunks(query, top_n=10)
    for i, r in enumerate(results, 1):
        print(f"{i}. [{r['relevance_score']}] {r['source_doc']}")
        print(f"   Section: {r['section']}")
        print(f"   Pages: {', '.join(r['page_refs'][:5])}")
        print(f"   Match: {r['matched_text'][:200]}...")
        print()
