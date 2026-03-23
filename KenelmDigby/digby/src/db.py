"""
Database setup and access for the Digby module.

SQLite database with 9 tables matching the 9 data models.
JSON exports supported for site rendering.
"""

import sqlite3
import os
import json
from pathlib import Path

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "digby.db")


def get_connection(db_path: str = None) -> sqlite3.Connection:
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(db_path: str = None):
    """Create all tables. Safe to call repeatedly (IF NOT EXISTS)."""
    conn = get_connection(db_path)
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS source_documents (
        id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        filepath TEXT NOT NULL,
        title TEXT NOT NULL,
        file_type TEXT NOT NULL CHECK(file_type IN ('pdf','txt','md','epub','xlsx','pptx')),
        author TEXT,
        year INTEGER,
        journal TEXT,
        doi TEXT,
        page_count INTEGER,
        text_extracted INTEGER DEFAULT 0,
        extracted_text_path TEXT,
        ingested_at TEXT,
        notes TEXT
    );

    CREATE TABLE IF NOT EXISTS source_excerpts (
        id TEXT PRIMARY KEY,
        source_document_id TEXT NOT NULL REFERENCES source_documents(id),
        text TEXT NOT NULL,
        page_start INTEGER,
        page_end INTEGER,
        section_heading TEXT,
        themes TEXT,
        source_method TEXT DEFAULT 'CORPUS_EXTRACTION',
        review_status TEXT DEFAULT 'DRAFT',
        created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS life_events (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        date_display TEXT NOT NULL,
        year INTEGER,
        description TEXT DEFAULT '',
        life_phase TEXT,
        location TEXT,
        people_involved TEXT,
        citation_ids TEXT,
        source_method TEXT DEFAULT 'CORPUS_EXTRACTION',
        review_status TEXT DEFAULT 'DRAFT',
        confidence TEXT DEFAULT 'MEDIUM'
    );

    CREATE TABLE IF NOT EXISTS work_records (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        year INTEGER,
        work_type TEXT,
        subject TEXT,
        description TEXT DEFAULT '',
        significance TEXT,
        citation_ids TEXT,
        source_method TEXT DEFAULT 'CORPUS_EXTRACTION',
        review_status TEXT DEFAULT 'DRAFT'
    );

    CREATE TABLE IF NOT EXISTS memoir_episodes (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        episode_number INTEGER,
        date_display TEXT,
        year INTEGER,
        summary TEXT DEFAULT '',
        key_events TEXT,
        people TEXT,
        places TEXT,
        themes TEXT,
        citation_ids TEXT,
        source_method TEXT DEFAULT 'CORPUS_EXTRACTION',
        review_status TEXT DEFAULT 'DRAFT'
    );

    CREATE TABLE IF NOT EXISTS digby_theme_records (
        id TEXT PRIMARY KEY,
        theme TEXT NOT NULL,
        title TEXT NOT NULL,
        summary TEXT DEFAULT '',
        key_details TEXT,
        people TEXT,
        places TEXT,
        date_display TEXT,
        year INTEGER,
        significance TEXT,
        citation_ids TEXT,
        source_method TEXT DEFAULT 'CORPUS_EXTRACTION',
        review_status TEXT DEFAULT 'DRAFT',
        confidence TEXT DEFAULT 'MEDIUM'
    );

    CREATE TABLE IF NOT EXISTS citations (
        id TEXT PRIMARY KEY,
        source_document_id TEXT NOT NULL REFERENCES source_documents(id),
        excerpt_id TEXT,
        page_or_location TEXT,
        quote_fragment TEXT,
        context TEXT,
        created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS hypnerotomachia_findings (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        claim TEXT NOT NULL,
        description TEXT DEFAULT '',
        evidence_excerpt TEXT,
        related_concepts TEXT,
        significance TEXT,
        citation_ids TEXT,
        source_method TEXT DEFAULT 'CORPUS_EXTRACTION',
        review_status TEXT DEFAULT 'DRAFT',
        confidence TEXT DEFAULT 'MEDIUM'
    );

    CREATE TABLE IF NOT EXISTS hypnerotomachia_evidence (
        id TEXT PRIMARY KEY,
        finding_id TEXT NOT NULL REFERENCES hypnerotomachia_findings(id),
        excerpt TEXT NOT NULL,
        source TEXT NOT NULL,
        page_or_location TEXT,
        notes TEXT
    );
    """)

    conn.commit()
    conn.close()


def insert_record(table: str, record_dict: dict, db_path: str = None):
    """Insert a record dict into the given table."""
    conn = get_connection(db_path)
    cols = ", ".join(record_dict.keys())
    placeholders = ", ".join(["?"] * len(record_dict))
    sql = f"INSERT OR REPLACE INTO {table} ({cols}) VALUES ({placeholders})"
    conn.execute(sql, list(record_dict.values()))
    conn.commit()
    conn.close()


def query_all(table: str, db_path: str = None) -> list[dict]:
    """Return all rows from a table as dicts."""
    conn = get_connection(db_path)
    rows = conn.execute(f"SELECT * FROM {table}").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def export_table_json(table: str, output_path: str, db_path: str = None):
    """Export a table to a JSON file."""
    data = query_all(table, db_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return len(data)


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
