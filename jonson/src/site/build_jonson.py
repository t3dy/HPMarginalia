"""Build static HTML pages for the Ben Jonson section.

Generates pages under site/jonson/ that integrate with the HP Marginalia nav.
"""

import json
import sys
from pathlib import Path
from html import escape

JONSON_DIR = Path(__file__).resolve().parent.parent.parent
BASE_DIR = JONSON_DIR.parent
SITE_DIR = BASE_DIR / "site" / "jonson"
EXPORTS = JONSON_DIR / "data" / "exports"

# Import the parent site's nav_html to stay consistent
sys.path.insert(0, str(BASE_DIR / "scripts"))
try:
    from build_site import nav_html as _parent_nav
except ImportError:
    _parent_nav = None


def nav_html(active=''):
    """Generate navigation matching the HP site, with Ben Jonson tab added."""
    prefix = '../'
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
        ('index.html', 'Ben Jonson', 'jonson'),
        (f'{prefix}about.html', 'About', 'about'),
    ]
    items = []
    for href, label, key in links:
        cls = ' class="active"' if key == active else ''
        items.append(f'<a href="{href}"{cls}>{label}</a>')
    return f'<nav class="site-nav">{"".join(items)}</nav>'


def page_shell(title, body, active_nav='jonson', extra_css='', extra_js=''):
    """Generate full HTML page for jonson/ subdirectory (depth=1)."""
    prefix = '../'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(title)} - Ben Jonson &amp; The Alchemist</title>
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
            {nav_html(active_nav)}
        </div>
    </header>
    <main>
{body}
    </main>
    <footer>
        <div class="footer-content">
            <div class="footer-section">
                <h4>Ben Jonson &amp; The Alchemist</h4>
                <p>A digital humanities project presenting Ben Jonson's alchemical world:
                annotated <em>Alchemist</em>, biographical timeline, and James Russell's
                findings on Jonson's annotations in the <em>Hypnerotomachia Poliphili</em>.</p>
            </div>
            <div class="footer-section">
                <h4>Data Provenance</h4>
                <p>Content is extracted from scholarly sources with citations.
                Records marked MANUAL have been hand-verified. Records marked
                LLM_ASSISTED require further review.</p>
            </div>
        </div>
    </footer>
    {extra_js}
</body>
</html>"""


def load_json(filename):
    """Load a JSON file. Supports relative paths from EXPORTS dir."""
    if filename.startswith(".."):
        path = EXPORTS / filename
    else:
        path = EXPORTS / filename
    path = path.resolve()
    if not path.exists():
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_index():
    """Build the Ben Jonson landing page."""
    life_events = load_json("life_events.json")
    annotations = load_json("annotations.json")
    findings = load_json("russell_findings.json")
    structure = load_json("play_structure.json")

    body = f"""
        <section class="intro" style="max-width:800px;margin:3rem auto;padding:0 2rem">
            <h2 style="font-size:1.8rem;margin-bottom:1rem">Ben Jonson &amp; <em>The Alchemist</em></h2>
            <p>This section presents Ben Jonson's relationship to alchemy through three lenses:
            an annotated guide to <em>The Alchemist</em> explaining the play's alchemical
            dimensions; a structured biography drawn from scholarly sources; and James Russell's
            findings on Jonson's annotations in the <em>Hypnerotomachia Poliphili</em>.</p>

            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1.5rem;margin:2rem 0">
                <div style="background:var(--bg-card);padding:1.5rem;border-radius:8px;border:1px solid var(--border)">
                    <h3 style="font-size:1.1rem;margin-bottom:0.5rem"><a href="read.html">Read The Alchemist</a></h3>
                    <p style="font-size:0.95rem;color:var(--text-muted)">{len(structure)} scenes across 5 acts with alchemical summaries</p>
                </div>
                <div style="background:var(--bg-card);padding:1.5rem;border-radius:8px;border:1px solid var(--border)">
                    <h3 style="font-size:1.1rem;margin-bottom:0.5rem"><a href="annotations.html">Alchemical Annotations</a></h3>
                    <p style="font-size:0.95rem;color:var(--text-muted)">{len(annotations)} annotation{'s' if len(annotations) != 1 else ''} on alchemical passages</p>
                </div>
                <div style="background:var(--bg-card);padding:1.5rem;border-radius:8px;border:1px solid var(--border)">
                    <h3 style="font-size:1.1rem;margin-bottom:0.5rem"><a href="life.html">Life of Ben Jonson</a></h3>
                    <p style="font-size:0.95rem;color:var(--text-muted)">{len(life_events)} life event{'s' if len(life_events) != 1 else ''} in chronological order</p>
                </div>
                <div style="background:var(--bg-card);padding:1.5rem;border-radius:8px;border:1px solid var(--border)">
                    <h3 style="font-size:1.1rem;margin-bottom:0.5rem"><a href="russell.html">Jonson's HP Annotations</a></h3>
                    <p style="font-size:0.95rem;color:var(--text-muted)">{len(findings)} finding{'s' if len(findings) != 1 else ''} from James Russell's research</p>
                </div>
            </div>

            <div style="display:flex;gap:1.5rem;margin-top:2rem;flex-wrap:wrap">
                <a href="sources.html" style="color:var(--accent);font-size:0.95rem">Sources &amp; Bibliography &rarr;</a>
                <a href="about.html" style="color:var(--accent);font-size:0.95rem">About the Project &rarr;</a>
            </div>
        </section>
