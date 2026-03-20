"""Create hp_copies table and seed Russell's 6 annotated copies.

Step 1 of the Manuscripts Pipeline (docs/MANUSCRIPTS_SPEC.md).
Idempotent.
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS hp_copies (
    id INTEGER PRIMARY KEY,
    shelfmark TEXT NOT NULL UNIQUE,
    institution TEXT NOT NULL,
    city TEXT,
    country TEXT,
    edition TEXT DEFAULT '1499',
    has_annotations BOOLEAN DEFAULT 0,
    studied_by TEXT,
    annotation_summary TEXT,
    hand_count INTEGER DEFAULT 0,
    copy_notes TEXT,
    has_images_in_project BOOLEAN DEFAULT 0,
    istc_id TEXT,
    review_status TEXT DEFAULT 'DRAFT',
    source_method TEXT DEFAULT 'DETERMINISTIC',
    confidence TEXT DEFAULT 'MEDIUM'
);
"""

COPIES = [
    {
        "shelfmark": "C.60.o.12",
        "institution": "British Library",
        "city": "London",
        "country": "United Kingdom",
        "edition": "1545",
        "has_annotations": True,
        "studied_by": "Russell 2014",
        "hand_count": 2,
        "has_images_in_project": True,
        "copy_notes": "1545 second Aldine edition. Two hands: Ben Jonson (Hand A) and an anonymous alchemist (Hand B). Purchased by Thomas Bourne in 1641. The BL copy's sequential photo numbering makes folio-to-image matching provisional.",
        "confidence": "LOW",
    },
    {
        "shelfmark": "Buffalo RBR",
        "institution": "Buffalo & Erie County Public Library",
        "city": "Buffalo, NY",
        "country": "United States",
        "edition": "1499",
        "has_annotations": True,
        "studied_by": "Russell 2014",
        "hand_count": 5,
        "has_images_in_project": False,
        "copy_notes": "The most densely annotated copy in Russell's study. Five interleaved hands (A-E). Hands A-B possibly Jesuit, St. Omer. Hand E is an alchemist following pseudo-Geber's sulphur and Sol/Luna framework.",
        "confidence": "HIGH",
    },
    {
        "shelfmark": "Inc.Stam.Chig.II.610",
        "institution": "Vatican Library (Biblioteca Apostolica Vaticana)",
        "city": "Vatican City",
        "country": "Vatican City",
        "edition": "1499",
        "has_annotations": True,
        "studied_by": "Russell 2014",
        "hand_count": 1,
        "has_images_in_project": False,
        "copy_notes": "Annotated by Fabio Chigi (Pope Alexander VII). Focus on acutezze (verbal wit). Chigi later commissioned Bernini's elephant-obelisk sculpture (1667) drawing on the HP's woodcut.",
        "confidence": "HIGH",
    },
    {
        "shelfmark": "INCUN A.5.13",
        "institution": "Cambridge University Library",
        "city": "Cambridge",
        "country": "United Kingdom",
        "edition": "1499",
        "has_annotations": True,
        "studied_by": "Russell 2014",
        "hand_count": 1,
        "has_images_in_project": False,
        "copy_notes": "Annotated by Benedetto Giovio. Natural-historical reading treating the HP as a Plinian reference compendium. Extractive annotation mode (inventio).",
        "confidence": "HIGH",
    },
    {
        "shelfmark": "Modena (Panini)",
        "institution": "Biblioteca Panini",
        "city": "Modena",
        "country": "Italy",
        "edition": "1499",
        "has_annotations": True,
        "studied_by": "Russell 2014",
        "hand_count": 1,
        "has_images_in_project": False,
        "copy_notes": "Also annotated by Benedetto Giovio. Comparison with Cambridge copy annotations reveals consistent bibliographic and natural-historical interests. First studied by Stichel (1994).",
        "confidence": "HIGH",
    },
    {
        "shelfmark": "O.III.38",
        "institution": "Biblioteca degli Intronati",
        "city": "Siena",
        "country": "Italy",
        "edition": "1499",
        "has_annotations": True,
        "studied_by": "Russell 2014",
        "hand_count": 1,
        "has_images_in_project": True,
        "copy_notes": "478-image digital facsimile with explicit folio-number filenames. Anonymous annotations. Basis for the project's most reliable concordance data (HIGH confidence matches).",
        "confidence": "HIGH",
    },
]


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("Creating hp_copies table...")
    cur.executescript(SCHEMA)

    print("Seeding Russell's 6 annotated copies...")
    inserted = 0
    for c in COPIES:
        cur.execute("""
            INSERT OR IGNORE INTO hp_copies
                (shelfmark, institution, city, country, edition,
                 has_annotations, studied_by, hand_count,
                 has_images_in_project, copy_notes, confidence,
                 source_method, review_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'DETERMINISTIC', 'DRAFT')
        """, (c["shelfmark"], c["institution"], c["city"], c["country"],
              c["edition"], c["has_annotations"], c["studied_by"],
              c["hand_count"], c["has_images_in_project"],
              c["copy_notes"], c["confidence"]))
        inserted += cur.rowcount

    conn.commit()
    conn.close()
    print(f"  Inserted {inserted} copies")
    print("Done.")


if __name__ == "__main__":
    main()
