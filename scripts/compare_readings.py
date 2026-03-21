#!/usr/bin/env python3
"""compare_readings.py — Compare image_readings against canonical DB records.

Systematically checks what image reading found vs what the database
already contains. Identifies:
  - Matches (vision confirms existing record)
  - Gaps (existing record has no vision confirmation)
  - Surprises (vision found something not in canonical tables)
  - Discrepancies (vision contradicts existing record)

Usage:
    python scripts/compare_readings.py woodcuts
    python scripts/compare_readings.py annotations --page 28
    python scripts/compare_readings.py offset
    python scripts/compare_readings.py density
    python scripts/compare_readings.py summary
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "hp.db"


def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def compare_woodcuts(conn):
    """Compare detected woodcuts (image_readings) vs canonical (woodcuts table)."""

    # Get all canonical woodcuts with BL photo numbers
    canonical = {}
    for row in conn.execute(
        "SELECT id, bl_photo_number, page_1545, title, description FROM woodcuts"
    ).fetchall():
        if row["bl_photo_number"]:
            canonical[row["bl_photo_number"]] = dict(row)

    # Get all vision-detected woodcuts
    detected = {}
    for row in conn.execute("""
        SELECT ir.id, json_extract(ir.raw_json, '$.photo_number') as photo,
               ir.page_number_read, ir.woodcut_description, ir.concordance_status
        FROM image_readings ir
        WHERE ir.has_woodcut = 1 AND ir.phase = 1
    """).fetchall():
        photo = int(row["photo"])
        detected[photo] = dict(row)

    # Classify
    matches = []       # In both canonical and detected
    canonical_only = [] # In canonical but NOT detected (gap)
    detected_only = []  # Detected but NOT in canonical (surprise)

    all_photos = set(canonical.keys()) | set(detected.keys())

    for photo in sorted(all_photos):
        in_canon = photo in canonical
        in_detect = photo in detected

        if in_canon and in_detect:
            matches.append({
                "photo": photo,
                "canonical": canonical[photo],
                "detected": detected[photo],
            })
        elif in_canon and not in_detect:
            canonical_only.append(canonical[photo])
        elif not in_canon and in_detect:
            detected_only.append(detected[photo])

    # Report
    print(f"\n=== WOODCUT COMPARISON ===\n")
    print(f"Canonical woodcuts (in table):  {len(canonical)}")
    print(f"Vision-detected woodcuts:       {len(detected)}")
    print(f"Matches (both):                 {len(matches)}")
    print(f"Canonical only (not detected):  {len(canonical_only)}")
    print(f"Detected only (new):            {len(detected_only)}")

    if canonical_only:
        print(f"\n--- Canonical woodcuts NOT detected by vision ---")
        for c in canonical_only:
            print(f"  Photo {c['bl_photo_number']}: {c['title']}")

    if detected_only:
        print(f"\n--- Newly detected woodcuts (not in canonical table) ---")
        for d in detected_only:
            desc = (d.get("woodcut_description") or "")[:60]
            print(f"  Photo {d['photo']}: p.{d.get('page_number_read', '?')} — {desc}")

    if matches:
        print(f"\n--- Confirmed matches ---")
        for m in matches[:10]:
            print(f"  Photo {m['photo']}: canonical='{m['canonical']['title'][:40]}' / "
                  f"detected='{(m['detected'].get('woodcut_description') or '')[:40]}'")
        if len(matches) > 10:
            print(f"  ... and {len(matches) - 10} more")

    return {
        "matches": len(matches),
        "canonical_only": len(canonical_only),
        "detected_only": len(detected_only),
    }


def compare_offset(conn):
    """Report on BL offset verification results."""
    rows = conn.execute("""
        SELECT page_number_read, page_number_expected, page_number_match,
               json_extract(raw_json, '$.photo_number') as photo
        FROM image_readings
        WHERE phase = 1 AND page_number_read IS NOT NULL
        ORDER BY CAST(json_extract(raw_json, '$.photo_number') AS INTEGER)
    """).fetchall()

    confirmed = sum(1 for r in rows if r["page_number_match"])
    mismatches = [r for r in rows if r["page_number_match"] == 0]
    unreadable = conn.execute("""
        SELECT COUNT(*) as c FROM image_readings
        WHERE phase = 1 AND page_number_read IS NULL
    """).fetchone()["c"]

    print(f"\n=== OFFSET VERIFICATION ===\n")
    print(f"Total Phase 1 readings:    189")
    print(f"Page numbers readable:     {len(rows)}")
    print(f"Offset confirmed:          {confirmed}/{len(rows)}")
    print(f"Mismatches:                {len(mismatches)}")
    print(f"Unreadable page numbers:   {unreadable}")
    print(f"Formula:                   page = photo_number - 13")

    if mismatches:
        print(f"\n--- MISMATCHES ---")
        for m in mismatches:
            print(f"  Photo {m['photo']}: read={m['page_number_read']}, "
                  f"expected={m['page_number_expected']}")
    else:
        print(f"\n  [OK] Zero mismatches. Offset formula fully confirmed.")

    return {"confirmed": confirmed, "mismatches": len(mismatches)}


def compare_annotations(conn, page=None):
    """Compare annotation presence (image_readings) vs canonical annotations."""

    # Get pages that have canonical annotations
    canon_pages = set()
    for row in conn.execute("""
        SELECT DISTINCT folio_number FROM annotations
        WHERE folio_number IS NOT NULL AND manuscript_id = 1
    """).fetchall():
        canon_pages.add(row["folio_number"])

    # Get pages where vision detected annotations
    vision_pages = {}
    for row in conn.execute("""
        SELECT ir.page_number_read as page, ir.has_annotations,
               ir.annotation_density,
               json_extract(ir.raw_json, '$.photo_number') as photo
        FROM image_readings ir
        WHERE ir.phase = 2 AND ir.has_annotations = 1
    """).fetchall():
        if row["page"]:
            vision_pages[row["page"]] = dict(row)

    vision_page_set = set(vision_pages.keys())

    both = canon_pages & vision_page_set
    canon_only = canon_pages - vision_page_set
    vision_only = vision_page_set - canon_pages

    print(f"\n=== ANNOTATION COMPARISON ===\n")
    print(f"Pages with canonical annotations:  {len(canon_pages)}")
    print(f"Pages with vision-detected annot:  {len(vision_page_set)}")
    print(f"Both (confirmed):                  {len(both)}")
    print(f"Canonical only (not vision-seen):   {len(canon_only)}")
    print(f"Vision only (undocumented):         {len(vision_only)}")

    if canon_only:
        print(f"\n--- Canonical annotations on pages NOT detected by vision ---")
        for p in sorted(canon_only):
            print(f"  Page {p}")

    if vision_only and len(vision_only) <= 30:
        print(f"\n--- Vision-detected annotations NOT in canonical table ---")
        for p in sorted(vision_only):
            v = vision_pages[p]
            print(f"  Page {p} (photo {v['photo']}): density={v['annotation_density']}")

    return {
        "both": len(both),
        "canonical_only": len(canon_only),
        "vision_only": len(vision_only),
    }


def compare_density(conn):
    """Report annotation density distribution from Phase 2."""
    rows = conn.execute("""
        SELECT annotation_density, COUNT(*) as c
        FROM image_readings
        WHERE phase = 2
        GROUP BY annotation_density
        ORDER BY
            CASE annotation_density
                WHEN 'HEAVY' THEN 1
                WHEN 'MODERATE' THEN 2
                WHEN 'LIGHT' THEN 3
                ELSE 4
            END
    """).fetchall()

    print(f"\n=== ANNOTATION DENSITY DISTRIBUTION ===\n")
    for row in rows:
        density = row["annotation_density"] or "NONE"
        bar = "█" * (row["c"] // 2)
        print(f"  {density:>10}: {row['c']:>4}  {bar}")

    # Languages
    langs = {}
    for row in conn.execute("""
        SELECT languages_detected FROM image_readings
        WHERE phase = 2 AND languages_detected IS NOT NULL
    """).fetchall():
        for lang in json.loads(row["languages_detected"]):
            langs[lang] = langs.get(lang, 0) + 1

    if langs:
        print(f"\n--- Languages detected across all pages ---")
        for lang, count in sorted(langs.items(), key=lambda x: -x[1]):
            print(f"  {lang}: {count} pages")


def summary(conn):
    """Print full comparison summary."""
    print("=" * 60)
    print("   HP MARGINALIA — IMAGE READING vs CANONICAL DATA")
    print("=" * 60)

    r_offset = compare_offset(conn)
    r_woodcuts = compare_woodcuts(conn)
    r_annot = compare_annotations(conn)
    compare_density(conn)

    # Phase 3 stats
    p3 = conn.execute("""
        SELECT COUNT(*) as c FROM image_readings WHERE phase = 3
    """).fetchone()["c"]
    discrepancies = conn.execute("""
        SELECT COUNT(*) as c FROM image_readings
        WHERE phase = 3 AND raw_json LIKE '%discrepanc%'
    """).fetchone()["c"]

    print(f"\n=== PHASE 3 DEEP READING ===\n")
    print(f"  Pages deep-read:       {p3}")
    print(f"  With discrepancies:    {discrepancies}")

    print(f"\n{'=' * 60}")
    print(f"   SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Offset:     {r_offset['confirmed']} confirmed, "
          f"{r_offset['mismatches']} mismatches")
    print(f"  Woodcuts:   {r_woodcuts['matches']} matched, "
          f"{r_woodcuts['detected_only']} new, "
          f"{r_woodcuts['canonical_only']} unconfirmed")
    print(f"  Annotations: {r_annot['both']} matched, "
          f"{r_annot['vision_only']} undocumented, "
          f"{r_annot['canonical_only']} unconfirmed")


def main():
    parser = argparse.ArgumentParser(
        description="Compare image_readings against canonical DB records"
    )
    parser.add_argument(
        "command",
        choices=["woodcuts", "annotations", "offset", "density", "summary"],
        help="What to compare"
    )
    parser.add_argument("--page", type=int, help="Filter to specific page")

    args = parser.parse_args()
    conn = get_conn()

    if args.command == "woodcuts":
        compare_woodcuts(conn)
    elif args.command == "annotations":
        compare_annotations(conn, args.page)
    elif args.command == "offset":
        compare_offset(conn)
    elif args.command == "density":
        compare_density(conn)
    elif args.command == "summary":
        summary(conn)

    conn.close()


if __name__ == "__main__":
    main()