"""
    return page_shell("Ben Jonson & The Alchemist", body)


def build_life_page():
    """Build the Life of Ben Jonson page."""
    events = load_json("life_events.json")
    events.sort(key=lambda e: e.get("date_sort", ""))

    rows = []
    for ev in events:
        citations = ', '.join(
            f'{c["source_id"]} {c.get("page_ref", "")}'.strip()
            for c in ev.get("citations", [])
        )
        cat_badge = f'<span class="confidence-badge confidence-medium">{escape(ev["category"])}</span>'
        notes = f'<p style="font-size:0.85rem;color:var(--text-muted);margin-top:0.5rem"><em>{escape(ev["notes"])}</em></p>' if ev.get("notes") else ''
        rows.append(f"""
            <div style="background:var(--bg-card);padding:1.5rem;border-radius:8px;border:1px solid var(--border);margin-bottom:1rem">
                <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:0.5rem">
                    <h3 style="font-size:1.1rem">{escape(ev["date"])} &mdash; {escape(ev["title"])}</h3>
                    {cat_badge}
                </div>
                <p>{escape(ev["description"])}</p>
                <p style="font-size:0.85rem;color:var(--text-muted);margin-top:0.5rem">Sources: {escape(citations)}</p>
                {notes}
            </div>
        """)

    body = f"""
        <section style="max-width:800px;margin:3rem auto;padding:0 2rem">
            <h2 style="font-size:1.8rem;margin-bottom:0.5rem">Life of Ben Jonson</h2>
            <p style="margin-bottom:2rem;color:var(--text-muted)">{len(events)} events from scholarly sources. This is a seed &mdash; more events will be extracted from the corpus.</p>
            {''.join(rows)}
        </section>
