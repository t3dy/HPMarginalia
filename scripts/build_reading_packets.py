"""Build structured reading packets for dictionary term enrichment.

For each dictionary term (or a specified subset), this script:
1. Searches the chunk corpus for relevant passages
2. Assembles a structured packet with full provenance
3. Writes packets to /staging/packets/[slug].json

Packets contain ONLY retrieved evidence. No generated interpretations.
Downstream enrichment scripts use packets as input.
"""

import sqlite3
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"
STAGING_DIR = BASE_DIR / "staging"
PACKETS_DIR = STAGING_DIR / "packets"

# Import corpus search
import sys
sys.path.insert(0, str(BASE_DIR / "scripts"))
from corpus_search import search_by_term, search_chunks


# Synonyms / alternate forms for better search coverage
TERM_SYNONYMS = {
    'signature': ['signature mark', 'sig.', 'quire mark'],
    'quire': ['gathering', 'quaternion'],
    'folio': ['leaf', 'fol.'],
    'marginalia': ['marginal note', 'annotation', 'margin'],
    'annotator-hand': ['hand A', 'hand B', 'hand C', 'hand D', 'hand E',
                        'annotator', 'handwriting'],
    'alchemical-allegory': ['alchemical reading', 'alchemical interpretation',
                            'alchemist'],
    'master-mercury': ['mercury', 'Mercurii', 'quicksilver', "d'Espagnet"],
    'sol-luna': ['Sol and Luna', 'sun and moon', 'gold and silver'],
    'chemical-wedding': ['chemical marriage', 'chymische Hochzeit',
                         'hermaphrodite'],
    'prisca-sapientia': ['ancient wisdom', 'prisca theologia',
                         'Hermes Trismegistus'],
    'woodcut': ['illustration', 'woodblock', 'woodcuts'],
    'acrostic': ['POLIAM FRATER', 'chapter initials'],
    'hieroglyph': ['hieroglyphic', 'Horapollo', 'pseudo-Egyptian'],
    'emblem': ['emblem book', 'Alciato', 'pictura'],
    'ekphrasis': ['ekphrastic', 'verbal description'],
    'incunabulum': ['incunabula', 'ISTC', 'fifteenth-century printing'],
    'aldus-manutius': ['Aldus', 'Manutius', 'Aldine'],
    'authorship-debate': ['Francesco Colonna', 'Alberti', 'authorship'],
    'dream-narrative': ['dream', 'Poliphilo falls asleep', 'dream-within'],
    'elephant-obelisk': ['elephant', 'obelisk', 'Bernini', 'b6v', 'b7r'],
    'ideogram': ['alchemical symbol', 'alchemical sign', 'ideogram'],
    'activity-book': ['activity book', 'humanistic activity'],
    'inventio': ['invention', 'rhetorical invention'],
    'ingegno': ['ingenium', 'wit', 'ingegno'],
    'acutezze': ['acutezza', 'wit', 'Alexander VII', 'Chigi'],
    'cythera': ['Cythera', 'island of Venus', 'circular garden'],
    'reception-history': ['reception', 'readership', 'readers'],
    'antiquarianism': ['antiquarian', 'Cyriacus', 'ancient monuments'],
    'vernacular-poetics': ['Petrarchan', 'vernacular', 'Italian poetry'],
    'collation': ['collation formula', 'a-z8', 'bibliographic structure'],
    'apparatus': ['critical edition', 'textual notes', 'apparatus criticus'],
    'commentary': ['commentator', 'gloss', 'interpretation'],
    'allegory': ['allegorical', 'allegory of love'],
    'architectural-body': ['architectural body', 'Lefaivre', 'embodied'],
    'recto': ['recto'],
    'verso': ['verso'],
    'gathering': ['gathering', 'quaternion'],
}


def build_packet(term_slug, term_label, category, current_status):
    """Build a reading packet for a single dictionary term.

    Returns a structured dict with retrieved evidence only.
    """
    synonyms = TERM_SYNONYMS.get(term_slug, [])

    # Search using term label + synonyms
    results = search_by_term(term_label, synonyms=synonyms)

    passages = []
    for r in results:
        passages.append({
            'text': r['matched_text'],
            'source_doc': r['source_doc'],
            'chunk_path': r['chunk_path'],
            'section': r['section'],
            'page_refs': r['page_refs'],
            'relevance_score': r['relevance_score'],
        })

    return {
        'term': term_label,
        'slug': term_slug,
        'category': category,
        'current_review_status': current_status,
        'passage_count': len(passages),
        'passages': passages,
        'search_terms_used': [term_label] + synonyms,
        'source_method': 'CORPUS_EXTRACTION',
    }


def build_all_packets(filter_status=None, filter_slugs=None):
    """Build reading packets for all (or filtered) dictionary terms.

    Args:
        filter_status: Only build for terms with this review_status (e.g. 'DRAFT')
        filter_slugs: Only build for these specific slugs
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    query = "SELECT slug, label, category, review_status FROM dictionary_terms"
    params = []
    if filter_status:
        query += " WHERE review_status = ?"
        params.append(filter_status)
    query += " ORDER BY slug"

    cur.execute(query, params)
    terms = cur.fetchall()
    conn.close()

    PACKETS_DIR.mkdir(parents=True, exist_ok=True)

    built = 0
    for slug, label, category, status in terms:
        if filter_slugs and slug not in filter_slugs:
            continue

        print(f"  Building packet: {slug} ({category})")
        packet = build_packet(slug, label, category, status)

        packet_path = PACKETS_DIR / f"{slug}.json"
        with open(packet_path, 'w', encoding='utf-8') as f:
            json.dump(packet, f, indent=2, ensure_ascii=False)

        built += 1
        print(f"    -> {packet['passage_count']} passages found")

    print(f"\nBuilt {built} reading packets in {PACKETS_DIR}")
    return built


if __name__ == "__main__":
    import sys
    print("=== Building Reading Packets ===\n")

    if len(sys.argv) > 1:
        # Build for specific slugs
        slugs = sys.argv[1:]
        build_all_packets(filter_slugs=slugs)
    else:
        # Build for all DRAFT terms
        build_all_packets(filter_status='DRAFT')
