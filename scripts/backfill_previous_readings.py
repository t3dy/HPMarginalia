"""Backfill 27 previous image readings into image_readings table.

These readings were performed manually during the 2026-03-20 session
and documented in docs/archive/IMAGEIDENTIFICATION.md. This script
converts them into structured image_readings rows (phase=0, historical).
"""

import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"

# The 27 BL photos that were read, with extracted data.
# Source: docs/archive/IMAGEIDENTIFICATION.md + READINGIMAGES.md
#
# Photo numbers and what was observed:
READINGS = [
    # Pre-text pages (photos 001-013)
    {"photo": 1, "page_read": None, "page_type": "COVER", "has_woodcut": False,
     "density": None, "has_annotations": False, "notes": "Blank endpaper"},
    {"photo": 2, "page_read": None, "page_type": "GUARD", "has_woodcut": False,
     "density": "HEAVY", "has_annotations": True,
     "notes": "Flyleaf recto — Thomas Bourne's provenance notes (1641)"},
    {"photo": 3, "page_read": None, "page_type": "GUARD", "has_woodcut": False,
     "density": "HEAVY", "has_annotations": True,
     "notes": "Flyleaf verso — Master Mercury declaration. Hand B alchemist text: "
              "'verus sensus intentionis huius libri est 3um'"},
    {"photo": 7, "page_read": None, "page_type": "OTHER", "has_woodcut": False,
     "density": "HEAVY", "has_annotations": True,
     "notes": "Prefatory verse (part 2, 'Finis') — annotated"},
    {"photo": 8, "page_read": None, "page_type": "OTHER", "has_woodcut": False,
     "density": "HEAVY", "has_annotations": True,
     "notes": "Argomento/summary — the most heavily annotated page"},
    {"photo": 9, "page_read": None, "page_type": "OTHER", "has_woodcut": False,
     "density": "HEAVY", "has_annotations": True,
     "notes": "Prefatory poem — annotated"},
    # Text pages (photo - 13 = page number)
    {"photo": 14, "page_read": 1, "page_type": "TEXT", "has_woodcut": False,
     "density": "HEAVY", "has_annotations": True,
     "notes": "a1r. Marginal annotations visible in right margin and bottom. "
              "Consistent with Russell's Hand A (Jonson) and Hand B (alchemist)."},
    {"photo": 20, "page_read": 7, "page_type": "TEXT", "has_woodcut": False,
     "density": "HEAVY", "has_annotations": True, "notes": "Page 7 verified."},
    {"photo": 25, "page_read": 12, "page_type": "TEXT", "has_woodcut": False,
     "density": "HEAVY", "has_annotations": True, "notes": "Page 12 verified."},
    {"photo": 30, "page_read": 17, "page_type": "TEXT", "has_woodcut": False,
     "density": "HEAVY", "has_annotations": True, "notes": "Page 17 verified."},
    {"photo": 33, "page_read": 20, "page_type": "TEXT", "has_woodcut": False,
     "density": "HEAVY", "has_annotations": True,
     "notes": "Page 20. Alchemical symbols visible in left margin."},
    {"photo": 35, "page_read": 22, "page_type": "TEXT", "has_woodcut": True,
     "density": None, "has_annotations": False,
     "woodcut": "Horse and rider/figure on sarcophagus",
     "notes": "b3v. Woodcut detected."},
    {"photo": 40, "page_read": 27, "page_type": "TEXT", "has_woodcut": True,
     "density": "HEAVY", "has_annotations": True,
     "woodcut": "Inscription monument (ΓΟΝΟΣ ΚΑΙ ΕΤΟΥΣΙΑ)",
     "notes": "b6r. Woodcut + heavy annotations."},
    {"photo": 41, "page_read": 28, "page_type": "TEXT", "has_woodcut": True,
     "density": "HEAVY", "has_annotations": True,
     "woodcut": "Elephant and Obelisk",
     "notes": "b6v. Densest alchemical annotation site per Russell Ch. 6. "
              "Annotations above, right margin, below woodcut. Fragment: 'bellua'."},
    {"photo": 42, "page_read": 29, "page_type": "TEXT", "has_woodcut": True,
     "density": "HEAVY", "has_annotations": True,
     "woodcut": "Figure on monument with Greek inscription",
     "notes": "b7r. Woodcut + annotations."},
    {"photo": 45, "page_read": 32, "page_type": "TEXT", "has_woodcut": False,
     "density": "HEAVY", "has_annotations": True, "notes": "Page 32 verified."},
    {"photo": 50, "page_read": 37, "page_type": "TEXT", "has_woodcut": False,
     "density": "LIGHT", "has_annotations": False, "notes": "Page 37. Minimal annotations."},
    {"photo": 55, "page_read": 42, "page_type": "TEXT", "has_woodcut": False,
     "density": "HEAVY", "has_annotations": True,
     "notes": "c5v. Greek inscription to Aphrodite/Dionysos/Demeter. "
              "Alchemical symbols visible at bottom. NEW ALCHEMICAL SITE — "
              "not previously in database. PROVISIONAL."},
    {"photo": 60, "page_read": 47, "page_type": "TEXT", "has_woodcut": False,
     "density": "MODERATE", "has_annotations": True, "notes": "Page 47 verified."},
    {"photo": 70, "page_read": 57, "page_type": "TEXT", "has_woodcut": False,
     "density": "LIGHT", "has_annotations": False, "notes": "Page 57. Minimal annotations."},
    {"photo": 77, "page_read": 64, "page_type": "TEXT", "has_woodcut": False,
     "density": "MODERATE", "has_annotations": True, "notes": "Page 64 verified."},
    {"photo": 78, "page_read": 65, "page_type": "TEXT", "has_woodcut": False,
     "density": "MODERATE", "has_annotations": True, "notes": "Page 65 verified."},
    {"photo": 80, "page_read": 67, "page_type": "TEXT", "has_woodcut": False,
     "density": "MODERATE", "has_annotations": True, "notes": "Page 67 verified."},
    {"photo": 90, "page_read": 77, "page_type": "TEXT", "has_woodcut": False,
     "density": "LIGHT", "has_annotations": False, "notes": "Page 77. Minimal annotations."},
    {"photo": 100, "page_read": 87, "page_type": "TEXT", "has_woodcut": True,
     "density": "MODERATE", "has_annotations": True,
     "woodcut": "Grotesque frieze with hybrid figures",
     "notes": "f4r. Decorative woodcut frieze + marginal annotations in right margin."},
    {"photo": 110, "page_read": 97, "page_type": "TEXT", "has_woodcut": False,
     "density": "MODERATE", "has_annotations": True,
     "notes": "Page 97. Confirmed signature 'g ii' at page foot."},
    {"photo": 120, "page_read": 107, "page_type": "TEXT", "has_woodcut": False,
     "density": "MODERATE", "has_annotations": True, "notes": "Page 107 verified."},
    {"photo": 140, "page_read": 127, "page_type": "TEXT", "has_woodcut": True,
     "density": "HEAVY", "has_annotations": True,
     "woodcut": "Figures at portal/doorway",
     "notes": "h8r. 'Synostra Gloria mundi' above woodcut. NEW ALCHEMICAL SITE — "
              "possibly Hand B. PROVISIONAL."},
    {"photo": 150, "page_read": 137, "page_type": "TEXT", "has_woodcut": False,
     "density": "MODERATE", "has_annotations": True, "notes": "Page 137 verified."},
    {"photo": 170, "page_read": 157, "page_type": "TEXT", "has_woodcut": True,
     "density": "MODERATE", "has_annotations": True,
     "woodcut": "Triumphal procession",
     "notes": "k5r. Large woodcut. Right margin has annotations including "
              "'Cortes' and 'Achiopian'."},
]


