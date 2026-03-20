"""Marginalia schema migration: fix BL confidence, create alchemical tables,
add alchemical_framework column, clean up redundancies.

Phase 1 of the Deckard Marginalia Spec (docs/DECKARD_MARGINALIA_SPEC.md).
Idempotent.
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("=== Marginalia Schema Migration ===\n")

    # 1. Fix BL confidence: downgrade MEDIUM to LOW for C.60.o.12
    print("Step 1: Fixing BL confidence levels...")
    cur.execute("""
        UPDATE matches SET confidence = 'LOW'
        WHERE confidence = 'MEDIUM'
        AND image_id IN (
            SELECT i.id FROM images i
            JOIN manuscripts m ON i.manuscript_id = m.id
            WHERE m.shelfmark = 'C.60.o.12'
        )
    """)
    downgraded = cur.rowcount
    print(f"  Downgraded {downgraded} BL matches from MEDIUM to LOW")

    # 2. Add alchemical_framework column to annotator_hands
    print("\nStep 2: Adding alchemical_framework column...")
    cur.execute("PRAGMA table_info(annotator_hands)")
    existing = {r[1] for r in cur.fetchall()}
    if 'alchemical_framework' not in existing:
        cur.execute("ALTER TABLE annotator_hands ADD COLUMN alchemical_framework TEXT")
        print("  Added annotator_hands.alchemical_framework")
    else:
        print("  Column already exists")

    # Populate for the two alchemists
    cur.execute("""
        UPDATE annotator_hands SET alchemical_framework = 'mercury_despagnet'
        WHERE hand_label = 'B' AND manuscript_shelfmark = 'C.60.o.12'
    """)
    cur.execute("""
        UPDATE annotator_hands SET alchemical_framework = 'sulphur_pseudo_geber'
        WHERE hand_label = 'E' AND manuscript_shelfmark = 'Buffalo RBR'
    """)
    print("  Set framework: Hand B = mercury_despagnet, Hand E = sulphur_pseudo_geber")

    # 3. Create alchemical_symbols table
    print("\nStep 3: Creating alchemical_symbols table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS alchemical_symbols (
            id INTEGER PRIMARY KEY,
            symbol_name TEXT NOT NULL UNIQUE,
            symbol_unicode TEXT,
            metal TEXT,
            planet TEXT,
            gender TEXT,
            framework TEXT,
            notes TEXT,
            source_basis TEXT
        )
    """)

    # 4. Create symbol_occurrences table
    print("Step 4: Creating symbol_occurrences table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS symbol_occurrences (
            id INTEGER PRIMARY KEY,
            symbol_id INTEGER REFERENCES alchemical_symbols(id),
            hand_id INTEGER REFERENCES annotator_hands(id),
            signature_ref TEXT,
            folio_description_id INTEGER REFERENCES folio_descriptions(id),
            context_text TEXT,
            latin_inflection TEXT,
            thesis_page INTEGER,
            confidence TEXT DEFAULT 'MEDIUM',
            source_method TEXT DEFAULT 'CORPUS_EXTRACTION',
            needs_review BOOLEAN DEFAULT 1
        )
    """)

    # 5. Seed the 7 standard planetary-metal symbols
    print("\nStep 5: Seeding alchemical symbols...")
    symbols = [
        ("Sol", "U+2609", "Gold (Aurum)", "Sun", "masculine", "standard",
         "The king of metals. Hand B uses with Latin inflections (-ra for aurata). Hand E identifies with masculine principle in chess match.",
         "Taylor 1951; Russell 2014, pp. 156-158, 187-190"),
        ("Luna", "U+263D", "Silver (Argentum)", "Moon", "feminine", "standard",
         "The queen of metals. Hand E emphasizes Luna as feminine principle, inverting gender at depth. Hand B uses less frequently than Sol.",
         "Taylor 1951; Russell 2014, pp. 187-190"),
        ("Mercury", "U+263F", "Quicksilver (Hydrargyrum)", "Mercury", "hermaphroditic", "d_espagnet",
         "The central principle for Hand B: 'Master Mercury' (Magisteri Mercurii). Catalytic agent uniting all elements. Consistent with d'Espagnet's Enchiridion.",
         "Taylor 1951; Russell 2014, pp. 159-163"),
        ("Venus", "U+2640", "Copper (Cuprum)", "Venus", "feminine", "standard",
         "Hand B uses with Latin inflection -eris. Associated with love, generation, and the feminine principle in both alchemical and narrative readings.",
         "Taylor 1951; Russell 2014, p. 157"),
        ("Mars", "U+2642", "Iron (Ferrum)", "Mars", "masculine", "standard",
         "The martial metal. Appears in Hand B's ideographic vocabulary but less prominently than Sol, Luna, and Mercury.",
         "Taylor 1951; Russell 2014, p. 157"),
        ("Jupiter", "U+2643", "Tin (Stannum)", "Jupiter", "masculine", "standard",
         "Hand B annotates the Jupiter passage on a4r, mapping the god's hierarchical position to the tin-gold transmutation sequence.",
         "Taylor 1951; Russell 2014, pp. 164-165"),
        ("Saturn", "U+2644", "Lead (Plumbum)", "Saturn", "masculine", "standard",
         "The base metal. Starting point of transmutation in both d'Espagnet and pseudo-Geber frameworks. Rarely written by Hand E, who prefers full Latin names.",
         "Taylor 1951; Russell 2014"),
    ]

    inserted = 0
    for s in symbols:
        cur.execute("""
            INSERT OR IGNORE INTO alchemical_symbols
                (symbol_name, symbol_unicode, metal, planet, gender, framework, notes, source_basis)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, s)
        inserted += cur.rowcount
    print(f"  Inserted {inserted} symbols")

    # Additional alchemical substances mentioned by Russell
    extras = [
        ("Cinnabar", None, "Mercuric Sulphide", None, None, "standard",
         "Red mercury ore. Hand B identifies cinnabar-related passages. The red color connects to rubedo (reddening) stage.",
         "Russell 2014, p. 161"),
        ("Sulphur", None, "Brimstone", None, "masculine", "pseudo_geber",
         "The masculine combustible principle in pseudo-Geber tradition. Hand E emphasizes sulphur as the active agent in transmutation.",
         "Newman 1991; Russell 2014, pp. 186-190"),
        ("Hermaphrodite", None, None, None, "hermaphroditic", "both",
         "The product of the chemical wedding: union of Sol and Luna producing a being that reconciles masculine and feminine. Hand E identifies hermaphroditic imagery on h1r.",
         "Russell 2014, pp. 189-190"),
    ]
    for s in extras:
        cur.execute("""
            INSERT OR IGNORE INTO alchemical_symbols
                (symbol_name, symbol_unicode, metal, planet, gender, framework, notes, source_basis)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, s)
        inserted += cur.rowcount

    conn.commit()

    # Report
    cur.execute("SELECT COUNT(*) FROM alchemical_symbols")
    sym_count = cur.fetchone()[0]
    cur.execute("SELECT confidence, COUNT(*) FROM matches GROUP BY confidence ORDER BY confidence")
    conf = {r[0]: r[1] for r in cur.fetchall()}
    print(f"\n=== Summary ===")
    print(f"  Alchemical symbols: {sym_count}")
    print(f"  Match confidence: {conf}")
    cur.execute("SELECT hand_label, manuscript_shelfmark, alchemical_framework FROM annotator_hands WHERE is_alchemist = 1")
    for r in cur.fetchall():
        print(f"  Alchemist: Hand {r[0]} ({r[1]}): {r[2]}")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
