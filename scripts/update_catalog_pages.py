#!/usr/bin/env python3
"""update_catalog_pages.py — Push confirmed page assignments into woodcut_catalog.

Updates page_seq for all 168 catalog entries based on visual IA scan results.
Also updates page_concordance.has_woodcut for newly discovered woodcut pages.
"""

import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "hp.db"

# Confirmed page assignments from IA visual scan
# Maps catalog_number -> page_seq
# For entries sharing a page, all get the same page_seq
CONFIRMED_PAGES = {
    # Already mapped (catalog 1-71, mostly correct, some corrections)
    1: 4, 2: 8, 3: 10, 4: 11, 5: 16, 6: 22, 7: 23, 8: 23,
    9: 24, 10: 25, 11: 27, 12: 28, 13: 29, 14: 30, 15: 31,
    16: 38, 17: 52, 18: 59, 19: 63, 20: 66, 21: 71, 22: 75,
    23: 80, 24: 84, 25: 88, 26: 90, 27: 92, 28: 93, 29: 94,
    30: 95, 31: 102, 32: 105, 33: 119, 34: 122, 35: 123,
    36: 124, 37: 125, 38: 126, 39: 127, 40: 129, 41: 130,
    42: 132, 43: 139,
    44: 149, 45: 149, 46: 150, 47: 151, 48: 151, 49: 152,
    50: 153, 51: 154, 52: 155, 53: 155, 54: 156, 55: 156,
    56: 158, 57: 159, 58: 160, 59: 159, 60: 160, 61: 161,
    62: 161, 63: 164, 64: 165, 65: 165, 66: 166, 67: 167,
    68: 167, 69: 167, 70: 167,

    # Newly confirmed from IA scan (catalog 71-168)
    71: 185,   # Worship of Priapus (full page)
    72: 195,   # Section and ground-plan of rotunda temple
    73: 197,   # Nude winged female half-figure
    74: 198,   # Globular lamp hung in chains
    75: 201,   # Crowning of lantern in cupola with bells
    76: 205,   # Temple of Venus: procession of seven virgins
    77: 207,   # Polia's torch extinguished
    78: 208,   # Temple ceremony with figures
    79: 208,   # Two virgins offering swans (same page as 78)
    80: 210,   # The altar in Temple of Venus
    81: 212,   # Temple ceremony continuation
    82: 213,   # Temple ceremony continuation
    83: 213,   # Temple ceremony continuation (same page)
    84: 221,   # Miracle of the roses
    85: 221,   # Receiving fruits from priestess (same page)
    86: 233,   # Ruins of Temple Polyandrion (obelisk)
    87: 233,   # Obelisk with hieroglyphic devices (same page)
    88: 233,   # Hieroglyphic medallion relief (first)
    89: 235,   # Hieroglyphic medallion relief (second)
    90: 235,   # Hieroglyphic medallion relief (third)
    91: 236,   # Hieroglyphic medallion relief (fourth)
    92: 236,   # Hieroglyphic relief (fifth)
    93: 236,   # Architrave fragment with bird and lamp
    94: 237,   # Cupola above entrance to crypt
    95: 238,   # Sarcophagus: Interna Plotoni
    96: 242,   # Mosaic of Hell on crypt ceiling
    97: 242,   # Sepulchral monument with masks
    98: 244,   # Sepulchral monument with Renaissance urn
    99: 244,   # Sacrifice relief
    100: 244,  # Epitaph with eagle and dolphins
    101: 246,  # Epitaph fragment
    102: 250,  # Sepulchral urn with Greek inscription
    103: 246,  # Tombstone surmounted by urn
    104: 246,  # Epitaph fragment with skulls and laurel
    105: 248,  # Epitaph: D.M. Lyndia
    106: 248,  # Sarcophagus: P. Cornelia Annia
    107: 250,  # Sarcophagus with hieroglyphic devices
    108: 252,  # Large epitaph: O lector infoelix
    109: 254,  # Sepulchral monument with laurel wreath
    110: 258,  # Monument of Artemisia
    111: 258,  # Epitaph with busts (same page)
    112: 260,  # Sepulchral portal: gates of life and death
    113: 275,  # Standard of Cupid's bark
    114: 281,  # The bark of the god of love
    115: 295,  # Water-work in garden
    116: 295,  # Tree clipped in ring-shape (same page)
    117: 296,  # Box-tree clipped as man with towers
    118: 296,  # Box-tree (same page)
    119: 296,  # Box-tree clipped as centre piece
    120: 297,  # Box-tree clipped as mushroom
    121: 298,  # Peristyle in pleasure-ground
    122: 301,  # Plan of the island of Venus
    123: 309,  # Ornament of a flower-bed
    124: 309,  # Square ornament (same page)
    125: 295,  # Clipped tree on altar (same page as 115-116)
    126: 311,  # Pattern of a flower-bed
    127: 313,  # Box-tree as three peacocks
    128: 313,  # Flower-bed eagle (same page)
    129: 317,  # Flower-bed: two birds on vase
    130: 317,  # Trophy of Roman arms
    131: 317,  # Trophy: tunic with genius head
    132: 319,  # Trophy: tiger-skin and bull's head
    133: 319,  # Trophy: disk with wings 'Quis evadet?'
    134: 319,  # Trophy with gold wings 'Nemo'
    135: 319,  # Trophy with gold wings and ribbons
    136: 321,  # Trophy: laurel wreath with Cupid
    137: 327,  # Superb nymph figure with javelin
    138: 330,  # Vase with dragon-handle monsters
    139: 331,  # Small precious stone vase
    140: 331,  # Earthenware amphora (same page)
    141: 334,  # Terminal figure with three male heads
    142: 334,  # Trophy with three heads of Cerberus
    143: 337,  # Triumph of Cupid (left)
    144: 337,  # Triumph of Cupid (right)
    145: 339,  # Column base with rams' heads
    146: 339,  # Frieze ornament with bull
    147: 341,  # The Amphitheatre
    148: 349,  # Ground-plan of fountain of Venus
    149: 363,  # Fountain of Venus
    150: 365,  # Statue of Venus on Tomb of Adonis
    151: 365,  # Poliphilus and Polia at fountain (same page)
    152: 387,  # Polia in temple of Diana
    153: 389,  # Polia drags prostrate Poliphilus
    154: 391,  # Dream of Polia: Cupid punishes
    155: 392,  # Cupid brandishes sword
    156: 393,  # Lion, dog, dragon devour victims
    157: 411,  # Poliphilus as dead; Polia kneels
    158: 412,  # Poliphilus revived in Polia's lap
    159: 413,  # Priestesses drive lovers from temple
    160: 415,  # Polia in bed-chamber; Diana vs Venus
    161: 419,  # Polia kneels before Venus priestess
    162: 419,  # Enamoured couple kneeling (same page)
    163: 425,  # Priestess enthroned; lovers kissing
    164: 433,  # Poliphilus writing at carved desk
    165: 435,  # Polia reading lover's letter
    166: 447,  # Poliphilus before Venus in clouds
    167: 449,  # Cupid with bust of Polia
    168: 449,  # Cupid shoots arrow at bust (same page)
}


