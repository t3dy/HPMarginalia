"""Validation and QA: check data integrity, flag issues, produce audit report."""

import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"
SITE_DIR = BASE_DIR / "site"


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    issues = []
    warnings = []
    stats = {}

    print("=== Validation & QA ===\n")

    # 1. Duplicate slugs in dictionary
    print("1. Checking for duplicate dictionary slugs...")
    cur.execute("""
        SELECT slug, COUNT(*) FROM dictionary_terms
        GROUP BY slug HAVING COUNT(*) > 1
    """)
    dupes = cur.fetchall()
    if dupes:
        for d in dupes:
            issues.append(f"DUPLICATE SLUG: dictionary term '{d[0]}' appears {d[1]} times")
    else:
        print("   OK - no duplicates")

    # 2. Terms without category
    print("2. Checking terms without category...")
    cur.execute("SELECT slug FROM dictionary_terms WHERE category IS NULL OR category = ''")
    no_cat = cur.fetchall()
    if no_cat:
        for t in no_cat:
            issues.append(f"MISSING CATEGORY: term '{t[0]}' has no category")
    else:
        print("   OK - all terms have categories")

    # 3. Scholar pages with no works
    print("3. Checking scholars with no works...")
    cur.execute("""
        SELECT s.name FROM scholars s
        LEFT JOIN scholar_works sw ON s.id = sw.scholar_id
        WHERE sw.scholar_id IS NULL
    """)
    no_works = cur.fetchall()
    stats['scholars_no_works'] = len(no_works)
    if no_works:
        for s in no_works:
            warnings.append(f"SCHOLAR NO WORKS: '{s[0]}' has no linked bibliography entries")
    print(f"   {len(no_works)} scholars without linked works (warning, not error)")

    # 4. Folio refs that don't resolve to images
    print("4. Checking unresolved folio references...")
    cur.execute("""
        SELECT r.id, r.signature_ref, r.thesis_page
        FROM dissertation_refs r
        LEFT JOIN matches m ON m.ref_id = r.id
        WHERE m.id IS NULL
    """)
    unmatched = cur.fetchall()
    stats['unmatched_refs'] = len(unmatched)
    if unmatched:
        warnings.append(f"UNMATCHED REFS: {len(unmatched)} dissertation references have no image match")
    print(f"   {len(unmatched)} unmatched references")

    # 5. Missing linked records in dictionary_term_links
    print("5. Checking dictionary link integrity...")
    cur.execute("""
        SELECT l.id, l.term_id, l.linked_term_id
        FROM dictionary_term_links l
        LEFT JOIN dictionary_terms t1 ON l.term_id = t1.id
        LEFT JOIN dictionary_terms t2 ON l.linked_term_id = t2.id
        WHERE t1.id IS NULL OR t2.id IS NULL
    """)
    broken_links = cur.fetchall()
    if broken_links:
        issues.append(f"BROKEN LINKS: {len(broken_links)} dictionary links point to missing terms")
    else:
        print("   OK - all links resolve")

    # 6. BL confidence check
    print("6. Verifying BL confidence downgrade...")
    cur.execute("""
        SELECT mat.confidence, COUNT(*)
        FROM matches mat
        JOIN images i ON mat.image_id = i.id
        JOIN manuscripts m ON i.manuscript_id = m.id
        WHERE m.shelfmark = 'C.60.o.12'
        GROUP BY mat.confidence
    """)
    bl_conf = cur.fetchall()
    for conf, count in bl_conf:
        if conf in ('HIGH', 'MEDIUM'):
            issues.append(f"BL CONFIDENCE: {count} BL matches still at {conf} (should be LOW)")
        else:
            print(f"   BL matches: {count} at {conf}")

    # 7. Review status summary
    print("7. Review status audit...")
    review_tables = [
        ('bibliography', 'needs_review'),
        ('scholars', 'needs_review'),
        ('dictionary_terms', 'needs_review'),
        ('matches', 'needs_review'),
    ]
    for table, col in review_tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table} WHERE {col} = 1")
            needs = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            total = cur.fetchone()[0]
            pct = (needs * 100 // total) if total > 0 else 0
            stats[f'{table}_needs_review'] = needs
            print(f"   {table}: {needs}/{total} need review ({pct}%)")
        except:
            pass

    # 8. Site file counts
    print("8. Checking generated site files...")
    site_counts = {
        'scholar pages': len(list((SITE_DIR / 'scholar').glob('*.html'))) if (SITE_DIR / 'scholar').exists() else 0,
        'dictionary pages': len(list((SITE_DIR / 'dictionary').glob('*.html'))) if (SITE_DIR / 'dictionary').exists() else 0,
        'marginalia pages': len(list((SITE_DIR / 'marginalia').glob('*.html'))) if (SITE_DIR / 'marginalia').exists() else 0,
    }
    for label, count in site_counts.items():
        print(f"   {label}: {count}")
        stats[label] = count

    # 9. Check for empty HTML files
    print("9. Checking for empty HTML files...")
    empty_count = 0
    for html in SITE_DIR.rglob('*.html'):
        if html.stat().st_size < 100:
            issues.append(f"EMPTY FILE: {html.relative_to(BASE_DIR)}")
            empty_count += 1
    if empty_count == 0:
        print("   OK - no empty files")

    # 10. Data.json integrity
    print("10. Checking data.json...")
    import json
    data_path = SITE_DIR / 'data.json'
    if data_path.exists():
        with open(data_path, encoding='utf-8') as f:
            data = json.load(f)
        n_entries = len(data.get('entries', []))
        n_low = sum(1 for e in data['entries'] if e.get('confidence') == 'LOW')
        print(f"   {n_entries} entries, {n_low} LOW confidence")
        stats['data_json_entries'] = n_entries
        if 'provenance' not in data:
            warnings.append("DATA.JSON: missing provenance field")
    else:
        issues.append("DATA.JSON: file not found")

    # === Produce Report ===
    print("\n" + "=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)

    if issues:
        print(f"\n  ISSUES ({len(issues)}):")
        for i in issues:
            print(f"    [!] {i}")
    else:
        print("\n  No critical issues found.")

    if warnings:
        print(f"\n  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"    [?] {w}")

    # Write audit report
    report_path = BASE_DIR / "AUDIT_REPORT.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# Audit Report\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")

        f.write("## What Changed (V2 Migration)\n\n")
        f.write("### Schema\n")
        f.write("- Added `annotations` table for first-class marginal note records\n")
        f.write("- Added `annotators` table (normalized from `annotator_hands`)\n")
        f.write("- Added `doc_folio_refs` table (generalized from `dissertation_refs`)\n")
        f.write("- Added `dictionary_terms` and `dictionary_term_links` tables\n")
        f.write("- Added `document_topics` junction table for multi-value topic clusters\n")
        f.write("- Added `review_status`, `needs_review`, `reviewed`, `source_method`, ")
        f.write("`confidence`, and `notes` columns across existing tables\n")
        f.write("- Downgraded all BL C.60.o.12 matches from MEDIUM to LOW confidence\n\n")

        f.write("### Site\n")
        f.write(f"- {site_counts.get('scholar pages', 0)} scholar profile pages (DB-driven, with review badges)\n")
        f.write(f"- {site_counts.get('dictionary pages', 0)} dictionary term pages (37 terms, 6 categories, 76 links)\n")
        f.write(f"- {site_counts.get('marginalia pages', 0)} marginalia folio detail pages (with annotator hand info)\n")
        f.write("- Site-wide navigation bar (Home, Marginalia, Scholars, Dictionary, About)\n")
        f.write("- About page with database statistics and rebuild instructions\n")
        f.write("- Confidence badges (HIGH/MEDIUM/LOW/PROVISIONAL) on all matches\n")
        f.write("- Review badges (Unreviewed) on LLM-assisted content\n\n")

        f.write("## What Remains Provisional\n\n")
        f.write("| Data Category | Total | Needs Review | Source Method |\n")
        f.write("|---|---|---|---|\n")
        f.write(f"| Bibliography entries | 88 | {stats.get('bibliography_needs_review', '?')} | LLM-assisted |\n")
        f.write(f"| Scholar profiles | 52 | {stats.get('scholars_needs_review', '?')} | LLM-assisted |\n")
        f.write(f"| Dictionary terms | 37 | {stats.get('dictionary_terms_needs_review', '?')} | LLM-assisted |\n")
        f.write(f"| Image matches | 610 | {stats.get('matches_needs_review', '?')} | Algorithmic (folio mapping) |\n")
        f.write(f"| BL matches specifically | 218 | 218 | LOW confidence (1545 edition offset) |\n\n")

        f.write("## What Still Needs Human Review\n\n")
        f.write("### Critical\n")
        f.write("1. **BL C.60.o.12 photo-to-folio mapping**: Verify that sequential photo numbers\n")
        f.write("   correspond to folio numbers. The BL copy is the 1545 edition; layout may differ\n")
        f.write("   from the 1499 signature map by a few leaves.\n")
        f.write("2. **Article summaries**: All 34 summaries were generated by Claude and have not\n")
        f.write("   been checked for factual accuracy, misattribution, or hallucination.\n")
        f.write("3. **Hand attributions**: Derived from reading Russell's prose in conversation.\n")
        f.write("   The signature-to-hand mapping rules are approximate.\n\n")

        f.write("### Important\n")
        f.write("4. **Scholar metadata**: Birth/death years, nationalities, and institutional\n")
        f.write("   affiliations should be cross-referenced against VIAF/WorldCat.\n")
        f.write("5. **Dictionary definitions**: Especially the alchemical and architectural terms\n")
        f.write("   should be reviewed by a domain specialist.\n")
        f.write("6. **Mislabeled files**: Jarzombek (De pictura, not HP) and Canone/Spruit\n")
        f.write("   (Poncet on Botticelli, not emblematics) were identified by LLM and\n")
        f.write("   should be confirmed.\n\n")

        f.write("### Nice to Have\n")
        f.write("7. **Timeline event dates**: Some date ranges are approximate.\n")
        f.write("8. **Topic cluster assignments**: Some works could belong to multiple clusters.\n")
        f.write("   The `document_topics` junction table supports this but most entries\n")
        f.write("   have only one topic assigned.\n\n")

        if issues:
            f.write("## Validation Issues\n\n")
            for i in issues:
                f.write(f"- **{i}**\n")
            f.write("\n")

        if warnings:
            f.write("## Validation Warnings\n\n")
            for w in warnings:
                f.write(f"- {w}\n")
            f.write("\n")

        f.write("## How to Rebuild\n\n")
        f.write("```bash\n")
        f.write("python scripts/migrate_v2.py        # Schema migration (idempotent)\n")
        f.write("python scripts/seed_dictionary.py   # Dictionary terms (idempotent)\n")
        f.write("python scripts/build_site.py        # Generate all HTML + JSON\n")
        f.write("python scripts/validate.py          # Run this audit\n")
        f.write("```\n")

    print(f"\nAudit report written to {report_path}")
    conn.close()


if __name__ == "__main__":
    main()
