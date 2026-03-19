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
        (f'{prefix}digital-edition.html', 'Edition', 'edition'),
        (f'{prefix}russell-alchemical-hands.html', 'Alchemical Hands', 'russell'),
        (f'{prefix}concordance-method.html', 'Concordance', 'concordance'),
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
                <h2>Scholars of the <em>Hypnerotomachia</em></h2>
                <p>The <em>Hypnerotomachia Poliphili</em> has attracted sustained scholarly
                attention since Domenico Gnoli's 1899 study, drawing researchers from
                art history, architectural theory, literary criticism, book history,
                reception studies, and the history of alchemy. This index presents
                {len(by_author)} scholars whose work shapes our understanding of the book
                and its readers, with {len(summaries)} article and monograph summaries.</p>
                <p>Each scholar page collects their contributions to HP studies alongside
                publication details and topic classifications. Summaries were generated
                with LLM assistance from our PDF corpus and are marked accordingly.
                We welcome corrections from the scholars represented here.</p>
            </div>
            {''.join(scholar_cards)}
        </div>"""

    index_page = page_shell('Scholars', index_body, active_nav='scholars')
    (SITE_DIR / 'scholars.html').write_text(index_page, encoding='utf-8')
    print(f"  scholars.html + {len(by_author)} scholar pages")


# ============================================================
# Dictionary pages
# ============================================================

def review_status_badge(status):
    """Generate a colored review status badge."""
    colors = {
        'DRAFT': ('review-badge-draft', 'Draft'),
        'REVIEWED': ('review-badge-reviewed', 'Reviewed'),
        'VERIFIED': ('review-badge-verified', 'Verified'),
        'PROVISIONAL': ('review-badge-provisional', 'Provisional'),
    }
    cls, label = colors.get(status, ('review-badge-draft', status or 'Draft'))
    return f'<span class="review-status-badge {cls}">{label}</span>'


def build_dictionary_pages(conn):
    """Generate dictionary/index.html and dictionary/*.html from DB."""
    cur = conn.cursor()
    dict_dir = SITE_DIR / 'dictionary'
    dict_dir.mkdir(exist_ok=True)

    # Get all terms with enriched fields
    cur.execute("""
        SELECT id, slug, label, category, definition_short, definition_long,
               source_basis, review_status, needs_review,
               significance_to_hp, significance_to_scholarship,
               source_documents, source_page_refs, source_quotes_short,
               source_method, confidence, notes, related_scholars
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
                <p>The <em>Hypnerotomachia Poliphili</em> sits at the intersection
                of book history, architectural theory, alchemical tradition,
                Renaissance philology, and dream literature. This dictionary
                defines {len(terms)} terms across {len(by_category)} categories
                that are essential for reading the book and its scholarship:
                from bibliographic fundamentals like <em>signature</em> and
                <em>quire</em> to interpretive concepts like <em>prisca sapientia</em>
                and <em>chemical wedding</em>.</p>
                <p>Terms are cross-linked&mdash;each page lists related concepts
                and see-also references, so you can follow threads through the
                HP's intellectual world. Definitions draw on specific scholarly
                sources cited on each page.</p>
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
        (tid, slug, label, category, def_short, def_long, source, status,
         needs_rev, sig_hp, sig_schol, src_docs, src_pages, src_quotes,
         src_method, confidence, notes, related_scholars) = t
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

        # Status badge
        status_html = review_status_badge(status)
        source_html = f'<div class="source-basis"><strong>Sources:</strong> {escape(source or "")}</div>' if source else ''

        # Significance sections
        sig_hp_html = ''
        if sig_hp:
            sig_hp_html = f'''
            <div class="dict-section">
                <h3>Why It Matters for the <em>Hypnerotomachia</em></h3>
                <p>{escape(sig_hp)}</p>
            </div>'''

        sig_schol_html = ''
        if sig_schol:
            sig_schol_html = f'''
            <div class="dict-section">
                <h3>Why It Matters in Scholarship</h3>
                <p>{escape(sig_schol)}</p>
            </div>'''

        # Evidence section
        evidence_html = ''
        if src_quotes:
            quotes = src_quotes.split(' | ')
            quote_items = ''.join(f'<li>{escape(q)}</li>' for q in quotes)
            evidence_html = f'''
            <div class="dict-section">
                <h3>Key Passages / Evidence</h3>
                <ul class="evidence-list">{quote_items}</ul>
            </div>'''

        # Source documents
        src_docs_html = ''
        if src_docs:
            src_docs_html = f'''
            <div class="dict-section">
                <h3>Source Documents</h3>
                <p class="source-docs">{escape(src_docs)}</p>
            </div>'''

        # Page references
        src_pages_html = ''
        if src_pages:
            src_pages_html = f'<div class="source-pages"><strong>Page references:</strong> {escape(src_pages)}</div>'

        # Related scholars
        scholars_html = ''
        if related_scholars:
            scholars_html = f'''
            <div class="dict-section">
                <h3>Related Scholars / Bibliography</h3>
                <p>{escape(related_scholars)}</p>
            </div>'''

        # Provenance section
        provenance_items = []
        if src_method:
            provenance_items.append(f'Source method: {escape(src_method)}')
        if confidence:
            provenance_items.append(f'Confidence: {escape(confidence)}')
        if notes:
            provenance_items.append(f'Notes: {escape(notes)}')
        provenance_html = ''
        if provenance_items:
            prov_list = ''.join(f'<li>{p}</li>' for p in provenance_items)
            provenance_html = f'''
            <div class="dict-section provenance-section">
                <h3>Review Status / Provenance</h3>
                <div class="provenance-status">{status_html}</div>
                <ul class="provenance-list">{prov_list}</ul>
            </div>'''

        detail_body = f"""
        <div class="dict-detail">
            <p><a href="index.html">&larr; Dictionary</a></p>
            <h2>{escape(label)} {status_html}</h2>
            <div class="category-label">{escape(category)}</div>
            <div class="definition-short">{escape(def_short)}</div>
            <div class="definition-long">{escape(def_long or '')}</div>
            {sig_hp_html}
            {sig_schol_html}
            {evidence_html}
            {src_docs_html}
            {src_pages_html}
            {source_html}
            {scholars_html}
            {links_section}
            {provenance_html}
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
                <p>Each card below represents a folio of the <em>Hypnerotomachia
                Poliphili</em> where marginal annotations have been documented in
                James Russell's PhD thesis. Folios are identified by their
                <strong>signature</strong>&mdash;a bibliographic notation combining
                a quire letter, leaf number, and side (<em>r</em> for recto,
                <em>v</em> for verso). For example, <em>b6v</em> is the verso of
                the sixth leaf in quire <em>b</em>.</p>
                <p>Folios tagged <span class="alchemist-tag" style="font-size:0.65rem">Alch.</span>
                contain annotations by one of two identified alchemist readers:
                Hand B in the British Library copy (a follower of d'Espagnet's
                mercury-centered framework) or Hand E in the Buffalo copy
                (a follower of pseudo-Geber's sulphur and Sol/Luna emphasis).</p>
                <p>{len(by_sig)} annotated folios from {len(set(r[5] for rows in by_sig.values() for r in rows))} manuscript copies.</p>
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
                <p>This bibliography tracks editions, translations, and scholarship
                on the <em>Hypnerotomachia Poliphili</em> from the first studies in
                the 1890s through contemporary work in narratology, botanical
                analysis, and reception history. It draws on the 310-entry
                bibliography of James Russell's PhD thesis (Durham, 2014),
                the <em>Word &amp; Image</em> special issues (1998, 2015),
                and ongoing web research.</p>
                <p>Entries are grouped by relevance: <strong>Primary Sources</strong>
                (editions and translations of the HP itself), <strong>Direct
                Scholarship</strong> (works whose primary subject is the HP),
                <strong>Related Studies</strong> (works that engage substantially
                with the HP as part of a broader argument), and <strong>General
                References</strong> (methodological or contextual works cited
                in HP scholarship). Each entry shows whether we hold the work
                in our collection and whether the citation has been verified.</p>
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
                The <em>Hypnerotomachia Poliphili</em>, published by Aldus Manutius
                in Venice in 1499, is among the most celebrated and least understood
                books of the Italian Renaissance. Written in a macaronic blend of
                Italian, Latin, Greek, and pseudo-hieroglyphs, and illustrated with
                172 woodcuts of extraordinary refinement, it tells the story of
                Poliphilo's dream-journey through ruined temples, enchanted gardens,
                and allegorical processions in pursuit of his beloved Polia.
                </p><p>
                This project documents the <em>readership</em> of the HP &mdash; not just
                the text itself, but what five centuries of readers did with it.
                James Russell's PhD thesis (Durham, 2014) conducted a world census
                of annotated copies, finding that readers as diverse as Ben Jonson,
                Pope Alexander VII, Benedetto Giovio, and anonymous alchemists left
                extensive marginalia recording their encounters with the text.
                This site presents Russell's findings alongside photographs of two
                annotated copies, a bibliography of HP scholarship, a dictionary of
                essential terminology, and the full documentation of how the platform
                was built.
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
    'migrate_dictionary_v2.py': ('Dictionary Schema V2', 'Extends dictionary_terms with significance, source tracking, provenance, and confidence columns.'),
    'corpus_search.py': ('Corpus Search', 'Keyword-based search across markdown chunks and documents with provenance tracking.'),
    'dictionary_audit.py': ('Dictionary Audit', 'Audits dictionary coverage: missing fields, duplicate slugs, orphaned links, weak terms.'),
    'build_reading_packets.py': ('Build Reading Packets', 'Assembles structured research packets from corpus search for dictionary enrichment.'),
    'enrich_dictionary.py': ('Enrich Dictionary', 'Populates dictionary fields from reading packets with source provenance and review status.'),
    'build_essay_data.py': ('Build Essay Data', 'Extracts structured evidence from DB and corpus for the Russell and Concordance essays.'),
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
                <p>This project was built in public, and these {len(docs)} documents
                record how and why each decision was made. They include the
                concordance methodology that links Russell's folio references
                to manuscript photographs, boundary audits distinguishing
                deterministic processing from LLM-assisted inference, a
                reverse-engineering of the MIT Electronic Hypnerotomachia,
                a multimodal architecture study, content quality proposals,
                and a frank accounting of mistakes made along the way.</p>
                <p>Publishing these documents is itself a design choice: a
                scholarly platform should show its working, not just its
                conclusions.</p>
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
                <p>Every page on this site is generated from a SQLite database by
                these {len(scripts)} Python scripts. The database is the source of
                truth; the scripts are a deterministic pipeline that transforms
                structured data into static HTML. No web framework is involved.
                The entire site can be rebuilt from scratch with three commands.</p>
                <p>Scripts are organized by function: schema initialization,
                image cataloging, signature mapping, reference extraction,
                image-reference matching, annotator profiling, bibliography
                management, dictionary seeding, site generation, and validation.
                Each script's full source is published here for transparency
                and reproducibility.</p>
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
# Essay: Russell's Alchemical Hands
# ============================================================

def build_russell_essay_page(conn):
    """Generate russell-alchemical-hands.html from DB evidence + corpus data."""
    cur = conn.cursor()

    # Get alchemist hands
    cur.execute("""
        SELECT hand_label, manuscript_shelfmark, attribution, school,
               description, language, ink_color, date_range, interests
        FROM annotator_hands WHERE is_alchemist = 1
    """)
    alchemist_hands = cur.fetchall()

    # Get alchemist refs with signatures
    cur.execute("""
        SELECT r.signature_ref, r.thesis_page, r.context_text, r.marginal_text,
               r.chapter_num, r.manuscript_shelfmark, h.hand_label, h.school
        FROM dissertation_refs r
        JOIN annotator_hands h ON r.hand_id = h.id
        WHERE h.is_alchemist = 1
        ORDER BY r.thesis_page
    """)
    alch_refs = cur.fetchall()

    # Count matched images for alchemist refs
    cur.execute("""
        SELECT mat.confidence, COUNT(*)
        FROM matches mat
        JOIN dissertation_refs r ON mat.ref_id = r.id
        JOIN annotator_hands h ON r.hand_id = h.id
        WHERE h.is_alchemist = 1
        GROUP BY mat.confidence
    """)
    conf_dist = {row[0]: row[1] for row in cur.fetchall()}

    # Get specific BL refs
    bl_refs = [r for r in alch_refs if r[5] == 'C.60.o.12']
    buf_refs = [r for r in alch_refs if r[5] == 'Buffalo RBR']

    # Build BL refs table
    bl_rows = ''
    for r in bl_refs[:20]:
        marginal = escape(r[3] or '') if r[3] else '<em>none recorded</em>'
        bl_rows += f'<tr><td>{escape(r[0] or "")}</td><td>{r[1]}</td><td>{marginal}</td></tr>'

    buf_rows = ''
    for r in buf_refs[:20]:
        marginal = escape(r[3] or '') if r[3] else '<em>none recorded</em>'
        buf_rows += f'<tr><td>{escape(r[0] or "")}</td><td>{r[1]}</td><td>{marginal}</td></tr>'

    essay_css = '<style>' + """
        .essay-page { max-width: 850px; margin: 2rem auto; padding: 0 2rem; }
        .essay-page h2 { color: var(--accent); margin: 2rem 0 0.5rem; border-bottom: 1px solid var(--border); padding-bottom: 0.3rem; }
        .essay-page h3 { margin: 1.5rem 0 0.5rem; }
        .essay-page p { line-height: 1.8; margin-bottom: 1rem; }
        .essay-page .provisional { background: #fff3cd; padding: 0.5rem 1rem; border-left: 3px solid #ffc107; margin: 1rem 0; font-size: 0.9rem; }
        .essay-page .evidence-note { background: var(--bg-card); padding: 0.5rem 1rem; border-left: 3px solid var(--accent); margin: 1rem 0; font-size: 0.85rem; color: var(--text-muted); }
        .essay-page table { width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.85rem; }
        .essay-page th, .essay-page td { padding: 0.5rem 0.75rem; border: 1px solid var(--border); text-align: left; }
        .essay-page th { background: var(--bg); font-weight: 600; }
        .essay-page blockquote { border-left: 3px solid var(--accent-light); padding-left: 1rem; color: var(--text-muted); font-style: italic; margin: 1rem 0; }
        .essay-page .section-anchor { color: var(--text-muted); text-decoration: none; font-size: 0.8em; margin-left: 0.3rem; }
        .essay-page .cross-links { margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--border); }
        .essay-page .cross-links a { display: inline-block; margin: 0.2rem 0.3rem; padding: 0.2rem 0.6rem; background: var(--bg); border: 1px solid var(--border); border-radius: 3px; font-size: 0.85rem; color: var(--text); text-decoration: none; }
        .essay-page .cross-links a:hover { border-color: var(--accent); color: var(--accent); }
    """ + '</style>'

    body = f"""
    <div class="essay-page">
        <p><a href="index.html">&larr; Home</a></p>

        <h1>Russell's Research on the Alchemical Hands</h1>
        <p class="evidence-note">This essay synthesizes evidence from James Russell's PhD thesis
        (Durham, 2014) and data extracted by this project's concordance pipeline. All claims about
        specific folios and images are grounded in retrieved dissertation references and matched
        image data. Where claims depend on provisional BL concordance data, this is marked explicitly.</p>

        <h2 id="overview">Overview of the Dissertation Project
            <a class="section-anchor" href="#overview">#</a></h2>
        <p>Russell's thesis, submitted to Durham University in 2014, documented the marginalia in six
        copies of the 1499 <em>Hypnerotomachia Poliphili</em>, identifying {len(alchemist_hands) + 9}
        distinct annotator hands across these copies. His work demonstrated that the HP was actively
        read and annotated by humanists, playwrights, a pope, and alchemists over roughly two centuries
        (1499&ndash;1700). The thesis framed the annotated HP as a "humanistic activity book" in which
        readers cultivated <em>ingegno</em> through creative engagement with the text and its woodcuts.</p>

        <h2 id="annotated-copies">Annotated Copies Relevant to the Alchemical Interpretation
            <a class="section-anchor" href="#annotated-copies">#</a></h2>
        <p>Two of the six copies studied by Russell contain alchemical annotations:</p>
        <ul>
            <li><strong>British Library, C.60.o.12</strong> (the "BL copy"): Contains two hands.
            Hand A is attributed to Ben Jonson. Hand B is an anonymous alchemist, possibly connected
            to the Royal Society circle, following the framework of Jean d'Espagnet.</li>
            <li><strong>Buffalo Rare Book Room</strong> (the "Buffalo copy"): Contains five interleaved
            hands (A&ndash;E). Hand E is an anonymous alchemist following the pseudo-Geber (Jabir ibn Hayyan)
            school, emphasizing sulphur and Sol/Luna pairings.</li>
        </ul>

        <h2 id="bl-alchemist">The BL Alchemical Hand (Hand B)
            <a class="section-anchor" href="#bl-alchemist">#</a></h2>
        <p>The BL alchemist (Hand B in C.60.o.12) is the more extensively documented of the two alchemical
        readers. Russell devotes Chapter 6 of his thesis primarily to this hand. On the flyleaf verso,
        Hand B wrote a Latin summary of the HP's perceived true meaning:</p>
        <blockquote>"verus sensus intentionis huius libri est 3um: Geni et Totius Naturae energiae
        &amp; operationum Magisteri Mercurii Descriptio elegans, ampla"</blockquote>
        <p>This annotation declares the HP's "true sense" to be the "full and elegant description of
        the energy and spirit of the whole nature, and of the operations of Master Mercury." This
        reading positions mercury (quicksilver) as the catalytic principle uniting all elements,
        consistent with d'Espagnet's <em>Enchiridion Physicae Restitutae</em> (published 1623).</p>
        <p>Hand B used an extensive vocabulary of alchemical ideograms&mdash;compact symbols for gold,
        silver, mercury, Venus, Jupiter, and other elements&mdash;within the syntax of Latin annotations.
        These signs sometimes had Latin inflections appended (e.g., the sun symbol + "-ra" for "aurata").
        Russell notes that B's ideographic vocabulary shows consistency with Newton's Keynes MSS,
        suggesting a possible connection to the Royal Society or Cambridge circle.</p>
        <p class="evidence-note">Source: Russell 2014, Ch. 6, pp. 154&ndash;168. This project has
        {len(bl_refs)} dissertation references attributed to Hand B in our database.</p>

        <h3>BL Alchemist: Referenced Folios</h3>
        <table>
            <thead><tr><th>Signature</th><th>Thesis Page</th><th>Marginal Text</th></tr></thead>
            <tbody>{bl_rows}</tbody>
        </table>
        <div class="provisional">Note: All BL image matches in this project are classified as LOW
        confidence because the BL photographs are sequentially numbered rather than labeled by folio.
        The BL copy is the 1545 edition; the signature map is based on the 1499 collation.
        Manual verification is required before these matches can be trusted.</div>

        <h2 id="buffalo-alchemist">The Buffalo Alchemical Hand (Hand E)
            <a class="section-anchor" href="#buffalo-alchemist">#</a></h2>
        <p>Hand E in the Buffalo copy is the latest of five interleaved hands, overwriting Hand D.
        Like the BL alchemist, Hand E labels passages and woodcuts with the element or stage of
        the alchemical process they were presumed to allegorize. However, Hand E follows a different
        alchemical school: the pseudo-Geber tradition, emphasizing sulphur and the Sol/Luna (Sun/Moon)
        duality rather than d'Espagnet's mercury-centered framework.</p>
        <p>Hand E identified the king and queen statues in the HP as Sol and Luna, and read the
        chess match passage (h1r) as an allegory of silver/gold transmutation. The chemical
        wedding&mdash;the union of Sol and Luna&mdash;maps onto Poliphilo and Polia's love story
        in this reading.</p>
        <p class="evidence-note">Source: Russell 2014, Ch. 7, pp. 170&ndash;191. This project has
        {len(buf_refs)} dissertation references attributed to Hand E.</p>

        <h3>Buffalo Alchemist: Referenced Folios</h3>
        <table>
            <thead><tr><th>Signature</th><th>Thesis Page</th><th>Marginal Text</th></tr></thead>
            <tbody>{buf_rows}</tbody>
        </table>

        <h2 id="differences">Differences in Notation, Language, and Interpretive Logic
            <a class="section-anchor" href="#differences">#</a></h2>
        <table>
            <thead><tr><th>Feature</th><th>BL Hand B</th><th>Buffalo Hand E</th></tr></thead>
            <tbody>
                <tr><td>Alchemical School</td><td>d'Espagnet (mercury-centered)</td><td>pseudo-Geber (sulphur / Sol-Luna)</td></tr>
                <tr><td>Language</td><td>Latin with alchemical ideograms</td><td>Latin and Italian, fewer ideograms</td></tr>
                <tr><td>Central Principle</td><td>Master Mercury as catalytic agent</td><td>Sol/Luna duality and chemical wedding</td></tr>
                <tr><td>Key Passage</td><td>Flyleaf verso (Master Mercury declaration)</td><td>h1r (chess match as transmutation)</td></tr>
                <tr><td>Notation Style</td><td>Extensive ideographic vocabulary</td><td>Minimal ideograms; more discursive</td></tr>
                <tr><td>Approximate Date</td><td>Late 17th century (post-1623)</td><td>Unknown (latest of five hands)</td></tr>
            </tbody>
        </table>

        <h2 id="images">What Images We Currently Have
            <a class="section-anchor" href="#images">#</a></h2>
        <p>This project has matched {sum(conf_dist.values())} images to alchemist-attributed
        dissertation references. The confidence distribution is:</p>
        <ul>
            <li>HIGH confidence: {conf_dist.get('HIGH', 0)} matches</li>
            <li>MEDIUM confidence: {conf_dist.get('MEDIUM', 0)} matches</li>
            <li>LOW confidence: {conf_dist.get('LOW', 0)} matches</li>
        </ul>
        <div class="provisional">The majority of BL matches are LOW confidence because the BL
        photograph numbering does not directly encode folio information. These matches should be
        treated as provisional until verified against the physical photographs.</div>

        <h2 id="secure-vs-provisional">What Is Secure vs. Provisional
            <a class="section-anchor" href="#secure-vs-provisional">#</a></h2>
        <p><strong>Secure:</strong></p>
        <ul>
            <li>The existence and general character of two alchemical annotators (BL Hand B and Buffalo Hand E)</li>
            <li>The alchemical schools they followed (d'Espagnet vs. pseudo-Geber)</li>
            <li>The Master Mercury declaration on the BL flyleaf</li>
            <li>The folio signatures referenced by Russell in his thesis</li>
            <li>The signature map for the 1499 edition</li>
        </ul>
        <p><strong>Provisional:</strong></p>
        <ul>
            <li>All BL photograph-to-folio matches (LOW confidence)</li>
            <li>The attribution of Hand B to the Royal Society circle</li>
            <li>The precise dating of Hand E relative to the other Buffalo hands</li>
            <li>Any specific image claimed to show a particular alchemical annotation</li>
        </ul>

        <h2 id="reception">Why the Alchemical Readers Matter for HP Reception History
            <a class="section-anchor" href="#reception">#</a></h2>
        <p>The alchemical annotations demonstrate that the HP's readership extended well beyond
        antiquarian humanists and poets. The two alchemist annotators independently decoded the
        HP as concealing alchemical formulae beneath its love narrative&mdash;yet they arrived
        at fundamentally different readings because they operated within different alchemical
        traditions. This diversity illustrates Russell's broader argument that the HP functioned
        as a "humanistic activity book": a text whose deliberate obscurity invited readers to
        impose their own interpretive frameworks.</p>
        <p>The alchemical tradition of reading the HP stretches back to Beroalde de Verville's
        1600 French edition, which included a "tableau steganographique" listing alchemical
        equivalents for the narrative's symbols. The BL and Buffalo annotations show that this
        tradition persisted into the seventeenth century and took distinct forms depending on
        the alchemical school of the reader.</p>

        <div class="cross-links">
            <h4>Related Pages</h4>
            <a href="dictionary/alchemical-allegory.html">Alchemical Allegory</a>
            <a href="dictionary/master-mercury.html">Master Mercury</a>
            <a href="dictionary/sol-luna.html">Sol and Luna</a>
            <a href="dictionary/chemical-wedding.html">Chemical Wedding</a>
            <a href="dictionary/ideogram.html">Ideogram</a>
            <a href="dictionary/annotator-hand.html">Annotator Hand</a>
            <a href="dictionary/activity-book.html">Activity Book</a>
            <a href="dictionary/prisca-sapientia.html">Prisca Sapientia</a>
            <a href="dictionary/ingegno.html">Ingegno</a>
            <a href="concordance-method.html">Concordance Methodology</a>
        </div>
    </div>"""

    page = page_shell("Russell's Alchemical Hands", body, active_nav='russell',
                       extra_css=essay_css)
    (SITE_DIR / 'russell-alchemical-hands.html').write_text(page, encoding='utf-8')
    print("  russell-alchemical-hands.html")


# ============================================================
# Essay: Concordance Methodology
# ============================================================

def build_concordance_essay_page(conn):
    """Generate concordance-method.html explaining the matching pipeline."""
    cur = conn.cursor()

    # Gather stats
    cur.execute("SELECT COUNT(*) FROM signature_map")
    sig_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM dissertation_refs")
    ref_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM images")
    img_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM matches")
    match_count = cur.fetchone()[0]

    cur.execute("SELECT confidence, COUNT(*) FROM matches GROUP BY confidence")
    conf_dist = {row[0]: row[1] for row in cur.fetchall()}

    cur.execute("SELECT match_method, COUNT(*) FROM matches GROUP BY match_method")
    method_dist = {row[0]: row[1] for row in cur.fetchall()}

    cur.execute("""
        SELECT m.shelfmark, mat.confidence, COUNT(*)
        FROM matches mat
        JOIN images i ON mat.image_id = i.id
        JOIN manuscripts m ON i.manuscript_id = m.id
        GROUP BY m.shelfmark, mat.confidence
    """)
    ms_conf = {}
    for row in cur.fetchall():
        ms_conf.setdefault(row[0], {})[row[1]] = row[2]

    siena_data = ms_conf.get('O.III.38', {})
    bl_data = ms_conf.get('C.60.o.12', {})

    cur.execute("""
        SELECT m.shelfmark, COUNT(DISTINCT i.id) FROM images i
        JOIN manuscripts m ON i.manuscript_id = m.id
        GROUP BY m.shelfmark
    """)
    img_by_ms = {row[0]: row[1] for row in cur.fetchall()}

    cur.execute("""
        SELECT manuscript_shelfmark, COUNT(*) FROM dissertation_refs
        WHERE manuscript_shelfmark IS NOT NULL
        GROUP BY manuscript_shelfmark ORDER BY COUNT(*) DESC
    """)
    ref_by_ms = {row[0]: row[1] for row in cur.fetchall()}

    essay_css = '<style>' + """
        .essay-page { max-width: 850px; margin: 2rem auto; padding: 0 2rem; }
        .essay-page h2 { color: var(--accent); margin: 2rem 0 0.5rem; border-bottom: 1px solid var(--border); padding-bottom: 0.3rem; }
        .essay-page h3 { margin: 1.5rem 0 0.5rem; }
        .essay-page p { line-height: 1.8; margin-bottom: 1rem; }
        .essay-page .provisional { background: #fff3cd; padding: 0.5rem 1rem; border-left: 3px solid #ffc107; margin: 1rem 0; font-size: 0.9rem; }
        .essay-page .evidence-note { background: var(--bg-card); padding: 0.5rem 1rem; border-left: 3px solid var(--accent); margin: 1rem 0; font-size: 0.85rem; color: var(--text-muted); }
        .essay-page table { width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.85rem; }
        .essay-page th, .essay-page td { padding: 0.5rem 0.75rem; border: 1px solid var(--border); text-align: left; }
        .essay-page th { background: var(--bg); font-weight: 600; }
        .essay-page .process-flow {{ display: flex; flex-wrap: wrap; gap: 1rem; margin: 1.5rem 0; }}
        .essay-page .process-step {{ flex: 1; min-width: 200px; padding: 1rem; background: var(--bg-card); border: 1px solid var(--border); border-radius: 4px; }}
        .essay-page .process-step .step-num {{ display: inline-block; width: 1.5rem; height: 1.5rem; background: var(--accent); color: white; border-radius: 50%; text-align: center; line-height: 1.5rem; font-size: 0.8rem; margin-right: 0.3rem; }}
        .essay-page .process-step h4 {{ margin: 0 0 0.5rem 0; font-size: 0.9rem; }}
        .essay-page .process-step p {{ font-size: 0.85rem; margin: 0; line-height: 1.5; }}
        .essay-page .section-anchor { color: var(--text-muted); text-decoration: none; font-size: 0.8em; margin-left: 0.3rem; }
        .essay-page .cross-links { margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--border); }
        .essay-page .cross-links a { display: inline-block; margin: 0.2rem 0.3rem; padding: 0.2rem 0.6rem; background: var(--bg); border: 1px solid var(--border); border-radius: 3px; font-size: 0.85rem; color: var(--text); text-decoration: none; }
        .essay-page .cross-links a:hover { border-color: var(--accent); color: var(--accent); }
    """ + '</style>'

    body = f"""
    <div class="essay-page">
        <p><a href="index.html">&larr; Home</a></p>

        <h1>Concordance Methodology</h1>
        <p class="evidence-note">This page documents the actual methods used to build the concordance
        between Russell's dissertation references and the manuscript photograph collections. All
        statistics are drawn from the project database. Uncertainty and provisional status are
        marked explicitly throughout.</p>

        <h2 id="problem">The Problem Russell Presents
            <a class="section-anchor" href="#problem">#</a></h2>
        <p>Russell's thesis references folios by signature (e.g., "b6v", "h1r") rather than by
        page number, since the 1499 edition has no printed pagination. Our manuscript photograph
        collections, however, use different naming conventions: the Siena images use folio numbers
        with recto/verso suffixes (e.g., O.III.38_0014r.jpg), while the BL images use sequential
        numbers (C_60_o_12-001.jpg through C_60_o_12-196.jpg). The core challenge is mapping
        Russell's {ref_count} signature-based references to the {img_count} available photographs.</p>

        <h2 id="image-sets">BL vs. Siena Image Sets
            <a class="section-anchor" href="#image-sets">#</a></h2>
        <table>
            <thead><tr><th>Property</th><th>Siena O.III.38</th><th>BL C.60.o.12</th></tr></thead>
            <tbody>
                <tr><td>Images</td><td>{img_by_ms.get('O.III.38', 0)}</td><td>{img_by_ms.get('C.60.o.12', 0)}</td></tr>
                <tr><td>Naming</td><td>Folio number + r/v suffix</td><td>Sequential number only</td></tr>
                <tr><td>Edition</td><td>1499 Aldine</td><td>1545 Aldine (second edition)</td></tr>
                <tr><td>Folio mapping</td><td>Directly encoded in filename</td><td>Requires inference</td></tr>
                <tr><td>Matching confidence</td><td>HIGH / MEDIUM</td><td>LOW (all provisional)</td></tr>
            </tbody>
        </table>
        <div class="provisional">The BL copy is the 1545 edition, not the 1499. The signature map
        is based on the 1499 collation formula. While the 1545 edition largely follows the same
        structure, any pagination differences between editions would make sequential-number-to-folio
        inference unreliable. All BL matches must be treated as provisional.</div>

        <h2 id="signature-map">How the Signature Map Works
            <a class="section-anchor" href="#signature-map">#</a></h2>
        <p>The signature map is a deterministic lookup table of {sig_count} entries generated from
        the 1499 collation formula: a&ndash;z<sup>8</sup> (omitting j, u, w), A&ndash;F<sup>8</sup>,
        G<sup>4</sup>. Each quire has 8 leaves (except G with 4), and each leaf has recto and verso
        sides. The map converts any valid signature (e.g., "b6v") to a sequential folio number
        and vice versa.</p>
        <p>This map is generated by <code>build_signature_map.py</code> and is fully deterministic.
        It is correct for the 1499 edition. Its applicability to the 1545 edition is assumed but
        not verified.</p>

        <h2 id="ref-extraction">How Dissertation References Were Extracted
            <a class="section-anchor" href="#ref-extraction">#</a></h2>
        <p>Russell's thesis PDF was processed by <code>extract_references.py</code> using PyMuPDF
        for text extraction and regular expressions for signature pattern matching. The script
        extracted {ref_count} references, distributed across manuscripts:</p>
        <table>
            <thead><tr><th>Manuscript</th><th>References</th></tr></thead>
            <tbody>{''.join(f"<tr><td>{escape(k)}</td><td>{v}</td></tr>" for k, v in sorted(ref_by_ms.items(), key=lambda x: -x[1]))}</tbody>
        </table>

        <h2 id="image-parsing">How Image Filenames Were Parsed
            <a class="section-anchor" href="#image-parsing">#</a></h2>
        <p><code>catalog_images.py</code> parses image filenames from two manuscript collections into
        structured records with folio number, side (recto/verso), and page type. The Siena images
        encode folio information directly (O.III.38_0014r.jpg = folio 14 recto). The BL images
        use sequential numbers that do not directly encode folio information.</p>

        <h2 id="matching">How Matching Was Performed
            <a class="section-anchor" href="#matching">#</a></h2>
        <div class="process-flow">
            <div class="process-step">
                <h4><span class="step-num">1</span> Signature Lookup</h4>
                <p>Convert each dissertation reference's signature (e.g., "b6v") to a folio number
                using the signature map.</p>
            </div>
            <div class="process-step">
                <h4><span class="step-num">2</span> Manuscript Filter</h4>
                <p>Filter images to the manuscript shelfmark specified in the dissertation reference.</p>
            </div>
            <div class="process-step">
                <h4><span class="step-num">3</span> Folio Match</h4>
                <p>Match the computed folio number to images with the same folio number and side.</p>
            </div>
            <div class="process-step">
                <h4><span class="step-num">4</span> Fallback Cross-Match</h4>
                <p>If no direct match, attempt cross-manuscript matching (lower confidence).</p>
            </div>
            <div class="process-step">
                <h4><span class="step-num">5</span> Confidence Assignment</h4>
                <p>Assign HIGH (exact Siena match), MEDIUM (folio-based), or LOW (BL sequential inference).</p>
            </div>
        </div>

        <h2 id="confidence">Where Confidence Is High vs. Low
            <a class="section-anchor" href="#confidence">#</a></h2>
        <table>
            <thead><tr><th>Confidence</th><th>Matches</th><th>Description</th></tr></thead>
            <tbody>
                <tr><td>HIGH</td><td>{conf_dist.get('HIGH', 0)}</td><td>Siena images with explicit folio+side in filename, matched by signature lookup</td></tr>
                <tr><td>MEDIUM</td><td>{conf_dist.get('MEDIUM', 0)}</td><td>Siena images matched by folio number (cross-manuscript or side ambiguous)</td></tr>
                <tr><td>LOW</td><td>{conf_dist.get('LOW', 0)}</td><td>BL images where sequential photo number is assumed to equal folio number</td></tr>
            </tbody>
        </table>

        <h3>By Manuscript</h3>
        <table>
            <thead><tr><th>Manuscript</th><th>HIGH</th><th>MEDIUM</th><th>LOW</th></tr></thead>
            <tbody>
                <tr><td>Siena O.III.38</td><td>{siena_data.get('HIGH', 0)}</td><td>{siena_data.get('MEDIUM', 0)}</td><td>{siena_data.get('LOW', 0)}</td></tr>
                <tr><td>BL C.60.o.12</td><td>{bl_data.get('HIGH', 0)}</td><td>{bl_data.get('MEDIUM', 0)}</td><td>{bl_data.get('LOW', 0)}</td></tr>
            </tbody>
        </table>

        <h2 id="bl-provisional">Why BL Matches Are Provisional
            <a class="section-anchor" href="#bl-provisional">#</a></h2>
        <div class="provisional"><strong>Critical caveat:</strong> All {sum(bl_data.values())} BL matches
        are classified as LOW confidence. The BL photographs are sequentially numbered (001&ndash;196)
        without folio labels. Our matching pipeline assumes that photo N corresponds to folio N, but
        this assumption is unverified. The BL copy is the 1545 edition, not the 1499 edition from which
        the signature map was built. Any differences in pagination, inserted leaves, or missing leaves
        between editions would invalidate this mapping. These matches require manual verification
        against the physical photographs.</div>

        <h2 id="human-review">What Human Review Is Still Needed
            <a class="section-anchor" href="#human-review">#</a></h2>
        <ul>
            <li>Verify BL photograph-to-folio correspondence against physical or high-resolution images</li>
            <li>Confirm that the 1545 edition follows the same collation as the 1499</li>
            <li>Spot-check MEDIUM confidence Siena matches for side (recto/verso) accuracy</li>
            <li>Review hand attribution for edge cases where multiple hands annotate the same folio</li>
            <li>Validate marginal text transcriptions against original manuscript images</li>
        </ul>

        <h2 id="future">How This Methodology Supports Future Scholarship
            <a class="section-anchor" href="#future">#</a></h2>
        <p>The concordance pipeline produces a structured, queryable dataset linking Russell's
        close reading to digital images. Once the BL matches are verified, this enables:</p>
        <ul>
            <li>Folio-level browsing of annotations alongside manuscript images</li>
            <li>Systematic comparison of annotation density across copies</li>
            <li>Identification of folios that attracted multiple annotators</li>
            <li>Cross-referencing between annotations and the dictionary of terms</li>
            <li>Future multimodal analysis using computer vision on manuscript images</li>
        </ul>

        <div class="cross-links">
            <h4>Related Pages</h4>
            <a href="dictionary/signature.html">Signature</a>
            <a href="dictionary/folio.html">Folio</a>
            <a href="dictionary/collation.html">Collation</a>
            <a href="dictionary/annotator-hand.html">Annotator Hand</a>
            <a href="dictionary/marginalia.html">Marginalia</a>
            <a href="russell-alchemical-hands.html">Alchemical Hands Essay</a>
            <a href="docs/concordance-methodology.html">Concordance Methodology (Doc)</a>
            <a href="code/match-refs-to-images.html">match_refs_to_images.py</a>
            <a href="code/build-signature-map.html">build_signature_map.py</a>
        </div>
    </div>"""

    page = page_shell('Concordance Methodology', body, active_nav='concordance',
                       extra_css=essay_css)
    (SITE_DIR / 'concordance-method.html').write_text(page, encoding='utf-8')
    print("  concordance-method.html")


# ============================================================
# Digital Edition stub page
# ============================================================

def build_digital_edition_page(conn):
    """Generate digital-edition.html as an honest editorial prospectus."""
    cur = conn.cursor()

    # Gather current state stats
    cur.execute("SELECT COUNT(*) FROM dictionary_terms")
    dict_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM bibliography")
    bib_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM scholars")
    scholar_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM matches")
    match_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM images")
    img_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM signature_map")
    sig_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM annotator_hands")
    hand_count = cur.fetchone()[0]

    edition_css = '<style>' + """
        .edition-page { max-width: 850px; margin: 2rem auto; padding: 0 2rem; }
        .edition-page h2 { color: var(--accent); margin: 2rem 0 0.5rem; border-bottom: 1px solid var(--border); padding-bottom: 0.3rem; }
        .edition-page h3 { margin: 1.5rem 0 0.5rem; }
        .edition-page p { line-height: 1.8; margin-bottom: 1rem; }
        .edition-page .status-grid { display: grid; grid-template-columns: auto 1fr; gap: 0.5rem 1.5rem; margin: 1rem 0; font-size: 0.9rem; }
        .edition-page .status-icon { font-weight: bold; }
        .edition-page .status-done { color: #155724; }
        .edition-page .status-partial { color: #856404; }
        .edition-page .status-planned { color: var(--text-muted); }
        .edition-page .status-blocked { color: #721c24; }
        .edition-page .roadmap-phase { margin: 1rem 0; padding: 1rem; background: var(--bg-card); border: 1px solid var(--border); border-radius: 4px; }
        .edition-page .roadmap-phase h4 { margin: 0 0 0.5rem 0; }
        .edition-page .roadmap-phase p { margin: 0; font-size: 0.9rem; }
        .edition-page .evidence-note { background: var(--bg-card); padding: 0.5rem 1rem; border-left: 3px solid var(--accent); margin: 1rem 0; font-size: 0.85rem; color: var(--text-muted); }
    """ + '</style>'

    body = f"""
    <div class="edition-page">
        <p><a href="index.html">&larr; Home</a></p>

        <h1>Digital Edition: Editorial Prospectus</h1>
        <p class="evidence-note">This page describes the vision, current state, and roadmap for a
        comprehensive digital edition of the <em>Hypnerotomachia Poliphili</em>. It is not a
        finished edition. It is a statement of intent, a map of what exists, and an honest
        accounting of what remains to be built.</p>

        <h2 id="vision">What This Edition Will Include</h2>
        <p>The eventual digital edition aims to provide:</p>
        <ul>
            <li><strong>Facsimile browsing:</strong> Page-by-page viewing of manuscript photographs
            from multiple copies, with folio-level navigation via the signature map.</li>
            <li><strong>Transcription:</strong> Diplomatic transcription of the 1499 text, linked
            to facsimile images at the folio level.</li>
            <li><strong>Translation witnesses:</strong> Parallel display of the 1499 Italian,
            Godwin's 1999 English translation, and the 1546 French adaptation.</li>
            <li><strong>Folio-level commentary:</strong> Annotation layers showing marginalia
            transcriptions, hand attributions, and interpretive notes.</li>
            <li><strong>Marginalia overlays:</strong> Visual overlays highlighting annotated
            passages on manuscript images, linked to the commentary apparatus.</li>
            <li><strong>Dictionary cross-links:</strong> Inline links from edition text to the
            dictionary of HP-specific terminology.</li>
            <li><strong>Bibliography integration:</strong> Citation links from commentary to the
            bibliography, enabling readers to trace scholarly arguments to their sources.</li>
            <li><strong>Copy comparison:</strong> Side-by-side viewing of the same folio across
            different annotated copies, showing how different readers engaged with the same
            passages.</li>
        </ul>

        <h2 id="current-state">What Is Already Built</h2>
        <div class="status-grid">
            <span class="status-icon status-done">[done]</span>
            <span>Signature map ({sig_count} entries, deterministic from 1499 collation)</span>
            <span class="status-icon status-done">[done]</span>
            <span>Image catalog ({img_count} photographs from 2 manuscripts)</span>
            <span class="status-icon status-done">[done]</span>
            <span>Dissertation reference extraction ({match_count} matches)</span>
            <span class="status-icon status-done">[done]</span>
            <span>Hand attribution ({hand_count} annotator hands identified)</span>
            <span class="status-icon status-done">[done]</span>
            <span>Dictionary ({dict_count} terms with corpus evidence)</span>
            <span class="status-icon status-done">[done]</span>
            <span>Bibliography ({bib_count} works) and scholar profiles ({scholar_count})</span>
            <span class="status-icon status-done">[done]</span>
            <span>Marginalia gallery with confidence scoring</span>
            <span class="status-icon status-done">[done]</span>
            <span>Corpus search infrastructure (PDF-to-markdown, chunking, search)</span>
        </div>

        <h2 id="provisional">What Remains Provisional</h2>
        <ul>
            <li>All BL C.60.o.12 image-to-folio matches are LOW confidence (sequential photo numbers
            assumed to equal folio numbers; unverified)</li>
            <li>Scholar summaries and dictionary definitions were generated with LLM assistance and
            are marked DRAFT; they have not been verified by domain experts</li>
            <li>Hand attributions beyond Russell's thesis data are inferred, not verified</li>
            <li>No transcription of the HP text itself exists in this project yet</li>
            <li>No translation texts are integrated</li>
        </ul>

        <h2 id="roadmap">Phased Roadmap</h2>

        <div class="roadmap-phase">
            <h4><span class="status-icon status-partial">[partial]</span> Phase 1: Data Foundation</h4>
            <p>Build the concordance pipeline, image catalog, signature map, and reference extraction.
            <strong>Status:</strong> Complete for Siena; BL matches provisional.</p>
        </div>

        <div class="roadmap-phase">
            <h4><span class="status-icon status-partial">[partial]</span> Phase 2: Scholarly Apparatus</h4>
            <p>Dictionary, bibliography, scholar profiles, hand attribution, corpus search.
            <strong>Status:</strong> Substantially built; entries at DRAFT status pending expert review.</p>
        </div>

        <div class="roadmap-phase">
            <h4><span class="status-icon status-planned">[planned]</span> Phase 3: Image Hosting</h4>
            <p>Host manuscript photographs at sufficient resolution for scholarly use. Requires:
            institutional permission for BL images; storage solution for 674+ high-resolution photographs;
            IIIF-compatible image serving if feasible.</p>
        </div>

        <div class="roadmap-phase">
            <h4><span class="status-icon status-planned">[planned]</span> Phase 4: Transcription</h4>
            <p>Create or integrate a diplomatic transcription of the 1499 text. Could begin with
            OCR of the Da Capo edition, validated against facsimile images. Requires: careful
            handling of the HP's unusual orthography and embedded hieroglyphs.</p>
        </div>

        <div class="roadmap-phase">
            <h4><span class="status-icon status-planned">[planned]</span> Phase 5: Translation Integration</h4>
            <p>Align existing English translation (Godwin 1999) and French adaptation (1546) at
            the folio level. Requires: copyright clearance or use of public-domain translations.</p>
        </div>

        <div class="roadmap-phase">
            <h4><span class="status-icon status-blocked">[blocked]</span> Phase 6: Multimodal Validation</h4>
            <p>Use computer vision to verify BL photograph-to-folio mappings by reading visible
            signature marks in images. Requires: high-resolution images and vision model access.
            See the <a href="docs/multimodal-rag-study.html">Multimodal RAG Study</a> for analysis.</p>
        </div>

        <div class="roadmap-phase">
            <h4><span class="status-icon status-planned">[planned]</span> Phase 7: Commentary &amp; Overlays</h4>
            <p>Build folio-level commentary with marginalia overlays, cross-linked to dictionary
            and bibliography. Requires: verified image matches, transcribed annotations, and
            editorial review infrastructure.</p>
        </div>

        <div class="roadmap-phase">
            <h4><span class="status-icon status-planned">[planned]</span> Phase 8: Copy Comparison</h4>
            <p>Enable side-by-side comparison of the same folio across different annotated copies.
            Requires: all preceding phases substantially complete, plus a viewer capable of
            synchronized scrolling across manuscript images.</p>
        </div>

        <h2 id="limitations">Current Limitations</h2>
        <ul>
            <li>This project has no independent transcription of the HP text</li>
            <li>Manuscript images are stored locally and not hosted for web viewing at scale</li>
            <li>The editorial review process is informal and has no structured workflow</li>
            <li>The 1545/1499 edition difference for the BL copy is unresolved</li>
            <li>No institutional collaboration or peer review is currently in place</li>
        </ul>

        <div class="evidence-note">This prospectus was generated from the project's SQLite database
        and reflects the current state of the data as of the most recent build. It will be updated
        as the project progresses.</div>
    </div>"""

    page = page_shell('Digital Edition', body, active_nav='edition', extra_css=edition_css)
    (SITE_DIR / 'digital-edition.html').write_text(page, encoding='utf-8')
    print("  digital-edition.html")


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

/* ===== Review Status Badges ===== */
.review-status-badge {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 3px;
    font-size: 0.65rem;
    font-weight: 700;
    font-family: var(--font-sans);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    vertical-align: middle;
    margin-left: 0.3rem;
}
.review-badge-draft { background: #fff3cd; color: #856404; }
.review-badge-reviewed { background: #cce5ff; color: #004085; }
.review-badge-verified { background: #d4edda; color: #155724; }
.review-badge-provisional { background: #e2e3e5; color: #383d41; }

/* ===== Dictionary enrichment sections ===== */
.dict-section { margin-top: 1.5rem; }
.dict-section h3 { font-size: 1rem; color: var(--accent); margin-bottom: 0.5rem; border-bottom: 1px solid var(--border); padding-bottom: 0.2rem; }
.dict-section p { line-height: 1.7; }
.evidence-list { font-size: 0.9rem; color: var(--text-muted); line-height: 1.6; }
.evidence-list li { margin-bottom: 0.5rem; }
.source-docs { font-size: 0.85rem; color: var(--text-muted); }
.source-pages { font-size: 0.85rem; color: var(--text-muted); margin-top: 0.5rem; }
.provenance-section { background: var(--bg-card); padding: 1rem; border-radius: 4px; margin-top: 2rem; }
.provenance-status { margin-bottom: 0.5rem; }
.provenance-list { font-size: 0.85rem; color: var(--text-muted); }
.provenance-list li { margin-bottom: 0.3rem; }
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
    build_russell_essay_page(conn)
    build_concordance_essay_page(conn)
    build_digital_edition_page(conn)

    conn.close()
    print("\n=== Build Complete ===")


if __name__ == "__main__":
    main()
