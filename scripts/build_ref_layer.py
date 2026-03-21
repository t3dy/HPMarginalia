#!/usr/bin/env python3
"""build_ref_layer.py — Build the page_concordance and woodcut_catalog reference tables.

Creates a unified concordance mapping every page surface of the 1499 HP
to all numbering systems (IA index, signature, folio, BL photo, section).

Also seeds the woodcut_catalog table with all 168 entries from the
1896 "Dream of Poliphilus" facsimile catalog.

Usage:
    python scripts/build_ref_layer.py
    python scripts/build_ref_layer.py --dry-run
"""

import argparse
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "hp.db"

# IA offset: IA page index = page_seq + 5
# Verified at 174/174 readable BL pages
IA_OFFSET = 5

# BL offset: BL photo = page_seq + 13
# (inverse: page = photo - 13)
# Verified at 174/174 readable pages
BL_OFFSET = 13

# BL photo range (sequential photos that map to book pages)
BL_FIRST_SEQ_PHOTO = 14   # Photo 14 = page 1
BL_LAST_SEQ_PHOTO = 202   # Approximate last sequential photo


# Narrative section assignments by page range
# These are approximate and will be refined
SECTIONS = [
    (1, 3, "PRELIMINARIES"),
    (4, 15, "DARK_FOREST"),
    (16, 37, "PYRAMID_RUINS"),
    (38, 62, "DRAGON_PORTAL"),
    (63, 79, "FIVE_SENSES"),
    (80, 105, "QUEEN_PALACE"),
    (106, 148, "JOURNEY_DOORS"),
    (149, 167, "PROCESSION"),
    (168, 185, "VENUS_TEMPLE"),
    (186, 215, "POLYANDRION"),
    (216, 220, "CYTHERA_VOYAGE"),
    (221, 255, "CYTHERA_GARDENS"),
    (256, 270, "VENUS_FOUNTAIN"),
    (271, 450, "BOOK_II_POLIA"),
    (451, 470, "COLOPHON"),
]


def get_section(page_seq):
    """Return the narrative section for a given page number."""
    for start, end, section in SECTIONS:
        if start <= page_seq <= end:
            return section
    return "UNKNOWN"


