"""Export matched references as JSON for the static showcase page."""

import sqlite3
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"
OUTPUT_PATH = BASE_DIR / "site" / "data.json"


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Get all HIGH confidence matches (Ch6 BL + Ch9 Siena) plus all matches for showcase
    cur.execute("""
        SELECT
            dr.id as ref_id,
            dr.thesis_page,
            dr.signature_ref,
            dr.manuscript_shelfmark,
            dr.context_text,
            dr.marginal_text,
            dr.chapter_num,
            i.filename as image_filename,
            i.folio_number,
            i.side,
            i.page_type,
            i.relative_path,
            m.confidence,
            m.match_method,
            ms.shelfmark,
            ms.institution,
            ms.city,
            sm.quire,
            sm.leaf_in_quire
        FROM matches m
        JOIN dissertation_refs dr ON m.ref_id = dr.id
        JOIN images i ON m.image_id = i.id
        JOIN manuscripts ms ON i.manuscript_id = ms.id
        LEFT JOIN signature_map sm ON sm.signature = dr.signature_ref
        WHERE m.confidence = 'HIGH'
        AND i.page_type = 'PAGE'
        ORDER BY sm.folio_number, i.side, dr.thesis_page
    """)

    entries = []
    seen = set()  # Deduplicate by (signature, image)

    for row in cur.fetchall():
        key = (row['signature_ref'], row['image_filename'])
        if key in seen:
            continue
        seen.add(key)

        entries.append({
            'ref_id': row['ref_id'],
            'thesis_page': row['thesis_page'],
            'signature': row['signature_ref'],
            'manuscript': row['shelfmark'],
            'institution': row['institution'],
            'city': row['city'],
            'context': row['context_text'],
            'marginal_text': row['marginal_text'],
            'chapter': row['chapter_num'],
            'image_file': row['image_filename'],
            'image_path': row['relative_path'],
            'folio_number': row['folio_number'],
            'side': row['side'],
            'confidence': row['confidence'],
            'quire': row['quire'],
            'leaf_in_quire': row['leaf_in_quire'],
        })

    # Also get manuscript info for the page
    cur.execute("SELECT shelfmark, institution, city, description, image_count FROM manuscripts")
    manuscripts = [dict(row) for row in cur.fetchall()]

    # Summary stats
    cur.execute("SELECT COUNT(DISTINCT signature_ref) FROM dissertation_refs")
    unique_sigs = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM dissertation_refs")
    total_refs = cur.fetchone()[0]

    data = {
        'entries': entries,
        'manuscripts': manuscripts,
        'stats': {
            'total_references': total_refs,
            'unique_signatures': unique_sigs,
            'high_confidence_matches': len(entries),
        }
    }

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Exported {len(entries)} showcase entries to {OUTPUT_PATH}")
    print(f"  BL C.60.o.12: {sum(1 for e in entries if e['manuscript'] == 'C.60.o.12')}")
    print(f"  Siena O.III.38: {sum(1 for e in entries if e['manuscript'] == 'O.III.38')}")

    # Show a few entries
    print("\nSample entries:")
    for e in entries[:5]:
        print(f"  {e['signature']} [{e['manuscript']}] -> {e['image_file']}")
        if e['marginal_text']:
            print(f"    Marginal: '{e['marginal_text'][:60]}'")

    conn.close()


if __name__ == "__main__":
    main()
