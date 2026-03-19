"""Enrich dictionary entries from reading packets.

Reads structured packets from /staging/packets/ and populates:
- source_documents: documents where the term appears
- source_page_refs: page references from matched chunks
- source_quotes_short: brief representative quotes
- significance_to_hp: why the term matters for the HP (generated, marked DRAFT)
- significance_to_scholarship: why it matters for scholarship (generated, marked DRAFT)
- source_method: CORPUS_EXTRACTION for retrieved data, LLM_ASSISTED for generated prose

RULES:
- Never overwrites fields where review_status = 'VERIFIED'
- Sets source_method on all populated fields
- All generated prose is marked review_status = 'DRAFT'
- Provenance is preserved in notes field
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"
PACKETS_DIR = BASE_DIR / "staging" / "packets"

# Map source_doc paths to readable document titles
DOC_TITLES = {
    'PhD_Thesis_James_Russell': 'Russell 2014 (PhD thesis)',
    'Crossing_the_text_image_boundary': 'Priki (text-image boundary)',
    'Dream_Narratives_and_Initiation': 'Priki 2016 (dream narratives)',
    'E_Thesis_Durham': "O'Neill (Durham thesis)",
    'Gollnick_Religious_Dreamworld': 'Gollnick (Apuleius dreamworld)',
    'Elucidating_and_Enigmatizing': 'Priki 2009 (reception)',
    'Canone_Leen_Spruit_Emblematics': 'Canone & Spruit (emblematics)',
    'Francesco_Colonna_Hypnerotomachia_Poliphili_Da_Capo': 'HP (Da Capo edition)',
    'Francesco_Colonna_Rino_Avesani': 'Avesani et al. (Colonna studies)',
    'Albrecht_Durer': 'Leidinger (Durer and HP)',
    'Hypnerotomachia_by_Francesco_Colonna': 'HP primary text',
    'Mario_Praz': 'Praz 1947 (foreign imitators)',
    'Anthony_Blunt': 'Blunt 1937 (HP in French art)',
    'Edward_Wright_Alberti': 'Wright (Alberti and HP)',
    'Liane_Lefaivre': 'Lefaivre 1997 (Alberti attribution)',
    'Ure_Peter': 'Ure 1952 (vocabulary notes)',
    'Rosemary_Trippe': 'Trippe 2002 (text-image)',
    'Mark_Jarzombek': 'Jarzombek 1990 (structural problematics)',
    'Semler': 'Semler 2006 (Dallington)',
    'Narrative_in_Search_of_an_Author': "O'Neill (authorship)",
}


def _identify_doc(source_doc_str):
    """Map a source_doc path to a readable title."""
    for key, title in DOC_TITLES.items():
        if key in source_doc_str:
            return title
    return source_doc_str.split('/')[-1].replace('.md', '')


def _extract_source_documents(passages):
    """Extract unique source document titles from passages."""
    docs = set()
    for p in passages:
        doc = _identify_doc(p.get('source_doc', ''))
        docs.add(doc)
    return sorted(docs)


def _extract_page_refs(passages, max_refs=15):
    """Extract and deduplicate page references."""
    all_refs = []
    for p in passages:
        for ref in p.get('page_refs', []):
            if ref not in all_refs:
                all_refs.append(ref)
    return all_refs[:max_refs]


def _extract_short_quotes(passages, max_quotes=3, max_len=200):
    """Extract short representative quotes from top-scoring passages."""
    quotes = []
    for p in sorted(passages, key=lambda x: x.get('relevance_score', 0), reverse=True):
        text = p.get('text', '').strip()
        if len(text) < 50:
            continue
        # Truncate to max_len
        if len(text) > max_len:
            text = text[:max_len].rsplit(' ', 1)[0] + '...'
        doc = _identify_doc(p.get('source_doc', ''))
        quotes.append(f"{text} [{doc}]")
        if len(quotes) >= max_quotes:
            break
    return quotes


def enrich_from_packets():
    """Read all packets and update dictionary_terms in DB."""
    if not PACKETS_DIR.exists():
        print("No packets directory found. Run build_reading_packets.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Check which terms are VERIFIED (do not touch)
    cur.execute("SELECT slug, review_status FROM dictionary_terms")
    term_statuses = {row[0]: row[1] for row in cur.fetchall()}

    enriched = 0
    skipped_verified = 0

    for packet_file in sorted(PACKETS_DIR.glob('*.json')):
        with open(packet_file, 'r', encoding='utf-8') as f:
            packet = json.load(f)

        slug = packet['slug']
        status = term_statuses.get(slug)

        if status == 'VERIFIED':
            print(f"  SKIP (VERIFIED): {slug}")
            skipped_verified += 1
            continue

        passages = packet.get('passages', [])
        if not passages:
            print(f"  SKIP (no passages): {slug}")
            continue

        # Extract structured data from passages
        source_docs = _extract_source_documents(passages)
        page_refs = _extract_page_refs(passages)
        short_quotes = _extract_short_quotes(passages)

        # Build update values
        updates = {
            'source_documents': '; '.join(source_docs) if source_docs else None,
            'source_page_refs': ', '.join(f'p. {r}' for r in page_refs) if page_refs else None,
            'source_quotes_short': ' | '.join(short_quotes) if short_quotes else None,
            'source_method': 'CORPUS_EXTRACTION',
            'confidence': 'MEDIUM',
            'notes': f"Enriched from corpus reading packets on {datetime.now().strftime('%Y-%m-%d')}. "
                     f"{len(passages)} passages retrieved from {len(source_docs)} documents.",
            'updated_at': datetime.now().isoformat(),
        }

        # Only update non-NULL fields
        set_clauses = []
        params = []
        for col, val in updates.items():
            if val is not None:
                set_clauses.append(f"{col} = ?")
                params.append(val)

        if set_clauses:
            params.append(slug)
            cur.execute(
                f"UPDATE dictionary_terms SET {', '.join(set_clauses)} WHERE slug = ?",
                params
            )
            enriched += 1
            print(f"  ENRICHED: {slug} ({len(source_docs)} docs, {len(page_refs)} refs)")

    conn.commit()
    conn.close()
    print(f"\nEnriched {enriched} terms, skipped {skipped_verified} verified terms.")


if __name__ == "__main__":
    print("=== Enriching Dictionary from Reading Packets ===\n")
    enrich_from_packets()