# 1896 Facsimile catalog: all 168 woodcuts
# Format: (catalog_number, description, subject_category, is_full_page, is_decorative, narrative_section)
# Page assignments will be computed separately
WOODCUT_CATALOG = [
    (1, "Poliphilus entering the dark forest", "NARRATIVE", False, False, "DARK_FOREST"),
    (2, "Poliphilus kneeling by a rivulet", "NARRATIVE", False, False, "DARK_FOREST"),
    (3, "Poliphilus sleeping under a tree (dream within dream)", "NARRATIVE", False, False, "DARK_FOREST"),
    (4, "Poliphilus among classical ruins with wolf", "NARRATIVE", False, False, "DARK_FOREST"),
    (5, "The great pyramidic temple with obelisk", "ARCHITECTURAL", True, False, "PYRAMID_RUINS"),
    (6, "Colossal bronze horse on pedestal with genii", "ARCHITECTURAL", False, False, "PYRAMID_RUINS"),
    (7, "Pedestal end: garland of marjoram and ferns (D.AMBIG.D.D.)", "HIEROGLYPHIC", False, False, "PYRAMID_RUINS"),
    (8, "Pedestal end: garland of orpine (Equus infalicitatis)", "HIEROGLYPHIC", False, False, "PYRAMID_RUINS"),
    (9, "Pedestal side: two-faced youths and nymphs dancing", "NARRATIVE", False, False, "PYRAMID_RUINS"),
    (10, "Pedestal side: youth distributing flowers", "NARRATIVE", False, False, "PYRAMID_RUINS"),
    (11, "Elephant saddle-cloth with Greek and Arabic inscription", "HIEROGLYPHIC", False, False, "PYRAMID_RUINS"),
    (12, "Colossal elephant of black stone bearing obelisk", "ARCHITECTURAL", False, False, "PYRAMID_RUINS"),
    (13, "Sarcophagus with nude King figure", "ARCHITECTURAL", False, False, "PYRAMID_RUINS"),
    (14, "Sarcophagus with nude Queen figure", "ARCHITECTURAL", False, False, "PYRAMID_RUINS"),
    (15, "Hieroglyphic devices with decorated casket", "HIEROGLYPHIC", False, False, "PYRAMID_RUINS"),
    (16, "Ancient gate with medallion busts", "ARCHITECTURAL", False, False, "DRAGON_PORTAL"),
    (17, "Poliphilus fleeing the dragon", "NARRATIVE", False, False, "DRAGON_PORTAL"),
    (18, "Emblematic devices (PATIENTIA / Anchor-Dolphin)", "HIEROGLYPHIC", False, False, "DRAGON_PORTAL"),
    (19, "Sleeping nymph fountain with satyrs", "NARRATIVE", False, False, "FIVE_SENSES"),
    (20, "Poliphilus meeting five nymphs", "NARRATIVE", False, False, "FIVE_SENSES"),
    (21, "Weather-cock with genius blowing trumpet", "DECORATIVE", False, True, "FIVE_SENSES"),
    (22, "Part of second fountain", "ARCHITECTURAL", False, False, "FIVE_SENSES"),
    (23, "Third fountain with Graces, harpies, griffins", "ARCHITECTURAL", False, False, "FIVE_SENSES"),
    (24, "Frieze ornament with genii, dolphins, bull skull", "DECORATIVE", False, True, "QUEEN_PALACE"),
    (25, "Panelled wall in Queen's palace with planetary names", "ARCHITECTURAL", False, False, "QUEEN_PALACE"),
    (26, "Poliphilus before Queen Eleuterylida enthroned", "NARRATIVE", False, False, "QUEEN_PALACE"),
    (27, "Medallion in canopy: youth with nimbus and eagle", "DECORATIVE", False, True, "QUEEN_PALACE"),
    (28, "Richly ornamented tripod", "DECORATIVE", False, True, "QUEEN_PALACE"),
    (29, "Golden basin upon wheels", "DECORATIVE", False, True, "QUEEN_PALACE"),
    (30, "Tripod with three naked boys on lion-footed pedestal", "DECORATIVE", False, True, "QUEEN_PALACE"),
    (31, "Vessel surmounted by coral-tree", "DECORATIVE", False, True, "QUEEN_PALACE"),
    (32, "Magnificent vessel with gold shrub, twice nymph height", "DECORATIVE", False, True, "QUEEN_PALACE"),
    (33, "Triangular obelisk of mystic Trinity with sphinxes", "ARCHITECTURAL", False, False, "JOURNEY_DOORS"),
    (34, "Cameo: Jupiter with cornucopia and vanquished giants", "DECORATIVE", False, True, "JOURNEY_DOORS"),
    (35, "Woman with tortoise and wings (Velocitatem sedendo)", "HIEROGLYPHIC", False, False, "JOURNEY_DOORS"),
    (36, "Circular bas-relief: two genii holding apple (Medium tenuere beati)", "HIEROGLYPHIC", False, False, "JOURNEY_DOORS"),
    (37, "Poliphilus at three gates: GLORIA DEI, MATER AMORIS, GLORIA MUNDI", "NARRATIVE", False, False, "JOURNEY_DOORS"),
    (38, "Poliphilus meets venerable matron with six attendants", "NARRATIVE", False, False, "JOURNEY_DOORS"),
    (39, "Poliphilus receives crown and palm-branch on sword", "NARRATIVE", False, False, "JOURNEY_DOORS"),
    (40, "Poliphilus among nymphs; flight of Logistica", "NARRATIVE", False, False, "JOURNEY_DOORS"),
    (41, "Poliphilus embraced by the nymph", "NARRATIVE", False, False, "JOURNEY_DOORS"),
    (42, "Poliphilus looking through bower as Polia approaches", "NARRATIVE", False, False, "JOURNEY_DOORS"),
    (43, "Poliphilus and Polia retreating from bower", "NARRATIVE", False, False, "JOURNEY_DOORS"),
    (44, "Triumphal car with Europa reliefs", "PROCESSION", False, False, "PROCESSION"),
    (45, "Relief: Rape of Europa", "PROCESSION", False, False, "PROCESSION"),
    (46, "Reliefs: Cupid shooting stars; Jupiter and Mars", "PROCESSION", False, False, "PROCESSION"),
    (47, "First Triumph of Europa: centaurs, nymphs, musicians (left)", "PROCESSION", False, False, "PROCESSION"),
    (48, "First Triumph of Europa (right continuation)", "PROCESSION", False, False, "PROCESSION"),
    (49, "Triumph of Leda reliefs: Leda lying-in, eggs presented", "PROCESSION", False, False, "PROCESSION"),
    (50, "Relief: King offering eggs at Temple of Apollo", "PROCESSION", False, False, "PROCESSION"),
    (51, "Reliefs: Cupid tracing figures; Judgment of Paris", "PROCESSION", False, False, "PROCESSION"),
    (52, "Second Triumph of Leda: elephants, swan (left)", "PROCESSION", False, False, "PROCESSION"),
    (53, "Second Triumph of Leda (right continuation)", "PROCESSION", False, False, "PROCESSION"),
    (54, "Triumph of Danae reliefs: Acrisius, tower construction", "PROCESSION", False, False, "PROCESSION"),
    (55, "Perseus with mirror and Medusa head; Pegasus", "PROCESSION", False, False, "PROCESSION"),
    (56, "Reliefs: Venus and Mars freed; Jupiter comforts Cupid", "PROCESSION", False, False, "PROCESSION"),
    (57, "Third Triumph of Danae: unicorns (left)", "PROCESSION", False, False, "PROCESSION"),
    (58, "Festival of Bacchus reliefs: Jupiter and Semele", "PROCESSION", False, False, "PROCESSION"),
    (59, "Third Triumph of Danae (right continuation)", "PROCESSION", False, False, "PROCESSION"),
    (60, "Jupiter commits infant Bacchus to Mercury", "PROCESSION", False, False, "PROCESSION"),
    (61, "Venus and Cupid before Jupiter; Psyche with lamp", "PROCESSION", False, False, "PROCESSION"),
    (62, "Vase relief: Jupiter and the Heliades", "PROCESSION", False, False, "PROCESSION"),
    (63, "Vintage scene with genii and young Bacchus", "PROCESSION", False, False, "PROCESSION"),
    (64, "Fourth Triumph: Festival of Bacchus, panthers (left)", "PROCESSION", False, False, "PROCESSION"),
    (65, "Festival of Bacchus with Silenus on ass (right)", "PROCESSION", False, False, "PROCESSION"),
    (66, "Triumph of Vertumnus and Pomona: satyrs, nymphs", "PROCESSION", False, False, "PROCESSION"),
    (67, "Four Seasons relief: Spring (Venus and Cupid)", "PROCESSION", False, True, "PROCESSION"),
    (68, "Four Seasons: Summer (Ceres with boy)", "PROCESSION", False, True, "PROCESSION"),
    (69, "Four Seasons: Autumn (Wine God with ram)", "PROCESSION", False, True, "PROCESSION"),
    (70, "Four Seasons: Winter (Jupiter Pluvius)", "PROCESSION", False, True, "PROCESSION"),
    (71, "Worship of Priapus with nineteen female and five male figures", "NARRATIVE", True, False, "VENUS_TEMPLE"),
    (72, "Section and ground-plan of rotunda temple", "DIAGRAM", False, False, "VENUS_TEMPLE"),
    (73, "Nude winged female half-figure with foliage", "DECORATIVE", False, True, "VENUS_TEMPLE"),
    (74, "Globular lamp hung in chains", "DECORATIVE", False, True, "VENUS_TEMPLE"),
    (75, "Crowning of lantern in cupola with bells", "DECORATIVE", False, True, "VENUS_TEMPLE"),
    (76, "Temple of Venus: procession of seven virgins to altar", "NARRATIVE", False, False, "VENUS_TEMPLE"),
    (77, "Polia's torch extinguished in altar-fountain", "NARRATIVE", False, False, "VENUS_TEMPLE"),
    (78, "Temple ceremony continuation", "NARRATIVE", False, False, "VENUS_TEMPLE"),
    (79, "Two virgins offering swans and doves for sacrifice", "NARRATIVE", False, False, "VENUS_TEMPLE"),
    (80, "The altar in the Temple of Venus", "ARCHITECTURAL", False, False, "VENUS_TEMPLE"),
    (81, "Temple ceremony continuation", "NARRATIVE", False, False, "VENUS_TEMPLE"),
    (82, "Temple ceremony continuation", "NARRATIVE", False, False, "VENUS_TEMPLE"),
    (83, "Temple ceremony continuation", "NARRATIVE", False, False, "VENUS_TEMPLE"),
    (84, "Miracle of the roses: rose-tree rising from altar, doves", "NARRATIVE", False, False, "VENUS_TEMPLE"),
    (85, "Poliphilus and Polia receive fruits from priestess", "NARRATIVE", False, False, "VENUS_TEMPLE"),
    (86, "Ruins of Temple Polyandrion with obelisk among trees", "ARCHITECTURAL", False, False, "POLYANDRION"),
    (87, "Obelisk with hieroglyphic devices", "HIEROGLYPHIC", False, False, "POLYANDRION"),
    (88, "Hieroglyphic medallion relief (first)", "HIEROGLYPHIC", False, True, "POLYANDRION"),
    (89, "Hieroglyphic medallion relief (second)", "HIEROGLYPHIC", False, True, "POLYANDRION"),
    (90, "Hieroglyphic medallion relief (third)", "HIEROGLYPHIC", False, True, "POLYANDRION"),
    (91, "Hieroglyphic medallion relief (fourth)", "HIEROGLYPHIC", False, True, "POLYANDRION"),
    (92, "Hieroglyphic relief (fifth)", "HIEROGLYPHIC", False, True, "POLYANDRION"),
    (93, "Architrave fragment with bird and lamp", "ARCHITECTURAL", False, True, "POLYANDRION"),
    (94, "Cupola above entrance to the crypt", "ARCHITECTURAL", False, False, "POLYANDRION"),
    (95, "Sarcophagus: Interna Plotoni", "ARCHITECTURAL", False, False, "POLYANDRION"),
    (96, "Mosaic of Hell on crypt ceiling (after Dante)", "NARRATIVE", False, False, "POLYANDRION"),
    (97, "Sepulchral monument with masks", "ARCHITECTURAL", False, False, "POLYANDRION"),
    (98, "Sepulchral monument with Renaissance urn", "ARCHITECTURAL", False, False, "POLYANDRION"),
    (99, "Sacrifice relief: old man, youth, faun, dancers", "NARRATIVE", False, False, "POLYANDRION"),
    (100, "Epitaph with eagle and dolphins", "ARCHITECTURAL", False, True, "POLYANDRION"),
    (101, "Epitaph fragment", "ARCHITECTURAL", False, True, "POLYANDRION"),
    (102, "Sepulchral urn with Greek inscription", "ARCHITECTURAL", False, True, "POLYANDRION"),
    (103, "Tombstone surmounted by urn", "ARCHITECTURAL", False, True, "POLYANDRION"),
    (104, "Epitaph fragment with skulls and laurel", "ARCHITECTURAL", False, True, "POLYANDRION"),
    (105, "Epitaph: D.M. Lyndia", "ARCHITECTURAL", False, True, "POLYANDRION"),
    (106, "Sarcophagus: P. Cornelia Annia", "ARCHITECTURAL", False, True, "POLYANDRION"),
    (107, "Sarcophagus with hieroglyphic devices", "HIEROGLYPHIC", False, True, "POLYANDRION"),
    (108, "Large epitaph: O lector infoelix", "ARCHITECTURAL", False, False, "POLYANDRION"),
    (109, "Sepulchral monument with laurel wreath", "ARCHITECTURAL", False, False, "POLYANDRION"),
    (110, "Monument of Artemisia drinking ashes of Mausolus", "NARRATIVE", False, False, "POLYANDRION"),
    (111, "Epitaph with busts of youth and woman", "ARCHITECTURAL", False, False, "POLYANDRION"),
    (112, "Sepulchral portal: narrow gates of life and death", "ARCHITECTURAL", False, False, "POLYANDRION"),
    (113, "Standard of Cupid's bark (blue silk with rebus)", "DECORATIVE", False, True, "CYTHERA_VOYAGE"),
    (114, "The bark of the god of love", "NARRATIVE", False, False, "CYTHERA_VOYAGE"),
    (115, "Water-work in garden of island of Venus", "ARCHITECTURAL", False, True, "CYTHERA_GARDENS"),
    (116, "Tree clipped in ring-shape", "DECORATIVE", False, True, "CYTHERA_GARDENS"),
    (117, "Box-tree clipped as man supporting towers with arch", "DECORATIVE", False, True, "CYTHERA_GARDENS"),
    (118, "Box-tree", "DECORATIVE", False, True, "CYTHERA_GARDENS"),
    (119, "Box-tree clipped as centre piece", "DECORATIVE", False, True, "CYTHERA_GARDENS"),
    (120, "Box-tree clipped as mushroom", "DECORATIVE", False, True, "CYTHERA_GARDENS"),
    (121, "Peristyle in pleasure-ground of island of Venus", "ARCHITECTURAL", False, False, "CYTHERA_GARDENS"),
    (122, "Plan of the island of Venus", "DIAGRAM", False, False, "CYTHERA_GARDENS"),
    (123, "Ornament of a flower-bed", "DECORATIVE", False, True, "CYTHERA_GARDENS"),
    (124, "Square ornament of a flower-bed", "DECORATIVE", False, True, "CYTHERA_GARDENS"),
    (125, "Clipped tree upon altar with bull's skull and festoons", "DECORATIVE", False, True, "CYTHERA_GARDENS"),
    (126, "Pattern of a flower-bed", "DECORATIVE", False, True, "CYTHERA_GARDENS"),
    (127, "Box-tree clipped as three peacocks on altar-vase", "DECORATIVE", False, True, "CYTHERA_GARDENS"),
    (128, "Flower-bed in shape of eagle", "DECORATIVE", False, True, "CYTHERA_GARDENS"),
    (129, "Flower-bed: two birds on a vase", "DECORATIVE", False, True, "CYTHERA_GARDENS"),
    (130, "Trophy of Roman arms with winged genius head", "DECORATIVE", False, True, "CYTHERA_GARDENS"),
    (131, "Trophy: tunic with winged genius head and laurel", "DECORATIVE", False, True, "CYTHERA_GARDENS"),
    (132, "Trophy: tiger-skin and bull's head", "DECORATIVE", False, True, "CYTHERA_GARDENS"),
    (133, "Trophy: disk with wings, tablet 'Quis evadet?'", "DECORATIVE", False, True, "CYTHERA_GARDENS"),
    (134, "Trophy with gold wings and tablet 'Nemo'", "DECORATIVE", False, True, "CYTHERA_GARDENS"),
    (135, "Trophy with gold wings and floating ribbons", "DECORATIVE", False, True, "CYTHERA_GARDENS"),
    (136, "Trophy: laurel wreath with Cupid, tablet 'Gained by spear'", "DECORATIVE", False, True, "CYTHERA_GARDENS"),
    (137, "Superb nymph figure with javelin", "PORTRAIT", False, False, "CYTHERA_GARDENS"),
    (138, "Vase with dragon-handle monsters", "DECORATIVE", False, True, "CYTHERA_GARDENS"),
    (139, "Small precious stone vase with fiery sparks", "DECORATIVE", False, True, "CYTHERA_GARDENS"),
    (140, "Earthenware amphora with odoriferous fumes", "DECORATIVE", False, True, "CYTHERA_GARDENS"),
    (141, "Terminal figure with three male heads", "DECORATIVE", False, True, "CYTHERA_GARDENS"),
    (142, "Trophy with three heads of Cerberus and serpent", "DECORATIVE", False, True, "CYTHERA_GARDENS"),
    (143, "Triumph of Cupid: nymphs, satyrs, dragons, captives (left)", "PROCESSION", False, False, "CYTHERA_GARDENS"),
    (144, "Triumph of Cupid (right continuation)", "PROCESSION", False, False, "CYTHERA_GARDENS"),
    (145, "Column base with rams' heads and sacrifice medallion", "DECORATIVE", False, True, "VENUS_FOUNTAIN"),
    (146, "Frieze ornament: bull with nude figure and satyrs", "DECORATIVE", False, True, "VENUS_FOUNTAIN"),
    (147, "The Amphitheatre in island of Venus", "ARCHITECTURAL", False, False, "VENUS_FOUNTAIN"),
    (148, "Ground-plan of fountain of Venus", "DIAGRAM", False, False, "VENUS_FOUNTAIN"),
    (149, "Fountain of Venus: water from sarcophagus of Adonis", "ARCHITECTURAL", False, False, "VENUS_FOUNTAIN"),
    (150, "Statue of Venus on Tomb of Adonis with nymphs", "NARRATIVE", False, False, "VENUS_FOUNTAIN"),
    (151, "Poliphilus and Polia at Fountain of Venus with nymphs", "NARRATIVE", False, False, "VENUS_FOUNTAIN"),
    (152, "Polia in temple of Diana; Poliphilus prostrate (Book II)", "NARRATIVE", False, False, "BOOK_II_POLIA"),
    (153, "Polia drags prostrate Poliphilus from sanctuary", "NARRATIVE", False, False, "BOOK_II_POLIA"),
    (154, "Dream of Polia: Cupid punishes two women", "NARRATIVE", False, False, "BOOK_II_POLIA"),
    (155, "Cupid brandishes sword over kneeling victim", "NARRATIVE", False, False, "BOOK_II_POLIA"),
    (156, "Lion, dog, dragon devour victims; Cupid flies above", "NARRATIVE", False, False, "BOOK_II_POLIA"),
    (157, "Poliphilus as dead; Polia kneels in grief", "NARRATIVE", False, False, "BOOK_II_POLIA"),
    (158, "Poliphilus revived in Polia's lap; embracing", "NARRATIVE", False, False, "BOOK_II_POLIA"),
    (159, "Priestesses drive lovers from Temple of Diana", "NARRATIVE", False, False, "BOOK_II_POLIA"),
    (160, "Polia in bed-chamber; Diana vs Venus vision in sky", "NARRATIVE", False, False, "BOOK_II_POLIA"),
    (161, "Polia kneels before Venus priestess; Poliphilus beside", "NARRATIVE", False, False, "BOOK_II_POLIA"),
    (162, "Enamoured couple kneeling before priestess", "NARRATIVE", False, False, "BOOK_II_POLIA"),
    (163, "Priestess enthroned; lovers kissing in her presence", "NARRATIVE", False, False, "BOOK_II_POLIA"),
    (164, "Poliphilus writing at carved desk", "NARRATIVE", False, False, "BOOK_II_POLIA"),
    (165, "Polia reading lover's letter in bed-chamber", "NARRATIVE", False, False, "BOOK_II_POLIA"),
    (166, "Poliphilus before Venus in clouds; Cupid listens", "NARRATIVE", False, False, "BOOK_II_POLIA"),
    (167, "Cupid with bust of Polia and arrow", "NARRATIVE", False, False, "BOOK_II_POLIA"),
    (168, "Cupid shoots arrow at bust of Polia", "NARRATIVE", False, False, "BOOK_II_POLIA"),
]

