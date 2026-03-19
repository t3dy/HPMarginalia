"""Build the signature-to-folio mapping table for the 1499 Aldine HP.

The 1499 Aldus Manutius edition uses the standard Aldine collation:
  Quires a-z (skipping j, u, w) then A-G
  Each quire has 8 leaves (quaternion format)
  Each leaf has recto (r) and verso (v)

Collation formula: a-y⁸ z⁴ A-F⁸ G⁴ = 234 leaves = 468 pages

This produces a deterministic lookup: signature "a1r" = folio 1 recto,
"a1v" = folio 1 verso, "b1r" = folio 9 recto, etc.
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"

# Standard Aldine quire sequence for the 1499 HP
# Lowercase quires: a through y, skipping j, u, w
LOWERCASE_QUIRES = [c for c in 'abcdefghiklmnopqrstxyz']
# Uppercase quires (for the second alphabet run): A through G
UPPERCASE_QUIRES = list('ABCDEFG')

# Leaves per quire - most are 8 (quaternion), but z and G are 4
QUIRE_SIZES = {}
for q in LOWERCASE_QUIRES:
    QUIRE_SIZES[q] = 4 if q == 'z' else 8
for q in UPPERCASE_QUIRES:
    QUIRE_SIZES[q] = 4 if q == 'G' else 8


def generate_signatures():
    """Generate all signatures in order with their sequential folio numbers."""
    all_quires = LOWERCASE_QUIRES + UPPERCASE_QUIRES
    folio_num = 1
    entries = []

    for quire in all_quires:
        leaves = QUIRE_SIZES[quire]
        for leaf in range(1, leaves + 1):
            for side in ('r', 'v'):
                sig = f"{quire}{leaf}{side}"
                entries.append({
                    'signature': sig,
                    'folio_number': folio_num,
                    'side': side,
                    'quire': quire,
                    'leaf_in_quire': leaf,
                })
            folio_num += 1

    return entries


def main():
    entries = generate_signatures()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Clear existing entries
    cur.execute("DELETE FROM signature_map")

    for e in entries:
        cur.execute(
            """INSERT INTO signature_map
               (signature, folio_number, side, quire, leaf_in_quire)
               VALUES (?, ?, ?, ?, ?)""",
            (e['signature'], e['folio_number'], e['side'], e['quire'], e['leaf_in_quire'])
        )

    conn.commit()

    # Summary
    total = len(entries)
    quire_count = len(LOWERCASE_QUIRES) + len(UPPERCASE_QUIRES)
    max_folio = entries[-1]['folio_number']
    print(f"Built signature map: {total} entries, {quire_count} quires, {max_folio} folios")
    print(f"  First: {entries[0]['signature']} = folio {entries[0]['folio_number']}")
    print(f"  Last:  {entries[-1]['signature']} = folio {entries[-1]['folio_number']}")

    # Spot checks
    print("\nSpot checks:")
    cur.execute("SELECT signature, folio_number FROM signature_map WHERE signature = 'a1r'")
    r = cur.fetchone()
    print(f"  a1r -> folio {r[1]}" if r else "  a1r NOT FOUND")

    cur.execute("SELECT signature, folio_number FROM signature_map WHERE signature = 'b1r'")
    r = cur.fetchone()
    print(f"  b1r -> folio {r[1]}" if r else "  b1r NOT FOUND")

    cur.execute("SELECT signature, folio_number FROM signature_map WHERE signature = 'e1r'")
    r = cur.fetchone()
    print(f"  e1r -> folio {r[1]} (Russell's methodology boundary)" if r else "  e1r NOT FOUND")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
