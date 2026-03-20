"""Classify annotations by type based on hand and content analysis.

Uses deterministic rules where possible:
- All alchemist-hand refs -> SYMBOL
- Refs with marginal_text containing Latin/Greek -> MARGINAL_NOTE
- Refs mentioning "underline" in context -> UNDERLINE
- Refs mentioning "cross-reference" or "source" -> CROSS_REFERENCE

Falls back to MARGINAL_NOTE for unclassifiable refs.
"""

import sqlite3
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("=== Classifying Annotation Types ===\n")

    # Get alchemist hand IDs
    cur.execute("SELECT id FROM annotator_hands WHERE is_alchemist = 1")
    alchemist_ids = set(r[0] for r in cur.fetchall())

    # Get all annotations with context
    cur.execute("""
        SELECT a.id, a.hand_id, a.annotation_text, a.notes, a.annotation_type
        FROM annotations a ORDER BY a.id
    """)
    annotations = cur.fetchall()

    updated = 0
    type_counts = {}

    for ann in annotations:
        aid, hand_id, ann_text, notes, current_type = ann
        context = (notes or '') + ' ' + (ann_text or '')
        context_lower = context.lower()

        new_type = None

        # Alchemist hands -> SYMBOL
        if hand_id in alchemist_ids:
            new_type = 'SYMBOL'
        # Check for source identification patterns
        elif re.search(r'(plin|vitruvius|ovid|virgil|plato|aristotle|cicero)', context_lower):
            new_type = 'CROSS_REFERENCE'
        # Check for underline mentions
        elif 'underlin' in context_lower:
            new_type = 'UNDERLINE'
        # Check for provenance
        elif re.search(r'(ex libris|ownership|bought|purchased|donated)', context_lower):
            new_type = 'PROVENANCE'
        # Check for index/label patterns
        elif re.search(r'(index|nota|nb|label)', context_lower):
            new_type = 'INDEX_ENTRY'
        # Check for emendation
        elif re.search(r'(correct|emend|sic|error)', context_lower):
            new_type = 'EMENDATION'
        # Default: keep as MARGINAL_NOTE
        else:
            new_type = 'MARGINAL_NOTE'

        if new_type and new_type != current_type:
            cur.execute("UPDATE annotations SET annotation_type = ? WHERE id = ?",
                        (new_type, aid))
            updated += 1

        type_counts[new_type] = type_counts.get(new_type, 0) + 1

    conn.commit()

    print(f"  Reclassified {updated} annotations")
    print(f"\n  Type distribution:")
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"    {t}: {c}")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
