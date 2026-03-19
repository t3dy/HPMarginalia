"""Catalog all manuscript images into the database."""

import sqlite3
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"


def parse_bl_filename(filename):
    """Parse BL C.60.o.12 image filenames.

    Patterns:
      C_60_o_12-NNN.jpg  -> sequential page scan
      BL HP NN.jpg        -> marginalia detail photo
      BL 2.1.jpg, BL2.jpg -> supplementary photos
    """
    # Sequential page scans
    m = re.match(r'C_60_o_12-(\d{3})\.jpg', filename)
    if m:
        seq = int(m.group(1))
        return {
            'folio_number': str(seq),
            'side': None,  # not encoded in filename
            'page_type': 'PAGE',
            'sort_order': seq,
        }

    # Marginalia detail photos
    m = re.match(r'BL\s*HP\s*(\d+)\.jpg', filename)
    if m:
        num = int(m.group(1))
        return {
            'folio_number': None,
            'side': None,
            'page_type': 'MARGINALIA_DETAIL',
            'sort_order': 1000 + num,
        }

    # Other BL supplementary
    m = re.match(r'BL\s*[\d.]+\.jpg', filename)
    if m:
        return {
            'folio_number': None,
            'side': None,
            'page_type': 'OTHER',
            'sort_order': 2000,
        }

    return {
        'folio_number': None,
        'side': None,
        'page_type': 'OTHER',
        'sort_order': 9999,
    }


def parse_siena_filename(filename):
    """Parse Siena O.III.38 image filenames.

    Patterns:
      O.III.38_NNNNr.jpg / O.III.38_NNNNv.jpg  -> folio recto/verso
      O.III.38_000antcop.jpg                     -> front cover
      O.III.38_000fdg1r.jpg                      -> guard leaf
      O.III.38_postcop.jpg                       -> back cover
      Siena HP N.jpg / Siena Hp N.jpg            -> marginalia detail
    """
    # Standard folio pages
    m = re.match(r'O\.III\.38_(\d{4})([rv])\.jpg', filename)
    if m:
        folio = int(m.group(1))
        side = m.group(2)
        sort_order = folio * 2 + (0 if side == 'r' else 1)
        return {
            'folio_number': str(folio),
            'side': side,
            'page_type': 'PAGE',
            'sort_order': sort_order,
        }

    # Cover and guard pages
    if 'antcop' in filename or 'postcop' in filename:
        sort_order = -2 if 'antcop' in filename else 99999
        return {
            'folio_number': None,
            'side': None,
            'page_type': 'COVER',
            'sort_order': sort_order,
        }

    if 'fdg' in filename or 'risg' in filename:
        sort_order = -1
        return {
            'folio_number': None,
            'side': None,
            'page_type': 'GUARD',
            'sort_order': sort_order,
        }

    # Marginalia detail photos
    m = re.match(r'Siena\s*[Hh][Pp]\s*(\d+)\.jpg', filename, re.IGNORECASE)
    if m:
        num = int(m.group(1))
        return {
            'folio_number': None,
            'side': None,
            'page_type': 'MARGINALIA_DETAIL',
            'sort_order': 100000 + num,
        }

    return {
        'folio_number': None,
        'side': None,
        'page_type': 'OTHER',
        'sort_order': 999999,
    }


def catalog_manuscript(conn, shelfmark, parser_fn):
    """Catalog all images for a manuscript."""
    cur = conn.cursor()
    cur.execute("SELECT id, image_dir FROM manuscripts WHERE shelfmark = ?", (shelfmark,))
    row = cur.fetchone()
    if not row:
        print(f"  WARNING: Manuscript {shelfmark} not found in database")
        return 0

    ms_id, image_dir = row
    img_path = BASE_DIR / image_dir
    if not img_path.exists():
        print(f"  WARNING: Image directory not found: {img_path}")
        return 0

    count = 0
    for f in sorted(img_path.glob('*.jpg')):
        parsed = parser_fn(f.name)
        relative = f"{image_dir}/{f.name}"
        cur.execute(
            """INSERT OR IGNORE INTO images
               (manuscript_id, filename, folio_number, side, page_type, sort_order, relative_path)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (ms_id, f.name, parsed['folio_number'], parsed['side'],
             parsed['page_type'], parsed['sort_order'], relative)
        )
        count += 1

    conn.commit()
    return count


def main():
    conn = sqlite3.connect(DB_PATH)

    print("Cataloging BL C.60.o.12 images...")
    bl_count = catalog_manuscript(conn, 'C.60.o.12', parse_bl_filename)
    print(f"  {bl_count} images cataloged")

    print("Cataloging Siena O.III.38 images...")
    siena_count = catalog_manuscript(conn, 'O.III.38', parse_siena_filename)
    print(f"  {siena_count} images cataloged")

    # Summary stats
    cur = conn.cursor()
    for page_type in ['PAGE', 'MARGINALIA_DETAIL', 'COVER', 'GUARD', 'OTHER']:
        cur.execute("SELECT COUNT(*) FROM images WHERE page_type = ?", (page_type,))
        print(f"  {page_type}: {cur.fetchone()[0]}")

    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()
