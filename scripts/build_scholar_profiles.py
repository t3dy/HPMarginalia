"""Build scholar profile pages and paper summary pages from summaries JSON."""

import json
import re
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SCHOLARS_DIR = BASE_DIR / "scholars"
SUMMARIES_PATH = BASE_DIR / "scholars" / "summaries.json"
SITE_DIR = BASE_DIR / "site"


def slugify(name):
    """Create a URL-safe slug from a name."""
    slug = name.lower().strip()
    slug = re.sub(r"['\u2019]", '', slug)
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    return slug.strip('-')


def paper_slug(title):
    """Create a short slug from a paper title."""
    words = re.sub(r'[^\w\s]', '', title.lower()).split()
    return '-'.join(words[:6])


def group_by_scholar(summaries):
    """Group paper summaries by author."""
    scholars = {}
    for paper in summaries:
        author = paper.get('author', 'Unknown')
        if author not in scholars:
            scholars[author] = []
        scholars[author].append(paper)
    return scholars


def write_scholar_profile(scholar_name, papers, scholar_dir):
    """Write a scholar's profile.md."""
    slug = slugify(scholar_name)
    profile_dir = scholar_dir / slug
    profile_dir.mkdir(parents=True, exist_ok=True)

    paper_list = []
    for p in sorted(papers, key=lambda x: x.get('year', 0) or 0):
        year = p.get('year', '?')
        journal = p.get('journal', '')
        p_slug = paper_slug(p['title'])
        paper_list.append(f"- [{p['title']}]({p_slug}.md) ({journal} {year})")

    content = f"""---
name: "{scholar_name}"
slug: "{slug}"
paper_count: {len(papers)}
topic_clusters: {json.dumps(list(set(p.get('topic_cluster', 'unknown') for p in papers)))}
---

# {scholar_name}

## Papers in the HP Corpus

{chr(10).join(paper_list)}
"""

    (profile_dir / "profile.md").write_text(content, encoding='utf-8')

    # Write individual paper summary files
    for p in papers:
        p_slug = paper_slug(p['title'])
        year = p.get('year', '?')
        journal = p.get('journal', '')
        topic = p.get('topic_cluster', 'unknown')
        summary = p.get('summary', 'Summary pending.')

        paper_content = f"""---
title: "{p['title']}"
author: "{scholar_name}"
year: {year if year and year != '?' else 'null'}
journal: "{journal}"
topic_cluster: "{topic}"
source_pdf: "{p.get('filename', '')}"
---

# {p['title']}

**{scholar_name}** | {journal} {year}

## Summary

{summary}

## Topic

{topic.replace('_', ' ').title()}
"""
        (profile_dir / f"{p_slug}.md").write_text(paper_content, encoding='utf-8')

    return slug


def generate_scholars_html(scholars_data, papers_data):
    """Generate the scholars directory HTML page."""
    cards = []
    for name, papers in sorted(scholars_data.items()):
        slug = slugify(name)
        topics = set(p.get('topic_cluster', '') for p in papers)
        topic_badges = ' '.join(
            f'<span class="topic-badge topic-{t}">{t.replace("_", " ").title()}</span>'
            for t in sorted(topics) if t
        )
        paper_count = len(papers)

        # Index card summaries for each paper
        paper_cards = []
        for p in sorted(papers, key=lambda x: x.get('year', 0) or 0):
            year = p.get('year', '?')
            journal = p.get('journal', '')
            summary = p.get('summary', 'Summary pending.')
            p_slug = paper_slug(p['title'])

            paper_cards.append(f"""
                <div class="paper-card">
                    <h4><a href="scholar/{slug}.html#{p_slug}">{escape_html(p['title'])}</a></h4>
                    <div class="paper-meta">{escape_html(journal)} {year}</div>
                    <p class="paper-summary">{escape_html(summary)}</p>
                </div>""")

        cards.append(f"""
            <div class="scholar-card" id="{slug}">
                <h3><a href="scholar/{slug}.html">{escape_html(name)}</a></h3>
                <div class="scholar-meta">{paper_count} paper{'s' if paper_count != 1 else ''} {topic_badges}</div>
                <div class="scholar-papers">
                    {''.join(paper_cards)}
                </div>
            </div>""")

    return cards