"""
    return page_shell("Life of Ben Jonson", body)


def build_annotations_page():
    """Build the Alchemical Annotations page."""
    annotations = load_json("annotations.json")

    cards = []
    for ann in annotations:
        passage = ann.get("passage", {})
        speaker = f' <span style="color:var(--accent)">({escape(passage.get("speaker", ""))})</span>' if passage.get("speaker") else ''
        loc = f'Act {passage.get("act", "?")}, Scene {passage.get("scene", "?")}, lines {passage.get("line_start", "?")}-{passage.get("line_end", "?")}'

        citations = ', '.join(
            f'{c["source_id"]} {c.get("page_ref", "")}'.strip()
            for c in ann.get("citations", [])
        )

        concept_badge = f'<span class="confidence-badge confidence-high">{escape(ann.get("alchemical_concept", ""))}</span>' if ann.get("alchemical_concept") else ''
        cat_badge = f'<span class="confidence-badge confidence-medium">{escape(ann.get("alchemical_category", ""))}</span>' if ann.get("alchemical_category") else ''

        cards.append(f"""
            <div style="background:var(--bg-card);padding:2rem;border-radius:8px;border:1px solid var(--border);margin-bottom:1.5rem">
                <h3 style="font-size:1.2rem;margin-bottom:0.5rem">{escape(ann["title"])}</h3>
                <p style="font-size:0.9rem;color:var(--text-muted);margin-bottom:1rem">{escape(loc)}{speaker} {concept_badge} {cat_badge}</p>
                <blockquote style="border-left:3px solid var(--accent);padding-left:1rem;margin:1rem 0;font-style:italic">
                    {escape(passage.get("text", ""))}
                </blockquote>
                <p style="margin-bottom:1rem">{escape(ann["explanation"])}</p>
                {'<p style="margin-bottom:1rem"><strong>Cultural context:</strong> ' + escape(ann.get("cultural_context", "")) + '</p>' if ann.get("cultural_context") else ''}
                <p style="font-size:0.85rem;color:var(--text-muted)">Sources: {escape(citations)}</p>
                {'<p style="font-size:0.85rem;color:var(--text-muted);margin-top:0.5rem"><em>' + escape(ann.get("notes", "")) + '</em></p>' if ann.get("notes") else ''}
            </div>
        """)

    body = f"""
        <section style="max-width:800px;margin:3rem auto;padding:0 2rem">
            <h2 style="font-size:1.8rem;margin-bottom:0.5rem">Alchemical Annotations</h2>
            <p style="margin-bottom:2rem;color:var(--text-muted)">Annotations explaining the specifically alchemical dimensions of <em>The Alchemist</em>. {len(annotations)} annotation{'s' if len(annotations) != 1 else ''} so far.</p>
            {''.join(cards)}
        </section>
"""
    return page_shell("Alchemical Annotations", body)


def build_russell_page():
    """Build the Russell Findings showcase page."""
    findings = load_json("russell_findings.json")

    # Group by category
    categories = {}
    for f in findings:
        cat = f.get("category", "other")
        categories.setdefault(cat, []).append(f)

    cat_labels = {
        "ownership": "Ownership & Provenance",
        "signature": "Signature & Motto",
        "hand_characteristics": "Characteristics of Jonson's Hand",
        "reading_practices": "Jonson's Reading Practices",
        "alchemist_links": "Links to The Alchemist",
        "attribution": "Attribution Questions",
    }

    sections = []
    for cat_key in ["signature", "hand_characteristics", "reading_practices", "alchemist_links", "ownership", "attribution"]:
        if cat_key not in categories:
            continue
        label = cat_labels.get(cat_key, cat_key)
        cards = []
        for f in categories[cat_key]:
            citations = ', '.join(
                f'{c["source_id"]} {c.get("page_ref", "")}'.strip()
                for c in f.get("citations", [])
            )
            # Build HP folio cross-reference links
            hp_ref_parts = []
            if f.get("hp_page_ref"):
                hp_ref_parts.append(escape(f["hp_page_ref"]))
            if f.get("hp_folio_sigs"):
                folio_links = ', '.join(
                    f'<a href="../marginalia/{sig}.html" style="color:var(--accent)">{sig}</a>'
                    for sig in f["hp_folio_sigs"]
                )
                hp_ref_parts.append(f'View in HP Marginalia: {folio_links}')
            hp_ref = f'<p style="font-size:0.85rem;color:var(--text-muted)">{" | ".join(hp_ref_parts)}</p>' if hp_ref_parts else ''
            evidence = f'<p style="font-size:0.9rem;margin-top:0.5rem"><strong>Evidence:</strong> {escape(f["evidence"])}</p>' if f.get("evidence") else ''
            notes = f'<p style="font-size:0.85rem;color:var(--text-muted);margin-top:0.5rem"><em>{escape(f["notes"])}</em></p>' if f.get("notes") else ''

            cards.append(f"""
                <div style="background:var(--bg-card);padding:1.5rem;border-radius:8px;border:1px solid var(--border);margin-bottom:1rem">
                    <h4 style="font-size:1.05rem;margin-bottom:0.5rem">{escape(f["title"])}</h4>
                    <p>{escape(f["description"])}</p>
                    {evidence}
                    {hp_ref}
                    <p style="font-size:0.85rem;color:var(--text-muted);margin-top:0.5rem">Sources: {escape(citations)}</p>
                    {notes}
                </div>
            """)

        sections.append(f"""
            <h3 style="font-size:1.3rem;margin:2rem 0 1rem;border-bottom:2px solid var(--border);padding-bottom:0.5rem">{escape(label)}</h3>
            {''.join(cards)}
        """)

    body = f"""
        <section style="max-width:800px;margin:3rem auto;padding:0 2rem">
            <h2 style="font-size:1.8rem;margin-bottom:0.5rem">Jonson's <em>Hypnerotomachia</em> Annotations</h2>
            <p style="margin-bottom:1rem">Findings from James Russell's research on Ben Jonson's annotations
            in the 1545 Aldine <em>Hypnerotomachia Poliphili</em> (British Library C.60.o.12).</p>
            <p style="margin-bottom:2rem;color:var(--text-muted)">{len(findings)} findings across {len(categories)} categories. Based primarily on the Russell &amp; O'Neill presentation.</p>
            {''.join(sections)}
        </section>
