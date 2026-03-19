"""Add annotator hands table and tag dissertation references with hand attributions.

Based on James Russell's PhD thesis analysis of six annotated copies of the HP.
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"


HANDS_SCHEMA = """
CREATE TABLE IF NOT EXISTS annotator_hands (
    id INTEGER PRIMARY KEY,
    hand_label TEXT NOT NULL,
    manuscript_shelfmark TEXT NOT NULL,
    attribution TEXT,
    language TEXT,
    ink_color TEXT,
    date_range TEXT,
    school TEXT,
    interests TEXT,
    description TEXT,
    is_alchemist BOOLEAN DEFAULT 0,
    chapter_num INTEGER,
    UNIQUE(hand_label, manuscript_shelfmark)
);

-- Add hand_id column to dissertation_refs if not exists
"""

ALTER_REFS = """
ALTER TABLE dissertation_refs ADD COLUMN hand_id INTEGER REFERENCES annotator_hands(id);
"""


# All annotator hands identified by Russell across the six copies
HANDS = [
    # BL C.60.o.12 (Ch. 6) — 1545 edition
    {
        'hand_label': 'A',
        'manuscript_shelfmark': 'C.60.o.12',
        'attribution': 'Ben Jonson',
        'language': 'English, Latin',
        'ink_color': None,
        'date_range': 'c.1600-1637',
        'school': None,
        'interests': 'stagecraft, linguistic technicalities, inventio, visual stage design',
        'description': (
            'First hand in the BL copy, convincingly attributed to Ben Jonson. '
            'Composed a selective summary foregrounding large-scale visual monuments '
            'and vehicles suitable for stage design. Extensive grammatical parsing '
            'through underlining (simple, double, bracket). Interested in architectural '
            'vocabulary and natural forms (snails, acanthus, seashells) as column models. '
            'Mining the HP for ideas for masque stagecraft (inventio).'
        ),
        'is_alchemist': False,
        'chapter_num': 6,
    },
    {
        'hand_label': 'B',
        'manuscript_shelfmark': 'C.60.o.12',
        'attribution': 'Anonymous (possibly Royal Society circle)',
        'language': 'Latin, English',
        'ink_color': None,
        'date_range': 'post-1641, late 17th century',
        'school': "Jean d'Espagnet (Enchiridion Physicae Restitutae)",
        'interests': 'alchemical allegory, Master Mercury, ideographic vocabulary, prisca sapientia',
        'description': (
            "Anonymous second hand in the BL copy. Inferred alchemical formulae beneath "
            "the narrative surface. Labelled passages and woodcuts with alchemical signs "
            "(gold, silver, mercury, Venus, Jupiter). Follower of Jean d'Espagnet's "
            "emphasis on mercury as catalytic bearer of solar energy. Used extensive "
            "alchemical ideograms with Latin inflections (e.g. sun-symbol + '-ra' for "
            "'aurata'). Consistency with Newton's Keynes MSS vocabulary suggests possible "
            "connection to Royal Society or Cambridge. Wrote programmatic summary on "
            "flyleaf verso: 'verus sensus intentionis huius libri est 3um' — threefold "
            "meaning centering on 'Master Mercury'. Notes decline in Book II but alchemical "
            "symbols persist. Also an Englishman ('frogg green')."
        ),
        'is_alchemist': True,
        'chapter_num': 6,
    },

    # Buffalo (Ch. 7) — 1499 edition
    {
        'hand_label': 'A',
        'manuscript_shelfmark': 'Buffalo RBR',
        'attribution': 'Anonymous (possibly Jesuit, St. Omer)',
        'language': 'French',
        'ink_color': 'black',
        'date_range': 'pre-1739',
        'school': None,
        'interests': 'narrative summary',
        'description': (
            'First French hand in black ink. Wrote summary of HP narrative on page '
            'following dedicatory letter. If the book was at St. Omer before 1739 '
            '(as Jesuit ex libris suggests), this may be a Jesuit annotator.'
        ),
        'is_alchemist': False,
        'chapter_num': 7,
    },
    {
        'hand_label': 'B',
        'manuscript_shelfmark': 'Buffalo RBR',
        'attribution': 'Anonymous (possibly Jesuit, St. Omer)',
        'language': 'French',
        'ink_color': 'light brown',
        'date_range': 'pre-1739',
        'school': None,
        'interests': 'Greek etymologies, Hebrew roots, Plinian sources',
        'description': (
            'Second French hand in light brown ink. Primary interest in etymologies '
            'of Greek terms. Only annotator in the study to identify Hebrew roots. '
            'Also traces Plinian sources (Naturalis historia) for wines, laws, '
            'architecture. Similar ductus to Hand A suggests common origin, possibly '
            'another Jesuit of St. Omer.'
        ),
        'is_alchemist': False,
        'chapter_num': 7,
    },
    {
        'hand_label': 'C',
        'manuscript_shelfmark': 'Buffalo RBR',
        'attribution': 'Anonymous',
        'language': 'Latin',
        'ink_color': 'brown',
        'date_range': None,
        'school': None,
        'interests': 'narrative signposting',
        'description': 'Latin hand in brown ink. Primarily interested in signposting the narrative, summarising major passages.',
        'is_alchemist': False,
        'chapter_num': 7,
    },
    {
        'hand_label': 'D',
        'manuscript_shelfmark': 'Buffalo RBR',
        'attribution': 'Anonymous',
        'language': 'Italian, Latin',
        'ink_color': None,
        'date_range': None,
        'school': None,
        'interests': 'architecture',
        'description': (
            'Italian hand responding to Hand A. In one instance crosses off A\'s comments '
            'and offers abbreviated summary. Primary interest in architecture. Switches to '
            'Latin when labelling architectural features.'
        ),
        'is_alchemist': False,
        'chapter_num': 7,
    },
    {
        'hand_label': 'E',
        'manuscript_shelfmark': 'Buffalo RBR',
        'attribution': 'Anonymous',
        'language': 'Latin',
        'ink_color': None,
        'date_range': 'late 17th-early 18th century',
        'school': 'pseudo-Geber (Jabir ibn Hayyan)',
        'interests': 'alchemical allegory, Sol/Luna, sulphur, chemical wedding',
        'description': (
            "Final distinguishable hand. Applies alchemical reading. Overwrites Hand D "
            "(latest hand). Follower of pseudo-Geber school emphasizing sulphur and "
            "Sol/Luna pairings. Unlike BL alchemist, uses minimal ideograms — writes "
            "out element names in full (e.g. 'sulphur naturae'). Labels passages with "
            "alchemical stages. Praises Geber's 'ingenium subtile'. Reads male-female "
            "pairings as alchemical weddings. Identifies chess match results as "
            "silver/gold transmutation."
        ),
        'is_alchemist': True,
        'chapter_num': 7,
    },

    # Modena (Ch. 4) — 1499 edition
    {
        'hand_label': 'Primary',
        'manuscript_shelfmark': 'Modena (Panini)',
        'attribution': 'Benedetto Giovio',
        'language': 'Italian, Latin',
        'ink_color': None,
        'date_range': 'early 16th century',
        'school': None,
        'interests': 'Plinian natural history, etymology, botany, music, medicine',
        'description': (
            'Primary hand attributed to Benedetto Giovio (1471-1545). Plinian '
            'encyclopedic reading: extracts etymologies, botanical identifications, '
            'medical terms, musical modes, mineralogy, and literary cross-references '
            '(Boccaccio, Erasmus, Homer). Over 150 sources identified by Stichel. '
            'Also modified woodcuts with coloring and shading.'
        ),
        'is_alchemist': False,
        'chapter_num': 4,
    },

    # Como (Ch. 5) — 1499 edition
    {
        'hand_label': 'Primary',
        'manuscript_shelfmark': 'INCUN A.5.13',
        'attribution': 'Benedetto Giovio',
        'language': 'Italian, Latin',
        'ink_color': None,
        'date_range': 'early 16th century',
        'school': None,
        'interests': 'Plinian botany, botanical vocabulary extraction',
        'description': (
            'Also attributed to Benedetto Giovio. Same hand as Modena copy. '
            'Focuses specifically on botanical vocabulary extraction, treating '
            'the HP as a Plinian encyclopedia. Identifies plants with Plinian '
            'cross-references.'
        ),
        'is_alchemist': False,
        'chapter_num': 5,
    },

    # Vatican (Ch. 8) — 1499 edition
    {
        'hand_label': 'Primary',
        'manuscript_shelfmark': 'Inc.Stam.Chig.II.610',
        'attribution': 'Pope Alexander VII (Fabio Chigi)',
        'language': 'Latin, Italian',
        'ink_color': None,
        'date_range': 'c.1630s-1667',
        'school': None,
        'interests': 'acutezze (verbal wit), architecture, Rome topography',
        'description': (
            'Attributed to Fabio Chigi, later Pope Alexander VII (1599-1667). '
            'Combed text for examples of verbal wit (acutezze). Compared '
            "Poliphilo's architectural journeys with his own passages through "
            "Rome. Interest in orthographic diagrams and textual emendation."
        ),
        'is_alchemist': False,
        'chapter_num': 8,
    },

    # Siena (Ch. 9) — 1499 edition
    {
        'hand_label': 'Primary',
        'manuscript_shelfmark': 'O.III.38',
        'attribution': 'Anonymous',
        'language': 'Latin, Italian',
        'ink_color': None,
        'date_range': 'early modern',
        'school': None,
        'interests': 'calligraphic annotation, textual emendation, educative marginalia',
        'description': (
            'Painstaking calligraphic marginalia. Multiple hands (A-D) including '
            "ownership marks by Francisci Fini and Friedrich Schaller. Hand C wrote "
            "'Ad lectorem' note. Hand D engaged with dating and literary analysis."
        ),
        'is_alchemist': False,
        'chapter_num': 9,
    },
]


# Rules for attributing dissertation references to hands
# Based on thesis content analysis: signature refs that Russell explicitly
# discusses in connection with specific hands.
HAND_ATTRIBUTION_RULES = {
    # BL C.60.o.12 — Ch. 6
    # Hand A (Jonson): stagecraft, grammatical parsing, architectural vocabulary
    ('C.60.o.12', 'A'): {
        'signatures': {
            'a4r',  # underlining techniques (p.147)
            'e7r',  # hatching technique for shadow (p.150)
            'b4v',  # Corinthian order identification (p.151)
            'm7v',  # Corinthian column base (p.152)
            'd4r',  # snail metaphor (p.152)
            't7v',  # seashell form (p.152)
        },
        'pages': range(123, 156),
    },
    # Hand B (Alchemist): ideograms, mercury, elemental signs
    ('C.60.o.12', 'B'): {
        'signatures': {
            'b6v',  # Elephant and Obelisk ideograms (p.157)
            'E8v',  # Venus symbol replacing name (p.157)
            'y7r',  # Fons Heptagonis labeled (p.136)
            'e1r',  # Panton Tokadi / vials labeled (p.163-164)
            'd8v',  # mercury/vas references (p.164)
            'a1r',  # dawn scene alchemical annotation (p.165)
            'a3r',  # alchemical context (p.155)
            'k5r',  # alchemical labeling (p.131)
        },
        'pages': range(155, 170),
    },
    # Buffalo — Ch. 7
    # Hand E (Alchemist): Geberian school, sulphur, Sol/Luna
    ('Buffalo RBR', 'E'): {
        'signatures': {
            'b7r',  # Geberian schema, ingenium subtile (p.187)
            'c6v',  # Venus/Bacchus/Ceres (p.187-188)
            'h1r',  # chess match/hermaphrodite (p.189-190)
            'b5r',  # alchemical context (p.190)
        },
        'pages': range(185, 200),
    },
    # Hand B (Etymologist): Plinian sources, etymologies
    ('Buffalo RBR', 'B'): {
        'signatures': {
            'b8v',  # Hebrew roots (p.172)
            'g8r',  # Plinian sources for laws (p.176)
            'h7r',  # serpent wreath correction (p.183)
        },
        'pages': range(172, 185),
    },
    # Hand D (Architect)
    ('Buffalo RBR', 'D'): {
        'signatures': {
            'b1r',  # architectural labels (p.173, 181)
        },
    },
    # Hand A (French narrative)
    ('Buffalo RBR', 'A'): {
        'signatures': {
            'A2r',  # Polia name origin (p.179)
        },
    },
}


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create hands table
    print("Creating annotator_hands table...")
    cur.executescript(HANDS_SCHEMA)

    # Add hand_id column if not exists
    try:
        cur.execute(ALTER_REFS)
        print("  Added hand_id column to dissertation_refs")
    except sqlite3.OperationalError as e:
        if 'duplicate column' in str(e).lower():
            print("  hand_id column already exists")
        else:
            raise

    # Insert hands
    print("Inserting annotator hands...")
    for h in HANDS:
        cur.execute(
            """INSERT OR REPLACE INTO annotator_hands
               (hand_label, manuscript_shelfmark, attribution, language,
                ink_color, date_range, school, interests, description,
                is_alchemist, chapter_num)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (h['hand_label'], h['manuscript_shelfmark'], h['attribution'],
             h['language'], h['ink_color'], h['date_range'], h['school'],
             h['interests'], h['description'], h['is_alchemist'],
             h['chapter_num'])
        )
    conn.commit()
    print(f"  Inserted {len(HANDS)} hands")

    # Attribute refs to hands based on rules
    print("\nAttributing dissertation references to hands...")
    attributed = 0
    for (shelfmark, hand_label), rule in HAND_ATTRIBUTION_RULES.items():
        # Get hand_id
        cur.execute(
            "SELECT id FROM annotator_hands WHERE manuscript_shelfmark=? AND hand_label=?",
            (shelfmark, hand_label)
        )
        row = cur.fetchone()
        if not row:
            print(f"  WARNING: hand not found: {shelfmark} / {hand_label}")
            continue
        hand_id = row[0]

        sigs = rule.get('signatures', set())
        pages = rule.get('pages')

        for sig in sigs:
            # Find matching refs
            if pages:
                cur.execute(
                    """UPDATE dissertation_refs SET hand_id = ?
                       WHERE signature_ref = ? AND manuscript_shelfmark = ?
                       AND thesis_page BETWEEN ? AND ?""",
                    (hand_id, sig, shelfmark, pages.start, pages.stop)
                )
            else:
                cur.execute(
                    """UPDATE dissertation_refs SET hand_id = ?
                       WHERE signature_ref = ? AND manuscript_shelfmark = ?""",
                    (hand_id, sig, shelfmark)
                )
            attributed += cur.rowcount

    # Also attribute by chapter for copies with single known hands
    single_hand_chapters = {
        4: ('Modena (Panini)', 'Primary'),
        5: ('INCUN A.5.13', 'Primary'),
        8: ('Inc.Stam.Chig.II.610', 'Primary'),
        9: ('O.III.38', 'Primary'),
    }
    for ch, (shelfmark, hand_label) in single_hand_chapters.items():
        cur.execute(
            "SELECT id FROM annotator_hands WHERE manuscript_shelfmark=? AND hand_label=?",
            (shelfmark, hand_label)
        )
        row = cur.fetchone()
        if not row:
            continue
        hand_id = row[0]
        cur.execute(
            "UPDATE dissertation_refs SET hand_id = ? WHERE chapter_num = ? AND hand_id IS NULL",
            (hand_id, ch)
        )
        attributed += cur.rowcount

    conn.commit()
    print(f"  Attributed {attributed} references to hands")

    # Summary
    print("\nHand attribution summary:")
    cur.execute("""
        SELECT h.hand_label, h.manuscript_shelfmark, h.attribution, h.is_alchemist,
               COUNT(r.id) as ref_count
        FROM annotator_hands h
        LEFT JOIN dissertation_refs r ON r.hand_id = h.id
        GROUP BY h.id
        ORDER BY h.chapter_num, h.hand_label
    """)
    for row in cur.fetchall():
        label, shelf, attr, alch, count = row
        alch_tag = " [ALCHEMIST]" if alch else ""
        print(f"  {shelf} Hand {label} ({attr}){alch_tag}: {count} refs")

    # Show unattributed
    cur.execute("SELECT COUNT(*) FROM dissertation_refs WHERE hand_id IS NULL")
    unattr = cur.fetchone()[0]
    print(f"\n  Unattributed references: {unattr}")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
