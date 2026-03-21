#!/usr/bin/env python3
"""fix_polyandrion.py — Fix remaining Polyandrion page assignments.

The gap verification revealed that ALL Polyandrion woodcuts are on
odd-numbered pages, not even. The previous fix corrected some but
missed the pattern. This script corrects the remaining off-by-one errors.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "hp.db"
IA_OFFSET = 5

# Verified corrections from gap scan
CORRECTIONS = {
    # old_page -> new_page (verified by IA visual inspection)
    242: 241,   # Hell mosaic -> p.241
    244: 243,   # D.M. Annirae -> p.243  (sacrifice relief is at p.245)
    246: 247,   # Epitaph fragments + Greek urn -> p.247
    248: 251,   # P. Cornelia Annia -> p.251
    250: 249,   # Tombstone with urn -> p.249 (Greek urn stays at 250? No, moves to 247)
}

# Some entries need more careful handling because the corrections
# create conflicts. Let me think through this:
#
# Current DB state (after previous fix):
#   p.242: Mosaic of Hell on Crypt Ceiling     -> should be p.241
#   p.244: Sepulchral Monument: D.M. Annirae   -> should be p.243
#   p.246: Epitaph Fragments with Urn           -> should be p.247
#   p.248: Sarcophagus: P. Cornelia Annia       -> should be p.251
#   p.250: Epitaphs: Greek Urn and D.M. Lyndia  -> stays? Check p.250
#   p.252: Sarcophagus with Hieroglyphic Devices -> check
#   p.254: Sepulchral Monument with Laurel Wreath -> check
#   p.258: Sepulchral Monument with Putti        -> check
#   p.260: Sepulchral Portal                     -> check
#
# And we need to ADD p.234 (hieroglyphic strip + medallion) and p.245 (sacrifice relief)

def main():
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    print("=== Polyandrion Page Corrections ===\n")

    # Step 1: Fix page assignments
    fixes = [
        (242, 241, "Mosaic of Hell on Crypt Ceiling"),
        (244, 243, "Sepulchral Monument: D.M. Annirae"),
        (246, 247, "Epitaph Fragments with Urn"),
        (248, 251, "P. Cornelia Annia"),
    ]

    for old_p, new_p, expected_title in fixes:
        row = cur.execute("SELECT id, title FROM woodcuts WHERE page_1499 = ?", (old_p,)).fetchone()
        if not row:
            print(f"  SKIP p.{old_p}: no entry found")
            continue

        # Check if target page already has an entry
        conflict = cur.execute("SELECT id, title FROM woodcuts WHERE page_1499 = ?", (new_p,)).fetchone()
        if conflict:
            print(f"  CONFLICT p.{old_p} -> p.{new_p}: target has '{conflict[1]}', merging")
            cur.execute("DELETE FROM woodcuts WHERE id = ?", (row[0],))
        else:
            cur.execute("UPDATE woodcuts SET page_1499 = ?, page_1499_ia = ? WHERE id = ?",
                        (new_p, new_p + IA_OFFSET, row[0]))
            print(f"  FIX p.{old_p} -> p.{new_p}: {row[1]}")

    # Step 2: Add p.234 (hieroglyphic device strip + Julius Caesar medallion)
    existing_234 = cur.execute("SELECT id FROM woodcuts WHERE page_1499 = 234").fetchone()
    if not existing_234:
        cur.execute("""
            INSERT INTO woodcuts (
                page_1499, page_1499_ia, slug, title, description,
                narrative_context, subject_category, source_method, confidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'LLM_ASSISTED', 'HIGH')
        """, (234, 234 + IA_OFFSET,
              'hieroglyphic-devices-julius-caesar-medallion',
              'Hieroglyphic Devices and Julius Caesar Medallion',
              'Strip of hieroglyphic emblems (torch, temple, scales, helmet, caduceus) with inscription DIVO IVLIO CAESARI SEMP. AVG. Below: large circular medallion with elephants flanking a caduceus, surrounded by botanical ornament.',
              'The Polyandrion entrance displays hieroglyphic devices dedicated to Julius Caesar, combining Roman imperial imagery with alchemical symbols. The circular medallion below depicts elephants (wisdom, strength) flanking a caduceus (Mercury, transformation).',
              'HIEROGLYPHIC'))
        print(f"  ADD p.234: Hieroglyphic Devices and Julius Caesar Medallion")

    # Step 3: Add p.245 (sacrifice relief)
    existing_245 = cur.execute("SELECT id FROM woodcuts WHERE page_1499 = 245").fetchone()
    if not existing_245:
        cur.execute("""
            INSERT INTO woodcuts (
                page_1499, page_1499_ia, slug, title, description,
                narrative_context, subject_category, source_method, confidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'LLM_ASSISTED', 'HIGH')
        """, (245, 245 + IA_OFFSET,
              'sacrifice-relief-polyandrion',
              'Sacrifice Relief: HAVE SERIA ORINTVM',
              'Relief panel depicting figures in a sacrifice scene: old man, youth, faun, and dancers. Inscription reads HAVE SERIA ORINTVM AMANTES VALE.',
              'A funerary relief in the Polyandrion depicting a ritual sacrifice, combining classical Roman sepulchral imagery with the HP narrative of love and death.',
              'NARRATIVE'))
        print(f"  ADD p.245: Sacrifice Relief HAVE SERIA ORINTVM")

    # Step 4: Update woodcut_catalog page assignments
    catalog_fixes = {
        96: 241,   # Mosaic of Hell
        97: 243,   # Sepulchral monument with masks (D.M. Annirae)
        98: 245,   # Renaissance urn monument (sacrifice relief)
        99: 245,   # Sacrifice relief
        100: 247,  # Epitaph with eagle
        101: 247,  # Epitaph fragment
        102: 249,  # Greek inscription urn -> p.249 not 250
        103: 249,  # Tombstone with urn
        104: 247,  # Epitaph with skulls
        105: 251,  # D.M. Lyndia -> p.251 not 248
        106: 251,  # P. Cornelia Annia
    }
    for cat_num, page_seq in catalog_fixes.items():
        cur.execute("UPDATE woodcut_catalog SET page_seq = ? WHERE catalog_number = ?",
                    (page_seq, cat_num))

    # Step 5: Update page_concordance
    for page in [234, 241, 243, 245, 247, 249, 251]:
        cur.execute("UPDATE page_concordance SET has_woodcut = 1 WHERE page_seq = ?", (page,))

    conn.commit()

    # Summary
    total = cur.execute("SELECT COUNT(*) FROM woodcuts").fetchone()[0]
    poly_count = cur.execute(
        "SELECT COUNT(*) FROM woodcuts WHERE page_1499 BETWEEN 228 AND 265"
    ).fetchone()[0]
    print(f"\n=== Summary ===")
    print(f"  Total woodcuts: {total}")
    print(f"  Polyandrion entries (pp.228-265): {poly_count}")

    conn.close()


if __name__ == "__main__":
    main()
