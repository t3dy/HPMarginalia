# HPython — All Python Scripts

Concatenated from `scripts/` directory. 2026-03-18

## Table of Contents

- [add_bibliography.py](#add-bibliography) (327 lines)
- [add_hands.py](#add-hands) (443 lines)
- [build_essay_data.py](#build-essay-data) (318 lines)
- [build_reading_packets.py](#build-reading-packets) (158 lines)
- [build_scholar_profiles.py](#build-scholar-profiles) (283 lines)
- [build_signature_map.py](#build-signature-map) (103 lines)
- [build_site.py](#build-site) (1434 lines)
- [catalog_images.py](#catalog-images) (174 lines)
- [chunk_documents.py](#chunk-documents) (261 lines)
- [corpus_search.py](#corpus-search) (220 lines)
- [dictionary_audit.py](#dictionary-audit) (160 lines)
- [enrich_dictionary.py](#enrich-dictionary) (170 lines)
- [export_showcase_data.py](#export-showcase-data) (116 lines)
- [extract_references.py](#extract-references) (176 lines)
- [ingest_perplexity.py](#ingest-perplexity) (217 lines)
- [init_db.py](#init-db) (191 lines)
- [match_refs_to_images.py](#match-refs-to-images) (142 lines)
- [migrate_dictionary_v2.py](#migrate-dictionary-v2) (55 lines)
- [migrate_v2.py](#migrate-v2) (389 lines)
- [pdf_to_markdown.py](#pdf-to-markdown) (373 lines)
- [seed_dictionary.py](#seed-dictionary) (429 lines)
- [validate.py](#validate) (264 lines)

---

## add_bibliography

`scripts/add_bibliography.py`

```python
"""Add bibliography table and populate with works cited in Russell's dissertation.

Tracks which works we have vs. which are cited but missing from our collection.
Enables gap analysis for scholarship expansion.
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS bibliography (
    id INTEGER PRIMARY KEY,
    author TEXT NOT NULL,
    title TEXT NOT NULL,
    year TEXT,
    pub_type TEXT CHECK(pub_type IN ('article','book','chapter','thesis','manuscript')),
    journal_or_publisher TEXT,
    cited_in TEXT DEFAULT 'Russell 2014',
    in_collection BOOLEAN DEFAULT 0,
    collection_filename TEXT,
    hp_relevance TEXT CHECK(hp_relevance IN ('PRIMARY','DIRECT','INDIRECT','TANGENTIAL')),
    topic_cluster TEXT,
    notes TEXT,
    UNIQUE(author, title)
);

CREATE TABLE IF NOT EXISTS scholars (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    birth_year INTEGER,
    death_year INTEGER,
    nationality TEXT,
    institution TEXT,
    specialization TEXT,
    hp_focus TEXT,
    bio_notes TEXT,
    work_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS scholar_works (
    scholar_id INTEGER REFERENCES scholars(id),
    bib_id INTEGER REFERENCES bibliography(id),
    PRIMARY KEY (scholar_id, bib_id)
);

CREATE TABLE IF NOT EXISTS timeline_events (
    id INTEGER PRIMARY KEY,
    year INTEGER NOT NULL,
    year_end INTEGER,
    event_type TEXT CHECK(event_type IN (
        'PUBLICATION','EDITION','TRANSLATION','DISCOVERY',
        'ATTRIBUTION','ACQUISITION','EXHIBITION','OTHER'
    )),
    title TEXT NOT NULL,
    description TEXT,
    scholar_id INTEGER REFERENCES scholars(id),
    bib_id INTEGER REFERENCES bibliography(id),
    manuscript_shelfmark TEXT
);
"""

# High-priority HP-specific works from Russell's bibliography
# that we do NOT have in our collection
HP_BIBLIOGRAPHY = [
    # --- Works we HAVE ---
    ('James Russell', 'Many Other Things Worthy of Knowledge and Memory: The Hypnerotomachia Poliphili and its Annotators, 1499-1700', '2014', 'thesis', 'Durham University', True, 'PhD_Thesis_ _James_Russell Hypnerotomachia Polyphili.pdf', 'DIRECT', 'reception'),
    ('Anthony Blunt', 'The Hypnerotomachia Poliphili in 17th Century France', '1937', 'article', 'Journal of the Warburg Institute 1:2', True, None, 'DIRECT', 'reception'),
    ('Mario Praz', 'Some Foreign Imitators of the Hypnerotomachia Poliphili', '1947', 'article', 'Italica 24:1', True, None, 'DIRECT', 'reception'),
    ('Liane Lefaivre', "Leon Battista Alberti's Hypnerotomachia Poliphili", '1997', 'book', 'MIT Press', True, None, 'DIRECT', 'authorship'),
    ('Rosemary Trippe', 'The Hypnerotomachia Poliphili: Image, Text, and Vernacular Poetics', '2002', 'article', 'Renaissance Quarterly 55:4', True, None, 'DIRECT', 'text_image'),
    ('L.E. Semler', "Robert Dallington's Hypnerotomachia and the Protestant Antiquity of Elizabethan England", '2006', 'article', 'Studies in Philology 103:2', True, None, 'DIRECT', 'reception'),
    ('John Dixon Hunt', 'Experiencing Gardens in the Hypnerotomachia Poliphili', '1998', 'article', 'Word & Image 14:1-2', True, None, 'DIRECT', 'architecture_gardens'),
    ('Roswitha Stewering', 'Architectural Representations in the Hypnerotomachia Poliphili', '2000', 'article', 'Journal of the SAH 59:1', True, None, 'DIRECT', 'architecture_gardens'),
    ('Efthymia Priki', 'Elucidating and Enigmatizing: the Reception of the HP', '2009', 'article', 'eSharp 14', True, None, 'DIRECT', 'reception'),

    # --- HIGH PRIORITY GAPS: foundational HP scholarship ---
    ('Maria Teresa Casella & Giovanni Pozzi', 'Francesco Colonna. Biografia e opere', '1959', 'book', 'Antenore, Padua', False, None, 'DIRECT', 'authorship'),
    ('Maurizio Calvesi', "La pugna d'amore in sogno di Francesco Colonna Romano", '1996', 'book', 'Lithos Editrice, Rome', False, None, 'DIRECT', 'authorship'),
    ('Myriam Billanovich & Emilio Menegazzo', 'Francesco Colonna tra Padova e Venezia', '1966', 'article', 'Italia medioevale e umanistica 9', False, None, 'DIRECT', 'authorship'),
    ('Myriam Billanovich', 'Francesco Colonna, il Poliphilo e la famiglia Lelli', '1968', 'article', 'Italia medioevale e umanistica 19', False, None, 'DIRECT', 'authorship'),
    ('Myriam Billanovich', 'Francesco Colonna e la famiglia Lelli', '1976', 'article', 'Italia medioevale e umanistica 19', False, None, 'DIRECT', 'authorship'),
    ('Domenico Gnoli', 'Il Sogno di Polifilo', '1899', 'article', 'La Bibliofilia 1', False, None, 'DIRECT', 'authorship'),
    ('Christian Huelsen', 'Le illustrazioni della Hypnerotomachia Poliphili', '1910', 'article', 'La Bibliofilia 12', False, None, 'DIRECT', 'text_image'),
    ('E.H. Gombrich', 'Hypnerotomachiana', '1972', 'chapter', 'in Symbolic Images, Phaidon', False, None, 'DIRECT', 'text_image'),
    ('Giorgio Agamben', 'Il Sogno della lingua. Per una lettura del Polifilo', '1984', 'chapter', 'in I linguaggi del sogno, Olschki', False, None, 'DIRECT', 'dream_religion'),
    ('George D. Painter', 'The Hypnerotomachia Poliphilo of 1499', '1963', 'book', 'Eugrammia Press, London', False, None, 'DIRECT', 'material_bibliographic'),
    ('Giovanni Pozzi', 'Il Polifilo nella storia del libro illustrato veneziano', '1981', 'chapter', 'in Giorgione e l\'Umanesimo veneziano', False, None, 'DIRECT', 'text_image'),
    ('Linda Fierz-David', 'The Dream of Poliphilo', '1987', 'book', 'Spring Publications, Dallas', False, None, 'DIRECT', 'dream_religion'),
    ('A. Khomentovskaia', "Felice Feliciano da Verona comme l'auteur de l'HP", '1935', 'article', 'La Bibliofilia 37-38', False, None, 'DIRECT', 'authorship'),
    ('Emanuela Kretzulesco-Quaranta', 'Les Jardins du Songe', '1976', 'book', 'Les Belles Lettres', False, None, 'DIRECT', 'architecture_gardens'),
    ('Charles Nodier', 'Franciscus Columna', '1844', 'book', 'Galerie des Beaux-Arts, Paris', False, None, 'DIRECT', 'reception'),
    ('Peter Dronke', 'Introduction [to HP]', '1981', 'chapter', 'Las Ediciones del Portico, Madrid', False, None, 'DIRECT', 'reception'),
    ('Edoardo Fumagalli', "Francesco Colonna lettore di Apuleio", '1984', 'article', 'Italia medioevale e umanistica 27', False, None, 'DIRECT', 'authorship'),
    ('Edoardo Fumagalli', "Due esemplari dell'Hypnerotomachia Poliphili", '1992', 'article', 'Aevum 66', False, None, 'DIRECT', 'material_bibliographic'),
    ('Dorothea Stichel', 'Reading the HP in the Cinquecento', '1994', 'chapter', 'in Aldus Manutius and Renaissance Culture', False, None, 'DIRECT', 'reception'),
    ('William H. Sherman', 'Used Books', '2007', 'book', 'University of Pennsylvania Press', False, None, 'INDIRECT', 'reception'),
    ('Carlo Caruso', "Un geroglifico dell'Hypnerotomachia Poliphili", '2004', 'article', 'Filologia italiana 1', False, None, 'DIRECT', 'text_image'),
    ('Alfredo Perifano', 'Nazari et Colonna: La Reecriture Alchimique', '2004', 'article', "Bibliotheque d'Humanisme et Renaissance 66:2", False, None, 'DIRECT', 'dream_religion'),
    ('N. Harris', 'Rising quadrats in the woodcuts of the Aldine HP', '2002', 'article', 'Gutenberg Jahrbuch 77', False, None, 'DIRECT', 'material_bibliographic'),
    ('Kent Hieatt & Anne Lake Prescott', 'Contemporizing Antiquity', '1992', 'article', 'Word and Image 8', False, None, 'DIRECT', 'text_image'),
    ('Philip Hofer', 'Variant Copies of the 1499 Poliphilus', '1932', 'article', 'Bulletin of the NYPL 36', False, None, 'DIRECT', 'material_bibliographic'),
    ('Helena Szepe', 'Artistic Identity in the Poliphilo', '1997', 'article', 'Papers of the BSC 35:1', False, None, 'DIRECT', 'text_image'),
    ('Benedetto Croce', 'La Hypnerotomachia Polyphili', '1950', 'article', 'Quaderni della Critica 4', False, None, 'DIRECT', 'reception'),
    ('Fritz Saxl', 'A Scene from the HP in a Painting by Garofalo', '1937', 'article', 'Journal of the Warburg Institute 1', False, None, 'DIRECT', 'text_image'),
    ('Lamberto Donati', 'Diciamo qualcosa del Polifilo!', '1938', 'article', 'Maso Finiguerra 3', False, None, 'DIRECT', 'reception'),
    ('Lamberto Donati', 'Studio esegetico sul Polifilo', '1950', 'article', 'La Bibliofilia 52', False, None, 'DIRECT', 'reception'),
    ('William S. Heckscher', "Bernini's Elephant and Obelisk", '1947', 'article', 'Art Bulletin 29', False, None, 'DIRECT', 'architecture_gardens'),
    ('William M. Ivins Jr.', 'The Aldine Hypnerotomachia Poliphili of 1499', '1923', 'article', 'Metropolitan Museum of Art Bulletin 18:12', False, None, 'DIRECT', 'material_bibliographic'),
    ('Sophie Huper', 'The Architectural Monuments of the HP', '1956', 'thesis', 'State University of Iowa', False, None, 'DIRECT', 'architecture_gardens'),
    ('Silvia Fogliati & David Dutto', 'Il Giardino di Polifilo', '2002', 'book', 'Franco Maria Ricci, Milan', False, None, 'DIRECT', 'architecture_gardens'),
    ('A. Perez-Gomez', 'Polyphilo, or The Dark Forest Revisited', '1994', 'book', 'MIT Press', False, None, 'DIRECT', 'architecture_gardens'),
    ('Anthony Colantuono', 'Titian, Colonna, and the Renaissance Science of Procreation', '2010', 'book', 'Ashgate', False, None, 'DIRECT', 'text_image'),
    ('Esteban Alejandro Cruz', 'Re-Discovering Antiquity through the Dreams of Poliphilus', '2006', 'book', 'Trafford, Oxford', False, None, 'DIRECT', 'architecture_gardens'),
    ('Helen Barolini', 'Aldus and his Dream Book', '1992', 'book', 'Italica Press, New York', False, None, 'DIRECT', 'material_bibliographic'),
    ('A. Serena', "Gli elementi trevigiani dell'HP", '1926', 'article', 'Atti del Reale Istituto Veneto 86:2', False, None, 'DIRECT', 'authorship'),
    ('Giuseppe Biadego', 'Intorno al sogno di Polifilo', '1900', 'article', 'Atti del Reale Istituto Veneto 60:2', False, None, 'DIRECT', 'authorship'),
    ('Emilio Menegazzo', 'Per la biografia di Francesco Colonna', '1962', 'article', 'Italia medioevale e umanistica 5', False, None, 'DIRECT', 'authorship'),
    ('Emilio Menegazzo', 'Francesco Colonna baccelliere nello Studio', '1966', 'article', 'Italia medioevale e umanistica 11', False, None, 'DIRECT', 'authorship'),
    ('Yasamin Bahadorzadeh', 'Silent Theatre', '2008', 'book', 'VDM Verlag Dr. Muller', False, None, 'DIRECT', 'architecture_gardens'),
    ('Marcel Francon', "Francesco Colonna's Poliphili Hypnerotomachia and Pantagruel", '1954', 'article', 'Italica 31:3', False, None, 'DIRECT', 'reception'),

    # --- TIMELINE ANCHORS: editions and translations ---
    ('Francesco Colonna', 'Hypnerotomachia Poliphili', '1499', 'book', 'Aldus Manutius, Venice', False, None, 'PRIMARY', 'text_image'),
    ('Francesco Colonna', 'La Hypnerotomachia di Poliphilo (2nd edition)', '1545', 'book', 'Figlioli di Aldo, Venice', False, None, 'PRIMARY', 'text_image'),
    ('Jean Martin (trans.)', 'Discours du Songe de Poliphile', '1546', 'book', 'Jacques Kerver, Paris', False, None, 'PRIMARY', 'reception'),
    ('R.D. (trans.)', 'The Strife of Love in a Dreame', '1592', 'book', 'Simon Waterston, London', False, None, 'PRIMARY', 'reception'),
    ('Beroalde de Verville', 'Le Tableau des riches Inventions...dans le songe de Poliphile', '1600', 'book', 'Guillemot, Paris', False, None, 'PRIMARY', 'dream_religion'),
]

# Key scholars for profile pages
SCHOLARS = [
    ('Francesco Colonna', None, 1527, 'Italian', 'SS. Giovanni e Paolo, Venice', 'Dominican friar, presumed author', 'authorship (acrostic attribution)'),
    ('Aldus Manutius', 1449, 1515, 'Italian', 'Aldine Press, Venice', 'printer, publisher, humanist', 'published 1499 and 1545 editions'),
    ('Benedetto Giovio', 1471, 1545, 'Italian', 'Como', 'humanist, Plinian scholar', 'annotator of Modena and Como copies'),
    ('Paolo Giovio', 1483, 1552, 'Italian', 'Como / Rome', 'historian, biographer', 'brother of Benedetto; possible co-annotator'),
    ('Ben Jonson', 1572, 1637, 'English', 'London', 'playwright, poet', 'annotator of BL C.60.o.12 (1545 edition)'),
    ('Fabio Chigi (Pope Alexander VII)', 1599, 1667, 'Italian', 'Rome / Vatican', 'pope, patron, bibliophile', 'annotator of Vatican Chig.II.610'),
    ('Jean Martin', None, 1553, 'French', 'Paris', 'translator', '1546 French translation'),
    ('Beroalde de Verville', 1556, 1626, 'French', 'Tours', 'writer, alchemist', '1600 alchemical edition'),
    ("Jean d'Espagnet", 1564, 1637, 'French', None, 'alchemist, natural philosopher', "BL Hand B's alchemical framework"),
    ('Robert Dallington', 1561, 1637, 'English', None, 'diplomat, writer', '1592 English translation (R.D.)'),
    ('Giovanni Pozzi', 1923, 2002, 'Swiss-Italian', 'University of Fribourg', 'philologist', 'critical edition (1964, with Ciapponi)'),
    ('Liane Lefaivre', None, None, 'Canadian', 'TU Delft', 'architectural historian', 'Alberti attribution thesis (1997)'),
    ('Maurizio Calvesi', 1927, 2020, 'Italian', 'Sapienza, Rome', 'art historian', 'Roman Colonna attribution (1996)'),
    ('Maria Teresa Casella', None, None, 'Italian', None, 'philologist', 'biography and works (1959, with Pozzi)'),
    ('Dorothea Stichel', None, None, 'German', None, 'book historian', 'first study of Modena marginalia (1994)'),
    ('James Russell', None, None, 'British', 'Durham University', 'book historian, marginalia scholar', 'world census of annotated copies (2014)'),
    ('Efthymia Priki', None, None, 'Greek', None, 'literary scholar', 'hieroglyphs, narrative, text-image, reception'),
    ('James O\'Neill', None, None, 'British', 'Durham University', 'narratologist', 'self-transformation, authorship, walking methodology'),
    ('Myriam Billanovich', None, None, 'Italian', None, 'philologist', 'Francesco Colonna biography, Lelli family'),
    ('Emilio Menegazzo', None, None, 'Italian', None, 'philologist', 'Francesco Colonna biography'),
    ('Christian Huelsen', 1858, 1935, 'German', 'DAI Rome', 'archaeologist, topographer', 'HP woodcut illustrations (1910)'),
    ('E.H. Gombrich', 1909, 2001, 'Austrian-British', 'Warburg Institute', 'art historian', 'Hypnerotomachiana (1972)'),
    ('Anthony Blunt', 1907, 1983, 'British', 'Courtauld Institute', 'art historian', 'HP in 17th-century France (1937)'),
    ('Fritz Saxl', 1890, 1948, 'Austrian-British', 'Warburg Institute', 'art historian', 'HP scene in Garofalo painting (1937)'),
    ('Domenico Gnoli', 1838, 1915, 'Italian', 'Rome', 'literary historian', 'Il Sogno di Polifilo (1899)'),
    ('Charles Nodier', 1780, 1844, 'French', 'Bibliothèque de l\'Arsenal', 'librarian, writer', 'Franciscus Columna (1844)'),
    ('Georg Leidinger', 1870, 1945, 'German', 'Bayerische Staatsbibliothek', 'librarian, paleographer', "Dürer's ownership of HP (1929)"),
    ('Linda Fierz-David', None, None, 'Swiss', None, 'Jungian analyst', 'Dream of Poliphilo (1950/1987)'),
    ('Mario Praz', 1896, 1982, 'Italian', 'Sapienza, Rome', 'literary historian, anglicist', 'Foreign imitators of HP (1947)'),
]

# Timeline events
TIMELINE = [
    (1499, None, 'PUBLICATION', 'Hypnerotomachia Poliphili published', 'Aldus Manutius publishes the HP in Venice. 172 woodcuts. Author identified by acrostic as POLIAM FRATER FRANCISCVS COLVMNA PERAMAVIT.', 'text_image'),
    (1500, 1545, 'OTHER', 'Giovio brothers annotate Modena and Como copies', 'Benedetto Giovio applies Plinian encyclopedic reading to two copies.', 'reception'),
    (1545, None, 'EDITION', 'Second Aldine edition published', "Aldus' sons reprint the HP with recast woodcuts.", 'material_bibliographic'),
    (1546, None, 'TRANSLATION', 'French translation by Jean Martin', 'Published by Jacques Kerver in Paris with modified and additional woodcuts.', 'reception'),
    (1554, None, 'EDITION', 'Second French edition', 'Kerver reprints Martin translation.', 'material_bibliographic'),
    (1561, None, 'EDITION', 'Third French edition with Gohorry notice', 'Jacques Gohorry adds prefatory notice.', 'material_bibliographic'),
    (1592, None, 'TRANSLATION', 'English translation: The Strife of Love in a Dreame', 'R.D. (Robert Dallington) publishes partial English translation for Simon Waterston.', 'reception'),
    (1600, None, 'EDITION', "Beroalde de Verville's alchemical edition", 'Le Tableau des riches Inventions includes tableau steganographique of alchemical symbols.', 'dream_religion'),
    (1600, 1637, 'OTHER', 'Ben Jonson annotates BL copy', 'Jonson mines the 1545 HP for stage design imagery and linguistic material.', 'reception'),
    (1641, None, 'ACQUISITION', 'Thomas Bourne purchases BL copy', 'Recorded purchase date of May 6, 1641. Anonymous alchemist (Hand B) annotates after this date.', 'reception'),
    (1641, 1700, 'OTHER', "Anonymous alchemist annotates BL copy (d'Espagnet school)", "Hand B applies alchemical reading centering on 'Master Mercury' following d'Espagnet's framework.", 'dream_religion'),
    (1650, 1700, 'OTHER', 'Anonymous alchemist annotates Buffalo copy (pseudo-Geber school)', 'Hand E applies Geberian alchemical reading emphasizing Sol/Luna and sulphur.', 'dream_religion'),
    (1655, 1667, 'OTHER', 'Pope Alexander VII annotates Vatican copy', 'Fabio Chigi combs text for acutezze (verbal wit) and architectural parallels with Rome.', 'reception'),
    (1804, None, 'EDITION', 'Legrand edition (Paris)', 'J.G. Legrand publishes new French edition.', 'material_bibliographic'),
    (1844, None, 'PUBLICATION', "Nodier's Franciscus Columna", 'Charles Nodier publishes romanticized biography of Colonna.', 'reception'),
    (1883, None, 'EDITION', 'Popelin French translation', 'Claudius Popelin publishes new French translation.', 'material_bibliographic'),
    (1899, None, 'PUBLICATION', "Gnoli's Il Sogno di Polifilo", 'Domenico Gnoli publishes foundational study.', 'authorship'),
    (1904, None, 'EDITION', 'Methuen facsimile edition', 'London facsimile of 1499 edition.', 'material_bibliographic'),
    (1910, None, 'PUBLICATION', "Huelsen's study of HP woodcut illustrations", 'Christian Huelsen publishes analysis of woodcuts and their architectural sources.', 'text_image'),
    (1929, None, 'DISCOVERY', "Leidinger discovers Dürer's ownership inscription", "Georg Leidinger finds proof that Albrecht Dürer owned a copy of the HP, purchased by Erasmus Hock in 1555.", 'material_bibliographic'),
    (1935, None, 'ATTRIBUTION', 'Khomentovskaia proposes Felice Feliciano as author', 'Alternative attribution beyond Francesco Colonna.', 'authorship'),
    (1937, None, 'PUBLICATION', "Blunt's HP in 17th Century France", 'Anthony Blunt traces French reception. Saxl publishes on Garofalo painting.', 'reception'),
    (1947, None, 'PUBLICATION', "Praz's Foreign Imitators + Heckscher on Bernini's Elephant", "Praz traces HP influence on Swinburne, Beardsley, de Mandiargues. Heckscher publishes on Bernini's elephant and obelisk.", 'reception'),
    (1950, None, 'PUBLICATION', "Croce's La Hypnerotomachia; Fierz-David's Jungian reading", 'Croce publishes study. Fierz-David publishes Jungian interpretation (expanded 1987).', 'dream_religion'),
    (1959, None, 'PUBLICATION', 'Casella & Pozzi: Francesco Colonna. Biografia e opere', 'Foundational biographical study establishing the Venetian Dominican attribution.', 'authorship'),
    (1964, None, 'EDITION', 'Pozzi & Ciapponi critical edition', 'Giovanni Pozzi and Lucia Ciapponi publish critical edition with Antenore.', 'material_bibliographic'),
    (1966, None, 'PUBLICATION', 'Billanovich & Menegazzo: archival discoveries', 'Major archival work on Francesco Colonna and the Lelli family in Padua and Venice.', 'authorship'),
    (1972, None, 'PUBLICATION', "Gombrich's Hypnerotomachiana", 'E.H. Gombrich publishes study in Symbolic Images.', 'text_image'),
    (1976, None, 'PUBLICATION', "Kretzulesco-Quaranta's Les Jardins du Songe", 'Major study of HP garden symbolism.', 'architecture_gardens'),
    (1994, None, 'PUBLICATION', "Stichel's study of Modena marginalia; Perez-Gomez's Dark Forest", 'First study of an annotated copy. Perez-Gomez publishes architectural reading.', 'reception'),
    (1996, None, 'PUBLICATION', "Calvesi's La pugna d'amore in sogno", 'Major study arguing for a Roman Francesco Colonna rather than the Venetian Dominican.', 'authorship'),
    (1997, None, 'PUBLICATION', "Lefaivre's Alberti attribution", 'Liane Lefaivre proposes Leon Battista Alberti as author.', 'authorship'),
    (1998, None, 'PUBLICATION', 'Word & Image special issue on HP', 'Major scholarly collection: Hunt, Leslie, Bury, Curran, Griggs, Segre, Stewering, Temple.', 'architecture_gardens'),
    (1999, None, 'EDITION', "Godwin's English translation; Ariani & Gabriele critical edition", 'Joscelyn Godwin publishes full English translation (Thames & Hudson). Adelphi publishes Italian critical edition.', 'text_image'),
    (2002, None, 'PUBLICATION', "Trippe's Image, Text, and Vernacular Poetics", 'Rosemary Trippe recovers HP as vernacular literature.', 'text_image'),
    (2006, None, 'PUBLICATION', "Semler on Dallington's English HP", 'L.E. Semler rehabilitates 1592 English adaptation.', 'reception'),
    (2014, None, 'PUBLICATION', "Russell's world census of annotated copies", "James Russell's PhD thesis documents marginalia across six copies.", 'reception'),
    (2015, None, 'PUBLICATION', 'Word & Image special issue (2015)', 'Second major scholarly collection: Farrington, Nygren, Fabiani Giannetto, Pumroy, Keller.', 'material_bibliographic'),
    (2020, None, 'PUBLICATION', "O'Neill's Self-Transformation thesis", "James O'Neill's PhD thesis on Poliphilo's inner transformation.", 'architecture_gardens'),
]


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("Creating bibliography and scholars tables...")
    cur.executescript(SCHEMA)
    conn.commit()

    # Insert bibliography
    print("Inserting bibliography entries...")
    bib_count = 0
    for entry in HP_BIBLIOGRAPHY:
        author, title, year, pub_type, journal, in_coll, filename, relevance, topic = entry
        cur.execute(
            """INSERT OR IGNORE INTO bibliography
               (author, title, year, pub_type, journal_or_publisher,
                in_collection, collection_filename, hp_relevance, topic_cluster)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (author, title, year, pub_type, journal, in_coll, filename, relevance, topic)
        )
        bib_count += cur.rowcount
    conn.commit()
    print(f"  Inserted {bib_count} bibliography entries")

    # Insert scholars
    print("Inserting scholar profiles...")
    scholar_count = 0
    for s in SCHOLARS:
        name, birth, death, nat, inst, spec, hp_focus = s
        cur.execute(
            """INSERT OR IGNORE INTO scholars
               (name, birth_year, death_year, nationality, institution,
                specialization, hp_focus)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (name, birth, death, nat, inst, spec, hp_focus)
        )
        scholar_count += cur.rowcount
    conn.commit()
    print(f"  Inserted {scholar_count} scholar profiles")

    # Link scholars to bibliography
    print("Linking scholars to works...")
    link_count = 0
    for entry in HP_BIBLIOGRAPHY:
        author = entry[0]
        title = entry[1]
        # Find scholar by name match (first author)
        first_author = author.split(' & ')[0].split(' (')[0].strip()
        # Try last name match
        last_name = first_author.split()[-1] if first_author else None
        if not last_name:
            continue
        cur.execute("SELECT id FROM scholars WHERE name LIKE ?", (f'%{last_name}%',))
        scholar_row = cur.fetchone()
        if not scholar_row:
            continue
        cur.execute("SELECT id FROM bibliography WHERE author=? AND title=?", (author, title))
        bib_row = cur.fetchone()
        if not bib_row:
            continue
        cur.execute(
            "INSERT OR IGNORE INTO scholar_works (scholar_id, bib_id) VALUES (?, ?)",
            (scholar_row[0], bib_row[0])
        )
        link_count += cur.rowcount
    conn.commit()
    print(f"  Created {link_count} scholar-work links")

    # Update work counts
    cur.execute("""
        UPDATE scholars SET work_count = (
            SELECT COUNT(*) FROM scholar_works WHERE scholar_id = scholars.id
        )
    """)
    conn.commit()

    # Insert timeline events
    print("Inserting timeline events...")
    timeline_count = 0
    for evt in TIMELINE:
        year, year_end, evt_type, title, desc, topic = evt
        cur.execute(
            """INSERT OR IGNORE INTO timeline_events
               (year, year_end, event_type, title, description)
               VALUES (?, ?, ?, ?, ?)""",
            (year, year_end, evt_type, title, desc)
        )
        timeline_count += cur.rowcount
    conn.commit()
    print(f"  Inserted {timeline_count} timeline events")

    # Summary stats
    print("\n=== Database Summary ===")
    for table in ['bibliography', 'scholars', 'scholar_works', 'timeline_events',
                  'annotator_hands', 'dissertation_refs', 'matches', 'images', 'manuscripts']:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        print(f"  {table}: {cur.fetchone()[0]} rows")

    print("\nBibliography gap analysis:")
    cur.execute("SELECT COUNT(*) FROM bibliography WHERE in_collection = 1")
    have = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM bibliography WHERE in_collection = 0")
    missing = cur.fetchone()[0]
    print(f"  In collection: {have}")
    print(f"  Missing (cited by Russell): {missing}")
    print(f"  Coverage: {have}/{have+missing} ({100*have//(have+missing)}%)")

    print("\nScholar profiles by nationality:")
    cur.execute("SELECT nationality, COUNT(*) FROM scholars GROUP BY nationality ORDER BY COUNT(*) DESC")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
```

---

## add_hands

`scripts/add_hands.py`

```python
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
```

---

## build_essay_data

`scripts/build_essay_data.py`

```python
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
        SELECT r.signature_ref, i.filename, i.relative_path,
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
```

---

## build_reading_packets

`scripts/build_reading_packets.py`

```python
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
```

---

## build_scholar_profiles

`scripts/build_scholar_profiles.py`

```python
"""Build scholar profile pages and paper summary pages from summaries JSON."""

import json
import re
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SCHOLARS_DIR = BASE_DIR / "scholars"
SUMMARIES_PATH = BASE_DIR / "scholars" / "summaries.json"
SITE_DIR = BASE_DIR / "site"


def slugify(name):
    """Create a URL-safe slug from a name."""
    slug = name.lower().strip()
    slug = re.sub(r"['\u2019]", '', slug)
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    return slug.strip('-')


def paper_slug(title):
    """Create a short slug from a paper title."""
    words = re.sub(r'[^\w\s]', '', title.lower()).split()
    return '-'.join(words[:6])


def group_by_scholar(summaries):
    """Group paper summaries by author."""
    scholars = {}
    for paper in summaries:
        author = paper.get('author', 'Unknown')
        if author not in scholars:
            scholars[author] = []
        scholars[author].append(paper)
    return scholars


def write_scholar_profile(scholar_name, papers, scholar_dir):
    """Write a scholar's profile.md."""
    slug = slugify(scholar_name)
    profile_dir = scholar_dir / slug
    profile_dir.mkdir(parents=True, exist_ok=True)

    paper_list = []
    for p in sorted(papers, key=lambda x: x.get('year', 0) or 0):
        year = p.get('year', '?')
        journal = p.get('journal', '')
        p_slug = paper_slug(p['title'])
        paper_list.append(f"- [{p['title']}]({p_slug}.md) ({journal} {year})")

    content = f"""---
name: "{scholar_name}"
slug: "{slug}"
paper_count: {len(papers)}
topic_clusters: {json.dumps(list(set(p.get('topic_cluster', 'unknown') for p in papers)))}
---

# {scholar_name}

## Papers in the HP Corpus

{chr(10).join(paper_list)}
"""

    (profile_dir / "profile.md").write_text(content, encoding='utf-8')

    # Write individual paper summary files
    for p in papers:
        p_slug = paper_slug(p['title'])
        year = p.get('year', '?')
        journal = p.get('journal', '')
        topic = p.get('topic_cluster', 'unknown')
        summary = p.get('summary', 'Summary pending.')

        paper_content = f"""---
title: "{p['title']}"
author: "{scholar_name}"
year: {year if year and year != '?' else 'null'}
journal: "{journal}"
topic_cluster: "{topic}"
source_pdf: "{p.get('filename', '')}"
---

# {p['title']}

**{scholar_name}** | {journal} {year}

## Summary

{summary}

## Topic

{topic.replace('_', ' ').title()}
"""
        (profile_dir / f"{p_slug}.md").write_text(paper_content, encoding='utf-8')

    return slug


def generate_scholars_html(scholars_data, papers_data):
    """Generate the scholars directory HTML page."""
    cards = []
    for name, papers in sorted(scholars_data.items()):
        slug = slugify(name)
        topics = set(p.get('topic_cluster', '') for p in papers)
        topic_badges = ' '.join(
            f'<span class="topic-badge topic-{t}">{t.replace("_", " ").title()}</span>'
            for t in sorted(topics) if t
        )
        paper_count = len(papers)

        # Index card summaries for each paper
        paper_cards = []
        for p in sorted(papers, key=lambda x: x.get('year', 0) or 0):
            year = p.get('year', '?')
            journal = p.get('journal', '')
            summary = p.get('summary', 'Summary pending.')
            p_slug = paper_slug(p['title'])

            paper_cards.append(f"""
                <div class="paper-card">
                    <h4><a href="scholar/{slug}.html#{p_slug}">{escape_html(p['title'])}</a></h4>
                    <div class="paper-meta">{escape_html(journal)} {year}</div>
                    <p class="paper-summary">{escape_html(summary)}</p>
                </div>""")

        cards.append(f"""
            <div class="scholar-card" id="{slug}">
                <h3><a href="scholar/{slug}.html">{escape_html(name)}</a></h3>
                <div class="scholar-meta">{paper_count} paper{'s' if paper_count != 1 else ''} {topic_badges}</div>
                <div class="scholar-papers">
                    {''.join(paper_cards)}
                </div>
            </div>""")

    return cards


def generate_scholar_page_html(name, papers):
    """Generate an individual scholar's HTML page."""
    slug = slugify(name)

    paper_sections = []
    for p in sorted(papers, key=lambda x: x.get('year', 0) or 0):
        year = p.get('year', '?')
        journal = p.get('journal', '')
        summary = p.get('summary', 'Summary pending.')
        topic = p.get('topic_cluster', 'unknown')
        p_slug = paper_slug(p['title'])

        paper_sections.append(f"""
        <article class="paper-detail" id="{p_slug}">
            <h3>{escape_html(p['title'])}</h3>
            <div class="paper-meta">
                {escape_html(journal)} {year}
                <span class="topic-badge topic-{topic}">{topic.replace('_', ' ').title()}</span>
            </div>
            <div class="paper-summary-full">
                <p>{escape_html(summary)}</p>
            </div>
        </article>""")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape_html(name)} — HP Scholarship</title>
    <link rel="stylesheet" href="../style.css">
    <link rel="stylesheet" href="../scholars.css">
</head>
<body>
    <header>
        <div class="header-content">
            <h1>{escape_html(name)}</h1>
            <p class="subtitle"><a href="../scholars.html">&larr; All Scholars</a></p>
        </div>
    </header>
    <main>
        <section class="scholar-detail">
            <h2>Papers in the HP Corpus ({len(papers)})</h2>
            {''.join(paper_sections)}
        </section>
    </main>
    <footer>
        <div class="footer-content">
            <div class="footer-section">
                <h4>HP Scholarship Database</h4>
                <p>Part of the <a href="../index.html">Hypnerotomachia Poliphili</a> digital humanities project.</p>
            </div>
        </div>
    </footer>
</body>
</html>"""


def escape_html(text):
    """Escape HTML special characters."""
    if not text:
        return ''
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;'))


def main():
    if not SUMMARIES_PATH.exists():
        print(f"ERROR: {SUMMARIES_PATH} not found. Create summaries.json first.")
        return

    with open(SUMMARIES_PATH, 'r', encoding='utf-8') as f:
        summaries = json.load(f)

    print(f"Loaded {len(summaries)} paper summaries")

    scholars = group_by_scholar(summaries)
    print(f"Found {len(scholars)} unique scholars")

    # Write scholar profile markdown files
    for name, papers in scholars.items():
        slug = write_scholar_profile(name, papers, SCHOLARS_DIR)
        print(f"  {name} ({slug}): {len(papers)} papers")

    # Generate HTML pages
    scholar_page_dir = SITE_DIR / "scholar"
    scholar_page_dir.mkdir(parents=True, exist_ok=True)

    # Individual scholar pages
    for name, papers in scholars.items():
        slug = slugify(name)
        html = generate_scholar_page_html(name, papers)
        (scholar_page_dir / f"{slug}.html").write_text(html, encoding='utf-8')

    # Scholars directory page
    cards = generate_scholars_html(scholars, summaries)
    scholars_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scholars — Hypnerotomachia Poliphili</title>
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="scholars.css">
</head>
<body>
    <header>
        <div class="header-content">
            <h1>HP Scholarship</h1>
            <p class="subtitle">Scholars and Their Contributions</p>
            <p class="attribution"><a href="index.html">&larr; Back to Marginalia</a></p>
        </div>
    </header>
    <main>
        <section class="intro">
            <div class="intro-content">
                <p>Five centuries of scholarship on the <em>Hypnerotomachia Poliphili</em>, organized by author. Each scholar's profile links to summaries of their contributions to the field.</p>
            </div>
        </section>
        <section class="scholars-grid">
            {''.join(cards)}
        </section>
    </main>
    <footer>
        <div class="footer-content">
            <div class="footer-section">
                <h4>HP Scholarship Database</h4>
                <p>Part of the <a href="index.html">Hypnerotomachia Poliphili</a> digital humanities project.</p>
            </div>
        </div>
    </footer>
</body>
</html>"""

    (SITE_DIR / "scholars.html").write_text(scholars_html, encoding='utf-8')
    print(f"\nGenerated {len(scholars)} scholar pages + scholars.html")


if __name__ == "__main__":
    main()
```

---

## build_signature_map

`scripts/build_signature_map.py`

```python
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
```

---

## build_site

`scripts/build_site.py`

```python
"""Unified site builder: generates all static pages from SQLite.

Replaces build_scholar_profiles.py and export_showcase_data.py.
Generates:
  - site/index.html           (marginalia gallery, updated nav)
  - site/data.json             (gallery data with confidence flags)
  - site/scholars.html         (scholars overview, DB-driven)
  - site/scholar/*.html        (individual scholar pages)
  - site/dictionary/index.html (dictionary landing)
  - site/dictionary/*.html     (individual term pages)
  - site/marginalia/*.html     (individual folio detail pages)
  - site/about.html            (about page)
"""

import sqlite3
import json
import re
import os
from pathlib import Path
from html import escape

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"
SITE_DIR = BASE_DIR / "site"
SUMMARIES_PATH = BASE_DIR / "scholars" / "summaries.json"

# ============================================================
# Shared HTML templates
# ============================================================

def slugify(text):
    s = text.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s.strip('-')


def nav_html(active='', prefix=''):
    """Generate navigation bar. prefix is '' for root, '../' for subdirectories."""
    links = [
        (f'{prefix}index.html', 'Home', 'home'),
        (f'{prefix}marginalia/index.html', 'Marginalia', 'marginalia'),
        (f'{prefix}scholars.html', 'Scholars', 'scholars'),
        (f'{prefix}bibliography.html', 'Bibliography', 'bibliography'),
        (f'{prefix}dictionary/index.html', 'Dictionary', 'dictionary'),
        (f'{prefix}docs/index.html', 'Docs', 'docs'),
        (f'{prefix}code/index.html', 'Code', 'code'),
        (f'{prefix}digital-edition.html', 'Edition', 'edition'),
        (f'{prefix}russell-alchemical-hands.html', 'Alchemical Hands', 'russell'),
        (f'{prefix}concordance-method.html', 'Concordance', 'concordance'),
        (f'{prefix}about.html', 'About', 'about'),
    ]
    items = []
    for href, label, key in links:
        cls = ' class="active"' if key == active else ''
        items.append(f'<a href="{href}"{cls}>{label}</a>')
    return f'<nav class="site-nav">{"".join(items)}</nav>'


def review_badge_html(needs_review, source_method=None):
    if not needs_review:
        return ''
    method = f' ({source_method})' if source_method else ''
    return f'<span class="review-badge">Unreviewed{method}</span>'


def confidence_badge_html(confidence):
    if not confidence:
        return ''
    cls = f'confidence-{confidence.lower()}'
    return f'<span class="confidence-badge {cls}">{confidence}</span>'


def page_shell(title, body, active_nav='', extra_css='', extra_js='', depth=0):
    """Generate full HTML page. depth=0 for site root, depth=1 for subdirectories."""
    prefix = '../' * depth if depth > 0 else ''
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(title)} - Hypnerotomachia Poliphili</title>
    <meta name="description" content="Digital scholarship and marginalia of the Hypnerotomachia Poliphili (Venice, 1499)">
    <link rel="stylesheet" href="{prefix}style.css">
    <link rel="stylesheet" href="{prefix}scholars.css">
    <link rel="stylesheet" href="{prefix}components.css">
    {extra_css}
</head>
<body>
    <header>
        <div class="header-content">
            <h1><a href="{prefix}index.html" style="color:inherit;text-decoration:none"><em>Hypnerotomachia Poliphili</em></a></h1>
            <p class="subtitle">Digital Scholarship &amp; Marginalia</p>
            {nav_html(active_nav, prefix)}
        </div>
    </header>
    <main>
{body}
    </main>
    <footer>
        <div class="footer-content">
            <div class="footer-section">
                <h4>About This Project</h4>
                <p>A digital humanities project documenting the readership
                and marginalia of the 1499 Aldine <em>Hypnerotomachia Poliphili</em>,
                based on James Russell's PhD thesis (Durham, 2014).</p>
            </div>
            <div class="footer-section">
                <h4>Data Provenance</h4>
                <p>Content marked with <span class="review-badge" style="font-size:0.7rem">Unreviewed</span>
                has been generated with LLM assistance and has not been
                verified by a human expert.</p>
            </div>
        </div>
    </footer>
    {extra_js}
</body>
</html>"""


# ============================================================
# Topic badge helpers
# ============================================================

TOPIC_LABELS = {
    'authorship': 'Authorship',
    'architecture_gardens': 'Architecture & Gardens',
    'text_image': 'Text & Image',
    'reception': 'Reception',
    'dream_religion': 'Dream & Religion',
    'material_bibliographic': 'Material & Bibliographic',
}


def topic_badges_html(topics_str):
    if not topics_str:
        return ''
    badges = []
    for t in topics_str.split(','):
        t = t.strip()
        label = TOPIC_LABELS.get(t, t.replace('_', ' ').title())
        badges.append(f'<span class="topic-badge topic-{t}">{label}</span>')
    return ' '.join(badges)


# ============================================================
# Data export: data.json
# ============================================================

def export_data_json(conn):
    """Export marginalia gallery data with confidence flags."""
    cur = conn.cursor()
    cur.execute("""
        SELECT
            r.id, r.thesis_page, r.signature_ref, m.shelfmark,
            m.institution, m.city, r.context_text, r.marginal_text,
            r.chapter_num, i.filename, i.relative_path,
            i.folio_number, i.side, mat.confidence,
            sm.quire, sm.leaf_in_quire,
            mat.needs_review as match_needs_review,
            h.hand_label, h.attribution, h.is_alchemist
        FROM matches mat
        JOIN dissertation_refs r ON mat.ref_id = r.id
        JOIN images i ON mat.image_id = i.id
        JOIN manuscripts m ON i.manuscript_id = m.id
        LEFT JOIN signature_map sm ON LOWER(r.signature_ref) = LOWER(sm.signature)
        LEFT JOIN annotator_hands h ON r.hand_id = h.id
        WHERE i.page_type = 'PAGE'
        GROUP BY r.signature_ref, i.filename
        ORDER BY COALESCE(sm.folio_number, 999), r.thesis_page
    """)

    entries = []
    sigs = set()
    for row in cur.fetchall():
        entry = {
            'ref_id': row[0], 'thesis_page': row[1],
            'signature': row[2], 'manuscript': row[3],
            'institution': row[4], 'city': row[5],
            'context': (row[6] or '')[:600],
            'marginal_text': row[7], 'chapter': row[8],
            'image_file': row[9],
            'image_path': row[10],
            'folio_number': row[11], 'side': row[12],
            'confidence': row[13] or 'PROVISIONAL',
            'quire': row[14], 'leaf_in_quire': row[15],
            'needs_review': bool(row[16]),
            'hand_label': row[17], 'hand_attribution': row[18],
            'is_alchemist': bool(row[19]) if row[19] is not None else False,
        }
        entries.append(entry)
        sigs.add(row[2])

    data = {
        'entries': entries,
        'stats': {
            'total_references': len(entries),
            'unique_signatures': len(sigs),
            'high_confidence_matches': sum(1 for e in entries if e['confidence'] == 'HIGH'),
            'low_confidence_matches': sum(1 for e in entries if e['confidence'] == 'LOW'),
            'needs_review': sum(1 for e in entries if e['needs_review']),
        },
        'provenance': {
            'source': 'hp.db v2',
            'note': 'BL C.60.o.12 matches are LOW confidence (1545 edition, unverified photo-folio mapping)',
        },
    }

    out = SITE_DIR / 'data.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  data.json: {len(entries)} entries")


# ============================================================
# Scholars pages (DB-driven)
# ============================================================

def build_scholars_pages(conn):
    """Generate scholars.html and scholar/*.html from DB + summaries.json."""
    # Load summaries for detailed content
    summaries = []
    if SUMMARIES_PATH.exists():
        with open(SUMMARIES_PATH, encoding='utf-8') as f:
            summaries = json.load(f)

    # Group by author
    by_author = {}
    for s in summaries:
        author = s.get('author', 'Unknown')
        by_author.setdefault(author, []).append(s)

    cur = conn.cursor()
    # Get review status from DB
    cur.execute("SELECT name, needs_review, source_method FROM scholars")
    scholar_review = {}
    for row in cur.fetchall():
        scholar_review[row[0]] = {'needs_review': row[1], 'source_method': row[2]}

    # Build scholars index
    scholar_cards = []
    scholar_dir = SITE_DIR / 'scholar'
    scholar_dir.mkdir(exist_ok=True)

    for author in sorted(by_author.keys()):
        papers = by_author[author]
        slug = slugify(author)
        review = scholar_review.get(author, {'needs_review': True, 'source_method': 'LLM_ASSISTED'})

        # Collect all topics
        topics = set()
        for p in papers:
            tc = p.get('topic_cluster', '')
            if tc:
                for t in tc.split(','):
                    topics.add(t.strip())

        badges = topic_badges_html(','.join(topics))
        review_html = review_badge_html(review.get('needs_review'), review.get('source_method'))

        # Paper cards for index
        paper_cards_html = ''
        for p in papers:
            paper_slug = slugify(p.get('title', ''))
            summary_preview = (p.get('summary', '') or '')[:250]
            if len(p.get('summary', '')) > 250:
                summary_preview += '...'
            paper_cards_html += f"""
                <div class="paper-card">
                    <h4><a href="{slug}.html">{escape(p.get('title', ''))}</a></h4>
                    <div class="paper-meta">{escape(p.get('journal', ''))} ({p.get('year', '?')})</div>
                    <div class="paper-summary">{escape(summary_preview)}</div>
                </div>"""

        scholar_cards.append(f"""
        <div class="scholar-card">
            <h3><a href="{slug}.html">{escape(author)}</a> {review_html}</h3>
            <div class="scholar-meta">{len(papers)} paper{'s' if len(papers) != 1 else ''} {badges}</div>
            <div class="scholar-papers">{paper_cards_html}</div>
        </div>""")

        # Build individual scholar page
        papers_detail = ''
        for p in papers:
            tc = p.get('topic_cluster', '')
            papers_detail += f"""
            <div class="paper-detail">
                <h3>{escape(p.get('title', ''))}</h3>
                <div class="paper-meta">{escape(p.get('journal', ''))} ({p.get('year', '?')})
                    {topic_badges_html(tc)}</div>
                <div class="paper-summary-full"><p>{escape(p.get('summary', ''))}</p></div>
            </div>"""

        detail_body = f"""
        <div class="scholar-detail">
            <h2>{escape(author)} {review_html}</h2>
            <p><a href="../scholars.html">&larr; All Scholars</a></p>
            {papers_detail}
        </div>"""

        detail_page = page_shell(author, detail_body, active_nav='scholars', depth=1)
        (scholar_dir / f'{slug}.html').write_text(detail_page, encoding='utf-8')

    # Build index page
    index_body = f"""
        <div class="scholars-grid">
            <div class="intro" style="margin-bottom:2rem">
                <p>{len(by_author)} scholars, {len(summaries)} works documented.
                Data sourced from SQLite database with provenance tracking.</p>
            </div>
            {''.join(scholar_cards)}
        </div>"""

    index_page = page_shell('Scholars', index_body, active_nav='scholars')
    (SITE_DIR / 'scholars.html').write_text(index_page, encoding='utf-8')
    print(f"  scholars.html + {len(by_author)} scholar pages")


# ============================================================
# Dictionary pages
# ============================================================

def review_status_badge(status):
    """Generate a colored review status badge."""
    colors = {
        'DRAFT': ('review-badge-draft', 'Draft'),
        'REVIEWED': ('review-badge-reviewed', 'Reviewed'),
        'VERIFIED': ('review-badge-verified', 'Verified'),
        'PROVISIONAL': ('review-badge-provisional', 'Provisional'),
    }
    cls, label = colors.get(status, ('review-badge-draft', status or 'Draft'))
    return f'<span class="review-status-badge {cls}">{label}</span>'


def build_dictionary_pages(conn):
    """Generate dictionary/index.html and dictionary/*.html from DB."""
    cur = conn.cursor()
    dict_dir = SITE_DIR / 'dictionary'
    dict_dir.mkdir(exist_ok=True)

    # Get all terms with enriched fields
    cur.execute("""
        SELECT id, slug, label, category, definition_short, definition_long,
               source_basis, review_status, needs_review,
               significance_to_hp, significance_to_scholarship,
               source_documents, source_page_refs, source_quotes_short,
               source_method, confidence, notes, related_scholars
        FROM dictionary_terms ORDER BY label
    """)
    terms = cur.fetchall()

    # Build per-term link map
    term_links = {}
    cur.execute("""
        SELECT t1.slug, t2.slug, t2.label, l.link_type
        FROM dictionary_term_links l
        JOIN dictionary_terms t1 ON l.term_id = t1.id
        JOIN dictionary_terms t2 ON l.linked_term_id = t2.id
    """)
    for row in cur.fetchall():
        term_links.setdefault(row[0], []).append({
            'slug': row[1], 'label': row[2], 'type': row[3]
        })

    # Group by category for index
    by_category = {}
    for t in terms:
        by_category.setdefault(t[3], []).append(t)

    # Build index page
    cat_sections = ''
    for cat in sorted(by_category.keys()):
        cat_terms = by_category[cat]
        items = ''
        for t in sorted(cat_terms, key=lambda x: x[2]):
            review = ' <span class="review-badge">Draft</span>' if t[8] else ''
            items += f"""
                <div class="dict-entry">
                    <h4><a href="{t[1]}.html">{escape(t[2])}</a>{review}</h4>
                    <p>{escape(t[4])}</p>
                </div>"""
        cat_sections += f"""
            <section class="dict-category">
                <h3>{escape(cat)}</h3>
                {items}
            </section>"""

    index_body = f"""
        <div class="dictionary-index">
            <div class="intro">
                <h2>Dictionary of the <em>Hypnerotomachia</em></h2>
                <p>{len(terms)} terms across {len(by_category)} categories.
                A glossary of concepts essential for understanding the book,
                its readers, and five centuries of scholarship.</p>
            </div>
            {cat_sections}
        </div>"""

    dict_css = '<style>' + """
        .dictionary-index { max-width: 900px; margin: 2rem auto; padding: 0 2rem; }
        .dict-category { margin-bottom: 2.5rem; }
        .dict-category h3 {
            font-size: 1.2rem; color: var(--accent);
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.3rem; margin-bottom: 1rem;
        }
        .dict-entry { margin-bottom: 1rem; }
        .dict-entry h4 { font-size: 1rem; margin-bottom: 0.2rem; }
        .dict-entry h4 a { color: var(--text); text-decoration: none; }
        .dict-entry h4 a:hover { color: var(--accent); }
        .dict-entry p { font-size: 0.9rem; color: var(--text-muted); line-height: 1.5; }
        .dict-detail { max-width: 800px; margin: 2rem auto; padding: 0 2rem; }
        .dict-detail h2 { color: var(--accent); margin-bottom: 0.5rem; }
        .dict-detail .category-label {
            font-size: 0.85rem; color: var(--text-muted);
            font-family: var(--font-sans); margin-bottom: 1.5rem;
        }
        .dict-detail .definition-short {
            font-size: 1.1rem; font-style: italic; margin-bottom: 1.5rem;
            padding: 1rem; background: var(--bg-card); border-left: 3px solid var(--accent);
        }
        .dict-detail .definition-long { line-height: 1.8; margin-bottom: 1.5rem; }
        .dict-detail .source-basis {
            font-size: 0.85rem; color: var(--text-muted);
            font-family: var(--font-sans); margin-top: 1rem;
            padding-top: 1rem; border-top: 1px solid var(--border);
        }
        .related-terms { margin-top: 1.5rem; }
        .related-terms h4 { font-size: 0.95rem; color: var(--accent); margin-bottom: 0.5rem; }
        .related-terms a {
            display: inline-block; margin: 0.2rem 0.3rem 0.2rem 0;
            padding: 0.2rem 0.6rem; background: var(--bg);
            border: 1px solid var(--border); border-radius: 3px;
            font-size: 0.85rem; color: var(--text); text-decoration: none;
        }
        .related-terms a:hover { border-color: var(--accent); color: var(--accent); }
    """ + '</style>'

    index_page = page_shell('Dictionary', index_body, active_nav='dictionary', depth=1)
    (dict_dir / 'index.html').write_text(index_page, encoding='utf-8')

    # Build individual term pages
    for t in terms:
        (tid, slug, label, category, def_short, def_long, source, status,
         needs_rev, sig_hp, sig_schol, src_docs, src_pages, src_quotes,
         src_method, confidence, notes, related_scholars) = t
        links = term_links.get(slug, [])

        related_html = ''
        see_also_html = ''
        for lk in links:
            link_el = f'<a href="{lk["slug"]}.html">{escape(lk["label"])}</a>'
            if lk['type'] == 'SEE_ALSO':
                see_also_html += link_el
            else:
                related_html += link_el

        links_section = ''
        if related_html:
            links_section += f'<div class="related-terms"><h4>Related Terms</h4>{related_html}</div>'
        if see_also_html:
            links_section += f'<div class="related-terms"><h4>See Also</h4>{see_also_html}</div>'

        # Status badge
        status_html = review_status_badge(status)
        source_html = f'<div class="source-basis"><strong>Sources:</strong> {escape(source or "")}</div>' if source else ''

        # Significance sections
        sig_hp_html = ''
        if sig_hp:
            sig_hp_html = f'''
            <div class="dict-section">
                <h3>Why It Matters for the <em>Hypnerotomachia</em></h3>
                <p>{escape(sig_hp)}</p>
            </div>'''

        sig_schol_html = ''
        if sig_schol:
            sig_schol_html = f'''
            <div class="dict-section">
                <h3>Why It Matters in Scholarship</h3>
                <p>{escape(sig_schol)}</p>
            </div>'''

        # Evidence section
        evidence_html = ''
        if src_quotes:
            quotes = src_quotes.split(' | ')
            quote_items = ''.join(f'<li>{escape(q)}</li>' for q in quotes)
            evidence_html = f'''
            <div class="dict-section">
                <h3>Key Passages / Evidence</h3>
                <ul class="evidence-list">{quote_items}</ul>
            </div>'''

        # Source documents
        src_docs_html = ''
        if src_docs:
            src_docs_html = f'''
            <div class="dict-section">
                <h3>Source Documents</h3>
                <p class="source-docs">{escape(src_docs)}</p>
            </div>'''

        # Page references
        src_pages_html = ''
        if src_pages:
            src_pages_html = f'<div class="source-pages"><strong>Page references:</strong> {escape(src_pages)}</div>'

        # Related scholars
        scholars_html = ''
        if related_scholars:
            scholars_html = f'''
            <div class="dict-section">
                <h3>Related Scholars / Bibliography</h3>
                <p>{escape(related_scholars)}</p>
            </div>'''

        # Provenance section
        provenance_items = []
        if src_method:
            provenance_items.append(f'Source method: {escape(src_method)}')
        if confidence:
            provenance_items.append(f'Confidence: {escape(confidence)}')
        if notes:
            provenance_items.append(f'Notes: {escape(notes)}')
        provenance_html = ''
        if provenance_items:
            prov_list = ''.join(f'<li>{p}</li>' for p in provenance_items)
            provenance_html = f'''
            <div class="dict-section provenance-section">
                <h3>Review Status / Provenance</h3>
                <div class="provenance-status">{status_html}</div>
                <ul class="provenance-list">{prov_list}</ul>
            </div>'''

        detail_body = f"""
        <div class="dict-detail">
            <p><a href="index.html">&larr; Dictionary</a></p>
            <h2>{escape(label)} {status_html}</h2>
            <div class="category-label">{escape(category)}</div>
            <div class="definition-short">{escape(def_short)}</div>
            <div class="definition-long">{escape(def_long or '')}</div>
            {sig_hp_html}
            {sig_schol_html}
            {evidence_html}
            {src_docs_html}
            {src_pages_html}
            {source_html}
            {scholars_html}
            {links_section}
            {provenance_html}
        </div>"""

        term_page = page_shell(label, detail_body, active_nav='dictionary', depth=1)
        (dict_dir / f'{slug}.html').write_text(term_page, encoding='utf-8')

    print(f"  dictionary/index.html + {len(terms)} term pages")


# ============================================================
# Marginalia folio detail pages
# ============================================================

def build_marginalia_pages(conn):
    """Generate marginalia/index.html and marginalia/[signature].html."""
    cur = conn.cursor()
    marg_dir = SITE_DIR / 'marginalia'
    marg_dir.mkdir(exist_ok=True)

    # Get all matched signatures with their images and annotations
    cur.execute("""
        SELECT
            r.signature_ref, r.thesis_page, r.context_text, r.marginal_text,
            r.chapter_num, m.shelfmark, m.institution, m.city,
            i.filename, i.relative_path, i.folio_number, i.side,
            mat.confidence, mat.needs_review,
            h.hand_label, h.attribution, h.is_alchemist, h.school,
            sm.quire, sm.leaf_in_quire
        FROM matches mat
        JOIN dissertation_refs r ON mat.ref_id = r.id
        JOIN images i ON mat.image_id = i.id
        JOIN manuscripts m ON i.manuscript_id = m.id
        LEFT JOIN signature_map sm ON LOWER(r.signature_ref) = LOWER(sm.signature)
        LEFT JOIN annotator_hands h ON r.hand_id = h.id
        WHERE i.page_type = 'PAGE'
        ORDER BY COALESCE(sm.folio_number, 999), m.shelfmark
    """)

    # Group by signature
    by_sig = {}
    for row in cur.fetchall():
        sig = row[0]
        by_sig.setdefault(sig, []).append(row)

    marg_css = '<style>' + """
        .marg-detail { max-width: 1000px; margin: 2rem auto; padding: 0 2rem; }
        .marg-detail h2 { color: var(--accent); margin-bottom: 0.5rem; }
        .marg-images { display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 1.5rem; margin: 1.5rem 0; }
        .marg-image-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 4px; overflow: hidden; }
        .marg-image-card img { width: 100%; display: block; }
        .marg-image-card .caption { padding: 0.75rem 1rem; font-size: 0.85rem; font-family: var(--font-sans); }
        .marg-annotation { background: var(--bg-card); border: 1px solid var(--border); border-radius: 4px; padding: 1.5rem; margin-bottom: 1rem; }
        .marg-annotation .marginal-text { font-style: italic; font-size: 1.05rem; padding: 0.75rem; border-left: 3px solid var(--accent-light); margin: 0.75rem 0; }
        .marg-annotation .context { font-size: 0.9rem; color: var(--text-muted); line-height: 1.6; max-height: 200px; overflow-y: auto; }
        .marg-annotation .hand-info { font-size: 0.85rem; font-family: var(--font-sans); color: var(--text-muted); margin-top: 0.5rem; }
        .alchemist-tag { display: inline-block; padding: 0.1rem 0.5rem; background: #e8d4d4; color: #6b2323; border-radius: 2px; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; }
        .marg-index { max-width: 1000px; margin: 2rem auto; padding: 0 2rem; }
        .marg-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }
        .marg-grid a { display: block; padding: 0.75rem 1rem; background: var(--bg-card); border: 1px solid var(--border); border-radius: 3px; text-decoration: none; color: var(--text); transition: all 0.2s; }
        .marg-grid a:hover { border-color: var(--accent); color: var(--accent); transform: translateY(-1px); }
        .marg-grid .sig-label { font-weight: 600; font-size: 1.1rem; color: var(--accent); }
        .marg-grid .sig-meta { font-size: 0.8rem; color: var(--text-muted); font-family: var(--font-sans); }
    """ + '</style>'

    # Build individual folio pages
    for sig, rows in by_sig.items():
        sig_slug = sig.lower().replace(' ', '')

        images_html = ''
        annotations_html = ''
        seen_images = set()

        for row in rows:
            (sig_ref, thesis_page, context, marginal, chapter,
             shelfmark, institution, city, img_file, img_path,
             folio_num, side, confidence, needs_rev,
             hand_label, attribution, is_alchemist, school,
             quire, leaf) = row

            # Image card (deduplicate)
            if img_file not in seen_images:
                seen_images.add(img_file)
                conf_badge = confidence_badge_html(confidence)
                rev_badge = '<span class="review-badge">Unverified</span>' if needs_rev else ''
                images_html += f"""
                    <div class="marg-image-card">
                        <img src="../{img_path}" alt="Folio {sig}" loading="lazy">
                        <div class="caption">
                            {escape(institution)}, {escape(city)} &mdash; {escape(shelfmark)}
                            {conf_badge} {rev_badge}
                        </div>
                    </div>"""

            # Annotation card
            hand_html = ''
            if hand_label:
                alch_tag = ' <span class="alchemist-tag">Alchemist</span>' if is_alchemist else ''
                school_info = f' ({escape(school)})' if school else ''
                hand_html = f'<div class="hand-info">Hand {escape(hand_label)}: {escape(attribution or "Anonymous")}{school_info}{alch_tag}</div>'

            marginal_html = ''
            if marginal:
                marginal_html = f'<div class="marginal-text">&ldquo;{escape(marginal)}&rdquo;</div>'

            context_html = ''
            if context:
                ctx = context[:500] + ('...' if len(context) > 500 else '')
                context_html = f'<div class="context">{escape(ctx)}</div>'

            annotations_html += f"""
                <div class="marg-annotation">
                    {hand_html}
                    {marginal_html}
                    {context_html}
                    <div class="hand-info">Russell, PhD Thesis, p. {thesis_page} (Ch. {chapter})</div>
                </div>"""

        folio_info = f'Folio {rows[0][10] or "?"}{rows[0][11] or ""}'
        quire_info = f', Quire {rows[0][18]}' if rows[0][18] else ''

        detail_body = f"""
        <div class="marg-detail">
            <p><a href="index.html">&larr; All Folios</a></p>
            <h2>Signature {escape(sig)}</h2>
            <p style="color:var(--text-muted); font-family:var(--font-sans); margin-bottom:1.5rem">
                {folio_info}{quire_info}</p>
            <div class="marg-images">{images_html}</div>
            <h3 style="margin:1.5rem 0 1rem">Annotations</h3>
            {annotations_html}
        </div>"""

        detail_page = page_shell(f'Folio {sig}', detail_body, active_nav='marginalia', depth=1)
        (marg_dir / f'{sig_slug}.html').write_text(detail_page, encoding='utf-8')

    # Build marginalia index
    grid_items = ''
    for sig in sorted(by_sig.keys(), key=lambda s: (
        # Sort by quire then leaf
        by_sig[s][0][18] or 'zzz',
        by_sig[s][0][10] or 999
    )):
        rows = by_sig[sig]
        sig_slug = sig.lower().replace(' ', '')
        n_images = len(set(r[8] for r in rows))
        n_annotations = len(rows)
        has_alchemist = any(r[16] for r in rows)
        alch = ' <span class="alchemist-tag">Alch.</span>' if has_alchemist else ''

        grid_items += f"""
            <a href="{sig_slug}.html">
                <div class="sig-label">{escape(sig)}{alch}</div>
                <div class="sig-meta">{n_images} image{'s' if n_images != 1 else ''}, {n_annotations} ref{'s' if n_annotations != 1 else ''}</div>
            </a>"""

    index_body = f"""
        <div class="marg-index">
            <div class="intro">
                <h2>Marginalia by Folio</h2>
                <p>{len(by_sig)} annotated folios documented from Russell's thesis.
                Click any signature to see images and annotations.</p>
            </div>
            <div class="marg-grid">{grid_items}</div>
        </div>"""

    index_page = page_shell('Marginalia', index_body, active_nav='marginalia', depth=1)
    (marg_dir / 'index.html').write_text(index_page, encoding='utf-8')
    print(f"  marginalia/index.html + {len(by_sig)} folio pages")


# ============================================================
# Bibliography page
# ============================================================

def build_bibliography_page(conn):
    """Generate bibliography.html with full HP bibliography from DB."""
    cur = conn.cursor()

    # Get all bibliography entries
    cur.execute("""
        SELECT id, author, title, year, pub_type, journal_or_publisher,
               hp_relevance, topic_cluster, in_collection, notes,
               review_status, needs_review
        FROM bibliography
        ORDER BY
            CASE WHEN year IS NULL THEN 9999 ELSE CAST(year AS INTEGER) END,
            author
    """)
    entries = cur.fetchall()

    # Group by relevance
    by_relevance = {}
    for e in entries:
        rel = e[6] or 'TANGENTIAL'
        by_relevance.setdefault(rel, []).append(e)

    relevance_order = ['PRIMARY', 'DIRECT', 'INDIRECT', 'TANGENTIAL']
    relevance_labels = {
        'PRIMARY': 'Primary Sources & Editions',
        'DIRECT': 'HP Scholarship (Direct)',
        'INDIRECT': 'Related Studies',
        'TANGENTIAL': 'General References',
    }

    bib_css = '<style>' + """
        .bib-page { max-width: 900px; margin: 2rem auto; padding: 0 2rem; }
        .bib-section { margin-bottom: 2.5rem; }
        .bib-section h3 {
            font-size: 1.1rem; color: var(--accent);
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.3rem; margin-bottom: 1rem;
        }
        .bib-entry { margin-bottom: 1rem; padding: 0.75rem 1rem; background: var(--bg-card); border: 1px solid var(--border); border-radius: 3px; }
        .bib-entry .bib-author { font-weight: 600; }
        .bib-entry .bib-title { font-style: italic; }
        .bib-entry .bib-details { font-size: 0.85rem; color: var(--text-muted); font-family: var(--font-sans); margin-top: 0.25rem; }
        .bib-entry .bib-badges { margin-top: 0.3rem; }
        .bib-badge-collection { display: inline-block; padding: 0.1rem 0.4rem; background: #d4edda; color: #155724; border-radius: 2px; font-size: 0.65rem; font-weight: 600; font-family: var(--font-sans); text-transform: uppercase; }
        .bib-badge-missing { display: inline-block; padding: 0.1rem 0.4rem; background: #f8d7da; color: #721c24; border-radius: 2px; font-size: 0.65rem; font-weight: 600; font-family: var(--font-sans); text-transform: uppercase; }
        .bib-stats { display: flex; gap: 1.5rem; flex-wrap: wrap; margin-bottom: 2rem; }
        .bib-stat { text-align: center; padding: 1rem; background: var(--bg-card); border: 1px solid var(--border); border-radius: 4px; flex: 1; min-width: 120px; }
        .bib-stat .num { font-size: 1.5rem; font-weight: 700; color: var(--accent); display: block; }
        .bib-stat .lbl { font-size: 0.8rem; color: var(--text-muted); font-family: var(--font-sans); }
    """ + '</style>'

    # Stats
    total = len(entries)
    in_coll = sum(1 for e in entries if e[8])
    primary = len(by_relevance.get('PRIMARY', []))
    direct = len(by_relevance.get('DIRECT', []))
    needs_rev = sum(1 for e in entries if e[11])

    stats_html = f"""
        <div class="bib-stats">
            <div class="bib-stat"><span class="num">{total}</span><span class="lbl">Total Works</span></div>
            <div class="bib-stat"><span class="num">{in_coll}</span><span class="lbl">In Collection</span></div>
            <div class="bib-stat"><span class="num">{primary}</span><span class="lbl">Primary Sources</span></div>
            <div class="bib-stat"><span class="num">{direct}</span><span class="lbl">Direct Scholarship</span></div>
            <div class="bib-stat"><span class="num">{needs_rev}</span><span class="lbl">Need Review</span></div>
        </div>"""

    # Build sections
    sections_html = ''
    for rel in relevance_order:
        items = by_relevance.get(rel, [])
        if not items:
            continue

        entries_html = ''
        for e in items:
            (eid, author, title, year, pub_type, journal,
             relevance, topic, in_coll_flag, notes,
             rev_status, needs_rev_flag) = e

            year_str = f' ({year})' if year else ''
            journal_str = f'. {escape(journal)}' if journal else ''
            type_str = f' [{pub_type}]' if pub_type else ''

            collection_badge = '<span class="bib-badge-collection">In Collection</span>' if in_coll_flag else '<span class="bib-badge-missing">Not in Collection</span>'
            review_badge = review_badge_html(needs_rev_flag) if needs_rev_flag else ''
            topic_html = topic_badges_html(topic) if topic else ''

            entries_html += f"""
                <div class="bib-entry">
                    <div><span class="bib-author">{escape(author or "")}</span>{year_str}.
                    <span class="bib-title">{escape(title)}</span>{journal_str}{type_str}.</div>
                    <div class="bib-badges">{collection_badge} {topic_html} {review_badge}</div>
                </div>"""

        label = relevance_labels.get(rel, rel)
        sections_html += f"""
            <section class="bib-section">
                <h3>{label} ({len(items)})</h3>
                {entries_html}
            </section>"""

    body = f"""
        <div class="bib-page">
            <div class="intro">
                <h2>Bibliography of the <em>Hypnerotomachia Poliphili</em></h2>
                <p>A comprehensive bibliography of editions, translations, and scholarship on
                the <em>Hypnerotomachia Poliphili</em>, compiled from Russell (2014), the
                <em>Word &amp; Image</em> special issues (1998, 2015), and ongoing research.</p>
            </div>
            {stats_html}
            {sections_html}
        </div>"""

    page = page_shell('Bibliography', body, active_nav='bibliography')
    (SITE_DIR / 'bibliography.html').write_text(page, encoding='utf-8')

    print(f"  bibliography.html: {total} entries")


# ============================================================
# About page
# ============================================================

def build_about_page(conn):
    cur = conn.cursor()

    # Get stats
    stats = {}
    for table in ['documents', 'images', 'dissertation_refs', 'matches',
                   'annotators', 'bibliography', 'scholars', 'dictionary_terms',
                   'timeline_events']:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = cur.fetchone()[0]
        except:
            stats[table] = 0

    cur.execute("SELECT COUNT(*) FROM matches WHERE confidence='HIGH'")
    stats['high_conf'] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM matches WHERE confidence='LOW'")
    stats['low_conf'] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM bibliography WHERE in_collection=1")
    stats['in_collection'] = cur.fetchone()[0]

    body = f"""
        <div class="scholar-detail">
            <h2>About This Project</h2>

            <div class="paper-detail">
                <h3>What Is This?</h3>
                <div class="paper-summary-full"><p>
                This is a digital humanities project documenting the readership and
                marginalia of the <em>Hypnerotomachia Poliphili</em> (Venice: Aldus Manutius, 1499),
                based on James Russell's PhD thesis
                <em>Many Other Things Worthy of Knowledge and Memory</em> (Durham University, 2014).
                </p><p>
                Russell conducted a world census of annotated copies of the HP, documenting
                marginalia by readers including Ben Jonson, Pope Alexander VII, Benedetto Giovio,
                and anonymous alchemists. This site presents his findings alongside photographs
                of two annotated copies, a dictionary of HP terminology, and an index of
                scholarship spanning five centuries.
                </p></div>
            </div>

            <div class="paper-detail">
                <h3>Database Statistics</h3>
                <div class="paper-summary-full">
                <ul style="list-style:none; padding:0;">
                    <li><strong>{stats['images']}</strong> manuscript images catalogued</li>
                    <li><strong>{stats['dissertation_refs']}</strong> folio references extracted from Russell's thesis</li>
                    <li><strong>{stats['matches']}</strong> image-reference matches
                        ({stats['high_conf']} high confidence, {stats['low_conf']} low/provisional)</li>
                    <li><strong>{stats['annotators']}</strong> annotator hands identified</li>
                    <li><strong>{stats['bibliography']}</strong> works in bibliography
                        ({stats['in_collection']} in our collection)</li>
                    <li><strong>{stats['scholars']}</strong> scholar profiles</li>
                    <li><strong>{stats['dictionary_terms']}</strong> dictionary terms</li>
                    <li><strong>{stats['timeline_events']}</strong> timeline events</li>
                </ul>
                </div>
            </div>

            <div class="paper-detail">
                <h3>Data Provenance</h3>
                <div class="paper-summary-full"><p>
                Content on this site has varying levels of verification:
                </p>
                <ul>
                    <li><strong>Verified</strong>: Signature maps, collation formulae, and image
                    cataloging are deterministic and correct.</li>
                    <li><strong>High confidence</strong>: Siena O.III.38 image matches use explicit
                    recto/verso naming.</li>
                    <li><strong>Low confidence</strong>: BL C.60.o.12 matches assume sequential photo
                    numbers equal folio numbers. The BL copy is the 1545 edition; the signature map
                    is based on the 1499. Manual verification needed.</li>
                    <li><strong>Unreviewed</strong>: Scholar summaries, dictionary definitions, and
                    hand attributions were generated with LLM assistance and have not been verified
                    by a domain expert. These are marked with
                    <span class="review-badge" style="font-size:0.7rem">Unreviewed</span> badges.</li>
                </ul>
                </div>
            </div>

            <div class="paper-detail">
                <h3>How to Rebuild</h3>
                <div class="paper-summary-full"><p>
                The site is generated from a SQLite database (<code>db/hp.db</code>).
                To rebuild all pages:
                </p>
                <pre style="background:var(--bg); padding:1rem; border-radius:4px; overflow-x:auto; font-size:0.85rem">
python scripts/migrate_v2.py        # Schema migration (idempotent)
python scripts/seed_dictionary.py   # Dictionary terms (idempotent)
python scripts/build_site.py        # Generate all HTML + JSON
                </pre>
                <p>Individual pipeline steps:</p>
                <pre style="background:var(--bg); padding:1rem; border-radius:4px; overflow-x:auto; font-size:0.85rem">
python scripts/init_db.py           # Initialize DB schema
python scripts/catalog_images.py    # Catalog manuscript images
python scripts/build_signature_map.py  # Build signature map
python scripts/extract_references.py   # Extract refs from thesis PDF
python scripts/match_refs_to_images.py # Match refs to images
python scripts/add_hands.py         # Add annotator hand profiles
python scripts/add_bibliography.py  # Add bibliography and timeline
                </pre>
                </div>
            </div>
        </div>"""

    page = page_shell('About', body, active_nav='about')
    (SITE_DIR / 'about.html').write_text(page, encoding='utf-8')
    print("  about.html")


# ============================================================
# Documents tab
# ============================================================

# Document metadata: (filename, title, one-line summary)
DOC_METADATA = {
    'README.md': ('README', 'Project overview, architecture, rebuild instructions, and data provenance table.'),
    'HPCONCORD.md': ('Concordance Methodology', 'How we built the 6-step folio-to-image concordance from Russell\'s thesis to manuscript photographs.'),
    'HPDECKARD.md': ('Boundary Audit v1', 'Deckard boundary map distinguishing deterministic tasks from probabilistic (LLM) tasks across 11 scripts.'),
    'HPDECKARD2.md': ('Boundary Audit v2', 'Second Deckard audit covering bibliography expansion, web research ingestion, and the hybrid verification pipeline.'),
    'HPMIT.md': ('MIT Site Analysis', 'Reverse-engineering of the MIT Electronic Hypnerotomachia (1997): strengths, weaknesses, and lessons for our digital edition.'),
    'HPMULTIMODAL.md': ('Multimodal RAG Study', 'How vision models and multimodal retrieval could read our 674 manuscript images to solve the BL confidence problem.'),
    'HPproposals.md': ('Content Quality Proposals', 'Six proposals for improving dictionary, bibliography, scholar, and summary pages through templating and LLM reading.'),
    'HPAGENTS.md': ('Agent Usage Analysis', 'Why and how Claude agents were used: what worked (foreground batches), what failed (background web tasks).'),
    'HPEMPTYOUTPUTFILES.md': ('Empty Output Files Post-Mortem', 'Root cause analysis of 0-byte agent output files and lessons for background agent reliability.'),
    'MISTAKESTOAVOID.md': ('Mistakes to Avoid', 'Twelve hard-won lessons from this project: provenance tagging, confidence scoring, name matching, and more.'),
    'AUDIT_REPORT.md': ('Audit Report', 'Validation results: what changed in V2 migration, what remains provisional, what still needs human review.'),
    'HPONTOLOGY.md': ('Ontology Design', 'Data model and entity relationships for the HP knowledge base: manuscripts, folios, hands, scholars, terms.'),
    'HPSCHOLARS.md': ('Scholars Analysis', 'Strategy for building scholar profiles and article summaries from our PDF corpus.'),
    'HPWEB.md': ('Web Architecture', 'Design decisions for the static site: why no framework, how SQLite drives page generation, URL structure.'),
}

# Script metadata: (filename, title, one-line summary)
SCRIPT_METADATA = {
    'init_db.py': ('Initialize Database', 'Creates SQLite schema (7 core tables) and catalogs PDFs/documents from the filesystem.'),
    'catalog_images.py': ('Catalog Images', 'Parses image filenames from BL and Siena collections into the images table with folio/side metadata.'),
    'build_signature_map.py': ('Build Signature Map', 'Generates the 448-entry signature-to-folio concordance from the Aldine collation formula (a-z, A-G).'),
    'extract_references.py': ('Extract References', 'Uses PyMuPDF + regex to extract 282 folio/signature references from Russell\'s PhD thesis PDF.'),
    'match_refs_to_images.py': ('Match Refs to Images', 'SQL join pipeline matching dissertation references to manuscript images via the signature map.'),
    'add_hands.py': ('Add Annotator Hands', 'Creates 11 annotator hand profiles and attributes dissertation references to specific hands.'),
    'add_bibliography.py': ('Add Bibliography', 'Populates bibliography (58 entries), scholars (29), timeline (39 events) from hardcoded research data.'),
    'migrate_v2.py': ('Schema Migration V2', 'Adds annotations, annotators, doc_folio_refs, dictionary tables, review/provenance columns. Downgrades BL confidence.'),
    'seed_dictionary.py': ('Seed Dictionary', 'Inserts 37 dictionary terms across 6 categories with 76 bidirectional cross-reference links.'),
    'build_site.py': ('Build Site', 'Unified site generator: exports data.json, builds all HTML pages (scholars, dictionary, marginalia, bibliography, docs, code, about).'),
    'build_scholar_profiles.py': ('Build Scholar Profiles (Legacy)', 'Original scholar page generator from summaries.json. Superseded by build_site.py.'),
    'export_showcase_data.py': ('Export Showcase Data (Legacy)', 'Original data.json exporter for the gallery. Superseded by build_site.py.'),
    'validate.py': ('Validate & QA', 'Checks data integrity (duplicate slugs, broken links, confidence distribution) and writes AUDIT_REPORT.md.'),
    'ingest_perplexity.py': ('Ingest Perplexity Research', 'Adds 9 bibliography entries and 3 timeline events from HPPERPLEXITY.txt web research.'),
    'pdf_to_markdown.py': ('PDF to Markdown', 'Extracts all PDFs to markdown with YAML frontmatter, page markers, and metadata lookup.'),
    'chunk_documents.py': ('Chunk Documents', 'Splits markdown files into ~1500-word semantic chunks for RAG/retrieval systems.'),
}


def markdown_to_html(md_text):
    """Minimal markdown-to-HTML conversion for document display."""
    import re
    lines = md_text.split('\n')
    html_lines = []
    in_code = False
    in_list = False
    in_table = False
    table_header_done = False

    for line in lines:
        # Code blocks
        if line.strip().startswith('```'):
            if in_code:
                html_lines.append('</code></pre>')
                in_code = False
            else:
                lang = line.strip()[3:]
                html_lines.append(f'<pre><code class="lang-{lang}">')
                in_code = True
            continue
        if in_code:
            html_lines.append(escape(line))
            continue

        # Close list if needed
        if in_list and not line.strip().startswith(('-', '*', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
            html_lines.append('</ul>')
            in_list = False

        # Tables
        if '|' in line and line.strip().startswith('|'):
            cells = [c.strip() for c in line.strip().split('|')[1:-1]]
            if all(set(c) <= set('- :') for c in cells):
                table_header_done = True
                continue
            if not in_table:
                html_lines.append('<table class="doc-table">')
                in_table = True
            tag = 'th' if not table_header_done else 'td'
            row = ''.join(f'<{tag}>{escape(c)}</{tag}>' for c in cells)
            html_lines.append(f'<tr>{row}</tr>')
            continue
        elif in_table:
            html_lines.append('</table>')
            in_table = False
            table_header_done = False

        stripped = line.strip()

        # Headings
        if stripped.startswith('### '):
            html_lines.append(f'<h4>{escape(stripped[4:])}</h4>')
        elif stripped.startswith('## '):
            html_lines.append(f'<h3>{escape(stripped[3:])}</h3>')
        elif stripped.startswith('# '):
            html_lines.append(f'<h2>{escape(stripped[2:])}</h2>')
        elif stripped.startswith('---'):
            html_lines.append('<hr>')
        elif stripped.startswith(('- ', '* ')):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            html_lines.append(f'<li>{escape(stripped[2:])}</li>')
        elif stripped.startswith('>'):
            html_lines.append(f'<blockquote>{escape(stripped[1:].strip())}</blockquote>')
        elif stripped == '':
            html_lines.append('')
        else:
            # Apply inline formatting
            text = escape(stripped)
            # Bold
            text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
            # Italic
            text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
            # Inline code
            text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
            html_lines.append(f'<p>{text}</p>')

    if in_list:
        html_lines.append('</ul>')
    if in_table:
        html_lines.append('</table>')
    if in_code:
        html_lines.append('</code></pre>')

    return '\n'.join(html_lines)


def build_docs_pages():
    """Generate docs/index.html and docs/*.html from project markdown files."""
    docs_dir = SITE_DIR / 'docs'
    docs_dir.mkdir(exist_ok=True)

    doc_css = '<style>' + """
        .docs-page { max-width: 900px; margin: 2rem auto; padding: 0 2rem; }
        .docs-table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; }
        .docs-table th, .docs-table td { padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid var(--border); }
        .docs-table th { font-family: var(--font-sans); font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
        .docs-table td a { color: var(--accent); text-decoration: none; font-weight: 600; }
        .docs-table td a:hover { text-decoration: underline; }
        .docs-table .doc-summary { font-size: 0.85rem; color: var(--text-muted); }
        .doc-content { max-width: 800px; margin: 2rem auto; padding: 0 2rem; }
        .doc-content h2 { color: var(--accent); margin: 2rem 0 0.5rem; }
        .doc-content h3 { color: var(--text); margin: 1.5rem 0 0.5rem; }
        .doc-content h4 { color: var(--text-muted); margin: 1rem 0 0.5rem; }
        .doc-content p { margin-bottom: 0.75rem; line-height: 1.7; }
        .doc-content pre { background: var(--bg); padding: 1rem; border-radius: 4px; overflow-x: auto; font-size: 0.85rem; margin: 1rem 0; }
        .doc-content code { font-size: 0.9em; background: var(--bg); padding: 0.1rem 0.3rem; border-radius: 2px; }
        .doc-content pre code { background: none; padding: 0; }
        .doc-content blockquote { border-left: 3px solid var(--accent-light); padding-left: 1rem; color: var(--text-muted); font-style: italic; margin: 1rem 0; }
        .doc-content ul { margin: 0.5rem 0 1rem 1.5rem; }
        .doc-content li { margin-bottom: 0.3rem; line-height: 1.6; }
        .doc-content hr { border: none; border-top: 1px solid var(--border); margin: 2rem 0; }
        .doc-content table.doc-table { width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.9rem; }
        .doc-content table.doc-table th, .doc-content table.doc-table td { padding: 0.5rem 0.75rem; border: 1px solid var(--border); }
        .doc-content table.doc-table th { background: var(--bg); font-weight: 600; }
    """ + '</style>'

    # Read all docs and build pages
    docs = []
    for filename, (title, summary) in sorted(DOC_METADATA.items()):
        filepath = BASE_DIR / filename
        if not filepath.exists():
            continue

        slug = slugify(title)
        content = filepath.read_text(encoding='utf-8')
        word_count = len(content.split())

        docs.append({
            'filename': filename,
            'title': title,
            'summary': summary,
            'slug': slug,
            'word_count': word_count,
        })

        # Build detail page
        content_html = markdown_to_html(content)
        detail_body = f"""
        <div class="doc-content">
            <p><a href="index.html">&larr; All Documents</a></p>
            <h2>{escape(title)}</h2>
            <p style="color:var(--text-muted); font-family:var(--font-sans); font-size:0.85rem; margin-bottom:1.5rem">
                {escape(filename)} &mdash; {word_count:,} words</p>
            {content_html}
        </div>"""

        detail_page = page_shell(title, detail_body, active_nav='docs', depth=1)
        (docs_dir / f'{slug}.html').write_text(detail_page, encoding='utf-8')

    # Build index page
    rows_html = ''
    for d in docs:
        rows_html += f"""
            <tr>
                <td><a href="{d['slug']}.html">{escape(d['title'])}</a></td>
                <td class="doc-summary">{escape(d['summary'])}</td>
                <td style="font-family:var(--font-sans); font-size:0.85rem; white-space:nowrap">{d['word_count']:,}</td>
            </tr>"""

    index_body = f"""
        <div class="docs-page">
            <div class="intro">
                <h2>Project Documents</h2>
                <p>{len(docs)} documents covering methodology, architecture, analysis, and lessons learned.</p>
            </div>
            <table class="docs-table">
                <thead><tr><th>Document</th><th>Description</th><th>Words</th></tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>"""

    index_page = page_shell('Documents', index_body, active_nav='docs', depth=1)
    (docs_dir / 'index.html').write_text(index_page, encoding='utf-8')
    print(f"  docs/index.html + {len(docs)} document pages")


def build_code_pages():
    """Generate code/index.html and code/*.html from Python scripts."""
    code_dir = SITE_DIR / 'code'
    code_dir.mkdir(exist_ok=True)

    code_css = '<style>' + """
        .code-page { max-width: 900px; margin: 2rem auto; padding: 0 2rem; }
        .code-table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; }
        .code-table th, .code-table td { padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid var(--border); }
        .code-table th { font-family: var(--font-sans); font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
        .code-table td a { color: var(--accent); text-decoration: none; font-weight: 600; font-family: monospace; }
        .code-table td a:hover { text-decoration: underline; }
        .code-table .code-summary { font-size: 0.85rem; color: var(--text-muted); }
        .code-content { max-width: 1000px; margin: 2rem auto; padding: 0 2rem; }
        .code-content h2 { color: var(--accent); margin-bottom: 0.5rem; }
        .code-content pre {
            background: #1e1e1e; color: #d4d4d4; padding: 1.5rem; border-radius: 4px;
            overflow-x: auto; font-size: 0.82rem; line-height: 1.5;
            max-height: 80vh; overflow-y: auto;
        }
        .code-content .line-num { color: #858585; user-select: none; display: inline-block; width: 3.5em; text-align: right; margin-right: 1em; }
        .code-meta { font-family: var(--font-sans); font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1.5rem; }
    """ + '</style>'

    scripts = []
    scripts_dir = BASE_DIR / 'scripts'

    for filename, (title, summary) in sorted(SCRIPT_METADATA.items()):
        filepath = scripts_dir / filename
        if not filepath.exists():
            continue

        slug = slugify(filename.replace('.py', ''))
        content = filepath.read_text(encoding='utf-8')
        line_count = len(content.splitlines())

        scripts.append({
            'filename': filename,
            'title': title,
            'summary': summary,
            'slug': slug,
            'line_count': line_count,
        })

        # Build detail page with syntax-highlighted code
        lines = content.splitlines()
        code_lines = []
        for i, line in enumerate(lines, 1):
            num = f'<span class="line-num">{i}</span>'
            code_lines.append(f'{num}{escape(line)}')
        code_html = '\n'.join(code_lines)

        detail_body = f"""
        <div class="code-content">
            <p><a href="index.html">&larr; All Scripts</a></p>
            <h2>{escape(title)}</h2>
            <div class="code-meta">{escape(filename)} &mdash; {line_count} lines</div>
            <p style="margin-bottom:1rem">{escape(summary)}</p>
            <pre>{code_html}</pre>
        </div>"""

        detail_page = page_shell(title, detail_body, active_nav='code', depth=1)
        (code_dir / f'{slug}.html').write_text(detail_page, encoding='utf-8')

    # Build index page
    rows_html = ''
    for s in scripts:
        rows_html += f"""
            <tr>
                <td><a href="{s['slug']}.html">{escape(s['filename'])}</a></td>
                <td>{escape(s['title'])}</td>
                <td class="code-summary">{escape(s['summary'])}</td>
                <td style="font-family:var(--font-sans); font-size:0.85rem; white-space:nowrap">{s['line_count']}</td>
            </tr>"""

    index_body = f"""
        <div class="code-page">
            <div class="intro">
                <h2>Pipeline Scripts</h2>
                <p>{len(scripts)} Python scripts that build the database, generate the site, and validate the data.
                SQLite is the source of truth; these scripts are the processing pipeline.</p>
            </div>
            <table class="code-table">
                <thead><tr><th>Script</th><th>Name</th><th>Description</th><th>Lines</th></tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>"""

    index_page = page_shell('Code', index_body, active_nav='code', depth=1)
    (code_dir / 'index.html').write_text(index_page, encoding='utf-8')
    print(f"  code/index.html + {len(scripts)} script pages")


# ============================================================
# Update main index.html with nav
# ============================================================

def update_index_nav():
    """Replace nav bar in index.html with current version, fix CSS links."""
    index_path = SITE_DIR / 'index.html'
    if not index_path.exists():
        return

    content = index_path.read_text(encoding='utf-8')
    updated = False

    # Replace any existing nav with current 8-link version
    import re
    nav = nav_html('home')
    old_nav_pattern = r'<nav class="site-nav">.*?</nav>'
    if re.search(old_nav_pattern, content):
        content = re.sub(old_nav_pattern, nav, content)
        updated = True
    elif 'site-nav' not in content:
        content = content.replace(
            '</div>\n    </header>',
            f'    {nav}\n        </div>\n    </header>',
            1
        )
        updated = True

    # Fix CSS links: add scholars.css and components.css if missing
    if 'scholars.css' not in content:
        content = content.replace(
            '<link rel="stylesheet" href="style.css">',
            '<link rel="stylesheet" href="style.css">\n    <link rel="stylesheet" href="scholars.css">\n    <link rel="stylesheet" href="components.css">'
        )
        updated = True

    # Add meta description if missing
    if 'meta name="description"' not in content:
        content = content.replace(
            '<meta name="viewport"',
            '<meta name="description" content="Digital scholarship and marginalia of the Hypnerotomachia Poliphili (Venice, 1499)">\n    <meta name="viewport"'
        )
        updated = True

    if updated:
        index_path.write_text(content, encoding='utf-8')
        print("  index.html: nav + CSS updated")


# ============================================================
# Update CSS for new components
# ============================================================

def update_styles():
    """Append new styles to style.css for nav, badges, etc."""
    css_path = SITE_DIR / 'style.css'
    content = css_path.read_text(encoding='utf-8')

    if 'site-nav' in content:
        return  # Already updated

    additions = """

/* ===== Site Navigation ===== */
.site-nav {
    margin-top: 1.5rem;
    display: flex;
    justify-content: center;
    gap: 0.25rem;
    flex-wrap: wrap;
}

.site-nav a {
    color: #9a8c7a;
    text-decoration: none;
    font-family: var(--font-sans);
    font-size: 0.9rem;
    padding: 0.4rem 1rem;
    border-radius: 3px;
    transition: all 0.2s;
}

.site-nav a:hover {
    color: var(--accent-light);
    background: rgba(255,255,255,0.05);
}

.site-nav a.active {
    color: var(--header-text);
    background: rgba(255,255,255,0.1);
}

/* ===== Review & Confidence Badges ===== */
.review-badge {
    display: inline-block;
    padding: 0.1rem 0.4rem;
    background: #fff3cd;
    color: #856404;
    border-radius: 2px;
    font-size: 0.65rem;
    font-weight: 600;
    font-family: var(--font-sans);
    text-transform: uppercase;
    letter-spacing: 0.03em;
    vertical-align: middle;
    margin-left: 0.3rem;
}

.confidence-badge {
    display: inline-block;
    padding: 0.1rem 0.4rem;
    border-radius: 2px;
    font-size: 0.65rem;
    font-weight: 600;
    font-family: var(--font-sans);
    text-transform: uppercase;
    letter-spacing: 0.03em;
    vertical-align: middle;
    margin-left: 0.3rem;
}

.confidence-high { background: #d4edda; color: #155724; }
.confidence-medium { background: #fff3cd; color: #856404; }
.confidence-low { background: #f8d7da; color: #721c24; }
.confidence-provisional { background: #e2e3e5; color: #383d41; }
"""

    css_path.write_text(content + additions, encoding='utf-8')
    print("  style.css: nav + badge styles added")


# ============================================================
# Main
# ============================================================

def main():
    print("=== Building Site ===\n")

    conn = sqlite3.connect(DB_PATH)

    print("Exporting data...")
    export_data_json(conn)

    print("\nBuilding pages...")
    update_styles()
    update_index_nav()
    build_scholars_pages(conn)
    build_dictionary_pages(conn)
    build_marginalia_pages(conn)
    build_bibliography_page(conn)
    build_docs_pages()
    build_code_pages()
    build_about_page(conn)

    conn.close()
    print("\n=== Build Complete ===")


if __name__ == "__main__":
    main()
```

---

## catalog_images

`scripts/catalog_images.py`

```python
"""Catalog all manuscript images into the database."""

import sqlite3
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"


def parse_bl_filename(filename):
    """Parse BL C.60.o.12 image filenames.

    Patterns:
      C_60_o_12-NNN.jpg  -> sequential page scan
      BL HP NN.jpg        -> marginalia detail photo
      BL 2.1.jpg, BL2.jpg -> supplementary photos
    """
    # Sequential page scans
    m = re.match(r'C_60_o_12-(\d{3})\.jpg', filename)
    if m:
        seq = int(m.group(1))
        return {
            'folio_number': str(seq),
            'side': None,  # not encoded in filename
            'page_type': 'PAGE',
            'sort_order': seq,
        }

    # Marginalia detail photos
    m = re.match(r'BL\s*HP\s*(\d+)\.jpg', filename)
    if m:
        num = int(m.group(1))
        return {
            'folio_number': None,
            'side': None,
            'page_type': 'MARGINALIA_DETAIL',
            'sort_order': 1000 + num,
        }

    # Other BL supplementary
    m = re.match(r'BL\s*[\d.]+\.jpg', filename)
    if m:
        return {
            'folio_number': None,
            'side': None,
            'page_type': 'OTHER',
            'sort_order': 2000,
        }

    return {
        'folio_number': None,
        'side': None,
        'page_type': 'OTHER',
        'sort_order': 9999,
    }


def parse_siena_filename(filename):
    """Parse Siena O.III.38 image filenames.

    Patterns:
      O.III.38_NNNNr.jpg / O.III.38_NNNNv.jpg  -> folio recto/verso
      O.III.38_000antcop.jpg                     -> front cover
      O.III.38_000fdg1r.jpg                      -> guard leaf
      O.III.38_postcop.jpg                       -> back cover
      Siena HP N.jpg / Siena Hp N.jpg            -> marginalia detail
    """
    # Standard folio pages
    m = re.match(r'O\.III\.38_(\d{4})([rv])\.jpg', filename)
    if m:
        folio = int(m.group(1))
        side = m.group(2)
        sort_order = folio * 2 + (0 if side == 'r' else 1)
        return {
            'folio_number': str(folio),
            'side': side,
            'page_type': 'PAGE',
            'sort_order': sort_order,
        }

    # Cover and guard pages
    if 'antcop' in filename or 'postcop' in filename:
        sort_order = -2 if 'antcop' in filename else 99999
        return {
            'folio_number': None,
            'side': None,
            'page_type': 'COVER',
            'sort_order': sort_order,
        }

    if 'fdg' in filename or 'risg' in filename:
        sort_order = -1
        return {
            'folio_number': None,
            'side': None,
            'page_type': 'GUARD',
            'sort_order': sort_order,
        }

    # Marginalia detail photos
    m = re.match(r'Siena\s*[Hh][Pp]\s*(\d+)\.jpg', filename, re.IGNORECASE)
    if m:
        num = int(m.group(1))
        return {
            'folio_number': None,
            'side': None,
            'page_type': 'MARGINALIA_DETAIL',
            'sort_order': 100000 + num,
        }

    return {
        'folio_number': None,
        'side': None,
        'page_type': 'OTHER',
        'sort_order': 999999,
    }


def catalog_manuscript(conn, shelfmark, parser_fn):
    """Catalog all images for a manuscript."""
    cur = conn.cursor()
    cur.execute("SELECT id, image_dir FROM manuscripts WHERE shelfmark = ?", (shelfmark,))
    row = cur.fetchone()
    if not row:
        print(f"  WARNING: Manuscript {shelfmark} not found in database")
        return 0

    ms_id, image_dir = row
    img_path = BASE_DIR / image_dir
    if not img_path.exists():
        print(f"  WARNING: Image directory not found: {img_path}")
        return 0

    count = 0
    for f in sorted(img_path.glob('*.jpg')):
        parsed = parser_fn(f.name)
        relative = f"{image_dir}/{f.name}"
        cur.execute(
            """INSERT OR IGNORE INTO images
               (manuscript_id, filename, folio_number, side, page_type, sort_order, relative_path)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (ms_id, f.name, parsed['folio_number'], parsed['side'],
             parsed['page_type'], parsed['sort_order'], relative)
        )
        count += 1

    conn.commit()
    return count


def main():
    conn = sqlite3.connect(DB_PATH)

    print("Cataloging BL C.60.o.12 images...")
    bl_count = catalog_manuscript(conn, 'C.60.o.12', parse_bl_filename)
    print(f"  {bl_count} images cataloged")

    print("Cataloging Siena O.III.38 images...")
    siena_count = catalog_manuscript(conn, 'O.III.38', parse_siena_filename)
    print(f"  {siena_count} images cataloged")

    # Summary stats
    cur = conn.cursor()
    for page_type in ['PAGE', 'MARGINALIA_DETAIL', 'COVER', 'GUARD', 'OTHER']:
        cur.execute("SELECT COUNT(*) FROM images WHERE page_type = ?", (page_type,))
        print(f"  {page_type}: {cur.fetchone()[0]}")

    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()
```

---

## chunk_documents

`scripts/chunk_documents.py`

```python
"""Split markdown files into semantic chunks."""

import re
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MD_DIR = BASE_DIR / "md"
CHUNKS_DIR = BASE_DIR / "chunks"

TARGET_CHUNK_SIZE = 1500  # words
MIN_CHUNK_SIZE = 200  # words


def parse_frontmatter(text):
    """Extract YAML frontmatter and body from markdown."""
    if text.startswith('---'):
        end = text.find('---', 3)
        if end > 0:
            frontmatter = text[3:end].strip()
            body = text[end + 3:].strip()
            # Parse simple YAML
            meta = {}
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, _, val = line.partition(':')
                    val = val.strip().strip('"').strip("'")
                    meta[key.strip()] = val
            return meta, body
    return {}, text


def find_section_breaks(text):
    """Find natural section breaks in the text."""
    # Look for markdown headings
    heading_pattern = re.compile(r'^(#{1,3})\s+(.+)$', re.MULTILINE)
    # Look for page markers
    page_pattern = re.compile(r'^<!-- Page (\d+) -->$', re.MULTILINE)
    # Look for horizontal rules
    rule_pattern = re.compile(r'^---+$', re.MULTILINE)

    breaks = []
    for m in heading_pattern.finditer(text):
        level = len(m.group(1))
        breaks.append({
            'pos': m.start(),
            'type': 'heading',
            'level': level,
            'title': m.group(2).strip(),
        })

    for m in page_pattern.finditer(text):
        breaks.append({
            'pos': m.start(),
            'type': 'page',
            'level': 99,
            'title': f'Page {m.group(1)}',
        })

    for m in rule_pattern.finditer(text):
        breaks.append({
            'pos': m.start(),
            'type': 'rule',
            'level': 99,
            'title': '',
        })

    breaks.sort(key=lambda b: b['pos'])
    return breaks


def chunk_by_headings(text, meta):
    """Split text into chunks based on headings, page markers, and size."""
    breaks = find_section_breaks(text)
    total_words = len(text.split())

    # If we have good heading structure, split by headings
    heading_breaks = [b for b in breaks if b['type'] == 'heading']

    if len(heading_breaks) >= 3:
        chunks = []
        for i, brk in enumerate(heading_breaks):
            start = brk['pos']
            end = heading_breaks[i + 1]['pos'] if i + 1 < len(heading_breaks) else len(text)
            chunk_text = text[start:end].strip()
            word_count = len(chunk_text.split())

            if word_count >= MIN_CHUNK_SIZE:
                chunks.append({
                    'text': chunk_text,
                    'title': brk['title'],
                    'word_count': word_count,
                })
            elif chunks:
                # Merge small chunks with previous
                chunks[-1]['text'] += '\n\n' + chunk_text
                chunks[-1]['word_count'] += word_count

        # Handle text before first heading
        pre_text = text[:heading_breaks[0]['pos']].strip()
        if pre_text and len(pre_text.split()) >= MIN_CHUNK_SIZE:
            chunks.insert(0, {
                'text': pre_text,
                'title': 'Introduction',
                'word_count': len(pre_text.split()),
            })

        # If chunks are still too big (>3000 words), sub-chunk them
        final_chunks = []
        for chunk in chunks:
            if chunk['word_count'] > 3000:
                sub = chunk_by_size(chunk['text'], base_title=chunk['title'])
                final_chunks.extend(sub)
            else:
                final_chunks.append(chunk)
        return final_chunks

    # For large documents without headings, split by page markers
    page_breaks = [b for b in breaks if b['type'] == 'page']
    if page_breaks and total_words > TARGET_CHUNK_SIZE * 2:
        return chunk_by_pages(text, page_breaks)

    # Small documents: split by size if needed
    if total_words > TARGET_CHUNK_SIZE * 2:
        return chunk_by_size(text)

    # Small enough to be one chunk
    if total_words >= MIN_CHUNK_SIZE:
        return [{'text': text, 'title': meta.get('title', 'Full Text'),
                 'word_count': total_words}]
    return []


def chunk_by_pages(text, page_breaks):
    """Group page markers into chunks of ~TARGET_CHUNK_SIZE words."""
    chunks = []
    current_text = []
    current_words = 0
    current_start_page = None

    for i, brk in enumerate(page_breaks):
        start = brk['pos']
        end = page_breaks[i + 1]['pos'] if i + 1 < len(page_breaks) else len(text)
        page_text = text[start:end].strip()
        page_words = len(page_text.split())
        page_num = brk['title'].replace('Page ', '')

        if current_start_page is None:
            current_start_page = page_num

        if current_words + page_words > TARGET_CHUNK_SIZE and current_words >= MIN_CHUNK_SIZE:
            chunks.append({
                'text': '\n\n'.join(current_text),
                'title': f'Pages {current_start_page}-{page_num}',
                'word_count': current_words,
            })
            current_text = [page_text]
            current_words = page_words
            current_start_page = page_num
        else:
            current_text.append(page_text)
            current_words += page_words

    if current_text and current_words >= MIN_CHUNK_SIZE:
        chunks.append({
            'text': '\n\n'.join(current_text),
            'title': f'Pages {current_start_page}-end',
            'word_count': current_words,
        })

    return chunks


def chunk_by_size(text, base_title=None):
    """Split text into roughly equal chunks by word count."""
    paragraphs = re.split(r'\n\n+', text)
    chunks = []
    current_text = []
    current_words = 0

    for para in paragraphs:
        para_words = len(para.split())
        if current_words + para_words > TARGET_CHUNK_SIZE and current_words >= MIN_CHUNK_SIZE:
            n = len(chunks) + 1
            title = f'{base_title} (part {n})' if base_title else f'Section {n}'
            chunks.append({
                'text': '\n\n'.join(current_text),
                'title': title,
                'word_count': current_words,
            })
            current_text = [para]
            current_words = para_words
        else:
            current_text.append(para)
            current_words += para_words

    if current_text:
        n = len(chunks) + 1
        title = f'{base_title} (part {n})' if base_title and len(chunks) > 0 else (base_title or f'Section {n}')
        chunks.append({
            'text': '\n\n'.join(current_text),
            'title': title,
            'word_count': current_words,
        })

    return chunks


def slugify(title):
    """Create a filename-safe slug from a title."""
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[\s]+', '_', slug).strip('_')
    return slug[:50] if slug else 'untitled'


def main():
    md_files = sorted(MD_DIR.glob('*.md'))
    print(f"Found {len(md_files)} markdown files to chunk")

    total_chunks = 0

    for md_path in md_files:
        doc_slug = md_path.stem
        doc_chunks_dir = CHUNKS_DIR / doc_slug
        doc_chunks_dir.mkdir(parents=True, exist_ok=True)

        text = md_path.read_text(encoding='utf-8')
        meta, body = parse_frontmatter(text)

        chunks = chunk_by_headings(body, meta)

        # Merge very small trailing chunks
        if len(chunks) > 1 and chunks[-1]['word_count'] < MIN_CHUNK_SIZE:
            chunks[-2]['text'] += '\n\n' + chunks[-1]['text']
            chunks[-2]['word_count'] += chunks[-1]['word_count']
            chunks.pop()

        for i, chunk in enumerate(chunks):
            chunk_slug = slugify(chunk['title'])
            chunk_filename = f"chunk_{i + 1:03d}_{chunk_slug}.md"
            chunk_path = doc_chunks_dir / chunk_filename

            frontmatter = f"""---
source: "md/{md_path.name}"
chunk: {i + 1}
total_chunks: {len(chunks)}
section: "{chunk['title']}"
word_count: {chunk['word_count']}
---

"""
            chunk_path.write_text(frontmatter + chunk['text'], encoding='utf-8')

        print(f"  {doc_slug}: {len(chunks)} chunks")
        total_chunks += len(chunks)

    print(f"\nTotal: {total_chunks} chunks from {len(md_files)} documents")


if __name__ == "__main__":
    main()
```

---

## corpus_search

`scripts/corpus_search.py`

```python
"""Corpus search utilities: search across markdown chunks and full documents.

Provides keyword-based search across the /chunks/ and /md/ directories
with provenance tracking. No embeddings required.

Functions:
    search_chunks(query, top_n=20) -> list of match dicts
    search_by_term(term_slug, synonyms=None) -> list of match dicts
    search_documents(query, doc_filter=None) -> list of match dicts
"""

import re
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CHUNKS_DIR = BASE_DIR / "chunks"
MD_DIR = BASE_DIR / "md"


def _parse_chunk_frontmatter(text):
    """Extract YAML frontmatter from a chunk file."""
    meta = {}
    if text.startswith('---'):
        end = text.find('---', 3)
        if end > 0:
            for line in text[3:end].strip().split('\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    val = val.strip().strip('"').strip("'")
                    meta[key.strip()] = val
    return meta


def _extract_page_refs(text):
    """Extract page markers from chunk text."""
    return re.findall(r'<!-- Page (\d+) -->', text)


def _score_match(text, query_terms):
    """Score a text block by frequency and proximity of query terms."""
    text_lower = text.lower()
    score = 0
    for term in query_terms:
        count = text_lower.count(term.lower())
        score += count
    return score


def _context_window(text, query_terms, window=300):
    """Extract the best context window around the query terms."""
    text_lower = text.lower()
    best_pos = -1
    best_score = 0

    for term in query_terms:
        pos = text_lower.find(term.lower())
        if pos >= 0:
            # Score this position by counting nearby term occurrences
            start = max(0, pos - window)
            end = min(len(text), pos + window)
            snippet = text_lower[start:end]
            score = sum(snippet.count(t.lower()) for t in query_terms)
            if score > best_score:
                best_score = score
                best_pos = pos

    if best_pos < 0:
        return text[:window * 2] if len(text) > window * 2 else text

    start = max(0, best_pos - window)
    end = min(len(text), best_pos + window)
    snippet = text[start:end].strip()

    # Clean up snippet boundaries
    if start > 0:
        first_space = snippet.find(' ')
        if first_space > 0:
            snippet = '...' + snippet[first_space:]
    if end < len(text):
        last_space = snippet.rfind(' ')
        if last_space > 0:
            snippet = snippet[:last_space] + '...'

    return snippet


def search_chunks(query, top_n=20):
    """Search across all chunk files for passages matching query.

    Args:
        query: Search string (can be multiple words)
        top_n: Maximum results to return

    Returns:
        List of dicts: {chunk_path, source_doc, section, page_refs,
                        matched_text, relevance_score, word_count}
    """
    if not CHUNKS_DIR.exists():
        return []

    query_terms = [t for t in query.lower().split() if len(t) > 2]
    if not query_terms:
        return []

    results = []

    for doc_dir in sorted(CHUNKS_DIR.iterdir()):
        if not doc_dir.is_dir():
            continue
        for chunk_file in sorted(doc_dir.glob('chunk_*.md')):
            text = chunk_file.read_text(encoding='utf-8', errors='replace')
            meta = _parse_chunk_frontmatter(text)

            # Strip frontmatter for content search
            body_start = text.find('---', 3)
            body = text[body_start + 3:].strip() if body_start > 0 else text

            score = _score_match(body, query_terms)
            if score == 0:
                continue

            page_refs = _extract_page_refs(body)
            context = _context_window(body, query_terms)

            results.append({
                'chunk_path': str(chunk_file.relative_to(BASE_DIR)),
                'source_doc': meta.get('source', str(doc_dir.name)),
                'section': meta.get('section', ''),
                'page_refs': page_refs,
                'matched_text': context,
                'relevance_score': score,
                'word_count': int(meta.get('word_count', 0)),
            })

    results.sort(key=lambda x: x['relevance_score'], reverse=True)
    return results[:top_n]


def search_by_term(term_label, synonyms=None):
    """Search for a dictionary term across all chunks.

    Args:
        term_label: The term label (e.g. "Signature")
        synonyms: Optional list of alternative forms to search

    Returns:
        List of match dicts (same format as search_chunks)
    """
    search_terms = [term_label]
    if synonyms:
        search_terms.extend(synonyms)

    all_results = []
    seen_paths = set()

    for term in search_terms:
        results = search_chunks(term, top_n=30)
        for r in results:
            if r['chunk_path'] not in seen_paths:
                seen_paths.add(r['chunk_path'])
                all_results.append(r)

    all_results.sort(key=lambda x: x['relevance_score'], reverse=True)
    return all_results[:20]


def search_documents(query, doc_filter=None):
    """Search across full markdown documents (not chunks).

    Args:
        query: Search string
        doc_filter: Optional substring to filter document filenames

    Returns:
        List of dicts: {doc_path, page_refs, matched_text, relevance_score}
    """
    if not MD_DIR.exists():
        return []

    query_terms = [t for t in query.lower().split() if len(t) > 2]
    if not query_terms:
        return []

    results = []

    for md_file in sorted(MD_DIR.glob('*.md')):
        if doc_filter and doc_filter.lower() not in md_file.name.lower():
            continue

        text = md_file.read_text(encoding='utf-8', errors='replace')
        score = _score_match(text, query_terms)
        if score == 0:
            continue

        page_refs = _extract_page_refs(text)
        context = _context_window(text, query_terms)

        results.append({
            'doc_path': str(md_file.relative_to(BASE_DIR)),
            'page_refs': page_refs,
            'matched_text': context,
            'relevance_score': score,
        })

    results.sort(key=lambda x: x['relevance_score'], reverse=True)
    return results


if __name__ == "__main__":
    import sys
    query = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else "alchemical mercury"
    print(f"Searching chunks for: '{query}'\n")
    results = search_chunks(query, top_n=10)
    for i, r in enumerate(results, 1):
        print(f"{i}. [{r['relevance_score']}] {r['source_doc']}")
        print(f"   Section: {r['section']}")
        print(f"   Pages: {', '.join(r['page_refs'][:5])}")
        print(f"   Match: {r['matched_text'][:200]}...")
        print()
```

---

## dictionary_audit

`scripts/dictionary_audit.py`

```python
"""Dictionary coverage audit: identifies terms needing improvement.

Checks for:
- Missing fields (significance, source_documents, etc.)
- Terms stuck at DRAFT status
- Duplicate slugs
- Orphaned links (links to nonexistent terms)
- Terms with no related links
- Coverage by category

Outputs JSON report to staging/dictionary_audit.json and console summary.
"""

import sqlite3
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"
STAGING_DIR = BASE_DIR / "staging"


def audit():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    report = {
        'total_terms': 0,
        'by_status': {},
        'by_category': {},
        'missing_fields': [],
        'duplicate_slugs': [],
        'orphaned_links': [],
        'terms_without_links': [],
        'weak_terms': [],
        'summary': {},
    }

    # Total terms
    cur.execute("SELECT COUNT(*) FROM dictionary_terms")
    report['total_terms'] = cur.fetchone()[0]

    # By status
    cur.execute("SELECT review_status, COUNT(*) FROM dictionary_terms GROUP BY review_status")
    report['by_status'] = {row[0]: row[1] for row in cur.fetchall()}

    # By category
    cur.execute("SELECT category, COUNT(*) FROM dictionary_terms GROUP BY category ORDER BY COUNT(*) DESC")
    report['by_category'] = {row[0]: row[1] for row in cur.fetchall()}

    # Check for missing fields on each term
    cur.execute("""
        SELECT slug, label, category, definition_short, definition_long,
               source_basis, review_status, significance_to_hp,
               significance_to_scholarship, source_documents, source_page_refs,
               source_method, confidence
        FROM dictionary_terms ORDER BY slug
    """)

    important_fields = [
        'definition_long', 'source_basis', 'significance_to_hp',
        'significance_to_scholarship', 'source_documents'
    ]

    for row in cur.fetchall():
        missing = []
        for field in important_fields:
            val = row[field] if field in row.keys() else None
            if not val or (isinstance(val, str) and val.strip() == ''):
                missing.append(field)

        if missing:
            report['missing_fields'].append({
                'slug': row['slug'],
                'label': row['label'],
                'category': row['category'],
                'review_status': row['review_status'],
                'missing': missing,
            })

        # "Weak" = DRAFT + missing 2+ important fields
        if row['review_status'] == 'DRAFT' and len(missing) >= 2:
            report['weak_terms'].append({
                'slug': row['slug'],
                'label': row['label'],
                'missing_count': len(missing),
                'missing': missing,
            })

    # Duplicate slugs
    cur.execute("""
        SELECT slug, COUNT(*) FROM dictionary_terms
        GROUP BY slug HAVING COUNT(*) > 1
    """)
    report['duplicate_slugs'] = [row[0] for row in cur.fetchall()]

    # Orphaned links
    cur.execute("""
        SELECT l.id, l.term_id, l.linked_term_id
        FROM dictionary_term_links l
        LEFT JOIN dictionary_terms t1 ON l.term_id = t1.id
        LEFT JOIN dictionary_terms t2 ON l.linked_term_id = t2.id
        WHERE t1.id IS NULL OR t2.id IS NULL
    """)
    report['orphaned_links'] = [dict(row) for row in cur.fetchall()]

    # Terms without any links
    cur.execute("""
        SELECT t.slug, t.label FROM dictionary_terms t
        LEFT JOIN dictionary_term_links l ON t.id = l.term_id
        WHERE l.id IS NULL
    """)
    report['terms_without_links'] = [{'slug': row[0], 'label': row[1]} for row in cur.fetchall()]

    # Summary
    report['summary'] = {
        'total_terms': report['total_terms'],
        'draft_count': report['by_status'].get('DRAFT', 0),
        'verified_count': report['by_status'].get('VERIFIED', 0),
        'terms_with_missing_fields': len(report['missing_fields']),
        'weak_terms_count': len(report['weak_terms']),
        'duplicate_slugs_count': len(report['duplicate_slugs']),
        'orphaned_links_count': len(report['orphaned_links']),
        'terms_without_links_count': len(report['terms_without_links']),
        'categories': len(report['by_category']),
    }

    conn.close()

    # Write report
    STAGING_DIR.mkdir(exist_ok=True)
    report_path = STAGING_DIR / "dictionary_audit.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Console output
    print("=== Dictionary Audit ===\n")
    print(f"Total terms: {report['total_terms']}")
    print(f"By status: {report['by_status']}")
    print(f"Categories: {len(report['by_category'])}")
    for cat, count in report['by_category'].items():
        print(f"  {cat}: {count}")
    print(f"\nTerms with missing important fields: {len(report['missing_fields'])}")
    print(f"Weak terms (DRAFT + 2+ missing): {len(report['weak_terms'])}")
    if report['weak_terms']:
        for wt in report['weak_terms']:
            print(f"  - {wt['slug']}: missing {', '.join(wt['missing'])}")
    print(f"Duplicate slugs: {len(report['duplicate_slugs'])}")
    print(f"Orphaned links: {len(report['orphaned_links'])}")
    print(f"Terms without links: {len(report['terms_without_links'])}")
    if report['terms_without_links']:
        for t in report['terms_without_links']:
            print(f"  - {t['slug']}")
    print(f"\nReport written to: {report_path}")
    return report


if __name__ == "__main__":
    audit()
```

---

## enrich_dictionary

`scripts/enrich_dictionary.py`

```python
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
```

---

## export_showcase_data

`scripts/export_showcase_data.py`

```python
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
```

---

## extract_references

`scripts/extract_references.py`

```python
"""Extract folio/signature references from Russell's PhD dissertation."""

import sqlite3
import re
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF not installed. Run: pip install PyMuPDF")
    raise

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"
THESIS_FILENAME = "PhD_Thesis_ _James_Russell Hypnerotomachia Polyphili.pdf"
THESIS_PATH = BASE_DIR / THESIS_FILENAME

# Chapter page ranges (approximate, from TOC - 1-indexed PDF pages)
# These will be refined after first extraction pass
CHAPTER_RANGES = {
    1: (1, 40),      # The HP and its readership
    2: (41, 60),     # Literature Review
    3: (61, 80),     # Methodology
    4: (81, 100),    # Modena - F.C. Panini Estate
    5: (101, 122),   # Como - INCUN A.5.13
    6: (123, 170),   # London - BL C.60.o.12
    7: (171, 203),   # Buffalo
    8: (204, 230),   # Vatican
    9: (204, 250),   # Siena O.III.38 + Sydney
    10: (251, 262),  # Conclusions
}

# Manuscript shelfmark by chapter
CHAPTER_MANUSCRIPTS = {
    4: 'Modena (Panini)',
    5: 'INCUN A.5.13',
    6: 'C.60.o.12',
    7: 'Buffalo RBR',
    8: 'Inc.Stam.Chig.II.610',
    9: 'O.III.38',
}

# Regex patterns for signature references
# Matches: (a4r), (c7v), (p6v), a7r:, i6r, etc.
SIG_PATTERN = re.compile(
    r'(?:\(([a-zA-Z]{1,2}\d[rv])\))'  # parenthesized: (a4r)
    r'|(?:\b([a-zA-Z]{1,2}\d[rv]):)'   # with colon: a4r:
    r'|(?:\b([a-zA-Z]{1,2}\d[rv])\b)'  # bare: a4r (more false positives)
)

# Pattern for quoted marginal text (text in single quotes near a signature ref)
MARGINAL_QUOTE = re.compile(r"['\u2018]([^'\u2019]{3,200})['\u2019]")


def get_chapter(page_num):
    """Determine chapter number from PDF page number."""
    for ch, (start, end) in CHAPTER_RANGES.items():
        if start <= page_num <= end:
            return ch
    return None


def get_manuscript(chapter_num):
    """Get manuscript shelfmark from chapter number."""
    return CHAPTER_MANUSCRIPTS.get(chapter_num)


def extract_context(text, match_start, match_end, window=500):
    """Extract surrounding paragraph context."""
    # Find paragraph boundaries (double newline or start/end of text)
    para_start = text.rfind('\n\n', 0, match_start)
    para_start = para_start + 2 if para_start >= 0 else max(0, match_start - window)

    para_end = text.find('\n\n', match_end)
    para_end = para_end if para_end >= 0 else min(len(text), match_end + window)

    return text[para_start:para_end].strip()


def extract_marginal_text(context, sig_pos):
    """Find quoted text near a signature reference."""
    quotes = list(MARGINAL_QUOTE.finditer(context))
    if not quotes:
        return None

    # Find the quote closest to the signature reference
    closest = min(quotes, key=lambda m: abs(m.start() - sig_pos))
    return closest.group(1)


def main():
    if not THESIS_PATH.exists():
        print(f"ERROR: Thesis not found at {THESIS_PATH}")
        return

    print(f"Opening {THESIS_FILENAME}...")
    doc = fitz.open(str(THESIS_PATH))
    total_pages = len(doc)
    print(f"  {total_pages} pages")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Clear existing refs
    cur.execute("DELETE FROM dissertation_refs")

    ref_count = 0
    all_sigs = set()

    for page_idx in range(total_pages):
        page = doc[page_idx]
        text = page.get_text()
        page_num = page_idx + 1  # 1-indexed

        for match in SIG_PATTERN.finditer(text):
            # Get the matched signature from whichever group matched
            sig = match.group(1) or match.group(2) or match.group(3)
            if not sig:
                continue

            # Skip very short matches that are likely false positives
            # (e.g., "in" + digit + r/v)
            quire_part = re.match(r'([a-zA-Z]+)', sig).group(1)
            if quire_part.lower() in ('in', 'an', 'on', 'or', 'as', 'at', 'is', 'it',
                                       'no', 'so', 'to', 'do', 'go', 'he', 'me', 'we',
                                       'be', 'of', 'if', 'up', 'my', 'by'):
                continue

            all_sigs.add(sig)
            chapter = get_chapter(page_num)
            manuscript = get_manuscript(chapter)

            context = extract_context(text, match.start(), match.end())
            marginal = extract_marginal_text(context, match.start() - (text.rfind('\n\n', 0, match.start()) or 0))

            cur.execute(
                """INSERT INTO dissertation_refs
                   (thesis_page, signature_ref, manuscript_shelfmark,
                    context_text, marginal_text, ref_type, chapter_num)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (page_num, sig, manuscript, context, marginal, 'MARGINALIA', chapter)
            )
            ref_count += 1

    conn.commit()
    doc.close()

    print(f"\nExtracted {ref_count} references")
    print(f"Unique signatures: {len(all_sigs)}")

    # Show distribution by chapter
    print("\nReferences by chapter:")
    for ch in range(1, 11):
        cur.execute("SELECT COUNT(*) FROM dissertation_refs WHERE chapter_num = ?", (ch,))
        count = cur.fetchone()[0]
        ms = CHAPTER_MANUSCRIPTS.get(ch, '')
        if count > 0:
            print(f"  Ch {ch} ({ms}): {count} refs")

    # Show sample references
    print("\nSample references:")
    cur.execute("""SELECT thesis_page, signature_ref, manuscript_shelfmark,
                   substr(context_text, 1, 100), marginal_text
                   FROM dissertation_refs LIMIT 10""")
    for row in cur.fetchall():
        page, sig, ms, ctx, marg = row
        print(f"  p.{page} {sig} [{ms}]: {ctx}...")
        if marg:
            print(f"    Marginal text: '{marg[:80]}'")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
```

---

## ingest_perplexity

`scripts/ingest_perplexity.py`

```python
"""Ingest new bibliography entries from HPPERPLEXITY.txt research into the database.

Adds entries that are genuinely new scholarship not already in our bibliography,
with proper source_method tagging.
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"

# New entries from HPPERPLEXITY.txt that are NOT already in our bibliography
NEW_ENTRIES = [
    # Scholarly articles discovered via Perplexity
    {
        "author": "Unknown (botanical study)",
        "title": "On the Botanical Content of Hypnerotomachia Poliphili",
        "year": "2016",
        "pub_type": "article",
        "journal": "Landscape Ecology / Taylor & Francis (Botanical Journal of the Linnean Society?)",
        "hp_relevance": "DIRECT",
        "topic_cluster": "architecture_gardens",
        "url": "https://www.tandfonline.com/doi/full/10.1080/23818107.2016.1166070",
        "notes": "Catalogues 285 plant entities referenced in the HP text. Via HPPERPLEXITY.txt.",
        "source_method": "WEB_SEARCH",
        "needs_verification": True,
    },
    {
        "author": "Unknown (musicological study)",
        "title": "Music and Its Powers in the Hypnerotomachia Poliphili (1499)",
        "year": "2020",
        "pub_type": "article",
        "journal": "Cahiers de recherches medievales et humanistes 39",
        "hp_relevance": "DIRECT",
        "topic_cluster": "text_image",
        "url": "https://classiques-garnier.com/cahiers-de-recherches-medievales-et-humanistes-journal-of-medieval-and-humanistic-studies-2020-1-n-39-music-and-its-powers-in-the-hypnerotomachia-poliphili-1499.html",
        "notes": "Musicological reading of musical scenes, instruments, and Ficinian spiritus. Via HPPERPLEXITY.txt.",
        "source_method": "WEB_SEARCH",
        "needs_verification": True,
    },
    {
        "author": "Unknown (UPenn repository)",
        "title": "Architectures of the Text: An Inquiry Into the Hypnerotomachia Poliphili",
        "year": None,
        "pub_type": "article",
        "journal": "University of Pennsylvania Repository",
        "hp_relevance": "DIRECT",
        "topic_cluster": "architecture_gardens",
        "url": "https://repository.upenn.edu/items/37a3b059-be9a-4b2a-aad4-9fc2feb5b7f1",
        "notes": "Architecture, design, and Aldine printing. Via HPPERPLEXITY.txt.",
        "source_method": "WEB_SEARCH",
        "needs_verification": True,
    },
    {
        "author": "Unknown (Polish publisher)",
        "title": "Hypnerotomachia Poliphili: Thoughts on the Earliest Reception",
        "year": None,
        "pub_type": "article",
        "journal": "Akademicka.pl (Polish academic press)",
        "hp_relevance": "DIRECT",
        "topic_cluster": "reception",
        "url": "https://books.akademicka.pl/publishing/catalog/download/145/488/469?inline=1",
        "notes": "Examines annotated copies and earliest readers. Via HPPERPLEXITY.txt.",
        "source_method": "WEB_SEARCH",
        "needs_verification": True,
    },

    # Digital editions and resources (not scholarship per se, but important references)
    {
        "author": "MIT Press",
        "title": "The Electronic Hypnerotomachia",
        "year": "1999",
        "pub_type": "book",
        "journal": "MIT Press (digital edition)",
        "hp_relevance": "PRIMARY",
        "topic_cluster": "text_image",
        "url": "https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pres_0/4196/HP.zip/hyptext1.htm",
        "notes": "Electronic text with typographic information. Companion to Lefaivre 1997.",
        "source_method": "WEB_SEARCH",
        "needs_verification": False,
    },

    # Routledge volume
    {
        "author": "Various (ed. unknown)",
        "title": "Francesco Colonna's Hypnerotomachia Poliphili and Its European Context",
        "year": "2023",
        "pub_type": "book",
        "journal": "Routledge (Anglo-Italian Renaissance Studies)",
        "hp_relevance": "DIRECT",
        "topic_cluster": "reception",
        "url": "https://api.pageplace.de/preview/DT0400.9781000911848_A46453224/preview-9781000911848_A46453224.pdf",
        "notes": "Chapters on narrative, architecture, travel, love, self-transformation. Via HPPERPLEXITY.txt.",
        "source_method": "WEB_SEARCH",
        "needs_verification": True,
    },

    # Music / creative works inspired by HP
    {
        "author": "Alexander Moosbrugger",
        "title": "Wind (opera based on Hypnerotomachia Poliphili)",
        "year": "2021",
        "pub_type": "book",
        "journal": "Contemporary opera",
        "hp_relevance": "INDIRECT",
        "topic_cluster": "reception",
        "notes": "Libretto drawn from German and English HP translations. Via HPPERPLEXITY.txt.",
        "source_method": "WEB_SEARCH",
        "needs_verification": True,
    },
    {
        "author": "Sagenhaft",
        "title": "Hypnerotomachia (dungeon synth EP)",
        "year": "2021",
        "pub_type": "book",
        "journal": "Moonlit Castle Records",
        "hp_relevance": "INDIRECT",
        "topic_cluster": "reception",
        "notes": "4-track EP inspired by the HP. Dungeon synth genre. Via HPPERPLEXITY.txt.",
        "source_method": "WEB_SEARCH",
        "needs_verification": True,
    },

    # The Codex 99 essay - important web resource
    {
        "author": "Codex 99",
        "title": "The Hypnerotomachia Poliphili (typographic essay)",
        "year": None,
        "pub_type": "article",
        "journal": "Codex 99 (web)",
        "hp_relevance": "INDIRECT",
        "topic_cluster": "material_bibliographic",
        "url": "http://www.codex99.com/typography/82.html",
        "notes": "Substantial web essay on printing, typography, and images with links to digitized copies.",
        "source_method": "WEB_SEARCH",
        "needs_verification": False,
    },
]

# Timeline events from Perplexity findings
NEW_TIMELINE = [
    (2021, None, 'OTHER', "Moosbrugger's opera Wind premieres",
     "German composer Alexander Moosbrugger uses HP translations as libretto for opera Wind.",
     'reception'),
    (2016, None, 'PUBLICATION', 'Botanical content study published',
     'Study cataloguing 285 plant entities referenced in the HP text.',
     'architecture_gardens'),
    (2020, None, 'PUBLICATION', 'Music and its powers study published',
     'Musicological analysis of musical episodes and Ficinian spiritus in the HP.',
     'text_image'),
]


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("Ingesting HPPERPLEXITY.txt entries...\n")

    inserted = 0
    skipped = 0
    for e in NEW_ENTRIES:
        # Check if already exists
        cur.execute(
            "SELECT id FROM bibliography WHERE title = ?",
            (e["title"],)
        )
        if cur.fetchone():
            skipped += 1
            continue

        cur.execute("""
            INSERT INTO bibliography
                (author, title, year, pub_type, journal_or_publisher,
                 hp_relevance, topic_cluster, notes,
                 in_collection, review_status, needs_review)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 'UNREVIEWED', 1)
        """, (e["author"], e["title"], e.get("year"),
              e["pub_type"], e.get("journal", ""),
              e["hp_relevance"], e.get("topic_cluster", ""),
              e.get("notes", "")))
        inserted += 1

    conn.commit()
    print(f"  Inserted {inserted} new bibliography entries (skipped {skipped} duplicates)")

    # Timeline events
    print("\nInserting timeline events...")
    tl_inserted = 0
    for year, year_end, evt_type, title, desc, topic in NEW_TIMELINE:
        cur.execute(
            "SELECT id FROM timeline_events WHERE title = ?", (title,)
        )
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO timeline_events
                    (year, year_end, event_type, title, description, needs_review, source_method)
                VALUES (?, ?, ?, ?, ?, 1, 'WEB_SEARCH')
            """, (year, year_end, evt_type, title, desc))
            tl_inserted += 1
    conn.commit()
    print(f"  Inserted {tl_inserted} timeline events")

    # Summary
    cur.execute("SELECT COUNT(*) FROM bibliography")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM bibliography WHERE in_collection = 1")
    have = cur.fetchone()[0]
    print(f"\nBibliography total: {total} entries ({have} in collection)")

    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()
```

---

## init_db

`scripts/init_db.py`

```python
"""Initialize the Hypnerotomachia Poliphili SQLite database."""

import sqlite3
import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    filename TEXT NOT NULL,
    title TEXT,
    author TEXT,
    year INTEGER,
    doc_type TEXT CHECK(doc_type IN ('PRIMARY_TEXT','DISSERTATION','SCHOLARSHIP','PRESENTATION')),
    page_count INTEGER,
    file_size_bytes INTEGER,
    has_selectable_text BOOLEAN
);

CREATE TABLE IF NOT EXISTS manuscripts (
    id INTEGER PRIMARY KEY,
    shelfmark TEXT NOT NULL UNIQUE,
    institution TEXT,
    city TEXT,
    description TEXT,
    image_count INTEGER,
    image_dir TEXT
);

CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY,
    manuscript_id INTEGER REFERENCES manuscripts(id),
    filename TEXT NOT NULL,
    folio_number TEXT,
    side TEXT CHECK(side IN ('r','v',NULL)),
    page_type TEXT CHECK(page_type IN ('PAGE','MARGINALIA_DETAIL','COVER','GUARD','OTHER')),
    sort_order INTEGER,
    relative_path TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS signature_map (
    id INTEGER PRIMARY KEY,
    signature TEXT NOT NULL UNIQUE,
    folio_number INTEGER,
    side TEXT CHECK(side IN ('r','v')),
    quire TEXT,
    leaf_in_quire INTEGER
);

CREATE TABLE IF NOT EXISTS dissertation_refs (
    id INTEGER PRIMARY KEY,
    thesis_page INTEGER,
    signature_ref TEXT,
    manuscript_shelfmark TEXT,
    context_text TEXT,
    marginal_text TEXT,
    source_text TEXT,
    ref_type TEXT CHECK(ref_type IN ('MARGINALIA','ILLUSTRATION','TEXT','BINDING','PROVENANCE')),
    chapter_num INTEGER
);

CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY,
    ref_id INTEGER REFERENCES dissertation_refs(id),
    image_id INTEGER REFERENCES images(id),
    match_method TEXT CHECK(match_method IN ('SIGNATURE_EXACT','FOLIO_EXACT','MANUAL')),
    confidence TEXT CHECK(confidence IN ('HIGH','MEDIUM','LOW')),
    needs_review BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    created_at TEXT DEFAULT (datetime('now'))
);
"""

# Known document metadata extracted from filenames
DOC_CLASSIFICATIONS = {
    'PRIMARY_TEXT': [
        'Francesco Colonna Hypnerotomachia Poliphili Da Capo',
        'Francesco Colonna Rino Avesani',
        'Hypnerotomachia by Francesco Colonna',
    ],
    'DISSERTATION': [
        'PhD_Thesis',
        'E_Thesis_Durham',
    ],
    'PRESENTATION': ['.pptx'],
}


def classify_doc(filename):
    for doc_type, patterns in DOC_CLASSIFICATIONS.items():
        for pat in patterns:
            if pat in filename:
                return doc_type
    return 'SCHOLARSHIP'


def extract_author_title(filename):
    """Best-effort extraction of author and title from filename."""
    name = Path(filename).stem
    # Remove common suffixes
    name = re.sub(r'\s*\(\d+\)\s*$', '', name)
    # Try splitting on known patterns
    parts = name.split(' - ')
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    # For space-separated names, take first few words as author guess
    return None, name


def populate_documents(conn):
    """Scan root dir for PDFs and PPTX files."""
    cur = conn.cursor()
    extensions = {'.pdf', '.pptx'}
    count = 0
    for f in sorted(BASE_DIR.iterdir()):
        if f.suffix.lower() in extensions and f.is_file():
            author, title = extract_author_title(f.name)
            doc_type = classify_doc(f.name)
            size = f.stat().st_size
            cur.execute(
                """INSERT OR IGNORE INTO documents
                   (filename, title, author, doc_type, file_size_bytes)
                   VALUES (?, ?, ?, ?, ?)""",
                (f.name, title, author, doc_type, size)
            )
            count += 1
    conn.commit()
    print(f"  Cataloged {count} documents")


def populate_manuscripts(conn):
    """Insert the two known manuscript records."""
    cur = conn.cursor()
    manuscripts = [
        (
            'C.60.o.12',
            'British Library',
            'London',
            'British Library copy of the 1499 Aldine Hypnerotomachia Poliphili with extensive marginalia',
            '3 BL C.60.o.12 Photos-20260319T001113Z-3-001/3 BL C.60.o.12 Photos'
        ),
        (
            'O.III.38',
            'Biblioteca degli Intronati',
            'Siena',
            'Siena copy of the 1499 Aldine Hypnerotomachia Poliphili, digital facsimile',
            'Siena O.III.38 Digital Facsimile-20260319T001110Z-3-001/Siena O.III.38 Digital Facsimile'
        ),
    ]
    for shelfmark, institution, city, desc, image_dir in manuscripts:
        # Count images
        img_path = BASE_DIR / image_dir
        img_count = len(list(img_path.glob('*.jpg'))) if img_path.exists() else 0
        cur.execute(
            """INSERT OR IGNORE INTO manuscripts
               (shelfmark, institution, city, description, image_count, image_dir)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (shelfmark, institution, city, desc, img_count, image_dir)
        )
    conn.commit()
    print("  Cataloged 2 manuscripts")


def main():
    print(f"Initializing database at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)

    print("Creating schema...")
    conn.executescript(SCHEMA)
    conn.execute("INSERT OR IGNORE INTO schema_version (version) VALUES (1)")
    conn.commit()

    print("Populating documents...")
    populate_documents(conn)

    print("Populating manuscripts...")
    populate_manuscripts(conn)

    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()
```

---

## match_refs_to_images

`scripts/match_refs_to_images.py`

```python
"""Match dissertation references to manuscript images via signature mapping."""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Clear existing matches
    cur.execute("DELETE FROM matches")

    # Get all dissertation refs
    cur.execute("""SELECT id, signature_ref, manuscript_shelfmark, chapter_num
                   FROM dissertation_refs""")
    refs = cur.fetchall()

    stats = {'total': len(refs), 'matched': 0, 'unmatched': 0,
             'high': 0, 'medium': 0, 'low': 0}

    for ref_id, sig_ref, ms_shelfmark, chapter_num in refs:
        # Look up signature in the mapping table
        # Try lowercase first (Russell typically uses lowercase)
        cur.execute("""SELECT folio_number, side FROM signature_map
                       WHERE signature = ? OR signature = ?""",
                    (sig_ref, sig_ref.lower()))
        sig_row = cur.fetchone()

        if not sig_row:
            stats['unmatched'] += 1
            continue

        folio_num, side = sig_row

        # Find matching image(s) for this manuscript
        if ms_shelfmark:
            # Try exact manuscript match
            cur.execute("""
                SELECT i.id FROM images i
                JOIN manuscripts m ON i.manuscript_id = m.id
                WHERE m.shelfmark = ?
                AND i.page_type = 'PAGE'
                AND (i.folio_number = ? OR i.folio_number = ?)
                ORDER BY i.sort_order
            """, (ms_shelfmark, str(folio_num), str(folio_num).zfill(4)))
            image_rows = cur.fetchall()

            if image_rows:
                # If side is specified and Siena images have side info, prefer exact match
                if side and ms_shelfmark == 'O.III.38':
                    cur.execute("""
                        SELECT i.id FROM images i
                        JOIN manuscripts m ON i.manuscript_id = m.id
                        WHERE m.shelfmark = ?
                        AND i.page_type = 'PAGE'
                        AND (i.folio_number = ? OR i.folio_number = ?)
                        AND i.side = ?
                    """, (ms_shelfmark, str(folio_num), str(folio_num).zfill(4), side))
                    exact_side = cur.fetchall()
                    if exact_side:
                        image_rows = exact_side

                for (image_id,) in image_rows:
                    confidence = 'HIGH'
                    method = 'SIGNATURE_EXACT'
                    cur.execute("""
                        INSERT INTO matches (ref_id, image_id, match_method, confidence, needs_review)
                        VALUES (?, ?, ?, ?, ?)
                    """, (ref_id, image_id, method, confidence, 0))
                    stats['matched'] += 1
                    stats['high'] += 1
            else:
                # Try matching across all manuscripts as fallback
                cur.execute("""
                    SELECT i.id, m.shelfmark FROM images i
                    JOIN manuscripts m ON i.manuscript_id = m.id
                    WHERE i.page_type = 'PAGE'
                    AND (i.folio_number = ? OR i.folio_number = ?)
                    ORDER BY i.sort_order
                """, (str(folio_num), str(folio_num).zfill(4)))
                fallback_rows = cur.fetchall()

                if fallback_rows:
                    for image_id, found_ms in fallback_rows:
                        cur.execute("""
                            INSERT INTO matches (ref_id, image_id, match_method, confidence, needs_review)
                            VALUES (?, ?, ?, ?, ?)
                        """, (ref_id, image_id, 'FOLIO_EXACT', 'MEDIUM', 1))
                        stats['matched'] += 1
                        stats['medium'] += 1
                else:
                    stats['unmatched'] += 1
        else:
            stats['unmatched'] += 1

    conn.commit()

    # Print statistics
    print("Match Statistics:")
    print(f"  Total references: {stats['total']}")
    print(f"  Matched: {stats['matched']}")
    print(f"  Unmatched: {stats['unmatched']}")
    print(f"  HIGH confidence: {stats['high']}")
    print(f"  MEDIUM confidence: {stats['medium']}")
    print(f"  LOW confidence: {stats['low']}")

    # Show unmatched refs
    cur.execute("""
        SELECT dr.id, dr.thesis_page, dr.signature_ref, dr.manuscript_shelfmark
        FROM dissertation_refs dr
        WHERE dr.id NOT IN (SELECT ref_id FROM matches)
        LIMIT 20
    """)
    unmatched = cur.fetchall()
    if unmatched:
        print(f"\nUnmatched references (first 20):")
        for ref_id, page, sig, ms in unmatched:
            print(f"  ref {ref_id}: p.{page} {sig} [{ms}]")

    # Show sample matches
    print("\nSample matches:")
    cur.execute("""
        SELECT dr.thesis_page, dr.signature_ref, dr.manuscript_shelfmark,
               i.filename, m.confidence
        FROM matches m
        JOIN dissertation_refs dr ON m.ref_id = dr.id
        JOIN images i ON m.image_id = i.id
        LIMIT 10
    """)
    for page, sig, ms, img_file, conf in cur.fetchall():
        print(f"  p.{page} {sig} [{ms}] -> {img_file} ({conf})")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
```

---

## migrate_dictionary_v2

`scripts/migrate_dictionary_v2.py`

```python
"""Extend dictionary_terms schema with new columns for enrichment pipeline.

Adds columns for:
- significance fields (HP-specific and scholarship-wide)
- source document tracking
- source method and notes
- confidence level

Idempotent: safe to run multiple times.
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"

NEW_COLUMNS = [
    ("significance_to_hp", "TEXT"),
    ("significance_to_scholarship", "TEXT"),
    ("related_scholars", "TEXT"),
    ("see_also_text", "TEXT"),
    ("source_documents", "TEXT"),
    ("source_page_refs", "TEXT"),
    ("source_quotes_short", "TEXT"),
    ("source_method", "TEXT"),
    ("confidence", "TEXT DEFAULT 'MEDIUM'"),
    ("notes", "TEXT"),
]


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Get existing columns
    cur.execute("PRAGMA table_info(dictionary_terms)")
    existing = {row[1] for row in cur.fetchall()}

    added = 0
    for col_name, col_type in NEW_COLUMNS:
        if col_name not in existing:
            cur.execute(f"ALTER TABLE dictionary_terms ADD COLUMN {col_name} {col_type}")
            print(f"  Added column: {col_name} ({col_type})")
            added += 1
        else:
            print(f"  Column exists: {col_name}")

    conn.commit()
    conn.close()
    print(f"\nDone. Added {added} new columns.")


if __name__ == "__main__":
    main()
```

---

## migrate_v2

`scripts/migrate_v2.py`

```python
"""Schema migration v2: Harden data model with review/provenance fields,
normalize tables, add dictionary and annotations support.

Idempotent — safe to run multiple times.
"""

import sqlite3
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"

MIGRATION_SQL = """
-- ============================================================
-- V2 MIGRATION: Hardened schema with review/provenance fields
-- ============================================================

-- 1. Annotations table: first-class representation of marginal notes
CREATE TABLE IF NOT EXISTS annotations (
    id INTEGER PRIMARY KEY,
    manuscript_id INTEGER REFERENCES manuscripts(id),
    hand_id INTEGER REFERENCES annotator_hands(id),
    signature_ref TEXT,
    folio_number INTEGER,
    side TEXT CHECK(side IN ('r','v',NULL)),
    annotation_text TEXT,
    annotation_type TEXT CHECK(annotation_type IN (
        'MARGINAL_NOTE','LABEL','SYMBOL','UNDERLINE','DRAWING',
        'CROSS_REFERENCE','INDEX_ENTRY','PROVENANCE','EMENDATION','OTHER'
    )),
    language TEXT,
    thesis_page INTEGER,
    thesis_chapter INTEGER,
    confidence TEXT CHECK(confidence IN ('HIGH','MEDIUM','LOW','PROVISIONAL')) DEFAULT 'PROVISIONAL',
    needs_review BOOLEAN DEFAULT 1,
    reviewed BOOLEAN DEFAULT 0,
    reviewed_by TEXT,
    reviewed_at TEXT,
    source_method TEXT CHECK(source_method IN (
        'MANUAL_TRANSCRIPTION','PDF_EXTRACTION','LLM_ASSISTED','INFERRED'
    )) DEFAULT 'INFERRED',
    notes TEXT
);

-- 2. Rename/normalize annotator_hands → annotators (keep old table, add view)
CREATE TABLE IF NOT EXISTS annotators (
    id INTEGER PRIMARY KEY,
    hand_label TEXT NOT NULL,
    manuscript_id INTEGER REFERENCES manuscripts(id),
    manuscript_shelfmark TEXT NOT NULL,
    attribution TEXT,
    attribution_confidence TEXT CHECK(attribution_confidence IN ('CERTAIN','PROBABLE','POSSIBLE','UNKNOWN')) DEFAULT 'POSSIBLE',
    language TEXT,
    ink_color TEXT,
    date_range TEXT,
    school TEXT,
    interests TEXT,
    description TEXT,
    is_alchemist BOOLEAN DEFAULT 0,
    chapter_num INTEGER,
    source_method TEXT DEFAULT 'LLM_ASSISTED',
    needs_review BOOLEAN DEFAULT 1,
    reviewed BOOLEAN DEFAULT 0,
    notes TEXT,
    UNIQUE(hand_label, manuscript_shelfmark)
);

-- 3. doc_folio_refs: references from any document to specific folios
CREATE TABLE IF NOT EXISTS doc_folio_refs (
    id INTEGER PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    signature_ref TEXT,
    folio_number INTEGER,
    side TEXT CHECK(side IN ('r','v',NULL)),
    manuscript_shelfmark TEXT,
    page_in_document INTEGER,
    context_text TEXT,
    marginal_text TEXT,
    ref_type TEXT CHECK(ref_type IN (
        'MARGINALIA','ILLUSTRATION','TEXT','BINDING','PROVENANCE','CROSS_REF'
    )),
    chapter_num INTEGER,
    hand_id INTEGER REFERENCES annotators(id),
    confidence TEXT CHECK(confidence IN ('HIGH','MEDIUM','LOW','PROVISIONAL')) DEFAULT 'PROVISIONAL',
    needs_review BOOLEAN DEFAULT 1,
    reviewed BOOLEAN DEFAULT 0,
    source_method TEXT DEFAULT 'PDF_EXTRACTION',
    notes TEXT
);

-- 4. Dictionary tables
CREATE TABLE IF NOT EXISTS dictionary_terms (
    id INTEGER PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    label TEXT NOT NULL,
    category TEXT NOT NULL,
    definition_short TEXT NOT NULL,
    definition_long TEXT,
    source_basis TEXT,
    review_status TEXT CHECK(review_status IN ('DRAFT','REVIEWED','VERIFIED')) DEFAULT 'DRAFT',
    needs_review BOOLEAN DEFAULT 1,
    reviewed BOOLEAN DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS dictionary_term_links (
    id INTEGER PRIMARY KEY,
    term_id INTEGER REFERENCES dictionary_terms(id),
    linked_term_id INTEGER REFERENCES dictionary_terms(id),
    link_type TEXT CHECK(link_type IN ('RELATED','SEE_ALSO','OPPOSITE','PARENT','CHILD')) DEFAULT 'RELATED',
    UNIQUE(term_id, linked_term_id, link_type)
);

-- 5. Topic cluster junction table (multi-value support)
CREATE TABLE IF NOT EXISTS document_topics (
    document_id INTEGER,
    topic TEXT NOT NULL,
    source_table TEXT NOT NULL CHECK(source_table IN ('bibliography','documents','summaries')),
    source_id INTEGER NOT NULL,
    PRIMARY KEY (source_table, source_id, topic)
);

-- 6. Add review/provenance columns to existing tables where missing
-- (ALTER TABLE IF NOT EXISTS not supported in SQLite, so we use try/except in Python)

-- 7. Update matches confidence constraint to include PROVISIONAL
-- (SQLite can't alter constraints, so we handle this in the matching logic)

-- 8. Update schema version
INSERT OR REPLACE INTO schema_version (version, created_at) VALUES (2, datetime('now'));
"""

# Columns to add to existing tables (table, column, type, default)
ALTER_COLUMNS = [
    ('matches', 'source_method', "TEXT DEFAULT 'FOLIO_EXACT'", None),
    ('matches', 'reviewed', 'BOOLEAN DEFAULT 0', None),
    ('matches', 'reviewed_by', 'TEXT', None),
    ('matches', 'notes', 'TEXT', None),
    ('documents', 'review_status', "TEXT DEFAULT 'UNREVIEWED'", None),
    ('documents', 'source_method', "TEXT DEFAULT 'FILESYSTEM_SCAN'", None),
    ('bibliography', 'review_status', "TEXT DEFAULT 'UNREVIEWED'", None),
    ('bibliography', 'needs_review', 'BOOLEAN DEFAULT 1', None),
    ('bibliography', 'reviewed', 'BOOLEAN DEFAULT 0', None),
    ('scholars', 'review_status', "TEXT DEFAULT 'UNREVIEWED'", None),
    ('scholars', 'needs_review', 'BOOLEAN DEFAULT 1', None),
    ('scholars', 'reviewed', 'BOOLEAN DEFAULT 0', None),
    ('scholars', 'source_method', "TEXT DEFAULT 'LLM_ASSISTED'", None),
    ('images', 'confidence', "TEXT DEFAULT 'PROVISIONAL'", None),
    ('images', 'needs_review', 'BOOLEAN DEFAULT 1', None),
    ('timeline_events', 'needs_review', 'BOOLEAN DEFAULT 1', None),
    ('timeline_events', 'source_method', "TEXT DEFAULT 'LLM_ASSISTED'", None),
]


def add_column_if_missing(cur, table, column, col_type, default):
    """Add a column to a table if it doesn't already exist."""
    cur.execute(f"PRAGMA table_info({table})")
    existing = {row[1] for row in cur.fetchall()}
    if column not in existing:
        sql = f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"
        cur.execute(sql)
        return True
    return False


def migrate_annotator_hands(conn):
    """Copy annotator_hands data into the new annotators table."""
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM annotator_hands")
    old_count = cur.fetchone()[0]
    if old_count == 0:
        return 0

    cur.execute("SELECT COUNT(*) FROM annotators")
    new_count = cur.fetchone()[0]
    if new_count > 0:
        return new_count  # Already migrated

    cur.execute("""
        INSERT OR IGNORE INTO annotators
            (hand_label, manuscript_shelfmark, attribution, language,
             ink_color, date_range, school, interests, description,
             is_alchemist, chapter_num, source_method, needs_review)
        SELECT
            hand_label, manuscript_shelfmark, attribution, language,
            ink_color, date_range, school, interests, description,
            is_alchemist, chapter_num, 'LLM_ASSISTED', 1
        FROM annotator_hands
    """)
    conn.commit()
    cur.execute("SELECT COUNT(*) FROM annotators")
    return cur.fetchone()[0]


def migrate_dissertation_refs(conn):
    """Copy dissertation_refs into doc_folio_refs with proper provenance."""
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM doc_folio_refs")
    if cur.fetchone()[0] > 0:
        return  # Already migrated

    # Find the Russell thesis document ID
    cur.execute("SELECT id FROM documents WHERE filename LIKE '%Russell%' LIMIT 1")
    row = cur.fetchone()
    doc_id = row[0] if row else None

    cur.execute("""
        INSERT INTO doc_folio_refs
            (document_id, signature_ref, manuscript_shelfmark,
             page_in_document, context_text, marginal_text,
             ref_type, chapter_num, hand_id, confidence, source_method)
        SELECT
            ?, signature_ref, manuscript_shelfmark,
            thesis_page, context_text, marginal_text,
            ref_type, chapter_num, hand_id, 'PROVISIONAL', 'PDF_EXTRACTION'
        FROM dissertation_refs
    """, (doc_id,))
    conn.commit()


def downgrade_bl_confidence(conn):
    """Downgrade all BL C.60.o.12 matches to LOW confidence.

    Rationale: BL copy is 1545 edition; our signature map is based on 1499.
    Photo numbers assumed to equal folio numbers without manual verification.
    """
    cur = conn.cursor()

    # Downgrade matches involving BL images
    cur.execute("""
        UPDATE matches SET confidence = 'LOW', needs_review = 1
        WHERE image_id IN (
            SELECT i.id FROM images i
            JOIN manuscripts m ON i.manuscript_id = m.id
            WHERE m.shelfmark = 'C.60.o.12'
        ) AND confidence != 'LOW'
    """)
    bl_downgraded = cur.rowcount

    # Also update doc_folio_refs for BL
    cur.execute("""
        UPDATE doc_folio_refs SET confidence = 'PROVISIONAL'
        WHERE manuscript_shelfmark = 'C.60.o.12'
    """)

    conn.commit()
    return bl_downgraded


def import_summaries_to_db(conn):
    """Import scholars/summaries.json into bibliography and scholars tables
    with proper provenance tracking."""
    summaries_path = BASE_DIR / "scholars" / "summaries.json"
    if not summaries_path.exists():
        print("  No summaries.json found, skipping")
        return

    with open(summaries_path, encoding='utf-8') as f:
        summaries = json.load(f)

    cur = conn.cursor()

    for s in summaries:
        author = s.get('author', 'Unknown')
        title = s.get('title', '')
        year = s.get('year')
        journal = s.get('journal', '')
        summary = s.get('summary', '')
        topic = s.get('topic_cluster', '')
        filename = s.get('filename', '')

        # Determine pub_type
        if 'PhD' in journal or 'Thesis' in journal or 'E-Thesis' in journal:
            pub_type = 'thesis'
        elif 'Press' in journal or '(' not in journal:
            pub_type = 'book'
        else:
            pub_type = 'article'

        # Upsert into bibliography
        cur.execute("""
            INSERT OR IGNORE INTO bibliography
                (author, title, year, pub_type, journal_or_publisher,
                 in_collection, collection_filename, hp_relevance,
                 topic_cluster, notes, review_status, needs_review)
            VALUES (?, ?, ?, ?, ?, 1, ?, 'DIRECT', ?, ?, 'UNREVIEWED', 1)
        """, (author, title, str(year) if year else None, pub_type, journal,
              filename, topic, f'LLM-generated summary: {summary[:200]}...'))

        # Upsert into scholars
        cur.execute("""
            INSERT OR IGNORE INTO scholars
                (name, source_method, needs_review, review_status)
            VALUES (?, 'LLM_ASSISTED', 1, 'UNREVIEWED')
        """, (author,))

        # Add topic to junction table
        if topic:
            cur.execute("SELECT id FROM bibliography WHERE author=? AND title=?", (author, title))
            bib_row = cur.fetchone()
            if bib_row:
                for t in topic.split(','):
                    t = t.strip()
                    if t:
                        cur.execute("""
                            INSERT OR IGNORE INTO document_topics
                                (source_table, source_id, topic)
                            VALUES ('bibliography', ?, ?)
                        """, (bib_row[0], t))

    conn.commit()
    print(f"  Imported {len(summaries)} summaries into bibliography/scholars")


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("=== Schema Migration V2 ===\n")

    # Step 1: Create new tables
    print("1. Creating new tables...")
    cur.executescript(MIGRATION_SQL)
    conn.commit()
    print("   Done (annotations, annotators, doc_folio_refs, dictionary_terms,")
    print("         dictionary_term_links, document_topics)")

    # Step 2: Add columns to existing tables
    print("\n2. Adding review/provenance columns to existing tables...")
    added = 0
    for table, column, col_type, default in ALTER_COLUMNS:
        if add_column_if_missing(cur, table, column, col_type, default):
            print(f"   + {table}.{column}")
            added += 1
    conn.commit()
    print(f"   Added {added} new columns")

    # Step 3: Migrate annotator_hands → annotators
    print("\n3. Migrating annotator_hands -> annotators...")
    n = migrate_annotator_hands(conn)
    print(f"   {n} annotators in normalized table")

    # Step 4: Migrate dissertation_refs → doc_folio_refs
    print("\n4. Migrating dissertation_refs -> doc_folio_refs...")
    migrate_dissertation_refs(conn)
    cur.execute("SELECT COUNT(*) FROM doc_folio_refs")
    print(f"   {cur.fetchone()[0]} folio references migrated")

    # Step 5: Downgrade BL confidence
    print("\n5. Downgrading BL C.60.o.12 matches to LOW confidence...")
    n = downgrade_bl_confidence(conn)
    print(f"   {n} matches downgraded")

    # Step 6: Import summaries.json with provenance
    print("\n6. Importing summaries.json into DB with provenance tracking...")
    import_summaries_to_db(conn)

    # Step 7: Summary
    print("\n=== Migration Summary ===")
    tables = [
        'documents', 'manuscripts', 'images', 'signature_map',
        'dissertation_refs', 'doc_folio_refs', 'matches',
        'annotator_hands', 'annotators', 'annotations',
        'bibliography', 'scholars', 'scholar_works',
        'timeline_events', 'dictionary_terms', 'dictionary_term_links',
        'document_topics', 'schema_version'
    ]
    for t in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            print(f"  {t}: {cur.fetchone()[0]} rows")
        except sqlite3.OperationalError:
            print(f"  {t}: (not found)")

    # Confidence distribution
    print("\nMatch confidence distribution:")
    cur.execute("SELECT confidence, COUNT(*) FROM matches GROUP BY confidence ORDER BY confidence")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    conn.close()
    print("\nMigration complete.")


if __name__ == "__main__":
    main()
```

---

## pdf_to_markdown

`scripts/pdf_to_markdown.py`

```python
"""Extract all PDFs to markdown files with YAML frontmatter."""

import re
import os
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF not installed. Run: pip install PyMuPDF")
    raise

BASE_DIR = Path(__file__).resolve().parent.parent
MD_DIR = BASE_DIR / "md"
MD_DIR.mkdir(exist_ok=True)

# Known metadata mappings for better frontmatter
KNOWN_METADATA = {
    'PhD_Thesis_ _James_Russell': {
        'title': 'Hypnerotomachia Poliphili: A Study of Marginal Annotations in Six Copies',
        'author': 'James Russell',
        'year': 2024,
        'doc_type': 'DISSERTATION',
    },
    'E_Thesis_Durham_University_Self_Transfor Oneill': {
        'title': 'Self-transformation in the Hypnerotomachia Poliphili',
        'author': "James O'Neill",
        'year': 2025,
        'journal': 'Durham University (E-Thesis)',
        'doc_type': 'DISSERTATION',
    },
    'A_Narrative_in_Search_of_an_Author': {
        'title': 'A Narrative in Search of an Author: The Hypnerotomachia Poliphili',
        'author': "James O'Neill",
        'year': 2025,
        'doc_type': 'SCHOLARSHIP',
    },
    'Francesco Colonna Hypnerotomachia Poliphili Da Capo': {
        'title': 'Hypnerotomachia Poliphili (Da Capo Press edition)',
        'author': 'Francesco Colonna',
        'year': 1499,
        'doc_type': 'PRIMARY_TEXT',
    },
    'Francesco Colonna Rino Avesani': {
        'title': 'Hypnerotomachia Poliphili, Vol. 1 (Antenore critical edition)',
        'author': 'Francesco Colonna (ed. Pozzi & Ciapponi)',
        'year': 1964,
        'doc_type': 'PRIMARY_TEXT',
    },
    'Hypnerotomachia by Francesco Colonna': {
        'title': 'Hypnerotomachia Poliphili',
        'author': 'Francesco Colonna',
        'year': 1499,
        'doc_type': 'PRIMARY_TEXT',
    },
    'The HP of Ben Jonson': {
        'title': 'The HP of Ben Jonson and Kenelm Digby',
        'author': 'Unknown',
        'year': 2025,
        'doc_type': 'PRESENTATION',
    },
    'Crossing_the_text_image_boundary': {
        'title': 'Crossing the Text-Image Boundary: The French HP',
        'author': 'Unknown',
        'doc_type': 'SCHOLARSHIP',
    },
    'Dream_Narratives_and_Initiation_Processe': {
        'title': 'Dream Narratives and Initiation Processes',
        'author': 'Unknown',
        'doc_type': 'SCHOLARSHIP',
    },
    'Editions SR 25 James Gollnick': {
        'title': 'Religious Dreamworld of Apuleius Metamorphoses: Recovering a Forgotten Hermeneutic',
        'author': 'James Gollnick',
        'doc_type': 'SCHOLARSHIP',
    },
    'Elucidating_and_Enigmatizing_the_Recepti': {
        'title': 'Elucidating and Enigmatizing the Reception of the HP',
        'author': 'Unknown',
        'doc_type': 'SCHOLARSHIP',
    },
    'Eugenio Canone_ Leen Spruit': {
        'title': 'Emblematics in the Early Modern Age: Case Studies',
        'author': 'Eugenio Canone and Leen Spruit',
        'doc_type': 'SCHOLARSHIP',
    },
    'Georg Leidinger Albrecht D': {
        'title': 'Albrecht Durer und die Hypnerotomachia Poliphili',
        'author': 'Georg Leidinger',
        'doc_type': 'SCHOLARSHIP',
    },
    'Italica 1947': {
        'title': 'Some Foreign Imitators of the Hypnerotomachia Poliphili',
        'author': 'Mario Praz',
        'year': 1947,
        'journal': 'Italica 24:1',
        'doc_type': 'SCHOLARSHIP',
    },
    'Journal of the Warburg Institute 1937': {
        'title': 'The Hypnerotomachia Poliphili in 17th Century France',
        'author': 'Anthony Blunt',
        'year': 1937,
        'journal': 'Journal of the Warburg Institute 1:2',
        'doc_type': 'SCHOLARSHIP',
    },
    'Journal of the Warburg and Courtauld Institutes vol 47': {
        'title': 'Alberti and the Hypnerotomachia Poliphili',
        'author': 'D. R. Edward Wright',
        'year': 1984,
        'journal': 'Journal of the Warburg and Courtauld Institutes 47',
        'doc_type': 'SCHOLARSHIP',
    },
    'Liane Lefaivre': {
        'title': "Leon Battista Alberti's Hypnerotomachia Poliphili: Re-Cognizing the Architectural Body",
        'author': 'Liane Lefaivre',
        'year': 1997,
        'doc_type': 'SCHOLARSHIP',
    },
    'Notes and Queries 1952': {
        'title': 'Some Notes on the Vocabulary of the Hypnerotomachia Poliphili',
        'author': 'Peter Ure',
        'year': 1952,
        'journal': 'Notes and Queries 197:26',
        'doc_type': 'SCHOLARSHIP',
    },
    'Renaissance Quarterly vol 55': {
        'title': 'The Hypnerotomachia Poliphili, Image, Text, and Vernacular Poetics',
        'author': 'Rosemary Trippe',
        'year': 2002,
        'journal': 'Renaissance Quarterly 55:4',
        'doc_type': 'SCHOLARSHIP',
    },
    'Renaissance Studies 1990': {
        'title': 'The Structural Problematic of the Hypnerotomachia Poliphili',
        'author': 'Mark Jarzombek',
        'year': 1990,
        'journal': 'Renaissance Studies 4:3',
        'doc_type': 'SCHOLARSHIP',
    },
    'Studies in Philology 2006': {
        'title': "Robert Dallington's Hypnerotomachia and the Protestant Antiquity of Elizabethan England",
        'author': 'L. E. Semler',
        'year': 2006,
        'journal': 'Studies in Philology 103:2',
        'doc_type': 'SCHOLARSHIP',
    },
    'Teaching_Eros': {
        'title': 'Teaching Eros: The Rhetoric of Love in the Hypnerotomachia Poliphili',
        'author': 'Unknown',
        'doc_type': 'SCHOLARSHIP',
    },
    'The Modern Language Review 1955': {
        'title': 'Francesco Colonna and Rabelais',
        'author': 'Marcel Francon',
        'year': 1955,
        'journal': 'The Modern Language Review 50:1',
        'doc_type': 'SCHOLARSHIP',
    },
    'The_Narrative_Function_of_Hieroglyphs': {
        'title': 'The Narrative Function of Hieroglyphs in the Hypnerotomachia Poliphili',
        'author': 'Unknown',
        'doc_type': 'SCHOLARSHIP',
    },
    'Untangling the knot': {
        'title': "Untangling the Knot: Garden Design in Francesco Colonna's Hypnerotomachia Poliphili",
        'author': 'Unknown',
        'doc_type': 'SCHOLARSHIP',
    },
    'Walking_in_the_Boboli': {
        'title': 'Walking in the Boboli Gardens in Florence',
        'author': 'Unknown',
        'doc_type': 'SCHOLARSHIP',
    },
    'Word Image 1998 jan vol 14 iss 1 2 Bury John': {
        'title': 'Chapter III of the Hypnerotomachia Poliphili and the Antiquarian Culture of the Quattrocento',
        'author': 'John Bury',
        'year': 1998,
        'journal': 'Word & Image 14:1-2',
        'doc_type': 'SCHOLARSHIP',
    },
    'Word Image 1998 jan vol 14 iss 1 2 Curran Brian': {
        'title': 'The Hypnerotomachia Poliphili and Renaissance Egyptology',
        'author': 'Brian A. Curran',
        'year': 1998,
        'journal': 'Word & Image 14:1-2',
        'doc_type': 'SCHOLARSHIP',
    },
    'Word Image 1998 jan vol 14 iss 1 2 Griggs Tamara': {
        'title': "Promoting the Past: The Hypnerotomachia Poliphili as Antiquarian Enterprise",
        'author': 'Tamara Griggs',
        'year': 1998,
        'journal': 'Word & Image 14:1-2',
        'doc_type': 'SCHOLARSHIP',
    },
    'Word Image 1998 jan vol 14 iss 1 2 Hunt John Dixon': {
        'title': 'Experiencing Gardens in the Hypnerotomachia Poliphili',
        'author': 'John Dixon Hunt',
        'year': 1998,
        'journal': 'Word & Image 14:1-2',
        'doc_type': 'SCHOLARSHIP',
    },
    'Word Image 1998 jan vol 14 iss 1 2 Leslie Michael': {
        'title': 'The Hypnerotomachia Poliphili and the Elizabethan Landscape Entertainment',
        'author': 'Michael Leslie',
        'year': 1998,
        'journal': 'Word & Image 14:1-2',
        'doc_type': 'SCHOLARSHIP',
    },
    'Word Image 1998 jan vol 14 iss 1 2 Stewering Roswitha': {
        'title': 'The Relationship between Text and Woodcuts in the Hypnerotomachia Poliphili',
        'author': 'Roswitha Stewering (trans. Lorna Maher)',
        'year': 1998,
        'journal': 'Word & Image 14:1-2',
        'doc_type': 'SCHOLARSHIP',
    },
    'Word Image 1998 jan vol 14 iss 1 2 Temple N': {
        'title': 'The Hypnerotomachia Poliphili as a Possible Model for Garden Design',
        'author': 'N. Temple',
        'year': 1998,
        'journal': 'Word & Image 14:1-2',
        'doc_type': 'SCHOLARSHIP',
    },
    'Word Image 2015 apr 03 vol 31 iss 2 Fabiani Giannetto': {
        'title': "Not Before Either: The Hypnerotomachia Poliphili and the Villa d'Este at Tivoli",
        'author': 'Raffaella Fabiani Giannetto',
        'year': 2015,
        'journal': 'Word & Image 31:2',
        'doc_type': 'SCHOLARSHIP',
    },
    'Word Image 2015 apr 03 vol 31 iss 2 Farrington Lynne': {
        'title': "Though I Could Lead a Quiet Life: The Hypnerotomachia Poliphili in English Translation",
        'author': 'Lynne Farrington',
        'year': 2015,
        'journal': 'Word & Image 31:2',
        'doc_type': 'SCHOLARSHIP',
    },
    'Word Image 2015 apr 03 vol 31 iss 2 Keller William': {
        'title': 'Hypnerotomachia Joins the Party: Reading across Word and Image',
        'author': 'William B. Keller',
        'year': 2015,
        'journal': 'Word & Image 31:2',
        'doc_type': 'SCHOLARSHIP',
    },
    'Word Image 2015 apr 03 vol 31 iss 2 Nygren Christopher': {
        'title': 'The Hypnerotomachia Poliphili and the Woodcut as Mirror',
        'author': 'Christopher J. Nygren',
        'year': 2015,
        'journal': 'Word & Image 31:2',
        'doc_type': 'SCHOLARSHIP',
    },
    'Word Image 2015 apr 03 vol 31 iss 2 Pumroy Eric': {
        'title': "Bryn Mawr College's 1499 Edition of the Hypnerotomachia Poliphili",
        'author': 'Eric L. Pumroy',
        'year': 2015,
        'journal': 'Word & Image 31:2',
        'doc_type': 'SCHOLARSHIP',
    },
}


def find_metadata(filename):
    """Match filename against known metadata."""
    for key, meta in KNOWN_METADATA.items():
        if key in filename:
            return dict(meta)
    return {}


def clean_filename(filename):
    """Create a clean slug from filename for the markdown file."""
    stem = Path(filename).stem
    # Remove common junk
    stem = re.sub(r'-20\d{5}T\d+Z.*', '', stem)
    stem = re.sub(r'\s*\(\d+\)\s*', '', stem)
    # Replace spaces and special chars
    slug = re.sub(r'[^\w]+', '_', stem)
    slug = re.sub(r'_+', '_', slug).strip('_')
    # Truncate
    if len(slug) > 80:
        slug = slug[:80].rstrip('_')
    return slug


def extract_pdf_text(pdf_path):
    """Extract text from PDF, return list of (page_num, text) tuples."""
    doc = fitz.open(str(pdf_path))
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text()
        if text.strip():
            pages.append((i + 1, text))
    doc.close()
    return pages


def pages_to_markdown(pages):
    """Convert extracted pages to a single markdown string."""
    parts = []
    for page_num, text in pages:
        # Clean up common PDF extraction artifacts
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Remove page headers/footers (single short lines at start/end)
        lines = text.split('\n')
        if lines and len(lines[0].strip()) < 10:
            lines = lines[1:]
        text = '\n'.join(lines)
        parts.append(f"<!-- Page {page_num} -->\n\n{text}")
    return '\n\n---\n\n'.join(parts)


def write_markdown(output_path, metadata, content, page_count):
    """Write markdown file with YAML frontmatter."""
    frontmatter_lines = ['---']
    for key in ['title', 'author', 'year', 'journal', 'source', 'doc_type']:
        if key in metadata and metadata[key]:
            val = metadata[key]
            if isinstance(val, str) and ':' in val:
                val = f'"{val}"'
            elif isinstance(val, str):
                val = f'"{val}"'
            frontmatter_lines.append(f'{key}: {val}')
    frontmatter_lines.append(f'page_count: {page_count}')
    frontmatter_lines.append('---')
    frontmatter = '\n'.join(frontmatter_lines)

    title = metadata.get('title', 'Untitled')
    header = f"# {title}\n\n"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"{frontmatter}\n\n{header}{content}")


def main():
    extensions = {'.pdf'}
    pdf_files = sorted([f for f in BASE_DIR.iterdir()
                       if f.suffix.lower() in extensions and f.is_file()])

    print(f"Found {len(pdf_files)} PDFs to convert")

    success = 0
    empty = 0
    errors = 0

    for pdf_path in pdf_files:
        slug = clean_filename(pdf_path.name)
        output_path = MD_DIR / f"{slug}.md"

        try:
            pages = extract_pdf_text(pdf_path)
            if not pages:
                print(f"  EMPTY: {pdf_path.name}")
                empty += 1
                continue

            metadata = find_metadata(pdf_path.name)
            metadata['source'] = pdf_path.name

            content = pages_to_markdown(pages)
            write_markdown(output_path, metadata, content, len(pages))

            word_count = len(content.split())
            print(f"  OK: {slug}.md ({len(pages)} pages, {word_count} words)")
            success += 1

        except Exception as e:
            print(f"  ERROR: {pdf_path.name}: {e}")
            errors += 1

    print(f"\nResults: {success} converted, {empty} empty, {errors} errors")


if __name__ == "__main__":
    main()
```

---

## seed_dictionary

`scripts/seed_dictionary.py`

```python
"""Seed the dictionary_terms table with 35+ core HP terminology entries."""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"

# Category constants
BOOK = "Book History & Bibliography"
TEXT = "Textual & Visual Motifs"
ANNOT = "Annotation Studies"
ALCHEM = "Alchemical Interpretation"
ARCH = "Architecture & Gardens"
DEBATE = "Scholarly Debates"

TERMS = [
    # === Book History & Bibliography ===
    {
        "slug": "signature",
        "label": "Signature",
        "category": BOOK,
        "definition_short": "A letter-number code printed at the foot of certain pages to guide the binder in assembling the book.",
        "definition_long": "In early printed books, signatures are marks (usually a lowercase letter followed by a numeral) placed at the bottom of the first recto of each leaf in a gathering. The 1499 HP uses signatures a-z (omitting j, u, w) then A-G, each gathering consisting of eight leaves. Russell's thesis references folios by signature (e.g., b6v) rather than by page number, since no page numbers were printed in the original.",
        "source_basis": "Standard bibliographic terminology; Russell 2014 passim",
    },
    {
        "slug": "quire",
        "label": "Quire",
        "category": BOOK,
        "definition_short": "A section of a book made from sheets folded together, also called a gathering.",
        "definition_long": "A quire (or gathering) is the basic structural unit of a bound book. In the HP, each quire consists of a single large sheet folded to produce eight leaves (sixteen pages). The quire is identified by its signature letter: quire 'a' contains leaves a1-a8, quire 'b' contains b1-b8, and so on. The collation formula of the 1499 HP describes this structure systematically.",
        "source_basis": "Standard bibliographic terminology",
    },
    {
        "slug": "folio",
        "label": "Folio",
        "category": BOOK,
        "definition_short": "A single leaf of a book, having two sides: recto (front) and verso (back).",
        "definition_long": "In bibliographic usage, 'folio' refers to a leaf rather than a page. Each folio has two sides. In the HP, folio references combine a signature with a side designation: 'b6v' means the verso (back) of the sixth leaf in quire b. The Siena digital facsimile photographs are labeled by folio number with recto/verso suffixes (e.g., O.III.38_0014r.jpg).",
        "source_basis": "Standard bibliographic terminology",
    },
    {
        "slug": "recto",
        "label": "Recto",
        "category": BOOK,
        "definition_short": "The front side of a leaf, conventionally the right-hand page when the book lies open.",
        "definition_long": "Abbreviated 'r' in signature references (e.g., a1r). In the HP's original layout, most woodcuts appear on the recto. The recto is the side that would have been printed first in the press.",
        "source_basis": "Standard bibliographic terminology",
    },
    {
        "slug": "verso",
        "label": "Verso",
        "category": BOOK,
        "definition_short": "The back side of a leaf, conventionally the left-hand page when the book lies open.",
        "definition_long": "Abbreviated 'v' in signature references (e.g., b6v). Some of the most important marginal annotations in the BL copy appear on versos facing significant woodcuts on the following recto.",
        "source_basis": "Standard bibliographic terminology",
    },
    {
        "slug": "gathering",
        "label": "Gathering",
        "category": BOOK,
        "definition_short": "A group of leaves folded together to form a section of a book; synonym for quire.",
        "definition_long": "The HP's gatherings are quaternions (four sheets folded to make eight leaves). The 1499 edition consists of approximately 29 gatherings (a-z then A-G, with some irregular final gatherings). The regularity of this structure is what makes the signature map a reliable concordance tool.",
        "source_basis": "Standard bibliographic terminology; build_signature_map.py",
    },
    {
        "slug": "collation",
        "label": "Collation",
        "category": BOOK,
        "definition_short": "A formula describing the physical structure of a printed book: how many gatherings, how many leaves per gathering.",
        "definition_long": "The collation formula for the 1499 HP is: a-z8 A-F8 G6 (with j, u, w omitted from the lowercase alphabet). This means 26 gatherings of 8 leaves each, plus 7 uppercase gatherings. The formula allows bibliographers to detect missing or inserted leaves. Harris (2002) used collation analysis to identify typographical anomalies in the HP's woodcuts.",
        "source_basis": "Harris 2002; standard bibliographic terminology",
    },
    {
        "slug": "incunabulum",
        "label": "Incunabulum",
        "category": BOOK,
        "definition_short": "A book printed before 1501, during the infancy of European printing.",
        "definition_long": "The 1499 HP is an incunabulum (plural: incunabula), produced in the last year of the fifteenth century. It is catalogued in the Incunabula Short Title Catalogue (ISTC) maintained by the British Library. Russell's world census was conducted primarily through ISTC records. The HP is widely regarded as the most elaborately illustrated incunabulum ever produced.",
        "source_basis": "Russell 2014, p. 16; Painter 1963",
    },
    {
        "slug": "woodcut",
        "label": "Woodcut",
        "category": TEXT,
        "definition_short": "An illustration printed from a carved wooden block, integral to the HP's text-image program.",
        "definition_long": "The 1499 HP contains 172 woodcut illustrations, attributed to an unidentified artist sometimes called the 'Master of the Poliphilo.' The woodcuts are integrated into the text in a manner unprecedented for the period, with images appearing mid-page within the flow of prose. The 1545 edition recast the woodcuts using new blocks. Huelsen (1910) provided the first systematic study of their architectural sources. Priki (2012) analyzed how the text-image relationship shifts across editions.",
        "source_basis": "Huelsen 1910; Priki 2012; Painter 1963",
    },

    # === Annotation Studies ===
    {
        "slug": "marginalia",
        "label": "Marginalia",
        "category": ANNOT,
        "definition_short": "Handwritten notes in the margins of a printed book, recording a reader's responses to the text.",
        "definition_long": "Russell's thesis documents marginalia in six copies of the HP, showing that the book was actively read and annotated by diverse readers including humanists, playwrights, a pope, and alchemists. The marginalia range from simple underlines and source identifications to elaborate alchemical decipherments and cross-references to other works. Russell frames the annotated HP as a 'humanistic activity book' in which readers cultivated their ingegno through playful engagement.",
        "source_basis": "Russell 2014 passim; Sherman 2007",
    },
    {
        "slug": "annotator-hand",
        "label": "Annotator Hand",
        "category": ANNOT,
        "definition_short": "A distinct handwriting identified in a manuscript or printed book, attributed to a specific reader.",
        "definition_long": "Russell identified 11 distinct annotator hands across 6 copies of the HP. Distinguishing hands involves analyzing ink color, language, ductus (letter formation), content focus, and stratigraphic relationships (which hand overwrites which). The BL copy bears two hands: Ben Jonson (Hand A) and an anonymous alchemist (Hand B). The Buffalo copy has five interleaved hands (A-E).",
        "source_basis": "Russell 2014, Ch. 6-9",
    },
    {
        "slug": "acrostic",
        "label": "Acrostic",
        "category": TEXT,
        "definition_short": "A text in which the initial letters of each section spell out a hidden message.",
        "definition_long": "The HP's chapter initials spell POLIAM FRATER FRANCISCVS COLVMNA PERAMAVIT ('Brother Francesco Colonna loved Polia greatly'). This acrostic is the primary evidence for attributing authorship to a Dominican friar named Francesco Colonna. However, the acrostic has been contested: Lefaivre (1997) argued it could have been inserted by someone other than the author, and proposed Leon Battista Alberti as the true author. The acrostic does not resolve which Francesco Colonna is meant, leading to the long-running authorship debate.",
        "source_basis": "Casella & Pozzi 1959; Lefaivre 1997; Russell 2014, p. 8",
    },
    {
        "slug": "hieroglyph",
        "label": "Hieroglyph",
        "category": TEXT,
        "definition_short": "A picture-writing system; in the HP, pseudo-Egyptian symbolic inscriptions that Poliphilo encounters and interprets.",
        "definition_long": "The HP contains numerous pseudo-hieroglyphic inscriptions that Poliphilo deciphers during his journey. These are not authentic Egyptian hieroglyphs but Renaissance inventions inspired by the rediscovery of Horapollo's Hieroglyphica. Curran (1998) situates them within fifteenth-century humanist Egyptology. Priki analyzes their narrative function, arguing they serve as structural devices within the dream journey rather than mere antiquarian decoration. The hieroglyphs influenced the later emblem tradition.",
        "source_basis": "Curran 1998; Priki (undated); Gombrich 1972",
    },
    {
        "slug": "emblem",
        "label": "Emblem",
        "category": TEXT,
        "definition_short": "A combination of image, motto, and explanatory text; a genre that the HP helped to inaugurate.",
        "definition_long": "The emblem tradition, formalized by Andrea Alciato in 1531, combined a motto (inscriptio), an image (pictura), and an explanatory verse (subscriptio). The HP's hieroglyphic woodcuts, which pair symbolic images with interpretive text, are widely considered proto-emblematic. The book's influence on Alciato and subsequent emblem books has been documented by Gombrich and others.",
        "source_basis": "Gombrich 1972; Caruso 2004",
    },
    {
        "slug": "ekphrasis",
        "label": "Ekphrasis",
        "category": TEXT,
        "definition_short": "A vivid verbal description of a visual work of art, used extensively throughout the HP.",
        "definition_long": "Much of the HP consists of elaborate ekphrastic descriptions: Poliphilo encounters buildings, sculptures, fountains, gardens, and processions, each described in painstaking visual detail. These descriptions serve multiple functions: they display the author's antiquarian learning, provide material for the woodcut illustrations, and create the immersive dream-atmosphere. Trippe (2002) argues these ekphrases adapt Petrarchan conventions of lyric poetry into a visual register.",
        "source_basis": "Trippe 2002; Stewering 2000",
    },

    # === Alchemical Interpretation ===
    {
        "slug": "alchemical-allegory",
        "label": "Alchemical Allegory",
        "category": ALCHEM,
        "definition_short": "The interpretation of the HP as encoding alchemical processes beneath its love narrative.",
        "definition_long": "Two annotators in Russell's study -- Hand B in the BL copy and Hand E in the Buffalo copy -- independently read the HP as concealing alchemical formulae. This interpretive tradition dates to Beroalde de Verville's 1600 French edition, which included a 'tableau steganographique' listing alchemical equivalents for the narrative's symbols. The two alchemists followed different schools: the BL annotator applied d'Espagnet's mercury-centered framework, while the Buffalo annotator followed pseudo-Geber's sulphur/Sol-Luna emphasis.",
        "source_basis": "Russell 2014, Ch. 6-7; Perifano 2004",
    },
    {
        "slug": "master-mercury",
        "label": "Master Mercury",
        "category": ALCHEM,
        "definition_short": "The central alchemical principle identified by the BL copy's anonymous annotator (Hand B).",
        "definition_long": "The BL alchemist wrote on the flyleaf verso: 'verus sensus intentionis huius libri est 3um: Geni et Totius Naturae energiae & operationum Magisteri Mercurii Descriptio elegans, ampla' -- the HP's true sense is the 'full and elegant description of the energy and spirit of the whole nature, and of the operations of Master Mercury.' This reading positions mercury (quicksilver) as the catalytic principle uniting all elements, consistent with d'Espagnet's Enchiridion Physicae Restitutae and with Isaac Newton's corpuscularian alchemy.",
        "source_basis": "Russell 2014, pp. 159-160",
    },
    {
        "slug": "sol-luna",
        "label": "Sol and Luna",
        "category": ALCHEM,
        "definition_short": "The Sun (gold, masculine) and Moon (silver, feminine) as alchemical principles of opposition and unity.",
        "definition_long": "In the pseudo-Geberian tradition followed by the Buffalo annotator (Hand E), Sol and Luna represent the masculine and feminine principles whose union produces the philosopher's stone. Hand E identified the king and queen statues in the HP as Sol and Luna, and read the chess match on h1r as an allegory of silver/gold transmutation. The chemical wedding -- the union of Sol and Luna -- maps onto Poliphilo and Polia's love story.",
        "source_basis": "Russell 2014, pp. 187-190; Newman 1991",
    },
    {
        "slug": "chemical-wedding",
        "label": "Chemical Wedding",
        "category": ALCHEM,
        "definition_short": "The alchemical union of two opposing substances, symbolized as a marriage producing a hermaphrodite.",
        "definition_long": "The alchemical concept of the chemical wedding (chymische Hochzeit) posits that the refinement of base matter requires the union of opposing principles. In the HP, the love between Poliphilo and Polia was read by alchemically-inclined readers as encoding this process. The offspring of the chemical wedding is the hermaphrodite, harmonizing male and female elements. Russell documents how the Buffalo annotator identified such hermaphroditic imagery on h1r.",
        "source_basis": "Russell 2014, pp. 189-190",
    },
    {
        "slug": "prisca-sapientia",
        "label": "Prisca Sapientia",
        "category": ALCHEM,
        "definition_short": "The concept of an 'ancient wisdom' transmitted from Hermes Trismegistus through successive sages, which alchemists sought to recover.",
        "definition_long": "Prisca sapientia held that original knowledge was progressively hidden under layers of allegory and obscurity. The more incomprehensible a text, the more ancient wisdom it was thought to contain. The HP's deliberately obscure language and its prefatory claim that only the most learned could penetrate its meaning made it an ideal vehicle for alchemical interpretation. Newton, Boyle, and d'Espagnet all worked within this paradigm.",
        "source_basis": "Russell 2014, pp. 153-156; Muslow & Hamalainen 2004",
    },

    # === Architecture & Gardens ===
    {
        "slug": "architectural-body",
        "label": "Architectural Body",
        "category": ARCH,
        "definition_short": "Lefaivre's concept that the HP treats architecture as an extension of embodied cognition and corporeal experience.",
        "definition_long": "In her 1997 attribution study, Liane Lefaivre argued that the HP presents architecture not as abstract geometrical form but as an expression of the body's engagement with space. This 'architectural body' concept connects the HP to Alberti's theories of design as dreamwork and to phenomenological approaches in architectural theory. Hunt (1998) extended this by arguing that the HP foregrounds the process of experiencing gardens over the description of finished architectural objects.",
        "source_basis": "Lefaivre 1997; Hunt 1998",
    },
    {
        "slug": "dream-narrative",
        "label": "Dream Narrative",
        "category": DEBATE,
        "definition_short": "A literary work framed as a dream, a genre to which the HP belongs alongside the Roman de la Rose.",
        "definition_long": "The HP is structured as a dream within a dream: Poliphilo falls asleep and enters a vision, within which he falls asleep again and enters a deeper dream (the dream-within-a-dream beginning at a6v). Priki (2016) places the HP in a comparative tradition with the Roman de la Rose and the Byzantine Tale of Livistros and Rodamne, arguing that the dream frame enables pedagogical encounters that prepare the lover for union with the beloved. Gollnick (1999) provides a theoretical framework for dream-narrative hermeneutics through his study of Apuleius.",
        "source_basis": "Priki 2016; Gollnick 1999; Agamben 1984",
    },
    {
        "slug": "inventio",
        "label": "Inventio",
        "category": ANNOT,
        "definition_short": "The rhetorical process of finding or discovering material for creative production; the act of gathering ideas.",
        "definition_long": "In classical rhetoric, inventio is the first of five canons: the discovery of arguments and material. Russell argues that early modern readers used the HP as a source for inventio -- gathering visual, architectural, linguistic, and philosophical material for their own creative projects. Ben Jonson mined it for stage design ideas. Benedetto Giovio extracted botanical and natural-historical content. The alchemists sought hidden formulae. All were practicing inventio through annotation.",
        "source_basis": "Russell 2014, pp. 38-42; Sloane 1989",
    },
    {
        "slug": "ingegno",
        "label": "Ingegno",
        "category": ANNOT,
        "definition_short": "Wit, mental agility, and improvisational intelligence -- a faculty that HP readers cultivated through annotation.",
        "definition_long": "Ingegno (or ingenium) in Renaissance usage encompassed wit, invention, and the ability to perceive unexpected connections. Russell proposes that the act of annotating the HP was itself a form of ingegno cultivation: readers sharpened their perceptiveness by decoding the text's obscurities, tracing its sources, and making creative associations. The BL alchemist twice praised the HP as 'ingeniosissimo,' recognizing it as exemplifying this virtue.",
        "source_basis": "Russell 2014, pp. 40-41, 160",
    },
    {
        "slug": "antiquarianism",
        "label": "Antiquarianism",
        "category": DEBATE,
        "definition_short": "The systematic study and collection of artifacts from the ancient past, a practice central to the HP's intellectual world.",
        "definition_long": "Griggs (1998) argues that the HP should be understood as the culmination of fifteenth-century Italian antiquarianism rather than as Romantic escapism. The book's verbal and visual strategies derive from Cyriacus of Ancona's commentaria and mid-century antiquarian syllogae (topographically organized manuscript collections of inscriptions and monuments). Poliphilo's journey through architectural ruins enacts the antiquarian mode of knowledge-making.",
        "source_basis": "Griggs 1998; Curran 1998",
    },
    {
        "slug": "vernacular-poetics",
        "label": "Vernacular Poetics",
        "category": DEBATE,
        "definition_short": "The HP as a work of Italian vernacular literature, adapting Petrarchan conventions into a prose-image hybrid.",
        "definition_long": "Trippe (2002) argues that the HP has been understudied as literature, with scholars treating it primarily as architectural or philosophical. Through close analysis of woodcuts and their accompanying text, she demonstrates how the author adapted Petrarchan tropes -- the beloved's beauty, the lover's suffering -- into an interplay of word and image. The HP's invented language operates within recognizable Italian vernacular poetic frameworks rather than being merely eccentric.",
        "source_basis": "Trippe 2002",
    },
    {
        "slug": "reception-history",
        "label": "Reception History",
        "category": DEBATE,
        "definition_short": "The study of how the HP was read, interpreted, and repurposed across five centuries and multiple cultures.",
        "definition_long": "The HP's reception spans Venetian humanism, French court culture, Elizabethan theatre, Enlightenment bibliography, Romantic aestheticism, Jungian psychology, and contemporary digital humanities. Priki (2009) surveys two peak periods of engagement: early modern (through c.1657) and the twentieth-century scholarly revival. Blunt (1937) documented French seventeenth-century reception. Praz (1947) traced influence on Swinburne and Beardsley. Semler (2006) reframed the 1592 English translation as deliberate cultural appropriation rather than failed translation.",
        "source_basis": "Priki 2009; Blunt 1937; Praz 1947; Semler 2006",
    },
    {
        "slug": "apparatus",
        "label": "Apparatus",
        "category": BOOK,
        "definition_short": "The scholarly infrastructure surrounding a critical edition: introduction, notes, bibliography, indexes.",
        "definition_long": "The HP has been the subject of two major critical editions: Pozzi & Ciapponi (1964) and Ariani & Gabriele (1998, Adelphi). Godwin's 1999 English translation (Thames & Hudson) provides the most accessible modern apparatus. The term 'apparatus criticus' refers specifically to the textual notes recording variant readings across copies and editions.",
        "source_basis": "Pozzi & Ciapponi 1964; Ariani & Gabriele 1998; Godwin 1999",
    },
    {
        "slug": "commentary",
        "label": "Commentary",
        "category": ANNOT,
        "definition_short": "A systematic explanation of a text, either printed alongside it or written in its margins.",
        "definition_long": "The HP lacks a printed commentary in either of its Aldine editions (1499, 1545). Instead, the commentary tradition is supplied by readers' marginalia. Russell shows that annotations by Giovio, Jonson, the alchemists, and Alexander VII collectively constitute an informal commentary tradition. Beroalde de Verville's 1600 edition adds the first published interpretive apparatus, though framed as an alchemical key rather than a philological commentary.",
        "source_basis": "Russell 2014 passim",
    },
    {
        "slug": "activity-book",
        "label": "Activity Book",
        "category": ANNOT,
        "definition_short": "Russell's concept of the HP as a text designed to provoke active, playful reader engagement.",
        "definition_long": "Drawing on analogy with modern educational media, Russell reframes the HP as a 'humanistic activity book' in which readers cultivated ingegno through creative engagement with the text and its woodcuts. The HP's puzzles, obscure language, embedded inscriptions, and visual-textual interplay invited readers to decode, annotate, cross-reference, and extend the text in their own marginalia. This concept shifts attention from the author's intent to the reader's creative practice.",
        "source_basis": "Russell 2014, pp. 34-42",
    },
    {
        "slug": "elephant-obelisk",
        "label": "Elephant and Obelisk",
        "category": ARCH,
        "definition_short": "A monumental image in the HP showing an elephant bearing an obelisk, later realized by Bernini in Rome.",
        "definition_long": "The woodcut of the elephant bearing an obelisk (b6v-b7r) is one of the HP's most influential images. Heckscher (1947) documented how Bernini drew upon it for his 1667 sculpture in the Piazza della Minerva, commissioned by Alexander VII (who annotated his own copy of the HP). The BL alchemist (Hand B) covered this image with alchemical ideograms, reading it as encoding alchemical processes. The Buffalo annotator (Hand E) identified the surrounding statues with Geberian Sol/Luna symbolism.",
        "source_basis": "Heckscher 1947; Russell 2014, pp. 157, 187",
    },
    {
        "slug": "cythera",
        "label": "Cythera",
        "category": ARCH,
        "definition_short": "The island of Venus, described in the HP with elaborate concentric garden designs.",
        "definition_long": "In the HP, Poliphilo travels to the island of Cythera, sacred to Venus, where he encounters an elaborate circular garden with concentric rings of planting. Segre (1998) provides the first critical analysis of Cythera's garden design, tracing its mythological associations and arguing it anticipates sixteenth-century botanical garden layouts. Fabiani Giannetto (2015) connects Cythera to the Sacro Bosco at Bomarzo through the lens of meraviglia (wonderment).",
        "source_basis": "Segre 1998; Fabiani Giannetto 2015",
    },
    {
        "slug": "aldus-manutius",
        "label": "Aldus Manutius",
        "category": BOOK,
        "definition_short": "The Venetian printer who published the HP in 1499, renowned for Greek scholarship and italic type.",
        "definition_long": "Aldus Manutius (c.1449-1515) published the HP as one of his most ambitious productions, at a time when his press was primarily known for Greek texts. The HP stands apart from his other publications in its elaborate illustration program and vernacular language. Farrington (2015) contextualizes the HP within Aldus's career and his partnership with Andrea Torresani. Davies (1999) provides the standard biography of Aldus as printer and publisher.",
        "source_basis": "Farrington 2015; Davies 1999",
    },
    {
        "slug": "authorship-debate",
        "label": "Authorship Debate",
        "category": DEBATE,
        "definition_short": "The centuries-long dispute over who wrote the HP, with candidates including two Francesco Colonnas, Alberti, and Feliciano.",
        "definition_long": "The acrostic points to 'Frater Franciscus Colonna,' but which one? Casella & Pozzi (1959) established the Venetian Dominican Francesco Colonna (d.1527) as the canonical attribution. Calvesi (1996) argued for a Roman nobleman of the same name. Lefaivre (1997) proposed Leon Battista Alberti. Khomentovskaia (1935) suggested Felice Feliciano. O'Neill (2021) surveys all candidates and proposes that future research should use narratological analysis rather than archival evidence alone.",
        "source_basis": "Casella & Pozzi 1959; Calvesi 1996; Lefaivre 1997; O'Neill 2021",
    },
    {
        "slug": "ideogram",
        "label": "Ideogram (Alchemical)",
        "category": ALCHEM,
        "definition_short": "A symbolic sign representing an alchemical element or process, used by annotators to label HP passages.",
        "definition_long": "The BL alchemist (Hand B) used an extensive vocabulary of alchemical ideograms -- compact symbols for gold, silver, mercury, Venus, Jupiter, and other elements -- within the syntax of Latin annotations. These signs often had Latin inflections appended (e.g., the sun symbol + '-ra' for 'aurata'). Russell notes that B's ideographic vocabulary shows consistency with Newton's Keynes MSS, suggesting a possible connection to the Royal Society or Cambridge circle.",
        "source_basis": "Russell 2014, pp. 156-158; Taylor 1951",
    },
    {
        "slug": "acutezze",
        "label": "Acutezze",
        "category": ANNOT,
        "definition_short": "Examples of verbal wit or sharp conceits; the primary interest of Pope Alexander VII's annotations.",
        "definition_long": "Fabio Chigi (Pope Alexander VII) annotated his copy of the HP with particular attention to acutezze -- instances of verbal cleverness, wordplay, and rhetorical ingenuity. This practice reflects the seventeenth-century Italian tradition of collecting examples of wit, codified in works like Tesauro's Il cannocchiale aristotelico (1663) and Pellegrini's Delle Acutezze (1639). Chigi's reading of the HP was aesthetic rather than alchemical or encyclopedic.",
        "source_basis": "Russell 2014, Ch. 8; Pellegrini 1639; Tesauro 1663",
    },
    {
        "slug": "allegory",
        "label": "Allegory",
        "category": TEXT,
        "definition_short": "A narrative in which characters and events represent abstract ideas or principles beneath the surface meaning.",
        "definition_long": "The HP has been read allegorically in multiple registers: as an allegory of love (the surface narrative), of alchemical transformation (Beroalde, the BL and Buffalo annotators), of humanist self-cultivation (Lefaivre), and of architectural and political dreams (Temple 1998). The multiplicity of allegorical readings reflects the HP's deliberate obscurity. Priki (2009) shows how each historical audience imposed its own allegorical framework based on cultural context.",
        "source_basis": "Priki 2009; Russell 2014 passim",
    },
]

# Related term links (slug pairs + type)
LINKS = [
    ("signature", "quire", "RELATED"),
    ("signature", "folio", "RELATED"),
    ("signature", "collation", "RELATED"),
    ("folio", "recto", "RELATED"),
    ("folio", "verso", "RELATED"),
    ("recto", "verso", "RELATED"),
    ("quire", "gathering", "RELATED"),
    ("gathering", "collation", "RELATED"),
    ("incunabulum", "aldus-manutius", "RELATED"),
    ("incunabulum", "woodcut", "RELATED"),
    ("woodcut", "ekphrasis", "RELATED"),
    ("woodcut", "emblem", "RELATED"),
    ("hieroglyph", "emblem", "RELATED"),
    ("hieroglyph", "ideogram", "SEE_ALSO"),
    ("marginalia", "annotator-hand", "RELATED"),
    ("marginalia", "commentary", "RELATED"),
    ("marginalia", "activity-book", "RELATED"),
    ("annotator-hand", "inventio", "RELATED"),
    ("annotator-hand", "ingegno", "RELATED"),
    ("acrostic", "authorship-debate", "RELATED"),
    ("alchemical-allegory", "master-mercury", "RELATED"),
    ("alchemical-allegory", "sol-luna", "RELATED"),
    ("alchemical-allegory", "chemical-wedding", "RELATED"),
    ("alchemical-allegory", "prisca-sapientia", "RELATED"),
    ("master-mercury", "ideogram", "RELATED"),
    ("sol-luna", "chemical-wedding", "RELATED"),
    ("prisca-sapientia", "alchemical-allegory", "RELATED"),
    ("architectural-body", "dream-narrative", "RELATED"),
    ("architectural-body", "ekphrasis", "SEE_ALSO"),
    ("dream-narrative", "allegory", "RELATED"),
    ("inventio", "ingegno", "RELATED"),
    ("inventio", "activity-book", "RELATED"),
    ("antiquarianism", "hieroglyph", "RELATED"),
    ("vernacular-poetics", "ekphrasis", "RELATED"),
    ("reception-history", "authorship-debate", "RELATED"),
    ("elephant-obelisk", "alchemical-allegory", "RELATED"),
    ("elephant-obelisk", "aldus-manutius", "SEE_ALSO"),
    ("cythera", "architectural-body", "RELATED"),
    ("acutezze", "ingegno", "RELATED"),
    ("allegory", "alchemical-allegory", "PARENT"),
    ("apparatus", "commentary", "RELATED"),
    ("aldus-manutius", "incunabulum", "RELATED"),
    ("authorship-debate", "acrostic", "RELATED"),
]


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("Seeding dictionary terms...")
    inserted = 0
    for t in TERMS:
        cur.execute("""
            INSERT OR IGNORE INTO dictionary_terms
                (slug, label, category, definition_short, definition_long,
                 source_basis, review_status, needs_review)
            VALUES (?, ?, ?, ?, ?, ?, 'DRAFT', 1)
        """, (t["slug"], t["label"], t["category"],
              t["definition_short"], t["definition_long"],
              t.get("source_basis", "")))
        inserted += cur.rowcount
    conn.commit()
    print(f"  Inserted {inserted} terms ({len(TERMS)} total defined)")

    print("Creating term links...")
    linked = 0
    for slug_a, slug_b, link_type in LINKS:
        cur.execute("SELECT id FROM dictionary_terms WHERE slug=?", (slug_a,))
        a = cur.fetchone()
        cur.execute("SELECT id FROM dictionary_terms WHERE slug=?", (slug_b,))
        b = cur.fetchone()
        if a and b:
            cur.execute("""
                INSERT OR IGNORE INTO dictionary_term_links
                    (term_id, linked_term_id, link_type)
                VALUES (?, ?, ?)
            """, (a[0], b[0], link_type))
            linked += cur.rowcount
            # Bidirectional for RELATED
            if link_type == "RELATED":
                cur.execute("""
                    INSERT OR IGNORE INTO dictionary_term_links
                        (term_id, linked_term_id, link_type)
                    VALUES (?, ?, ?)
                """, (b[0], a[0], link_type))
                linked += cur.rowcount
    conn.commit()
    print(f"  Created {linked} links")

    # Summary
    print("\nDictionary by category:")
    cur.execute("""
        SELECT category, COUNT(*) FROM dictionary_terms
        GROUP BY category ORDER BY COUNT(*) DESC
    """)
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
```

---

## validate

`scripts/validate.py`

```python
"""Validation and QA: check data integrity, flag issues, produce audit report."""

import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"
SITE_DIR = BASE_DIR / "site"


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    issues = []
    warnings = []
    stats = {}

    print("=== Validation & QA ===\n")

    # 1. Duplicate slugs in dictionary
    print("1. Checking for duplicate dictionary slugs...")
    cur.execute("""
        SELECT slug, COUNT(*) FROM dictionary_terms
        GROUP BY slug HAVING COUNT(*) > 1
    """)
    dupes = cur.fetchall()
    if dupes:
        for d in dupes:
            issues.append(f"DUPLICATE SLUG: dictionary term '{d[0]}' appears {d[1]} times")
    else:
        print("   OK - no duplicates")

    # 2. Terms without category
    print("2. Checking terms without category...")
    cur.execute("SELECT slug FROM dictionary_terms WHERE category IS NULL OR category = ''")
    no_cat = cur.fetchall()
    if no_cat:
        for t in no_cat:
            issues.append(f"MISSING CATEGORY: term '{t[0]}' has no category")
    else:
        print("   OK - all terms have categories")

    # 3. Scholar pages with no works
    print("3. Checking scholars with no works...")
    cur.execute("""
        SELECT s.name FROM scholars s
        LEFT JOIN scholar_works sw ON s.id = sw.scholar_id
        WHERE sw.scholar_id IS NULL
    """)
    no_works = cur.fetchall()
    stats['scholars_no_works'] = len(no_works)
    if no_works:
        for s in no_works:
            warnings.append(f"SCHOLAR NO WORKS: '{s[0]}' has no linked bibliography entries")
    print(f"   {len(no_works)} scholars without linked works (warning, not error)")

    # 4. Folio refs that don't resolve to images
    print("4. Checking unresolved folio references...")
    cur.execute("""
        SELECT r.id, r.signature_ref, r.thesis_page
        FROM dissertation_refs r
        LEFT JOIN matches m ON m.ref_id = r.id
        WHERE m.id IS NULL
    """)
    unmatched = cur.fetchall()
    stats['unmatched_refs'] = len(unmatched)
    if unmatched:
        warnings.append(f"UNMATCHED REFS: {len(unmatched)} dissertation references have no image match")
    print(f"   {len(unmatched)} unmatched references")

    # 5. Missing linked records in dictionary_term_links
    print("5. Checking dictionary link integrity...")
    cur.execute("""
        SELECT l.id, l.term_id, l.linked_term_id
        FROM dictionary_term_links l
        LEFT JOIN dictionary_terms t1 ON l.term_id = t1.id
        LEFT JOIN dictionary_terms t2 ON l.linked_term_id = t2.id
        WHERE t1.id IS NULL OR t2.id IS NULL
    """)
    broken_links = cur.fetchall()
    if broken_links:
        issues.append(f"BROKEN LINKS: {len(broken_links)} dictionary links point to missing terms")
    else:
        print("   OK - all links resolve")

    # 6. BL confidence check
    print("6. Verifying BL confidence downgrade...")
    cur.execute("""
        SELECT mat.confidence, COUNT(*)
        FROM matches mat
        JOIN images i ON mat.image_id = i.id
        JOIN manuscripts m ON i.manuscript_id = m.id
        WHERE m.shelfmark = 'C.60.o.12'
        GROUP BY mat.confidence
    """)
    bl_conf = cur.fetchall()
    for conf, count in bl_conf:
        if conf in ('HIGH', 'MEDIUM'):
            issues.append(f"BL CONFIDENCE: {count} BL matches still at {conf} (should be LOW)")
        else:
            print(f"   BL matches: {count} at {conf}")

    # 7. Review status summary
    print("7. Review status audit...")
    review_tables = [
        ('bibliography', 'needs_review'),
        ('scholars', 'needs_review'),
        ('dictionary_terms', 'needs_review'),
        ('matches', 'needs_review'),
    ]
    for table, col in review_tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table} WHERE {col} = 1")
            needs = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            total = cur.fetchone()[0]
            pct = (needs * 100 // total) if total > 0 else 0
            stats[f'{table}_needs_review'] = needs
            print(f"   {table}: {needs}/{total} need review ({pct}%)")
        except:
            pass

    # 8. Site file counts
    print("8. Checking generated site files...")
    site_counts = {
        'scholar pages': len(list((SITE_DIR / 'scholar').glob('*.html'))) if (SITE_DIR / 'scholar').exists() else 0,
        'dictionary pages': len(list((SITE_DIR / 'dictionary').glob('*.html'))) if (SITE_DIR / 'dictionary').exists() else 0,
        'marginalia pages': len(list((SITE_DIR / 'marginalia').glob('*.html'))) if (SITE_DIR / 'marginalia').exists() else 0,
    }
    for label, count in site_counts.items():
        print(f"   {label}: {count}")
        stats[label] = count

    # 9. Check for empty HTML files
    print("9. Checking for empty HTML files...")
    empty_count = 0
    for html in SITE_DIR.rglob('*.html'):
        if html.stat().st_size < 100:
            issues.append(f"EMPTY FILE: {html.relative_to(BASE_DIR)}")
            empty_count += 1
    if empty_count == 0:
        print("   OK - no empty files")

    # 10. Data.json integrity
    print("10. Checking data.json...")
    import json
    data_path = SITE_DIR / 'data.json'
    if data_path.exists():
        with open(data_path, encoding='utf-8') as f:
            data = json.load(f)
        n_entries = len(data.get('entries', []))
        n_low = sum(1 for e in data['entries'] if e.get('confidence') == 'LOW')
        print(f"   {n_entries} entries, {n_low} LOW confidence")
        stats['data_json_entries'] = n_entries
        if 'provenance' not in data:
            warnings.append("DATA.JSON: missing provenance field")
    else:
        issues.append("DATA.JSON: file not found")

    # === Produce Report ===
    print("\n" + "=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)

    if issues:
        print(f"\n  ISSUES ({len(issues)}):")
        for i in issues:
            print(f"    [!] {i}")
    else:
        print("\n  No critical issues found.")

    if warnings:
        print(f"\n  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"    [?] {w}")

    # Write audit report
    report_path = BASE_DIR / "AUDIT_REPORT.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# Audit Report\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")

        f.write("## What Changed (V2 Migration)\n\n")
        f.write("### Schema\n")
        f.write("- Added `annotations` table for first-class marginal note records\n")
        f.write("- Added `annotators` table (normalized from `annotator_hands`)\n")
        f.write("- Added `doc_folio_refs` table (generalized from `dissertation_refs`)\n")
        f.write("- Added `dictionary_terms` and `dictionary_term_links` tables\n")
        f.write("- Added `document_topics` junction table for multi-value topic clusters\n")
        f.write("- Added `review_status`, `needs_review`, `reviewed`, `source_method`, ")
        f.write("`confidence`, and `notes` columns across existing tables\n")
        f.write("- Downgraded all BL C.60.o.12 matches from MEDIUM to LOW confidence\n\n")

        f.write("### Site\n")
        f.write(f"- {site_counts.get('scholar pages', 0)} scholar profile pages (DB-driven, with review badges)\n")
        f.write(f"- {site_counts.get('dictionary pages', 0)} dictionary term pages (37 terms, 6 categories, 76 links)\n")
        f.write(f"- {site_counts.get('marginalia pages', 0)} marginalia folio detail pages (with annotator hand info)\n")
        f.write("- Site-wide navigation bar (Home, Marginalia, Scholars, Dictionary, About)\n")
        f.write("- About page with database statistics and rebuild instructions\n")
        f.write("- Confidence badges (HIGH/MEDIUM/LOW/PROVISIONAL) on all matches\n")
        f.write("- Review badges (Unreviewed) on LLM-assisted content\n\n")

        f.write("## What Remains Provisional\n\n")
        f.write("| Data Category | Total | Needs Review | Source Method |\n")
        f.write("|---|---|---|---|\n")
        f.write(f"| Bibliography entries | 88 | {stats.get('bibliography_needs_review', '?')} | LLM-assisted |\n")
        f.write(f"| Scholar profiles | 52 | {stats.get('scholars_needs_review', '?')} | LLM-assisted |\n")
        f.write(f"| Dictionary terms | 37 | {stats.get('dictionary_terms_needs_review', '?')} | LLM-assisted |\n")
        f.write(f"| Image matches | 610 | {stats.get('matches_needs_review', '?')} | Algorithmic (folio mapping) |\n")
        f.write(f"| BL matches specifically | 218 | 218 | LOW confidence (1545 edition offset) |\n\n")

        f.write("## What Still Needs Human Review\n\n")
        f.write("### Critical\n")
        f.write("1. **BL C.60.o.12 photo-to-folio mapping**: Verify that sequential photo numbers\n")
        f.write("   correspond to folio numbers. The BL copy is the 1545 edition; layout may differ\n")
        f.write("   from the 1499 signature map by a few leaves.\n")
        f.write("2. **Article summaries**: All 34 summaries were generated by Claude and have not\n")
        f.write("   been checked for factual accuracy, misattribution, or hallucination.\n")
        f.write("3. **Hand attributions**: Derived from reading Russell's prose in conversation.\n")
        f.write("   The signature-to-hand mapping rules are approximate.\n\n")

        f.write("### Important\n")
        f.write("4. **Scholar metadata**: Birth/death years, nationalities, and institutional\n")
        f.write("   affiliations should be cross-referenced against VIAF/WorldCat.\n")
        f.write("5. **Dictionary definitions**: Especially the alchemical and architectural terms\n")
        f.write("   should be reviewed by a domain specialist.\n")
        f.write("6. **Mislabeled files**: Jarzombek (De pictura, not HP) and Canone/Spruit\n")
        f.write("   (Poncet on Botticelli, not emblematics) were identified by LLM and\n")
        f.write("   should be confirmed.\n\n")

        f.write("### Nice to Have\n")
        f.write("7. **Timeline event dates**: Some date ranges are approximate.\n")
        f.write("8. **Topic cluster assignments**: Some works could belong to multiple clusters.\n")
        f.write("   The `document_topics` junction table supports this but most entries\n")
        f.write("   have only one topic assigned.\n\n")

        if issues:
            f.write("## Validation Issues\n\n")
            for i in issues:
                f.write(f"- **{i}**\n")
            f.write("\n")

        if warnings:
            f.write("## Validation Warnings\n\n")
            for w in warnings:
                f.write(f"- {w}\n")
            f.write("\n")

        f.write("## How to Rebuild\n\n")
        f.write("```bash\n")
        f.write("python scripts/migrate_v2.py        # Schema migration (idempotent)\n")
        f.write("python scripts/seed_dictionary.py   # Dictionary terms (idempotent)\n")
        f.write("python scripts/build_site.py        # Generate all HTML + JSON\n")
        f.write("python scripts/validate.py          # Run this audit\n")
        f.write("```\n")

    print(f"\nAudit report written to {report_path}")
    conn.close()


if __name__ == "__main__":
    main()
```

---

