"""
Build the Digby static website from database content.

Produces 8 HTML pages in site/:
- digby_home.html
- life_works.html
- memoir.html
- pirate.html
- alchemist.html
- courtier.html
- hypnerotomachia.html
- sources.html
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.db import init_db, query_all, get_connection

# Output to both local site/ AND main project site/digby/
DIGBY_DIR = Path(PROJECT_ROOT)
BASE_DIR = DIGBY_DIR.parent.parent  # hypnerotomachia polyphili/
LOCAL_SITE_DIR = os.path.join(PROJECT_ROOT, "site")
MAIN_SITE_DIR = str(BASE_DIR / "site" / "digby")

for d in [LOCAL_SITE_DIR, MAIN_SITE_DIR]:
    os.makedirs(d, exist_ok=True)


# --- Main site nav (matching HP Marginalia) ---

def site_nav_html(active='digby'):
    """Generate HP Marginalia top-level navigation with Digby active."""
    prefix = '../'
    links = [
        (f'{prefix}index.html', 'Home', 'home'),
        (f'{prefix}marginalia/index.html', 'Marginalia', 'marginalia'),
        (f'{prefix}scholars.html', 'Scholars', 'scholars'),
        (f'{prefix}bibliography.html', 'Bibliography', 'bibliography'),
        (f'{prefix}dictionary/index.html', 'Dictionary', 'dictionary'),
        (f'{prefix}the-book.html', 'The Book', 'thebook'),
        (f'{prefix}timeline.html', 'Timeline', 'timeline'),
        (f'{prefix}woodcuts/index.html', 'Woodcuts', 'woodcuts'),
        (f'{prefix}manuscripts/index.html', 'Manuscripts', 'manuscripts'),
        (f'{prefix}digital-edition.html', 'Editions', 'edition'),
        (f'{prefix}russell-alchemical-hands.html', 'Alchemical Hands', 'russell'),
        (f'{prefix}concordance/index.html', 'Concordance', 'concordance'),
        (f'{prefix}jonson/index.html', 'Ben Jonson', 'jonson'),
        ('index.html', 'Digby', 'digby'),
        (f'{prefix}about.html', 'About', 'about'),
    ]
    items = []
    for href, label, key in links:
        cls = ' class="active"' if key == active else ''
        items.append(f'<a href="{href}"{cls}>{label}</a>')
    return f'<nav class="site-nav">{"".join(items)}</nav>'


# --- Digby sub-nav ---

def digby_subnav_html(active_tab: str = "") -> str:
    tabs = [
        ("index.html", "Digby Home"),
        ("life_works.html", "Life & Works"),
        ("memoir.html", "Memoir"),
        ("pirate.html", "Pirate"),
        ("alchemist.html", "Alchemist"),
        ("courtier.html", "Courtier"),
        ("hypnerotomachia.html", "Digby & the HP"),
        ("sources.html", "Sources"),
    ]
    nav_items = []
    for href, label in tabs:
        active = ' class="active"' if href == active_tab else ""
        nav_items.append(f'<a href="{href}"{active}>{label}</a>')
    return "\n        ".join(nav_items)


def html_head(title: str, active_tab: str = "") -> str:
    subnav = digby_subnav_html(active_tab)
    prefix = '../'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Sir Kenelm Digby</title>
    <link rel="stylesheet" href="{prefix}style.css">
    <style>
        .digby-subnav {{
            background: #5a3a28;
            padding: 0.4rem 2rem;
            display: flex;
            flex-wrap: wrap;
            gap: 0.3rem;
        }}
        .digby-subnav a {{
            color: #e8dcc8;
            text-decoration: none;
            padding: 0.3rem 0.7rem;
            border-radius: 3px;
            font-size: 0.85rem;
            transition: background 0.2s;
        }}
        .digby-subnav a:hover, .digby-subnav a.active {{
            background: #6b4226;
            color: #fff;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
        }}
        h1 {{
            font-size: 2rem;
            color: #6b4226;
            margin-bottom: 0.5rem;
            border-bottom: 2px solid #d4c5a9;
            padding-bottom: 0.5rem;
        }}
        h2 {{
            font-size: 1.4rem;
            color: #6b4226;
            margin: 2rem 0 0.8rem;
        }}
        h3 {{
            font-size: 1.1rem;
            margin: 1.2rem 0 0.5rem;
            color: #4a3520;
        }}
        .subtitle {{
            font-style: italic;
            color: #666;
            margin-bottom: 2rem;
        }}
        .card {{
            background: #fff;
            border: 1px solid #d4c5a9;
            border-radius: 6px;
            padding: 1.2rem 1.5rem;
            margin: 1rem 0;
        }}
        .card h3 {{
            margin-top: 0;
            color: #6b4226;
        }}
        .card .meta {{
            font-size: 0.85rem;
            color: #888;
            margin: 0.3rem 0 0.8rem;
        }}
        .tag {{
            display: inline-block;
            background: #6b4226;
            color: #fff;
            padding: 0.15rem 0.5rem;
            border-radius: 3px;
            font-size: 0.75rem;
            margin-right: 0.3rem;
        }}
        .tag.medium {{ background: #b8860b; }}
        .tag.draft {{ background: #999; }}
        .evidence {{
            background: #f5f0e6;
            border-left: 3px solid #6b4226;
            padding: 0.8rem 1rem;
            margin: 0.8rem 0;
            font-size: 0.9rem;
        }}
        .citation {{
            font-size: 0.8rem;
            color: #888;
            font-style: italic;
            margin-top: 0.5rem;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }}
        th, td {{
            padding: 0.6rem 0.8rem;
            text-align: left;
            border-bottom: 1px solid #d4c5a9;
        }}
        th {{
            background: #3d2b1f;
            color: #f0e6d2;
            font-weight: normal;
        }}
        .significance {{
            font-style: italic;
            color: #555;
            margin-top: 0.5rem;
        }}
        .prose-section {{
            margin: 1.5rem 0;
            line-height: 1.8;
        }}
        .prose-section p {{
            margin-bottom: 1rem;
            text-align: justify;
        }}
        .prose-section h2 {{
            margin-top: 2.5rem;
        }}
        .phase-header {{
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #d4c5a9;
            color: #6b4226;
            font-size: 1.15rem;
        }}
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <h1><a href="{prefix}index.html" style="color:inherit;text-decoration:none">Alchemical Hands in the <em>Hypnerotomachia Poliphili</em></a></h1>
            <p class="subtitle">Marginalia, Scholarship &amp; Reception</p>
            {site_nav_html()}
        </div>
    </header>
    <div class="digby-subnav">
        {subnav}
    </div>
    <div class="container">
"""


