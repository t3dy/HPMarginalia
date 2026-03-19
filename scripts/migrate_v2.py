"""Schema migration v2: Harden data model with review/provenance fields,
normalize tables, add dictionary and annotations support.

Idempotent — safe to run multiple times.
"""

import sqlite3
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"

MIGRATION_SQL = """
-- ============================================================
-- V2 MIGRATION: Hardened schema with review/provenance fields
-- ============================================================

-- 1. Annotations table: first-class representation of marginal notes
CREATE TABLE IF NOT EXISTS annotations (
    id INTEGER PRIMARY KEY,
    manuscript_id INTEGER REFERENCES manuscripts(id),
    hand_id INTEGER REFERENCES annotator_hands(id),
    signature_ref TEXT,
    folio_number INTEGER,
    side TEXT CHECK(side IN ('r','v',NULL)),
    annotation_text TEXT,
    annotation_type TEXT CHECK(annotation_type IN (
        'MARGINAL_NOTE','LABEL','SYMBOL','UNDERLINE','DRAWING',
        'CROSS_REFERENCE','INDEX_ENTRY','PROVENANCE','EMENDATION','OTHER'
    )),
    language TEXT,
    thesis_page INTEGER,
    thesis_chapter INTEGER,
    confidence TEXT CHECK(confidence IN ('HIGH','MEDIUM','LOW','PROVISIONAL')) DEFAULT 'PROVISIONAL',
    needs_review BOOLEAN DEFAULT 1,
    reviewed BOOLEAN DEFAULT 0,
    reviewed_by TEXT,
    reviewed_at TEXT,
    source_method TEXT CHECK(source_method IN (
        'MANUAL_TRANSCRIPTION','PDF_EXTRACTION','LLM_ASSISTED','INFERRED'
    )) DEFAULT 'INFERRED',
    notes TEXT
);

-- 2. Rename/normalize annotator_hands → annotators (keep old table, add view)
CREATE TABLE IF NOT EXISTS annotators (
    id INTEGER PRIMARY KEY,
    hand_label TEXT NOT NULL,
    manuscript_id INTEGER REFERENCES manuscripts(id),
    manuscript_shelfmark TEXT NOT NULL,
    attribution TEXT,
    attribution_confidence TEXT CHECK(attribution_confidence IN ('CERTAIN','PROBABLE','POSSIBLE','UNKNOWN')) DEFAULT 'POSSIBLE',
    language TEXT,
    ink_color TEXT,
    date_range TEXT,
    school TEXT,
    interests TEXT,
    description TEXT,
    is_alchemist BOOLEAN DEFAULT 0,
    chapter_num INTEGER,
    source_method TEXT DEFAULT 'LLM_ASSISTED',
    needs_review BOOLEAN DEFAULT 1,
    reviewed BOOLEAN DEFAULT 0,
    notes TEXT,
    UNIQUE(hand_label, manuscript_shelfmark)
);

-- 3. doc_folio_refs: references from any document to specific folios
CREATE TABLE IF NOT EXISTS doc_folio_refs (
    id INTEGER PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    signature_ref TEXT,
    folio_number INTEGER,
    side TEXT CHECK(side IN ('r','v',NULL)),
    manuscript_shelfmark TEXT,
    page_in_document INTEGER,
    context_text TEXT,
    marginal_text TEXT,
    ref_type TEXT CHECK(ref_type IN (
        'MARGINALIA','ILLUSTRATION','TEXT','BINDING','PROVENANCE','CROSS_REF'
    )),
    chapter_num INTEGER,
    hand_id INTEGER REFERENCES annotators(id),
    confidence TEXT CHECK(confidence IN ('HIGH','MEDIUM','LOW','PROVISIONAL')) DEFAULT 'PROVISIONAL',
    needs_review BOOLEAN DEFAULT 1,
    reviewed BOOLEAN DEFAULT 0,
    source_method TEXT DEFAULT 'PDF_EXTRACTION',
    notes TEXT
);

-- 4. Dictionary tables
CREATE TABLE IF NOT EXISTS dictionary_terms (
    id INTEGER PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    label TEXT NOT NULL,
    category TEXT NOT NULL,
    definition_short TEXT NOT NULL,
    definition_long TEXT,
    source_basis TEXT,
    review_status TEXT CHECK(review_status IN ('DRAFT','REVIEWED','VERIFIED')) DEFAULT 'DRAFT',
    needs_review BOOLEAN DEFAULT 1,
    reviewed BOOLEAN DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS dictionary_term_links (
    id INTEGER PRIMARY KEY,
    term_id INTEGER REFERENCES dictionary_terms(id),
    linked_term_id INTEGER REFERENCES dictionary_terms(id),
    link_type TEXT CHECK(link_type IN ('RELATED','SEE_ALSO','OPPOSITE','PARENT','CHILD')) DEFAULT 'RELATED',
    UNIQUE(term_id, linked_term_id, link_type)
);

-- 5. Topic cluster junction table (multi-value support)
CREATE TABLE IF NOT EXISTS document_topics (
    document_id INTEGER,
    topic TEXT NOT NULL,
    source_table TEXT NOT NULL CHECK(source_table IN ('bibliography','documents','summaries')),
    source_id INTEGER NOT NULL,
    PRIMARY KEY (source_table, source_id, topic)
);

-- 6. Add review/provenance columns to existing tables where missing
-- (ALTER TABLE IF NOT EXISTS not supported in SQLite, so we use try/except in Python)

-- 7. Update matches confidence constraint to include PROVISIONAL
-- (SQLite can't alter constraints, so we handle this in the matching logic)

-- 8. Update schema version
INSERT OR REPLACE INTO schema_version (version, created_at) VALUES (2, datetime('now'));
"""

