"""Initialize the Hypnerotomachia Poliphili SQLite database."""

import sqlite3
import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    filename TEXT NOT NULL,
    title TEXT,
    author TEXT,
    year INTEGER,
    doc_type TEXT CHECK(doc_type IN ('PRIMARY_TEXT','DISSERTATION','SCHOLARSHIP','PRESENTATION')),
    page_count INTEGER,
    file_size_bytes INTEGER,
    has_selectable_text BOOLEAN
);

CREATE TABLE IF NOT EXISTS manuscripts (
    id INTEGER PRIMARY KEY,
    shelfmark TEXT NOT NULL UNIQUE,
    institution TEXT,
    city TEXT,
    description TEXT,
    image_count INTEGER,
    image_dir TEXT
);

CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY,
    manuscript_id INTEGER REFERENCES manuscripts(id),
    filename TEXT NOT NULL,
    folio_number TEXT,
    side TEXT CHECK(side IN ('r','v',NULL)),
    page_type TEXT CHECK(page_type IN ('PAGE','MARGINALIA_DETAIL','COVER','GUARD','OTHER')),
    sort_order INTEGER,
    relative_path TEXT NOT NULL,
    master_path TEXT,
    web_path TEXT
);

CREATE TABLE IF NOT EXISTS signature_map (
    id INTEGER PRIMARY KEY,
    signature TEXT NOT NULL UNIQUE,
    folio_number INTEGER,
    side TEXT CHECK(side IN ('r','v')),
    quire TEXT,
    leaf_in_quire INTEGER
);

CREATE TABLE IF NOT EXISTS dissertation_refs (
    id INTEGER PRIMARY KEY,
    thesis_page INTEGER,
    signature_ref TEXT,
    manuscript_shelfmark TEXT,
    context_text TEXT,
    marginal_text TEXT,
    source_text TEXT,
    ref_type TEXT CHECK(ref_type IN ('MARGINALIA','ILLUSTRATION','TEXT','BINDING','PROVENANCE')),
    chapter_num INTEGER
);

CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY,
    ref_id INTEGER REFERENCES dissertation_refs(id),
    image_id INTEGER REFERENCES images(id),
    match_method TEXT CHECK(match_method IN ('SIGNATURE_EXACT','FOLIO_EXACT','MANUAL','VISION_VERIFIED')),
    confidence TEXT CHECK(confidence IN ('HIGH','MEDIUM','LOW','PROVISIONAL')),
    needs_review BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS image_readings (
    id INTEGER PRIMARY KEY,
    image_id INTEGER REFERENCES images(id),
    phase INTEGER NOT NULL,
    model TEXT NOT NULL,
    raw_json TEXT NOT NULL,
    page_number_read INTEGER,
    page_number_expected INTEGER,
    page_number_match BOOLEAN,
    has_woodcut BOOLEAN,
    woodcut_description TEXT,
    has_annotations BOOLEAN,
    annotation_density TEXT CHECK(annotation_density IN ('LIGHT','MODERATE','HEAVY',NULL)),
    annotation_locations TEXT,
    languages_detected TEXT,
    legible_fragments TEXT,
    deep_reading_json TEXT,
    concordance_status TEXT CHECK(concordance_status IN (
        'CONFIRMED', 'DISCREPANCY', 'UNVERIFIED'
    )) DEFAULT 'UNVERIFIED',
    reviewed BOOLEAN DEFAULT 0,
    reviewed_by TEXT,
    reviewed_at TEXT,
    promoted_to TEXT,
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    created_at TEXT DEFAULT (datetime('now'))
);
"""

# Known document metadata extracted from filenames
DOC_CLASSIFICATIONS = {
    'PRIMARY_TEXT': [
        'Francesco Colonna Hypnerotomachia Poliphili Da Capo',
        'Francesco Colonna Rino Avesani',
        'Hypnerotomachia by Francesco Colonna',
    ],
    'DISSERTATION': [
        'PhD_Thesis',
        'E_Thesis_Durham',
    ],
    'PRESENTATION': ['.pptx'],
}


def classify_doc(filename):
    for doc_type, patterns in DOC_CLASSIFICATIONS.items():
        for pat in patterns:
            if pat in filename:
                return doc_type
    return 'SCHOLARSHIP'


def extract_author_title(filename):
    """Best-effort extraction of author and title from filename."""
    name = Path(filename).stem
    # Remove common suffixes
    name = re.sub(r'\s*\(\d+\)\s*$', '', name)
    # Try splitting on known patterns
    parts = name.split(' - ')
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    # For space-separated names, take first few words as author guess
    return None, name


def populate_documents(conn):
    """Scan root dir for PDFs and PPTX files."""
    cur = conn.cursor()
    extensions = {'.pdf', '.pptx'}
    count = 0
    for f in sorted(BASE_DIR.iterdir()):
        if f.suffix.lower() in extensions and f.is_file():
            author, title = extract_author_title(f.name)
            doc_type = classify_doc(f.name)
            size = f.stat().st_size
            cur.execute(
                """INSERT OR IGNORE INTO documents
                   (filename, title, author, doc_type, file_size_bytes)
                   VALUES (?, ?, ?, ?, ?)""",
                (f.name, title, author, doc_type, size)
            )
            count += 1
    conn.commit()
    print(f"  Cataloged {count} documents")


def populate_manuscripts(conn):
    """Insert the two known manuscript records."""
    cur = conn.cursor()
    manuscripts = [
        (
            'C.60.o.12',
            'British Library',
            'London',
            'British Library copy of the 1499 Aldine Hypnerotomachia Poliphili with extensive marginalia',
            '3 BL C.60.o.12 Photos-20260319T001113Z-3-001/3 BL C.60.o.12 Photos'
        ),
        (
            'O.III.38',
            'Biblioteca degli Intronati',
            'Siena',
            'Siena copy of the 1499 Aldine Hypnerotomachia Poliphili, digital facsimile',
            'Siena O.III.38 Digital Facsimile-20260319T001110Z-3-001/Siena O.III.38 Digital Facsimile'
        ),
    ]
    for shelfmark, institution, city, desc, image_dir in manuscripts:
        # Count images
        img_path = BASE_DIR / image_dir
        img_count = len(list(img_path.glob('*.jpg'))) if img_path.exists() else 0
        cur.execute(
            """INSERT OR IGNORE INTO manuscripts
               (shelfmark, institution, city, description, image_count, image_dir)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (shelfmark, institution, city, desc, img_count, image_dir)
        )
    conn.commit()
    print("  Cataloged 2 manuscripts")


def main():
    print(f"Initializing database at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)

    print("Creating schema...")
    conn.executescript(SCHEMA)
    conn.execute("INSERT OR IGNORE INTO schema_version (version) VALUES (1)")
    conn.commit()

    print("Populating documents...")
    populate_documents(conn)

    print("Populating manuscripts...")
    populate_manuscripts(conn)

    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()
