"""Unified site builder: generates all static pages from SQLite.

Replaces build_scholar_profiles.py and export_showcase_data.py.
Generates:
  - site/index.html           (marginalia gallery, updated nav)
  - site/data.json             (gallery data with confidence flags)
  - site/scholars.html         (scholars overview, DB-driven)
  - site/scholar/*.html        (individual scholar pages)
  - site/dictionary/index.html (dictionary landing)
  - site/dictionary/*.html     (individual term pages)
  - site/marginalia/*.html     (individual folio detail pages)
  - site/about.html            (about page)
"""

import sqlite3
import json
import re
import os
from pathlib import Path
from html import escape

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"
SITE_DIR = BASE_DIR / "site"
SUMMARIES_PATH = BASE_DIR / "scholars" / "summaries.json"

# ============================================================
# Shared HTML templates
# ============================================================

def slugify(text):
    s = text.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s.strip('-')


def nav_html(active='', prefix=''):
    """Generate navigation bar. prefix is '' for root, '../' for subdirectories."""
    links = [
        (f'{prefix}index.html', 'Home', 'home'),
        (f'{prefix}marginalia/index.html', 'Marginalia', 'marginalia'),
        (f'{prefix}scholars.html', 'Scholars', 'scholars'),
        (f'{prefix}bibliography.html', 'Bibliography', 'bibliography'),
        (f'{prefix}dictionary/index.html', 'Dictionary', 'dictionary'),
        (f'{prefix}docs/index.html', 'Docs', 'docs'),
        (f'{prefix}code/index.html', 'Code', 'code'),
        (f'{prefix}about.html', 'About', 'about'),
    ]
    items = []
    for href, label, key in links:
        cls = ' class="active"' if key == active else ''
        items.append(f'<a href="{href}"{cls}>{label}</a>')
    return f'<nav class="site-nav">{"".join(items)}</nav>'


def review_badge_html(needs_review, source_method=None):
    if not needs_review:
        return ''
    method = f' ({source_method})' if source_method else ''
    return f'<span class="review-badge">Unreviewed{method}</span>'


def confidence_badge_html(confidence):
    if not confidence:
        return ''
    cls = f'confidence-{confidence.lower()}'
    return f'<span class="confidence-badge {cls}">{confidence}</span>'


def page_shell(title, body, active_nav='', extra_css='', extra_js='', depth=0):
    """Generate full HTML page. depth=0 for site root, depth=1 for subdirectories."""
    prefix = '../' * depth if depth > 0 else ''
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(title)} - Hypnerotomachia Poliphili</title>
    <meta name="description" content="Digital scholarship and marginalia of the Hypnerotomachia Poliphili (Venice, 1499)">
    <link rel="stylesheet" href="{prefix}style.css">
    <link rel="stylesheet" href="{prefix}scholars.css">
    <link rel="stylesheet" href="{prefix}components.css">
    {extra_css}
</head>
<body>
    <header>
        <div class="header-content">
            <h1><a href="{prefix}index.html" style="color:inherit;text-decoration:none"><em>Hypnerotomachia Poliphili</em></a></h1>
            <p class="subtitle">Digital Scholarship &amp; Marginalia</p>
            {nav_html(active_nav, prefix)}
        </div>
    </header>
    <main>
{body}
    </main>
    <footer>
        <div class="footer-content">
            <div class="footer-section">
                <h4>About This Project</h4>
                <p>A digital humanities project documenting the readership
                and marginalia of the 1499 Aldine <em>Hypnerotomachia Poliphili</em>,
                based on James Russell's PhD thesis (Durham, 2014).</p>
            </div>
            <div class="footer-section">
                <h4>Data Provenance</h4>
                <p>Content marked with <span class="review-badge" style="font-size:0.7rem">Unreviewed</span>
                has been generated with LLM assistance and has not been
                verified by a human expert.</p>
            </div>
        </div>
    </footer>
    {extra_js}
