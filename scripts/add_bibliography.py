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