"""
    return page_shell("Jonson's HP Annotations", body)


def build_read_page():
    """Build the Read The Alchemist page with act/scene navigation."""
    structure = load_json("play_structure.json")
    annotations = load_json("annotations.json")

    # Build annotation index by act.scene
    ann_index = {}
    for ann in annotations:
        p = ann.get("passage", {})
        key = f"{p.get('act', 0)}.{p.get('scene', 0)}"
        ann_index.setdefault(key, []).append(ann)

    # Group scenes by act
    acts = {}
    for scene in structure:
        acts.setdefault(scene["act"], []).append(scene)

    # TOC
    toc_items = []
    for act_num in sorted(acts.keys()):
        scenes = acts[act_num]
        scene_links = ', '.join(
            f'<a href="#act{act_num}-scene{s["scene"]}" style="color:var(--accent)">{s["scene"]}</a>'
            for s in scenes
        )
        toc_items.append(f'<li><strong>Act {act_num}</strong>: Scenes {scene_links}</li>')

    # Scene cards
    act_sections = []
    for act_num in sorted(acts.keys()):
        scenes = acts[act_num]
        scene_cards = []
        for sc in scenes:
            key = f"{sc['act']}.{sc['scene']}"
            scene_anns = ann_index.get(key, [])
            chars = ', '.join(sc.get("characters", []))

            ann_html = ""
            if scene_anns:
                ann_items = []
                for ann in scene_anns:
                    ann_items.append(f"""
                        <div style="background:var(--bg);padding:1rem;border-radius:6px;margin-top:0.75rem;border-left:3px solid var(--accent)">
                            <strong><a href="annotations.html#{ann['annotation_id']}" style="color:var(--accent)">{escape(ann['title'])}</a></strong>
                            <span class="confidence-badge confidence-high" style="margin-left:0.5rem">{escape(ann.get('alchemical_concept', ''))}</span>
                            <p style="font-size:0.9rem;margin-top:0.3rem">{escape(ann['explanation'][:150])}...</p>
                        </div>
                    """)
                ann_html = f'<div style="margin-top:1rem"><strong style="font-size:0.9rem;color:var(--accent)">Alchemical Annotations ({len(scene_anns)}):</strong>{"".join(ann_items)}</div>'

            alch_content = f'<p style="font-size:0.9rem;margin-top:0.75rem"><strong>Alchemical content:</strong> {escape(sc.get("alchemical_content", ""))}</p>' if sc.get("alchemical_content") else ''

            scene_cards.append(f"""
                <div id="act{sc['act']}-scene{sc['scene']}" style="background:var(--bg-card);padding:1.5rem;border-radius:8px;border:1px solid var(--border);margin-bottom:1rem">
                    <div style="display:flex;justify-content:space-between;align-items:baseline">
                        <h4 style="font-size:1.1rem">Scene {sc['scene']}: {escape(sc['title'])}</h4>
                        <span style="font-size:0.85rem;color:var(--text-muted)">~{sc.get('line_count_approx', '?')} lines</span>
                    </div>
                    <p style="font-size:0.85rem;color:var(--text-muted);margin:0.3rem 0">{escape(sc.get('setting', ''))} | {escape(chars)}</p>
                    <p style="margin-top:0.75rem">{escape(sc['summary'])}</p>
                    {alch_content}
                    {ann_html}
                </div>
            """)

        act_sections.append(f"""
            <h3 style="font-size:1.4rem;margin:2.5rem 0 1rem;border-bottom:2px solid var(--border);padding-bottom:0.5rem">Act {act_num}</h3>
            {''.join(scene_cards)}
        """)

    body = f"""
        <section style="max-width:800px;margin:3rem auto;padding:0 2rem">
            <h2 style="font-size:1.8rem;margin-bottom:0.5rem">Read <em>The Alchemist</em></h2>
            <p style="margin-bottom:1rem">A scene-by-scene guide to Ben Jonson's <em>The Alchemist</em> (1610),
            with summaries highlighting the play's alchemical content and links to detailed annotations.</p>
            <p style="margin-bottom:2rem;font-size:0.9rem;color:var(--text-muted)">
                {len(structure)} scenes across 5 acts. {len(annotations)} alchemical annotations linked.
                Scene summaries describe the alchemical dimensions; a full text edition is planned for Phase 2.
            </p>

            <div style="background:var(--bg-card);padding:1.5rem;border-radius:8px;border:1px solid var(--border);margin-bottom:2rem">
                <h3 style="font-size:1.1rem;margin-bottom:0.75rem">Contents</h3>
                <ol style="padding-left:1.5rem;line-height:2">{''.join(toc_items)}</ol>
            </div>

            {''.join(act_sections)}

            <div style="background:var(--bg-card);padding:1.5rem;border-radius:8px;border:1px solid var(--border);margin-top:2rem">
                <h3 style="font-size:1.1rem;margin-bottom:0.5rem">About This Page</h3>
                <p style="font-size:0.9rem">This is a structural guide, not a full text. Scene summaries focus on alchemical content.
                For the complete text, see the H.C. Hart edition (1903) in our source corpus, or consult a modern
                critical edition such as the Cambridge Ben Jonson or the Revels Plays edition.</p>
            </div>
        </section>
