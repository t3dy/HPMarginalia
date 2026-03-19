"""Extend dictionary_terms schema with new columns for enrichment pipeline.

Adds columns for:
- significance fields (HP-specific and scholarship-wide)
- source document tracking
- source method and notes
- confidence level

Idempotent: safe to run multiple times.
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"

NEW_COLUMNS = [
    ("significance_to_hp", "TEXT"),
    ("significance_to_scholarship", "TEXT"),
    ("related_scholars", "TEXT"),
    ("see_also_text", "TEXT"),
    ("source_documents", "TEXT"),
    ("source_page_refs", "TEXT"),
    ("source_quotes_short", "TEXT"),
    ("source_method", "TEXT"),
    ("confidence", "TEXT DEFAULT 'MEDIUM'"),
    ("notes", "TEXT"),
]


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Get existing columns
    cur.execute("PRAGMA table_info(dictionary_terms)")
    existing = {row[1] for row in cur.fetchall()}

    added = 0
    for col_name, col_type in NEW_COLUMNS:
        if col_name not in existing:
            cur.execute(f"ALTER TABLE dictionary_terms ADD COLUMN {col_name} {col_type}")
            print(f"  Added column: {col_name} ({col_type})")
            added += 1
        else:
            print(f"  Column exists: {col_name}")

    conn.commit()
    conn.close()
    print(f"\nDone. Added {added} new columns.")


if __name__ == "__main__":
    main()