# Columns to add to existing tables (table, column, type, default)
ALTER_COLUMNS = [
    ('matches', 'source_method', "TEXT DEFAULT 'FOLIO_EXACT'", None),
    ('matches', 'reviewed', 'BOOLEAN DEFAULT 0', None),
    ('matches', 'reviewed_by', 'TEXT', None),
    ('matches', 'notes', 'TEXT', None),
    ('documents', 'review_status', "TEXT DEFAULT 'UNREVIEWED'", None),
    ('documents', 'source_method', "TEXT DEFAULT 'FILESYSTEM_SCAN'", None),
    ('bibliography', 'review_status', "TEXT DEFAULT 'UNREVIEWED'", None),
    ('bibliography', 'needs_review', 'BOOLEAN DEFAULT 1', None),
    ('bibliography', 'reviewed', 'BOOLEAN DEFAULT 0', None),
    ('scholars', 'review_status', "TEXT DEFAULT 'UNREVIEWED'", None),
    ('scholars', 'needs_review', 'BOOLEAN DEFAULT 1', None),
    ('scholars', 'reviewed', 'BOOLEAN DEFAULT 0', None),
    ('scholars', 'source_method', "TEXT DEFAULT 'LLM_ASSISTED'", None),
    ('images', 'confidence', "TEXT DEFAULT 'PROVISIONAL'", None),
    ('images', 'needs_review', 'BOOLEAN DEFAULT 1', None),
    ('timeline_events', 'needs_review', 'BOOLEAN DEFAULT 1', None),
    ('timeline_events', 'source_method', "TEXT DEFAULT 'LLM_ASSISTED'", None),
]


def add_column_if_missing(cur, table, column, col_type, default):
    """Add a column to a table if it doesn't already exist."""
    cur.execute(f"PRAGMA table_info({table})")
    existing = {row[1] for row in cur.fetchall()}
    if column not in existing:
        sql = f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"
        cur.execute(sql)
        return True
    return False


def migrate_annotator_hands(conn):
    """Copy annotator_hands data into the new annotators table."""
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM annotator_hands")
    old_count = cur.fetchone()[0]
    if old_count == 0:
        return 0

    cur.execute("SELECT COUNT(*) FROM annotators")
    new_count = cur.fetchone()[0]
    if new_count > 0:
        return new_count  # Already migrated

    cur.execute("""
        INSERT OR IGNORE INTO annotators
            (hand_label, manuscript_shelfmark, attribution, language,
             ink_color, date_range, school, interests, description,
             is_alchemist, chapter_num, source_method, needs_review)
        SELECT
            hand_label, manuscript_shelfmark, attribution, language,
            ink_color, date_range, school, interests, description,
            is_alchemist, chapter_num, 'LLM_ASSISTED', 1
        FROM annotator_hands
    """)
    conn.commit()
    cur.execute("SELECT COUNT(*) FROM annotators")
    return cur.fetchone()[0]


def migrate_dissertation_refs(conn):
    """Copy dissertation_refs into doc_folio_refs with proper provenance."""
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM doc_folio_refs")
    if cur.fetchone()[0] > 0:
        return  # Already migrated

    # Find the Russell thesis document ID
    cur.execute("SELECT id FROM documents WHERE filename LIKE '%Russell%' LIMIT 1")
    row = cur.fetchone()
    doc_id = row[0] if row else None

    cur.execute("""
        INSERT INTO doc_folio_refs
            (document_id, signature_ref, manuscript_shelfmark,
             page_in_document, context_text, marginal_text,
             ref_type, chapter_num, hand_id, confidence, source_method)
        SELECT
            ?, signature_ref, manuscript_shelfmark,
            thesis_page, context_text, marginal_text,
            ref_type, chapter_num, hand_id, 'PROVISIONAL', 'PDF_EXTRACTION'
        FROM dissertation_refs
    """, (doc_id,))
    conn.commit()


def downgrade_bl_confidence(conn):
    """Downgrade all BL C.60.o.12 matches to LOW confidence.

    Rationale: BL copy is 1545 edition; our signature map is based on 1499.
    Photo numbers assumed to equal folio numbers without manual verification.
    """
    cur = conn.cursor()

    # Downgrade matches involving BL images
    cur.execute("""
        UPDATE matches SET confidence = 'LOW', needs_review = 1
        WHERE image_id IN (
            SELECT i.id FROM images i
            JOIN manuscripts m ON i.manuscript_id = m.id
            WHERE m.shelfmark = 'C.60.o.12'
        ) AND confidence != 'LOW'
    """)
    bl_downgraded = cur.rowcount

    # Also update doc_folio_refs for BL
    cur.execute("""
        UPDATE doc_folio_refs SET confidence = 'PROVISIONAL'
        WHERE manuscript_shelfmark = 'C.60.o.12'
    """)

    conn.commit()
    return bl_downgraded


