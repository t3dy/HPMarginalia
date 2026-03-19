"""Extract folio/signature references from Russell's PhD dissertation."""

import sqlite3
import re
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF not installed. Run: pip install PyMuPDF")
    raise

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"
THESIS_FILENAME = "PhD_Thesis_ _James_Russell Hypnerotomachia Polyphili.pdf"
THESIS_PATH = BASE_DIR / THESIS_FILENAME

# Chapter page ranges (approximate, from TOC - 1-indexed PDF pages)
# These will be refined after first extraction pass
CHAPTER_RANGES = {
    1: (1, 40),      # The HP and its readership
    2: (41, 60),     # Literature Review
    3: (61, 80),     # Methodology
    4: (81, 100),    # Modena - F.C. Panini Estate
    5: (101, 122),   # Como - INCUN A.5.13
    6: (123, 170),   # London - BL C.60.o.12
    7: (171, 203),   # Buffalo
    8: (204, 230),   # Vatican
    9: (204, 250),   # Siena O.III.38 + Sydney
    10: (251, 262),  # Conclusions
}

# Manuscript shelfmark by chapter
CHAPTER_MANUSCRIPTS = {
    4: 'Modena (Panini)',
    5: 'INCUN A.5.13',
    6: 'C.60.o.12',
    7: 'Buffalo RBR',
    8: 'Inc.Stam.Chig.II.610',
    9: 'O.III.38',
}

# Regex patterns for signature references
# Matches: (a4r), (c7v), (p6v), a7r:, i6r, etc.
SIG_PATTERN = re.compile(
    r'(?:\(([a-zA-Z]{1,2}\d[rv])\))'  # parenthesized: (a4r)
    r'|(?:\b([a-zA-Z]{1,2}\d[rv]):)'   # with colon: a4r:
    r'|(?:\b([a-zA-Z]{1,2}\d[rv])\b)'  # bare: a4r (more false positives)
)

# Pattern for quoted marginal text (text in single quotes near a signature ref)
MARGINAL_QUOTE = re.compile(r"['\u2018]([^'\u2019]{3,200})['\u2019]")


def get_chapter(page_num):
    """Determine chapter number from PDF page number."""
    for ch, (start, end) in CHAPTER_RANGES.items():
        if start <= page_num <= end:
            return ch
    return None


def get_manuscript(chapter_num):
    """Get manuscript shelfmark from chapter number."""
    return CHAPTER_MANUSCRIPTS.get(chapter_num)


def extract_context(text, match_start, match_end, window=500):
    """Extract surrounding paragraph context."""
    # Find paragraph boundaries (double newline or start/end of text)
    para_start = text.rfind('\n\n', 0, match_start)
    para_start = para_start + 2 if para_start >= 0 else max(0, match_start - window)

    para_end = text.find('\n\n', match_end)
    para_end = para_end if para_end >= 0 else min(len(text), match_end + window)

    return text[para_start:para_end].strip()


def extract_marginal_text(context, sig_pos):
    """Find quoted text near a signature reference."""
    quotes = list(MARGINAL_QUOTE.finditer(context))
    if not quotes:
        return None

    # Find the quote closest to the signature reference
    closest = min(quotes, key=lambda m: abs(m.start() - sig_pos))
    return closest.group(1)


def main():
    if not THESIS_PATH.exists():
        print(f"ERROR: Thesis not found at {THESIS_PATH}")
        return

    print(f"Opening {THESIS_FILENAME}...")
    doc = fitz.open(str(THESIS_PATH))
    total_pages = len(doc)
    print(f"  {total_pages} pages")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Clear existing refs
    cur.execute("DELETE FROM dissertation_refs")

    ref_count = 0
    all_sigs = set()

    for page_idx in range(total_pages):
        page = doc[page_idx]
        text = page.get_text()
        page_num = page_idx + 1  # 1-indexed

        for match in SIG_PATTERN.finditer(text):
            # Get the matched signature from whichever group matched
            sig = match.group(1) or match.group(2) or match.group(3)
            if not sig:
                continue

            # Skip very short matches that are likely false positives
            # (e.g., "in" + digit + r/v)
            quire_part = re.match(r'([a-zA-Z]+)', sig).group(1)
            if quire_part.lower() in ('in', 'an', 'on', 'or', 'as', 'at', 'is', 'it',
                                       'no', 'so', 'to', 'do', 'go', 'he', 'me', 'we',
                                       'be', 'of', 'if', 'up', 'my', 'by'):
                continue

            all_sigs.add(sig)
            chapter = get_chapter(page_num)
            manuscript = get_manuscript(chapter)

            context = extract_context(text, match.start(), match.end())
            marginal = extract_marginal_text(context, match.start() - (text.rfind('\n\n', 0, match.start()) or 0))

            cur.execute(
                """INSERT INTO dissertation_refs
                   (thesis_page, signature_ref, manuscript_shelfmark,
                    context_text, marginal_text, ref_type, chapter_num)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (page_num, sig, manuscript, context, marginal, 'MARGINALIA', chapter)
            )
            ref_count += 1

    conn.commit()
    doc.close()

    print(f"\nExtracted {ref_count} references")
    print(f"Unique signatures: {len(all_sigs)}")

    # Show distribution by chapter
    print("\nReferences by chapter:")
    for ch in range(1, 11):
        cur.execute("SELECT COUNT(*) FROM dissertation_refs WHERE chapter_num = ?", (ch,))
        count = cur.fetchone()[0]
        ms = CHAPTER_MANUSCRIPTS.get(ch, '')
        if count > 0:
            print(f"  Ch {ch} ({ms}): {count} refs")

    # Show sample references
    print("\nSample references:")
    cur.execute("""SELECT thesis_page, signature_ref, manuscript_shelfmark,
                   substr(context_text, 1, 100), marginal_text
                   FROM dissertation_refs LIMIT 10""")
    for row in cur.fetchall():
        page, sig, ms, ctx, marg = row
        print(f"  p.{page} {sig} [{ms}]: {ctx}...")
        if marg:
            print(f"    Marginal text: '{marg[:80]}'")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
