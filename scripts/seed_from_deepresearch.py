#!/usr/bin/env python3
"""seed_from_deepresearch.py — Ingest data from HPDEEPRESEARCH.txt into the database.

Seeds: editions, scholars, dictionary_terms, timeline_events, bibliography.
All data sourced from the HPDEEPRESEARCH.txt comprehensive survey.

Usage:
    python scripts/seed_from_deepresearch.py
    python scripts/seed_from_deepresearch.py --dry-run
"""

import argparse
import re
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "hp.db"


def slugify(text):
    s = text.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s[:80].rstrip('-')


# ============================================================
# EDITIONS DATA
# ============================================================

EDITIONS = [
    {
        "title": "Hypnerotomachia Poliphili (Editio Princeps)",
        "year": 1499,
        "city": "Venice",
        "printer_publisher": "Aldus Manutius (Aldine Press)",
        "language": "Italian (macaronic Latin-Italian hybrid)",
        "edition_type": "FIRST_EDITION",
        "description": "The first edition of the Hypnerotomachia Poliphili, published in December 1499 by Aldus Manutius. Commissioned by Leonardo Crasso, a Venetian nobleman. Contains 172 woodcut illustrations by an unidentified artist (Benedetto Bordon most widely proposed). Printed using Francesco Griffo's Roman typeface, which set a new standard for Western typography.",
        "significance": "The most ambitious illustrated book of the incunable period. Contains the first instances of Arabic type in Europe. The harmonious integration of text and image was unprecedented and has never been surpassed in letterpress printing. 267 extant copies confirmed by James Russell's census.",
        "woodcut_info": "172 woodcut illustrations. Full-page and in-text woodcuts depicting architectural fantasies, allegorical scenes, hieroglyphic friezes, and the triumphal procession. The artist remains unidentified despite centuries of attribution debate.",
        "digital_facsimile_url": "https://archive.org/details/A336080v1",
        "extant_copies": 267,
    },
    {
        "title": "Hypnerotomachia Poliphili (Second Italian Edition)",
        "year": 1545,
        "city": "Venice",
        "printer_publisher": "Sons of Aldus (Paolo Manuzio)",
        "language": "Italian",
        "edition_type": "REPRINT",
        "description": "The second Italian edition, published by Aldus's sons using the original 1499 woodblocks with updated typography. This is the edition owned by the British Library copy C.60.o.12, which contains the alchemical annotations studied by James Russell.",
        "significance": "Reuses the original 1499 woodblocks, demonstrating their durability. The BL copy of this edition (C.60.o.12) contains annotations by Ben Jonson (Hand A) and an anonymous alchemist (Hand B), making it one of the most important annotated copies for reception history.",
        "woodcut_info": "Same 172 woodblocks as the 1499 edition, with some showing signs of wear. Typography updated to mid-16th century Aldine house style.",
        "worldcat_url": "https://www.worldcat.org/title/hypnerotomachia-poliphili/oclc/58533211",
    },
    {
        "title": "Le Songe de Poliphile (First French Edition)",
        "year": 1546,
        "city": "Paris",
        "printer_publisher": "Jacques Kerver",
        "translator": "Jean Martin",
        "language": "French",
        "edition_type": "TRANSLATION",
        "description": "The first French translation by Jean Martin, published by Jacques Kerver in Paris. Features entirely new woodcuts in the Mannerist style, attributed to Jean Cousin the Elder. The translation adapts Colonna's macaronic prose into elegant French, making the text accessible to a wider audience.",
        "significance": "Crucial for the HP's influence on French architecture, garden design, and royal spectacle. The new Mannerist woodcuts by Jean Cousin reinterpret the Italian originals through a French aesthetic lens. Anthony Blunt documented the book's influence on 17th-century French royal entries.",
        "woodcut_info": "Entirely new set of woodcuts in the Mannerist style, attributed to Jean Cousin the Elder. These French woodcuts reinterpret rather than copy the 1499 Italian originals, offering a fascinating comparison between Italian and French visual culture.",
    },
    {
        "title": "The Strife of Love in a Dream (First English Edition)",
        "year": 1592,
        "city": "London",
        "printer_publisher": "Simon Waterson",
        "translator": "R.D. (Robert Dallington)",
        "language": "English",
        "edition_type": "TRANSLATION",
        "description": "The first English translation, published in London by Simon Waterson. A partial translation covering Book I only, attributed to 'R.D.' (identified as Robert Dallington). The Elizabethan English rendering captures the dreamlike quality of the original.",
        "significance": "Made the HP accessible to English readers for the first time. Published during the height of the English Renaissance, when interest in Italian culture and classical antiquity was at its peak. Ben Jonson, who annotated the 1545 Italian edition (BL C.60.o.12), may have known this translation.",
        "digital_facsimile_url": "https://archive.org/details/hypnerotomachiap00colo",
    },
    {
        "title": "Tableau des riches inventions (Alchemical Edition)",
        "year": 1600,
        "city": "Paris",
        "printer_publisher": "Matthieu Guillemot",
        "translator": "Beroalde de Verville",
        "language": "French",
        "edition_type": "ADAPTATION",
        "description": "A radical reinterpretation by Beroalde de Verville that reads the HP explicitly as an alchemical allegory. Rather than a faithful translation, Beroalde restructures the narrative to foreground the alchemical symbolism, presenting the HP's architectural journey as a map of the Great Work (opus magnum).",
        "significance": "The most important alchemical reading of the HP before the modern period. Beroalde's interpretation established the tradition of reading Poliphilo's journey as an alchemical process, a tradition that would continue through Hand B's annotations in the BL copy and into modern scholarship. Connects the HP to the broader 17th-century vogue for alchemical emblem books.",
        "woodcut_info": "Reuses and adapts earlier woodcut designs. The visual program is recontextualized through Beroalde's alchemical hermeneutic.",
        "digital_facsimile_url": "http://architectura.cesr.univ-tours.fr/Traite/Notice/CESR_4023.asp?param=",
    },
    {
        "title": "Hypnerotomachia Poliphili (Godwin Translation)",
        "year": 1999,
        "city": "London / New York",
        "printer_publisher": "Thames & Hudson",
        "translator": "Joscelyn Godwin",
        "language": "English",
        "edition_type": "MODERN_TRANSLATION",
        "description": "The first complete English translation, published on the 500th anniversary of the original. Translated by Joscelyn Godwin with an introduction by Alberto Perez-Gomez. Set in the Poliphilus typeface (Monotype's 1923 revival of Griffo's original), creating a visual continuity with the 1499 edition.",
        "significance": "Made the complete HP available in English for the first time. Widely used as the standard scholarly reference translation. The Thames & Hudson edition includes all 172 woodcuts and extensive notes. Published simultaneously with the 500th anniversary scholarly conferences.",
    },
    {
        "title": "Hypnerotomachia Poliphili (Ariani & Gabriele Critical Edition)",
        "year": 1998,
        "city": "Milan",
        "printer_publisher": "Adelphi",
        "language": "Italian (with critical apparatus)",
        "edition_type": "CRITICAL_EDITION",
        "description": "The standard modern Italian critical edition, edited by Marco Ariani and Mino Gabriele. Includes the complete original text with extensive philological notes, commentary, and scholarly apparatus.",
        "significance": "The definitive scholarly edition for Italian-language research. Supersedes the earlier Pozzi & Ciapponi critical edition (Padua, 1980) in scope and commentary.",
    },
    {
        "title": "Hypnerotomachia Poliphili (Pozzi & Ciapponi Critical Edition)",
        "year": 1980,
        "city": "Padua",
        "printer_publisher": "Antenore",
        "language": "Italian (with critical apparatus)",
        "edition_type": "CRITICAL_EDITION",
        "description": "The first modern critical edition, edited by Giovanni Pozzi and Lucia A. Ciapponi. Established the scholarly framework for systematic study of the HP text.",
        "significance": "The foundational critical edition that enabled modern HP scholarship. Pozzi's philological analysis of Colonna's macaronic language remains authoritative.",
    },
]