def html_foot() -> str:
    return f"""
    </div>
    <footer>
        <div class="footer-content">
            Sir Kenelm Digby (1603&ndash;1665) &middot; HP Marginalia Project
            &middot; Generated {datetime.now().strftime('%Y-%m-%d')}
        </div>
    </footer>
</body>
</html>"""


def escape(text: str) -> str:
    if not text:
        return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def get_citation_text(cit_ids: str, citations: dict) -> str:
    if not cit_ids:
        return ""
    parts = []
    for cid in cit_ids.split(","):
        cid = cid.strip()
        if cid in citations:
            c = citations[cid]
            src = c.get("source_document_id", "")
            loc = c.get("page_or_location", "")
            parts.append(f"{src}: {loc}" if loc else src)
    if parts:
        return '<div class="citation">Sources: ' + "; ".join(parts) + "</div>"
    return ""


def get_page_sections(page: str) -> list[dict]:
    """Query page_sections for a given page, ordered by position."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM page_sections WHERE page = ? ORDER BY position",
        (page,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def render_section(section: dict, citations_dict: dict) -> str:
    """Render a page_section as HTML."""
    title = section.get("title", "")
    body = section.get("body", "")
    cit = get_citation_text(section.get("citation_ids"), citations_dict)
    html = ""
    if title:
        html += f'<h2>{escape(title)}</h2>\n'
    # Body is pre-formatted HTML-safe prose (paragraphs separated by newlines)
    for para in body.split("\n\n"):
        para = para.strip()
        if para:
            html += f"<p>{para}</p>\n"
    if cit:
        html += cit + "\n"
    return f'<div class="prose-section">\n{html}</div>\n'


def render_sections_by_key(sections: list[dict], key: str, citations_dict: dict) -> str:
    """Render all sections matching a given section_key."""
    html = ""
    for s in sections:
        if s.get("section_key") == key:
            html += render_section(s, citations_dict)
    return html


def render_card(title, body, meta="", citation_html="", significance="", tags=None):
    tag_html = ""
    if tags:
        tag_html = " ".join(f'<span class="tag">{t}</span>' for t in tags)
    sig_html = f'<p class="significance">{escape(significance)}</p>' if significance else ""
    return f"""<div class="card">
    <h3>{escape(title)}</h3>
    {f'<div class="meta">{escape(meta)} {tag_html}</div>' if meta or tag_html else ''}
    <p>{body}</p>
    {sig_html}
    {citation_html}
