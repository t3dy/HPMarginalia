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
        (f'{prefix}the-book.html', 'The Book', 'thebook'),
        (f'{prefix}timeline.html', 'Timeline', 'timeline'),
        (f'{prefix}woodcuts/index.html', 'Woodcuts', 'woodcuts'),
        (f'{prefix}manuscripts/index.html', 'Manuscripts', 'manuscripts'),
        (f'{prefix}digital-edition.html', 'Editions', 'edition'),
        (f'{prefix}russell-alchemical-hands.html', 'Alchemical Hands', 'russell'),
        (f'{prefix}concordance/index.html', 'Concordance', 'concordance'),
        (f'{prefix}jonson/index.html', 'Ben Jonson', 'jonson'),
        (f'{prefix}digby/index.html', 'Digby', 'digby'),
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
    <title>{escape(title)} - Alchemical Hands in the Hypnerotomachia Poliphili</title>
    <meta name="description" content="Alchemical hands in the marginalia of the Hypnerotomachia Poliphili (Venice, 1499). A digital scholarship platform based on James Russell's PhD thesis.">
    <link rel="stylesheet" href="{prefix}style.css">
    <link rel="stylesheet" href="{prefix}scholars.css">
    <link rel="stylesheet" href="{prefix}components.css">
    {extra_css}