# ============================================================
# SCHOLARS DATA (new entries not already in the database)
# ============================================================

SCHOLARS = [
    {
        "name": "Liane Lefaivre",
        "nationality": "Canadian",
        "specialization": "Architectural history",
        "hp_focus": "Argues for Leon Battista Alberti's authorship based on architectural theories. Author of the MIT Press monograph on the HP (1997).",
        "bio_notes": "Architectural historian who authored the influential monograph 'Leon Battista Alberti's Hypnerotomachia Poliphili' (MIT Press, 1997), accompanied by the MIT electronic edition.",
    },
    {
        "name": "Efthymia Priki",
        "nationality": "Greek",
        "specialization": "Garden history, Renaissance studies",
        "hp_focus": "Explored the historical trajectory of the HP garden within landscape design. Analyzed the narrative function of the book's hieroglyphs.",
        "bio_notes": "Scholar focusing on garden design in Renaissance literature.",
    },
    {
        "name": "Tamara Griggs",
        "nationality": "American",
        "specialization": "Renaissance studies, court culture",
        "hp_focus": "Situated the HP as an antiquarian enterprise within 15th-century courtly culture and 'service professionals'.",
        "bio_notes": "Scholar of Renaissance court culture and antiquarianism.",
    },
    {
        "name": "Linda Fierz-David",
        "nationality": "Swiss",
        "specialization": "Jungian psychology",
        "hp_focus": "Authored 'The Dream of Poliphilo' — a Jungian analysis focusing on the anima and individuation process in the HP narrative.",
        "bio_notes": "Jungian analyst who produced one of the most influential psychological readings of the HP.",
        "death_year": 1955,
    },
    {
        "name": "Roswitha Stewering",
        "nationality": "German",
        "specialization": "Architectural history",
        "hp_focus": "Investigated the role of the dream in architectural compositions within the HP. Analyzed architectural representations in the 1499 woodcuts.",
        "bio_notes": "Architectural historian specializing in Renaissance dream architecture.",
    },
    {
        "name": "Esteban Alejandro Cruz",
        "nationality": "Argentine",
        "specialization": "Digital reconstruction, architectural visualization",
        "hp_focus": "Developed the Formas Imaginisque Poliphili (F.I.P.) project — 3D reconstructions of the HP's architecture using CAD, polygon modeling, and environmental simulation.",
        "bio_notes": "Creator of the F.I.P. project that produced vectorial and 3D polygon reconstructions of the Great Pyramid, the Baths of the Five Nymphs, and the Temple of Venus Physizoa.",
    },
    {
        "name": "Anthony Blunt",
        "birth_year": 1907,
        "death_year": 1983,
        "nationality": "British",
        "specialization": "Art history, French baroque",
        "hp_focus": "Analyzed the HP's reception and influence on 17th-century French royal entries and spectacle.",
        "bio_notes": "Surveyor of the King's Pictures, art historian, and Soviet spy. His scholarship on the HP's French reception remains influential.",
        "is_historical_subject": True,
    },
    {
        "name": "Alberto Perez-Gomez",
        "nationality": "Mexican-Canadian",
        "specialization": "Architectural theory, phenomenology",
        "hp_focus": "Identified 'desire' as the erotic gap between parts not-yet-joined, driving the constructive act of concinnitas. Authored 'Polyphilo, or The Dark Forest Revisited' (MIT Press, 1994).",
        "bio_notes": "Bronfman Professor of Architectural History at McGill University. Phenomenological approach to architectural meaning.",
    },
    {
        "name": "Francesco Griffo",
        "birth_year": 1450,
        "death_year": 1518,
        "nationality": "Italian",
        "specialization": "Type design, punchcutting",
        "hp_focus": "Cut the Roman typeface used in the 1499 HP — the foundation of modern Roman type. His reduction of lowercase letter weight created the 'superbly harmonious effect' that defined Aldine typography.",
        "bio_notes": "Bolognese punchcutter who created the typefaces for Aldus Manutius. His Roman type, first used for Bembo's De Aetna (1496) and perfected in the HP (1499), is the ancestor of all modern Roman typefaces.",
        "is_historical_subject": True,
    },
    {
        "name": "Jean Cousin the Elder",
        "birth_year": 1490,
        "death_year": 1560,
        "nationality": "French",
        "specialization": "Painting, printmaking, stained glass",
        "hp_focus": "Attributed as the designer of the new Mannerist woodcuts in the 1546 French edition (Le Songe de Poliphile), reinterpreting the Italian originals through a French aesthetic.",
        "bio_notes": "French Renaissance artist known for Eva Prima Pandora. His HP woodcuts represent a French Mannerist reinterpretation of the Italian originals.",
        "is_historical_subject": True,
    },
    {
        "name": "Beroalde de Verville",
        "birth_year": 1556,
        "death_year": 1626,
        "nationality": "French",
        "specialization": "Literature, alchemy, mathematics",
        "hp_focus": "Produced the 'Tableau des riches inventions' (1600), a radical alchemical reinterpretation of the HP that established the tradition of reading Poliphilo's journey as an alchemical opus.",
        "bio_notes": "French polymath who read the HP as an encoded alchemical treatise. His 1600 adaptation is the most important alchemical reading before the modern period.",
        "is_historical_subject": True,
    },
    {
        "name": "Joscelyn Godwin",
        "birth_year": 1945,
        "nationality": "British-American",
        "specialization": "Musicology, esotericism",
        "hp_focus": "Produced the first complete English translation of the HP (1999, Thames & Hudson), published on the 500th anniversary. The standard scholarly reference translation.",
        "bio_notes": "Professor of Music at Colgate University. Translator and scholar of Western esotericism.",
    },
]