"""
    return page_shell("Read The Alchemist", body)


def build_sources_page():
    """Build the Sources / Bibliography page."""
    sources = load_json("../raw/sources.json")
    annotations = load_json("annotations.json")
    findings = load_json("russell_findings.json")
    events = load_json("life_events.json")

    # Collect all citations
    all_citations = {}
    for record_list in [annotations, findings, events]:
        for record in record_list:
            for cit in record.get("citations", []):
                sid = cit["source_id"]
                all_citations.setdefault(sid, 0)
                all_citations[sid] += 1

    rows = []
    for src in sources:
        count = all_citations.get(src["source_id"], 0)
        focus = ', '.join(src.get("content_focus", []))
        notes = f'<p style="font-size:0.85rem;color:var(--text-muted);margin-top:0.3rem"><em>{escape(src.get("notes", ""))}</em></p>' if src.get("notes") else ''
        rows.append(f"""
            <div style="background:var(--bg-card);padding:1.5rem;border-radius:8px;border:1px solid var(--border);margin-bottom:1rem">
                <h4 style="font-size:1.05rem;margin-bottom:0.3rem">{escape(src['title'])}</h4>
                <p style="font-size:0.9rem;color:var(--text-muted)">{escape(src.get('author', 'Unknown'))} | {escape(src['doc_type'].upper())} | {src.get('page_count', '?')} pages</p>
                <p style="font-size:0.9rem;margin-top:0.5rem">Content focus: {escape(focus)}</p>
                <p style="font-size:0.9rem">Referenced in {count} citation{'s' if count != 1 else ''}</p>
                {notes}
            </div>
        """)

    body = f"""
        <section style="max-width:800px;margin:3rem auto;padding:0 2rem">
            <h2 style="font-size:1.8rem;margin-bottom:0.5rem">Sources &amp; Bibliography</h2>
            <p style="margin-bottom:2rem;color:var(--text-muted)">{len(sources)} source documents in the corpus.</p>
            {''.join(rows)}
        </section>