# Known page assignments for catalog entries (from existing woodcuts table)
# Maps catalog_number -> page_1499
# Entries #1-70 can be mapped from existing data; #71-168 need verification
KNOWN_CATALOG_PAGES = {
    1: 4,     # Dark forest
    2: 8,     # Rivulet
    3: 10,    # Dream within dream
    4: 11,    # Classical ruins with wolf
    5: 16,    # Great pyramid (full page)
    6: 22,    # Bronze horse
    7: 23,    # Pedestal end (D.AMBIG.D.D.)
    8: 23,    # Same page as #7 (two ends on one page)
    9: 24,    # Pedestal side (TEMPVS)
    10: 25,   # Pedestal side (flowers)
    11: 27,   # Elephant saddle-cloth
    12: 28,   # Elephant and obelisk
    13: 29,   # Sarcophagus King
    14: 30,   # Sarcophagus Queen
    15: 31,   # Hieroglyphic devices
    16: 38,   # Ancient gate
    17: 52,   # Dragon
    18: 59,   # Emblematic devices
    19: 63,   # Sleeping nymph
    20: 66,   # Five nymphs
    21: 71,   # Weather-cock
    22: 75,   # Second fountain
    23: 80,   # Third fountain with Graces
    # 24-27: Palace section, approximate
    24: 84,   # Frieze ornament (near palace)
    25: 88,   # Palace wall with planets
    26: 90,   # Queen enthroned
    27: 92,   # Medallion in canopy
    28: 93,   # Tripod
    29: 94,   # Basin on wheels
    30: 95,   # Tripod with boys
    # 31-32: More decorative objects
    31: 102,  # Vessel with coral (approximate)
    32: 105,  # Magnificent vessel with nymph
    33: 119,  # Triangular obelisk
    34: 122,  # Cameo Jupiter
    35: 123,  # Woman with tortoise
    36: 124,  # Circular bas-relief
    37: 125,  # Three gates
    38: 126,  # Meeting matron
    39: 127,  # Crown and palm-branch
    40: 129,  # Nymphs; Logistica
    41: 130,  # Poliphilus embraced
    42: 132,  # Looking through bower
    43: 139,  # Retreating from bower
    # Procession: woodcuts 44-70 map to pages 149-167
    44: 149,  # Europa car reliefs
    45: 149,  # Same page (stacked panels)
    46: 150,  # Front/back reliefs
    47: 151,  # First Triumph left
    48: 151,  # Same page (continuation)
    49: 152,  # Leda reliefs
    50: 153,  # Apollo temple relief
    51: 154,  # Cupid / Paris reliefs
    52: 155,  # Second Triumph left
    53: 155,  # Same page
    54: 156,  # Danae reliefs
    55: 156,  # Same page
    56: 158,  # Venus/Mars reliefs
    57: 159,  # Third Triumph
    58: 160,  # Bacchus reliefs
    59: 159,  # Same as #57 (continuation)
    60: 160,  # Same as #58
    61: 161,  # Venus and Cupid before Jupiter
    62: 161,  # Same page
    63: 164,  # Vintage scene
    64: 165,  # Fourth Triumph left
    65: 165,  # Same page
    66: 166,  # Vertumnus and Pomona
    67: 167,  # Spring
    68: 167,  # Summer (same page as seasonal reliefs)
    69: 167,  # Autumn
    70: 167,  # Winter
    # After procession: woodcuts 71-168 need page verification
    71: 170,  # Priapus worship (full page)
}