</body>
</html>"""


# ============================================================
# Topic badge helpers
# ============================================================

TOPIC_LABELS = {
    'authorship': 'Authorship',
    'architecture_gardens': 'Architecture & Gardens',
    'text_image': 'Text & Image',
    'reception': 'Reception',
    'dream_religion': 'Dream & Religion',
    'material_bibliographic': 'Material & Bibliographic',
}


def topic_badges_html(topics_str):
    if not topics_str:
        return ''
    badges = []
    for t in topics_str.split(','):
        t = t.strip()
        label = TOPIC_LABELS.get(t, t.replace('_', ' ').title())
        badges.append(f'<span class="topic-badge topic-{t}">{label}</span>')
    return ' '.join(badges)


# ============================================================
# Data export: data.json
# ============================================================

def export_data_json(conn):
    """Export marginalia gallery data with confidence flags."""
    cur = conn.cursor()
    cur.execute("""
        SELECT
            r.id, r.thesis_page, r.signature_ref, m.shelfmark,
            m.institution, m.city, r.context_text, r.marginal_text,
            r.chapter_num, i.filename, i.relative_path,
            i.folio_number, i.side, mat.confidence,
            sm.quire, sm.leaf_in_quire,
            mat.needs_review as match_needs_review,
            h.hand_label, h.attribution, h.is_alchemist
        FROM matches mat
        JOIN dissertation_refs r ON mat.ref_id = r.id
        JOIN images i ON mat.image_id = i.id
        JOIN manuscripts m ON i.manuscript_id = m.id
        LEFT JOIN signature_map sm ON LOWER(r.signature_ref) = LOWER(sm.signature)
        LEFT JOIN annotator_hands h ON r.hand_id = h.id
        WHERE i.page_type = 'PAGE'
        GROUP BY r.signature_ref, i.filename
        ORDER BY COALESCE(sm.folio_number, 999), r.thesis_page
    """)

    entries = []
    sigs = set()
    for row in cur.fetchall():
        entry = {
            'ref_id': row[0], 'thesis_page': row[1],
            'signature': row[2], 'manuscript': row[3],
            'institution': row[4], 'city': row[5],
            'context': (row[6] or '')[:600],
            'marginal_text': row[7], 'chapter': row[8],
            'image_file': row[9],
            'image_path': row[10],
            'folio_number': row[11], 'side': row[12],
            'confidence': row[13] or 'PROVISIONAL',
            'quire': row[14], 'leaf_in_quire': row[15],
            'needs_review': bool(row[16]),
            'hand_label': row[17], 'hand_attribution': row[18],
            'is_alchemist': bool(row[19]) if row[19] is not None else False,
        }
        entries.append(entry)
        sigs.add(row[2])

    data = {
        'entries': entries,
        'stats': {
            'total_references': len(entries),
            'unique_signatures': len(sigs),
            'high_confidence_matches': sum(1 for e in entries if e['confidence'] == 'HIGH'),
            'low_confidence_matches': sum(1 for e in entries if e['confidence'] == 'LOW'),
            'needs_review': sum(1 for e in entries if e['needs_review']),
        },
        'provenance': {
            'source': 'hp.db v2',
            'note': 'BL C.60.o.12 matches are LOW confidence (1545 edition, unverified photo-folio mapping)',
        },
    }

    out = SITE_DIR / 'data.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  data.json: {len(entries)} entries")


# ============================================================
# Scholars pages (DB-driven)
# ============================================================

def build_scholars_pages(conn):
    """Generate scholars.html and scholar/*.html from DB + summaries.json."""
    # Load summaries for detailed content
    summaries = []
    if SUMMARIES_PATH.exists():
        with open(SUMMARIES_PATH, encoding='utf-8') as f:
            summaries = json.load(f)

    # Group by author
    by_author = {}
    for s in summaries:
        author = s.get('author', 'Unknown')
        by_author.setdefault(author, []).append(s)

    cur = conn.cursor()
    # Get review status from DB
    cur.execute("SELECT name, needs_review, source_method FROM scholars")
    scholar_review = {}
    for row in cur.fetchall():
        scholar_review[row[0]] = {'needs_review': row[1], 'source_method': row[2]}

    # Build scholars index
    scholar_cards = []
    scholar_dir = SITE_DIR / 'scholar'
    scholar_dir.mkdir(exist_ok=True)

    for author in sorted(by_author.keys()):
        papers = by_author[author]
        slug = slugify(author)
        review = scholar_review.get(author, {'needs_review': True, 'source_method': 'LLM_ASSISTED'})

        # Collect all topics
        topics = set()
        for p in papers:
            tc = p.get('topic_cluster', '')
            if tc:
                for t in tc.split(','):
                    topics.add(t.strip())

        badges = topic_badges_html(','.join(topics))
        review_html = review_badge_html(review.get('needs_review'), review.get('source_method'))

        # Paper cards for index
        paper_cards_html = ''
        for p in papers:
            paper_slug = slugify(p.get('title', ''))
            summary_preview = (p.get('summary', '') or '')[:250]
            if len(p.get('summary', '')) > 250:
                summary_preview += '...'
            paper_cards_html += f"""
                <div class="paper-card">
                    <h4><a href="{slug}.html">{escape(p.get('title', ''))}</a></h4>
                    <div class="paper-meta">{escape(p.get('journal', ''))} ({p.get('year', '?')})</div>
                    <div class="paper-summary">{escape(summary_preview)}</div>
                </div>"""

        scholar_cards.append(f"""
        <div class="scholar-card">
            <h3><a href="{slug}.html">{escape(author)}</a> {review_html}</h3>
            <div class="scholar-meta">{len(papers)} paper{'s' if len(papers) != 1 else ''} {badges}</div>
            <div class="scholar-papers">{paper_cards_html}</div>
        </div>""")

        # Build individual scholar page
        papers_detail = ''
        for p in papers:
            tc = p.get('topic_cluster', '')
            papers_detail += f"""
            <div class="paper-detail">
                <h3>{escape(p.get('title', ''))}</h3>
                <div class="paper-meta">{escape(p.get('journal', ''))} ({p.get('year', '?')})
                    {topic_badges_html(tc)}</div>
                <div class="paper-summary-full"><p>{escape(p.get('summary', ''))}</p></div>
            </div>"""

        detail_body = f"""
        <div class="scholar-detail">
            <h2>{escape(author)} {review_html}</h2>
            <p><a href="../scholars.html">&larr; All Scholars</a></p>
            {papers_detail}
        </div>"""

        detail_page = page_shell(author, detail_body, active_nav='scholars', depth=1)
        (scholar_dir / f'{slug}.html').write_text(detail_page, encoding='utf-8')

    # Build index page
    index_body = f"""
        <div class="scholars-grid">
            <div class="intro" style="margin-bottom:2rem">
                <p>{len(by_author)} scholars, {len(summaries)} works documented.
                Data sourced from SQLite database with provenance tracking.</p>
            </div>
            {''.join(scholar_cards)}
        </div>"""

    index_page = page_shell('Scholars', index_body, active_nav='scholars')
    (SITE_DIR / 'scholars.html').write_text(index_page, encoding='utf-8')
    print(f"  scholars.html + {len(by_author)} scholar pages")


# ============================================================
# Dictionary pages
# ============================================================

def build_dictionary_pages(conn):
    """Generate dictionary/index.html and dictionary/*.html from DB."""
    cur = conn.cursor()
    dict_dir = SITE_DIR / 'dictionary'
    dict_dir.mkdir(exist_ok=True)

    # Get all terms
    cur.execute("""
        SELECT id, slug, label, category, definition_short, definition_long,
               source_basis, review_status, needs_review
        FROM dictionary_terms ORDER BY label
    """)
    terms = cur.fetchall()

    # Build per-term link map
    term_links = {}
    cur.execute("""
        SELECT t1.slug, t2.slug, t2.label, l.link_type
        FROM dictionary_term_links l
        JOIN dictionary_terms t1 ON l.term_id = t1.id
        JOIN dictionary_terms t2 ON l.linked_term_id = t2.id
    """)
    for row in cur.fetchall():
        term_links.setdefault(row[0], []).append({
            'slug': row[1], 'label': row[2], 'type': row[3]
        })

    # Group by category for index
    by_category = {}
    for t in terms:
        by_category.setdefault(t[3], []).append(t)

    # Build index page
    cat_sections = ''
    for cat in sorted(by_category.keys()):
        cat_terms = by_category[cat]
        items = ''
        for t in sorted(cat_terms, key=lambda x: x[2]):
            review = ' <span class="review-badge">Draft</span>' if t[8] else ''
            items += f"""
                <div class="dict-entry">
                    <h4><a href="{t[1]}.html">{escape(t[2])}</a>{review}</h4>
                    <p>{escape(t[4])}</p>
                </div>"""
        cat_sections += f"""
            <section class="dict-category">
                <h3>{escape(cat)}</h3>
                {items}
            </section>"""

    index_body = f"""
        <div class="dictionary-index">
            <div class="intro">
                <h2>Dictionary of the <em>Hypnerotomachia</em></h2>
                <p>{len(terms)} terms across {len(by_category)} categories.
                A glossary of concepts essential for understanding the book,
                its readers, and five centuries of scholarship.</p>
            </div>
            {cat_sections}
        </div>"""

    dict_css = '<style>' + """
        .dictionary-index { max-width: 900px; margin: 2rem auto; padding: 0 2rem; }
        .dict-category { margin-bottom: 2.5rem; }
        .dict-category h3 {
            font-size: 1.2rem; color: var(--accent);
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.3rem; margin-bottom: 1rem;
        }
        .dict-entry { margin-bottom: 1rem; }
        .dict-entry h4 { font-size: 1rem; margin-bottom: 0.2rem; }
        .dict-entry h4 a { color: var(--text); text-decoration: none; }
        .dict-entry h4 a:hover { color: var(--accent); }
        .dict-entry p { font-size: 0.9rem; color: var(--text-muted); line-height: 1.5; }
        .dict-detail { max-width: 800px; margin: 2rem auto; padding: 0 2rem; }
        .dict-detail h2 { color: var(--accent); margin-bottom: 0.5rem; }
        .dict-detail .category-label {
            font-size: 0.85rem; color: var(--text-muted);
            font-family: var(--font-sans); margin-bottom: 1.5rem;
        }
        .dict-detail .definition-short {
            font-size: 1.1rem; font-style: italic; margin-bottom: 1.5rem;
            padding: 1rem; background: var(--bg-card); border-left: 3px solid var(--accent);
        }
        .dict-detail .definition-long { line-height: 1.8; margin-bottom: 1.5rem; }
        .dict-detail .source-basis {
            font-size: 0.85rem; color: var(--text-muted);
            font-family: var(--font-sans); margin-top: 1rem;
            padding-top: 1rem; border-top: 1px solid var(--border);
        }
        .related-terms { margin-top: 1.5rem; }
        .related-terms h4 { font-size: 0.95rem; color: var(--accent); margin-bottom: 0.5rem; }
        .related-terms a {
            display: inline-block; margin: 0.2rem 0.3rem 0.2rem 0;
            padding: 0.2rem 0.6rem; background: var(--bg);
            border: 1px solid var(--border); border-radius: 3px;
            font-size: 0.85rem; color: var(--text); text-decoration: none;
        }
        .related-terms a:hover { border-color: var(--accent); color: var(--accent); }
    """ + '</style>'

    index_page = page_shell('Dictionary', index_body, active_nav='dictionary', depth=1)
    (dict_dir / 'index.html').write_text(index_page, encoding='utf-8')

    # Build individual term pages
    for t in terms:
        tid, slug, label, category, def_short, def_long, source, status, needs_rev = t
        links = term_links.get(slug, [])

        related_html = ''
        see_also_html = ''
        for lk in links:
            link_el = f'<a href="{lk["slug"]}.html">{escape(lk["label"])}</a>'
            if lk['type'] == 'SEE_ALSO':
                see_also_html += link_el
            else:
                related_html += link_el

        links_section = ''
        if related_html:
            links_section += f'<div class="related-terms"><h4>Related Terms</h4>{related_html}</div>'
        if see_also_html:
            links_section += f'<div class="related-terms"><h4>See Also</h4>{see_also_html}</div>'

        review_html = review_badge_html(needs_rev)
        source_html = f'<div class="source-basis"><strong>Sources:</strong> {escape(source or "")}</div>' if source else ''

        detail_body = f"""
        <div class="dict-detail">
            <p><a href="index.html">&larr; Dictionary</a></p>
            <h2>{escape(label)} {review_html}</h2>
            <div class="category-label">{escape(category)}</div>
            <div class="definition-short">{escape(def_short)}</div>
            <div class="definition-long">{escape(def_long or '')}</div>
            {source_html}
            {links_section}
        </div>"""

        term_page = page_shell(label, detail_body, active_nav='dictionary', depth=1)
        (dict_dir / f'{slug}.html').write_text(term_page, encoding='utf-8')

    print(f"  dictionary/index.html + {len(terms)} term pages")


# ============================================================
# Marginalia folio detail pages
# ============================================================

def build_marginalia_pages(conn):
    """Generate marginalia/index.html and marginalia/[signature].html."""
    cur = conn.cursor()
    marg_dir = SITE_DIR / 'marginalia'
    marg_dir.mkdir(exist_ok=True)

    # Get all matched signatures with their images and annotations
    cur.execute("""
        SELECT
            r.signature_ref, r.thesis_page, r.context_text, r.marginal_text,
            r.chapter_num, m.shelfmark, m.institution, m.city,
            i.filename, i.relative_path, i.folio_number, i.side,
            mat.confidence, mat.needs_review,
            h.hand_label, h.attribution, h.is_alchemist, h.school,
            sm.quire, sm.leaf_in_quire
        FROM matches mat
        JOIN dissertation_refs r ON mat.ref_id = r.id
        JOIN images i ON mat.image_id = i.id
        JOIN manuscripts m ON i.manuscript_id = m.id
        LEFT JOIN signature_map sm ON LOWER(r.signature_ref) = LOWER(sm.signature)
        LEFT JOIN annotator_hands h ON r.hand_id = h.id
        WHERE i.page_type = 'PAGE'
        ORDER BY COALESCE(sm.folio_number, 999), m.shelfmark
    """)

    # Group by signature
    by_sig = {}
    for row in cur.fetchall():
        sig = row[0]
        by_sig.setdefault(sig, []).append(row)

    marg_css = '<style>' + """
        .marg-detail { max-width: 1000px; margin: 2rem auto; padding: 0 2rem; }
        .marg-detail h2 { color: var(--accent); margin-bottom: 0.5rem; }
        .marg-images { display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 1.5rem; margin: 1.5rem 0; }
        .marg-image-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 4px; overflow: hidden; }
        .marg-image-card img { width: 100%; display: block; }
        .marg-image-card .caption { padding: 0.75rem 1rem; font-size: 0.85rem; font-family: var(--font-sans); }
        .marg-annotation { background: var(--bg-card); border: 1px solid var(--border); border-radius: 4px; padding: 1.5rem; margin-bottom: 1rem; }
        .marg-annotation .marginal-text { font-style: italic; font-size: 1.05rem; padding: 0.75rem; border-left: 3px solid var(--accent-light); margin: 0.75rem 0; }
        .marg-annotation .context { font-size: 0.9rem; color: var(--text-muted); line-height: 1.6; max-height: 200px; overflow-y: auto; }
        .marg-annotation .hand-info { font-size: 0.85rem; font-family: var(--font-sans); color: var(--text-muted); margin-top: 0.5rem; }
        .alchemist-tag { display: inline-block; padding: 0.1rem 0.5rem; background: #e8d4d4; color: #6b2323; border-radius: 2px; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; }
        .marg-index { max-width: 1000px; margin: 2rem auto; padding: 0 2rem; }
        .marg-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }
        .marg-grid a { display: block; padding: 0.75rem 1rem; background: var(--bg-card); border: 1px solid var(--border); border-radius: 3px; text-decoration: none; color: var(--text); transition: all 0.2s; }
        .marg-grid a:hover { border-color: var(--accent); color: var(--accent); transform: translateY(-1px); }
        .marg-grid .sig-label { font-weight: 600; font-size: 1.1rem; color: var(--accent); }
        .marg-grid .sig-meta { font-size: 0.8rem; color: var(--text-muted); font-family: var(--font-sans); }
    """ + '</style>'

    # Build individual folio pages
    for sig, rows in by_sig.items():
        sig_slug = sig.lower().replace(' ', '')

        images_html = ''
        annotations_html = ''
        seen_images = set()

        for row in rows:
            (sig_ref, thesis_page, context, marginal, chapter,
             shelfmark, institution, city, img_file, img_path,
             folio_num, side, confidence, needs_rev,
             hand_label, attribution, is_alchemist, school,
             quire, leaf) = row

            # Image card (deduplicate)
            if img_file not in seen_images:
                seen_images.add(img_file)
                conf_badge = confidence_badge_html(confidence)
                rev_badge = '<span class="review-badge">Unverified</span>' if needs_rev else ''
                images_html += f"""
                    <div class="marg-image-card">
                        <img src="../{img_path}" alt="Folio {sig}" loading="lazy">
                        <div class="caption">
                            {escape(institution)}, {escape(city)} &mdash; {escape(shelfmark)}
                            {conf_badge} {rev_badge}
                        </div>
                    </div>"""

            # Annotation card
            hand_html = ''
            if hand_label:
                alch_tag = ' <span class="alchemist-tag">Alchemist</span>' if is_alchemist else ''
                school_info = f' ({escape(school)})' if school else ''
                hand_html = f'<div class="hand-info">Hand {escape(hand_label)}: {escape(attribution or "Anonymous")}{school_info}{alch_tag}</div>'

            marginal_html = ''
            if marginal:
                marginal_html = f'<div class="marginal-text">&ldquo;{escape(marginal)}&rdquo;</div>'

            context_html = ''
            if context:
                ctx = context[:500] + ('...' if len(context) > 500 else '')
                context_html = f'<div class="context">{escape(ctx)}</div>'

            annotations_html += f"""
                <div class="marg-annotation">
                    {hand_html}
                    {marginal_html}
                    {context_html}
                    <div class="hand-info">Russell, PhD Thesis, p. {thesis_page} (Ch. {chapter})</div>
                </div>"""

        folio_info = f'Folio {rows[0][10] or "?"}{rows[0][11] or ""}'
        quire_info = f', Quire {rows[0][18]}' if rows[0][18] else ''

        detail_body = f"""
        <div class="marg-detail">
            <p><a href="index.html">&larr; All Folios</a></p>
            <h2>Signature {escape(sig)}</h2>
            <p style="color:var(--text-muted); font-family:var(--font-sans); margin-bottom:1.5rem">
                {folio_info}{quire_info}</p>
            <div class="marg-images">{images_html}</div>
            <h3 style="margin:1.5rem 0 1rem">Annotations</h3>
            {annotations_html}
        </div>"""

        detail_page = page_shell(f'Folio {sig}', detail_body, active_nav='marginalia', depth=1)
        (marg_dir / f'{sig_slug}.html').write_text(detail_page, encoding='utf-8')

    # Build marginalia index
    grid_items = ''
    for sig in sorted(by_sig.keys(), key=lambda s: (
        # Sort by quire then leaf
        by_sig[s][0][18] or 'zzz',
        by_sig[s][0][10] or 999
    )):
        rows = by_sig[sig]
        sig_slug = sig.lower().replace(' ', '')
        n_images = len(set(r[8] for r in rows))
        n_annotations = len(rows)
        has_alchemist = any(r[16] for r in rows)
        alch = ' <span class="alchemist-tag">Alch.</span>' if has_alchemist else ''

        grid_items += f"""
            <a href="{sig_slug}.html">
                <div class="sig-label">{escape(sig)}{alch}</div>
                <div class="sig-meta">{n_images} image{'s' if n_images != 1 else ''}, {n_annotations} ref{'s' if n_annotations != 1 else ''}</div>
            </a>"""

    index_body = f"""
        <div class="marg-index">
            <div class="intro">
                <h2>Marginalia by Folio</h2>
                <p>{len(by_sig)} annotated folios documented from Russell's thesis.
                Click any signature to see images and annotations.</p>
            </div>
            <div class="marg-grid">{grid_items}</div>
        </div>"""

    index_page = page_shell('Marginalia', index_body, active_nav='marginalia', depth=1)
    (marg_dir / 'index.html').write_text(index_page, encoding='utf-8')
    print(f"  marginalia/index.html + {len(by_sig)} folio pages")


# ============================================================
# Bibliography page
# ============================================================

def build_bibliography_page(conn):
    """Generate bibliography.html with full HP bibliography from DB."""
    cur = conn.cursor()

    # Get all bibliography entries
    cur.execute("""
        SELECT id, author, title, year, pub_type, journal_or_publisher,
               hp_relevance, topic_cluster, in_collection, notes,
               review_status, needs_review
        FROM bibliography
        ORDER BY
            CASE WHEN year IS NULL THEN 9999 ELSE CAST(year AS INTEGER) END,
            author
    """)
    entries = cur.fetchall()

    # Group by relevance
    by_relevance = {}
    for e in entries:
        rel = e[6] or 'TANGENTIAL'
        by_relevance.setdefault(rel, []).append(e)

    relevance_order = ['PRIMARY', 'DIRECT', 'INDIRECT', 'TANGENTIAL']
    relevance_labels = {
        'PRIMARY': 'Primary Sources & Editions',
        'DIRECT': 'HP Scholarship (Direct)',
        'INDIRECT': 'Related Studies',
        'TANGENTIAL': 'General References',
    }

    bib_css = '<style>' + """
        .bib-page { max-width: 900px; margin: 2rem auto; padding: 0 2rem; }
        .bib-section { margin-bottom: 2.5rem; }
        .bib-section h3 {
            font-size: 1.1rem; color: var(--accent);
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.3rem; margin-bottom: 1rem;
        }
        .bib-entry { margin-bottom: 1rem; padding: 0.75rem 1rem; background: var(--bg-card); border: 1px solid var(--border); border-radius: 3px; }
        .bib-entry .bib-author { font-weight: 600; }
        .bib-entry .bib-title { font-style: italic; }
        .bib-entry .bib-details { font-size: 0.85rem; color: var(--text-muted); font-family: var(--font-sans); margin-top: 0.25rem; }
        .bib-entry .bib-badges { margin-top: 0.3rem; }
        .bib-badge-collection { display: inline-block; padding: 0.1rem 0.4rem; background: #d4edda; color: #155724; border-radius: 2px; font-size: 0.65rem; font-weight: 600; font-family: var(--font-sans); text-transform: uppercase; }
        .bib-badge-missing { display: inline-block; padding: 0.1rem 0.4rem; background: #f8d7da; color: #721c24; border-radius: 2px; font-size: 0.65rem; font-weight: 600; font-family: var(--font-sans); text-transform: uppercase; }
        .bib-stats { display: flex; gap: 1.5rem; flex-wrap: wrap; margin-bottom: 2rem; }
        .bib-stat { text-align: center; padding: 1rem; background: var(--bg-card); border: 1px solid var(--border); border-radius: 4px; flex: 1; min-width: 120px; }
        .bib-stat .num { font-size: 1.5rem; font-weight: 700; color: var(--accent); display: block; }
        .bib-stat .lbl { font-size: 0.8rem; color: var(--text-muted); font-family: var(--font-sans); }
    """ + '</style>'

    # Stats
    total = len(entries)
    in_coll = sum(1 for e in entries if e[8])
    primary = len(by_relevance.get('PRIMARY', []))
    direct = len(by_relevance.get('DIRECT', []))
    needs_rev = sum(1 for e in entries if e[11])

    stats_html = f"""
        <div class="bib-stats">
            <div class="bib-stat"><span class="num">{total}</span><span class="lbl">Total Works</span></div>
            <div class="bib-stat"><span class="num">{in_coll}</span><span class="lbl">In Collection</span></div>
            <div class="bib-stat"><span class="num">{primary}</span><span class="lbl">Primary Sources</span></div>
            <div class="bib-stat"><span class="num">{direct}</span><span class="lbl">Direct Scholarship</span></div>
            <div class="bib-stat"><span class="num">{needs_rev}</span><span class="lbl">Need Review</span></div>
        </div>"""

    # Build sections
    sections_html = ''
    for rel in relevance_order:
        items = by_relevance.get(rel, [])
        if not items:
            continue

        entries_html = ''
        for e in items:
            (eid, author, title, year, pub_type, journal,
             relevance, topic, in_coll_flag, notes,
             rev_status, needs_rev_flag) = e

            year_str = f' ({year})' if year else ''
            journal_str = f'. {escape(journal)}' if journal else ''
            type_str = f' [{pub_type}]' if pub_type else ''

            collection_badge = '<span class="bib-badge-collection">In Collection</span>' if in_coll_flag else '<span class="bib-badge-missing">Not in Collection</span>'
            review_badge = review_badge_html(needs_rev_flag) if needs_rev_flag else ''
            topic_html = topic_badges_html(topic) if topic else ''

            entries_html += f"""
                <div class="bib-entry">
                    <div><span class="bib-author">{escape(author or "")}</span>{year_str}.
                    <span class="bib-title">{escape(title)}</span>{journal_str}{type_str}.</div>
                    <div class="bib-badges">{collection_badge} {topic_html} {review_badge}</div>
                </div>"""

        label = relevance_labels.get(rel, rel)
        sections_html += f"""
            <section class="bib-section">
                <h3>{label} ({len(items)})</h3>
                {entries_html}
            </section>"""

    body = f"""
        <div class="bib-page">
            <div class="intro">
                <h2>Bibliography of the <em>Hypnerotomachia Poliphili</em></h2>
                <p>A comprehensive bibliography of editions, translations, and scholarship on
                the <em>Hypnerotomachia Poliphili</em>, compiled from Russell (2014), the
                <em>Word &amp; Image</em> special issues (1998, 2015), and ongoing research.</p>
            </div>
            {stats_html}
            {sections_html}
        </div>"""

    page = page_shell('Bibliography', body, active_nav='bibliography')
    (SITE_DIR / 'bibliography.html').write_text(page, encoding='utf-8')

    print(f"  bibliography.html: {total} entries")


# ============================================================
# About page
# ============================================================

def build_about_page(conn):
    cur = conn.cursor()

    # Get stats
    stats = {}
    for table in ['documents', 'images', 'dissertation_refs', 'matches',
                   'annotators', 'bibliography', 'scholars', 'dictionary_terms',
                   'timeline_events']:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = cur.fetchone()[0]
        except:
            stats[table] = 0

    cur.execute("SELECT COUNT(*) FROM matches WHERE confidence='HIGH'")
    stats['high_conf'] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM matches WHERE confidence='LOW'")
    stats['low_conf'] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM bibliography WHERE in_collection=1")
    stats['in_collection'] = cur.fetchone()[0]

    body = f"""
        <div class="scholar-detail">
            <h2>About This Project</h2>

            <div class="paper-detail">
                <h3>What Is This?</h3>
                <div class="paper-summary-full"><p>
                This is a digital humanities project documenting the readership and
                marginalia of the <em>Hypnerotomachia Poliphili</em> (Venice: Aldus Manutius, 1499),
                based on James Russell's PhD thesis
                <em>Many Other Things Worthy of Knowledge and Memory</em> (Durham University, 2014).
                </p><p>
                Russell conducted a world census of annotated copies of the HP, documenting
                marginalia by readers including Ben Jonson, Pope Alexander VII, Benedetto Giovio,
                and anonymous alchemists. This site presents his findings alongside photographs
                of two annotated copies, a dictionary of HP terminology, and an index of
                scholarship spanning five centuries.
                </p></div>
            </div>

            <div class="paper-detail">
                <h3>Database Statistics</h3>
                <div class="paper-summary-full">
                <ul style="list-style:none; padding:0;">
                    <li><strong>{stats['images']}</strong> manuscript images catalogued</li>
                    <li><strong>{stats['dissertation_refs']}</strong> folio references extracted from Russell's thesis</li>
                    <li><strong>{stats['matches']}</strong> image-reference matches
                        ({stats['high_conf']} high confidence, {stats['low_conf']} low/provisional)</li>
                    <li><strong>{stats['annotators']}</strong> annotator hands identified</li>
                    <li><strong>{stats['bibliography']}</strong> works in bibliography
                        ({stats['in_collection']} in our collection)</li>
                    <li><strong>{stats['scholars']}</strong> scholar profiles</li>
                    <li><strong>{stats['dictionary_terms']}</strong> dictionary terms</li>
                    <li><strong>{stats['timeline_events']}</strong> timeline events</li>
                </ul>
                </div>
            </div>

            <div class="paper-detail">
                <h3>Data Provenance</h3>
                <div class="paper-summary-full"><p>
                Content on this site has varying levels of verification:
                </p>
                <ul>
                    <li><strong>Verified</strong>: Signature maps, collation formulae, and image
                    cataloging are deterministic and correct.</li>
                    <li><strong>High confidence</strong>: Siena O.III.38 image matches use explicit
                    recto/verso naming.</li>
                    <li><strong>Low confidence</strong>: BL C.60.o.12 matches assume sequential photo
                    numbers equal folio numbers. The BL copy is the 1545 edition; the signature map
                    is based on the 1499. Manual verification needed.</li>
                    <li><strong>Unreviewed</strong>: Scholar summaries, dictionary definitions, and
                    hand attributions were generated with LLM assistance and have not been verified
                    by a domain expert. These are marked with
                    <span class="review-badge" style="font-size:0.7rem">Unreviewed</span> badges.</li>
                </ul>
                </div>
            </div>

            <div class="paper-detail">
                <h3>How to Rebuild</h3>
                <div class="paper-summary-full"><p>
                The site is generated from a SQLite database (<code>db/hp.db</code>).
                To rebuild all pages:
                </p>
                <pre style="background:var(--bg); padding:1rem; border-radius:4px; overflow-x:auto; font-size:0.85rem">
python scripts/migrate_v2.py        # Schema migration (idempotent)
python scripts/seed_dictionary.py   # Dictionary terms (idempotent)
python scripts/build_site.py        # Generate all HTML + JSON
                </pre>
                <p>Individual pipeline steps:</p>
                <pre style="background:var(--bg); padding:1rem; border-radius:4px; overflow-x:auto; font-size:0.85rem">
python scripts/init_db.py           # Initialize DB schema
python scripts/catalog_images.py    # Catalog manuscript images
python scripts/build_signature_map.py  # Build signature map
python scripts/extract_references.py   # Extract refs from thesis PDF
python scripts/match_refs_to_images.py # Match refs to images
python scripts/add_hands.py         # Add annotator hand profiles
python scripts/add_bibliography.py  # Add bibliography and timeline
                </pre>
                </div>
            </div>
        </div>"""

    page = page_shell('About', body, active_nav='about')
    (SITE_DIR / 'about.html').write_text(page, encoding='utf-8')
    print("  about.html")


# ============================================================
# Documents tab
# ============================================================

# Document metadata: (filename, title, one-line summary)
DOC_METADATA = {
    'README.md': ('README', 'Project overview, architecture, rebuild instructions, and data provenance table.'),
    'HPCONCORD.md': ('Concordance Methodology', 'How we built the 6-step folio-to-image concordance from Russell\'s thesis to manuscript photographs.'),
    'HPDECKARD.md': ('Boundary Audit v1', 'Deckard boundary map distinguishing deterministic tasks from probabilistic (LLM) tasks across 11 scripts.'),
    'HPDECKARD2.md': ('Boundary Audit v2', 'Second Deckard audit covering bibliography expansion, web research ingestion, and the hybrid verification pipeline.'),
    'HPMIT.md': ('MIT Site Analysis', 'Reverse-engineering of the MIT Electronic Hypnerotomachia (1997): strengths, weaknesses, and lessons for our digital edition.'),
    'HPMULTIMODAL.md': ('Multimodal RAG Study', 'How vision models and multimodal retrieval could read our 674 manuscript images to solve the BL confidence problem.'),
    'HPproposals.md': ('Content Quality Proposals', 'Six proposals for improving dictionary, bibliography, scholar, and summary pages through templating and LLM reading.'),
    'HPAGENTS.md': ('Agent Usage Analysis', 'Why and how Claude agents were used: what worked (foreground batches), what failed (background web tasks).'),
    'HPEMPTYOUTPUTFILES.md': ('Empty Output Files Post-Mortem', 'Root cause analysis of 0-byte agent output files and lessons for background agent reliability.'),
    'MISTAKESTOAVOID.md': ('Mistakes to Avoid', 'Twelve hard-won lessons from this project: provenance tagging, confidence scoring, name matching, and more.'),
    'AUDIT_REPORT.md': ('Audit Report', 'Validation results: what changed in V2 migration, what remains provisional, what still needs human review.'),
    'HPONTOLOGY.md': ('Ontology Design', 'Data model and entity relationships for the HP knowledge base: manuscripts, folios, hands, scholars, terms.'),
    'HPSCHOLARS.md': ('Scholars Analysis', 'Strategy for building scholar profiles and article summaries from our PDF corpus.'),
    'HPWEB.md': ('Web Architecture', 'Design decisions for the static site: why no framework, how SQLite drives page generation, URL structure.'),
}

# Script metadata: (filename, title, one-line summary)
SCRIPT_METADATA = {
    'init_db.py': ('Initialize Database', 'Creates SQLite schema (7 core tables) and catalogs PDFs/documents from the filesystem.'),
    'catalog_images.py': ('Catalog Images', 'Parses image filenames from BL and Siena collections into the images table with folio/side metadata.'),
    'build_signature_map.py': ('Build Signature Map', 'Generates the 448-entry signature-to-folio concordance from the Aldine collation formula (a-z, A-G).'),
    'extract_references.py': ('Extract References', 'Uses PyMuPDF + regex to extract 282 folio/signature references from Russell\'s PhD thesis PDF.'),
    'match_refs_to_images.py': ('Match Refs to Images', 'SQL join pipeline matching dissertation references to manuscript images via the signature map.'),
    'add_hands.py': ('Add Annotator Hands', 'Creates 11 annotator hand profiles and attributes dissertation references to specific hands.'),
    'add_bibliography.py': ('Add Bibliography', 'Populates bibliography (58 entries), scholars (29), timeline (39 events) from hardcoded research data.'),
    'migrate_v2.py': ('Schema Migration V2', 'Adds annotations, annotators, doc_folio_refs, dictionary tables, review/provenance columns. Downgrades BL confidence.'),
    'seed_dictionary.py': ('Seed Dictionary', 'Inserts 37 dictionary terms across 6 categories with 76 bidirectional cross-reference links.'),
    'build_site.py': ('Build Site', 'Unified site generator: exports data.json, builds all HTML pages (scholars, dictionary, marginalia, bibliography, docs, code, about).'),
    'build_scholar_profiles.py': ('Build Scholar Profiles (Legacy)', 'Original scholar page generator from summaries.json. Superseded by build_site.py.'),
    'export_showcase_data.py': ('Export Showcase Data (Legacy)', 'Original data.json exporter for the gallery. Superseded by build_site.py.'),
    'validate.py': ('Validate & QA', 'Checks data integrity (duplicate slugs, broken links, confidence distribution) and writes AUDIT_REPORT.md.'),
    'ingest_perplexity.py': ('Ingest Perplexity Research', 'Adds 9 bibliography entries and 3 timeline events from HPPERPLEXITY.txt web research.'),
    'pdf_to_markdown.py': ('PDF to Markdown', 'Extracts all PDFs to markdown with YAML frontmatter, page markers, and metadata lookup.'),
    'chunk_documents.py': ('Chunk Documents', 'Splits markdown files into ~1500-word semantic chunks for RAG/retrieval systems.'),
}


def markdown_to_html(md_text):
    """Minimal markdown-to-HTML conversion for document display."""
    import re
    lines = md_text.split('\n')
    html_lines = []
    in_code = False
    in_list = False
    in_table = False
    table_header_done = False

    for line in lines:
        # Code blocks
        if line.strip().startswith('```'):
            if in_code:
                html_lines.append('</code></pre>')
                in_code = False
            else:
                lang = line.strip()[3:]
                html_lines.append(f'<pre><code class="lang-{lang}">')
                in_code = True
            continue
        if in_code:
            html_lines.append(escape(line))
            continue

        # Close list if needed
        if in_list and not line.strip().startswith(('-', '*', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
            html_lines.append('</ul>')
            in_list = False

        # Tables
        if '|' in line and line.strip().startswith('|'):
            cells = [c.strip() for c in line.strip().split('|')[1:-1]]
            if all(set(c) <= set('- :') for c in cells):
                table_header_done = True
                continue
            if not in_table:
                html_lines.append('<table class="doc-table">')
                in_table = True
            tag = 'th' if not table_header_done else 'td'
            row = ''.join(f'<{tag}>{escape(c)}</{tag}>' for c in cells)
            html_lines.append(f'<tr>{row}</tr>')
            continue
        elif in_table:
            html_lines.append('</table>')
            in_table = False
            table_header_done = False

        stripped = line.strip()

        # Headings
        if stripped.startswith('### '):
            html_lines.append(f'<h4>{escape(stripped[4:])}</h4>')
        elif stripped.startswith('## '):
            html_lines.append(f'<h3>{escape(stripped[3:])}</h3>')
        elif stripped.startswith('# '):
            html_lines.append(f'<h2>{escape(stripped[2:])}</h2>')
        elif stripped.startswith('---'):
            html_lines.append('<hr>')
        elif stripped.startswith(('- ', '* ')):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            html_lines.append(f'<li>{escape(stripped[2:])}</li>')
        elif stripped.startswith('>'):
            html_lines.append(f'<blockquote>{escape(stripped[1:].strip())}</blockquote>')
        elif stripped == '':
            html_lines.append('')
        else:
            # Apply inline formatting
            text = escape(stripped)
            # Bold
            text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
            # Italic
            text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
            # Inline code
            text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
            html_lines.append(f'<p>{text}</p>')

    if in_list:
        html_lines.append('</ul>')
    if in_table:
        html_lines.append('</table>')
    if in_code:
        html_lines.append('</code></pre>')

    return '\n'.join(html_lines)


def build_docs_pages():
    """Generate docs/index.html and docs/*.html from project markdown files."""
    docs_dir = SITE_DIR / 'docs'
    docs_dir.mkdir(exist_ok=True)

    doc_css = '<style>' + """
        .docs-page { max-width: 900px; margin: 2rem auto; padding: 0 2rem; }
        .docs-table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; }
        .docs-table th, .docs-table td { padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid var(--border); }
        .docs-table th { font-family: var(--font-sans); font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
        .docs-table td a { color: var(--accent); text-decoration: none; font-weight: 600; }
        .docs-table td a:hover { text-decoration: underline; }
        .docs-table .doc-summary { font-size: 0.85rem; color: var(--text-muted); }
        .doc-content { max-width: 800px; margin: 2rem auto; padding: 0 2rem; }
        .doc-content h2 { color: var(--accent); margin: 2rem 0 0.5rem; }
        .doc-content h3 { color: var(--text); margin: 1.5rem 0 0.5rem; }
        .doc-content h4 { color: var(--text-muted); margin: 1rem 0 0.5rem; }
        .doc-content p { margin-bottom: 0.75rem; line-height: 1.7; }
        .doc-content pre { background: var(--bg); padding: 1rem; border-radius: 4px; overflow-x: auto; font-size: 0.85rem; margin: 1rem 0; }
        .doc-content code { font-size: 0.9em; background: var(--bg); padding: 0.1rem 0.3rem; border-radius: 2px; }
        .doc-content pre code { background: none; padding: 0; }
        .doc-content blockquote { border-left: 3px solid var(--accent-light); padding-left: 1rem; color: var(--text-muted); font-style: italic; margin: 1rem 0; }
        .doc-content ul { margin: 0.5rem 0 1rem 1.5rem; }
        .doc-content li { margin-bottom: 0.3rem; line-height: 1.6; }
        .doc-content hr { border: none; border-top: 1px solid var(--border); margin: 2rem 0; }
        .doc-content table.doc-table { width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.9rem; }
        .doc-content table.doc-table th, .doc-content table.doc-table td { padding: 0.5rem 0.75rem; border: 1px solid var(--border); }
        .doc-content table.doc-table th { background: var(--bg); font-weight: 600; }
    """ + '</style>'

    # Read all docs and build pages
    docs = []
    for filename, (title, summary) in sorted(DOC_METADATA.items()):
        filepath = BASE_DIR / filename
        if not filepath.exists():
            continue

        slug = slugify(title)
        content = filepath.read_text(encoding='utf-8')
        word_count = len(content.split())

        docs.append({
            'filename': filename,
            'title': title,
            'summary': summary,
            'slug': slug,
            'word_count': word_count,
        })

        # Build detail page
        content_html = markdown_to_html(content)
        detail_body = f"""
        <div class="doc-content">
            <p><a href="index.html">&larr; All Documents</a></p>
            <h2>{escape(title)}</h2>
            <p style="color:var(--text-muted); font-family:var(--font-sans); font-size:0.85rem; margin-bottom:1.5rem">
                {escape(filename)} &mdash; {word_count:,} words</p>
            {content_html}
        </div>"""

        detail_page = page_shell(title, detail_body, active_nav='docs', depth=1)
        (docs_dir / f'{slug}.html').write_text(detail_page, encoding='utf-8')

    # Build index page
    rows_html = ''
    for d in docs:
        rows_html += f"""
            <tr>
                <td><a href="{d['slug']}.html">{escape(d['title'])}</a></td>
                <td class="doc-summary">{escape(d['summary'])}</td>
                <td style="font-family:var(--font-sans); font-size:0.85rem; white-space:nowrap">{d['word_count']:,}</td>
            </tr>"""

    index_body = f"""
        <div class="docs-page">
            <div class="intro">
                <h2>Project Documents</h2>
                <p>{len(docs)} documents covering methodology, architecture, analysis, and lessons learned.</p>
            </div>
            <table class="docs-table">
                <thead><tr><th>Document</th><th>Description</th><th>Words</th></tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>"""

    index_page = page_shell('Documents', index_body, active_nav='docs', depth=1)
    (docs_dir / 'index.html').write_text(index_page, encoding='utf-8')
    print(f"  docs/index.html + {len(docs)} document pages")


def build_code_pages():
    """Generate code/index.html and code/*.html from Python scripts."""
    code_dir = SITE_DIR / 'code'
    code_dir.mkdir(exist_ok=True)

    code_css = '<style>' + """
        .code-page { max-width: 900px; margin: 2rem auto; padding: 0 2rem; }
        .code-table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; }
        .code-table th, .code-table td { padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid var(--border); }
        .code-table th { font-family: var(--font-sans); font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
        .code-table td a { color: var(--accent); text-decoration: none; font-weight: 600; font-family: monospace; }
        .code-table td a:hover { text-decoration: underline; }
        .code-table .code-summary { font-size: 0.85rem; color: var(--text-muted); }
        .code-content { max-width: 1000px; margin: 2rem auto; padding: 0 2rem; }
        .code-content h2 { color: var(--accent); margin-bottom: 0.5rem; }
        .code-content pre {
            background: #1e1e1e; color: #d4d4d4; padding: 1.5rem; border-radius: 4px;
            overflow-x: auto; font-size: 0.82rem; line-height: 1.5;
            max-height: 80vh; overflow-y: auto;
        }
        .code-content .line-num { color: #858585; user-select: none; display: inline-block; width: 3.5em; text-align: right; margin-right: 1em; }
        .code-meta { font-family: var(--font-sans); font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1.5rem; }
    """ + '</style>'

    scripts = []
    scripts_dir = BASE_DIR / 'scripts'

    for filename, (title, summary) in sorted(SCRIPT_METADATA.items()):
        filepath = scripts_dir / filename
        if not filepath.exists():
            continue

        slug = slugify(filename.replace('.py', ''))
        content = filepath.read_text(encoding='utf-8')
        line_count = len(content.splitlines())

        scripts.append({
            'filename': filename,
            'title': title,
            'summary': summary,
            'slug': slug,
            'line_count': line_count,
        })

        # Build detail page with syntax-highlighted code
        lines = content.splitlines()
        code_lines = []
        for i, line in enumerate(lines, 1):
            num = f'<span class="line-num">{i}</span>'
            code_lines.append(f'{num}{escape(line)}')
        code_html = '\n'.join(code_lines)

        detail_body = f"""
        <div class="code-content">
            <p><a href="index.html">&larr; All Scripts</a></p>
            <h2>{escape(title)}</h2>
            <div class="code-meta">{escape(filename)} &mdash; {line_count} lines</div>
            <p style="margin-bottom:1rem">{escape(summary)}</p>
            <pre>{code_html}</pre>
        </div>"""

        detail_page = page_shell(title, detail_body, active_nav='code', depth=1)
        (code_dir / f'{slug}.html').write_text(detail_page, encoding='utf-8')

    # Build index page
    rows_html = ''
    for s in scripts:
        rows_html += f"""
            <tr>
                <td><a href="{s['slug']}.html">{escape(s['filename'])}</a></td>
                <td>{escape(s['title'])}</td>
                <td class="code-summary">{escape(s['summary'])}</td>
                <td style="font-family:var(--font-sans); font-size:0.85rem; white-space:nowrap">{s['line_count']}</td>
            </tr>"""

    index_body = f"""
        <div class="code-page">
            <div class="intro">
                <h2>Pipeline Scripts</h2>
                <p>{len(scripts)} Python scripts that build the database, generate the site, and validate the data.
                SQLite is the source of truth; these scripts are the processing pipeline.</p>
            </div>
            <table class="code-table">
                <thead><tr><th>Script</th><th>Name</th><th>Description</th><th>Lines</th></tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>"""

    index_page = page_shell('Code', index_body, active_nav='code', depth=1)
    (code_dir / 'index.html').write_text(index_page, encoding='utf-8')
    print(f"  code/index.html + {len(scripts)} script pages")


# ============================================================
# Update main index.html with nav
# ============================================================

def update_index_nav():
    """Replace nav bar in index.html with current version, fix CSS links."""
    index_path = SITE_DIR / 'index.html'
    if not index_path.exists():
        return

    content = index_path.read_text(encoding='utf-8')
    updated = False

    # Replace any existing nav with current 8-link version
    import re
    nav = nav_html('home')
    old_nav_pattern = r'<nav class="site-nav">.*?</nav>'
    if re.search(old_nav_pattern, content):
        content = re.sub(old_nav_pattern, nav, content)
        updated = True
    elif 'site-nav' not in content:
        content = content.replace(
            '</div>\n    </header>',
            f'    {nav}\n        </div>\n    </header>',
            1
        )
        updated = True

    # Fix CSS links: add scholars.css and components.css if missing
    if 'scholars.css' not in content:
        content = content.replace(
            '<link rel="stylesheet" href="style.css">',
            '<link rel="stylesheet" href="style.css">\n    <link rel="stylesheet" href="scholars.css">\n    <link rel="stylesheet" href="components.css">'
        )
        updated = True

    # Add meta description if missing
    if 'meta name="description"' not in content:
        content = content.replace(
            '<meta name="viewport"',
            '<meta name="description" content="Digital scholarship and marginalia of the Hypnerotomachia Poliphili (Venice, 1499)">\n    <meta name="viewport"'
        )
        updated = True

    if updated:
        index_path.write_text(content, encoding='utf-8')
        print("  index.html: nav + CSS updated")


# ============================================================
# Update CSS for new components
# ============================================================

def update_styles():
    """Append new styles to style.css for nav, badges, etc."""
    css_path = SITE_DIR / 'style.css'
    content = css_path.read_text(encoding='utf-8')

    if 'site-nav' in content:
        return  # Already updated

    additions = """

/* ===== Site Navigation ===== */
.site-nav {
    margin-top: 1.5rem;
    display: flex;
    justify-content: center;
    gap: 0.25rem;
    flex-wrap: wrap;
}