def import_summaries_to_db(conn):
    """Import scholars/summaries.json into bibliography and scholars tables
    with proper provenance tracking."""
    summaries_path = BASE_DIR / "scholars" / "summaries.json"
    if not summaries_path.exists():
        print("  No summaries.json found, skipping")
        return

    with open(summaries_path, encoding='utf-8') as f:
        summaries = json.load(f)

    cur = conn.cursor()

    for s in summaries:
        author = s.get('author', 'Unknown')
        title = s.get('title', '')
        year = s.get('year')
        journal = s.get('journal', '')
        summary = s.get('summary', '')
        topic = s.get('topic_cluster', '')
        filename = s.get('filename', '')

        # Determine pub_type
        if 'PhD' in journal or 'Thesis' in journal or 'E-Thesis' in journal:
            pub_type = 'thesis'
        elif 'Press' in journal or '(' not in journal:
            pub_type = 'book'
        else:
            pub_type = 'article'

        # Upsert into bibliography
        cur.execute("""
            INSERT OR IGNORE INTO bibliography
                (author, title, year, pub_type, journal_or_publisher,
                 in_collection, collection_filename, hp_relevance,
                 topic_cluster, notes, review_status, needs_review)
            VALUES (?, ?, ?, ?, ?, 1, ?, 'DIRECT', ?, ?, 'UNREVIEWED', 1)
        """, (author, title, str(year) if year else None, pub_type, journal,
              filename, topic, f'LLM-generated summary: {summary[:200]}...'))

        # Upsert into scholars
        cur.execute("""
            INSERT OR IGNORE INTO scholars
                (name, source_method, needs_review, review_status)
            VALUES (?, 'LLM_ASSISTED', 1, 'UNREVIEWED')
        """, (author,))

        # Add topic to junction table
        if topic:
            cur.execute("SELECT id FROM bibliography WHERE author=? AND title=?", (author, title))
            bib_row = cur.fetchone()
            if bib_row:
                for t in topic.split(','):
                    t = t.strip()
                    if t:
                        cur.execute("""
                            INSERT OR IGNORE INTO document_topics
                                (source_table, source_id, topic)
                            VALUES ('bibliography', ?, ?)
                        """, (bib_row[0], t))

    conn.commit()
    print(f"  Imported {len(summaries)} summaries into bibliography/scholars")


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("=== Schema Migration V2 ===\n")

    # Step 1: Create new tables
    print("1. Creating new tables...")
    cur.executescript(MIGRATION_SQL)
    conn.commit()
    print("   Done (annotations, annotators, doc_folio_refs, dictionary_terms,")
    print("         dictionary_term_links, document_topics)")

    # Step 2: Add columns to existing tables
    print("\n2. Adding review/provenance columns to existing tables...")
    added = 0
    for table, column, col_type, default in ALTER_COLUMNS:
        if add_column_if_missing(cur, table, column, col_type, default):
            print(f"   + {table}.{column}")
            added += 1
    conn.commit()
    print(f"   Added {added} new columns")

    # Step 3: Migrate annotator_hands → annotators
    print("\n3. Migrating annotator_hands -> annotators...")
    n = migrate_annotator_hands(conn)
    print(f"   {n} annotators in normalized table")

    # Step 4: Migrate dissertation_refs → doc_folio_refs
    print("\n4. Migrating dissertation_refs -> doc_folio_refs...")
    migrate_dissertation_refs(conn)
    cur.execute("SELECT COUNT(*) FROM doc_folio_refs")
    print(f"   {cur.fetchone()[0]} folio references migrated")

    # Step 5: Downgrade BL confidence
    print("\n5. Downgrading BL C.60.o.12 matches to LOW confidence...")
    n = downgrade_bl_confidence(conn)
    print(f"   {n} matches downgraded")

    # Step 6: Import summaries.json with provenance
    print("\n6. Importing summaries.json into DB with provenance tracking...")
    import_summaries_to_db(conn)

    # Step 7: Summary
    print("\n=== Migration Summary ===")
    tables = [
        'documents', 'manuscripts', 'images', 'signature_map',
        'dissertation_refs', 'doc_folio_refs', 'matches',
        'annotator_hands', 'annotators', 'annotations',
        'bibliography', 'scholars', 'scholar_works',
        'timeline_events', 'dictionary_terms', 'dictionary_term_links',
        'document_topics', 'schema_version'
    ]
    for t in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            print(f"  {t}: {cur.fetchone()[0]} rows")
        except sqlite3.OperationalError:
            print(f"  {t}: (not found)")

    # Confidence distribution
    print("\nMatch confidence distribution:")
    cur.execute("SELECT confidence, COUNT(*) FROM matches GROUP BY confidence ORDER BY confidence")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    conn.close()
    print("\nMigration complete.")


if __name__ == "__main__":
    main()