def find_image_id(conn, photo_number):
    """Find the images.id for a BL photo number."""
    # BL filenames: C_60_o_12-NNN.jpg for sequential scans
    filename = f"C_60_o_12-{photo_number:03d}.jpg"
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM images WHERE filename = ?",
        (filename,)
    )
    row = cur.fetchone()
    if row:
        return row[0]

    # Try alternate naming patterns for non-sequential photos
    cur.execute(
        "SELECT id FROM images WHERE filename LIKE ? AND manuscript_id = "
        "(SELECT id FROM manuscripts WHERE shelfmark = 'C.60.o.12')",
        (f"%{photo_number:03d}%",)
    )
    row = cur.fetchone()
    return row[0] if row else None


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Check if already backfilled
    cur.execute("SELECT COUNT(*) FROM image_readings WHERE phase = 0")
    existing = cur.fetchone()[0]
    if existing > 0:
        print(f"Already have {existing} phase-0 readings. Skipping backfill.")
        conn.close()
        return

    inserted = 0
    skipped = 0
    for r in READINGS:
        image_id = find_image_id(conn, r["photo"])
        if not image_id:
            print(f"  WARNING: No image found for photo {r['photo']}, skipping")
            skipped += 1
            continue

        page_expected = r["photo"] - 13 if r["photo"] > 13 else None
        page_match = (r["page_read"] == page_expected) if (
            r["page_read"] is not None and page_expected is not None
        ) else None

        raw = json.dumps(r, ensure_ascii=False)

        cur.execute("""
            INSERT INTO image_readings (
                image_id, phase, model, raw_json,
                page_number_read, page_number_expected, page_number_match,
                has_woodcut, woodcut_description,
                has_annotations, annotation_density,
                concordance_status, notes, created_at
            ) VALUES (?, 0, 'claude-opus-4-6-manual', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                      '2026-03-20 00:00:00')
        """, (
            image_id, raw,
            r["page_read"], page_expected, page_match,
            r.get("has_woodcut", False), r.get("woodcut"),
            r.get("has_annotations", False), r.get("density"),
            'CONFIRMED' if page_match else 'UNVERIFIED',
            r["notes"],
        ))
        inserted += 1

    conn.commit()

    # Summary
    cur.execute("SELECT COUNT(*) FROM image_readings WHERE phase = 0")
    total = cur.fetchone()[0]
    cur.execute("""
        SELECT concordance_status, COUNT(*)
        FROM image_readings WHERE phase = 0
        GROUP BY concordance_status
    """)
    statuses = dict(cur.fetchall())

    print(f"\nBackfilled {inserted} readings ({skipped} skipped)")
    print(f"  CONFIRMED: {statuses.get('CONFIRMED', 0)}")
    print(f"  UNVERIFIED: {statuses.get('UNVERIFIED', 0)}")

    cur.execute("""
        SELECT COUNT(*) FROM image_readings
        WHERE phase = 0 AND has_woodcut = 1
    """)
    print(f"  With woodcuts: {cur.fetchone()[0]}")

    cur.execute("""
        SELECT COUNT(*) FROM image_readings
        WHERE phase = 0 AND annotation_density = 'HEAVY'
    """)
    print(f"  HEAVY density: {cur.fetchone()[0]}")

    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()
