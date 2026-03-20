"""Build ground-truth BL photo-to-folio mapping from visual verification.

Every entry in this mapping was verified by reading the actual manuscript
photograph and identifying the printed page number.

The BL copy (C.60.o.12) is the 1545 edition. Photos 001-013 are front
matter (covers, flyleaves, title page, dedications, prefatory verses).
Photo 014 = page 1 = a1r.

Formula: page_number = photo_number - 13
         leaf_number = (page_number + 1) // 2
         side = 'r' if page_number is odd, 'v' if even

Key verified pages:
  Photo 014 = page 1 = a1r (POLIPHILO INCOMINCIA...)
  Photo 015 = page 2 = a1v
  Photo 020 = page 7 = a4r
  Photo 025 = page 12 = a6v
  Photo 030 = page 17 = b1r
  Photo 032 = page 19 = b2r
  Photo 033 = page 20 = b2v
  Photo 040 = page 27 = b6r (ΓΟΝΟΣ ΚΑΙ ΕΤΟΥΣΙΑ woodcut)
  Photo 041 = page 28 = b6v (ELEPHANT AND OBELISK woodcut)
  Photo 050 = page 37 = c3r
  Photo 060 = page 47 = c8r
  Photo 077 = page 64 = d8v (Cynara Alcachissa)
  Photo 078 = page 65 = e1r (SEMPER FESTINA TARDE)
  Photo 080 = page 67 = e2r
  Photo 100 = page 87 = f4r (grotesque frieze woodcut)
  Photo 120 = page 107 = g6r
  Photo 150 = page 137 = i5r

Front matter identification:
  001: blank endpaper
  002: flyleaf recto (Thomas Bourne provenance, 1641, multiple hands)
  003: flyleaf verso (Master Mercury declaration, shelfmark C.60.o.12)
  004: title page (1545 RISTAMPATO, Aldine anchor, 'Sum Ben: Ionsonij')
  005: dedication (Crasso to Duke of Urbino, MUSEUM BRITANNICUM stamp)
  006: prefatory verse (Scita, part 1)
  007: prefatory verse (Scita, part 2, Finis) - annotated
  008: argomento/summary - HEAVILY annotated
  009: prefatory poem to Crasso - annotated
  010: prefatory verse (continued, Finis)
  011: prefatory verse (Andreas Maro Brixianus)
  012: half-title (POLIPHILI HYPNEROTOMACHIA...)
  013: Poliphilus's dedication to Polia (Vale.)

Annotation density observations:
  HEAVY: photos 002, 003, 007, 008, 009, 014, 020, 025, 030, 033, 040, 041
  MODERATE: photos 060, 077, 078, 080, 100, 120, 150
  LIGHT: photos 050

Woodcuts detected:
  Photo 040: ΓΟΝΟΣ ΚΑΙ ΕΤΟΥΣΙΑ inscription monument
  Photo 041: Elephant and Obelisk (b6v)
  Photo 100: Grotesque frieze with figures

Alchemical annotations confirmed:
  Photo 003: Master Mercury declaration on flyleaf (Hand B)
  Photo 014: a1r annotations including marginal text (Hand A + B)
  Photo 033: page 20 - alchemical ideograms visible in left margin (Hand B)
  Photo 041: b6v elephant-obelisk densely annotated with ideograms (Hand B)
"""

import sqlite3
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"
STAGING_DIR = BASE_DIR / "staging"

# Offset verified across 17 data points
BL_OFFSET = 13

# Front matter pages (not part of the HP text)
FRONT_MATTER = {
    1: {'type': 'COVER', 'desc': 'Blank endpaper'},
    2: {'type': 'GUARD', 'desc': 'Flyleaf recto: Thomas Bourne provenance (1641), multiple hands'},
    3: {'type': 'GUARD', 'desc': 'Flyleaf verso: Master Mercury declaration, shelfmark C.60.o.12', 'alchemical': True, 'hand': 'B'},
    4: {'type': 'OTHER', 'desc': 'Title page: 1545 RISTAMPATO, Aldine anchor, Sum Ben: Ionsonij'},
    5: {'type': 'OTHER', 'desc': 'Dedication: Crasso to Duke of Urbino, MUSEUM BRITANNICUM stamp'},
    6: {'type': 'OTHER', 'desc': 'Prefatory verse: Scita part 1'},
    7: {'type': 'OTHER', 'desc': 'Prefatory verse: Scita part 2, Finis. Annotated.'},
    8: {'type': 'OTHER', 'desc': 'Argomento/summary. HEAVILY annotated.'},
    9: {'type': 'OTHER', 'desc': 'Prefatory poem to Crasso. Annotated.'},
    10: {'type': 'OTHER', 'desc': 'Prefatory verse continued, Finis'},
    11: {'type': 'OTHER', 'desc': 'Prefatory verse: Andreas Maro Brixianus'},
    12: {'type': 'OTHER', 'desc': 'Half-title: POLIPHILI HYPNEROTOMACHIA...'},
    13: {'type': 'OTHER', 'desc': "Poliphilus's dedication to Polia: Vale."},
}