# ============================================================
# DICTIONARY TERMS
# ============================================================

DICTIONARY_TERMS = [
    {
        "term": "concinnitas",
        "definition": "The Albertian principle of harmonious composition in which all parts are so perfectly arranged that nothing can be added, taken away, or altered without diminishing the whole.",
        "significance_to_hp": "The HP's architecture embodies concinnitas through its obsessive attention to proportion, material, and ornament. Poliphilo's buildings achieve a perfection of parts-to-whole relationship that reflects Alberti's aesthetic ideal.",
        "significance_to_scholarship": "Alberto Perez-Gomez identifies concinnitas as the constructive act driven by desire — the erotic gap between parts not-yet-joined. This reading connects architectural theory to the HP's love narrative.",
    },
    {
        "term": "recombinant design",
        "definition": "Liane Lefaivre's term for the HP's architectural methodology: taking valid precedents from antiquity and combining them into visionary new forms that transcend their sources.",
        "significance_to_hp": "The first building Poliphilo encounters is a hybrid of temple, triumphal arch, pyramid, obelisk, and labyrinth. This combinatorial logic defines Colonna's architectural imagination.",
        "significance_to_scholarship": "Lefaivre's concept explains how the HP's buildings are neither pure fantasy nor faithful reconstructions but a systematic recombination of classical elements.",
    },
    {
        "term": "phantasia logistike",
        "definition": "From Aristotelian psychology: the rational faculty of the imagination that combines and recombines sensory images stored in memory to produce new composite mental pictures.",
        "significance_to_hp": "Poliphilo's dream journey can be read as an exercise in phantasia logistike — the systematic combination of architectural, natural, and mythological images into new composite visions.",
        "significance_to_scholarship": "This Aristotelian framework explains why the HP's architecture feels both familiar and impossible: it is built from real classical elements recombined through the 'phantastic' faculty.",
    },
    {
        "term": "symmetry norm",
        "definition": "The Renaissance aesthetic principle that nature's forms must be ordered and symmetric to be beautiful, replacing the medieval preference for enclosed, irregular garden spaces.",
        "significance_to_hp": "The HP's gardens document the transition from the medieval hortus conclusus to the Renaissance ideal of geometric order. The gardens of Cythera embody the symmetry norm at its most extreme.",
        "significance_to_scholarship": "The HP influenced landscape architects across Europe. The gardens of Bomarzo are regarded by some scholars as literal illustrations of scenes from the HP.",
    },
    {
        "term": "hortus conclusus",
        "definition": "The 'enclosed garden' of medieval tradition — a walled garden space associated with the Virgin Mary, privacy, and contemplation. Contrasted with the Renaissance open, geometric garden.",
        "significance_to_hp": "Poliphilo's journey moves from enclosed, threatening spaces (the dark forest, the dragon's lair) toward increasingly open, ordered gardens. This spatial progression mirrors the historical shift from medieval to Renaissance garden design.",
        "significance_to_scholarship": "The HP is a key document in garden history, recording the aesthetic transition from enclosed medieval gardens to the symmetrical designs that would culminate in Versailles.",
    },
    {
        "term": "imago mundi",
        "definition": "A literary genre presenting an imagined world through a physical journey across a cohesive landscape. The HP follows this tradition, mapping its entire narrative onto a traversable geography.",
        "significance_to_hp": "The HP's narrative structure is an imago mundi: Poliphilo's walk from forest to pyramid to palace to island constitutes a complete imagined world with consistent internal geography.",
        "significance_to_scholarship": "Understanding the HP as imago mundi connects it to medieval encyclopedia traditions and to later world-building literature (Morris, Tolkien).",
    },
    {
        "term": "macaronic prose",
        "definition": "A literary style mixing two or more languages, especially vernacular Italian with Latin. The HP's prose combines Italian syntax with heavily Latinate and Greek vocabulary, creating an 'extraordinarily exotic' hybrid language.",
        "significance_to_hp": "Colonna's macaronic style is not mere pedantry but a deliberate expressive strategy: the hybrid language mirrors the hybrid architecture and the dream-state fusion of ancient and modern.",
        "significance_to_scholarship": "The HP's language has been both celebrated and condemned. Modern scholars recognize it as a purposeful literary experiment, not a failure of style.",
    },
]


