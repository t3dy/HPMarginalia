"""Rebuild all BL matches from scratch using corrected folio numbers.

The original 218 LOW matches were built with wrong folio assumptions
(photo N = folio N, but actually photo N = folio N-13). This script:
1. Deletes all existing BL matches
2. Rebuilds matches using corrected image folio numbers
3. Assigns confidence based on verification status
"""

import sqlite3
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"

BL_OFFSET = 13

# Pages verified by visual inspection
VERIFIED_PAGES = {
    14:1, 15:2, 18:5, 20:7, 25:12, 30:17, 32:19, 33:20,
    35:22, 40:27, 41:28, 42:29, 45:32, 50:37, 55:42,
    60:47, 70:57, 77:64, 78:65, 80:67, 90:77,
    100:87, 110:97, 120:107, 140:127, 150:137, 170:157,
}


def signature_to_page(sig):
    """Convert a signature to a page number using the 1499/1545 collation."""
    m = re.match(r'([a-zA-Z])(\d+)([rv])', sig)
    if not m:
        return None, None
    ql, leaf, side = m.group(1), int(m.group(2)), m.group(3)

    quires = [c for c in 'abcdefghiklmnopqrstxyz']
    upper = list('ABCDEFG')
    all_q = quires + upper

    if ql not in all_q:
        return None, None

    qi = all_q.index(ql)
    total_leaf = qi * 8 + leaf
    page = (total_leaf - 1) * 2 + (1 if side == 'r' else 2)
    return page, side


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("=== Rebuilding BL Matches ===\n")

    # Get BL manuscript ID
    cur.execute("SELECT id FROM manuscripts WHERE shelfmark = 'C.60.o.12'")
    bl_id = cur.fetchone()[0]

    # Step 1: Delete all existing BL matches
    cur.execute("""
        DELETE FROM matches WHERE image_id IN (
            SELECT id FROM images WHERE manuscript_id = ?
        )
    """, (bl_id,))
    deleted = cur.rowcount
    print(f"Step 1: Deleted {deleted} old BL matches")

    # Step 2: Build image lookup by (folio_number, side)
    cur.execute("""
        SELECT id, filename, folio_number, side FROM images
        WHERE manuscript_id = ? AND page_type = 'PAGE'
        AND folio_number IS NOT NULL
    """, (bl_id,))
    img_by_folio = {}
    for row in cur.fetchall():
        img_id, fname, fnum, side = row
        key = (str(fnum), side)
        img_by_folio[key] = (img_id, fname)

    # Step 3: Get all BL dissertation refs
    cur.execute("""
        SELECT id, signature_ref FROM dissertation_refs
        WHERE manuscript_shelfmark = 'C.60.o.12' AND signature_ref IS NOT NULL
    """)
    bl_refs = cur.fetchall()
    print(f"Step 2: {len(bl_refs)} BL dissertation refs to match")

    # Step 4: Create new matches
    matched = 0
    high = 0
    medium = 0
    unmatched = []

    for ref_id, sig_ref in bl_refs:
        page, side = signature_to_page(sig_ref)
        if page is None:
            unmatched.append((ref_id, sig_ref, "invalid signature"))
            continue

        # Check if this page is within photo range
        photo_num = page + BL_OFFSET
        if photo_num > 189 or photo_num < 14:
            unmatched.append((ref_id, sig_ref, f"page {page} outside photo range"))
            continue

        # Compute leaf number and side
        leaf_num = (page + 1) // 2
        computed_side = 'r' if page % 2 == 1 else 'v'

        # Find matching image
        key = (str(leaf_num), computed_side)
        img_data = img_by_folio.get(key)

        if not img_data:
            # Try without side match
            for s in ['r', 'v']:
                alt_key = (str(leaf_num), s)
                img_data = img_by_folio.get(alt_key)
                if img_data:
                    break

        if img_data:
            img_id, fname = img_data
            # Determine confidence
            if photo_num in VERIFIED_PAGES:
                conf = 'HIGH'
                high += 1
            else:
                conf = 'MEDIUM'
                medium += 1

            cur.execute("""
                INSERT OR IGNORE INTO matches
                    (ref_id, image_id, match_method, confidence, needs_review, source_method)
                VALUES (?, ?, 'FOLIO_EXACT', ?, 0, 'DETERMINISTIC')
            """, (ref_id, img_id, conf))
            matched += 1
        else:
            unmatched.append((ref_id, sig_ref, f"no image for leaf {leaf_num}{computed_side}"))

    conn.commit()

    # Summary
    print(f"\nStep 3: Results")
    print(f"  Matched: {matched}")
    print(f"  HIGH confidence: {high}")
    print(f"  MEDIUM confidence: {medium}")
    print(f"  Unmatched: {len(unmatched)}")
    if unmatched:
        print(f"  Unmatched reasons:")
        reasons = {}
        for _, sig, reason in unmatched:
            reasons[reason] = reasons.get(reason, 0) + 1
        for reason, count in sorted(reasons.items(), key=lambda x: -x[1]):
            print(f"    {reason}: {count}")

    # Overall match stats
    cur.execute("SELECT confidence, COUNT(*) FROM matches GROUP BY confidence ORDER BY confidence")
    print(f"\nAll matches after rebuild:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
