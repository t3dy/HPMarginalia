#!/usr/bin/env python3
"""check_links.py — Validate all internal links in the generated site.

Parses every HTML file in site/, extracts href and src attributes,
and verifies they resolve to existing files. Reports broken links,
missing stylesheets, and unreachable pages.

Usage:
    python scripts/check_links.py
    python scripts/check_links.py --verbose
    python scripts/check_links.py --fix    # (future: auto-fix common issues)

Run after build_site.py to catch broken links before deployment.
"""

import argparse
import re
import sys
from pathlib import Path
from html import unescape

SITE_DIR = Path(__file__).parent.parent / "site"

# Attributes to check
LINK_ATTRS = re.compile(r'(?:href|src)\s*=\s*"([^"]*)"', re.IGNORECASE)

# Skip patterns (external URLs, anchors, javascript, mailto)
SKIP_PATTERNS = re.compile(r'^(https?://|#|javascript:|mailto:|data:)')


def check_file(html_path, verbose=False):
    """Check all links in a single HTML file. Returns list of (link, issue) tuples."""
    issues = []
    try:
        content = html_path.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        return [('', f'Cannot read file: {e}')]

    links = LINK_ATTRS.findall(content)
    file_dir = html_path.parent

    for link in links:
        link = unescape(link).strip()

        # Skip external, anchors, etc.
        if SKIP_PATTERNS.match(link):
            continue

        # Strip query string and fragment
        clean = link.split('?')[0].split('#')[0]
        if not clean:
            continue

        # Resolve relative path
        target = (file_dir / clean).resolve()

        if not target.exists():
            rel_from_site = html_path.relative_to(SITE_DIR)
            issues.append((str(rel_from_site), link, 'FILE NOT FOUND'))
            if verbose:
                print(f"  BROKEN: {rel_from_site} -> {link}")

    return issues


def check_depth_consistency(verbose=False):
    """Check that all subdirectory pages use depth=1 (../prefix) for stylesheets."""
    issues = []
    subdirs = [d for d in SITE_DIR.iterdir() if d.is_dir() and (d / 'index.html').exists()]

    for subdir in subdirs:
        for html_file in subdir.glob('*.html'):
            content = html_file.read_text(encoding='utf-8', errors='replace')

            # Check stylesheet links
            css_links = re.findall(r'<link[^>]+href="([^"]*\.css)"', content)
            for css_link in css_links:
                if not css_link.startswith('../') and not css_link.startswith('http'):
                    rel = html_file.relative_to(SITE_DIR)
                    issues.append((str(rel), css_link, 'MISSING ../ PREFIX (depth issue)'))
                    if verbose:
                        print(f"  DEPTH: {rel} -> {css_link} (should be ../{css_link})")

    return issues


def main():
    parser = argparse.ArgumentParser(description="Validate site links")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    if not SITE_DIR.exists():
        print("ERROR: site/ directory not found. Run build_site.py first.")
        sys.exit(1)

    print("=== HPMarginalia Link Validator ===\n")

    # Collect all HTML files
    html_files = list(SITE_DIR.rglob('*.html'))
    print(f"Scanning {len(html_files)} HTML files...\n")

    # Check all links
    all_issues = []
    files_checked = 0
    for html_file in sorted(html_files):
        issues = check_file(html_file, args.verbose)
        all_issues.extend(issues)
        files_checked += 1

    # Check depth consistency
    print("Checking depth/prefix consistency...")
    depth_issues = check_depth_consistency(args.verbose)
    all_issues.extend(depth_issues)

    # Check for orphaned pages (HTML files not linked from anywhere)
    print("Checking for None.html or other artifacts...")
    artifacts = list(SITE_DIR.rglob('None.html'))
    for a in artifacts:
        rel = a.relative_to(SITE_DIR)
        all_issues.append((str(rel), 'None.html', 'ARTIFACT FILE (should be deleted)'))

    # Summary
    print(f"\n=== Results ===")
    print(f"  Files checked: {files_checked}")
    print(f"  Issues found: {len(all_issues)}")

    if all_issues:
        print(f"\n--- Issues ---")

        # Group by type
        by_type = {}
        for source, link, issue_type in all_issues:
            by_type.setdefault(issue_type, []).append((source, link))

        for issue_type, items in sorted(by_type.items()):
            print(f"\n  {issue_type} ({len(items)}):")
            for source, link in items[:20]:  # Cap at 20 per type
                print(f"    {source} -> {link}")
            if len(items) > 20:
                print(f"    ... and {len(items) - 20} more")

        print(f"\nTotal: {len(all_issues)} issues")
        sys.exit(1)
    else:
        print("\n  All links valid!")
        sys.exit(0)


if __name__ == "__main__":
    main()
