#!/usr/bin/env python3
"""scan_ia_pages.py — Scan IA facsimile pages to identify woodcut locations.

Downloads page images from the Internet Archive 1499 HP facsimile
and identifies pages likely to contain woodcut illustrations based
on file size analysis. Woodcut pages produce significantly larger
JPEG files than text-only pages.

After scanning, outputs candidate pages for visual verification
and updates page_concordance.has_woodcut.

Usage:
    python scripts/scan_ia_pages.py --range 170-270
    python scripts/scan_ia_pages.py --range 170-448 --threshold 80
    python scripts/scan_ia_pages.py --range 170-270 --dry-run
    python scripts/scan_ia_pages.py --analyze   # Analyze existing downloads
"""

import argparse
import json
import os
import sqlite3
import ssl
import statistics
import time
import urllib.request
import urllib.error
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "hp.db"
SCAN_DIR = Path(__file__).parent.parent / "staging" / "ia_scan"
IA_IDENTIFIER = "A336080v1"
IA_URL_TEMPLATE = "https://archive.org/download/{id}/page/n{page}.jpg"
IA_OFFSET = 5


def download_page(ia_page, output_path, dry_run=False):
    """Download a single IA page image."""
    url = IA_URL_TEMPLATE.format(id=IA_IDENTIFIER, page=ia_page)

    if dry_run:
        print(f"  DRY RUN: Would download n{ia_page}")
        return 0

    if output_path.exists():
        return output_path.stat().st_size

    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(url, headers={
            'User-Agent': 'HP-Marginalia-Project/1.0 (scholarly research)'
        })
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            data = resp.read()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(data)

        return len(data)

    except Exception as e:
        print(f"  ERROR downloading n{ia_page}: {e}")
        return -1


def analyze_sizes(scan_dir, page_range, threshold_kb=80):
    """Analyze downloaded page sizes to identify woodcut candidates.

    Logic: Pages with woodcuts have significantly larger file sizes
    than text-only pages. We compute the median size and flag pages
    above a threshold as candidates.
    """
    sizes = {}
    for f in sorted(scan_dir.glob("n*.jpg")):
        page_num = int(f.stem[1:])  # Extract number from n123.jpg
        hp_page = page_num - IA_OFFSET
        if page_range and not (page_range[0] <= hp_page <= page_range[1]):
            continue
        sizes[hp_page] = f.stat().st_size / 1024  # KB

    if not sizes:
        print("No scanned pages found in range")
        return {}

    all_sizes = sorted(sizes.values())
    median = statistics.median(all_sizes)
    mean = statistics.mean(all_sizes)
    stdev = statistics.stdev(all_sizes) if len(all_sizes) > 1 else 0

    print(f"\n=== File Size Analysis ===")
    print(f"  Pages scanned: {len(sizes)}")
    print(f"  Median size: {median:.0f} KB")
    print(f"  Mean size: {mean:.0f} KB")
    print(f"  Std dev: {stdev:.0f} KB")
    print(f"  Threshold: {threshold_kb} KB")

    # Candidates: pages above threshold
    candidates = {p: s for p, s in sizes.items() if s >= threshold_kb}
    text_only = {p: s for p, s in sizes.items() if s < threshold_kb}

    print(f"\n  Candidate woodcut pages (>= {threshold_kb} KB): {len(candidates)}")
    print(f"  Text-only pages (< {threshold_kb} KB): {len(text_only)}")

    if candidates:
        print(f"\n=== Candidate Pages ===")
        for p in sorted(candidates):
            ia_p = p + IA_OFFSET
            print(f"  p.{p:3d} (IA n{ia_p:3d})  {candidates[p]:.0f} KB")

    return candidates


def update_concordance(candidates, conn):
    """Update page_concordance.has_woodcut for candidate pages."""
    cur = conn.cursor()
    updated = 0
    for page_seq in candidates:
        cur.execute("""
            UPDATE page_concordance
            SET has_woodcut = 1,
                notes = COALESCE(notes, '') || ' [IA scan candidate]'
            WHERE page_seq = ? AND has_woodcut = 0
        """, (page_seq,))
        if cur.rowcount:
            updated += 1
    conn.commit()
    return updated


def save_scan_report(candidates, scan_dir, page_range):
    """Save scan results as JSON for later use."""
    report = {
        "range": list(page_range) if page_range else None,
        "scan_date": time.strftime("%Y-%m-%d %H:%M"),
        "candidates": {str(k): v for k, v in sorted(candidates.items())},
        "count": len(candidates),
    }
    report_path = scan_dir / "scan_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved: {report_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Scan IA pages to identify woodcut locations"
    )
    parser.add_argument("--range", type=str, default="170-448",
                        help="Page range to scan (e.g., 170-270)")
    parser.add_argument("--threshold", type=int, default=80,
                        help="File size threshold in KB for woodcut detection")
    parser.add_argument("--delay", type=float, default=0.5,
                        help="Delay between downloads (seconds)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--analyze", action="store_true",
                        help="Only analyze existing downloads (no new downloads)")
    parser.add_argument("--update-db", action="store_true",
                        help="Update page_concordance with candidates")
    args = parser.parse_args()

    # Parse range
    start, end = [int(x) for x in args.range.split('-')]
    page_range = (start, end)

    SCAN_DIR.mkdir(parents=True, exist_ok=True)

    if not args.analyze:
        # Download pages
        total = end - start + 1
        print(f"Scanning IA pages {start}-{end} ({total} pages)")
        print(f"Downloading to: {SCAN_DIR}")

        downloaded = 0
        skipped = 0
        errors = 0

        for page_seq in range(start, end + 1):
            ia_page = page_seq + IA_OFFSET
            output_path = SCAN_DIR / f"n{ia_page:03d}.jpg"

            if output_path.exists() and not args.dry_run:
                skipped += 1
                continue

            size = download_page(ia_page, output_path, args.dry_run)
            if size > 0:
                downloaded += 1
                size_kb = size / 1024
                marker = " ***" if size_kb >= args.threshold else ""
                print(f"  p.{page_seq:3d} (n{ia_page:3d}): {size_kb:.0f} KB{marker}")
                time.sleep(args.delay)
            elif size == 0:
                pass  # dry run
            else:
                errors += 1

        print(f"\nDownload: {downloaded} new, {skipped} cached, {errors} errors")

    # Analyze
    candidates = analyze_sizes(SCAN_DIR, page_range, args.threshold)

    if candidates:
        save_scan_report(candidates, SCAN_DIR, page_range)

        if args.update_db:
            conn = sqlite3.connect(str(DB_PATH))
            updated = update_concordance(candidates, conn)
            conn.close()
            print(f"Updated {updated} pages in page_concordance")


if __name__ == "__main__":
    main()
