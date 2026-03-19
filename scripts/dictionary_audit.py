"""Dictionary coverage audit: identifies terms needing improvement.

Checks for:
- Missing fields (significance, source_documents, etc.)
- Terms stuck at DRAFT status
- Duplicate slugs
- Orphaned links (links to nonexistent terms)
- Terms with no related links
- Coverage by category

Outputs JSON report to staging/dictionary_audit.json and console summary.
"""

import sqlite3
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"
STAGING_DIR = BASE_DIR / "staging"


def audit():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    report = {
        'total_terms': 0,
        'by_status': {},
        'by_category': {},
        'missing_fields': [],
        'duplicate_slugs': [],
        'orphaned_links': [],
        'terms_without_links': [],
        'weak_terms': [],
        'summary': {},
    }

    # Total terms
    cur.execute("SELECT COUNT(*) FROM dictionary_terms")
    report['total_terms'] = cur.fetchone()[0]

    # By status
    cur.execute("SELECT review_status, COUNT(*) FROM dictionary_terms GROUP BY review_status")
    report['by_status'] = {row[0]: row[1] for row in cur.fetchall()}

    # By category
    cur.execute("SELECT category, COUNT(*) FROM dictionary_terms GROUP BY category ORDER BY COUNT(*) DESC")
    report['by_category'] = {row[0]: row[1] for row in cur.fetchall()}

    # Check for missing fields on each term
    cur.execute("""
        SELECT slug, label, category, definition_short, definition_long,
               source_basis, review_status, significance_to_hp,
               significance_to_scholarship, source_documents, source_page_refs,
               source_method, confidence
        FROM dictionary_terms ORDER BY slug
    """)

    important_fields = [
        'definition_long', 'source_basis', 'significance_to_hp',
        'significance_to_scholarship', 'source_documents'
    ]

    for row in cur.fetchall():
        missing = []
        for field in important_fields:
            val = row[field] if field in row.keys() else None
            if not val or (isinstance(val, str) and val.strip() == ''):
                missing.append(field)

        if missing:
            report['missing_fields'].append({
                'slug': row['slug'],
                'label': row['label'],
                'category': row['category'],
                'review_status': row['review_status'],
                'missing': missing,
            })

        # "Weak" = DRAFT + missing 2+ important fields
        if row['review_status'] == 'DRAFT' and len(missing) >= 2:
            report['weak_terms'].append({
                'slug': row['slug'],
                'label': row['label'],
                'missing_count': len(missing),
                'missing': missing,
            })

    # Duplicate slugs
    cur.execute("""
        SELECT slug, COUNT(*) FROM dictionary_terms
        GROUP BY slug HAVING COUNT(*) > 1
    """)
    report['duplicate_slugs'] = [row[0] for row in cur.fetchall()]

    # Orphaned links
    cur.execute("""
        SELECT l.id, l.term_id, l.linked_term_id
        FROM dictionary_term_links l
        LEFT JOIN dictionary_terms t1 ON l.term_id = t1.id
        LEFT JOIN dictionary_terms t2 ON l.linked_term_id = t2.id
        WHERE t1.id IS NULL OR t2.id IS NULL
    """)
    report['orphaned_links'] = [dict(row) for row in cur.fetchall()]

    # Terms without any links
    cur.execute("""
        SELECT t.slug, t.label FROM dictionary_terms t
        LEFT JOIN dictionary_term_links l ON t.id = l.term_id
        WHERE l.id IS NULL
    """)
    report['terms_without_links'] = [{'slug': row[0], 'label': row[1]} for row in cur.fetchall()]

    # Summary
    report['summary'] = {
        'total_terms': report['total_terms'],
        'draft_count': report['by_status'].get('DRAFT', 0),
        'verified_count': report['by_status'].get('VERIFIED', 0),
        'terms_with_missing_fields': len(report['missing_fields']),
        'weak_terms_count': len(report['weak_terms']),
        'duplicate_slugs_count': len(report['duplicate_slugs']),
        'orphaned_links_count': len(report['orphaned_links']),
        'terms_without_links_count': len(report['terms_without_links']),
        'categories': len(report['by_category']),
    }

    conn.close()

    # Write report
    STAGING_DIR.mkdir(exist_ok=True)
    report_path = STAGING_DIR / "dictionary_audit.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Console output
    print("=== Dictionary Audit ===\n")
    print(f"Total terms: {report['total_terms']}")
    print(f"By status: {report['by_status']}")
    print(f"Categories: {len(report['by_category'])}")
    for cat, count in report['by_category'].items():
        print(f"  {cat}: {count}")
    print(f"\nTerms with missing important fields: {len(report['missing_fields'])}")
    print(f"Weak terms (DRAFT + 2+ missing): {len(report['weak_terms'])}")
    if report['weak_terms']:
        for wt in report['weak_terms']:
            print(f"  - {wt['slug']}: missing {', '.join(wt['missing'])}")
    print(f"Duplicate slugs: {len(report['duplicate_slugs'])}")
    print(f"Orphaned links: {len(report['orphaned_links'])}")
    print(f"Terms without links: {len(report['terms_without_links'])}")
    if report['terms_without_links']:
        for t in report['terms_without_links']:
            print(f"  - {t['slug']}")
    print(f"\nReport written to: {report_path}")
    return report


if __name__ == "__main__":
    audit()