.site-nav a {
    color: #9a8c7a;
    text-decoration: none;
    font-family: var(--font-sans);
    font-size: 0.9rem;
    padding: 0.4rem 1rem;
    border-radius: 3px;
    transition: all 0.2s;
}

.site-nav a:hover {
    color: var(--accent-light);
    background: rgba(255,255,255,0.05);
}

.site-nav a.active {
    color: var(--header-text);
    background: rgba(255,255,255,0.1);
}

/* ===== Review & Confidence Badges ===== */
.review-badge {
    display: inline-block;
    padding: 0.1rem 0.4rem;
    background: #fff3cd;
    color: #856404;
    border-radius: 2px;
    font-size: 0.65rem;
    font-weight: 600;
    font-family: var(--font-sans);
    text-transform: uppercase;
    letter-spacing: 0.03em;
    vertical-align: middle;
    margin-left: 0.3rem;
}

.confidence-badge {
    display: inline-block;
    padding: 0.1rem 0.4rem;
    border-radius: 2px;
    font-size: 0.65rem;
    font-weight: 600;
    font-family: var(--font-sans);
    text-transform: uppercase;
    letter-spacing: 0.03em;
    vertical-align: middle;
    margin-left: 0.3rem;
}

.confidence-high { background: #d4edda; color: #155724; }
.confidence-medium { background: #fff3cd; color: #856404; }
.confidence-low { background: #f8d7da; color: #721c24; }
.confidence-provisional { background: #e2e3e5; color: #383d41; }
"""

    css_path.write_text(content + additions, encoding='utf-8')
    print("  style.css: nav + badge styles added")


# ============================================================
# Main
# ============================================================

def main():
    print("=== Building Site ===\n")

    conn = sqlite3.connect(DB_PATH)

    print("Exporting data...")
    export_data_json(conn)

    print("\nBuilding pages...")
    update_styles()
    update_index_nav()
    build_scholars_pages(conn)
    build_dictionary_pages(conn)
    build_marginalia_pages(conn)
    build_bibliography_page(conn)
    build_docs_pages()
    build_code_pages()
    build_about_page(conn)

    conn.close()
    print("\n=== Build Complete ===")


if __name__ == "__main__":
    main()