def create_tables(cur, dry_run=False):
    """Create the reference layer tables."""
    if dry_run:
        print("DRY RUN: Would create page_concordance and woodcut_catalog tables")
        return

    cur.execute("""
        CREATE TABLE IF NOT EXISTS page_concordance (
            id INTEGER PRIMARY KEY,
            page_seq INTEGER UNIQUE NOT NULL,
            signature TEXT,
            folio_number INTEGER,
            side TEXT CHECK(side IN ('r', 'v')),
            quire TEXT,
            leaf_in_quire INTEGER,
            ia_page_index INTEGER,
            bl_photo_number INTEGER,
            bl_photo_has_content BOOLEAN DEFAULT 0,
            siena_photo_number INTEGER,
            has_woodcut BOOLEAN DEFAULT 0,
            woodcut_catalog_number INTEGER,
            has_text BOOLEAN DEFAULT 1,
            is_full_page_woodcut BOOLEAN DEFAULT 0,
            section TEXT,
            source_method TEXT DEFAULT 'COMPUTED',
            confidence TEXT DEFAULT 'HIGH',
            verified BOOLEAN DEFAULT 0,
            notes TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS woodcut_catalog (
            id INTEGER PRIMARY KEY,
            catalog_number INTEGER UNIQUE NOT NULL,
            description TEXT NOT NULL,
            page_seq INTEGER,
            woodcut_id INTEGER,
            subject_category TEXT,
            is_full_page BOOLEAN DEFAULT 0,
            is_decorative BOOLEAN DEFAULT 0,
            narrative_section TEXT,
            source TEXT DEFAULT '1896_FACSIMILE',
            confidence TEXT DEFAULT 'HIGH',
            FOREIGN KEY (page_seq) REFERENCES page_concordance(page_seq),
            FOREIGN KEY (woodcut_id) REFERENCES woodcuts(id)
        )
    """)

    # Index for fast lookups
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pc_page_seq ON page_concordance(page_seq)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pc_signature ON page_concordance(signature)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pc_ia_page ON page_concordance(ia_page_index)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pc_bl_photo ON page_concordance(bl_photo_number)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_wc_page_seq ON woodcut_catalog(page_seq)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_wc_catalog ON woodcut_catalog(catalog_number)")