</div>"""


# --- Page Builders ---

def build_home(citations_dict):
    events = query_all("life_events")
    works = query_all("work_records")
    sections = get_page_sections("home")
    html = html_head("Home", "index.html")
    html += """
        <h1>Sir Kenelm Digby (1603-1665)</h1>
        <p class="subtitle">Pirate, Alchemist, Natural Philosopher, Courtier, Bibliophile</p>"""

    # Render intro section from DB if available, otherwise use default
    intro_html = render_sections_by_key(sections, "intro", citations_dict)
    if intro_html:
        html += intro_html
    else:
        html += """
        <p>Sir Kenelm Digby was one of the most remarkable Englishmen of the seventeenth century:
        a trusted advisor to King Charles I, a pioneering natural philosopher, a daring privateer,
        a committed alchemist, a Catholic in a Protestant nation, and a man whose life spanned
        the most turbulent decades of early modern English history.</p>

        <p>This section of the HP Marginalia project presents Digby's life, works, and significance,
        with particular attention to his connection to the <em>Hypnerotomachia Poliphili</em> as
        a possible alchemical annotator of the text.</p>"""

    # Render "why digby matters" section if available
    html += render_sections_by_key(sections, "significance", citations_dict)

    html += """
        <h2>Explore</h2>
        <div class="card">
            <h3><a href="life_works.html">Life & Works</a></h3>
            <p>Chronological biography, major works, intellectual profile.</p>
        </div>
        <div class="card">
            <h3><a href="memoir.html">Memoir Summary</a></h3>
            <p>Episode-by-episode summary of Digby's <em>Private Memoirs</em>.</p>
        </div>
        <div class="card">
            <h3><a href="pirate.html">Pirate</a></h3>
            <p>Voyages, privateering, the Battle of Scanderoon.</p>
        </div>
        <div class="card">
            <h3><a href="alchemist.html">Alchemist & Natural Philosopher</a></h3>
            <p>The Powder of Sympathy, alchemical experiments, natural philosophical theories.</p>
        </div>
        <div class="card">
            <h3><a href="courtier.html">Courtier & Legal Thinker</a></h3>
            <p>Court life, patronage, the Petition of Right.</p>
        </div>
        <div class="card">
            <h3><a href="hypnerotomachia.html">Digby & the Hypnerotomachia</a></h3>
            <p>Russell's research on Digby as the alchemical annotator of the HP.</p>
        </div>
        <div class="card">
            <h3><a href="sources.html">Sources & Bibliography</a></h3>
            <p>Complete source corpus for this section.</p>
        </div>
    """
    html += f"""
        <h2>Key Facts</h2>
        <table>
            <tr><th>Item</th><th>Count</th></tr>
            <tr><td>Life Events</td><td>{len(events)}</td></tr>
            <tr><td>Works</td><td>{len(works)}</td></tr>
        </table>
    """
    html += html_foot()
    return html


LIFE_PHASES = [
    ("youth", "Youth and Education (1603-1620)"),
    ("education", "Youth and Education (1603-1620)"),
    ("grand_tour", "Grand Tour (1620-1623)"),
    ("early_career", "Early Career and Marriage (1623-1627)"),
    ("marriage", "Early Career and Marriage (1623-1627)"),
    ("voyage", "The Mediterranean Voyage (1627-1629)"),
    ("return", "Return and Settled Life (1629-1633)"),
    ("intellectual_life", "Return and Settled Life (1629-1633)"),
    ("career", "Return and Settled Life (1629-1633)"),
    ("grief", "Grief and Alchemy (1633-1640)"),
    ("mourning", "Grief and Alchemy (1633-1640)"),
    ("civil_war", "Civil War and Exile (1640-1660)"),
    ("exile", "Civil War and Exile (1640-1660)"),
    ("restoration", "The Restoration and Final Years (1660-1665)"),
    ("death", "The Restoration and Final Years (1660-1665)"),
]
PHASE_ORDER = {phase: i for i, (phase, _) in enumerate(LIFE_PHASES)}
PHASE_LABELS = dict(LIFE_PHASES)


def build_life_works(citations_dict):
    events = sorted(query_all("life_events"), key=lambda e: e.get("year") or 0)
    works = sorted(query_all("work_records"), key=lambda w: w.get("year") or 0)
    sections = get_page_sections("life_works")
    html = html_head("Life & Works", "life_works.html")
    html += "<h1>Life & Works</h1>"
    html += '<p class="subtitle">A chronological overview of Digby\'s life and major writings</p>'

    # Intro section
    html += render_sections_by_key(sections, "intro", citations_dict)

    html += "<h2>Life Events</h2>"

    # Group events by life_phase and render with phase headers
    current_phase_label = None
    for evt in events:
        phase = evt.get("life_phase", "")
        phase_label = PHASE_LABELS.get(phase, "")
        if phase_label and phase_label != current_phase_label:
            current_phase_label = phase_label
            html += f'<h3 class="phase-header">{phase_label}</h3>'
            # Render phase-specific section if available
            phase_key = f"phase_{phase}"
            html += render_sections_by_key(sections, phase_key, citations_dict)

        tags = []
        if evt.get("confidence"):
            tags.append(evt["confidence"])
        cit = get_citation_text(evt.get("citation_ids"), citations_dict)
        html += render_card(
            evt["title"],
            escape(evt.get("description", "")),
            meta=evt.get("date_display", ""),
            citation_html=cit,
            tags=tags,
        )

    html += "<h2>Major Works</h2>"
    html += render_sections_by_key(sections, "works_intro", citations_dict)

    for w in works:
        year = f"({w['year']})" if w.get("year") else ""
        wtype = f" [{w['work_type']}]" if w.get("work_type") else ""
        cit = get_citation_text(w.get("citation_ids"), citations_dict)
        html += render_card(
            f"{w['title']} {year}",
            escape(w.get("description", "")),
            meta=f"{wtype}",
            citation_html=cit,
            significance=w.get("significance"),
        )

    html += html_foot()
    return html


def build_memoir(citations_dict):
    episodes = sorted(query_all("memoir_episodes"),
                      key=lambda e: e.get("episode_number") or 0)
    sections = get_page_sections("memoir")
    html = html_head("Memoir Summary", "memoir.html")
    html += "<h1>Memoir Summary</h1>"
    html += '<p class="subtitle">Structured summary of Digby\'s <em>Private Memoirs</em></p>'

    # Intro section from DB or default
    intro_html = render_sections_by_key(sections, "intro", citations_dict)
    if intro_html:
        html += intro_html
    else:
        html += "<p>Digby wrote his memoirs in the third person, casting himself as 'Theagenes' and his wife Venetia Stanley as 'Stelliana', in a style modelled on the Greek romance of Heliodorus.</p>"

    # Structure essay if available
    html += render_sections_by_key(sections, "structure", citations_dict)

    for ep in episodes:
        details = []
        if ep.get("key_events"):
            details.append(f"<strong>Key events:</strong> {escape(ep['key_events'])}")
        if ep.get("people"):
            details.append(f"<strong>People:</strong> {escape(ep['people'])}")
        if ep.get("places"):
            details.append(f"<strong>Places:</strong> {escape(ep['places'])}")
        detail_html = "<br>".join(details)
        cit = get_citation_text(ep.get("citation_ids"), citations_dict)
        body = f"<p>{escape(ep.get('summary', ''))}</p>"
        if detail_html:
            body += f'<div class="evidence">{detail_html}</div>'
        html += f"""<div class="card">
    <h3>Episode {ep.get('episode_number', '?')}: {escape(ep['title'])}</h3>
    <div class="meta">{escape(ep.get('date_display', ''))}</div>
    {body}
    {cit}
