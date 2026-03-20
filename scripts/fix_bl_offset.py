"""Fix the BL C.60.o.12 photo-to-folio mapping.

DISCOVERY: Visual inspection of BL photographs reveals that the first 13
photos are covers, endpapers, flyleaves, and front matter. The actual text
begins at photo 014 = folio 1 (a1r).

Therefore: folio_number = photo_number - 13

This script:
1. Updates all BL images with corrected folio numbers
2. Re-runs matching with corrected folio numbers
3. Upgrades confidence from LOW to MEDIUM where the new mapping produces
   a valid signature match
4. Logs all changes to staging/bl_offset_fix.json

VERIFICATION DATA:
  Photo 001 = blank cover
  Photo 003 = flyleaf (Master Mercury declaration)
  Photo 010 = prefatory verse (Finis)
  Photo 014 = a1r (POLIPHILO INCOMINCIA..., page 1)
  Photo 015 = page 2 (015 - 13 = 2)
  Photo 020 = page 7 (020 - 13 = 7)
  Photo 032 = page 19 (032 - 13 = 19)
  Photo 033 = page 20 (033 - 13 = 20)
  Photo 050 = page 37 (050 - 13 = 37)
  Photo 100 = page 87 (100 - 13 = 87)

All verified by reading actual manuscript images.
"""

import sqlite3
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"
STAGING_DIR = BASE_DIR / "staging"

