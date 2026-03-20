"""Consolidate dissertation_refs into the annotations table.

Migrates 282 dissertation_refs into the canonical annotations table,
mapping fields and resolving manuscript_shelfmark to manuscript_id.

Also runs a regex hand attribution pass on unattributed refs by
searching thesis chunks for "Hand [A-E]" near signature references.

Idempotent: checks for existing rows before inserting.
"""

import sqlite3
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"
CHUNKS_DIR = BASE_DIR / "chunks" / "PhD_Thesis_James_Russell_Hypnerotomachia_Polyphili"


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("=== Consolidating Annotations ===\n")

    # Step 1: Build manuscript_id lookup
    cur.execute("SELECT id, shelfmark FROM manuscripts")
    ms_ids = {row[1]: row[0] for row in cur.fetchall()}

    # Also check hp_copies for additional shelfmarks
    cur.execute("SELECT id, shelfmark FROM hp_copies")
    copy_ids = {row[1]: row[0] for row in cur.fetchall()}

    # Step 2: Get all dissertation_refs
    cur.execute("""
        SELECT id, thesis_page, signature_ref, manuscript_shelfmark,
               context_text, marginal_text, source_text, ref_type,
               chapter_num, hand_id
        FROM dissertation_refs ORDER BY id
    """)
    refs = cur.fetchall()

    # Step 3: Check what's already in annotations
    cur.execute("SELECT thesis_page, signature_ref FROM annotations")
    existing = set((row[0], row[1]) for row in cur.fetchall())

    # Step 4: Parse signature to get folio_number and side
    def parse_sig(sig):
        if not sig:
            return None, None
        m = re.match(r'([a-zA-Z]+)(\d+)([rv])?', sig)
        if m:
            return int(m.group(2)), m.group(3)
        return None, None

    # Step 5: Migrate
    migrated = 0
    for ref in refs:
        (rid, thesis_page, sig_ref, ms_shelfmark, context, marginal,
         source, ref_type, chapter, hand_id) = ref

        # Skip if already exists
        if (thesis_page, sig_ref) in existing:
            continue

        # Resolve manuscript_id
        ms_id = ms_ids.get(ms_shelfmark)

        # Parse signature
        folio_num, side = parse_sig(sig_ref)

        # Map ref_type to annotation_type CHECK constraint
        type_map = {
            'MARGINALIA': 'MARGINAL_NOTE',
            'ILLUSTRATION': 'DRAWING',
            'TEXT': 'LABEL',
            'BINDING': 'OTHER',
            'PROVENANCE': 'PROVENANCE',
        }
        ann_type = type_map.get(ref_type, 'OTHER')

        # Determine source_method
        source_method = 'PDF_EXTRACTION'

        cur.execute("""
            INSERT INTO annotations
                (manuscript_id, hand_id, signature_ref, folio_number, side,
                 annotation_text, annotation_type, thesis_page, thesis_chapter,
                 confidence, needs_review, source_method, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'MEDIUM', 1, ?, ?)
        """, (ms_id, hand_id, sig_ref, folio_num, side,
              marginal, ann_type, thesis_page, chapter,
              source_method, context))
        migrated += 1

    conn.commit()
    print(f"  Migrated {migrated} refs into annotations table")

    # Step 6: Regex hand attribution pass
    print("\nStep 2: Regex hand attribution pass...")

    # Get unattributed annotations
    cur.execute("""
        SELECT id, thesis_page, signature_ref, notes, thesis_chapter
        FROM annotations WHERE hand_id IS NULL
    """)
    unattributed = cur.fetchall()

    # Get hand IDs by label+manuscript
    cur.execute("SELECT id, hand_label, manuscript_shelfmark FROM annotator_hands")
    hands = cur.fetchall()

    # Build chapter-to-manuscript mapping from Russell's thesis structure
    # Ch. 4 = Modena (Giovio), Ch. 5 = Cambridge (Giovio),
    # Ch. 6 = BL, Ch. 7 = Buffalo, Ch. 8 = Vatican, Ch. 9 = Siena
    chapter_ms = {
        4: 'Modena (Panini)',
        5: 'INCUN A.5.13',
        6: 'C.60.o.12',
        7: 'Buffalo RBR',
        8: 'Inc.Stam.Chig.II.610',
        9: 'O.III.38',
    }

    # For chapters 4-9, single-hand copies get automatic attribution
    single_hand_chapters = {
        4: ('Primary', 'Modena (Panini)'),
        5: ('Primary', 'INCUN A.5.13'),
        8: ('Primary', 'Inc.Stam.Chig.II.610'),
        9: ('Primary', 'O.III.38'),
    }

    # Build hand_id lookup
    hand_lookup = {}
    for hid, hlabel, hms in hands:
        hand_lookup[(hlabel, hms)] = hid

    attributed = 0
    for ann in unattributed:
        aid, thesis_page, sig_ref, notes, chapter = ann

        # Try chapter-based attribution for single-hand copies
        if chapter in single_hand_chapters:
            hlabel, hms = single_hand_chapters[chapter]
            hid = hand_lookup.get((hlabel, hms))
            if hid:
                cur.execute("UPDATE annotations SET hand_id = ? WHERE id = ?", (hid, aid))
                # Also update dissertation_refs
                cur.execute("""
                    UPDATE dissertation_refs SET hand_id = ?
                    WHERE thesis_page = ? AND signature_ref = ? AND hand_id IS NULL
                """, (hid, thesis_page, sig_ref))
                attributed += 1
                continue

        # For multi-hand copies (Ch. 6 = BL, Ch. 7 = Buffalo), try regex on context
        if chapter in (6, 7) and notes:
            ms = chapter_ms.get(chapter)
            # Search for "Hand [A-E]" pattern
            hand_match = re.search(r'[Hh]and\s+([A-E])\b', notes)
            if hand_match:
                hlabel = hand_match.group(1)
                hid = hand_lookup.get((hlabel, ms))
                if hid:
                    cur.execute("UPDATE annotations SET hand_id = ? WHERE id = ?", (hid, aid))
                    cur.execute("""
                        UPDATE dissertation_refs SET hand_id = ?
                        WHERE thesis_page = ? AND signature_ref = ? AND hand_id IS NULL
                    """, (hid, thesis_page, sig_ref))
                    attributed += 1

    conn.commit()
    print(f"  Attributed {attributed} previously unattributed refs")

    # Summary
    cur.execute("SELECT COUNT(*) FROM annotations")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM annotations WHERE hand_id IS NOT NULL")
    with_hand = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM annotations WHERE hand_id IS NULL")
    without_hand = cur.fetchone()[0]

    print(f"\n=== Summary ===")
    print(f"  Total annotations: {total}")
    print(f"  With hand attribution: {with_hand}")
    print(f"  Without hand attribution: {without_hand}")

    # By type
    cur.execute("SELECT annotation_type, COUNT(*) FROM annotations GROUP BY annotation_type")
    for r in cur.fetchall():
        print(f"    {r[0]}: {r[1]}")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
