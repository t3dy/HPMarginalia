#!/usr/bin/env python3
"""upgrade_concordance.py — Upgrade concordance status based on vision confirmations.

Two upgrades:
1. Phase-1 image_readings with page_number_match=1 get concordance_status='CONFIRMED'
2. Matches backed by vision-confirmed readings get reviewed=1, needs_review=0

Usage:
    python scripts/upgrade_concordance.py --dry-run
    python scripts/upgrade_concordance.py
"""

import argparse
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "hp.db"


def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def upgrade_readings(conn, dry_run=False):
    """Upgrade phase-1 readings with page_number_match=1 to CONFIRMED."""
    candidates = conn.execute("""
        SELECT id, image_id, page_number_read, page_number_expected
        FROM image_readings
        WHERE phase = 1
          AND page_number_match = 1
          AND concordance_status = 'UNVERIFIED'
    """).fetchall()

    print(f"Phase-1 readings to confirm: {len(candidates)}")

    if dry_run or not candidates:
        return len(candidates)

    now = datetime.now().isoformat()
    conn.executemany("""
        UPDATE image_readings
        SET concordance_status = 'CONFIRMED',
            notes = COALESCE(notes || '; ', '')
                || 'Concordance confirmed: page_number_match=1 (offset verified). Upgraded '
                || ?
        WHERE id = ?
    """, [(now, r["id"]) for r in candidates])

    return len(candidates)


def upgrade_matches(conn, dry_run=False):
    """Mark matches with vision-confirmed backing as reviewed."""
    candidates = conn.execute("""
        SELECT DISTINCT m.id, m.image_id, ir.page_number_read
        FROM matches m
        JOIN image_readings ir
          ON m.image_id = ir.image_id
          AND ir.phase = 1
          AND ir.page_number_match = 1
        WHERE m.needs_review = 1
           OR m.reviewed = 0
    """).fetchall()

    print(f"Matches to mark reviewed: {len(candidates)}")

    if dry_run or not candidates:
        return len(candidates)

    now = datetime.now().isoformat()
    conn.executemany("""
        UPDATE matches
        SET reviewed = 1,
            needs_review = 0,
            reviewed_by = 'vision_phase1_confirmation',
            notes = COALESCE(notes || '; ', '')
                || 'Vision-confirmed page match (phase 1). Reviewed '
                || ?
        WHERE id = ?
    """, [(now, r["id"]) for r in candidates])

    return len(candidates)


def main():
    parser = argparse.ArgumentParser(description="Upgrade concordance confidence")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change without modifying the database")
    args = parser.parse_args()

    conn = get_conn()

    if args.dry_run:
        print("=== DRY RUN ===\n")

    readings_count = upgrade_readings(conn, args.dry_run)
    matches_count = upgrade_matches(conn, args.dry_run)

    if not args.dry_run and (readings_count or matches_count):
        conn.commit()
        print(f"\nCommitted: {readings_count} readings confirmed, {matches_count} matches reviewed.")
    elif args.dry_run:
        print(f"\nWould upgrade: {readings_count} readings, {matches_count} matches.")
    else:
        print("\nNothing to upgrade.")

    conn.close()


if __name__ == "__main__":
    main()