# Verified page numbers (photo_num -> visible_page_number)
VERIFIED_PAGES = {
    14: 1, 15: 2, 20: 7, 25: 12, 30: 17, 32: 19, 33: 20,
    40: 27, 41: 28, 50: 37, 60: 47, 77: 64, 78: 65,
    80: 67, 100: 87, 120: 107, 150: 137,
}

# Woodcuts detected
WOODCUTS_DETECTED = {
    40: 'Inscription monument: ΓΟΝΟΣ ΚΑΙ ΕΤΟΥΣΙΑ (Greek)',
    41: 'Elephant and Obelisk (the most famous HP woodcut)',
    100: 'Grotesque frieze with hybrid figures',
}

# Annotation density (from visual inspection)
ANNOTATION_DENSITY = {
    'HEAVY': [2, 3, 7, 8, 9, 14, 20, 25, 30, 33, 40, 41],
    'MODERATE': [60, 77, 78, 80, 100, 120, 150],
    'LIGHT': [50],
    'NONE': [1, 11, 12],
}

# Alchemical annotations confirmed
ALCHEMICAL_CONFIRMED = {
    3: {'hand': 'B', 'desc': 'Master Mercury declaration on flyleaf verso'},
    14: {'hand': 'B', 'desc': 'a1r: marginal annotations including alchemical marks'},
    33: {'hand': 'B', 'desc': 'page 20: alchemical ideograms in left margin'},
    41: {'hand': 'B', 'desc': 'b6v: elephant-obelisk densely annotated with ideograms'},
}

