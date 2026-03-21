"""Extract and structure evidence for the two essay pages.

Produces:
- staging/essay_russell.json: evidence for the Russell Alchemical Hands essay
- staging/essay_concordance.json: evidence for the Concordance Methodology essay

All data is retrieved evidence + DB queries. No generated interpretation.
"""

import sqlite3
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"
STAGING_DIR = BASE_DIR / "staging"

import sys
sys.path.insert(0, str(BASE_DIR / "scripts"))
from corpus_search import search_chunks


def build_russell_essay_data():
    """Gather evidence for the Russell Alchemical Hands essay."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    data = {
        'title': "Russell's Research on the Alchemical Hands",
        'source_method': 'CORPUS_EXTRACTION',
        'sections': [],
    }

    # 1. Get all annotator hands, especially alchemists
    cur.execute("""
        SELECT hand_label, manuscript_shelfmark, attribution, is_alchemist,
               school, language, ink_color, date_range, description, interests
        FROM annotator_hands ORDER BY manuscript_shelfmark, hand_label
    """)
    all_hands = [dict(row) for row in cur.fetchall()]
    alchemist_hands = [h for h in all_hands if h['is_alchemist']]

    data['sections'].append({
        'id': 'annotator-hands-overview',
        'title': 'All Annotator Hands in the Corpus',
        'evidence_type': 'DB_QUERY',
        'data': all_hands,
    })

    data['sections'].append({
        'id': 'alchemist-hands',
        'title': 'Alchemist Annotators',
        'evidence_type': 'DB_QUERY',
        'data': alchemist_hands,
    })

    # 2. Get dissertation refs attributed to alchemist hands
    cur.execute("""
        SELECT r.signature_ref, r.thesis_page, r.context_text, r.marginal_text,
               r.chapter_num, r.manuscript_shelfmark,
               h.hand_label, h.attribution, h.school
        FROM dissertation_refs r
        JOIN annotator_hands h ON r.hand_id = h.id
        WHERE h.is_alchemist = 1
        ORDER BY r.thesis_page
    """)
    alchemist_refs = [dict(row) for row in cur.fetchall()]

    data['sections'].append({
        'id': 'alchemist-refs',
        'title': 'Dissertation References to Alchemical Annotations',
        'evidence_type': 'DB_QUERY',
        'count': len(alchemist_refs),
        'data': alchemist_refs[:50],  # cap for file size
    })

    # 3. Get images matched to alchemist refs
    cur.execute("""
        SELECT r.signature_ref, i.filename, COALESCE(i.web_path, i.relative_path) as relative_path,
               m.shelfmark, mat.confidence,
               h.hand_label, h.school
        FROM matches mat
        JOIN dissertation_refs r ON mat.ref_id = r.id
        JOIN images i ON mat.image_id = i.id
        JOIN manuscripts m ON i.manuscript_id = m.id
        JOIN annotator_hands h ON r.hand_id = h.id
        WHERE h.is_alchemist = 1
        ORDER BY mat.confidence DESC, r.signature_ref
    """)
    alchemist_images = [dict(row) for row in cur.fetchall()]

    data['sections'].append({
        'id': 'alchemist-images',
        'title': 'Images Matched to Alchemical Annotations',
        'evidence_type': 'DB_QUERY',
        'count': len(alchemist_images),
        'data': alchemist_images[:30],
    })

    # 4. Search corpus for key alchemical evidence
    searches = [
        ('BL alchemist Hand B', 'Hand B alchemist BL mercury'),
        ('Buffalo alchemist Hand E', 'Hand E Buffalo alchemist Geber'),
        ("d'Espagnet framework", "Espagnet mercury Enchiridion"),
        ('Master Mercury flyleaf', 'Mercury Magisteri flyleaf verus sensus'),
        ('Sol Luna Buffalo', 'Sol Luna gold silver Buffalo chess'),
        ('alchemical ideograms', 'ideogram alchemical symbol sign'),
    ]

    for label, query in searches:
        results = search_chunks(query, top_n=5)
        data['sections'].append({
            'id': f'corpus-{label.lower().replace(" ", "-")}',
            'title': f'Corpus Evidence: {label}',
            'evidence_type': 'CORPUS_SEARCH',
            'query': query,
            'results': [{
                'source_doc': r['source_doc'],
                'section': r['section'],
                'page_refs': r['page_refs'],
                'matched_text': r['matched_text'],
                'relevance_score': r['relevance_score'],
            } for r in results],
        })

    # 5. Match statistics
    cur.execute("""
        SELECT mat.confidence, COUNT(*)
        FROM matches mat
        JOIN dissertation_refs r ON mat.ref_id = r.id
        JOIN annotator_hands h ON r.hand_id = h.id
        WHERE h.is_alchemist = 1
        GROUP BY mat.confidence
    """)
    confidence_dist = {row[0]: row[1] for row in cur.fetchall()}

    data['sections'].append({
        'id': 'confidence-distribution',
        'title': 'Confidence Distribution for Alchemist Matches',
        'evidence_type': 'DB_QUERY',
        'data': confidence_dist,
    })

    conn.close()

    out_path = STAGING_DIR / "essay_russell.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Russell essay data: {out_path}")
    return data


def build_concordance_essay_data():
    """Gather evidence for the Concordance Methodology essay."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    data = {
        'title': 'Concordance Methodology',
        'source_method': 'DETERMINISTIC',
        'sections': [],
    }

    # 1. Manuscript overview
    cur.execute("SELECT * FROM manuscripts")
    manuscripts = [dict(row) for row in cur.fetchall()]
    data['sections'].append({
        'id': 'manuscripts',
        'title': 'Manuscripts in the Corpus',
        'evidence_type': 'DB_QUERY',
        'data': manuscripts,
    })

    # 2. Signature map stats
    cur.execute("SELECT COUNT(*) FROM signature_map")
    sig_count = cur.fetchone()[0]
    cur.execute("SELECT MIN(signature), MAX(signature) FROM signature_map")
    sig_range = cur.fetchone()
    cur.execute("SELECT quire, COUNT(*) FROM signature_map GROUP BY quire ORDER BY quire")
    quire_counts = {row[0]: row[1] for row in cur.fetchall()}

    data['sections'].append({
        'id': 'signature-map',
        'title': 'Signature Map Statistics',
        'evidence_type': 'DB_QUERY',
        'data': {
            'total_signatures': sig_count,
            'range': [sig_range[0], sig_range[1]],
            'quires': quire_counts,
        },
    })

    # 3. Dissertation refs stats
    cur.execute("SELECT COUNT(*) FROM dissertation_refs")
    ref_count = cur.fetchone()[0]
    cur.execute("""
        SELECT ref_type, COUNT(*) FROM dissertation_refs
        GROUP BY ref_type ORDER BY COUNT(*) DESC
    """)
    ref_types = {row[0]: row[1] for row in cur.fetchall()}
    cur.execute("""
        SELECT manuscript_shelfmark, COUNT(*) FROM dissertation_refs
        WHERE manuscript_shelfmark IS NOT NULL
        GROUP BY manuscript_shelfmark ORDER BY COUNT(*) DESC
    """)
    ref_by_ms = {row[0]: row[1] for row in cur.fetchall()}

    data['sections'].append({
        'id': 'dissertation-refs',
        'title': 'Dissertation Reference Extraction',
        'evidence_type': 'DB_QUERY',
        'data': {
            'total_refs': ref_count,
            'by_type': ref_types,
            'by_manuscript': ref_by_ms,
        },
    })

    # 4. Image catalog stats
    cur.execute("SELECT COUNT(*) FROM images")
    img_count = cur.fetchone()[0]
    cur.execute("""
        SELECT m.shelfmark, COUNT(*) FROM images i
        JOIN manuscripts m ON i.manuscript_id = m.id
        GROUP BY m.shelfmark
    """)
    img_by_ms = {row[0]: row[1] for row in cur.fetchall()}
    cur.execute("""
        SELECT page_type, COUNT(*) FROM images
        GROUP BY page_type ORDER BY COUNT(*) DESC
    """)
    img_by_type = {row[0]: row[1] for row in cur.fetchall()}

    data['sections'].append({
        'id': 'image-catalog',
        'title': 'Image Catalog Statistics',
        'evidence_type': 'DB_QUERY',
        'data': {
            'total_images': img_count,
            'by_manuscript': img_by_ms,
            'by_type': img_by_type,
        },
    })

    # 5. Match statistics
    cur.execute("SELECT COUNT(*) FROM matches")
    match_count = cur.fetchone()[0]
    cur.execute("""
        SELECT confidence, COUNT(*) FROM matches
        GROUP BY confidence ORDER BY COUNT(*) DESC
    """)
    match_conf = {row[0]: row[1] for row in cur.fetchall()}
    cur.execute("""
        SELECT match_method, COUNT(*) FROM matches
        GROUP BY match_method ORDER BY COUNT(*) DESC
    """)
    match_methods = {row[0]: row[1] for row in cur.fetchall()}

    # BL vs Siena breakdown
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

    data['sections'].append({
        'id': 'matching-stats',
        'title': 'Matching Pipeline Statistics',
        'evidence_type': 'DB_QUERY',
        'data': {
            'total_matches': match_count,
            'by_confidence': match_conf,
            'by_method': match_methods,
            'by_manuscript_and_confidence': ms_conf,
        },
    })

    # 6. Hand attribution stats
    cur.execute("SELECT COUNT(*) FROM annotator_hands")
    hand_count = cur.fetchone()[0]
    cur.execute("""
        SELECT hand_label, manuscript_shelfmark, attribution, is_alchemist
        FROM annotator_hands ORDER BY manuscript_shelfmark
    """)
    hands = [dict(row) for row in cur.fetchall()]

    data['sections'].append({
        'id': 'hand-attribution',
        'title': 'Hand Attribution Data',
        'evidence_type': 'DB_QUERY',
        'data': {
            'total_hands': hand_count,
            'hands': hands,
        },
    })

    conn.close()

    out_path = STAGING_DIR / "essay_concordance.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Concordance essay data: {out_path}")
    return data


if __name__ == "__main__":
    print("=== Building Essay Data ===\n")
    STAGING_DIR.mkdir(exist_ok=True)
    build_russell_essay_data()
    build_concordance_essay_data()
    print("\nDone.")
