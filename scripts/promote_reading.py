#!/usr/bin/env python3
"""promote_reading.py — Safely promote image_readings to canonical tables.

Moves reviewed findings from image_readings into woodcuts, annotations,
or symbol_occurrences with full audit trail. Never overwrites existing
canonical data. Never promotes UNVERIFIED readings without --force.

Usage:
    python scripts/promote_reading.py --list-candidates woodcuts
    python scripts/promote_reading.py --list-candidates annotations
    python scripts/promote_reading.py --promote woodcut --reading-id 42
    python scripts/promote_reading.py --promote woodcut --reading-id 42 --dry-run
    python scripts/promote_reading.py --batch-promote woodcuts --reviewed-only
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "hp.db"


def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def list_woodcut_candidates(conn, reviewed_only=False):
    """List image_readings with woodcuts that are not yet in the canonical table."""
    query = """
        SELECT ir.id as reading_id, ir.image_id, ir.phase,
               ir.has_woodcut, ir.woodcut_description,
               ir.concordance_status, ir.reviewed,
               ir.page_number_read as page_number,
               i.master_path,
               json_extract(ir.raw_json, '$.photo_number') as photo_number
        FROM image_readings ir
        JOIN images i ON ir.image_id = i.id
        WHERE ir.has_woodcut = 1
          AND ir.phase = 1
          AND CAST(json_extract(ir.raw_json, '$.photo_number') AS INTEGER) NOT IN (
              SELECT bl_photo_number FROM woodcuts
              WHERE bl_photo_number IS NOT NULL
          )
    """
    if reviewed_only:
        query += " AND ir.reviewed = 1"
    query += " ORDER BY CAST(json_extract(ir.raw_json, '$.photo_number') AS INTEGER)"

    rows = conn.execute(query).fetchall()
    return rows


def list_annotation_candidates(conn, reviewed_only=False):
    """List Phase 3 deep readings with transcription data not yet in annotations."""
    query = """
        SELECT ir.id as reading_id, ir.image_id, ir.phase,
               ir.deep_reading_json,
               ir.concordance_status, ir.reviewed,
               ir.page_number_read as page_number,
               json_extract(ir.raw_json, '$.photo_number') as photo_number
        FROM image_readings ir
        WHERE ir.phase = 3
          AND ir.deep_reading_json IS NOT NULL
    """
    if reviewed_only:
        query += " AND ir.reviewed = 1"
    query += " ORDER BY CAST(json_extract(ir.raw_json, '$.photo_number') AS INTEGER)"

    rows = conn.execute(query).fetchall()
    return rows


def promote_woodcut(conn, reading_id, dry_run=False, force=False):
    """Promote a single woodcut detection from image_readings to woodcuts table.

    Returns (success, message).
    """
    row = conn.execute(
        "SELECT * FROM image_readings WHERE id = ?", (reading_id,)
    ).fetchone()

    if not row:
        return False, f"No image_reading with id={reading_id}"

    if not row["has_woodcut"]:
        return False, f"Reading {reading_id} does not have a woodcut"

    if row["concordance_status"] != "CONFIRMED" and not force:
        return False, (
            f"Reading {reading_id} is {row['concordance_status']}, not CONFIRMED. "
            f"Use --force to promote anyway (will be marked PROVISIONAL)."
        )

    # Get photo number
    raw = json.loads(row["raw_json"])
    photo_num = raw.get("photo_number")

    # Check if woodcut already exists for this photo
    existing = conn.execute(
        "SELECT id FROM woodcuts WHERE bl_photo_number = ?", (photo_num,)
    ).fetchone()
    if existing:
        return False, (
            f"Woodcut already exists for photo {photo_num} "
            f"(woodcuts.id={existing['id']}). Will not overwrite."
        )

    # Parse description
    desc = row["woodcut_description"] or "Woodcut detected by vision reading"
    page_num = row["page_number_read"]

    # Determine confidence
    confidence = "HIGH" if row["concordance_status"] == "CONFIRMED" else "PROVISIONAL"

    if dry_run:
        return True, (
            f"DRY RUN: Would insert woodcut for photo {photo_num}, "
            f"page={page_num}, desc='{desc[:60]}...', confidence={confidence}"
        )

    # Insert into woodcuts table using its actual schema
    conn.execute("""
        INSERT INTO woodcuts (
            title, page_1545, description,
            has_bl_photo, bl_photo_number,
            source_method, confidence, review_status
        ) VALUES (?, ?, ?, 1, ?, 'VISION_MODEL', ?, 'DRAFT')
    """, (
        f"Woodcut p.{page_num}" if page_num else f"Woodcut photo {photo_num}",
        page_num, desc, photo_num, confidence
    ))

    # Mark the reading as promoted
    conn.execute("""
        UPDATE image_readings
        SET promoted_to = 'woodcuts',
            reviewed = CASE WHEN reviewed = 0 THEN 0 ELSE reviewed END
        WHERE id = ?
    """, (reading_id,))

    conn.commit()
    return True, (
        f"Promoted: reading {reading_id} → woodcuts "
        f"(image_id={row['image_id']}, page={page_num})"
    )


def batch_promote_woodcuts(conn, reviewed_only=True, dry_run=False, force=False):
    """Promote all eligible woodcut candidates."""
    candidates = list_woodcut_candidates(conn, reviewed_only=reviewed_only)
    results = {"promoted": 0, "skipped": 0, "errors": 0}

    for row in candidates:
        if reviewed_only and not row["reviewed"]:
            results["skipped"] += 1
            continue

        ok, msg = promote_woodcut(
            conn, row["reading_id"], dry_run=dry_run, force=force
        )
        if ok:
            results["promoted"] += 1
            print(f"  {msg}")
        else:
            results["skipped"] += 1
            if "already exists" not in msg:
                print(f"  SKIP: {msg}")

    return results


def cmd_list(conn, target, reviewed_only):
    """List promotion candidates."""
    if target == "woodcuts":
        rows = list_woodcut_candidates(conn, reviewed_only)
        print(f"\nWoodcut promotion candidates ({len(rows)}):\n")
        print(f"{'ID':>5} {'Photo':>6} {'Page':>5} {'Status':>12} {'Rev':>4}  Description")
        print("-" * 80)
        for r in rows:
            desc = (r["woodcut_description"] or "")[:40]
            rev = "YES" if r["reviewed"] else "no"
            print(
                f"{r['reading_id']:>5} {r['photo_number']:>6} "
                f"{r['page_number'] or '?':>5} {r['concordance_status']:>12} "
                f"{rev:>4}  {desc}"
            )
    elif target == "annotations":
        rows = list_annotation_candidates(conn, reviewed_only)
        print(f"\nAnnotation promotion candidates ({len(rows)}):\n")
        print(f"{'ID':>5} {'Photo':>6} {'Status':>12} {'Rev':>4}  Notes")
        print("-" * 80)
        for r in rows:
            dr = json.loads(r["deep_reading_json"]) if r["deep_reading_json"] else {}
            sig = dr.get("scholarly_significance", "")[:50]
            rev = "YES" if r["reviewed"] else "no"
            print(
                f"{r['reading_id']:>5} {r['photo_number']:>6} "
                f"{r['concordance_status']:>12} {rev:>4}  {sig}"
            )
    else:
        print(f"Unknown target: {target}. Use 'woodcuts' or 'annotations'.")
        sys.exit(1)


def cmd_mark_reviewed(conn, reading_ids, reviewer="human"):
    """Mark readings as reviewed."""
    now = datetime.now().isoformat()
    for rid in reading_ids:
        conn.execute("""
            UPDATE image_readings
            SET reviewed = 1, reviewed_by = ?, reviewed_at = ?
            WHERE id = ?
        """, (reviewer, now, rid))
        print(f"  Marked reading {rid} as reviewed by {reviewer}")
    conn.commit()


def main():
    parser = argparse.ArgumentParser(
        description="Promote reviewed image_readings to canonical tables"
    )
    sub = parser.add_subparsers(dest="command")

    # list
    p_list = sub.add_parser("list", help="List promotion candidates")
    p_list.add_argument("target", choices=["woodcuts", "annotations"])
    p_list.add_argument("--reviewed-only", action="store_true")

    # promote
    p_prom = sub.add_parser("promote", help="Promote a single reading")
    p_prom.add_argument("target", choices=["woodcut", "annotation"])
    p_prom.add_argument("--reading-id", type=int, required=True)
    p_prom.add_argument("--dry-run", action="store_true")
    p_prom.add_argument("--force", action="store_true",
                        help="Promote even if not CONFIRMED")

    # batch-promote
    p_batch = sub.add_parser("batch-promote", help="Promote all eligible readings")
    p_batch.add_argument("target", choices=["woodcuts"])
    p_batch.add_argument("--reviewed-only", action="store_true", default=True)
    p_batch.add_argument("--include-unreviewed", action="store_true")
    p_batch.add_argument("--dry-run", action="store_true")
    p_batch.add_argument("--force", action="store_true")

    # mark-reviewed
    p_rev = sub.add_parser("mark-reviewed", help="Mark readings as reviewed")
    p_rev.add_argument("reading_ids", type=int, nargs="+")
    p_rev.add_argument("--reviewer", default="human")

    # status
    p_stat = sub.add_parser("status", help="Show promotion statistics")

    args = parser.parse_args()
    conn = get_conn()

    if args.command == "list":
        cmd_list(conn, args.target, args.reviewed_only)

    elif args.command == "promote":
        if args.target == "woodcut":
            ok, msg = promote_woodcut(
                conn, args.reading_id,
                dry_run=args.dry_run, force=args.force
            )
            print(msg)
            sys.exit(0 if ok else 1)
        else:
            print("Annotation promotion not yet implemented.")
            sys.exit(1)

    elif args.command == "batch-promote":
        reviewed_only = not args.include_unreviewed
        results = batch_promote_woodcuts(
            conn, reviewed_only=reviewed_only,
            dry_run=args.dry_run, force=args.force
        )
        print(f"\nResults: {results['promoted']} promoted, "
              f"{results['skipped']} skipped, {results['errors']} errors")

    elif args.command == "mark-reviewed":
        cmd_mark_reviewed(conn, args.reading_ids, args.reviewer)

    elif args.command == "status":
        # Promotion statistics
        stats = conn.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN has_woodcut = 1 THEN 1 ELSE 0 END) as with_woodcut,
                SUM(CASE WHEN promoted_to IS NOT NULL THEN 1 ELSE 0 END) as promoted,
                SUM(CASE WHEN reviewed = 1 THEN 1 ELSE 0 END) as reviewed,
                SUM(CASE WHEN concordance_status = 'CONFIRMED' THEN 1 ELSE 0 END) as confirmed,
                SUM(CASE WHEN concordance_status = 'DISCREPANCY' THEN 1 ELSE 0 END) as discrepancy
            FROM image_readings
        """).fetchone()

        wc_canonical = conn.execute("SELECT COUNT(*) as c FROM woodcuts").fetchone()["c"]
        wc_candidates = len(list_woodcut_candidates(conn))

        print(f"\nPromotion Status")
        print(f"  Total readings:      {stats['total']}")
        print(f"  Reviewed:            {stats['reviewed']}")
        print(f"  Confirmed:           {stats['confirmed']}")
        print(f"  Discrepancies:       {stats['discrepancy']}")
        print(f"  Already promoted:    {stats['promoted']}")
        print(f"  Woodcuts detected:   {stats['with_woodcut']}")
        print(f"  Woodcuts canonical:  {wc_canonical}")
        print(f"  Woodcut candidates:  {wc_candidates}")

    else:
        parser.print_help()

    conn.close()


if __name__ == "__main__":
    main()
