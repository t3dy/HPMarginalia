"""
Stage 2: Extract excerpts from ingested source documents.

Breaks extracted text into manageable chunks (~500-1500 words)
preserving page references where detectable.
"""

import os
import sys
import re
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.models import SourceExcerpt, make_id
from src.validate import validate_source_excerpt
from src.db import get_connection, insert_record, init_db

TARGET_WORDS = 800
MIN_WORDS = 200
MAX_WORDS = 1500


def detect_page_breaks(text: str) -> list[tuple[int | None, str]]:
    """Split text on page break markers, returning (page_num, text) tuples."""
    # Common page break patterns in extracted PDFs
    patterns = [
        r'\n\s*---\s*\n',           # Markdown horizontal rules
        r'\n\s*\* \* \*\s*\n',      # Asterisk separators
        r'\f',                       # Form feed
        r'\n(?:Page|p\.)\s*(\d+)',   # Explicit page numbers
    ]

    # Try page number pattern first
    page_pattern = re.compile(r'\n(?:Page|p\.)\s*(\d+)\s*\n', re.IGNORECASE)
    page_matches = list(page_pattern.finditer(text))

    if page_matches:
        segments = []
        prev_end = 0
        for m in page_matches:
            if prev_end < m.start():
                segments.append((None, text[prev_end:m.start()]))
            prev_end = m.end()
            page_num = int(m.group(1))
            # Find next match or end
            next_start = page_matches[page_matches.index(m) + 1].start() if m != page_matches[-1] else len(text)
            segments.append((page_num, text[m.end():next_start]))
            prev_end = next_start
        return [(p, t) for p, t in segments if t.strip()]

    # Fallback: split on section markers
    sections = re.split(r'\n\s*---\s*\n|\n\s*#{1,3}\s+', text)
    return [(None, s) for s in sections if s.strip()]


def chunk_text(text: str, target_words: int = TARGET_WORDS) -> list[str]:
    """Split text into chunks of approximately target_words."""
    paragraphs = re.split(r'\n\s*\n', text)
    chunks = []
    current_chunk = []
    current_words = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        para_words = len(para.split())

        if current_words + para_words > MAX_WORDS and current_words >= MIN_WORDS:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [para]
            current_words = para_words
        else:
            current_chunk.append(para)
            current_words += para_words

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks


def detect_section_heading(text: str) -> str | None:
    """Try to extract a section heading from the start of text."""
    lines = text.strip().split("\n")
    if lines:
        first = lines[0].strip()
        # Markdown headings
        if first.startswith("#"):
            return re.sub(r'^#+\s*', '', first)
        # ALL CAPS headings (common in PDFs)
        if first.isupper() and len(first) < 100:
            return first.title()
        # Short first line that looks like a heading
        if len(first) < 80 and not first.endswith("."):
            return first
    return None


def excerpt_all():
    """Generate excerpts from all extracted source documents."""
    init_db()
    conn = get_connection()
    docs = conn.execute(
        "SELECT * FROM source_documents WHERE text_extracted = 1"
    ).fetchall()
    conn.close()

    total_excerpts = 0

    for doc in docs:
        doc = dict(doc)
        if not doc["extracted_text_path"] or not os.path.exists(doc["extracted_text_path"]):
            continue

        with open(doc["extracted_text_path"], "r", encoding="utf-8") as f:
            text = f.read()

        if not text.strip():
            continue

        # Chunk the text
        chunks = chunk_text(text)
        print(f"  {doc['filename'][:60]}... -> {len(chunks)} excerpts")

        for i, chunk in enumerate(chunks):
            heading = detect_section_heading(chunk)
            exc = SourceExcerpt(
                id=make_id("exc"),
                source_document_id=doc["id"],
                text=chunk,
                section_heading=heading,
                created_at=datetime.now().isoformat(),
            )
            validate_source_excerpt(exc)
            insert_record("source_excerpts", exc.to_dict())
            total_excerpts += 1

    print(f"\nCreated {total_excerpts} excerpts.")


if __name__ == "__main__":
    excerpt_all()