def populate_concordance(cur, dry_run=False):
    """Build page_concordance from signature_map + offset formulas."""

    # Get signature_map data
    sig_rows = cur.execute("""
        SELECT signature, folio_number, side, quire, leaf_in_quire
        FROM signature_map
        ORDER BY id
    """).fetchall()

    if not sig_rows:
        print("ERROR: signature_map is empty")
        return 0

    # Convert to page_seq: sequential numbering of page surfaces
    # signature_map is already in order, so row index + 1 = page_seq
    inserted = 0
    for i, (sig, folio, side, quire, leaf) in enumerate(sig_rows):
        page_seq = i + 1
        ia_page = page_seq + IA_OFFSET

        # BL photo mapping (inverse of page = photo - 13 → photo = page + 13)
        bl_photo = page_seq + BL_OFFSET
        bl_has_content = BL_FIRST_SEQ_PHOTO <= bl_photo <= BL_LAST_SEQ_PHOTO

        # Check if this page has a woodcut (from existing woodcuts table)
        has_wc = cur.execute(
            "SELECT COUNT(*) FROM woodcuts WHERE page_1499 = ?", (page_seq,)
        ).fetchone()[0] > 0

        section = get_section(page_seq)

        if dry_run:
            if has_wc or page_seq <= 5 or page_seq % 50 == 0:
                print(f"  p.{page_seq:3d} {sig:5s} folio={folio:3d}{side} "
                      f"IA=n{ia_page:3d} BL={bl_photo:3d} "
                      f"{'WC' if has_wc else '  '} {section}")
        else:
            cur.execute("""
                INSERT OR IGNORE INTO page_concordance (
                    page_seq, signature, folio_number, side, quire,
                    leaf_in_quire, ia_page_index, bl_photo_number,
                    bl_photo_has_content, has_woodcut, section
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (page_seq, sig, folio, side, quire, leaf,
                  ia_page, bl_photo, bl_has_content, has_wc, section))
        inserted += 1

    return inserted


def populate_woodcut_catalog(cur, dry_run=False):
    """Seed the woodcut_catalog with all 168 entries."""
    inserted = 0

    for cat_num, desc, category, full_page, decorative, section in WOODCUT_CATALOG:
        page_seq = KNOWN_CATALOG_PAGES.get(cat_num)

        # Try to find matching woodcut_id from existing woodcuts table
        woodcut_id = None
        if page_seq:
            row = cur.execute(
                "SELECT id FROM woodcuts WHERE page_1499 = ? LIMIT 1",
                (page_seq,)
            ).fetchone()
            if row:
                woodcut_id = row[0]

        confidence = 'HIGH' if page_seq and cat_num <= 70 else 'MEDIUM'

        if dry_run:
            linked = f"-> wc#{woodcut_id}" if woodcut_id else ""
            page_str = f"p.{page_seq}" if page_seq else "p.???"
            print(f"  #{cat_num:3d} {page_str:>6s} [{category:13s}] "
                  f"{desc[:50]:50s} {linked}")
        else:
            cur.execute("""
                INSERT OR IGNORE INTO woodcut_catalog (
                    catalog_number, description, page_seq, woodcut_id,
                    subject_category, is_full_page, is_decorative,
                    narrative_section, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (cat_num, desc, page_seq, woodcut_id, category,
                  full_page, decorative, section, confidence))
        inserted += 1

    return inserted


def main():
    parser = argparse.ArgumentParser(
        description="Build the HP reference layer (page_concordance + woodcut_catalog)"
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    print("=== Building HP Reference Layer ===\n")

    # Step 1: Create tables
    print("Step 1: Creating tables...")
    create_tables(cur, args.dry_run)

    # Step 2: Populate page_concordance from signature_map
    print("\nStep 2: Populating page_concordance from signature_map...")
    n_pages = populate_concordance(cur, args.dry_run)
    print(f"  {n_pages} page surfaces mapped")

    # Step 3: Populate woodcut_catalog
    print("\nStep 3: Populating woodcut_catalog (168 entries)...")
    n_wc = populate_woodcut_catalog(cur, args.dry_run)
    print(f"  {n_wc} catalog entries seeded")

    # Step 4: Summary stats
    if not args.dry_run:
        conn.commit()

        total_pages = cur.execute("SELECT COUNT(*) FROM page_concordance").fetchone()[0]
        wc_pages = cur.execute("SELECT COUNT(*) FROM page_concordance WHERE has_woodcut = 1").fetchone()[0]
        catalog_mapped = cur.execute("SELECT COUNT(*) FROM woodcut_catalog WHERE page_seq IS NOT NULL").fetchone()[0]
        catalog_linked = cur.execute("SELECT COUNT(*) FROM woodcut_catalog WHERE woodcut_id IS NOT NULL").fetchone()[0]

        print(f"\n=== Summary ===")
        print(f"  page_concordance: {total_pages} page surfaces")
        print(f"  Pages with woodcuts: {wc_pages}")
        print(f"  woodcut_catalog: {n_wc} entries")
        print(f"    Mapped to pages: {catalog_mapped}/168")
        print(f"    Linked to woodcuts table: {catalog_linked}/168")
        print(f"    Unmapped (need IA scan): {168 - catalog_mapped}")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