def main():
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    # Step 1: Update woodcut_catalog page assignments
    print("Updating woodcut_catalog page assignments...")
    updated = 0
    for cat_num, page_seq in CONFIRMED_PAGES.items():
        cur.execute("""
            UPDATE woodcut_catalog
            SET page_seq = ?, confidence = 'HIGH'
            WHERE catalog_number = ?
        """, (page_seq, cat_num))
        if cur.rowcount:
            updated += 1

    print(f"  Updated {updated} catalog entries")

    # Step 2: Update page_concordance.has_woodcut for newly discovered pages
    print("Updating page_concordance.has_woodcut...")
    new_wc_pages = set(CONFIRMED_PAGES.values())
    marked = 0
    for page_seq in new_wc_pages:
        cur.execute("""
            UPDATE page_concordance
            SET has_woodcut = 1
            WHERE page_seq = ? AND has_woodcut = 0
        """, (page_seq,))
        if cur.rowcount:
            marked += 1

    print(f"  Marked {marked} new woodcut pages")

    # Step 3: Summary
    conn.commit()

    total_mapped = cur.execute(
        "SELECT COUNT(*) FROM woodcut_catalog WHERE page_seq IS NOT NULL"
    ).fetchone()[0]
    total_high = cur.execute(
        "SELECT COUNT(*) FROM woodcut_catalog WHERE confidence = 'HIGH'"
    ).fetchone()[0]
    wc_pages = cur.execute(
        "SELECT COUNT(*) FROM page_concordance WHERE has_woodcut = 1"
    ).fetchone()[0]
    distinct_pages = cur.execute(
        "SELECT COUNT(DISTINCT page_seq) FROM woodcut_catalog WHERE page_seq IS NOT NULL"
    ).fetchone()[0]

    print(f"\n=== Summary ===")
    print(f"  Catalog entries mapped: {total_mapped}/168")
    print(f"  HIGH confidence: {total_high}/168")
    print(f"  Distinct woodcut pages: {distinct_pages}")
    print(f"  Total pages with woodcuts: {wc_pages}")

    conn.close()


if __name__ == "__main__":
    main()