BL_OFFSET = 13  # Photos 001-013 are non-text pages


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("=== Fixing BL Photo-to-Folio Offset ===\n")
    print(f"Offset: photo_number - {BL_OFFSET} = folio_number")
    print("Verified by visual inspection of 10 photographs.\n")

    # Step 1: Get BL manuscript ID
    cur.execute("SELECT id FROM manuscripts WHERE shelfmark = 'C.60.o.12'")
    bl_ms = cur.fetchone()
    if not bl_ms:
        print("ERROR: BL manuscript not found")
        return
    bl_id = bl_ms[0]

    # Step 2: Get all BL images
    cur.execute("""
        SELECT id, filename, folio_number, side, relative_path
        FROM images WHERE manuscript_id = ?
        ORDER BY sort_order
    """, (bl_id,))
    images = cur.fetchall()
    print(f"BL images: {len(images)}")

    # Step 3: Extract photo number from filename and compute corrected folio
    changes = []
    for img in images:
        img_id, filename, old_folio, old_side, path = img

        # Extract photo number from filename (C_60_o_12-NNN.jpg)
        m = re.search(r'(\d+)\.jpg$', filename)
        if not m:
            continue
        photo_num = int(m.group(1))

        # Compute corrected folio number
        corrected_folio = photo_num - BL_OFFSET

        if corrected_folio < 1:
            # This is a non-text page (cover, flyleaf, etc.)
            new_type = 'OTHER'
            if photo_num <= 2:
                new_type = 'COVER'
            elif photo_num <= 5:
                new_type = 'GUARD'  # flyleaves
            cur.execute("""
                UPDATE images SET folio_number = NULL, page_type = ?
                WHERE id = ?
            """, (new_type, img_id))
            changes.append({
                'image_id': img_id, 'filename': filename,
                'photo_num': photo_num, 'old_folio': old_folio,
                'new_folio': None, 'action': f'Reclassified as {new_type}',
            })
        else:
            # Determine recto/verso from corrected folio
            # In the photo sequence, odd corrected folios are recto, even are verso
            # (This is an assumption - each physical leaf has two sides)
            # Actually, each photo is one page, so we need to determine r/v
            # from position: the BL photos appear to photograph each opening
            # Photo 014 = folio 1 = a1r (recto, right page)
            # Photo 015 = folio 2 = a1v (verso, left page of next opening)
            # Actually looking at the images: 014 is clearly a recto (right page)
            # and 015 shows page "2" which is a1v (verso)
            # So: odd corrected_folio = recto, even = verso? No...
            # corrected_folio 1 (photo 14) = recto
            # corrected_folio 2 (photo 15) = verso... but page 2 is a1v
            # Actually in the HP, each LEAF has two sides.
            # Leaf 1 has recto (page 1) and verso (page 2)
            # So page_number maps to: leaf = (page+1)//2, side = r if odd, v if even
            leaf_num = (corrected_folio + 1) // 2
            side = 'r' if corrected_folio % 2 == 1 else 'v'

            cur.execute("""
                UPDATE images SET folio_number = ?, side = ?
                WHERE id = ?
            """, (str(leaf_num), side, img_id))
            changes.append({
                'image_id': img_id, 'filename': filename,
                'photo_num': photo_num,
                'old_folio': old_folio, 'new_folio': leaf_num,
                'new_side': side,
                'corrected_page': corrected_folio,
            })

    conn.commit()
    print(f"Updated {len(changes)} image records")

    # Step 4: Re-run matching for BL images with corrected folios
    print("\nStep 2: Re-matching BL references with corrected folios...")

    # Get all BL matches
    cur.execute("""
        SELECT mat.id, mat.ref_id, mat.image_id, mat.confidence
        FROM matches mat
        JOIN images i ON mat.image_id = i.id
        WHERE i.manuscript_id = ?
    """, (bl_id,))
    bl_matches = cur.fetchall()

    # Get dissertation refs for BL
    cur.execute("""
        SELECT id, signature_ref FROM dissertation_refs
        WHERE manuscript_shelfmark = 'C.60.o.12'
    """)
    bl_refs = {row[0]: row[1] for row in cur.fetchall()}

    # Get signature map
    cur.execute("SELECT signature, folio_number, side FROM signature_map")
    sig_to_folio = {}
    folio_to_sig = {}
    for row in cur.fetchall():
        sig_to_folio[row[0].lower()] = (row[1], row[2])
        folio_to_sig[(row[1], row[2])] = row[0]

    upgraded = 0
    for match in bl_matches:
        match_id, ref_id, image_id, old_conf = match

        # Get the corrected folio for this image
        cur.execute("SELECT folio_number, side FROM images WHERE id = ?", (image_id,))
        img_row = cur.fetchone()
        if not img_row or not img_row[0]:
            continue

        img_folio = int(img_row[0])
        img_side = img_row[1]

        # Get the expected folio from the dissertation ref's signature
        sig = bl_refs.get(ref_id)
        if not sig:
            continue

        expected = sig_to_folio.get(sig.lower())
        if not expected:
            continue

        exp_folio, exp_side = expected

        # Check if corrected image folio matches expected
        if img_folio == exp_folio and (img_side == exp_side or not exp_side):
            # Exact match with corrected offset!
            cur.execute("""
                UPDATE matches SET confidence = 'MEDIUM',
                    match_method = 'FOLIO_EXACT'
                WHERE id = ?
            """, (match_id,))
            upgraded += 1

    conn.commit()
    print(f"Upgraded {upgraded} BL matches from LOW to MEDIUM")

    # Step 5: Summary
    cur.execute("""
        SELECT mat.confidence, COUNT(*)
        FROM matches mat
        JOIN images i ON mat.image_id = i.id
        JOIN manuscripts m ON i.manuscript_id = m.id
        WHERE m.shelfmark = 'C.60.o.12'
        GROUP BY mat.confidence
    """)
    print("\nBL match confidence after fix:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    cur.execute("SELECT confidence, COUNT(*) FROM matches GROUP BY confidence ORDER BY confidence")
    print("\nAll matches:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    # Write staging log
    staging_path = STAGING_DIR / "bl_offset_fix.json"
    with open(staging_path, 'w', encoding='utf-8') as f:
        json.dump({
            'offset': BL_OFFSET,
            'verification': {
                'photo_014': 'a1r (POLIPHILO INCOMINCIA...)',
                'photo_015': 'page 2',
                'photo_020': 'page 7',
                'photo_032': 'page 19',
                'photo_033': 'page 20',
                'photo_050': 'page 37',
                'photo_100': 'page 87',
            },
            'images_updated': len(changes),
            'matches_upgraded': upgraded,
        }, f, indent=2)
    print(f"\nStaging: {staging_path}")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