</div>"""

    # Conclusion section
    html += render_sections_by_key(sections, "conclusion", citations_dict)

    html += html_foot()
    return html


def render_theme_card(r: dict, citations_dict: dict) -> str:
    """Render a single digby_theme_record as an HTML card."""
    details = []
    if r.get("key_details"):
        details.append(escape(r["key_details"]))
    if r.get("people"):
        details.append(f"<strong>People:</strong> {escape(r['people'])}")
    if r.get("places"):
        details.append(f"<strong>Places:</strong> {escape(r['places'])}")
    detail_html = ""
    if details:
        detail_html = '<div class="evidence">' + "<br>".join(details) + "</div>"

    tags = []
    if r.get("confidence"):
        tags.append(r["confidence"])
    cit = get_citation_text(r.get("citation_ids"), citations_dict)
    sig = r.get("significance", "")

    return f"""<div class="card">
    <h3>{escape(r['title'])}</h3>
    <div class="meta">{escape(r.get('date_display', ''))} {' '.join(f'<span class="tag">{t}</span>' for t in tags)}</div>
    <p>{escape(r.get('summary', ''))}</p>
    {detail_html}
    {f'<p class="significance">{escape(sig)}</p>' if sig else ''}
    {cit}
</div>"""


def build_theme_page(theme_value, page_title, subtitle, filename, citations_dict,
                     page_key=None):
    conn = get_connection()
    records = conn.execute(
        "SELECT * FROM digby_theme_records WHERE theme = ? ORDER BY year, date_display",
        (theme_value,)
    ).fetchall()
    conn.close()
    records = [dict(r) for r in records]

    # Determine page key for sections lookup
    if page_key is None:
        page_key = filename.replace(".html", "")
    sections = get_page_sections(page_key)

    html = html_head(page_title, filename)
    html += f"<h1>{page_title}</h1>"
    html += f'<p class="subtitle">{subtitle}</p>'

    # Render intro sections
    html += render_sections_by_key(sections, "intro", citations_dict)

    # Render pre-cards essay sections
    html += render_sections_by_key(sections, "context", citations_dict)

    # Render records
    if records:
        for r in records:
            html += render_theme_card(r, citations_dict)
    else:
        html += "<p><em>No records yet. Content will be added as sources are processed.</em></p>"

    # Render post-cards essay sections
    html += render_sections_by_key(sections, "essay", citations_dict)

    # Render conclusion
    html += render_sections_by_key(sections, "conclusion", citations_dict)

    html += html_foot()
    return html


def build_hypnerotomachia(citations_dict):
    findings = query_all("hypnerotomachia_findings")
    evidence = query_all("hypnerotomachia_evidence")
    sections = get_page_sections("hypnerotomachia")
    # Index evidence by finding_id
    ev_by_finding = {}
    for e in evidence:
        fid = e.get("finding_id", "")
        ev_by_finding.setdefault(fid, []).append(e)

    html = html_head("Digby & the Hypnerotomachia", "hypnerotomachia.html")
    html += "<h1>Digby and the Hypnerotomachia</h1>"
    html += '<p class="subtitle">The case for Kenelm Digby as the alchemical annotator of the <em>Hypnerotomachia Poliphili</em></p>'

    # Intro section from DB or default
    intro_html = render_sections_by_key(sections, "intro", citations_dict)
    if intro_html:
        html += intro_html
    else:
        html += """<h2>Overview</h2>
    <p>An annotated copy of the 1499 <em>Hypnerotomachia Poliphili</em> contains marginalia from
    several distinct hands. One hand is characterized by alchemical symbolic markings, Latin notes,
    and attention to alchemical allegory in both text and images. James Russell's research argues
    that this 'alchemical hand' can be attributed to Sir Kenelm Digby, based on conceptual
    parallels with Digby's known writings, historical plausibility, and the alignment of the
    annotations with Digby's alchemical theories.</p>
    """

    # Methodology section if available
    html += render_sections_by_key(sections, "methodology", citations_dict)

    html += "<h2>Findings</h2>"
    for f in findings:
        tags = []
        if f.get("confidence"):
            tags.append(f["confidence"])
        if f.get("review_status"):
            tags.append(f["review_status"])

        cit = get_citation_text(f.get("citation_ids"), citations_dict)

        # Related concepts
        concepts = ""
        if f.get("related_concepts"):
            concepts = f'<p><strong>Related concepts:</strong> {escape(f["related_concepts"])}</p>'

        # Evidence
        ev_html = ""
        fid = f.get("id", "")
        if fid in ev_by_finding:
            ev_items = []
            for e in ev_by_finding[fid]:
                ev_items.append(f"""<div class="evidence">
    <p>{escape(e.get('excerpt', ''))}</p>
    <div class="citation">Source: {escape(e.get('source', ''))}
    {f" ({escape(e.get('page_or_location', ''))})" if e.get('page_or_location') else ''}</div>
    {f'<p><em>{escape(e.get("notes", ""))}</em></p>' if e.get("notes") else ''}