# ============================================================
# TIMELINE EVENTS
# ============================================================

TIMELINE_EVENTS = [
    (1496, None, "PUBLICATION", "Griffo's Roman type debuts in De Aetna",
     "Francesco Griffo's Roman typeface first used in Pietro Bembo's De Aetna, printed by Aldus Manutius. This type would reach maturity in the HP three years later.",
     "Venice"),
    (1499, None, "PUBLICATION", "Hypnerotomachia Poliphili published",
     "The first edition published by Aldus Manutius in Venice, December 1499. Commissioned by Leonardo Crasso. Contains 172 woodcuts and the first Arabic type in Europe.",
     "Venice"),
    (1545, None, "PUBLICATION", "Second Italian edition published",
     "Published by Paolo Manuzio (Aldus's son) reusing the original 1499 woodblocks. The BL copy C.60.o.12 of this edition was later annotated by Ben Jonson and an anonymous alchemist.",
     "Venice"),
    (1546, None, "PUBLICATION", "Le Songe de Poliphile — first French edition",
     "Translated by Jean Martin, published by Jacques Kerver in Paris. Features entirely new Mannerist woodcuts attributed to Jean Cousin the Elder.",
     "Paris"),
    (1592, None, "PUBLICATION", "First English edition: The Strife of Love in a Dream",
     "Partial translation (Book I only) by 'R.D.' (Robert Dallington), published by Simon Waterson in London.",
     "London"),
    (1600, None, "PUBLICATION", "Tableau des riches inventions — alchemical edition",
     "Beroalde de Verville's radical alchemical reinterpretation published in Paris. Establishes the tradition of reading the HP as an encoded alchemical treatise.",
     "Paris"),
    (1923, None, "OTHER", "Poliphilus typeface revival",
     "Stanley Morison directs the revival of Griffo's HP typeface for the Monotype Corporation, creating the 'Poliphilus' font. Later used for Godwin's 1999 translation.",
     "London"),
    (1929, None, "OTHER", "Bembo typeface revival",
     "Stanley Morison produces the Bembo typeface for Monotype, based on Griffo's earlier iteration for De Aetna. Becomes a standard of 20th-century book design.",
     "London"),
    (1947, None, "PUBLICATION", "Fierz-David publishes Jungian analysis",
     "Linda Fierz-David publishes 'The Dream of Poliphilo', a Jungian analysis focusing on the anima and individuation in the HP narrative.",
     "Zurich"),
    (1980, None, "PUBLICATION", "Pozzi & Ciapponi critical edition",
     "First modern critical edition published by Giovanni Pozzi and Lucia Ciapponi (Antenore, Padua). Establishes the philological framework for modern HP scholarship.",
     "Padua"),
    (1994, None, "PUBLICATION", "Perez-Gomez: Polyphilo, or The Dark Forest Revisited",
     "Alberto Perez-Gomez publishes architectural-phenomenological analysis of the HP through MIT Press.",
     "Cambridge, MA"),
    (1997, None, "PUBLICATION", "Lefaivre MIT Press monograph and electronic edition",
     "Liane Lefaivre publishes 'Leon Battista Alberti's Hypnerotomachia Poliphili' with MIT Press. Accompanied by the MIT electronic facsimile — one of the earliest digital humanities projects.",
     "Cambridge, MA"),
    (1998, None, "PUBLICATION", "Ariani & Gabriele critical edition",
     "Marco Ariani and Mino Gabriele publish the standard modern Italian critical edition through Adelphi.",
     "Milan"),
    (1999, None, "PUBLICATION", "Godwin English translation — 500th anniversary",
     "Joscelyn Godwin publishes the first complete English translation (Thames & Hudson). Set in the Poliphilus typeface. Published on the 500th anniversary of the original.",
     "London"),
    (2021, None, "OTHER", "Alexander Moosbrugger: Wind (opera)",
     "Modern opera inspired by the HP, staging the search for Polia using Reiser and Godwin translations.",
     None),
]


