"""Add new columns to timeline_events for the Timeline tab.

Adds: category, medium, location, image_ref, confidence.
Idempotent.
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"

NEW_COLUMNS = [
    ("category", "TEXT"),
    ("medium", "TEXT"),
    ("location", "TEXT"),
    ("image_ref", "TEXT"),
    ("confidence", "TEXT DEFAULT 'MEDIUM'"),
]


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(timeline_events)")
    existing = {r[1] for r in cur.fetchall()}

    added = 0
    for col, ctype in NEW_COLUMNS:
        if col not in existing:
            cur.execute(f"ALTER TABLE timeline_events ADD COLUMN {col} {ctype}")
            print(f"  Added: {col}")
            added += 1

    conn.commit()
    conn.close()
    print(f"Done. Added {added} columns.")


if __name__ == "__main__":
    main()