def generate_scholar_page_html(name, papers):
    """Generate an individual scholar's HTML page."""
    slug = slugify(name)

    paper_sections = []
    for p in sorted(papers, key=lambda x: x.get('year', 0) or 0):
        year = p.get('year', '?')
        journal = p.get('journal', '')
        summary = p.get('summary', 'Summary pending.')
        topic = p.get('topic_cluster', 'unknown')
        p_slug = paper_slug(p['title'])

        paper_sections.append(f"""
        <article class="paper-detail" id="{p_slug}">
            <h3>{escape_html(p['title'])}</h3>
            <div class="paper-meta">
                {escape_html(journal)} {year}
                <span class="topic-badge topic-{topic}">{topic.replace('_', ' ').title()}</span>
            </div>
            <div class="paper-summary-full">
                <p>{escape_html(summary)}</p>
            </div>
        </article>""")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape_html(name)} — HP Scholarship</title>
    <link rel="stylesheet" href="../style.css">
    <link rel="stylesheet" href="../scholars.css">
</head>
<body>
    <header>
        <div class="header-content">
            <h1>{escape_html(name)}</h1>
            <p class="subtitle"><a href="../scholars.html">&larr; All Scholars</a></p>
        </div>
    </header>
    <main>
        <section class="scholar-detail">
            <h2>Papers in the HP Corpus ({len(papers)})</h2>
            {''.join(paper_sections)}
        </section>
    </main>
    <footer>
        <div class="footer-content">
            <div class="footer-section">
                <h4>HP Scholarship Database</h4>
                <p>Part of the <a href="../index.html">Hypnerotomachia Poliphili</a> digital humanities project.</p>
            </div>
        </div>
    </footer>
</body>
</html>"""


def escape_html(text):
    """Escape HTML special characters."""
    if not text:
        return ''
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;'))


def main():
    if not SUMMARIES_PATH.exists():
        print(f"ERROR: {SUMMARIES_PATH} not found. Create summaries.json first.")
        return

    with open(SUMMARIES_PATH, 'r', encoding='utf-8') as f:
        summaries = json.load(f)

    print(f"Loaded {len(summaries)} paper summaries")

    scholars = group_by_scholar(summaries)
    print(f"Found {len(scholars)} unique scholars")

    # Write scholar profile markdown files
    for name, papers in scholars.items():
        slug = write_scholar_profile(name, papers, SCHOLARS_DIR)
        print(f"  {name} ({slug}): {len(papers)} papers")

    # Generate HTML pages
    scholar_page_dir = SITE_DIR / "scholar"
    scholar_page_dir.mkdir(parents=True, exist_ok=True)

    # Individual scholar pages
    for name, papers in scholars.items():
        slug = slugify(name)
        html = generate_scholar_page_html(name, papers)
        (scholar_page_dir / f"{slug}.html").write_text(html, encoding='utf-8')

    # Scholars directory page
    cards = generate_scholars_html(scholars, summaries)
    scholars_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scholars — Hypnerotomachia Poliphili</title>
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="scholars.css">
</head>
<body>
    <header>
        <div class="header-content">
            <h1>HP Scholarship</h1>
            <p class="subtitle">Scholars and Their Contributions</p>
            <p class="attribution"><a href="index.html">&larr; Back to Marginalia</a></p>
        </div>
    </header>
    <main>
        <section class="intro">
            <div class="intro-content">
                <p>Five centuries of scholarship on the <em>Hypnerotomachia Poliphili</em>, organized by author. Each scholar's profile links to summaries of their contributions to the field.</p>
            </div>
        </section>
        <section class="scholars-grid">
            {''.join(cards)}
        </section>
    </main>
    <footer>
        <div class="footer-content">
            <div class="footer-section">
                <h4>HP Scholarship Database</h4>
                <p>Part of the <a href="index.html">Hypnerotomachia Poliphili</a> digital humanities project.</p>
            </div>
        </div>
    </footer>
</body>
</html>"""

    (SITE_DIR / "scholars.html").write_text(scholars_html, encoding='utf-8')
    print(f"\nGenerated {len(scholars)} scholar pages + scholars.html")


if __name__ == "__main__":
    main()
