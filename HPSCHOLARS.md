# HP Scholars: Representing the Scholarship of the Hypnerotomachia Poliphili

## The Problem of Scholarly Representation

We have 38 documents about the *Hypnerotomachia Poliphili* sitting in a folder. They span from a 1937 *Journal of the Warburg Institute* article by Anthony Blunt to James Russell's 2024 PhD thesis. They are written in English, Italian, and German. They address architecture, gardens, hieroglyphs, literary reception, emblematics, pedagogy, love rhetoric, dream narrative, and philological method. They cite each other, contradict each other, and occasionally ignore each other entirely.

The question is: how do we make this body of scholarship navigable, queryable, and ultimately presentable on a website — without flattening the intellectual complexity that makes it valuable?

## What We Have: The Documents Table

Our SQLite database currently stores each document with minimal metadata:

| Field | Example |
|-------|---------|
| filename | `Word Image 1998 jan vol 14 iss 1 2 Bury John Chapter III of the Hypnerotomachia.pdf` |
| title | (extracted from filename, imperfect) |
| author | (extracted from filename, imperfect) |
| doc_type | SCHOLARSHIP / PRIMARY_TEXT / DISSERTATION / PRESENTATION |
| file_size_bytes | varies |

This is a starting point, not a destination. The filename-based metadata extraction is rough — it captures author names and journal information when they happen to be encoded in the filename, but misses publication year, volume, DOI, abstract, and subject classification.

## Thinking Through the Scholarly Landscape

### Clustering by Topic

Reading through the filenames and sampling the PDFs, the scholarship clusters into recognizable research threads:

**1. Authorship and Attribution**
The HP's authorship has been debated for five centuries. The acrostic formed by the decorated initials of each chapter spells POLIAM FRATER FRANCISCVS COLVMNA PERAMAVIT ("Brother Francesco Colonna greatly loved Polia"), but which Francesco Colonna? A Dominican friar in Venice? A Roman nobleman? Someone else entirely?
- O'Neill, "A Narrative in Search of an Author"
- Lefaivre, "Leon Battista Alberti's Hypnerotomachia Poliphili: Re-Cognizing the Architectural Body"

**2. Architecture and Gardens**
The HP is one of the most detailed architectural descriptions in Renaissance literature. Scholars have traced its influence on real gardens and buildings.
- Wright, "Alberti and the Hypnerotomachia Poliphili" (Warburg & Courtauld, 1984)
- Hunt, "Experiencing gardens in the Hypnerotomachia" (Word & Image, 1998)
- Temple, "The Hypnerotomachia Poliphili as a possible model for garden design" (Word & Image, 1998)
- Jarzombek, "The structural problematic of the HP" (Renaissance Studies, 1990)
- "Untangling the knot: Garden design in Francesco Colonna's HP"
- "Walking in the Boboli Gardens in Florence"
- Fabiani Giannetto, "Not before either..." (Word & Image, 2015)

**3. Text-Image Relations**
The 172 woodcuts are inseparable from the text. How do they function narratively, symbolically, and materially?
- Bury, "Chapter III of the Hypnerotomachia" (Word & Image, 1998)
- Stewering, "The relationship between..." (Word & Image, 1998)
- Leslie, "The Hypnerotomachia Poliphili and..." (Word & Image, 1998)
- Nygren, "The Hypnerotomachia Poliphili..." (Word & Image, 2015)
- "Crossing the text-image boundary"
- "The Narrative Function of Hieroglyphs"

**4. Literary Reception and Influence**
How was the HP read, imitated, and repurposed in later centuries?
- Praz, "Some Foreign Imitators of the Hypnerotomachia" (Italica, 1947)
- Francon, on Colonna and Rabelais (MLR, 1955)
- Semler, "Robert Dallington's Hypnerotomachia" (Studies in Philology, 2006)
- Trippe, "The Hypnerotomachia Poliphili..." (Renaissance Quarterly, 2002)
- Farrington, "Though I could lead a quiet life..." (Word & Image, 2015)
- Keller, "Hypnerotomachia joins the Party" (Word & Image, 2015)
- "The HP of Ben Jonson and Kenelm Digby" (presentation)

**5. Dream, Religion, and Initiation**
The HP as dream narrative, mystery religion, or initiatory journey.
- Gollnick, "Religious Dreamworld of Apuleius' Metamorphoses"
- "Dream Narratives and Initiation Processes"
- "Teaching Eros: The Rhetoric of Love"
- O'Neill, "Self-transformation in the HP" (Durham thesis)
- "Elucidating and Enigmatizing the Reception"

**6. Material and Bibliographic Study**
The physical book as an object of study — its printing, its copies, its readers' marks.
- **Russell, PhD Thesis** — the central work for our project
- Pumroy, "Bryn Mawr College's 1499 edition" (Word & Image, 2015)
- Curran, "The Hypnerotomachia Poliphili and..." (Word & Image, 1998)
- Griggs, "Promoting the past" (Word & Image, 1998)
- Ure, "Some notes on the vocabulary" (Notes and Queries, 1952)
- Blunt, "The Hypnerotomachia Poliphili..." (Warburg, 1937)
- Canone & Spruit, "Emblematics in the Early Modern Age"

