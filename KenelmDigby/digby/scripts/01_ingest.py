"""
Stage 1: Ingest source files from the Kenelm Digby corpus.

Reads all files from ../  (the parent KenelmDigby/ folder),
registers them as source_documents in the database, and
extracts text from readable formats (txt, md).

PDF text extraction requires PyPDF2 or pdfplumber — falls back
gracefully if not installed.
"""

import os
import sys
import re
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.models import SourceDocument, make_id
from src.validate import validate_source_document
from src.db import init_db, insert_record, get_connection

CORPUS_DIR = os.path.join(PROJECT_ROOT, "..")  # KenelmDigby/
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
SUPPORTED_TYPES = {".pdf", ".txt", ".md", ".epub", ".xlsx", ".pptx"}


def parse_filename_metadata(filename: str) -> dict:
    """Extract author, year, journal, DOI from structured filenames."""
    meta = {"author": None, "year": None, "journal": None, "doi": None}

    # Try to extract DOI pattern like [10.xxxx/yyyy]
    doi_match = re.search(r'\[(\d+\.\d+[/_][^\]]+)\]', filename)
    if doi_match:
        meta["doi"] = doi_match.group(1).replace("_", "/")

    # Try to extract author from {Author, Name} pattern
    author_match = re.search(r'\{([^}]+?)(?:\(author\))?\}', filename)
    if author_match:
        meta["author"] = author_match.group(1).strip().rstrip(",").rstrip("_")

    # Try to extract year from (YYYY ...) pattern
    year_match = re.search(r'\((\d{4})\b', filename)
    if year_match:
        meta["year"] = int(year_match.group(1))

    # Try to extract journal from [Journal Name ...] at start
    journal_match = re.match(r'\[([^\]]+?)\s+\d{4}', filename)
    if journal_match:
        meta["journal"] = journal_match.group(1)

    return meta


def make_title(filename: str) -> str:
    """Create a human-readable title from the filename."""
    # Remove extension
    name = os.path.splitext(filename)[0]
    # Remove libgen suffix
    name = re.sub(r'\s*[-_]?\s*libgen\.li$', '', name)
    # Remove DOI brackets
    name = re.sub(r'\[\d+\.\d+[^\]]*\]', '', name)
    # Remove ID numbers in braces at end
    name = re.sub(r'\{\d+\}\s*$', '', name)
    # Clean up multiple spaces
    name = re.sub(r'\s+', ' ', name).strip()
    # Truncate if very long
    if len(name) > 200:
        name = name[:197] + "..."
    return name


def extract_text_simple(filepath: str, file_type: str) -> str | None:
    """Extract text from simple formats (txt, md). Returns None for others."""
    if file_type in ("txt", "md"):
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except Exception as e:
            print(f"  Warning: Could not read {filepath}: {e}")
            return None
    return None


def extract_text_pdf(filepath: str) -> str | None:
    """Try to extract text from PDF. Returns None if library not available."""
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
        return "\n\n".join(text_parts) if text_parts else None
    except ImportError:
        pass

    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(filepath)
        text_parts = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
        return "\n\n".join(text_parts) if text_parts else None
    except ImportError:
        return None
    except Exception as e:
        print(f"  Warning: PDF extraction failed for {filepath}: {e}")
        return None


def ingest_all():
    """Scan corpus directory and ingest all supported files."""
    init_db()
    os.makedirs(RAW_DIR, exist_ok=True)

    corpus_path = Path(CORPUS_DIR).resolve()
    # Skip the digby/ subdirectory itself
    digby_subdir = Path(PROJECT_ROOT).resolve()

    files = sorted([
        f for f in corpus_path.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_TYPES
        and not f.resolve().is_relative_to(digby_subdir)
    ])

    print(f"Found {len(files)} source files in {corpus_path}")
    ingested = 0

    for fpath in files:
        filename = fpath.name
        file_type = fpath.suffix.lower().lstrip(".")
        doc_id = make_id("sdoc")
        meta = parse_filename_metadata(filename)
        title = make_title(filename)

        # Try text extraction
        text = None
        extracted_path = None
        if file_type in ("txt", "md"):
            text = extract_text_simple(str(fpath), file_type)
        elif file_type == "pdf":
            text = extract_text_pdf(str(fpath))

        if text:
            extracted_path = os.path.join(RAW_DIR, f"{doc_id}.txt")
            with open(extracted_path, "w", encoding="utf-8") as f:
                f.write(text)

        doc = SourceDocument(
            id=doc_id,
            filename=filename,
            filepath=str(fpath.relative_to(corpus_path.parent)),
            title=title,
            file_type=file_type,
            author=meta["author"],
            year=meta["year"],
            journal=meta["journal"],
            doi=meta["doi"],
            text_extracted=text is not None,
            extracted_text_path=extracted_path,
            ingested_at=datetime.now().isoformat(),
        )

        validate_source_document(doc)
        insert_record("source_documents", doc.to_dict())
        status = "extracted" if text else "registered"
        print(f"  [{status}] {filename[:80]}...")
        ingested += 1

    print(f"\nIngested {ingested} source documents.")


if __name__ == "__main__":
    ingest_all()
