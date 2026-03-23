"""
Stage 5: Export database tables to JSON for site rendering.

Produces:
- Per-table exports in data/exports/
- Page-specific combined exports for each site page
"""

import os
import sys
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.db import init_db, export_table_json, query_all, get_connection

EXPORTS_DIR = os.path.join(PROJECT_ROOT, "data", "exports")

TABLES = [
    "source_documents",
    "source_excerpts",
    "life_events",
    "work_records",
    "memoir_episodes",
    "digby_theme_records",
    "citations",
    "hypnerotomachia_findings",
    "hypnerotomachia_evidence",
]

# Page-specific export definitions
PAGE_EXPORTS = {
    "digby_home": {
        "tables": ["life_events", "work_records"],
        "description": "Overview data for the Digby home page",
    },
    "life_works": {
        "tables": ["life_events", "work_records", "citations"],
        "description": "Life events and works with citations",
    },
    "memoir": {
        "tables": ["memoir_episodes", "citations"],
        "description": "Memoir episodes with citations",
    },
    "pirate": {
        "tables": ["digby_theme_records", "citations"],
        "filter": {"digby_theme_records": "theme = 'pirate'"},
        "description": "Pirate theme records",
    },
    "alchemist": {
        "tables": ["digby_theme_records", "citations"],
        "filter": {"digby_theme_records": "theme = 'alchemist_natural_philosopher'"},
        "description": "Alchemist theme records",
    },
    "courtier": {
        "tables": ["digby_theme_records", "citations"],
        "filter": {"digby_theme_records": "theme = 'courtier_legal_thinker'"},
        "description": "Courtier theme records",
    },
    "hypnerotomachia": {
        "tables": ["hypnerotomachia_findings", "hypnerotomachia_evidence", "citations"],
        "description": "Hypnerotomachia findings and evidence",
    },
    "sources": {
        "tables": ["source_documents"],
        "description": "Source bibliography",
    },
}


def export_all():
    """Export all tables and page-specific data."""
    init_db()
    os.makedirs(EXPORTS_DIR, exist_ok=True)

    # Export each table
    print("Exporting tables:")
    for table in TABLES:
        path = os.path.join(EXPORTS_DIR, f"{table}.json")
        count = export_table_json(table, path)
        print(f"  {table}: {count} records")

    # Export page-specific data
    print("\nExporting page data:")
    conn = get_connection()
    for page, config in PAGE_EXPORTS.items():
        page_data = {}
        for table in config["tables"]:
            if "filter" in config and table in config["filter"]:
                where = config["filter"][table]
                rows = conn.execute(
                    f"SELECT * FROM {table} WHERE {where}"
                ).fetchall()
                page_data[table] = [dict(r) for r in rows]
            else:
                page_data[table] = query_all(table)

        path = os.path.join(EXPORTS_DIR, f"page_{page}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(page_data, f, indent=2, ensure_ascii=False)
        total = sum(len(v) for v in page_data.values())
        print(f"  {page}: {total} records across {len(config['tables'])} tables")

    conn.close()
    print("\nExport complete.")


if __name__ == "__main__":
    export_all()