### Clustering by Publication Venue

Two special journal issues dominate the corpus:
- **Word & Image 14:1-2 (1998)**: 7 articles — a dedicated HP issue
- **Word & Image 31:2 (2015)**: 5 articles — another dedicated HP issue

These two issues alone account for 12 of our 32 scholarship PDFs. They represent coordinated scholarly interventions, and the website should present them as such — not as 12 isolated articles but as two curated collections with editorial framing.

## Schema Enhancements for Scholarly Representation

The current `documents` table needs enrichment. Here is my thinking on what to add:

### Enhanced Document Metadata

```sql
ALTER TABLE documents ADD COLUMN journal TEXT;
ALTER TABLE documents ADD COLUMN volume TEXT;
ALTER TABLE documents ADD COLUMN issue TEXT;
ALTER TABLE documents ADD COLUMN pub_year INTEGER;
ALTER TABLE documents ADD COLUMN language TEXT DEFAULT 'en';
ALTER TABLE documents ADD COLUMN abstract TEXT;
ALTER TABLE documents ADD COLUMN topic_cluster TEXT;
ALTER TABLE documents ADD COLUMN doi TEXT;
```

### A Citations Table

Scholarship is a web of references. If Russell cites Blunt, and Blunt cites Colonna, those links are information. A `citations` table would capture:

```sql
CREATE TABLE citations (
    id INTEGER PRIMARY KEY,
    citing_doc_id INTEGER REFERENCES documents(id),
    cited_doc_id INTEGER REFERENCES documents(id),
    citation_context TEXT,  -- the sentence containing the citation
    page_in_citing INTEGER  -- where in the citing work
);
```

This enables "cited by" views on the website and bibliographic network visualization.

### A Folio-to-Document Reference Table

Many scholarly works reference specific folios. A `doc_folio_refs` table would link:

```sql
CREATE TABLE doc_folio_refs (
    id INTEGER PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    signature_ref TEXT,
    page_in_document INTEGER,
    context TEXT
);
```

This would allow the showcase page to say: "This folio (c7v) is discussed by Russell (p. 97), Blunt (p. 154), and Bury (p. 23)."

## How to Process the Scholarship

### Phase A: Metadata Extraction
For each of the 38 documents:
1. Extract text with PyMuPDF (already proven to work on Russell's thesis)
2. Parse the first few pages for title, author, journal, year, abstract
3. Classify into topic clusters using the taxonomy above
4. Store enhanced metadata in the database

This is partially automated, partially manual. Journal articles from Word & Image have standardized metadata in their headers. Monographs and theses are less predictable.

### Phase B: Citation Network
For each document:
1. Extract the bibliography/references section
2. Match cited works against our document inventory
3. Build the citation graph

This is harder. Citation formats vary wildly across five decades of scholarship. A pragmatic approach: extract author-year pairs from bibliographies, fuzzy-match against our documents table, and flag uncertain matches for human review.

### Phase C: Folio Reference Extraction
For each document (not just Russell):
1. Run the same signature-pattern regex used on Russell's thesis
2. Store folio references with page numbers and context

This would reveal which folios are the most discussed across the entire scholarly literature — likely the decorated initials, the major woodcuts, and the hieroglyphic passages.

## Representing Scholars as People

Beyond documents, scholars themselves are entities worth tracking:

| Scholar | Affiliation | Active Period | Key Contribution |
|---------|------------|---------------|-----------------|
| James Russell | (thesis) | 2024 | Systematic marginalia analysis across 6 copies |
| Anthony Blunt | Warburg Institute | 1937 | Early architectural analysis |
| Liane Lefaivre | — | 1997 | Alberti attribution argument |
| John Dixon Hunt | — | 1998 | Garden history perspective |
| Mario Praz | — | 1947 | Early reception history |

A `scholars` table could link to their documents and institutional affiliations, enabling "browse by scholar" on the website. But this is a later enhancement — the documents themselves are the primary interface.

## The Key Insight: Scholarship as Layered Interpretation

The most important thing about representing HP scholarship is recognizing that scholars don't just "study" the HP — they construct interpretive frameworks that guide what subsequent scholars notice. Blunt's 1937 architectural reading shaped fifty years of HP studies. The 1998 Word & Image issue reframed the book as a multimedia object. Russell's 2024 thesis reframed it as a material object bearing traces of its readers.

The website should make these interpretive layers visible. When a user looks at folio c7v, they should be able to see not just the image and Russell's note, but the entire stack of scholarly attention that folio has received, ordered chronologically, revealing how understanding of that page has evolved.

This is what distinguishes a digital humanities project from a digital filing cabinet.
