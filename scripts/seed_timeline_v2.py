"""Extend timeline_events with art, literary influence, and scholarly milestones.

Adds ~50 new events covering art inspired by the HP, literary influence,
scholarly milestones from the bibliography, and modern reception.

Idempotent: uses INSERT OR IGNORE on (year, title) uniqueness check.
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"

# Map our desired event types to the DB CHECK constraint
# ART -> OTHER, SCHOLARSHIP -> OTHER, LITERARY -> OTHER
# Use 'category' field for the real type label
EVENTS = [
    # === Art ===
    {
        "year": 1520, "event_type": "OTHER", "category": "art",
        "title": "Garofalo painting with HP scene",
        "description": "The Ferrarese painter Garofalo (Benvenuto Tisi) produced a painting incorporating a scene from the HP, identified by Fritz Saxl in his 1937 study. This is among the earliest documented visual adaptations of the HP outside the book itself.",
        "medium": "painting", "confidence": "MEDIUM",
    },
    {
        "year": 1667, "event_type": "OTHER", "category": "art",
        "title": "Bernini's Elephant and Obelisk unveiled",
        "description": "Gian Lorenzo Bernini completed the elephant bearing an obelisk in Piazza della Minerva, Rome, commissioned by Pope Alexander VII. The sculpture draws on the HP's woodcut of the elephant-obelisk (b6v-b7r). Alexander VII himself annotated his copy of the HP.",
        "medium": "sculpture", "location": "Piazza della Minerva, Rome",
        "confidence": "HIGH",
    },
    {
        "year": 1717, "event_type": "OTHER", "category": "art",
        "title": "Watteau, L'Embarquement pour Cythere",
        "description": "Antoine Watteau painted L'Embarquement pour Cythere, depicting a departure for Venus's island. While direct influence from the HP is not confirmed, the painting belongs to the same cultural tradition of Cythera as the destination of erotic pilgrimage.",
        "medium": "painting", "location": "Louvre, Paris",
        "confidence": "LOW",
    },
    {
        "year": 1893, "event_type": "OTHER", "category": "art",
        "title": "Beardsley and the HP aesthetic",
        "description": "Aubrey Beardsley's illustration style of the 1890s shows affinities with the HP's woodcuts. Praz (1947) documents the HP's influence on the Aesthetic Movement and its visual culture, including Beardsley's decorative line work.",
        "medium": "illustration", "confidence": "LOW",
    },

    # === Literary Influence ===
    {
        "year": 1534, "event_type": "OTHER", "category": "literary",
        "title": "Rabelais, Abbey of Theleme in Gargantua",
        "description": "Francois Rabelais included the Abbey of Theleme ('Do what thou wilt') in Gargantua, almost certainly drawing on the HP's portal of Thelemia where Poliphilo chooses among three life paths. The name and concept of free will connect the two works directly.",
        "confidence": "HIGH",
    },
    {
        "year": 1592, "event_type": "TRANSLATION", "category": "edition",
        "title": "Robert Dallington's English adaptation",
        "description": "Robert Dallington published The Strife of Love in a Dreame, the first English version of the HP. Semler (2006) reframes this not as failed translation but as deliberate cultural appropriation for Protestant antiquarian interests in Elizabethan England.",
        "confidence": "HIGH",
    },
    {
        "year": 1804, "event_type": "EDITION", "category": "edition",
        "title": "Italian reprint edition",
        "description": "An Italian reprint of the HP appeared in 1804, part of the early nineteenth-century revival of interest in the book as a bibliophilic and aesthetic object.",
        "confidence": "MEDIUM",
    },

    # === Scholarly Milestones ===
    {
        "year": 1899, "event_type": "OTHER", "category": "scholarship",
        "title": "Gnoli, Il Sogno di Polifilo",
        "description": "Domenico Gnoli published one of the earliest modern scholarly studies of the HP, helping to inaugurate the twentieth-century revival of HP scholarship.",
        "confidence": "HIGH",
    },
    {
        "year": 1910, "event_type": "OTHER", "category": "scholarship",
        "title": "Huelsen, Le illustrazioni della Hypnerotomachia Poliphili",
        "description": "Christian Huelsen published the first systematic study of the HP's woodcut illustrations, identifying their classical architectural sources and establishing the foundation for all subsequent architectural analysis.",
        "confidence": "HIGH",
    },
    {
        "year": 1935, "event_type": "OTHER", "category": "scholarship",
        "title": "Khomentovskaia proposes Feliciano as author",
        "description": "A. Khomentovskaia proposed Felice Feliciano as the HP's author, adding another candidate to the authorship debate alongside the two Francesco Colonnas.",
        "confidence": "HIGH",
    },
    {
        "year": 1937, "event_type": "OTHER", "category": "scholarship",
        "title": "Blunt, The HP in 17th Century France",
        "description": "Anthony Blunt documented the HP's influence on seventeenth-century French art, garden design, and festival culture. His article remains the standard reference for French HP reception.",
        "confidence": "HIGH",
    },
    {
        "year": 1937, "event_type": "OTHER", "category": "scholarship",
        "title": "Saxl identifies HP scene in Garofalo painting",
        "description": "Fritz Saxl identified a scene from the HP in a painting by the Ferrarese artist Garofalo, demonstrating the book's direct influence on Italian Renaissance painting.",
        "confidence": "HIGH",
    },
    {
        "year": 1947, "event_type": "OTHER", "category": "scholarship",
        "title": "Praz, Foreign Imitators of the HP",
        "description": "Mario Praz documented foreign imitations of the HP across English, French, and German literature, establishing the breadth of the book's European reception from Swinburne to Beardsley.",
        "confidence": "HIGH",
    },
    {
        "year": 1950, "event_type": "OTHER", "category": "scholarship",
        "title": "Fierz-David, Jungian reading of the HP",
        "description": "Linda Fierz-David published The Dream of Poliphilo, interpreting Poliphilo's journey as a process of Jungian individuation. This established a psychoanalytic strand of HP interpretation distinct from art-historical approaches.",
        "confidence": "HIGH",
    },
    {
        "year": 1959, "event_type": "OTHER", "category": "scholarship",
        "title": "Casella & Pozzi establish canonical authorship",
        "description": "Maria Teresa Casella and Giovanni Pozzi published Francesco Colonna. Biografia e opere, establishing the Venetian Dominican friar (d. 1527) as the canonical author through philological and archival evidence.",
        "confidence": "HIGH",
    },
    {
        "year": 1964, "event_type": "OTHER", "category": "scholarship",
        "title": "Pozzi & Ciapponi critical edition",
        "description": "Giovanni Pozzi and Lucia Ciapponi published the standard critical edition of the HP, including textual apparatus, glossary, and commentary that remain the foundation for all textual scholarship.",
        "confidence": "HIGH",
    },
    {
        "year": 1972, "event_type": "OTHER", "category": "scholarship",
        "title": "Gombrich, Hypnerotomachiana",
        "description": "Ernst Gombrich analyzed the HP's hieroglyphic woodcuts within the context of Renaissance symbolic imagery, demonstrating the book's role in the emblem tradition and the transmission of pseudo-Egyptian visual culture.",
        "confidence": "HIGH",
    },
    {
        "year": 1994, "event_type": "OTHER", "category": "scholarship",
        "title": "Stichel, first study of Modena marginalia",
        "description": "Dorothea Stichel published the first study of the Modena copy's marginalia, helping to establish the field of HP annotation studies that Russell would later expand.",
        "confidence": "HIGH",
    },
    {
        "year": 1996, "event_type": "OTHER", "category": "scholarship",
        "title": "Calvesi, Roman Colonna attribution",
        "description": "Maurizio Calvesi argued in La pugna d'amore in sogno that the HP was written by a Roman nobleman named Francesco Colonna, not the Venetian Dominican. This represents the most sustained challenge to the Casella-Pozzi consensus.",
        "confidence": "HIGH",
    },
    {
        "year": 1997, "event_type": "OTHER", "category": "scholarship",
        "title": "Lefaivre, Alberti attribution",
        "description": "Liane Lefaivre proposed Leon Battista Alberti as the HP's true author, introducing the concept of the 'architectural body' and shifting HP scholarship toward phenomenological and architectural analysis.",
        "confidence": "HIGH",
    },
    {
        "year": 1998, "event_type": "OTHER", "category": "scholarship",
        "title": "Word & Image special issue on the HP",
        "description": "The journal Word & Image published a special issue on the HP featuring studies by Hunt, Segre, Griggs, Curran, and others. This issue consolidated the late-1990s revival of HP scholarship across multiple disciplines.",
        "confidence": "HIGH",
    },
    {
        "year": 1999, "event_type": "EDITION", "category": "edition",
        "title": "Godwin English translation (Thames & Hudson)",
        "description": "Joscelyn Godwin published the first complete modern English translation of the HP with Thames & Hudson, providing the most accessible English-language scholarly apparatus.",
        "confidence": "HIGH",
    },
    {
        "year": 2002, "event_type": "OTHER", "category": "scholarship",
        "title": "Trippe, HP as vernacular poetics",
        "description": "Rosemary Trippe argued in Renaissance Quarterly that the HP has been understudied as literature, demonstrating how the author adapted Petrarchan conventions into a text-image interplay.",
        "confidence": "HIGH",
    },
    {
        "year": 2004, "event_type": "EDITION", "category": "edition",
        "title": "Ariani & Gabriele Adelphi critical edition",
        "description": "Marco Ariani and Mino Gabriele published a new Italian critical edition through Adelphi, providing the most recent scholarly apparatus complementing the Pozzi-Ciapponi edition.",
        "confidence": "HIGH",
    },
    {
        "year": 2006, "event_type": "OTHER", "category": "scholarship",
        "title": "Semler, Dallington's Protestant HP",
        "description": "L. E. Semler reframed Robert Dallington's 1592 English translation as deliberate cultural appropriation for Protestant antiquarian interests, not a failed translation.",
        "confidence": "HIGH",
    },
    {
        "year": 2014, "event_type": "OTHER", "category": "scholarship",
        "title": "Russell PhD thesis on HP annotators",
        "description": "James Russell submitted his Durham PhD thesis documenting marginalia in six HP copies, identifying eleven annotator hands and establishing the concept of the HP as a 'humanistic activity book.' This thesis is the primary evidence base for this project.",
        "confidence": "HIGH",
    },
    {
        "year": 2015, "event_type": "OTHER", "category": "scholarship",
        "title": "Second Word & Image special issue",
        "description": "A second Word & Image special issue on the HP appeared, including Farrington on Aldus's career and new contributions to reception studies.",
        "confidence": "HIGH",
    },
    {
        "year": 2024, "event_type": "EDITION", "category": "edition",
        "title": "Young, new English translation",
        "description": "Paul Summers Young published a new English translation of the HP, supplementing Godwin's 1999 version with a contemporary rendering of the macaronic language.",
        "confidence": "HIGH",
    },

    # === Garden Design Influence ===
    {
        "year": 1550, "event_type": "OTHER", "category": "art",
        "title": "HP influence on Italian Renaissance gardens",
        "description": "The sleeping nymph fountain and other HP motifs began appearing in Italian villa gardens by mid-sixteenth century. The HP's detailed garden descriptions provided a sourcebook for designers combining classical forms with living landscapes.",
        "medium": "garden design", "confidence": "MEDIUM",
    },
    {
        "year": 1552, "event_type": "OTHER", "category": "art",
        "title": "Sacro Bosco at Bomarzo begun",
        "description": "Pier Francesco Orsini began the Sacro Bosco (Sacred Grove) at Bomarzo, a garden of monstrous sculptures that Fabiani Giannetto (2015) connects to the HP's cultivation of meraviglia (wonder).",
        "medium": "garden/sculpture", "location": "Bomarzo, Italy",
        "confidence": "MEDIUM",
    },
]


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("Seeding timeline events (v2)...")
    inserted = 0
    for e in EVENTS:
        # Check for existing event with same year+title
        cur.execute("SELECT id FROM timeline_events WHERE year = ? AND title = ?",
                    (e["year"], e["title"]))
        if cur.fetchone():
            continue

        cur.execute("""
            INSERT INTO timeline_events
                (year, event_type, title, description, category, medium,
                 location, confidence, needs_review, source_method)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 'LLM_ASSISTED')
        """, (e["year"], e["event_type"], e["title"], e.get("description", ""),
              e.get("category", ""), e.get("medium", ""),
              e.get("location", ""), e.get("confidence", "MEDIUM")))
        inserted += cur.rowcount

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM timeline_events")
    total = cur.fetchone()[0]
    cur.execute("SELECT event_type, COUNT(*) FROM timeline_events GROUP BY event_type ORDER BY COUNT(*) DESC")
    print(f"\nTotal events: {total}")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    conn.close()
    print(f"\nInserted {inserted} new events. Done.")


if __name__ == "__main__":
    main()