"""
    return page_shell("Sources & Bibliography", body)


def build_about_page():
    """Build the About the Project page."""
    body = """
        <section style="max-width:800px;margin:3rem auto;padding:0 2rem">
            <h2 style="font-size:1.8rem;margin-bottom:1rem">About the Project</h2>

            <h3 style="margin-top:2rem">Purpose</h3>
            <p>This project presents Ben Jonson's relationship to alchemy through three lenses:</p>
            <ol style="padding-left:1.5rem;margin:1rem 0;line-height:2">
                <li>An <strong>annotated guide to <em>The Alchemist</em></strong> explaining the play's specifically alchemical dimensions &mdash; chemical meanings, alchemical theories, terminology, and symbolic content relevant to alchemy.</li>
                <li>A <strong>structured Life of Ben Jonson</strong> presenting key biographical events in chronological order with citations to scholarly sources.</li>
                <li>A <strong>research showcase</strong> presenting James Russell and James O'Neill's findings on Jonson's annotations in the <em>Hypnerotomachia Poliphili</em> (British Library C.60.o.12, Venice, Aldine Press, 1545).</li>
            </ol>

            <h3 style="margin-top:2rem">Scope</h3>
            <p>This project is intentionally narrow. It does not attempt to be a general edition of <em>The Alchemist</em>, a comprehensive Jonson biography, or a study of Kenelm Digby. The annotations focus on alchemy only &mdash; not on the play's other themes (class, gender, urban life, Puritanism) except where they intersect with alchemical content.</p>

            <h3 style="margin-top:2rem">Source Corpus</h3>
            <p>All content is extracted from five scholarly sources with full citations:</p>
            <ul style="padding-left:1.5rem;margin:1rem 0;line-height:2">
                <li><strong>H.C. Hart's edition of <em>The Alchemist</em></strong> (1903) &mdash; the play text with scholarly notes</li>
                <li><strong>Arden critical reader</strong> (Julian &amp; Ostovich, 2013) &mdash; modern critical essays</li>
                <li><strong>James Mardock, <em>Our Scene is London</em></strong> (2008) &mdash; Jonson's relationship to London</li>
                <li><strong>Stanton Linden, <em>Darke Hierogliphicks</em></strong> &mdash; alchemy in English literature</li>
                <li><strong>Russell &amp; O'Neill presentation</strong> &mdash; Jonson's HP marginalia and the alchemical hand</li>
            </ul>

            <h3 style="margin-top:2rem">Method</h3>
            <p>Source documents were converted to markdown, split into page-level excerpts (491 total), and classified by keyword matching into three categories: Jonson's life, The Alchemist's alchemy, and Jonson's HP annotations. Structured records (life events, alchemical annotations, Russell findings) were hand-crafted from the classified excerpts with citations to specific sources and pages.</p>
            <p>Every record carries provenance: extraction method (MANUAL or LLM_ASSISTED) and confidence level (HIGH, MEDIUM, LOW). No content is presented without a source citation.</p>

            <h3 style="margin-top:2rem">Integration</h3>
            <p>This project is a section of the <a href="../index.html">HP Marginalia</a> website, which presents the wider marginalia, scholarship, and reception history of the 1499 <em>Hypnerotomachia Poliphili</em>. The Ben Jonson section connects to the parent site's documentation of BL C.60.o.12 and the various annotating hands identified by James Russell.</p>

            <h3 style="margin-top:2rem">Limitations</h3>
            <ul style="padding-left:1.5rem;margin:1rem 0;line-height:2">
                <li>The Alchemist text is not yet included as a full reading edition (the OCR of the Hart PDF is too degraded). Scene summaries are provided instead.</li>
                <li>Annotations cover selected passages, not the complete play.</li>
                <li>Life events are extracted from a limited corpus and do not constitute a full biography.</li>
                <li>Digby appears only as context for understanding Jonson's HP copy. The attribution of the alchemical hand to Digby is Russell &amp; O'Neill's hypothesis, not a settled fact.</li>
            </ul>
        </section>
"""
    return page_shell("About the Project", body)


def build_all():
    """Build all Jonson pages."""
    SITE_DIR.mkdir(parents=True, exist_ok=True)

    pages = [
        ("index.html", build_index()),
        ("life.html", build_life_page()),
        ("annotations.html", build_annotations_page()),
        ("russell.html", build_russell_page()),
        ("read.html", build_read_page()),
        ("sources.html", build_sources_page()),
        ("about.html", build_about_page()),
    ]

    for filename, html in pages:
        path = SITE_DIR / filename
        path.write_text(html, encoding='utf-8')
        print(f"  Built {path.relative_to(BASE_DIR)}")

    print(f"\nBuilt {len(pages)} pages in site/jonson/")


if __name__ == "__main__":
    build_all()