</head>
<body>
    <header>
        <div class="header-content">
            <h1><a href="{prefix}index.html" style="color:inherit;text-decoration:none">Alchemical Hands in the <em>Hypnerotomachia Poliphili</em></a></h1>
            <p class="subtitle">Marginalia, Scholarship &amp; Reception</p>
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
                <p>A digital scholarship platform exploring the alchemical
                annotations and wider marginalia of the 1499 <em>Hypnerotomachia
                Poliphili</em>, based on James Russell's PhD thesis (Durham, 2014).</p>
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
            a.id, a.thesis_page, a.signature_ref, m.shelfmark,
            m.institution, m.city, dr.context_text, a.annotation_text,
            a.thesis_chapter, i.filename, COALESCE(i.web_path, i.relative_path),
            i.folio_number, i.side, mat.confidence,
            sm.quire, sm.leaf_in_quire,
            mat.needs_review as match_needs_review,
            h.hand_label, h.attribution, h.is_alchemist,
            a.annotation_type
        FROM matches mat
        JOIN annotations a ON mat.ref_id = a.id
        JOIN images i ON mat.image_id = i.id
        JOIN manuscripts m ON i.manuscript_id = m.id
        LEFT JOIN dissertation_refs dr ON a.id = dr.id
        LEFT JOIN signature_map sm ON LOWER(a.signature_ref) = LOWER(sm.signature)
        LEFT JOIN annotator_hands h ON a.hand_id = h.id
        WHERE i.page_type = 'PAGE'
        GROUP BY a.signature_ref, i.filename
        ORDER BY COALESCE(sm.folio_number, 999), a.thesis_page
    """)

    # Load folio descriptions for alchemist annotations
    folio_descs = {}
    try:
        cur2 = conn.cursor()
        cur2.execute("""
            SELECT signature_ref, manuscript_shelfmark, hand_label,
                   title, description, alchemical_element, alchemical_process,
                   alchemical_framework, russell_page_ref
            FROM folio_descriptions
        """)
        for fd in cur2.fetchall():
            key = (fd[0], fd[1])
            folio_descs[key] = {
                'desc_title': fd[3], 'desc_text': fd[4],
                'alch_element': fd[5], 'alch_process': fd[6],
                'alch_framework': fd[7], 'russell_pages': fd[8],
            }
    except:
        pass  # Table may not exist yet

    entries = []
    sigs = set()
    for row in cur.fetchall():
        sig = row[2]
        ms = row[3]
        entry = {
            'ref_id': row[0], 'thesis_page': row[1],
            'signature': sig, 'manuscript': ms,
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
            'annotation_type': row[20],
        }
        # Add folio description if available
        fd = folio_descs.get((sig, ms)) or folio_descs.get((sig, None))
        if fd:
            entry['desc_title'] = fd['desc_title']
            entry['desc_text'] = fd['desc_text']
            entry['alch_element'] = fd['alch_element']

        # Generate a brief description for every entry
        parts = []
        if entry.get('desc_title'):
            parts.append(entry['desc_title'] + '.')
        else:
            # Build description from available data
            ms_name = 'the BL copy' if ms == 'C.60.o.12' else 'the Siena copy'
            if entry.get('hand_label') and entry.get('hand_attribution'):
                hand_desc = f"Hand {entry['hand_label']}"
                if entry['hand_attribution'] and entry['hand_attribution'] != 'Anonymous':
                    hand_desc += f" ({entry['hand_attribution']})"
                if entry.get('is_alchemist'):
                    hand_desc += ', an alchemist'
                parts.append(f"Annotated by {hand_desc} in {ms_name}.")
            elif entry.get('hand_label'):
                parts.append(f"Annotated by Hand {entry['hand_label']} in {ms_name}.")
            else:
                parts.append(f"A folio from {ms_name} referenced in Russell's thesis.")

            if entry.get('marginal_text'):
                mt = entry['marginal_text']
                if len(mt) > 5:
                    parts.append(f'Russell records the marginal note: "{mt[:80]}{"..." if len(mt) > 80 else ""}"')

        entry['card_description'] = ' '.join(parts)
        entries.append(entry)
        sigs.add(sig)

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
    """Generate scholars.html and scholar/*.html from DB + summaries.json.

    Uses scholar_overview, is_historical_subject, and scholar_works data
    to build rich profiles per docs/SCHOLAR_SPEC.md.
    """
    # Load summaries for detailed content
    summaries = []
    if SUMMARIES_PATH.exists():
        with open(SUMMARIES_PATH, encoding='utf-8') as f:
            summaries = json.load(f)

    # Index summaries by (author, title) for lookup
    summary_lookup = {}
    for s in summaries:
        key = (s.get('author', ''), s.get('title', ''))
        summary_lookup[key] = s

    # Group summaries by author for backward compat
    by_author_summaries = {}
    for s in summaries:
        author = s.get('author', 'Unknown')
        by_author_summaries.setdefault(author, []).append(s)

    cur = conn.cursor()

    # Get all scholars with overview data
    cur.execute("""
        SELECT id, name, specialization, hp_focus, bio_notes,
               scholar_overview, is_historical_subject,
               needs_review, source_method, review_status
        FROM scholars ORDER BY name
    """)
    all_scholars = cur.fetchall()

    # Get scholar_works with bibliography data
    cur.execute("""
        SELECT sw.scholar_id, b.author, b.title, b.year, b.pub_type,
               b.journal_or_publisher, sw.has_summary, sw.summary_source,
               b.hp_relevance, b.in_collection
        FROM scholar_works sw
        JOIN bibliography b ON sw.bib_id = b.id
        ORDER BY b.year DESC
    """)
    works_by_scholar = {}
    for row in cur.fetchall():
        works_by_scholar.setdefault(row[0], []).append(row)

    scholar_cards = []
    scholar_dir = SITE_DIR / 'scholar'
    scholar_dir.mkdir(exist_ok=True)
    pages_built = 0

    for scholar in all_scholars:
        (sid, name, specialization, hp_focus, bio_notes,
         overview, is_hist, needs_rev, source_method, rev_status) = scholar

        slug = slugify(name)
        works = works_by_scholar.get(sid, [])
        author_summaries = by_author_summaries.get(name, [])

        # Collect topics from summaries
        topics = set()
        for p in author_summaries:
            tc = p.get('topic_cluster', '')
            if tc:
                for t in tc.split(','):
                    topics.add(t.strip())

        badges = topic_badges_html(','.join(topics))
        review_html = review_badge_html(needs_rev, source_method)

        # Historical figure badge
        hist_badge = ' <span class="review-status-badge review-badge-provisional">Historical Figure</span>' if is_hist else ''

        # Overview preview for card (300 chars)
        overview_text = overview or ''
        overview_first_para = overview_text.split('\n\n')[0] if overview_text else ''
        overview_preview = overview_first_para[:300]
        if len(overview_first_para) > 300:
            overview_preview = overview_preview.rsplit(' ', 1)[0] + '...'

        # Work count
        work_count = len(works) or len(author_summaries)
        work_label = f"{work_count} work{'s' if work_count != 1 else ''}" if work_count else "No works catalogued"

        # Card
        overview_card_html = ''
        if overview_preview:
            overview_card_html = f"""
                <div class="scholar-overview-preview">
                    <p>{escape(overview_preview)}
                    <a href="scholar/{slug}.html">Read more</a></p>
                </div>"""

        scholar_cards.append(f"""
        <div class="scholar-card">
            <h3><a href="scholar/{slug}.html">{escape(name)}</a>{hist_badge} {review_html}</h3>
            <div class="scholar-meta">{work_label} {badges}</div>
            {overview_card_html}
        </div>""")

        # === Detail page ===

        # Full overview
        overview_html = ''
        if overview_text:
            paras = overview_text.split('\n\n')
            overview_html = ''.join(f'<p>{escape(p.strip())}</p>' for p in paras if p.strip())
            overview_html = f'<div class="scholar-overview">{overview_html}</div>'

        # Works in archive (with summaries)
        archive_works_html = ''
        works_with_summaries = [w for w in works if w[6]]  # has_summary = True
        if not works_with_summaries and author_summaries:
            # Fallback to summaries.json directly
            for p in author_summaries:
                tc = p.get('topic_cluster', '')
                archive_works_html += f"""
                <div class="paper-detail">
                    <h4>{escape(p.get('title', ''))}</h4>
                    <div class="paper-meta">{escape(p.get('journal', ''))} ({p.get('year', '?')})
                        {topic_badges_html(tc)}</div>
                    <div class="paper-summary-full"><p>{escape(p.get('summary', ''))}</p></div>
                </div>"""
        else:
            for w in works_with_summaries:
                _, bauthor, btitle, byear, bpubtype, bjournal, _, _, _, _ = w
                # Find matching summary
                summary_text = ''
                for s in author_summaries:
                    if s.get('title', '') == btitle:
                        summary_text = s.get('summary', '')
                        break
                tc = ''
                for s in author_summaries:
                    if s.get('title', '') == btitle:
                        tc = s.get('topic_cluster', '')
                        break

                archive_works_html += f"""
                <div class="paper-detail">
                    <h4>{escape(btitle or '')}</h4>
                    <div class="paper-meta">{escape(bjournal or '')} ({byear or '?'}) [{bpubtype or ''}]
                        {topic_badges_html(tc)}</div>
                    <div class="paper-summary-full"><p>{escape(summary_text)}</p></div>
                </div>"""

        # Other known works (without summaries)
        other_works_html = ''
        works_without_summaries = [w for w in works if not w[6]]
        for w in works_without_summaries:
            _, bauthor, btitle, byear, bpubtype, bjournal, _, _, _, _ = w
            other_works_html += f"""
            <div class="paper-detail">
                <h4>{escape(btitle or '')}</h4>
                <div class="paper-meta">{escape(bjournal or '')} ({byear or '?'}) [{bpubtype or ''}]</div>
                <p class="no-summary" style="color:var(--text-muted); font-style:italic; font-size:0.9rem">Summary not yet available.</p>
            </div>"""

        # Build sections
        works_section = ''
        if archive_works_html:
            works_section += f'<h3>Works in Archive</h3>{archive_works_html}'
        if other_works_html:
            works_section += f'<h3>Other Known Works</h3>{other_works_html}'
        if not works_section and not author_summaries:
            works_section = '<p style="color:var(--text-muted)">No works catalogued yet.</p>'

        # Provenance
        provenance_html = f"""
        <div class="provenance-section" style="margin-top:2rem; padding:1rem; background:var(--bg-card); border-radius:4px">
            <h4 style="margin-top:0">Review Status / Provenance</h4>
            <p>{review_status_badge(rev_status or 'DRAFT')} Source: {escape(source_method or 'LLM_ASSISTED')}</p>
        </div>"""

        detail_body = f"""
        <div class="scholar-detail">
            <p><a href="../scholars.html">&larr; All Scholars</a></p>
            <h2>{escape(name)}{hist_badge} {review_html}</h2>
            {overview_html}
            {works_section}
            {provenance_html}
        </div>"""

        detail_page = page_shell(name, detail_body, active_nav='scholars', depth=1)
        (scholar_dir / f'{slug}.html').write_text(detail_page, encoding='utf-8')
        pages_built += 1

    # Build index page
    # Count stats
    modern_count = sum(1 for s in all_scholars if not s[6])
    hist_count = sum(1 for s in all_scholars if s[6])

    index_body = f"""
        <div class="scholars-grid">
            <div class="intro" style="margin-bottom:2rem">
                <h2>Scholars of the <em>Hypnerotomachia</em></h2>
                <p>The scholarship on the <em>Hypnerotomachia Poliphili</em> is wide-ranging
                and interdisciplinary. It spans bibliography, book history, architecture,
                garden studies, allegory, philology, reception history, emblematic reading,
                and the history of interpretation. This section organizes that scholarly
                landscape by person: {modern_count} modern scholars and {hist_count} historical
                figures, with {len(summaries)} article and monograph summaries.</p>
                <p>These pages are meant to make the field legible at a glance.
                Where content is LLM-assisted or otherwise provisional, that status
                remains visible.</p>
            </div>
            {''.join(scholar_cards)}
        </div>"""

    index_page = page_shell('Scholars', index_body, active_nav='scholars')
    (SITE_DIR / 'scholars.html').write_text(index_page, encoding='utf-8')
    print(f"  scholars.html + {pages_built} scholar pages")


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
                <p>The dictionary is the conceptual armature of the site. It defines
                the {len(terms)} terms across {len(by_category)} categories that recur across the
                <em>Hypnerotomachia</em> corpus and its scholarship&mdash;book-historical
                terms, annotation concepts, alchemical vocabulary, architectural and garden
                discourse, textual-visual rhetoric, and major historiographical debates.
                Its purpose is not merely lexical; it is to help readers move between page
                evidence and scholarly interpretation.</p>
                <p>This section is most useful when read alongside the folio pages, essays,
                and bibliography. Terms are cross-linked: each page lists related concepts
                and see-also references, so you can follow threads through the HP's
                intellectual world. Review and provenance badges indicate which entries
                rest on stable ground and which are still in draft.</p>
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

        # Essay cross-links: terms that appear in essays
        essay_links_html = ''
        russell_terms = {
            'alchemical-allegory', 'master-mercury', 'sol-luna', 'chemical-wedding',
            'ideogram', 'annotator-hand', 'activity-book', 'prisca-sapientia',
            'ingegno', 'marginalia', 'elephant-obelisk', 'reception-history',
            'inventio', 'acutezze', 'commentary', 'allegory',
            'poliphilo', 'polia', 'venus-aphrodite', 'cupid-eros',
            'beroalde-1600', '1499-edition', '1545-edition',
        }
        concordance_terms = {
            'signature', 'folio', 'collation', 'quire', 'recto', 'verso',
            'gathering', 'annotator-hand', 'marginalia', 'incunabulum',
            '1499-edition', '1545-edition',
        }
        essay_links = []
        if slug in russell_terms:
            essay_links.append('<a href="../russell-alchemical-hands.html">Alchemical Hands Essay</a>')
        if slug in concordance_terms:
            essay_links.append('<a href="../concordance-method.html">Concordance Methodology</a>')
        if essay_links:
            essay_links_html = f'''
            <div class="related-terms">
                <h4>Discussed In</h4>
                {''.join(essay_links)}
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
            {essay_links_html}
            {provenance_html}
        </div>"""

        term_page = page_shell(label, detail_body, active_nav='dictionary', depth=1)
        (dict_dir / f'{slug}.html').write_text(term_page, encoding='utf-8')

    print(f"  dictionary/index.html + {len(terms)} term pages")


# ============================================================
# Marginalia folio detail pages
# ============================================================

def _render_deep_reading(dr):
    """Render a Phase 3 deep reading JSON object as HTML."""
    parts = []
    parts.append('<h3 style="margin:1.5rem 0 1rem">Vision Reading <span style="font-size:0.7rem;font-weight:400;color:var(--text-muted)">(Phase 3 deep analysis)</span></h3>')

    # Metadata bar
    meta_items = []
    if dr.get('primary_hand'):
        meta_items.append(f'<strong>Primary hand:</strong> {escape(dr["primary_hand"])}')
    if dr.get('hands_detected'):
        meta_items.append(f'<strong>Hands:</strong> {dr["hands_detected"]}')
    if dr.get('page_type'):
        meta_items.append(f'<strong>Type:</strong> {escape(dr["page_type"])}')
    if dr.get('signature'):
        meta_items.append(f'<strong>Sig:</strong> {escape(dr["signature"])}')
    if meta_items:
        parts.append(
            '<div style="font-size:0.85rem;font-family:var(--font-sans);color:var(--text-muted);'
            f'margin-bottom:1rem">{" &middot; ".join(meta_items)}</div>'
        )

    # Woodcut analysis
    wc = dr.get('woodcut_analysis')
    if wc:
        wc_html = f'<div class="marg-annotation" style="border-left:3px solid #6b8e5a">'
        wc_html += f'<h4 style="color:#6b8e5a;margin-bottom:0.5rem">Woodcut: {escape(wc.get("subject", ""))}</h4>'
        if wc.get('description'):
            wc_html += f'<p style="line-height:1.7;margin-bottom:0.5rem">{escape(wc["description"])}</p>'
        if wc.get('inscription_below'):
            wc_html += f'<div class="marginal-text" style="border-color:#6b8e5a">{escape(wc["inscription_below"])}</div>'
        if wc.get('condition'):
            wc_html += f'<div class="hand-info">Condition: {escape(wc["condition"])}</div>'
        wc_html += '</div>'
        parts.append(wc_html)

    # Transcription attempts
    transcriptions = dr.get('transcription_attempts', [])
    if transcriptions:
        parts.append('<h4 style="color:var(--accent);margin:1rem 0 0.5rem;font-size:0.95rem">Transcription Attempts</h4>')
        for t in transcriptions:
            conf_color = {'HIGH': '#2d8a4e', 'MEDIUM': '#b8860b', 'LOW': '#c44'}.get(
                t.get('confidence', ''), '#888')
            loc = escape(t.get('location', ''))
            lang = escape(t.get('language', ''))
            text = escape(t.get('text_partial', t.get('text', '')))
            notes = escape(t.get('notes', ''))
            conf = t.get('confidence', '')

            t_html = '<div class="marg-annotation">'
            t_html += f'<div class="hand-info" style="margin-bottom:0.5rem">'
            t_html += f'<strong>{loc}</strong>'
            if lang:
                t_html += f' &middot; {lang}'
            if conf:
                t_html += (f' &middot; <span style="color:{conf_color};font-weight:600">'
                          f'{conf}</span>')
            t_html += '</div>'
            if text:
                t_html += f'<div class="marginal-text">{text}</div>'
            if notes:
                t_html += f'<div class="context">{notes}</div>'
            t_html += '</div>'
            parts.append(t_html)

    # Symbols detected
    symbols = dr.get('symbols_detected', [])
    if symbols:
        parts.append('<h4 style="color:var(--accent);margin:1rem 0 0.5rem;font-size:0.95rem">Symbols Detected</h4>')
        for s in symbols:
            s_html = '<div class="marg-annotation">'
            s_html += f'<div class="hand-info"><strong>{escape(s.get("type", ""))}</strong>'
            if s.get('location'):
                s_html += f' &middot; {escape(s["location"])}'
            s_html += '</div>'
            if s.get('description'):
                s_html += f'<p style="line-height:1.7;margin:0.5rem 0">{escape(s["description"])}</p>'
            s_html += '</div>'
            parts.append(s_html)

    # Scholarly significance
    if dr.get('scholarly_significance'):
        parts.append(
            '<div class="marg-annotation" style="border-left:3px solid var(--accent);background:var(--bg)">'
            '<h4 style="color:var(--accent);margin-bottom:0.5rem">Scholarly Significance</h4>'
            f'<p style="line-height:1.7">{escape(dr["scholarly_significance"])}</p>'
            '</div>'
        )

    # Cross-references
    xrefs = dr.get('cross_references', [])
    if xrefs:
        refs_html = ', '.join(escape(x) for x in xrefs)
        parts.append(
            f'<div class="hand-info" style="margin-top:0.5rem">'
            f'<strong>Cross-references:</strong> {refs_html}</div>'
        )

    # Discrepancies
    discreps = dr.get('discrepancies', [])
    if discreps:
        for d in discreps:
            parts.append(
                '<div style="background:#fff8e1;border:1px solid #f0e68c;border-radius:4px;'
                'padding:0.75rem 1rem;margin:0.5rem 0;font-size:0.85rem">'
                f'<strong>Note ({escape(d.get("type", ""))}):</strong> '
                f'{escape(d.get("description", ""))}</div>'
            )

    # Provenance badge
    parts.append(
        '<div class="hand-info" style="margin-top:0.75rem">'
        '<span class="review-badge">Vision reading (Claude Code, Phase 3)</span></div>'
    )

    return '\n'.join(parts)


def build_marginalia_pages(conn):
    """Generate marginalia/index.html and marginalia/[signature].html."""
    cur = conn.cursor()
    marg_dir = SITE_DIR / 'marginalia'
    marg_dir.mkdir(exist_ok=True)

    # Get all matched signatures with their images and annotations
    cur.execute("""
        SELECT
            a.signature_ref, a.thesis_page, dr.context_text, a.annotation_text,
            a.thesis_chapter, m.shelfmark, m.institution, m.city,
            i.filename, COALESCE(i.web_path, i.relative_path), i.folio_number, i.side,
            mat.confidence, mat.needs_review,
            h.hand_label, h.attribution, h.is_alchemist, h.school,
            sm.quire, sm.leaf_in_quire,
            a.annotation_type
        FROM matches mat
        JOIN annotations a ON mat.ref_id = a.id
        JOIN images i ON mat.image_id = i.id
        JOIN manuscripts m ON i.manuscript_id = m.id
        LEFT JOIN dissertation_refs dr ON a.id = dr.id
        LEFT JOIN signature_map sm ON LOWER(a.signature_ref) = LOWER(sm.signature)
        LEFT JOIN annotator_hands h ON a.hand_id = h.id
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

    # Load folio descriptions (alchemist analyses)
    folio_descs = {}
    try:
        cur2 = conn.cursor()
        cur2.execute("""
            SELECT signature_ref, manuscript_shelfmark, hand_label,
                   title, description, alchemical_element, alchemical_process,
                   alchemical_framework, russell_page_ref
            FROM folio_descriptions
        """)
        for fd in cur2.fetchall():
            folio_descs.setdefault(fd[0], []).append({
                'ms': fd[1], 'hand': fd[2], 'title': fd[3],
                'desc': fd[4], 'element': fd[5], 'process': fd[6],
                'framework': fd[7], 'pages': fd[8],
            })
    except:
        pass

    # Load annotation types by signature
    ann_types_by_sig = {}
    try:
        cur_at = conn.cursor()
        cur_at.execute("""
            SELECT signature_ref, annotation_type, COUNT(*) FROM annotations
            WHERE annotation_type IS NOT NULL
            GROUP BY signature_ref, annotation_type
        """)
        for row in cur_at.fetchall():
            ann_types_by_sig.setdefault(row[0], []).append({
                'type': row[1], 'count': row[2]
            })
    except:
        pass

    # Load symbol occurrences by signature
    symbol_by_sig = {}
    try:
        cur3 = conn.cursor()
        cur3.execute("""
            SELECT so.signature_ref, s.symbol_name, s.metal, s.planet, s.gender,
                   so.context_text, so.latin_inflection, so.thesis_page, so.confidence,
                   h.hand_label, h.manuscript_shelfmark
            FROM symbol_occurrences so
            JOIN alchemical_symbols s ON so.symbol_id = s.id
            JOIN annotator_hands h ON so.hand_id = h.id
            ORDER BY so.signature_ref, s.symbol_name
        """)
        for row in cur3.fetchall():
            symbol_by_sig.setdefault(row[0], []).append({
                'symbol': row[1], 'metal': row[2], 'planet': row[3],
                'gender': row[4], 'context': row[5], 'inflection': row[6],
                'thesis_page': row[7], 'confidence': row[8],
                'hand': row[9], 'ms': row[10],
            })
    except:
        pass

    # Load Phase 3 deep readings by signature
    deep_by_sig = {}
    try:
        cur_dr = conn.cursor()
        cur_dr.execute("""
            SELECT sm.signature, ir.deep_reading_json
            FROM image_readings ir
            JOIN images i ON ir.image_id = i.id
            JOIN signature_map sm ON (
                CAST(REPLACE(REPLACE(i.filename, 'C_60_o_12-', ''), '.jpg', '') AS INTEGER) - 13
            ) = sm.id
            WHERE ir.phase = 3 AND ir.deep_reading_json IS NOT NULL
        """)
        for row in cur_dr.fetchall():
            deep_by_sig[row[0].lower()] = row[1]
    except Exception as e:
        print(f"  Warning: could not load deep readings: {e}")

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
             quire, leaf, annotation_type) = row

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

            type_html = ''
            if annotation_type:
                type_label = annotation_type.replace('_', ' ').title()
                type_html = f'<span style="display:inline-block;padding:0.1rem 0.5rem;background:var(--bg);border:1px solid var(--border);border-radius:2px;font-size:0.7rem;font-weight:600;text-transform:uppercase;margin-left:0.5rem;color:var(--text-muted)">{type_label}</span>'

            marginal_html = ''
            if marginal:
                marginal_html = f'<div class="marginal-text">&ldquo;{escape(marginal)}&rdquo;</div>'

            context_html = ''
            if context:
                ctx = context[:500] + ('...' if len(context) > 500 else '')
                context_html = f'<div class="context">{escape(ctx)}</div>'

            annotations_html += f"""
                <div class="marg-annotation">
                    {hand_html}{type_html}
                    {marginal_html}
                    {context_html}
                    <div class="hand-info">Russell, PhD Thesis, p. {thesis_page} (Ch. {chapter})</div>
                </div>"""

        folio_info = f'Folio {rows[0][10] or "?"}{rows[0][11] or ""}'
        quire_info = f', Quire {rows[0][18]}' if rows[0][18] else ''

        # Render folio description (alchemist analysis) if available
        desc_html = ''
        descs = folio_descs.get(sig, [])
        if descs:
            for fd in descs:
                element_html = f'<div class="hand-info"><strong>Element:</strong> {escape(fd["element"])}</div>' if fd.get('element') else ''
                process_html = f'<div class="hand-info"><strong>Process:</strong> {escape(fd["process"])}</div>' if fd.get('process') else ''
                framework_html = f'<div class="hand-info"><strong>Framework:</strong> {escape(fd["framework"])}</div>' if fd.get('framework') else ''
                pages_html = f'<div class="hand-info">Russell, {escape(fd["pages"])}</div>' if fd.get('pages') else ''
                desc_html += f"""
                <div class="marg-annotation" style="border-left:3px solid var(--accent); background:var(--bg)">
                    <h4 style="color:var(--accent); margin-bottom:0.5rem; font-size:1.05rem">{escape(fd["title"])}</h4>
                    <p style="line-height:1.7; margin-bottom:0.75rem">{escape(fd["desc"])}</p>
                    {element_html}
                    {process_html}
                    {framework_html}
                    {pages_html}
                    <div class="hand-info" style="margin-top:0.5rem"><span class="review-badge">LLM-assisted synthesis from Russell</span></div>
                </div>"""

        # Symbol occurrences for this folio
        symbols_html = ''
        sig_symbols = symbol_by_sig.get(sig, [])
        if sig_symbols:
            sym_rows = ''
            for s in sig_symbols:
                conf = confidence_badge_html(s['confidence'])
                infl = f' <code>{escape(s["inflection"])}</code>' if s.get('inflection') else ''
                sym_rows += f"""<tr>
                    <td><strong>{escape(s['symbol'])}</strong></td>
                    <td>{escape(s.get('metal') or '')}</td>
                    <td>{escape(s.get('planet') or '')}</td>
                    <td>{escape(s.get('gender') or '')}</td>
                    <td>Hand {escape(s['hand'])}{infl}</td>
                    <td>{conf}</td>
                </tr>"""
            symbols_html = f"""
            <h3 style="margin:1.5rem 0 1rem">Alchemical Symbols Present</h3>
            <table style="width:100%; border-collapse:collapse; font-size:0.85rem; margin-bottom:1rem">
                <thead><tr style="background:var(--bg)">
                    <th style="padding:0.5rem; border:1px solid var(--border)">Symbol</th>
                    <th style="padding:0.5rem; border:1px solid var(--border)">Metal</th>
                    <th style="padding:0.5rem; border:1px solid var(--border)">Planet</th>
                    <th style="padding:0.5rem; border:1px solid var(--border)">Gender</th>
                    <th style="padding:0.5rem; border:1px solid var(--border)">Hand</th>
                    <th style="padding:0.5rem; border:1px solid var(--border)">Conf.</th>
                </tr></thead>
                <tbody>{sym_rows}</tbody>
            </table>"""

        # Cross-links for alchemical folios
        alchem_cross = ''
        if desc_html or sig_symbols:
            links = ['<a href="../dictionary/alchemical-allegory.html">Alchemical Allegory</a>',
                     '<a href="../russell-alchemical-hands.html">Alchemical Hands Essay</a>']
            for s in sig_symbols:
                slug = slugify(s['symbol'])
                if slug in ('sol', 'mercury', 'hermaphrodite', 'sulphur'):
                    term_slugs = {'sol': 'sol-luna', 'mercury': 'master-mercury',
                                  'hermaphrodite': 'chemical-wedding', 'sulphur': 'great-work'}
                    ts = term_slugs.get(slug)
                    if ts:
                        links.append(f'<a href="../dictionary/{ts}.html">{escape(s["symbol"])}</a>')
            alchem_cross = f"""
            <div style="margin-top:1rem; padding-top:0.5rem; border-top:1px solid var(--border)">
                <strong style="font-size:0.85rem">Related:</strong> {''.join(set(links))}
            </div>"""

        detail_body = f"""
        <div class="marg-detail">
            <p><a href="index.html">&larr; All Folios</a></p>
            <h2>Signature {escape(sig)}</h2>
            <p style="color:var(--text-muted); font-family:var(--font-sans); margin-bottom:1.5rem">
                {folio_info}{quire_info}</p>
            <div class="marg-images">{images_html}</div>
            {f'<h3 style="margin:1.5rem 0 1rem">Alchemical Analysis</h3>' + desc_html if desc_html else ''}
            {symbols_html}
            {alchem_cross}"""

        # Deep reading section (Phase 3 vision analysis)
        deep_json = deep_by_sig.get(sig.lower())
        if deep_json:
            import json as _json
            try:
                dr = _json.loads(deep_json)
                dr_html = _render_deep_reading(dr)
                detail_body += dr_html
            except Exception:
                pass

        detail_body += """
            <h3 style="margin:1.5rem 0 1rem">Annotations</h3>"""

        # Add annotation type badges
        ann_types = ann_types_by_sig.get(sig, [])
        if ann_types:
            type_badges = ''
            for at in ann_types:
                type_badges += (
                    f'<span style="display:inline-block;padding:0.15rem 0.5rem;'
                    f'margin:0.1rem;border-radius:3px;font-size:0.7rem;font-weight:600;'
                    f'font-family:var(--font-sans);background:var(--bg);'
                    f'border:1px solid var(--border)">'
                    f'{escape(at["type"])} ({at["count"]})</span>'
                )
            detail_body += f'\n            <div style="margin-bottom:0.75rem">{type_badges}</div>'

        detail_body += f"""
            {annotations_html}
        </div>"""

        detail_page = page_shell(f'Folio {sig}', detail_body, active_nav='marginalia', depth=1)
        (marg_dir / f'{sig_slug}.html').write_text(detail_page, encoding='utf-8')

    # Build standalone pages for deep readings without Russell annotations
    standalone_dr = 0
    for dr_sig, dr_json in deep_by_sig.items():
        # Skip if already rendered in a marginalia page
        if any(dr_sig == s.lower() for s in by_sig.keys()):
            continue

        sig_slug = dr_sig.lower().replace(' ', '')
        import json as _json
        try:
            dr = _json.loads(dr_json)
        except Exception:
            continue

        # Look up folio info from signature_map
        sm_row = cur.execute(
            "SELECT folio_number, side, quire FROM signature_map WHERE LOWER(signature) = ?",
            (dr_sig,)
        ).fetchone()
        folio_info = f'Folio {sm_row[0]}{sm_row[1]}' if sm_row else ''
        quire_info = f', Quire {sm_row[2]}' if sm_row and sm_row[2] else ''

        # Get BL image if available
        page_num = None
        if sm_row:
            page_num_row = cur.execute(
                "SELECT id FROM signature_map WHERE LOWER(signature) = ?", (dr_sig,)
            ).fetchone()
            if page_num_row:
                page_num = page_num_row[0]

        img_html = ''
        if page_num:
            bl_photo = page_num + 13
            img_row = cur.execute(
                "SELECT COALESCE(web_path, relative_path), filename FROM images WHERE filename LIKE ?",
                (f'C_60_o_12-{bl_photo:03d}%',)
            ).fetchone()
            if img_row:
                img_html = f"""
                <div class="marg-images">
                    <div class="marg-image-card">
                        <img src="../{img_row[0]}" alt="Folio {dr_sig}" loading="lazy">
                        <div class="caption">British Library, London &mdash; C.60.o.12</div>
                    </div>
                </div>"""

        dr_html = _render_deep_reading(dr)

        detail_body = f"""
        <div class="marg-detail">
            <p><a href="index.html">&larr; All Folios</a></p>
            <h2>Signature {escape(dr_sig)}</h2>
            <p style="color:var(--text-muted); font-family:var(--font-sans); margin-bottom:1.5rem">
                {folio_info}{quire_info}</p>
            {img_html}
            {dr_html}
        </div>"""

        detail_page = page_shell(f'Folio {dr_sig}', detail_body, active_nav='marginalia', depth=1)
        (marg_dir / f'{sig_slug}.html').write_text(detail_page, encoding='utf-8')
        by_sig[dr_sig] = []  # Add to index
        standalone_dr += 1

    # Build marginalia index
    grid_items = ''
    def _sig_sort_key(s):
        rows = by_sig[s]
        if rows:
            return (str(rows[0][18] or 'zzz'), int(rows[0][10] or 999))
        # Standalone deep-reading pages: sort by signature string
        return (s[0] if s else 'zzz', int(''.join(c for c in s if c.isdigit()) or '999'))

    for sig in sorted(by_sig.keys(), key=_sig_sort_key):
        rows = by_sig[sig]
        sig_slug = sig.lower().replace(' ', '')

        if rows:
            n_images = len(set(r[8] for r in rows))
            n_annotations = len(rows)
            has_alchemist = any(r[16] for r in rows)
            alch = ' <span class="alchemist-tag">Alch.</span>' if has_alchemist else ''
            meta = f'{n_images} image{"s" if n_images != 1 else ""}, {n_annotations} ref{"s" if n_annotations != 1 else ""}'
        else:
            alch = ''
            has_dr = sig.lower() in deep_by_sig
            meta = 'Vision reading only' if has_dr else 'No annotations'

        grid_items += f"""
            <a href="{sig_slug}.html">
                <div class="sig-label">{escape(sig)}{alch}</div>
                <div class="sig-meta">{meta}</div>
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
                <h2>Bibliography</h2>
                <p>This bibliography is not a simple reading list. It is the site's
                map of the scholarly field: a structured record of primary sources,
                direct <em>Hypnerotomachia</em> scholarship, and related studies that
                help explain the book's material form, reception, imagery, and
                interpretive traditions. Entries are grouped so that readers can
                distinguish the core literature from the wider scholarly surround.</p>
                <p>Because bibliography is one of the project's main trust surfaces,
                this section places emphasis on review state, collection status,
                and data hygiene. Each entry shows whether we hold the work in our
                collection and whether the citation has been verified. That
                uncertainty remains visible rather than hidden behind uniform
                presentation.</p>
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
    for table in ['documents', 'images', 'annotations', 'matches',
                   'annotator_hands', 'bibliography', 'scholars', 'dictionary_terms',
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
                    <li><strong>{stats['annotations']}</strong> annotations extracted from Russell's thesis</li>
                    <li><strong>{stats['matches']}</strong> image-reference matches
                        ({stats['high_conf']} high confidence, {stats['low_conf']} low/provisional)</li>
                    <li><strong>{stats['annotator_hands']}</strong> annotator hands identified</li>
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
    # Core docs (root level)
    'SYSTEM.md': ('System Architecture', 'Architecture, data flow, operating modes, and constraints for the HP platform.'),
    'ONTOLOGY.md': ('Data Ontology', 'All 22 tables: canonical entities, deprecated tables, relationships, coverage, and confidence.'),
    'PIPELINE.md': ('Build Pipeline', 'Every script in execution order, from PDF ingestion through site generation.'),
    'INTERFACE.md': ('Interface Design', 'How data becomes pages: navigation, surfacing audit, page builders, design language.'),
    'ROADMAP.md': ('Execution Roadmap', 'What is BUILT, READY, BLOCKED, and SPECULATIVE. No hypothetical features.'),
    'README.md': ('README', 'Project overview for GitHub.'),
    # Archived docs (still published on the site for reference)
    'docs/archive/HPCONCORD.md': ('Concordance Methodology', 'How the 6-step folio-to-image concordance was built from Russell\'s thesis.'),
    'docs/archive/HPMIT.md': ('MIT Site Analysis', 'Reverse-engineering of the MIT Electronic Hypnerotomachia (1997).'),
    'docs/archive/HPMULTIMODAL.md': ('Multimodal RAG Study', 'Vision model proposal for reading 674 manuscript images.'),
    'docs/archive/MISTAKESTOAVOID.md': ('Mistakes to Avoid', 'Twelve hard-won lessons from this project.'),
    'docs/archive/IMAGEIDENTIFICATION.md': ('Image Identification', 'What Claude saw reading 69 BL manuscript photographs.'),
    'docs/archive/CONCORDANCEHACKING.md': ('Concordance Progress', 'How the concordance problem-solving progressed and metrics.'),
    'docs/archive/WOODCUTRESEARCHREPORT.md': ('Woodcut Research', '18 woodcuts: subjects, attribution, scholarly context.'),
    'docs/archive/ISIDORE4.md': ('System Critique', 'Concordance system audit: 7 issues, 0 integrity errors.'),
    'docs/archive/OUTWARDNOTDEEPER.md': ('Session Findings', 'Build outward not deeper: session discoveries and philosophy.'),
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
    'add_alchemist_descriptions.py': ('Add Alchemist Descriptions', 'Inserts 13 folio-specific scholarly descriptions for the two alchemist annotators from Russell Ch. 6-7.'),
    'seed_dictionary_v2.py': ('Seed Dictionary V2', 'Seeds 43 HP entity terms: characters, places, architecture, gardens, processions, aesthetics, materials.'),
    'seed_dictionary_v3.py': ('Seed Dictionary V3', 'Seeds 14 additional terms: narrative form, built form, aesthetics, alchemy, material culture.'),
    'generate_dictionary_significance.py': ('Generate Significance', 'Generates significance_to_hp and significance_to_scholarship prose for all 80+ dictionary terms.'),
    'link_scholars.py': ('Link Scholars', 'Links scholars to bibliography, tags historical figures, matches summaries.json to bibliography entries.'),
    'generate_scholar_overviews.py': ('Generate Scholar Overviews', 'Generates 2-3 paragraph overview prose for modern scholars and role descriptions for historical figures.'),
    'migrate_timeline.py': ('Timeline Migration', 'Adds category, medium, location, image_ref, confidence columns to timeline_events table.'),
    'seed_timeline_v2.py': ('Seed Timeline V2', 'Seeds ~30 new timeline events: art, literary influence, scholarly milestones, garden design.'),
    'seed_copies.py': ('Seed Copies', 'Creates hp_copies table and seeds six annotated copies with full metadata from Russell 2014.'),
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
                <p>This section makes the project legible as a research build
                rather than a black box. It gathers {len(docs)} internal methodological
                and reflective documents&mdash;ontology notes, concordance method,
                boundary audits, proposals, mistakes, aesthetic reviews, and related
                planning texts&mdash;that explain what the project thinks it is doing
                and where its assumptions have shifted over time.</p>
                <p>These documents are part of the scholarly apparatus, not just
                engineering residue. They record how the database, site, and
                interpretive claims were assembled, where the strongest arguments
                lie, and where the project has had to revise itself.</p>
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
                <p>This section exposes the deterministic pipeline behind the site.
                Rather than hiding the build logic, it presents these {len(scripts)} Python
                scripts that initialize the database, parse filenames, extract references,
                match folios to images, seed and enrich metadata, validate assumptions,
                and generate the static pages. The aim is transparency and reproducibility.</p>
                <p>The project's architectural stance is deliberately conservative: SQLite
                as source of truth, Python for transformation, JSON and static HTML for
                delivery, and as little framework machinery as possible. That simplicity
                is not an omission; it is part of the project's long-term durability model.</p>
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

def _build_annotated_woodcuts_gallery(conn):
    """Build the annotated woodcuts gallery section for the Alchemical Hands page.

    Shows the 18 CORPUS_EXTRACTION woodcuts with their scholarly apparatus:
    images, descriptions, annotation notes, dictionary links, and discussion.
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT slug, title, signature_1499, page_1499,
               subject_category, description, narrative_context,
               has_annotation, alchemical_annotation, annotation_density,
               dictionary_terms, scholarly_discussion, influence,
               depicted_elements
        FROM woodcuts
        WHERE source_method = 'CORPUS_EXTRACTION'
        ORDER BY page_1499
    """)
    woodcuts = cur.fetchall()
    if not woodcuts:
        return ''

    ia_img_dir = SITE_DIR / 'images' / 'woodcuts_1499'
    marg_dir = SITE_DIR / 'marginalia'
    dict_dir = SITE_DIR / 'dictionary'
    _ag_marg_sigs = {f.stem for f in marg_dir.glob('*.html') if f.stem != 'index'} if marg_dir.exists() else set()
    _ag_dict_slugs = {f.stem for f in dict_dir.glob('*.html') if f.stem != 'index'} if dict_dir.exists() else set()

    cat_colors = {
        'ARCHITECTURAL': '#8b5cf6', 'LANDSCAPE': '#10b981', 'NARRATIVE': '#3b82f6',
        'HIEROGLYPHIC': '#f59e0b', 'PROCESSION': '#ef4444', 'DECORATIVE': '#6366f1',
        'PORTRAIT': '#ec4899', 'DIAGRAM': '#14b8a6',
    }

    cards = ''
    for (slug, title, sig, page, cat, desc, narrative,
         has_ann, has_alch, ann_density, dict_terms,
         scholarly, influence, elements) in woodcuts:

        color = cat_colors.get(cat, '#6b7280')
        img_filename = f'hp1499_p{page:03d}.jpg'
        img_exists = (ia_img_dir / img_filename).exists()

        # Image
        if img_exists:
            img_tag = f'<img src="images/woodcuts_1499/{img_filename}" alt="{escape(title)}" style="width:100%;max-height:400px;object-fit:contain;border:1px solid var(--border);background:#f5f0e8;">'
        else:
            img_tag = '<div style="height:200px;background:#e8e0d0;display:flex;align-items:center;justify-content:center;color:#999">Image pending</div>'

        # Badges
        badges = f'<span class="wc-cat-badge" style="background:{color}">{escape(cat or "")}</span>'
        if has_alch:
            badges += ' <span class="alchemist-tag">Alchemist</span>'
        if ann_density:
            badges += f' <span style="font-size:0.7rem;color:var(--text-muted)">{ann_density}</span>'

        # Annotation note
        ann_note = ''
        if has_ann:
            ann_note = f'<p style="font-size:0.85rem;color:var(--accent);margin:0.5rem 0 0"><strong>BL annotations present</strong>'
            if has_alch:
                ann_note += ' (alchemical)'
            if sig and sig.lower() in _ag_marg_sigs:
                ann_note += f' &mdash; <a href="marginalia/{sig.lower()}.html">View folio {escape(sig)}</a>'
            ann_note += '</p>'

        # Dictionary links
        dict_html = ''
        if dict_terms:
            terms = [t.strip() for t in dict_terms.split(',') if t.strip() and t.strip() in _ag_dict_slugs]
            dict_links = ' '.join(f'<a href="dictionary/{t}.html" style="font-size:0.75rem;padding:0.1rem 0.4rem;background:var(--bg);border:1px solid var(--border);border-radius:2px;text-decoration:none;color:var(--text)">{t.replace("-", " ").title()}</a>' for t in terms)
            dict_html = f'<div style="margin-top:0.5rem">{dict_links}</div>'

        # Scholarly discussion
        schol_html = ''
        if scholarly:
            schol_html = f'<p style="font-size:0.85rem;color:var(--text-muted);margin-top:0.5rem;font-style:italic">{escape(scholarly[:200])}{"..." if len(scholarly) > 200 else ""}</p>'

        cards += f"""
        <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:6px;padding:1.25rem;margin-bottom:1.5rem">
            <div style="display:grid;grid-template-columns:minmax(200px,350px) 1fr;gap:1.5rem;align-items:start">
                <div>{img_tag}</div>
                <div>
                    <h4 style="margin:0 0 0.3rem;font-size:1.05rem;color:var(--text)">{escape(title)}</h4>
                    <div style="margin-bottom:0.5rem">{badges} <span style="font-size:0.8rem;color:var(--text-muted)">{escape(sig or "")} &middot; p.{page}</span></div>
                    <p style="line-height:1.7;margin:0">{escape(desc or "")}</p>
                    {schol_html}
                    {ann_note}
                    {dict_html}
                </div>
            </div>
        </div>"""

    alch_count = sum(1 for w in woodcuts if w[8])  # has_alch
    heavy_count = sum(1 for w in woodcuts if w[9] == 'HEAVY')

    return f"""
        <h2 id="annotated-woodcuts">Woodcuts with Marginal Annotations
            <a class="section-anchor" href="#annotated-woodcuts">#</a></h2>
        <p>Russell's dissertation identified 18 woodcut pages in the BL copy (C.60.o.12) that bear
        marginal annotations. Of these, {alch_count} have specifically alchemical annotations by Hand B,
        and {heavy_count} have heavy annotation density. These pages represent the intersection of the
        HP's visual program with its readers' interpretive activity &mdash; the woodcuts that provoked
        the most active engagement from the annotating hands.</p>
        <p class="evidence-note">These woodcuts were extracted from Russell's corpus analysis. Each entry
        preserves the original scholarly description, annotation data, and dictionary cross-references.
        Click the folio link to view the full marginalia page with Phase 3 deep readings.</p>
        {cards}"""


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
        SELECT a.signature_ref, a.thesis_page, dr.context_text, a.annotation_text,
               a.thesis_chapter, h.manuscript_shelfmark, h.hand_label, h.school
        FROM annotations a
        JOIN annotator_hands h ON a.hand_id = h.id
        LEFT JOIN dissertation_refs dr ON a.id = dr.id
        WHERE h.is_alchemist = 1
        ORDER BY a.thesis_page
    """)
    alch_refs = cur.fetchall()

    # Count matched images for alchemist refs
    cur.execute("""
        SELECT mat.confidence, COUNT(*)
        FROM matches mat
        JOIN annotations a ON mat.ref_id = a.id
        JOIN annotator_hands h ON a.hand_id = h.id
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
        <p>The BL alchemist (Hand B in C.60.o.12) is the more extensively documented of the two
        alchemical readers. Russell devotes Chapter 6 of his thesis to this hand, situating it within
        the broader tradition of seventeenth-century alchemical theory. The animating purpose of
        that theory was the recovery of <a href="dictionary/prisca-sapientia.html"><em>prisca sapientia</em></a>&mdash;an original wisdom, beginning
        with Hermes Trismegistus, that had been progressively obscured over the centuries. A text
        as complicated and linguistically obscure as the HP would have drawn much attention from
        an alchemist steeped in this tradition: the more recondite the text, the more ancient
        wisdom it was presumed to contain (Russell 2014, pp. 154&ndash;156).</p>

        <div style="margin:1.5rem 0; text-align:center">
            <img src="images/bl/C_60_o_12-003.jpg" alt="BL flyleaf verso: Master Mercury declaration"
                 style="max-width:100%; border:1px solid var(--border); border-radius:4px" loading="lazy">
            <p style="font-size:0.8rem; color:var(--text-muted); margin-top:0.3rem">
                BL C.60.o.12, flyleaf verso (photo 003). Hand B's Master Mercury declaration.
                The shelfmark "C.60.o.12" and the date "1641" are visible below.</p>
        </div>

        <h3>The <a href="dictionary/master-mercury.html" style="color:inherit">Master Mercury</a> Declaration</h3>
        <p>On the flyleaf verso, Hand B wrote a Latin summary declaring what the HP truly means:</p>
        <blockquote>"verus sensus intentionis huius libri est 3um: Geni et Totius Naturae energiae
        &amp; operationum Magisteri Mercurii Descriptio elegans, ampla"</blockquote>
        <p><em>The true sense of the intention of this book is threefold: the full and elegant
        description of the energy and spirit of the whole nature, and of the operations of
        Master Mercury.</em></p>
        <p>This declaration positions mercury (quicksilver) as the central principle. In the
        alchemical framework of Jean d'Espagnet (1564&ndash;1637), whose <em>Enchiridion Physicae
        Restitutae</em> was available in English from 1651, mercury is the vehicle of the
        <em>spiritus mundi</em>&mdash;the world spirit emanating from the sun. Mercury was understood
        to be the primal metal, always liquid at room temperature, while all other metals achieved
        liquidity only through heat. It was, as Russell puts it, "all things to all people" in the
        alchemical tradition (Russell 2014, pp. 159&ndash;161).</p>
        <p>The annotator also twice praises the HP as "ingeniosissimo," recognizing it as exemplifying
        the <a href="dictionary/ingegno.html"><em>ingegno</em></a>&mdash;the improvisational
        intelligence&mdash;that early modern readers cultivated through annotation.</p>

        <div style="margin:1.5rem 0; text-align:center">
            <img src="images/bl/C_60_o_12-041.jpg" alt="BL b6v: Elephant and Obelisk with alchemical annotations"
                 style="max-width:100%; border:1px solid var(--border); border-radius:4px" loading="lazy">
            <p style="font-size:0.8rem; color:var(--text-muted); margin-top:0.3rem">
                BL C.60.o.12, signature b6v (photo 041). The elephant and obelisk woodcut,
                densely annotated by Hand B with alchemical ideograms. This image later
                inspired Bernini's 1667 sculpture in Piazza della Minerva, Rome.</p>
        </div>

        <h3>The Ideographic Vocabulary</h3>
        <p>Hand B used an extensive vocabulary of alchemical ideograms&mdash;compact symbols for
        gold, silver, mercury, Venus, Jupiter, and other elements&mdash;embedded within the syntax
        of Latin sentences. A particularly distinctive feature is the way B appended Latin case
        inflections to these symbols: "aurum" would be written as the gold symbol + "-um," and
        "Veneris" as the Venus symbol + "-eris." This creates a hybrid semiotic system where
        chemical signs function as Latin nouns within grammatical sentences
        (Russell 2014, pp. 149&ndash;152).</p>
        <p>Russell notes that B's ideographic vocabulary shows striking consistency with Isaac
        Newton's manuscripts in the Keynes collection at Cambridge. Although the BL hand is
        certainly not Newton's, this consistency "may suggest that B was attached to the Royal
        Society, from the environs of Cambridge, or was otherwise connected to the figure of
        Newton" (Russell 2014, pp. 158&ndash;159). A careful comparison of B's annotations with
        Newton's remains, Russell notes, a productive avenue for future research.</p>

        <p class="evidence-note">Source: Russell 2014, Ch. 6, pp. 154&ndash;168. This project has
        {len(bl_refs)} dissertation references attributed to Hand B, and has visually confirmed
        the Master Mercury declaration and ideographic annotations on BL photographs 003 (flyleaf)
        and 041 (b6v, elephant and obelisk).</p>

        <div style="display:flex; gap:1rem; flex-wrap:wrap; margin:1.5rem 0">
            <div style="flex:1; min-width:250px; text-align:center">
                <img src="images/bl/C_60_o_12-014.jpg" alt="BL a1r: opening page with annotations"
                     style="max-width:100%; border:1px solid var(--border); border-radius:4px" loading="lazy">
                <p style="font-size:0.8rem; color:var(--text-muted); margin-top:0.3rem">
                    a1r (photo 014). The HP's opening page: "POLIPHILO INCOMINCIA."
                    Marginal annotations from both Hand A (Jonson) and Hand B (alchemist).</p>
            </div>
            <div style="flex:1; min-width:250px; text-align:center">
                <img src="images/bl/C_60_o_12-004.jpg" alt="BL title page with Jonson ownership"
                     style="max-width:100%; border:1px solid var(--border); border-radius:4px" loading="lazy">
                <p style="font-size:0.8rem; color:var(--text-muted); margin-top:0.3rem">
                    Title page (photo 004). "RISTAMPATO DI NOVO... M.D.XXXXV" (1545).
                    Ben Jonson's ownership inscription "Sum Ben: Ionsonij" at bottom.</p>
            </div>
        </div>

        <h3>BL Alchemist: Referenced Folios</h3>
        <table>
            <thead><tr><th>Signature</th><th>Thesis Page</th><th>Marginal Text</th></tr></thead>
            <tbody>{bl_rows}</tbody>
        </table>
        <div class="evidence-note">BL image matches are HIGH confidence: the BL offset
        (page = photo number &minus; 13) has been vision-verified at 174 of 174 readable pages
        with zero mismatches. The BL copy is the 1545 edition; the signature map is based on
        the 1499 collation, but the offset is confirmed stable across the entire volume.</div>

        <h2 id="buffalo-alchemist">The Buffalo Alchemical Hand (Hand E)
            <a class="section-anchor" href="#buffalo-alchemist">#</a></h2>
        <p>Hand E in the Buffalo copy is the latest of five interleaved hands, overwriting Hand D.
        Like the BL alchemist, Hand E labels passages and woodcuts with the element or stage of
        the alchemical process they were presumed to allegorize. But Hand E follows a fundamentally
        different alchemical school: the pseudo-Geber tradition (from Jabir ibn Hayyan), which
        emphasizes sulphur and the <a href="dictionary/sol-luna.html">Sol/Luna</a> (Sun/Moon)
        duality rather than mercury (Russell 2014, pp. 170&ndash;186).</p>
        <p>In the Geberian framework, the masculine principle is represented by Sol (gold) and the
        feminine by Luna (silver). What makes Geber's thought distinctive is that these are understood
        as creative inverses: gold is masculine "in its height" and feminine "in its depth," while
        silver is feminine "in its height" and masculine "in its depth." It is the variance in these
        proportions that differentiates elements (Russell 2014, p. 187).</p>

        <h3>The Chess Match as Alchemical Distillation</h3>
        <p>Hand E's most remarkable annotation is a sustained alchemical reading of the human chess
        match at Queen Eleuterylida's palace (g8r&ndash;h1r). Thirty-two maidens play, one side
        dressed in silver and the other in gold. But the queens of both sides wear gold, and the
        kings of both wear silver&mdash;the inverse of the Geberian ideal, signaling that transmutation
        has yet to occur.</p>
        <p>The annotator recorded the results of each of three rounds. Silver wins the first match;
        Hand E writes "Argentum" and draws a small crescent moon (Luna). Silver wins again in the
        second round. Gold finally triumphs in the third, and E initially writes "Rex ex auro factus
        victoriam ultimam"&mdash;then hesitates, corrects "Rex" to "[Re]gina," "auro" to "aura,"
        "factus" to the solar symbol + "uestita," and "victor" to "victrix." E then cancels "Regina"
        and places "Auru(m)" as the culmination. The king of gold wins only after multiple rounds of
        play, each round representing a distillation (Russell 2014, pp. 188&ndash;189).</p>
        <p>The outcome of this alchemical marriage is a hermaphrodite&mdash;the <em>coincidentia
        oppositorum</em>, the union of opposite qualities. Hand E found this principle encoded in
        the epigram D.AMBIG.D.D. ("dedicated to the ambiguous gods") on a statue base (b5r),
        which E reads as "diis ambiguis id est metallis hermafroditis"&mdash;"to the ambiguous gods,
        that is, to the metallic hermaphrodites" (Russell 2014, pp. 189&ndash;190).</p>

        <div style="margin:1.5rem 0; text-align:center">
            <img src="images/bl/C_60_o_12-036.jpg" alt="BL b4r: Twin inscribed monuments with D.AMBIG.D.D."
                 style="max-width:100%; border:1px solid var(--border); border-radius:4px" loading="lazy">
            <p style="font-size:0.8rem; color:var(--text-muted); margin-top:0.3rem">
                BL C.60.o.12, signature b4r (photo 036). The twin inscribed monuments bearing
                "D.AMBIG.D.D." &mdash; which Hand E in the Buffalo copy reads as "dedicated to
                the ambiguous gods, that is, to the metallic hermaphrodites." The BL copy
                shows this same passage heavily annotated by both hands.</p>
        </div>

        <p class="evidence-note">Source: Russell 2014, Ch. 7, pp. 170&ndash;191. This project has
        {len(buf_refs)} dissertation references attributed to Hand E. The Buffalo copy has no
        photographs; images above show the same folios in the BL copy.</p>

        <div style="margin:1.5rem 0; text-align:center">
            <img src="images/bl/C_60_o_12-033.jpg" alt="BL page 20: alchemical ideograms visible in left margin"
                 style="max-width:100%; border:1px solid var(--border); border-radius:4px" loading="lazy">
            <p style="font-size:0.8rem; color:var(--text-muted); margin-top:0.3rem">
                BL C.60.o.12, page 20 (photo 033). Alchemical ideograms visible in the left
                margin, showing Hand B's characteristic practice of embedding planetary
                symbols within Latin syntax. The pyramid passage is densely annotated.</p>
        </div>

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
        <div class="evidence-note">All BL matches are HIGH confidence, verified by vision reading
        of 174 sequential BL photographs with a confirmed offset of 13 (zero mismatches).</div>

        <h2 id="secure-vs-provisional">What Is Secure vs. Provisional
            <a class="section-anchor" href="#secure-vs-provisional">#</a></h2>
        <p><strong>Secure:</strong></p>
        <ul>
            <li>The existence and general character of two alchemical annotators (BL Hand B and Buffalo Hand E)</li>
            <li>The alchemical schools they followed (d'Espagnet vs. pseudo-Geber)</li>
            <li>The Master Mercury declaration on the BL flyleaf</li>
            <li>The folio signatures referenced by Russell in his thesis</li>
            <li>The signature map for the 1499 edition</li>
            <li>BL photograph-to-folio matches (HIGH confidence, vision-verified at 174/174 pages)</li>
        </ul>
        <p><strong>Provisional:</strong></p>
        <ul>
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

        {_build_annotated_woodcuts_gallery(conn)}

        <div class="cross-links">
            <h4>Related Dictionary Terms</h4>
            <a href="dictionary/alchemical-allegory.html">Alchemical Allegory</a>
            <a href="dictionary/master-mercury.html">Master Mercury</a>
            <a href="dictionary/sol-luna.html">Sol and Luna</a>
            <a href="dictionary/chemical-wedding.html">Chemical Wedding</a>
            <a href="dictionary/ideogram.html">Ideogram</a>
            <a href="dictionary/prisca-sapientia.html">Prisca Sapientia</a>
            <a href="dictionary/annotator-hand.html">Annotator Hand</a>
            <a href="dictionary/activity-book.html">Activity Book</a>
            <a href="dictionary/ingegno.html">Ingegno</a>
            <a href="dictionary/elephant-obelisk.html">Elephant and Obelisk</a>
            <a href="dictionary/beroalde-1600.html">Beroalde 1600 Edition</a>
            <a href="dictionary/poliphilo.html">Poliphilo</a>
            <a href="dictionary/polia.html">Polia</a>
            <a href="dictionary/venus-aphrodite.html">Venus</a>
            <a href="dictionary/cupid-eros.html">Cupid / Eros</a>
            <h4>Related Pages</h4>
            <a href="concordance-method.html">Concordance Methodology</a>
            <a href="scholar/james-russell.html">James Russell</a>
            <a href="dictionary/reception-history.html">Reception History</a>
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
    cur.execute("SELECT COUNT(*) FROM annotations")
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
            <h4>Related Dictionary Terms</h4>
            <a href="dictionary/signature.html">Signature</a>
            <a href="dictionary/folio.html">Folio</a>
            <a href="dictionary/recto.html">Recto</a>
            <a href="dictionary/verso.html">Verso</a>
            <a href="dictionary/quire.html">Quire</a>
            <a href="dictionary/collation.html">Collation</a>
            <a href="dictionary/incunabulum.html">Incunabulum</a>
            <a href="dictionary/annotator-hand.html">Annotator Hand</a>
            <a href="dictionary/marginalia.html">Marginalia</a>
            <a href="dictionary/1499-edition.html">1499 Edition</a>
            <a href="dictionary/1545-edition.html">1545 Edition</a>
            <h4>Related Pages</h4>
            <a href="russell-alchemical-hands.html">Alchemical Hands Essay</a>
            <a href="scholar/james-russell.html">James Russell</a>
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
# Timeline page
# ============================================================

def build_timeline_page(conn):
    """Generate timeline.html with chronological HP reception history."""
    cur = conn.cursor()
    cur.execute("""
        SELECT year, year_end, event_type, title, description, category,
               medium, location, confidence, manuscript_shelfmark
        FROM timeline_events ORDER BY year, id
    """)
    events = cur.fetchall()

    # Group by year
    by_year = {}
    for e in events:
        by_year.setdefault(e[0], []).append(e)

    # Category colors
    cat_colors = {
        'art': '#8b5cf6', 'scholarship': '#3b82f6', 'edition': '#10b981',
        'literary': '#f59e0b', '': '#6b7280',
    }
    cat_labels = {
        'art': 'Art & Design', 'scholarship': 'Scholarship', 'edition': 'Edition',
        'literary': 'Literary Influence', '': 'Other',
    }

    timeline_css = '<style>' + """
        .timeline-page { max-width: 900px; margin: 2rem auto; padding: 0 2rem; }
        .timeline-page h2 { color: var(--accent); }
        .timeline-page p { line-height: 1.8; }
        .timeline-filters { display: flex; gap: 0.5rem; flex-wrap: wrap; margin: 1.5rem 0; }
        .timeline-filters label { display: flex; align-items: center; gap: 0.3rem; font-size: 0.85rem; font-family: var(--font-sans); cursor: pointer; padding: 0.3rem 0.6rem; border: 1px solid var(--border); border-radius: 3px; }
        .timeline-filters input { margin: 0; }
        .timeline { position: relative; padding-left: 2rem; margin-top: 2rem; }
        .timeline::before { content: ''; position: absolute; left: 0.5rem; top: 0; bottom: 0; width: 2px; background: var(--border); }
        .timeline-year { margin-bottom: 2rem; position: relative; }
        .year-marker { position: sticky; top: 4rem; font-size: 1.3rem; font-weight: 700; color: var(--accent); font-family: var(--font-sans); margin-bottom: 0.5rem; padding-left: 0; margin-left: -2rem; background: var(--bg-main, #fff); z-index: 1; }
        .timeline-card { padding: 0.75rem 1rem; margin-bottom: 0.75rem; background: var(--bg-card); border: 1px solid var(--border); border-radius: 4px; position: relative; }
        .timeline-card::before { content: ''; position: absolute; left: -1.55rem; top: 1rem; width: 8px; height: 8px; border-radius: 50%; background: var(--accent); }
        .card-type-badge { display: inline-block; font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; padding: 0.1rem 0.4rem; border-radius: 2px; color: white; margin-bottom: 0.3rem; font-family: var(--font-sans); }
        .timeline-card h4 { margin: 0 0 0.3rem 0; font-size: 0.95rem; }
        .timeline-card p { font-size: 0.85rem; color: var(--text-muted); margin: 0; line-height: 1.6; }
        .timeline-card .card-meta { font-size: 0.75rem; color: var(--text-muted); font-family: var(--font-sans); margin-top: 0.3rem; }
    """ + '</style>'

    # Build timeline HTML
    timeline_html = ''
    for year in sorted(by_year.keys()):
        year_events = by_year[year]
        cards = ''
        for e in year_events:
            (yr, yr_end, etype, title, desc, cat, medium, loc, conf, ms) = e
            cat = cat or ''
            color = cat_colors.get(cat, '#6b7280')
            label = cat_labels.get(cat, etype or 'Other')
            badge = f'<span class="card-type-badge" style="background:{color}">{escape(label)}</span>'
            meta_parts = []
            if medium:
                meta_parts.append(escape(medium))
            if loc:
                meta_parts.append(escape(loc))
            if conf and conf != 'HIGH':
                meta_parts.append(f'Confidence: {escape(conf)}')
            meta = f'<div class="card-meta">{" | ".join(meta_parts)}</div>' if meta_parts else ''

            cards += f"""
                <div class="timeline-card" data-category="{escape(cat)}">
                    {badge}
                    <h4>{escape(title)}</h4>
                    <p>{escape(desc or '')}</p>
                    {meta}
                </div>"""

        year_label = f"{year}" if not year_events[0][1] else f"{year}-{year_events[0][1]}"
        timeline_html += f"""
            <div class="timeline-year">
                <div class="year-marker">{year_label}</div>
                {cards}
            </div>"""

    # Filters
    categories = sorted(set(e[5] or '' for e in events))
    filter_html = ''
    for cat in categories:
        label = cat_labels.get(cat, cat or 'Other')
        color = cat_colors.get(cat, '#6b7280')
        filter_html += f'<label><input type="checkbox" checked data-filter="{escape(cat)}"> <span style="color:{color}">{escape(label)}</span></label>'

    filter_js = """
    <script>
    document.querySelectorAll('.timeline-filters input').forEach(cb => {
        cb.addEventListener('change', () => {
            const cat = cb.dataset.filter;
            const show = cb.checked;
            document.querySelectorAll(`.timeline-card[data-category="${cat}"]`).forEach(card => {
                card.style.display = show ? '' : 'none';
            });
            // Hide empty year markers
            document.querySelectorAll('.timeline-year').forEach(yr => {
                const visible = yr.querySelectorAll('.timeline-card:not([style*="display: none"])');
                yr.style.display = visible.length ? '' : 'none';
            });
        });
    });
    </script>"""

    body = f"""
    <div class="timeline-page">
        <h2>Timeline of the <em>Hypnerotomachia Poliphili</em></h2>
        <p>A chronological view of the HP's five-century reception: editions, translations,
        annotations, scholarship, and art inspired by the book. {len(events)} events spanning
        {min(by_year.keys())}&ndash;{max(by_year.keys())}.</p>
        <p style="font-size:0.85rem; color:var(--text-muted)">Filter by category:</p>
        <div class="timeline-filters">{filter_html}</div>
        <div class="timeline">{timeline_html}</div>
    </div>"""

    page = page_shell('Timeline', body, active_nav='timeline',
                       extra_css=timeline_css, extra_js=filter_js)
    (SITE_DIR / 'timeline.html').write_text(page, encoding='utf-8')
    print(f"  timeline.html ({len(events)} events)")


# ============================================================
# Manuscripts pages
# ============================================================

def build_manuscripts_pages(conn):
    """Generate manuscripts/index.html and manuscripts/*.html from hp_copies."""
    cur = conn.cursor()
    manu_dir = SITE_DIR / 'manuscripts'
    manu_dir.mkdir(exist_ok=True)

    # Get all copies
    cur.execute("""
        SELECT id, shelfmark, institution, city, country, edition,
               has_annotations, studied_by, annotation_summary,
               hand_count, copy_notes, has_images_in_project,
               confidence, review_status
        FROM hp_copies ORDER BY edition, shelfmark
    """)
    copies = cur.fetchall()

    # Get hands per copy
    cur.execute("""
        SELECT manuscript_shelfmark, hand_label, attribution, is_alchemist, school, description
        FROM annotator_hands ORDER BY manuscript_shelfmark, hand_label
    """)
    hands_by_ms = {}
    for row in cur.fetchall():
        hands_by_ms.setdefault(row[0], []).append(row)

    # Get ref counts per copy (uses dissertation_refs because 51 annotations
    # lack manuscript_id linkage — TODO: backfill manuscript_id in annotations)
    cur.execute("""
        SELECT manuscript_shelfmark, COUNT(*) FROM dissertation_refs
        WHERE manuscript_shelfmark IS NOT NULL
        GROUP BY manuscript_shelfmark
    """)
    refs_by_ms = {row[0]: row[1] for row in cur.fetchall()}

    # Get match counts per copy
    cur.execute("""
        SELECT m.shelfmark, mat.confidence, COUNT(*)
        FROM matches mat
        JOIN images i ON mat.image_id = i.id
        JOIN manuscripts m ON i.manuscript_id = m.id
        GROUP BY m.shelfmark, mat.confidence
    """)
    matches_by_ms = {}
    for row in cur.fetchall():
        matches_by_ms.setdefault(row[0], {})[row[1]] = row[2]

    manu_css = '<style>' + """
        .manuscripts-page { max-width: 900px; margin: 2rem auto; padding: 0 2rem; }
        .manuscripts-page h2 { color: var(--accent); border-bottom: 1px solid var(--border); padding-bottom: 0.3rem; }
        .manuscripts-page h3 { margin-top: 2rem; }
        .manuscripts-page p { line-height: 1.8; }
        .copy-card { padding: 1.5rem; margin-bottom: 1.5rem; background: var(--bg-card); border: 1px solid var(--border); border-radius: 4px; }
        .copy-card h3 { margin-top: 0; color: var(--accent); }
        .copy-card .copy-meta { font-size: 0.85rem; color: var(--text-muted); font-family: var(--font-sans); margin-bottom: 0.5rem; }
        .copy-card .copy-notes { font-size: 0.9rem; line-height: 1.7; }
        .copy-detail { max-width: 850px; margin: 2rem auto; padding: 0 2rem; }
        .copy-detail h2 { color: var(--accent); }
        .copy-detail h3 { margin-top: 1.5rem; border-bottom: 1px solid var(--border); padding-bottom: 0.2rem; }
        .copy-detail p { line-height: 1.8; }
        .copy-detail table { width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.85rem; }
        .copy-detail th, .copy-detail td { padding: 0.5rem 0.75rem; border: 1px solid var(--border); text-align: left; }
        .copy-detail th { background: var(--bg); font-weight: 600; }
        .copy-detail .provisional { background: #fff3cd; padding: 0.5rem 1rem; border-left: 3px solid #ffc107; margin: 1rem 0; font-size: 0.9rem; }
        .copy-detail .cross-links { margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--border); }
        .copy-detail .cross-links a { display: inline-block; margin: 0.2rem 0.3rem; padding: 0.2rem 0.6rem; background: var(--bg); border: 1px solid var(--border); border-radius: 3px; font-size: 0.85rem; color: var(--text); text-decoration: none; }
        .copy-detail .cross-links a:hover { border-color: var(--accent); color: var(--accent); }
    """ + '</style>'

    # Build detail pages
    annotated_cards = ''
    for copy in copies:
        (cid, shelfmark, inst, city, country, edition, has_annot,
         studied_by, annot_summary, hand_count, notes,
         has_images, confidence, status) = copy

        slug = slugify(shelfmark)
        hands = hands_by_ms.get(shelfmark, [])
        ref_count = refs_by_ms.get(shelfmark, 0)
        match_data = matches_by_ms.get(shelfmark, {})

        # Confidence badge
        conf_badge = confidence_badge_html(confidence) if confidence else ''

        # Card for index
        meta_parts = [f'{escape(inst)}, {escape(city or "")}']
        if edition:
            meta_parts.append(f'{edition} edition')
        if hand_count:
            meta_parts.append(f'{hand_count} annotator hand{"s" if hand_count != 1 else ""}')
        if ref_count:
            meta_parts.append(f'{ref_count} dissertation refs')

        annotated_cards += f"""
        <div class="copy-card">
            <h3><a href="{slug}.html">{escape(shelfmark)}</a> {conf_badge}</h3>
            <div class="copy-meta">{" | ".join(meta_parts)}</div>
            <div class="copy-notes">{escape(notes or '')}</div>
        </div>"""

        # Detail page
        # Hands table
        hands_html = ''
        if hands:
            rows = ''
            for h in hands:
                alch = ' (alchemist)' if h[3] else ''
                school = f' [{escape(h[4])}]' if h[4] else ''
                rows += f'<tr><td>{escape(h[1])}</td><td>{escape(h[2] or "Anonymous")}{alch}{school}</td><td>{escape((h[5] or "")[:200])}</td></tr>'
            hands_html = f"""
            <h3>Annotator Hands</h3>
            <table>
                <thead><tr><th>Hand</th><th>Attribution</th><th>Description</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>"""

        # Match stats
        match_html = ''
        if match_data:
            total = sum(match_data.values())
            match_html = f"""
            <h3>Image Matches</h3>
            <p>{total} images matched to dissertation references.</p>
            <ul>
                <li>HIGH confidence: {match_data.get('HIGH', 0)}</li>
                <li>MEDIUM confidence: {match_data.get('MEDIUM', 0)}</li>
                <li>LOW confidence: {match_data.get('LOW', 0)}</li>
            </ul>"""

        # Provisional warning for BL
        prov_html = ''
        if confidence == 'LOW':
            prov_html = '<div class="provisional">All image matches for this copy are LOW confidence. The photograph numbering does not directly encode folio information. Manual verification is required.</div>'

        # Cross links
        cross_links = ['<a href="../dictionary/annotator-hand.html">Annotator Hand</a>',
                       '<a href="../dictionary/marginalia.html">Marginalia</a>',
                       '<a href="../concordance-method.html">Concordance Method</a>']
        if any(h[3] for h in hands):
            cross_links.append('<a href="../russell-alchemical-hands.html">Alchemical Hands Essay</a>')
            cross_links.append('<a href="../dictionary/alchemical-allegory.html">Alchemical Allegory</a>')

        detail_body = f"""
        <div class="copy-detail">
            <p><a href="index.html">&larr; All Manuscripts</a></p>
            <h2>{escape(shelfmark)} {conf_badge}</h2>
            <p><strong>{escape(inst)}</strong>, {escape(city or '')} ({escape(country or '')})</p>
            <p>Edition: {escape(edition or 'unknown')} | Studied by: {escape(studied_by or 'not studied')} |
               Dissertation references: {ref_count} | Images in project: {'Yes' if has_images else 'No'}</p>
            <h3>Description</h3>
            <p>{escape(notes or 'No description available.')}</p>
            {hands_html}
            {match_html}
            {prov_html}
            <div class="cross-links">
                <h4>Related Pages</h4>
                {''.join(cross_links)}
            </div>
        </div>"""

        detail_page = page_shell(shelfmark, detail_body, active_nav='manuscripts',
                                  extra_css=manu_css, depth=1)
        (manu_dir / f'{slug}.html').write_text(detail_page, encoding='utf-8')

    # Index page
    index_body = f"""
    <div class="manuscripts-page">
        <h2>Manuscripts of the <em>Hypnerotomachia Poliphili</em></h2>
        <p>The 1499 <em>Hypnerotomachia Poliphili</em> survives in approximately 200 copies
        worldwide. Russell's PhD thesis (2014) studied six annotated copies in detail,
        identifying eleven distinct annotator hands. This section presents those copies
        with their annotation profiles, hand attributions, and links to the project's
        marginalia and concordance data.</p>
        <p>Each copy page shows the annotator hands identified by Russell, the number of
        dissertation references attributed to that copy, and any matched images. Where
        matching confidence is low, that status is marked explicitly.</p>

        <h3>Annotated Copies Studied by Russell (2014)</h3>
        {annotated_cards}
    </div>"""

    index_page = page_shell('Manuscripts', index_body, active_nav='manuscripts',
                             extra_css=manu_css, depth=1)
    (manu_dir / 'index.html').write_text(index_page, encoding='utf-8')
    print(f"  manuscripts/index.html + {len(copies)} copy pages")


# ============================================================
# Woodcuts pages
# ============================================================

def build_woodcuts_pages(conn):
    """Generate woodcuts/index.html and woodcuts/*.html — 1499 edition gallery.

    Sources woodcut images from Internet Archive facsimile (A336080v1,
    University of Seville copy, 600ppi). Falls back to BL photographs
    where IA images are not yet cached.
    """
    cur = conn.cursor()
    wc_dir = SITE_DIR / 'woodcuts'
    wc_dir.mkdir(exist_ok=True)
    ia_img_dir = SITE_DIR / 'images' / 'woodcuts_1499'

    # Clean up stale pages from previous builds
    for old_file in wc_dir.glob('*.html'):
        if old_file.stem != 'index':
            old_file.unlink()

    # Which signatures have marginalia pages?
    marg_dir = SITE_DIR / 'marginalia'
    _wc_marg_sigs = set()
    if marg_dir.exists():
        for f in marg_dir.glob('*.html'):
            if f.stem != 'index':
                _wc_marg_sigs.add(f.stem)

    # Which dictionary terms exist?
    dict_dir = SITE_DIR / 'dictionary'
    _wc_dict_slugs = set()
    if dict_dir.exists():
        for f in dict_dir.glob('*.html'):
            if f.stem != 'index':
                _wc_dict_slugs.add(f.stem)

    cur.execute("""
        SELECT id, slug, title, signature_1499, page_1499, page_1499_ia,
               bl_photo_number, subject_category, woodcut_type,
               description, narrative_context, chapter_context,
               depicted_elements, has_annotation, alchemical_annotation,
               annotation_density, dictionary_terms, scholarly_discussion,
               influence, source_method, confidence, notes,
               ia_image_cached
        FROM woodcuts
        WHERE page_1499 IS NOT NULL
          AND source_method != 'CORPUS_EXTRACTION'
        ORDER BY page_1499
    """)
    woodcuts = cur.fetchall()

    if not woodcuts:
        print("  woodcuts: no data")
        return

    cat_colors = {
        'ARCHITECTURAL': '#8b5cf6', 'LANDSCAPE': '#10b981', 'NARRATIVE': '#3b82f6',
        'HIEROGLYPHIC': '#f59e0b', 'PROCESSION': '#ef4444', 'DECORATIVE': '#6366f1',
        'PORTRAIT': '#ec4899', 'DIAGRAM': '#14b8a6',
    }

    wc_css = '<style>' + """
        .woodcuts-page { max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }
        .woodcuts-page h1 { color: var(--accent); font-size: 1.8rem; margin-bottom: 0.3rem; }
        .woodcuts-page .intro { max-width: 800px; line-height: 1.8; margin-bottom: 1.5rem; color: var(--text-muted); }
        .wc-filters { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 1.5rem; }
        .wc-filter-btn { padding: 0.3rem 0.7rem; border: 1px solid var(--border); border-radius: 3px;
                         font-size: 0.75rem; font-weight: 600; text-transform: uppercase; cursor: pointer;
                         background: var(--bg); color: var(--text-muted); transition: all 0.15s; }
        .wc-filter-btn:hover, .wc-filter-btn.active { background: var(--accent); color: white; border-color: var(--accent); }
        .woodcut-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1.5rem; }
        .woodcut-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 6px;
                        overflow: hidden; transition: box-shadow 0.2s, transform 0.2s; }
        .woodcut-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); transform: translateY(-2px); }
        .woodcut-card img { width: 100%; height: 320px; object-fit: cover; object-position: top;
                            border-bottom: 1px solid var(--border); background: #f5f0e8; }
        .woodcut-card .wc-info { padding: 0.75rem 1rem; }
        .woodcut-card h4 { margin: 0 0 0.3rem; font-size: 0.95rem; }
        .woodcut-card h4 a { color: var(--text); text-decoration: none; }
        .woodcut-card h4 a:hover { color: var(--accent); }
        .woodcut-card .wc-meta { font-size: 0.75rem; color: var(--text-muted); font-family: var(--font-sans); }
        .woodcut-card .wc-desc { font-size: 0.82rem; color: var(--text-muted); margin: 0.3rem 0 0; line-height: 1.5; }
        .wc-cat-badge { display: inline-block; padding: 0.15rem 0.45rem; border-radius: 2px;
                        font-size: 0.65rem; font-weight: 600; text-transform: uppercase; color: white; margin-right: 0.3rem; }
        .woodcut-detail { max-width: 900px; margin: 2rem auto; padding: 0 2rem; }
        .woodcut-detail h2 { color: var(--accent); margin-bottom: 0.5rem; }
        .woodcut-detail h3 { margin-top: 1.5rem; border-bottom: 1px solid var(--border); padding-bottom: 0.2rem; }
        .woodcut-detail p { line-height: 1.8; }
        .woodcut-detail .wc-image-frame { text-align: center; margin: 1.5rem 0; }
        .woodcut-detail .wc-image-frame img { max-width: 100%; max-height: 700px; border: 1px solid var(--border);
                                               box-shadow: 0 2px 8px rgba(0,0,0,0.1); background: #f5f0e8; }
        .woodcut-detail .wc-image-caption { font-size: 0.8rem; color: var(--text-muted); margin-top: 0.5rem; font-style: italic; }
        .woodcut-detail .cross-links { margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--border); }
        .woodcut-detail .cross-links a { display: inline-block; margin: 0.2rem 0.3rem; padding: 0.2rem 0.6rem;
                                          background: var(--bg); border: 1px solid var(--border); border-radius: 3px;
                                          font-size: 0.85rem; color: var(--text); text-decoration: none; }
        .woodcut-detail .cross-links a:hover { border-color: var(--accent); color: var(--accent); }
        .wc-nav-strip { display: flex; justify-content: space-between; margin: 1.5rem 0; font-size: 0.85rem; }
        .wc-nav-strip a { color: var(--accent); text-decoration: none; }
        .wc-annotation-note { background: var(--bg-card); border-left: 3px solid var(--accent);
                               padding: 0.75rem 1rem; margin: 1rem 0; font-size: 0.9rem; }
        @media (max-width: 768px) {
            .woodcut-grid { grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); }
            .woodcut-card img { height: 240px; }
        }
    """ + '</style>'

    # Build detail pages and collect card HTML
    cards_html = ''
    slugs = []  # For prev/next navigation

    for wc in woodcuts:
        (wid, slug, title, sig, page, ia_page, photo, cat, wtype,
         desc, narrative, context, elements, has_ann, has_alch,
         ann_density, dict_terms, scholarly, influence, source,
         conf, notes, ia_cached) = wc
        slugs.append((slug, title, page))

    for idx, wc in enumerate(woodcuts):
        (wid, slug, title, sig, page, ia_page, photo, cat, wtype,
         desc, narrative, context, elements, has_ann, has_alch,
         ann_density, dict_terms, scholarly, influence, source,
         conf, notes, ia_cached) = wc

        color = cat_colors.get(cat, '#6b7280')
        cat_badge = f'<span class="wc-cat-badge" style="background:{color}">{escape(cat or "")}</span>'
        alch_badge = ' <span class="alchemist-tag">Alchemist</span>' if has_alch else ''

        # Determine image path
        img_filename = f'hp1499_p{page:03d}.jpg'
        img_exists = (ia_img_dir / img_filename).exists()
        img_path = f'../images/woodcuts_1499/{img_filename}' if img_exists else ''

        # Card for index
        img_tag = f'<img src="../images/woodcuts_1499/{img_filename}" alt="{escape(title)}" loading="lazy">' if img_exists else '<div style="height:320px;background:#e8e0d0;display:flex;align-items:center;justify-content:center;color:#999;font-style:italic">Image pending</div>'
        cards_html += f"""
        <div class="woodcut-card" data-category="{escape(cat or '')}">
            <a href="{slug}.html">{img_tag}</a>
            <div class="wc-info">
                <h4><a href="{slug}.html">{escape(title)}</a></h4>
                <div class="wc-meta">{cat_badge} p.{page}{alch_badge}</div>
                <p class="wc-desc">{escape((desc or '')[:120])}{'...' if desc and len(desc) > 120 else ''}</p>
            </div>
        </div>"""

        # Detail page
        # Image
        if img_exists:
            img_html = f"""
            <div class="wc-image-frame">
                <img src="../images/woodcuts_1499/{img_filename}" alt="{escape(title)}">
                <div class="wc-image-caption">From the 1499 Aldine first edition (University of Seville copy, via Internet Archive)</div>
            </div>"""
        else:
            img_html = ''

        # Narrative context (prefer narrative_context, fall back to chapter_context)
        narr = narrative or context or ''
        narr_html = f'<h3>In the Narrative</h3><p>{escape(narr)}</p>' if narr else ''

        desc_html = f'<p>{escape(desc or "")}</p>' if desc else ''
        scholarly_html = f'<h3>In Scholarship</h3><p>{escape(scholarly or "")}</p>' if scholarly else ''
        influence_html = f'<h3>Influence &amp; Reception</h3><p>{escape(influence or "")}</p>' if influence else ''

        # Annotation note (if this page has BL annotations)
        ann_html = ''
        if has_ann or has_alch:
            ann_parts = []
            if has_alch:
                ann_parts.append('alchemical annotations by Hand B')
            if ann_density:
                ann_parts.append(f'{ann_density.lower()} annotation density')
            if photo:
                ann_parts.append(f'BL photograph #{photo}')
            folio_link = f' <a href="../marginalia/{(sig or "").lower()}.html">View folio &rarr;</a>' if (sig or '').lower() in _wc_marg_sigs else ''
            ann_html = f'<div class="wc-annotation-note"><strong>In the BL copy (C.60.o.12):</strong> This page has {", ".join(ann_parts)}.{folio_link}</div>'

        # Cross links
        cross_html = ''
        cross_parts = []
        if dict_terms:
            term_links = ''.join(f'<a href="../dictionary/{t.strip()}.html">{t.strip().replace("-", " ").title()}</a>'
                                  for t in dict_terms.split(',') if t.strip() and t.strip() in _wc_dict_slugs)
            if term_links:
                cross_parts.append(f'<h4>Related Dictionary Terms</h4>{term_links}')
        if sig and sig.lower() in _wc_marg_sigs:
            cross_parts.append(f'<h4>Related Folio</h4><a href="../marginalia/{sig.lower()}.html">Folio {escape(sig)}</a>')
        if cross_parts:
            cross_html = f'<div class="cross-links">{"".join(cross_parts)}</div>'

        # Prev/next navigation
        prev_link = f'<a href="{slugs[idx-1][0]}.html">&larr; {escape(slugs[idx-1][1][:30])}</a>' if idx > 0 else '<span></span>'
        next_link = f'<a href="{slugs[idx+1][0]}.html">{escape(slugs[idx+1][1][:30])} &rarr;</a>' if idx < len(slugs) - 1 else '<span></span>'

        source_label = source or 'unknown'
        detail_body = f"""
        <div class="woodcut-detail">
            <p><a href="index.html">&larr; All Woodcuts</a></p>
            <h2>{escape(title)}</h2>
            <div style="margin-bottom:1rem">{cat_badge} {escape(sig or '')} &middot; p.{page}</div>
            {img_html}
            {desc_html}
            {narr_html}
            {ann_html}
            {scholarly_html}
            {influence_html}
            {cross_html}
            <div class="wc-nav-strip">{prev_link}{next_link}</div>
            <p style="font-size:0.8rem; color:var(--text-muted); border-top:1px solid var(--border); padding-top:0.5rem; margin-top:1rem">
                Source: {escape(source_label)} &middot; {escape(conf or 'DRAFT')}</p>
        </div>"""

        detail_page = page_shell(title, detail_body, active_nav='woodcuts',
                                  extra_css=wc_css, depth=1)
        (wc_dir / f'{slug}.html').write_text(detail_page, encoding='utf-8')

    # Count categories for filter buttons
    cat_counts = {}
    for wc in woodcuts:
        cat = wc[7] or 'UNCATEGORIZED'
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    filter_buttons = '<button class="wc-filter-btn active" onclick="filterWoodcuts(\'ALL\')">All</button>'
    for cat in sorted(cat_counts.keys()):
        color = cat_colors.get(cat, '#6b7280')
        filter_buttons += f'<button class="wc-filter-btn" onclick="filterWoodcuts(\'{cat}\')" style="border-color:{color}">{cat} ({cat_counts[cat]})</button>'

    filter_js = """
    <script>
    function filterWoodcuts(cat) {
        document.querySelectorAll('.wc-filter-btn').forEach(b => b.classList.remove('active'));
        event.target.classList.add('active');
        document.querySelectorAll('.woodcut-card').forEach(card => {
            if (cat === 'ALL' || card.dataset.category === cat) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    }
    </script>"""

    with_images = sum(1 for wc in woodcuts if (ia_img_dir / f'hp1499_p{wc[4]:03d}.jpg').exists())

    index_body = f"""
    <div class="woodcuts-page">
        <h1>Woodcuts of the <em>Hypnerotomachia Poliphili</em></h1>
        <p class="intro">The 1499 Aldine first edition contains approximately 172 woodcut illustrations &mdash;
        the most ambitious visual program of any incunabulum. Their designer remains unidentified,
        though Benedetto Bordon is the most widely proposed candidate. The woodcuts integrate text and
        image with unprecedented sophistication, each composition calibrated to its surrounding typography.
        Images are from the 1499 first edition (University of Seville copy, via Internet Archive).</p>

        <div class="wc-filters">{filter_buttons}</div>

        <p style="font-size:0.8rem; color:var(--text-muted); margin-bottom:1rem">
            Showing {len(woodcuts)} woodcuts &middot; {with_images} with facsimile images</p>

        <div class="woodcut-grid">{cards_html}</div>
    </div>"""

    index_page = page_shell('Woodcuts &mdash; Hypnerotomachia Poliphili', index_body,
                             active_nav='woodcuts', extra_css=wc_css,
                             extra_js=filter_js, depth=1)
    (wc_dir / 'index.html').write_text(index_page, encoding='utf-8')
    print(f"  woodcuts/index.html + {len(woodcuts)} woodcut pages ({with_images} with images)")


# ============================================================
# "The Book" page — narrative summary of the HP
# ============================================================

def build_the_book_page():
    """Generate the-book.html: a narrative walkthrough of the HP for non-specialists."""

    book_css = '<style>' + """
        .book-page { max-width: 850px; margin: 2rem auto; padding: 0 2rem; }
        .book-page h2 { color: var(--accent); margin: 2rem 0 0.5rem; border-bottom: 1px solid var(--border); padding-bottom: 0.3rem; }
        .book-page h3 { margin: 1.5rem 0 0.5rem; }
        .book-page p { line-height: 1.9; margin-bottom: 1rem; }
        .book-page .book-note { background: var(--bg-card); padding: 0.75rem 1rem; border-left: 3px solid var(--accent); margin: 1rem 0; font-size: 0.9rem; color: var(--text-muted); }
        .book-page .cross-links { margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--border); }
        .book-page .cross-links a { display: inline-block; margin: 0.2rem 0.3rem; padding: 0.2rem 0.6rem; background: var(--bg); border: 1px solid var(--border); border-radius: 3px; font-size: 0.85rem; color: var(--text); text-decoration: none; }
        .book-page .cross-links a:hover { border-color: var(--accent); color: var(--accent); }
    """ + '</style>'

    body = """
    <div class="book-page">
        <h1>The Book</h1>

        <p class="book-note">This page summarizes the narrative of the <em>Hypnerotomachia
        Poliphili</em> for readers who have not encountered it before. It is not a scholarly
        analysis but a walkthrough &mdash; a map of the journey Poliphilo takes through
        his dream, with pointers to the woodcuts, places, and characters you will encounter
        on other pages of this site.</p>

        <h2>What the <em>Hypnerotomachia</em> Is</h2>

        <p>The <em>Hypnerotomachia Poliphili</em> &mdash; the title means roughly
        "Poliphilo's struggle of love in a dream" &mdash; was published in Venice in 1499
        by <a href="dictionary/aldus-manutius.html">Aldus Manutius</a>, the most
        celebrated printer of the Renaissance. It is a large folio volume of 234 leaves,
        illustrated with <a href="woodcuts/index.html">172 woodcut illustrations</a>
        of extraordinary refinement. The text is written in a
        <a href="dictionary/macaronic-language.html">macaronic language</a> that mixes
        Italian syntax with Latin vocabulary, Greek loanwords, and invented words &mdash;
        a hybrid tongue that has baffled and delighted readers for five centuries.</p>

        <p>The book tells the story of a young man named
        <a href="dictionary/poliphilo.html">Poliphilo</a> who falls asleep and dreams.
        In his dream, he journeys through ruined classical buildings, elaborate gardens,
        and allegorical landscapes in search of his beloved,
        <a href="dictionary/polia.html">Polia</a>. Along the way he encounters
        queens, nymphs, processions, sacrifices, inscriptions, and monuments &mdash;
        each described in painstaking visual and architectural detail. The dream is
        also a dream within a dream: partway through his journey, Poliphilo falls
        asleep again and enters a deeper vision.</p>

        <p>The author's identity is concealed in an <a href="dictionary/acrostic.html">acrostic</a>
        formed by the chapter initials: POLIAM FRATER FRANCISCVS COLVMNA PERAMAVIT
        ("Brother Francesco Colonna loved Polia greatly"). Which Francesco Colonna &mdash;
        a Venetian Dominican friar, a Roman nobleman, or someone else entirely &mdash;
        remains the subject of a long-running
        <a href="dictionary/authorship-debate.html">authorship debate</a>.</p>

        <h2>The Journey</h2>

        <h3>The Dark Forest</h3>
        <p>The narrative opens with Poliphilo lost in a
        <a href="dictionary/dark-forest.html">dark, terrifying forest</a> &mdash; a
        deliberate echo of Dante's <em>selva oscura</em> at the beginning of the
        <em>Inferno</em>. He is alone, frightened, and disoriented. The
        <a href="russell-alchemical-hands.html#annotated-woodcuts">woodcut of the dark forest</a> establishes
        the visual register that will govern the entire book: dense, precise, and
        atmospheric.</p>

        <p>Poliphilo emerges from the forest into an open landscape and, exhausted,
        falls asleep &mdash; entering the
        <a href="dictionary/dream-within-dream.html">dream within the dream</a>
        that contains the main narrative.</p>

        <h3>The Ruins and the Pyramid</h3>
        <p>In his inner dream, Poliphilo encounters a vast ruined classical complex:
        a <a href="dictionary/ruined-temple.html">great temple</a>, a colossal
        <a href="dictionary/pyramid.html">pyramid</a> surmounted by an
        <a href="dictionary/obelisk.html">obelisk</a>, and monumental gates decorated
        with reliefs and inscriptions. He describes their
        <a href="dictionary/column-orders.html">column orders</a>,
        proportions, and materials with the precision of an architectural treatise.
        This is where the book's reputation as an encyclopedia of classical design
        originates: the ruins are not mere scenery but occasions for sustained
        <a href="dictionary/ekphrasis.html">ekphrasis</a> &mdash; verbal descriptions
        so vivid they rival the woodcut illustrations.</p>

        <p>The most famous image in the book appears here: the
        <a href="russell-alchemical-hands.html#annotated-woodcuts">elephant bearing an obelisk</a>
        (signature b6v), decorated with pseudo-<a href="dictionary/hieroglyph.html">hieroglyphic</a>
        carvings. This image later inspired Bernini's 1667 sculpture in the Piazza della
        Minerva in Rome, commissioned by Pope Alexander VII &mdash; who himself annotated
        his own copy of the HP.</p>

        <h3>Queen Eleuterylida and the Three Gates</h3>
        <p>Poliphilo arrives at the court of <a href="dictionary/eleuterylida.html">Queen
        Eleuterylida</a>, whose name derives from the Greek word for freedom.
        At the <a href="dictionary/thelemia.html">gate of Thelemia</a> (free will),
        he must choose among three doors representing three ways of life: pleasure,
        action, and contemplation. He chooses the middle path.</p>

        <p>The queen's court introduces the
        <a href="dictionary/nymphs-five-senses.html">five nymphs</a> who represent
        the bodily senses: sight, hearing, smell, taste, and touch. They will guide
        Poliphilo through the next stage of his journey.</p>

        <h3>The Nymphs and the Bath</h3>
        <p>The five nymphs bathe Poliphilo in elaborate
        <a href="dictionary/bath-thermae.html">classical thermae</a>, dress him in fine
        garments, and lead him through the queen's palace. These passages combine
        sensory education with erotic initiation &mdash; the nymphs awaken Poliphilo's
        body and mind simultaneously. The architecture of the bath is described with
        attention to water systems, marble surfaces, and spatial arrangement, embodying
        what Liane Lefaivre called the
        <a href="dictionary/architectural-body.html">"architectural body"</a>:
        architecture experienced through the flesh, not through abstract geometry.</p>

        <h3>The Triumphal Processions</h3>
        <p>Poliphilo witnesses a series of elaborate
        <a href="dictionary/triumphal-procession.html">triumphal processions</a>
        featuring chariots drawn by exotic animals, musicians, dancers, and allegorical
        personifications. The <a href="russell-alchemical-hands.html#annotated-woodcuts">procession
        woodcuts</a> are among the most complex in the book. These passages connect the HP
        to Renaissance festival culture and to the classical literary tradition of the
        <em>triumphus</em>. The alchemical annotators later read them as encoding stages
        of the <a href="dictionary/great-work.html">Great Work</a> of transmutation.</p>

        <h3>The Sacrifice to Priapus</h3>
        <p>One of the HP's most explicitly pagan scenes: a
        <a href="dictionary/sacrifice-priapus.html">ritual sacrifice</a> at the altar
        of Priapus, the garden god of fertility. A donkey is offered in a ceremony that
        combines classical sacrificial practice with frank fertility symbolism. Scholarship
        has called this "perhaps the most censored woodcut of the Renaissance."</p>

        <h3>The Voyage to Cythera</h3>
        <p>Poliphilo and Polia travel by boat to
        <a href="dictionary/cythera.html">Cythera</a>, the island sacred to
        <a href="dictionary/venus-aphrodite.html">Venus</a>. The sea crossing represents
        the passage from earthly desire to divine love. On the island, they encounter
        an elaborate <a href="dictionary/circular-garden.html">circular garden</a> with
        concentric rings of planting surrounding Venus's temple &mdash; a cosmological
        design radiating from the goddess at the center outward through successive levels
        of material existence.</p>

        <p>At the temple, <a href="dictionary/cupid-eros.html">Cupid</a> presides over
        the union of Poliphilo and Polia. The consummation of their love is the narrative
        climax of Book I.</p>

        <h3>Book II: Polia Speaks</h3>
        <p>In a remarkable structural move, the HP gives Polia her own voice. Book II
        is narrated by Polia herself, who tells the story of her initial rejection of
        Poliphilo, her resistance to love, and her eventual conversion by Venus. This
        reframing of the love story from the beloved's perspective makes the HP unusual
        among Renaissance love narratives, which typically silence the beloved or reduce
        her to a visual object.</p>

        <h3>The Awakening</h3>
        <p>Poliphilo wakes. Polia dissolves. The dream ends. The reader is returned
        to the waking world that framed the narrative from the beginning. What remains
        is the book itself &mdash; the woodcuts, the language, the architecture, the
        gardens &mdash; and five centuries of readers who have left their marks in its
        margins.</p>

        <h2>The Readers</h2>
        <p>James Russell's 2014 PhD thesis documented the
        <a href="dictionary/marginalia.html">marginalia</a> in six copies of the HP,
        identifying eleven distinct <a href="dictionary/annotator-hand.html">annotator
        hands</a>. What he found overturns the idea that the HP was an unread curiosity.
        The Giovio brothers read it as a botanical compendium. Ben Jonson mined it for
        stage design imagery. Pope Alexander VII collected examples of verbal
        <a href="dictionary/acutezze.html">wit</a>. And two anonymous alchemists,
        working independently in different copies, decoded the love story as an
        <a href="dictionary/alchemical-allegory.html">alchemical allegory</a> &mdash;
        but they disagreed about which kind.</p>

        <p>The BL alchemist (Hand B) followed the framework of Jean d'Espagnet,
        reading the HP as encoding the operations of
        <a href="dictionary/master-mercury.html">Master Mercury</a>. The Buffalo
        alchemist (Hand E) followed pseudo-Geber, reading it through the lens of
        <a href="dictionary/sol-luna.html">Sol and Luna</a> and the
        <a href="dictionary/chemical-wedding.html">chemical wedding</a>. Their
        competing readings are explored in the
        <a href="russell-alchemical-hands.html">Alchemical Hands essay</a>.</p>

        <p>Russell's concept of the HP as a
        <a href="dictionary/activity-book.html">"humanistic activity book"</a> &mdash;
        a text whose puzzles, obscure language, and visual-textual interplay invited
        readers to cultivate <a href="dictionary/ingegno.html"><em>ingegno</em></a>
        (improvisational intelligence) through creative annotation &mdash; is the
        central argument of his thesis and the intellectual foundation of this site.</p>

        <div class="cross-links">
            <h4>Explore Further</h4>
            <a href="marginalia/index.html">Browse the Marginalia</a>
            <a href="woodcuts/index.html">See the Woodcuts</a>
            <a href="dictionary/index.html">Dictionary of Terms</a>
            <a href="russell-alchemical-hands.html">The Alchemical Hands</a>
            <a href="timeline.html">500 Years of Reception</a>
            <a href="scholars.html">The Scholars</a>
            <a href="manuscripts/index.html">The Copies</a>
        </div>
    </div>"""

    page = page_shell('The Book', body, active_nav='thebook', extra_css=book_css)
    (SITE_DIR / 'the-book.html').write_text(page, encoding='utf-8')
    print("  the-book.html")


# ============================================================
# Digital Edition stub page
# ============================================================

def build_digital_edition_page(conn):
    """Generate digital-edition.html — editions of the Hypnerotomachia Poliphili."""
    cur = conn.cursor()

    # Load editions data
    cur.execute("""
        SELECT id, title, year, city, printer_publisher, translator,
               language, edition_type, description, significance,
               woodcut_info, digital_facsimile_url, worldcat_url,
               extant_copies, slug
        FROM editions ORDER BY year
    """)
    editions = cur.fetchall()

    type_labels = {
        'FIRST_EDITION': 'First Edition',
        'REPRINT': 'Reprint',
        'TRANSLATION': 'Translation',
        'ADAPTATION': 'Adaptation',
        'FACSIMILE': 'Facsimile',
        'CRITICAL_EDITION': 'Critical Edition',
        'MODERN_TRANSLATION': 'Modern Translation',
    }
    type_colors = {
        'FIRST_EDITION': '#8b5cf6',
        'REPRINT': '#6366f1',
        'TRANSLATION': '#3b82f6',
        'ADAPTATION': '#ef4444',
        'CRITICAL_EDITION': '#10b981',
        'MODERN_TRANSLATION': '#f59e0b',
    }

    edition_css = '<style>' + """
        .editions-page { max-width: 1000px; margin: 2rem auto; padding: 0 2rem; }
        .editions-page h1 { color: var(--accent); font-size: 1.8rem; }
        .editions-page .intro { max-width: 800px; line-height: 1.8; margin-bottom: 2rem; color: var(--text-muted); }
        .edition-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 6px;
                        padding: 1.5rem; margin-bottom: 1.5rem; transition: box-shadow 0.2s; }
        .edition-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
        .edition-card h3 { margin: 0 0 0.5rem; color: var(--text); font-size: 1.1rem; }
        .edition-card .ed-meta { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.75rem;
                                  font-family: var(--font-sans); }
        .edition-card .ed-type { display: inline-block; padding: 0.15rem 0.5rem; border-radius: 2px;
                                  font-size: 0.65rem; font-weight: 600; text-transform: uppercase;
                                  color: white; margin-right: 0.5rem; }
        .edition-card p { line-height: 1.7; margin: 0.5rem 0; font-size: 0.92rem; }
        .edition-card .ed-significance { border-top: 1px solid var(--border); padding-top: 0.75rem;
                                          margin-top: 0.75rem; }
        .edition-card .ed-significance strong { color: var(--accent); }
        .edition-card .ed-woodcuts { font-size: 0.85rem; color: var(--text-muted); font-style: italic;
                                      margin-top: 0.5rem; }
        .edition-card .ed-links { margin-top: 0.75rem; }
        .edition-card .ed-links a { display: inline-block; margin-right: 0.75rem; padding: 0.3rem 0.7rem;
                                     background: var(--bg); border: 1px solid var(--border); border-radius: 3px;
                                     font-size: 0.8rem; color: var(--accent); text-decoration: none; }
        .edition-card .ed-links a:hover { border-color: var(--accent); background: var(--accent); color: white; }
        .editions-timeline { position: relative; padding-left: 2rem; }
        .editions-timeline::before { content: ''; position: absolute; left: 0.5rem; top: 0; bottom: 0;
                                      width: 2px; background: var(--border); }
        .edition-card::before { content: ''; position: absolute; left: -1.55rem; top: 1.5rem;
                                 width: 10px; height: 10px; border-radius: 50%;
                                 background: var(--accent); border: 2px solid var(--bg); }
        .edition-card { position: relative; }
    """ + '</style>'

    # Build edition cards
    cards = ''
    for ed in editions:
        (eid, title, year, city, printer, translator, lang, etype,
         desc, significance, woodcuts_info, facsimile_url, worldcat_url,
         extant, slug) = ed

        color = type_colors.get(etype, '#6b7280')
        type_label = type_labels.get(etype, etype or '')
        type_badge = f'<span class="ed-type" style="background:{color}">{type_label}</span>'

        meta_parts = [str(year)]
        if city:
            meta_parts.append(escape(city))
        if printer:
            meta_parts.append(escape(printer))

        translator_line = f'<br>Translator: {escape(translator)}' if translator else ''
        lang_line = f' &middot; {escape(lang)}' if lang else ''

        desc_html = f'<p>{escape(desc)}</p>' if desc else ''
        sig_html = f'<div class="ed-significance"><strong>Significance:</strong> {escape(significance)}</div>' if significance else ''
        wc_html = f'<p class="ed-woodcuts">{escape(woodcuts_info)}</p>' if woodcuts_info else ''
        extant_html = f' &middot; {extant} extant copies' if extant else ''

        links = ''
        link_parts = []
        if facsimile_url:
            link_parts.append(f'<a href="{escape(facsimile_url)}" target="_blank">Digital Facsimile &rarr;</a>')
        if worldcat_url:
            link_parts.append(f'<a href="{escape(worldcat_url)}" target="_blank">WorldCat &rarr;</a>')
        if link_parts:
            links = f'<div class="ed-links">{"".join(link_parts)}</div>'

        cards += f"""
        <div class="edition-card">
            <h3>{escape(title)}</h3>
            <div class="ed-meta">{type_badge} {" &middot; ".join(meta_parts)}{lang_line}{extant_html}{translator_line}</div>
            {desc_html}
            {sig_html}
            {wc_html}
            {links}
        </div>"""

    body = f"""
    <div class="editions-page">
        <p><a href="index.html">&larr; Home</a></p>
        <h1>Editions of the <em>Hypnerotomachia Poliphili</em></h1>
        <p class="intro">From its first printing by Aldus Manutius in 1499 to Joscelyn Godwin's
        complete English translation exactly five centuries later, the <em>Hypnerotomachia Poliphili</em>
        has been published, translated, adapted, and reinterpreted across languages, centuries, and
        intellectual traditions. Each edition reflects the concerns of its moment: humanist philology
        in 1499, Mannerist aesthetics in 1546, alchemical hermeneutics in 1600, and scholarly
        archaeology from 1980 onward.</p>

        <div class="editions-timeline">
            {cards}
        </div>
    </div>"""

    page = page_shell('Editions', body, active_nav='edition', extra_css=edition_css)
    (SITE_DIR / 'digital-edition.html').write_text(page, encoding='utf-8')
    print(f"  digital-edition.html ({len(editions)} editions)")


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
# Concordance Browser
# ============================================================

def build_concordance_browser(conn):
    """Generate concordance/index.html — 448-page browser of the 1499 HP."""
    cur = conn.cursor()
    conc_dir = SITE_DIR / 'concordance'
    conc_dir.mkdir(exist_ok=True)
    ia_img_dir = SITE_DIR / 'images' / 'woodcuts_1499'

    # Which signatures have marginalia pages?
    marg_dir = SITE_DIR / 'marginalia'
    marg_sigs = set()
    if marg_dir.exists():
        for f in marg_dir.glob('*.html'):
            if f.stem != 'index':
                marg_sigs.add(f.stem)

    cur.execute("""
        SELECT pc.page_seq, pc.signature, pc.folio_number, pc.side, pc.quire,
               pc.section, pc.has_woodcut, pc.bl_photo_number,
               pc.ia_page_index, pc.notes,
               w.slug as woodcut_slug, w.title as woodcut_title,
               w.subject_category as woodcut_category
        FROM page_concordance pc
        LEFT JOIN woodcuts w ON pc.page_seq = w.page_1499
        ORDER BY pc.page_seq
    """)
    pages = cur.fetchall()

    if not pages:
        print("  concordance: no data")
        return

    section_colors = {
        'PRELIMINARIES': '#6b7280', 'DARK_FOREST': '#065f46', 'PYRAMID_RUINS': '#92400e',
        'DRAGON_PORTAL': '#7c2d12', 'FIVE_SENSES': '#4338ca', 'QUEEN_PALACE': '#7e22ce',
        'JOURNEY_DOORS': '#0369a1', 'PROCESSION': '#b91c1c', 'VENUS_TEMPLE': '#be185d',
        'POLYANDRION': '#374151', 'CYTHERA_VOYAGE': '#0891b2', 'CYTHERA_GARDENS': '#15803d',
        'VENUS_FOUNTAIN': '#9333ea', 'BOOK_II_POLIA': '#78350f', 'COLOPHON': '#6b7280',
    }
    section_labels = {
        'PRELIMINARIES': 'Preliminaries', 'DARK_FOREST': 'Dark Forest',
        'PYRAMID_RUINS': 'Pyramid & Ruins', 'DRAGON_PORTAL': 'Dragon Portal',
        'FIVE_SENSES': 'Five Senses', 'QUEEN_PALACE': "Queen's Palace",
        'JOURNEY_DOORS': 'Journey of the Doors', 'PROCESSION': 'Triumphal Procession',
        'VENUS_TEMPLE': 'Temple of Venus', 'POLYANDRION': 'Polyandrion',
        'CYTHERA_VOYAGE': 'Voyage to Cythera', 'CYTHERA_GARDENS': 'Gardens of Cythera',
        'VENUS_FOUNTAIN': 'Fountain of Venus', 'BOOK_II_POLIA': 'Book II: Polia',
        'COLOPHON': 'Colophon',
    }

    conc_css = '<style>' + """
        .conc-page { max-width: 1100px; margin: 2rem auto; padding: 0 2rem; }
        .conc-page h1 { color: var(--accent); font-size: 1.8rem; margin-bottom: 0.3rem; }
        .conc-page .intro { max-width: 800px; line-height: 1.8; margin-bottom: 1.5rem; color: var(--text-muted); }
        .conc-controls { display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center; margin-bottom: 1.5rem;
                         padding: 0.75rem; background: var(--bg-card); border: 1px solid var(--border); border-radius: 6px; }
        .conc-controls label { font-size: 0.8rem; color: var(--text-muted); cursor: pointer; display: flex; align-items: center; gap: 0.3rem; }
        .conc-controls input[type="checkbox"] { accent-color: var(--accent); }
        .conc-jump { padding: 0.35rem 0.6rem; border: 1px solid var(--border); border-radius: 3px; font-size: 0.85rem;
                     font-family: var(--font-sans); width: 120px; }
        .conc-jump:focus { outline: none; border-color: var(--accent); }
        .conc-stats { font-size: 0.8rem; color: var(--text-muted); margin-left: auto; }
        .conc-section { margin-bottom: 1rem; }
        .conc-section-header { display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 0.75rem;
                                background: var(--bg); border: 1px solid var(--border); border-radius: 4px;
                                cursor: pointer; position: sticky; top: 0; z-index: 5; user-select: none; }
        .conc-section-header:hover { background: var(--bg-card); }
        .conc-section-header .sec-badge { display: inline-block; padding: 0.15rem 0.5rem; border-radius: 2px;
                                           font-size: 0.7rem; font-weight: 600; color: white; text-transform: uppercase; }
        .conc-section-header .sec-label { font-weight: 600; font-size: 0.95rem; }
        .conc-section-header .sec-count { font-size: 0.75rem; color: var(--text-muted); margin-left: auto; }
        .conc-section-header .sec-toggle { font-size: 0.8rem; color: var(--text-muted); transition: transform 0.2s; }
        .conc-section.collapsed .sec-toggle { transform: rotate(-90deg); }
        .conc-section.collapsed .conc-rows { display: none; }
        .conc-rows { border: 1px solid var(--border); border-top: none; border-radius: 0 0 4px 4px; }
        .conc-row { display: flex; align-items: center; gap: 0.5rem; padding: 0.4rem 0.75rem;
                    border-bottom: 1px solid #eee; font-size: 0.82rem; transition: background 0.1s; }
        .conc-row:last-child { border-bottom: none; }
        .conc-row:hover { background: var(--bg); }
        .conc-row.has-wc { background: rgba(139,69,19,0.04); }
        .conc-row .pg { width: 45px; font-weight: 600; color: var(--text); font-family: var(--font-sans); }
        .conc-row .sig { width: 45px; font-family: var(--font-sans); color: var(--accent); }
        .conc-row .folio { width: 55px; color: var(--text-muted); font-family: var(--font-sans); }
        .conc-row .quire-col { width: 30px; color: var(--text-muted); font-family: var(--font-sans); text-align: center; }
        .conc-row .wc-thumb { width: 60px; height: 45px; flex-shrink: 0; }
        .conc-row .wc-thumb img { width: 60px; height: 45px; object-fit: cover; object-position: top;
                                   border: 1px solid var(--border); border-radius: 2px; }
        .conc-row .wc-info { flex: 1; min-width: 0; }
        .conc-row .wc-title { font-size: 0.8rem; color: var(--text); }
        .conc-row .wc-title a { color: var(--text); text-decoration: none; }
        .conc-row .wc-title a:hover { color: var(--accent); }
        .conc-row .wc-cat { font-size: 0.65rem; font-weight: 600; text-transform: uppercase; padding: 0.1rem 0.3rem;
                            border-radius: 2px; color: white; }
        .conc-row .links { display: flex; gap: 0.3rem; flex-shrink: 0; }
        .conc-row .links a { font-size: 0.7rem; padding: 0.15rem 0.4rem; border: 1px solid var(--border);
                              border-radius: 2px; text-decoration: none; color: var(--text-muted); background: var(--bg-card); }
        .conc-row .links a:hover { border-color: var(--accent); color: var(--accent); }
        .conc-row.hidden { display: none; }
        .conc-row.highlight { background: #fef3c7 !important; }
        @media (max-width: 768px) {
            .conc-row .folio, .conc-row .quire-col { display: none; }
            .conc-row .wc-thumb { width: 40px; height: 30px; }
            .conc-row .wc-thumb img { width: 40px; height: 30px; }
        }
    """ + '</style>'

    wc_cat_colors = {
        'ARCHITECTURAL': '#8b5cf6', 'LANDSCAPE': '#10b981', 'NARRATIVE': '#3b82f6',
        'HIEROGLYPHIC': '#f59e0b', 'PROCESSION': '#ef4444', 'DECORATIVE': '#6366f1',
        'PORTRAIT': '#ec4899', 'DIAGRAM': '#14b8a6',
    }

    # Group pages by section
    from collections import OrderedDict
    sections = OrderedDict()
    total_wc = 0
    for row in pages:
        (pg, sig, folio, side, quire, section, has_wc, bl_photo,
         ia_page, notes, wc_slug, wc_title, wc_cat) = row
        if section not in sections:
            sections[section] = []
        sections[section].append(row)
        if has_wc:
            total_wc += 1

    # Build section blocks
    sections_html = ''
    for section, sec_pages in sections.items():
        color = section_colors.get(section, '#6b7280')
        label = section_labels.get(section, section.replace('_', ' ').title())
        wc_in_sec = sum(1 for p in sec_pages if p[6])
        pg_range = f'pp.{sec_pages[0][0]}&ndash;{sec_pages[-1][0]}'

        rows_html = ''
        for (pg, sig, folio, side, quire, sec, has_wc, bl_photo,
             ia_page, notes, wc_slug, wc_title, wc_cat) in sec_pages:

            row_cls = 'conc-row'
            data_attrs = f'data-section="{section}" data-page="{pg}" data-sig="{sig}"'
            if has_wc:
                row_cls += ' has-wc'
                data_attrs += ' data-woodcut="1"'

            # Thumbnail
            thumb_html = '<div class="wc-thumb"></div>'
            if has_wc:
                img_file = f'hp1499_p{pg:03d}.jpg'
                if (ia_img_dir / img_file).exists():
                    thumb_html = f'<div class="wc-thumb"><img src="../images/woodcuts_1499/{img_file}" alt="" loading="lazy"></div>'

            # Woodcut info
            wc_html = '<div class="wc-info"></div>'
            if wc_title and wc_slug:
                # Check if this woodcut's detail page exists (CORPUS_EXTRACTION pages were moved to Alchemical Hands)
                wc_page_exists = (SITE_DIR / 'woodcuts' / f'{wc_slug}.html').exists()
                if wc_page_exists:
                    cat_badge = f'<span class="wc-cat" style="background:{wc_cat_colors.get(wc_cat, "#6b7280")}">{escape(wc_cat or "")}</span> ' if wc_cat else ''
                    wc_html = f'<div class="wc-info"><span class="wc-title"><a href="../woodcuts/{wc_slug}.html">{cat_badge}{escape(wc_title[:50])}</a></span></div>'
                else:
                    # Moved to Alchemical Hands page
                    wc_html = f'<div class="wc-info"><span class="wc-title"><a href="../russell-alchemical-hands.html#annotated-woodcuts" style="color:var(--accent)">{escape(wc_title[:50])}</a></span></div>'
            elif has_wc and not wc_slug:
                wc_html = '<div class="wc-info"><span class="wc-title" style="color:var(--accent)">Annotated woodcut</span></div>'

            # Links
            links = []
            sig_lower = sig.lower() if sig else ''
            if sig_lower in marg_sigs:
                links.append(f'<a href="../marginalia/{sig_lower}.html" title="View marginalia">M</a>')
            if bl_photo:
                bl_file = f'C_60_o_12-{bl_photo:03d}.jpg'
                if (SITE_DIR / 'images' / 'bl' / bl_file).exists():
                    links.append(f'<a href="../images/bl/{bl_file}" title="BL photo #{bl_photo}" target="_blank">BL</a>')
            links_html = f'<div class="links">{"".join(links)}</div>' if links else ''

            rows_html += f"""
            <div class="{row_cls}" {data_attrs} id="p{pg}">
                <span class="pg">p.{pg}</span>
                <span class="sig">{escape(sig or '')}</span>
                <span class="folio">f.{folio}{side}</span>
                <span class="quire-col">{escape(quire or '')}</span>
                {thumb_html}
                {wc_html}
                {links_html}
            </div>"""

        sections_html += f"""
        <div class="conc-section" data-section="{section}">
            <div class="conc-section-header" onclick="toggleSection(this)">
                <span class="sec-badge" style="background:{color}">{escape(label)}</span>
                <span class="sec-label">{pg_range}</span>
                <span class="sec-count">{len(sec_pages)} pages, {wc_in_sec} woodcuts</span>
                <span class="sec-toggle">&#9660;</span>
            </div>
            <div class="conc-rows">{rows_html}</div>
        </div>"""

    # Filter buttons for sections
    sec_buttons = ''
    for section in sections:
        color = section_colors.get(section, '#6b7280')
        label = section_labels.get(section, section)
        sec_buttons += f'<button class="wc-filter-btn" onclick="filterSection(\'{section}\')" style="border-color:{color}">{label}</button> '

    conc_js = """
    <script>
    function toggleSection(header) {
        header.parentElement.classList.toggle('collapsed');
    }
    function filterSection(sec) {
        document.querySelectorAll('.conc-section').forEach(s => {
            if (sec === 'ALL') { s.style.display = ''; }
            else { s.style.display = s.dataset.section === sec ? '' : 'none'; }
        });
        document.querySelectorAll('.wc-filter-btn').forEach(b => b.classList.remove('active'));
        event.target.classList.add('active');
        updateStats();
    }
    function filterWoodcuts(checked) {
        document.querySelectorAll('.conc-row').forEach(r => {
            if (checked && !r.dataset.woodcut) { r.classList.add('hidden'); }
            else { r.classList.remove('hidden'); }
        });
        updateStats();
    }
    function jumpToPage(val) {
        val = val.trim().toLowerCase();
        if (!val) return;
        // Try as page number
        let target = document.getElementById('p' + val);
        // Try as signature
        if (!target) {
            const rows = document.querySelectorAll('.conc-row');
            for (const r of rows) {
                if (r.dataset.sig && r.dataset.sig.toLowerCase() === val) {
                    target = r; break;
                }
            }
        }
        if (target) {
            // Expand section if collapsed
            const sec = target.closest('.conc-section');
            if (sec && sec.classList.contains('collapsed')) {
                sec.classList.remove('collapsed');
            }
            // Show if hidden
            target.classList.remove('hidden');
            // Scroll and highlight
            target.scrollIntoView({ behavior: 'smooth', block: 'center' });
            document.querySelectorAll('.conc-row.highlight').forEach(r => r.classList.remove('highlight'));
            target.classList.add('highlight');
            setTimeout(() => target.classList.remove('highlight'), 3000);
        }
    }
    function updateStats() {
        const visible = document.querySelectorAll('.conc-row:not(.hidden):not([style*="display: none"])');
        const total = document.querySelectorAll('.conc-row');
        const wc = document.querySelectorAll('.conc-row.has-wc:not(.hidden)');
        const el = document.getElementById('conc-stats');
        if (el) el.textContent = visible.length + ' of ' + total.length + ' pages shown';
    }
    document.getElementById('conc-jump')?.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') { jumpToPage(this.value); }
    });
    document.getElementById('wc-only')?.addEventListener('change', function() {
        filterWoodcuts(this.checked);
    });
    </script>"""

    body = f"""
    <div class="conc-page">
        <p><a href="../concordance-method.html">Methodology &amp; Confidence &rarr;</a></p>
        <h1>Page Concordance</h1>
        <p class="intro">All 448 page surfaces of the 1499 Aldine first edition, mapped across three
        numbering systems: sequential page, bibliographic signature (quire + leaf + recto/verso), and
        folio number. Pages with woodcut illustrations show thumbnails from the Internet Archive facsimile
        (University of Seville copy). Links connect to marginalia folios (M) and British Library photographs (BL)
        where available.</p>

        <div class="conc-controls">
            <input type="text" class="conc-jump" id="conc-jump" placeholder="Jump to p.123 or b6v">
            <label><input type="checkbox" id="wc-only"> Woodcut pages only</label>
            <span class="conc-stats" id="conc-stats">{len(pages)} pages, {total_wc} with woodcuts</span>
        </div>

        {sections_html}
    </div>"""

    page_html = page_shell("Page Concordance", body, active_nav='concordance',
                            extra_css=conc_css, extra_js=conc_js, depth=1)
    (conc_dir / 'index.html').write_text(page_html, encoding='utf-8')
    print(f"  concordance/index.html ({len(pages)} pages, {total_wc} woodcuts)")


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
    build_the_book_page()
    build_russell_essay_page(conn)
    build_concordance_essay_page(conn)
    build_digital_edition_page(conn)
    build_timeline_page(conn)
    build_woodcuts_pages(conn)
    build_concordance_browser(conn)
    build_manuscripts_pages(conn)

    conn.close()
    print("\n=== Build Complete ===")


if __name__ == "__main__":
    main()