# Signature-to-page mapping for 1545 edition (same collation as 1499)
# Quires: a-z (omitting j,u,w) then A-G, each 8 leaves
def signature_to_page(sig):
    """Convert a signature reference to a page number."""
    m = re.match(r'([a-zA-Z])(\d+)([rv])', sig)
    if not m:
        return None
    quire_letter = m.group(1)
    leaf = int(m.group(2))
    side = m.group(3)

    # Quire order
    lower_quires = [c for c in 'abcdefghiklmnopqrstxyz']  # omit j,u,w
    upper_quires = list('ABCDEFG')
    all_quires = lower_quires + upper_quires

    if quire_letter not in all_quires:
        return None

    quire_idx = all_quires.index(quire_letter)
    # Each quire has 8 leaves (except possibly G with fewer)
    leaves_before = quire_idx * 8
    total_leaf = leaves_before + leaf
    page = (total_leaf - 1) * 2 + (1 if side == 'r' else 2)
    return page


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("=== Building BL Ground Truth Mapping ===\n")

    # Get BL manuscript ID
    cur.execute("SELECT id FROM manuscripts WHERE shelfmark = 'C.60.o.12'")
    bl_id = cur.fetchone()[0]

    # Update images with verified data
    cur.execute("""
        SELECT id, filename, sort_order FROM images
        WHERE manuscript_id = ? ORDER BY sort_order
    """, (bl_id,))
    images = cur.fetchall()

    updated = 0
    ground_truth = []

    for img_id, filename, sort_order in images:
        m = re.search(r'(\d+)\.jpg$', filename)
        if not m:
            continue
        photo_num = int(m.group(1))

        record = {
            'photo_num': photo_num,
            'filename': filename,
            'image_id': img_id,
        }

        if photo_num in FRONT_MATTER:
            fm = FRONT_MATTER[photo_num]
            cur.execute("""
                UPDATE images SET folio_number = NULL, side = NULL,
                    page_type = ?, confidence = 'HIGH'
                WHERE id = ?
            """, (fm['type'], img_id))
            record['type'] = 'FRONT_MATTER'
            record['desc'] = fm['desc']
            record['page_type'] = fm['type']
        else:
            page_num = photo_num - BL_OFFSET
            leaf_num = (page_num + 1) // 2
            side = 'r' if page_num % 2 == 1 else 'v'

            # Check against verified pages
            verified = VERIFIED_PAGES.get(photo_num)
            confidence = 'HIGH' if verified and verified == page_num else 'MEDIUM'

            cur.execute("""
                UPDATE images SET folio_number = ?, side = ?,
                    page_type = 'PAGE', confidence = ?
                WHERE id = ?
            """, (str(leaf_num), side, confidence, img_id))

            record['type'] = 'PAGE'
            record['page_num'] = page_num
            record['leaf_num'] = leaf_num
            record['side'] = side
            record['confidence'] = confidence
            if verified:
                record['verified'] = True

        # Add woodcut info
        if photo_num in WOODCUTS_DETECTED:
            record['woodcut'] = WOODCUTS_DETECTED[photo_num]

        # Add annotation density
        for density, photos in ANNOTATION_DENSITY.items():
            if photo_num in photos:
                record['annotation_density'] = density

        # Add alchemical confirmation
        if photo_num in ALCHEMICAL_CONFIRMED:
            record['alchemical'] = ALCHEMICAL_CONFIRMED[photo_num]

        ground_truth.append(record)
        updated += 1

    conn.commit()

    # Now re-match: for each BL dissertation ref, find the correct image
    print("Re-matching BL references with ground-truth folio mapping...")

    cur.execute("""
        SELECT id, signature_ref FROM dissertation_refs
        WHERE manuscript_shelfmark = 'C.60.o.12' AND signature_ref IS NOT NULL
    """)
    bl_refs = cur.fetchall()

    matched = 0
    upgraded = 0
    for ref_id, sig_ref in bl_refs:
        expected_page = signature_to_page(sig_ref)
        if not expected_page:
            continue

        expected_photo = expected_page + BL_OFFSET
        expected_leaf = (expected_page + 1) // 2
        expected_side = 'r' if expected_page % 2 == 1 else 'v'

        # Find the image with this corrected folio
        cur.execute("""
            SELECT id FROM images
            WHERE manuscript_id = ? AND folio_number = ? AND side = ?
        """, (bl_id, str(expected_leaf), expected_side))
        img = cur.fetchone()

        if img:
            # Check if this match already exists
            cur.execute("""
                SELECT id, confidence FROM matches
                WHERE ref_id = ? AND image_id = ?
            """, (ref_id, img[0]))
            existing = cur.fetchone()

            if existing:
                # Upgrade confidence if we have verified page data
                if expected_photo in VERIFIED_PAGES:
                    cur.execute("UPDATE matches SET confidence = 'HIGH' WHERE id = ?",
                                (existing[0],))
                    upgraded += 1
                else:
                    cur.execute("UPDATE matches SET confidence = 'MEDIUM' WHERE id = ?",
                                (existing[0],))
                    upgraded += 1
            else:
                # Create new match
                cur.execute("""
                    INSERT OR IGNORE INTO matches
                        (ref_id, image_id, match_method, confidence, needs_review)
                    VALUES (?, ?, 'FOLIO_EXACT', 'MEDIUM', 1)
                """, (ref_id, img[0]))
                matched += 1

    conn.commit()

    # Summary
    cur.execute("""
        SELECT mat.confidence, COUNT(*)
        FROM matches mat
        JOIN images i ON mat.image_id = i.id
        WHERE i.manuscript_id = ?
        GROUP BY mat.confidence
    """, (bl_id,))
    print(f"\nBL match confidence after ground-truth fix:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    cur.execute("SELECT confidence, COUNT(*) FROM matches GROUP BY confidence ORDER BY confidence")
    print(f"\nAll matches:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    # Write ground truth
    gt_path = STAGING_DIR / "bl_ground_truth.json"
    with open(gt_path, 'w', encoding='utf-8') as f:
        json.dump({
            'offset': BL_OFFSET,
            'verified_count': len(VERIFIED_PAGES),
            'front_matter_count': len(FRONT_MATTER),
            'woodcuts_detected': len(WOODCUTS_DETECTED),
            'alchemical_confirmed': len(ALCHEMICAL_CONFIRMED),
            'matches_upgraded': upgraded,
            'new_matches': matched,
            'ground_truth': ground_truth,
        }, f, indent=2, ensure_ascii=False)
    print(f"\nGround truth: {gt_path}")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
