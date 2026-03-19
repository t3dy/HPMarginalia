"""Link scholars to bibliography entries and summaries.json.

Step 1 of the Scholar Pipeline (docs/SCHOLAR_PIPELINE.md).

This script:
1. Adds missing columns (scholar_overview, is_historical_subject, has_summary, summary_source)
2. Tags historical figures
3. Matches summaries.json -> bibliography by author+title
4. Sets has_summary flags on scholar_works
5. Logs unmatched entries

Idempotent and non-destructive.
"""

import sqlite3
import json
import re
import unicodedata
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"
SUMMARIES_PATH = BASE_DIR / "scholars" / "summaries.json"
STAGING_DIR = BASE_DIR / "staging" / "scholar"

# Historical figures: HP subjects, not modern scholars
HISTORICAL_FIGURES = [
    "Francesco Colonna",
    "Aldus Manutius",
    "Ben Jonson",
    "Fabio Chigi (Pope Alexander VII)",
    "Benedetto Giovio",
    "Paolo Giovio",
    "Jean Martin",
    "Beroalde de Verville",
    "Charles Nodier",
    "Pope Alexander VII",
]


def normalize_name(name):
    """Normalize a name for comparison: lowercase, strip periods, collapse spaces."""
    if not name:
        return ''
    s = name.lower().strip()
    # Remove accents for comparison
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    # Strip periods
    s = s.replace('.', '')
    # Collapse whitespace
    s = re.sub(r'\s+', ' ', s)
    return s


def normalize_title(title):
    """Normalize a title for comparison."""
    if not title:
        return ''
    s = title.lower().strip()
    # Remove common prefixes
    s = re.sub(r'^(the|a|an)\s+', '', s)
    # Remove punctuation
    s = re.sub(r'[^\w\s]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s[:80]  # First 80 chars for matching


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("=== Scholar Linking Pipeline ===\n")

    # Step 1: Add missing columns
    print("Step 1: Adding missing columns...")
    existing_scholar_cols = {r[1] for r in cur.execute("PRAGMA table_info(scholars)")}
    existing_sw_cols = {r[1] for r in cur.execute("PRAGMA table_info(scholar_works)")}

    if 'scholar_overview' not in existing_scholar_cols:
        cur.execute("ALTER TABLE scholars ADD COLUMN scholar_overview TEXT")
        print("  Added scholars.scholar_overview")
    if 'is_historical_subject' not in existing_scholar_cols:
        cur.execute("ALTER TABLE scholars ADD COLUMN is_historical_subject BOOLEAN DEFAULT 0")
        print("  Added scholars.is_historical_subject")
    if 'has_summary' not in existing_sw_cols:
        cur.execute("ALTER TABLE scholar_works ADD COLUMN has_summary BOOLEAN DEFAULT 0")
        print("  Added scholar_works.has_summary")
    if 'summary_source' not in existing_sw_cols:
        cur.execute("ALTER TABLE scholar_works ADD COLUMN summary_source TEXT")
        print("  Added scholar_works.summary_source")
    conn.commit()

    # Step 2: Tag historical figures
    print("\nStep 2: Tagging historical figures...")
    tagged = 0
    for hist_name in HISTORICAL_FIGURES:
        norm = normalize_name(hist_name)
        cur.execute("SELECT id, name FROM scholars")
        for sid, sname in cur.fetchall():
            if normalize_name(sname) == norm or norm in normalize_name(sname):
                cur.execute("UPDATE scholars SET is_historical_subject = 1 WHERE id = ?", (sid,))
                if cur.rowcount:
                    tagged += 1
                    print(f"  Tagged: {sname}")
    conn.commit()
    print(f"  {tagged} historical figures tagged")

    # Step 3: Load summaries and match to bibliography
    print("\nStep 3: Matching summaries.json to bibliography...")
    summaries = []
    if SUMMARIES_PATH.exists():
        with open(SUMMARIES_PATH, encoding='utf-8') as f:
            summaries = json.load(f)

    # Get all bibliography entries
    cur.execute("SELECT id, author, title, year FROM bibliography")
    bib_entries = cur.fetchall()

    # Build normalized lookup
    bib_lookup = {}
    for bid, bauthor, btitle, byear in bib_entries:
        key = (normalize_name(bauthor), normalize_title(btitle))
        bib_lookup[key] = bid

    matched_summaries = 0
    unmatched_summaries = []

    for s in summaries:
        s_author = s.get('author', '')
        s_title = s.get('title', '')
        s_key = (normalize_name(s_author), normalize_title(s_title))

        # Try exact match first
        bib_id = bib_lookup.get(s_key)

        # Try partial title match if no exact
        if not bib_id:
            norm_author = normalize_name(s_author)
            norm_title = normalize_title(s_title)
            for (ba, bt), bid in bib_lookup.items():
                if norm_author == ba and (norm_title[:30] in bt or bt[:30] in norm_title):
                    bib_id = bid
                    break

        if bib_id:
            matched_summaries += 1
            # Find the scholar for this author
            cur.execute("SELECT id FROM scholars WHERE LOWER(name) = LOWER(?)", (s_author,))
            scholar = cur.fetchone()
            if scholar:
                # Update scholar_works with has_summary
                cur.execute("""
                    UPDATE scholar_works SET has_summary = 1, summary_source = 'summaries.json'
                    WHERE scholar_id = ? AND bib_id = ?
                """, (scholar[0], bib_id))
                if cur.rowcount == 0:
                    # Link might not exist, create it
                    cur.execute("""
                        INSERT OR IGNORE INTO scholar_works (scholar_id, bib_id, has_summary, summary_source)
                        VALUES (?, ?, 1, 'summaries.json')
                    """, (scholar[0], bib_id))
        else:
            unmatched_summaries.append({
                'author': s_author,
                'title': s_title,
                'reason': 'no bibliography match found',
            })

    conn.commit()
    print(f"  Matched: {matched_summaries}/{len(summaries)} summaries to bibliography")
    print(f"  Unmatched: {len(unmatched_summaries)}")

    # Step 4: Log unmatched
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    unmatched_path = STAGING_DIR / "unmatched.json"
    with open(unmatched_path, 'w', encoding='utf-8') as f:
        json.dump({
            'unmatched_summaries': unmatched_summaries,
            'summary_match_rate': f"{matched_summaries}/{len(summaries)}",
        }, f, indent=2, ensure_ascii=False)
    print(f"\n  Unmatched log: {unmatched_path}")

    # Step 5: Report
    cur.execute("SELECT COUNT(*) FROM scholars WHERE is_historical_subject = 1")
    hist_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM scholars WHERE is_historical_subject = 0 OR is_historical_subject IS NULL")
    modern_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM scholar_works WHERE has_summary = 1")
    with_summary = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM scholar_works")
    total_links = cur.fetchone()[0]

    print(f"\n=== Summary ===")
    print(f"  Historical figures: {hist_count}")
    print(f"  Modern scholars: {modern_count}")
    print(f"  Scholar-work links: {total_links}")
    print(f"  Links with summaries: {with_summary}")
    print(f"  Summary match rate: {matched_summaries}/{len(summaries)}")

    conn.close()


if __name__ == "__main__":
    main()
