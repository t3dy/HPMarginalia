"""Match dissertation references to manuscript images via signature mapping."""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Clear existing matches
    cur.execute("DELETE FROM matches")

    # Get all dissertation refs
    cur.execute("""SELECT id, signature_ref, manuscript_shelfmark, chapter_num
                   FROM dissertation_refs""")
    refs = cur.fetchall()

    stats = {'total': len(refs), 'matched': 0, 'unmatched': 0,
             'high': 0, 'medium': 0, 'low': 0}

    for ref_id, sig_ref, ms_shelfmark, chapter_num in refs:
        # Look up signature in the mapping table
        # Try lowercase first (Russell typically uses lowercase)
        cur.execute("""SELECT folio_number, side FROM signature_map
                       WHERE signature = ? OR signature = ?""",
                    (sig_ref, sig_ref.lower()))
        sig_row = cur.fetchone()

        if not sig_row:
            stats['unmatched'] += 1
            continue

        folio_num, side = sig_row

        # Find matching image(s) for this manuscript
        if ms_shelfmark:
            # Try exact manuscript match
            cur.execute("""
                SELECT i.id FROM images i
                JOIN manuscripts m ON i.manuscript_id = m.id
                WHERE m.shelfmark = ?
                AND i.page_type = 'PAGE'
                AND (i.folio_number = ? OR i.folio_number = ?)
                ORDER BY i.sort_order
            """, (ms_shelfmark, str(folio_num), str(folio_num).zfill(4)))
            image_rows = cur.fetchall()

            if image_rows:
                # If side is specified and Siena images have side info, prefer exact match
                if side and ms_shelfmark == 'O.III.38':
                    cur.execute("""
                        SELECT i.id FROM images i
                        JOIN manuscripts m ON i.manuscript_id = m.id
                        WHERE m.shelfmark = ?
                        AND i.page_type = 'PAGE'
                        AND (i.folio_number = ? OR i.folio_number = ?)
                        AND i.side = ?
                    """, (ms_shelfmark, str(folio_num), str(folio_num).zfill(4), side))
                    exact_side = cur.fetchall()
                    if exact_side:
                        image_rows = exact_side

                for (image_id,) in image_rows:
                    confidence = 'HIGH'
                    method = 'SIGNATURE_EXACT'
                    cur.execute("""
                        INSERT INTO matches (ref_id, image_id, match_method, confidence, needs_review)
                        VALUES (?, ?, ?, ?, ?)
                    """, (ref_id, image_id, method, confidence, 0))
                    stats['matched'] += 1
                    stats['high'] += 1
            else:
                # Try matching across all manuscripts as fallback
                cur.execute("""
                    SELECT i.id, m.shelfmark FROM images i
                    JOIN manuscripts m ON i.manuscript_id = m.id
                    WHERE i.page_type = 'PAGE'
                    AND (i.folio_number = ? OR i.folio_number = ?)
                    ORDER BY i.sort_order
                """, (str(folio_num), str(folio_num).zfill(4)))
                fallback_rows = cur.fetchall()

                if fallback_rows:
                    for image_id, found_ms in fallback_rows:
                        cur.execute("""
                            INSERT INTO matches (ref_id, image_id, match_method, confidence, needs_review)
                            VALUES (?, ?, ?, ?, ?)
                        """, (ref_id, image_id, 'FOLIO_EXACT', 'MEDIUM', 1))
                        stats['matched'] += 1
                        stats['medium'] += 1
                else:
                    stats['unmatched'] += 1
        else:
            stats['unmatched'] += 1

    conn.commit()

    # Print statistics
    print("Match Statistics:")
    print(f"  Total references: {stats['total']}")
    print(f"  Matched: {stats['matched']}")
    print(f"  Unmatched: {stats['unmatched']}")
    print(f"  HIGH confidence: {stats['high']}")
    print(f"  MEDIUM confidence: {stats['medium']}")
    print(f"  LOW confidence: {stats['low']}")

    # Show unmatched refs
    cur.execute("""
        SELECT dr.id, dr.thesis_page, dr.signature_ref, dr.manuscript_shelfmark
        FROM dissertation_refs dr
        WHERE dr.id NOT IN (SELECT ref_id FROM matches)
        LIMIT 20
    """)
    unmatched = cur.fetchall()
    if unmatched:
        print(f"\nUnmatched references (first 20):")
        for ref_id, page, sig, ms in unmatched:
            print(f"  ref {ref_id}: p.{page} {sig} [{ms}]")

    # Show sample matches
    print("\nSample matches:")
    cur.execute("""
        SELECT dr.thesis_page, dr.signature_ref, dr.manuscript_shelfmark,
               i.filename, m.confidence
        FROM matches m
        JOIN dissertation_refs dr ON m.ref_id = dr.id
        JOIN images i ON m.image_id = i.id
        LIMIT 10
    """)
    for page, sig, ms, img_file, conf in cur.fetchall():
        print(f"  p.{page} {sig} [{ms}] -> {img_file} ({conf})")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