# ============================================================
# BIBLIOGRAPHY ENTRIES
# ============================================================

BIBLIOGRAPHY = [
    ("Anthony Blunt", "The Hypnerotomachia Poliphili in 17th Century France", None,
     "article", "Journal of the Warburg and Courtauld Institutes",
     "French reception, royal entries", "http://www.jstor.org/pss/750050"),
    ("Liane Lefaivre", "Leon Battista Alberti's Hypnerotomachia Poliphili", "1997",
     "book", "MIT Press",
     "Alberti authorship, recombinant design", None),
    ("Efthymia Priki", "Untangling the Knot: Garden Design in the Hypnerotomachia Poliphili", None,
     "article", None,
     "Garden history, landscape design", "https://www.researchgate.net/publication/264043803"),
    ("Tamara Griggs", "Hypnerotomachia Poliphili", None,
     "article", None,
     "Antiquarianism, court culture", None),
    ("Linda Fierz-David", "The Dream of Poliphilo", "1947",
     "book", None,
     "Jungian analysis, anima, individuation", None),
    ("Roswitha Stewering", "Architectural Representations in the Hypnerotomachia Poliphili", None,
     "article", None,
     "Dream architecture, architectural composition", "https://www.researchgate.net/publication/274742971"),
    ("Alberto Perez-Gomez", "Polyphilo, or The Dark Forest Revisited", "1994",
     "book", "MIT Press",
     "Phenomenology, desire, architectural meaning", None),
    ("Joscelyn Godwin", "Hypnerotomachia Poliphili: The Strife of Love in a Dream (translation)", "1999",
     "book", "Thames & Hudson",
     "Complete English translation, 500th anniversary", None),
    ("Esteban Alejandro Cruz", "Hypnerotomachia Poliphili: An Architectural Vision from the First Renaissance", None,
     "book", None,
     "F.I.P. project, 3D reconstruction, digital reconstruction", None),
    ("Giovanni Pozzi and Lucia A. Ciapponi", "Hypnerotomachia Poliphili (critical edition)", "1980",
     "book", "Antenore (Padua)",
     "Critical edition, philological analysis", None),
    ("Marco Ariani and Mino Gabriele", "Hypnerotomachia Poliphili (critical edition)", "1998",
     "book", "Adelphi (Milan)",
     "Critical edition, modern Italian commentary", None),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # --- EDITIONS ---
    print("=== Seeding Editions ===")
    ed_count = 0
    for ed in EDITIONS:
        slug = slugify(ed["title"])
        existing = cur.execute("SELECT id FROM editions WHERE slug=?", (slug,)).fetchone()
        if existing:
            print(f"  SKIP: {ed['title'][:50]} (exists)")
            continue
        if args.dry_run:
            print(f"  DRY: {ed['title'][:50]}")
            ed_count += 1
            continue
        cur.execute("""
            INSERT INTO editions (title, year, city, printer_publisher, translator,
                language, edition_type, description, significance, woodcut_info,
                digital_facsimile_url, worldcat_url, extant_copies, slug)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            ed["title"], ed["year"], ed.get("city"), ed.get("printer_publisher"),
            ed.get("translator"), ed.get("language"), ed.get("edition_type"),
            ed.get("description"), ed.get("significance"), ed.get("woodcut_info"),
            ed.get("digital_facsimile_url"), ed.get("worldcat_url"),
            ed.get("extant_copies"), slug
        ))
        ed_count += 1
        print(f"  Added: {ed['title'][:50]}")
    print(f"  Editions: {ed_count} added")

    # --- SCHOLARS ---
    print("\n=== Seeding Scholars ===")
    sc_count = 0
    for sc in SCHOLARS:
        existing = cur.execute("SELECT id FROM scholars WHERE name=?", (sc["name"],)).fetchone()
        if existing:
            print(f"  SKIP: {sc['name']} (exists)")
            continue
        if args.dry_run:
            print(f"  DRY: {sc['name']}")
            sc_count += 1
            continue
        cur.execute("""
            INSERT INTO scholars (name, birth_year, death_year, nationality,
                specialization, hp_focus, bio_notes, is_historical_subject,
                source_method)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            sc["name"], sc.get("birth_year"), sc.get("death_year"),
            sc.get("nationality"), sc.get("specialization"),
            sc.get("hp_focus"), sc.get("bio_notes"),
            sc.get("is_historical_subject", False),
            "LLM_ASSISTED"
        ))
        sc_count += 1
        print(f"  Added: {sc['name']}")
    print(f"  Scholars: {sc_count} added")

    # --- DICTIONARY TERMS ---
    print("\n=== Seeding Dictionary Terms ===")
    dt_count = 0
    for dt in DICTIONARY_TERMS:
        slug = slugify(dt["term"])
        existing = cur.execute("SELECT id FROM dictionary_terms WHERE slug=?", (slug,)).fetchone()
        if existing:
            print(f"  SKIP: {dt['term']} (exists)")
            continue
        if args.dry_run:
            print(f"  DRY: {dt['term']}")
            dt_count += 1
            continue
        cur.execute("""
            INSERT INTO dictionary_terms (label, slug, category, definition_short,
                significance_to_hp, significance_to_scholarship,
                source_method, review_status)
            VALUES (?,?,?,?,?,?,?,?)
        """, (
            dt["term"], slug, "CONCEPT", dt["definition"],
            dt["significance_to_hp"], dt["significance_to_scholarship"],
            "LLM_ASSISTED", "DRAFT"
        ))
        dt_count += 1
        print(f"  Added: {dt['term']}")
    print(f"  Dictionary terms: {dt_count} added")

    # --- TIMELINE EVENTS ---
    print("\n=== Seeding Timeline Events ===")
    te_count = 0
    for year, year_end, etype, title, desc, location in TIMELINE_EVENTS:
        existing = cur.execute(
            "SELECT id FROM timeline_events WHERE year=? AND title=?",
            (year, title)
        ).fetchone()
        if existing:
            print(f"  SKIP: {year} {title[:40]} (exists)")
            continue
        if args.dry_run:
            print(f"  DRY: {year} {title[:40]}")
            te_count += 1
            continue
        cur.execute("""
            INSERT INTO timeline_events (year, year_end, event_type, title,
                description, location, source_method, category)
            VALUES (?,?,?,?,?,?,?,?)
        """, (
            year, year_end, etype, title, desc, location,
            "LLM_ASSISTED", "HP_RECEPTION"
        ))
        te_count += 1
        print(f"  Added: {year} {title[:40]}")
    print(f"  Timeline events: {te_count} added")

    # --- BIBLIOGRAPHY ---
    print("\n=== Seeding Bibliography ===")
    bib_count = 0
    for author, title, year, ptype, journal, topic, url in BIBLIOGRAPHY:
        existing = cur.execute(
            "SELECT id FROM bibliography WHERE author=? AND title=?",
            (author, title)
        ).fetchone()
        if existing:
            print(f"  SKIP: {author[:20]} — {title[:30]} (exists)")
            continue
        if args.dry_run:
            print(f"  DRY: {author[:20]} — {title[:30]}")
            bib_count += 1
            continue
        cur.execute("""
            INSERT INTO bibliography (author, title, year, pub_type,
                journal_or_publisher, topic_cluster, cited_in, notes)
            VALUES (?,?,?,?,?,?,?,?)
        """, (
            author, title, year, ptype, journal, topic,
            "HPDEEPRESEARCH.txt", url
        ))
        bib_count += 1
        print(f"  Added: {author[:20]} — {title[:30]}")
    print(f"  Bibliography: {bib_count} added")

    if not args.dry_run:
        conn.commit()
    conn.close()

    print(f"\n=== TOTALS: {ed_count} editions, {sc_count} scholars, "
          f"{dt_count} terms, {te_count} events, {bib_count} bib entries ===")


if __name__ == "__main__":
    main()
