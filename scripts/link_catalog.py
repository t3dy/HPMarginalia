#!/usr/bin/env python3
"""link_catalog.py — Map woodcut_catalog entries to confirmed page numbers and woodcut IDs.

Uses the IA scan results to assign page_seq to catalog entries #72-168,
then links woodcut_id via the page join.

Usage:
    python scripts/link_catalog.py
    python scripts/link_catalog.py --dry-run
"""

import argparse
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "hp.db"

# Confirmed catalog -> page mappings from IA visual scan
# Format: catalog_number -> page_1499
CATALOG_PAGE_MAP = {
    # Venus Temple section
    72: 195,   # Section and ground-plan of rotunda temple
    73: 197,   # Nude winged female half-figure
    74: 198,   # Globular lamp hung in chains
    75: 201,   # Crowning of lantern in cupola
    76: 205,   # Procession of seven virgins to altar
    77: 207,   # Polia's torch extinguished
    78: 208,   # Temple ceremony at altar
    79: 210,   # Two virgins offering swans and doves
    80: 212,   # The altar in the Temple of Venus
    81: 213,   # Temple ceremony: miracle of roses area
    82: 219,   # Ceremony continuation (sacrifice with swans)
    83: 204,   # Inscribed tablets in temple (hieroglyphic)
    84: 222,   # Miracle of the roses
    85: 224,   # Poliphilus and Polia receive fruits

    # Polyandrion section
    86: 228,   # Ruins of Temple Polyandrion
    87: 233,   # Obelisk with hieroglyphic devices
    88: 233,   # Hieroglyphic medallion (first) — same page as #87
    89: 235,   # Hieroglyphic medallion (second)
    90: 235,   # Hieroglyphic medallion (third) — same page as #89
    91: 234,   # Hieroglyphic relief (fourth) — device strip
    92: 234,   # Hieroglyphic relief (fifth) — Julius Caesar medallion
    93: 236,   # Architrave fragment: POLYANDRION inscription
    94: 237,   # Cupola above entrance to crypt
    95: 238,   # Sarcophagus: Interno Plotoni
    96: 241,   # Mosaic of Hell on crypt ceiling
    97: 243,   # Sepulchral monument (D.M. Annirae)
    98: 243,   # Sepulchral monument with urn — same page as #97
    99: 245,   # Sacrifice relief: Have Seria Obitum
    100: 247,  # Epitaph fragments with urn
    101: 247,  # Epitaph fragment — same page as #100
    102: 250,  # Sepulchral urn with Greek inscription
    103: 249,  # Tombstone surmounted by urn
    104: 258,  # Epitaph fragment with skulls (sepulchral monument with putti)
    105: 250,  # Epitaph D.M. Lyndia — same page as #102
    106: 251,  # Sarcophagus: P. Cornelia Annia
    107: 252,  # Sarcophagus with hieroglyphic devices
    108: 253,  # Large epitaph: O lector infoelix
    109: 254,  # Sepulchral monument with laurel wreath
    110: 257,  # Monument of Artemisia
    111: 259,  # Epitaph with busts of youth and woman
    112: 261,  # Sepulchral portal: gates of life and death

    # Cythera voyage
    113: 275,  # Standard of Cupid's bark
    114: 281,  # The bark of the god of love

    # Cythera gardens
    115: 291,  # Water-work fountain
    116: 295,  # Tree clipped in ring-shape
    117: 296,  # Box-tree as candelabra/man supporting towers
    118: 296,  # Box-tree — same page as #117
    119: 296,  # Box-tree clipped as centre piece — same page
    120: 297,  # Box-tree clipped as mushroom
    121: 298,  # Peristyle colonnade with trellis
    122: 301,  # Plan of the island of Venus
    123: 307,  # Ornament of a flower-bed (circular)
    124: 311,  # Square ornament of a flower-bed
    125: 309,  # Clipped tree on altar — approximate
    126: 307,  # Pattern of a flower-bed — same page as #123
    127: 312,  # Peacock topiary on pedestal
    128: 313,  # Flower-bed in shape of eagle
    129: 314,  # Flower-bed: eagle/urn design
    130: 317,  # Trophy of Roman arms
    131: 317,  # Trophy: tunic with genius head — same page as #130
    132: 318,  # Trophy: QVIS EVADET
    133: 318,  # Trophy: disk with wings — same page as #132
    134: 319,  # Trophy with NEMO tablet
    135: 319,  # Trophy with floating ribbons — same page as #134
    136: 319,  # Trophy: laurel wreath with Cupid — same page
    137: 325,  # Superb nymph figure with javelin — approximate
    138: 328,  # Vase with dragon-handle monsters
    139: 331,  # Small precious stone vase with fiery sparks
    140: 330,  # Earthenware amphora with fumes
    141: 334,  # Terminal figure with three male heads
    142: 335,  # Trophy with three heads of Cerberus
    143: 336,  # Triumph of Cupid (left)
    144: 337,  # Triumph of Cupid (right continuation)
    145: 339,  # Column base with rams' heads
    146: 339,  # Frieze ornament: bull — same page as #145
    147: 341,  # The Amphitheatre
    148: 349,  # Ground-plan of fountain of Venus
    149: 365,  # Fountain of Venus (approximate — near fountain area)
    150: 365,  # Statue of Venus — same page area
    151: 365,  # Poliphilus and Polia at Fountain

    # Book II
    152: 387,  # Polia in temple of Diana; Poliphilus prostrate
    153: 386,  # Polia drags prostrate Poliphilus
    154: 393,  # Dream of Polia: Cupid punishes two women
    155: 390,  # Cupid brandishes sword over victims
    156: 391,  # Lion, dog, dragon devour victims
    157: 411,  # Poliphilus dead; Polia kneels
    158: 412,  # Poliphilus revived in Polia's lap
    159: 413,  # Priestesses drive lovers from Temple
    160: 416,  # Polia in bed-chamber; Diana vs Venus vision
    161: 419,  # Polia kneels before Venus priestess
    162: 421,  # Enamoured couple before priestess
    163: 425,  # Priestess enthroned; lovers kissing
    164: 433,  # Poliphilus writing at carved desk
    165: 436,  # Polia reading letter in bed-chamber
    166: 447,  # Poliphilus before Venus in clouds
    167: 448,  # Cupid with bust of Polia / shoots arrow
    168: 448,  # Cupid shoots arrow — same page as #167
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    print("=== Linking woodcut_catalog to confirmed pages ===\n")

    # Step 1: Update page_seq for all catalog entries
    mapped = 0
    for cat_num, page in CATALOG_PAGE_MAP.items():
        if args.dry_run:
            cur_page = cur.execute(
                "SELECT page_seq FROM woodcut_catalog WHERE catalog_number = ?",
                (cat_num,)
            ).fetchone()
            if cur_page and cur_page[0] is None:
                print(f"  #{cat_num:3d} -> p.{page}")
        else:
            cur.execute(
                "UPDATE woodcut_catalog SET page_seq = ? WHERE catalog_number = ?",
                (page, cat_num)
            )
        mapped += 1

    print(f"\n  Mapped {mapped} catalog entries to pages")

    # Step 2: Link woodcut_id via page join
    if not args.dry_run:
        conn.commit()

    # Now link woodcut_id where page_seq matches a woodcut
    linkable = cur.execute("""
        SELECT wc.catalog_number, wc.page_seq, w.id, w.title
        FROM woodcut_catalog wc
        JOIN woodcuts w ON wc.page_seq = w.page_1499
        WHERE wc.woodcut_id IS NULL
    """).fetchall()

    linked = 0
    for cat_num, page, wc_id, title in linkable:
        if args.dry_run:
            print(f"  Link #{cat_num:3d} p.{page} -> wc#{wc_id} '{title[:45]}'")
        else:
            cur.execute(
                "UPDATE woodcut_catalog SET woodcut_id = ? WHERE catalog_number = ?",
                (wc_id, cat_num)
            )
        linked += 1

    print(f"\n  Linked {linked} catalog entries to woodcuts table")

    # Step 3: Add catalog_number to woodcuts table if not exists
    # Check if column exists
    cols = [row[1] for row in cur.execute("PRAGMA table_info(woodcuts)").fetchall()]
    if 'catalog_number' not in cols:
        if not args.dry_run:
            cur.execute("ALTER TABLE woodcuts ADD COLUMN catalog_number INTEGER")
            print("\n  Added catalog_number column to woodcuts table")

            # Backfill from woodcut_catalog
            cur.execute("""
                UPDATE woodcuts SET catalog_number = (
                    SELECT wc.catalog_number FROM woodcut_catalog wc
                    WHERE wc.woodcut_id = woodcuts.id
                    LIMIT 1
                )
            """)
            backfilled = cur.rowcount
            print(f"  Backfilled catalog_number for {backfilled} woodcuts")
        else:
            print("\n  Would add catalog_number column to woodcuts table")
    else:
        print("\n  catalog_number column already exists")

    if not args.dry_run:
        conn.commit()

    # Final stats
    total_cat = cur.execute("SELECT COUNT(*) FROM woodcut_catalog").fetchone()[0]
    mapped_cat = cur.execute("SELECT COUNT(*) FROM woodcut_catalog WHERE page_seq IS NOT NULL").fetchone()[0]
    linked_cat = cur.execute("SELECT COUNT(*) FROM woodcut_catalog WHERE woodcut_id IS NOT NULL").fetchone()[0]
    wc_with_cat = cur.execute("SELECT COUNT(*) FROM woodcuts WHERE catalog_number IS NOT NULL").fetchone()[0] if 'catalog_number' in cols or not args.dry_run else 0

    print(f"\n=== Final State ===")
    print(f"  woodcut_catalog: {mapped_cat}/{total_cat} mapped to pages")
    print(f"  woodcut_catalog: {linked_cat}/{total_cat} linked to woodcuts")
    print(f"  woodcuts with catalog_number: {wc_with_cat}/141")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