</div>""")
            ev_html = "<h4>Supporting Evidence</h4>" + "\n".join(ev_items)

        html += f"""<div class="card">
    <h3>{escape(f['title'])}</h3>
    <div class="meta">{' '.join(f'<span class="tag">{t}</span>' for t in tags)}</div>
    <p><strong>Claim:</strong> {escape(f.get('claim', ''))}</p>
    <p>{escape(f.get('description', ''))}</p>
    {concepts}
    {f'<p class="significance">{escape(f.get("significance", ""))}</p>' if f.get("significance") else ''}
    {ev_html}
    {cit}
</div>"""

    # Implications section
    html += render_sections_by_key(sections, "implications", citations_dict)
    html += render_sections_by_key(sections, "conclusion", citations_dict)

    html += html_foot()
    return html


def build_sources(citations_dict):
    docs = sorted(query_all("source_documents"), key=lambda d: d.get("year") or 9999)
    sections = get_page_sections("sources")
    html = html_head("Sources & Bibliography", "sources.html")
    html += "<h1>Sources & Bibliography</h1>"
    html += f'<p class="subtitle">{len(docs)} source documents in the Digby corpus</p>'

    # Intro prose
    html += render_sections_by_key(sections, "intro", citations_dict)
    html += render_sections_by_key(sections, "primary", citations_dict)

    html += """<table>
    <tr>
        <th>Title</th>
        <th>Author</th>
        <th>Year</th>
        <th>Type</th>
        <th>Journal</th>
    </tr>"""

    for d in docs:
        html += f"""<tr>
        <td>{escape(d.get('title', ''))}</td>
        <td>{escape(d.get('author', '') or '')}</td>
        <td>{d.get('year', '') or ''}</td>
        <td><span class="tag">{d.get('file_type', '')}</span></td>
        <td>{escape(d.get('journal', '') or '')}</td>
    </tr>"""

    html += "</table>"
    html += html_foot()
    return html


def build_all():
    """Build all site pages."""
    init_db()

    # Load citations for cross-referencing
    cits = query_all("citations")
    citations_dict = {c["id"]: c for c in cits}

    pages = {
        "index.html": build_home(citations_dict),
        "life_works.html": build_life_works(citations_dict),
        "memoir.html": build_memoir(citations_dict),
        "pirate.html": build_theme_page(
            "pirate", "Digby the Pirate",
            "Voyages, privateering, and the maritime career of Sir Kenelm Digby",
            "pirate.html", citations_dict),
        "alchemist.html": build_theme_page(
            "alchemist_natural_philosopher",
            "Digby the Alchemist & Natural Philosopher",
            "Theories, experiments, and the Powder of Sympathy",
            "alchemist.html", citations_dict),
        "courtier.html": build_theme_page(
            "courtier_legal_thinker",
            "Digby the Courtier & Legal Thinker",
            "Court life, patronage, politics, and constitutional thought",
            "courtier.html", citations_dict),
        "hypnerotomachia.html": build_hypnerotomachia(citations_dict),
        "sources.html": build_sources(citations_dict),
    }

    # Write to both local site/ and main project site/digby/
    for out_dir in [LOCAL_SITE_DIR, MAIN_SITE_DIR]:
        for filename, content in pages.items():
            path = os.path.join(out_dir, filename)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        print(f"  Built {len(pages)} pages in {out_dir}/")

    print(f"\nTotal: {len(pages)} pages deployed to 2 locations.")


if __name__ == "__main__":
    build_all()
