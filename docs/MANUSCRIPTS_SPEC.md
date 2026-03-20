# Manuscripts Tab Specification

> This spec defines the data model, content structure, and page design for a new
> Manuscripts tab tracking all known copies of the HP worldwide, with essays on
> annotated copies studied by scholars.

## Goal

Create a manuscripts/copies page that:

1. Lists all known surviving copies of the HP (from Russell's census + ISTC)
2. Distinguishes annotated copies (studied by Russell) from unannotated holdings
3. Provides per-copy essays for the 6 annotated copies Russell studied
4. Links to relevant scholar pages, hand attributions, and marginalia images
5. Shows the geographic distribution of HP copies worldwide

## Data Model

### Existing Table: `manuscripts` (2 rows — only copies with images)

The current table tracks only the two manuscripts with local photographs.
It needs expansion to cover all known copies.

### New Table: `hp_copies`

```sql
CREATE TABLE IF NOT EXISTS hp_copies (
    id INTEGER PRIMARY KEY,
    shelfmark TEXT NOT NULL,
    institution TEXT NOT NULL,
    city TEXT,
    country TEXT,
    edition TEXT DEFAULT '1499',  -- '1499' | '1545' | 'other'
    has_annotations BOOLEAN DEFAULT 0,
    studied_by TEXT,              -- 'Russell 2014' or other scholars
    annotation_summary TEXT,      -- brief description of annotations
    hand_count INTEGER DEFAULT 0,
    copy_notes TEXT,              -- binding, provenance, condition
    has_images_in_project BOOLEAN DEFAULT 0,
    istc_id TEXT,                 -- ISTC catalog identifier
    review_status TEXT DEFAULT 'DRAFT',
    source_method TEXT DEFAULT 'DETERMINISTIC',
    confidence TEXT DEFAULT 'MEDIUM'
);
```

### Data to Populate

**Russell's 6 annotated copies (HIGH confidence):**

| Shelfmark | Institution | City | Edition | Hands | Studied By |
|-----------|-------------|------|---------|-------|------------|
| C.60.o.12 | British Library | London | 1545 | 2 (Jonson, alchemist) | Russell 2014 |
| Buffalo RBR | Buffalo & Erie County Public Library | Buffalo, NY | 1499 | 5 (A-E, incl. alchemist) | Russell 2014 |
| Inc.Stam.Chig.II.610 | Vatican Library | Vatican City | 1499 | 1 (Alexander VII) | Russell 2014 |
| INCUN A.5.13 | Cambridge University Library | Cambridge | 1499 | 1 (Giovio) | Russell 2014 |
| Modena (Panini) | Biblioteca Panini | Modena | 1499 | 1 (Giovio) | Russell 2014 |
| O.III.38 | Biblioteca degli Intronati | Siena | 1499 | 1 (anonymous) | Russell 2014 |

**Additional known copies (from ISTC, bibliography, Russell's census):**
- To be populated from Russell's thesis world census data
- ISTC records list approximately 200 surviving copies of the 1499 edition
- Exact institutional holdings can be extracted from ISTC database

## Page Design

### Manuscripts Landing Page (`site/manuscripts.html`)

**Structure:**
```
<h2>Copies of the Hypnerotomachia Poliphili</h2>
<p>Orientation intro...</p>

<h3>Annotated Copies Studied by Russell (2014)</h3>
<!-- 6 detailed cards with essay links -->

<h3>Other Known Copies</h3>
<!-- Table of additional institutional holdings -->

<h3>Geographic Distribution</h3>
<!-- Summary by country/region -->
```

### Per-Copy Essay Pages (`site/manuscripts/{slug}.html`)

One essay page per annotated copy, covering:

1. **Physical description:** edition, binding, condition, provenance
2. **Annotation overview:** how many hands, what languages, what interests
3. **Hand profiles:** for each hand in this copy, a description of their annotations
4. **Key folios:** specific folios with significant annotations, linked to marginalia pages
5. **Scholarly significance:** what this copy reveals about HP reception
6. **Images:** linked to available photographs (for BL and Siena)
7. **Provenance:** known ownership history
8. **Review status / confidence markers**

### Per-Copy Essay Template

Following `docs/WRITING_TEMPLATES.md`:
- Voice: present tense, third-person scholarly
- Length: 800-2000 words per copy essay
- Required: at least one passage from Russell's thesis as evidence
- Required: links to relevant scholar pages, dictionary terms, hand pages
- Required: explicit confidence markers for provisional claims

## Pipeline

### Step 1: `scripts/seed_copies.py`

- Create `hp_copies` table
- Populate Russell's 6 annotated copies with full metadata
- Add any additional copies identifiable from the bibliography
- Link to existing `manuscripts`, `annotator_hands` tables

### Step 2: `scripts/generate_copy_essays.py`

- For each of Russell's 6 annotated copies:
  - Query all dissertation_refs for that shelfmark
  - Query all annotator_hands for that shelfmark
  - Query all matches for that shelfmark
  - Use corpus_search to find relevant thesis passages
  - Generate structured essay from evidence
  - Store in hp_copies.annotation_summary (short) and as full page content
- All generated prose marked DRAFT, LLM_ASSISTED

### Step 3: Update `build_site.py`

- Add `build_manuscripts_page()` and `build_manuscripts_detail_pages()`
- Add "Manuscripts" tab to nav
- Cross-link to existing marginalia, scholar, and dictionary pages

## Data Sources

### For Russell's 6 copies:
- `dissertation_refs` table: 282 references distributed across 6 copies
- `annotator_hands` table: 11 hands across copies
- `matches` table: 610 image matches
- Corpus chunks from Russell's thesis (especially Ch. 3-9)

### For additional copies:
- Russell's thesis introduction (census methodology and results)
- ISTC database (institutional holdings)
- Bibliography entries mentioning specific copies

## Copy Essays to Write

### 1. British Library C.60.o.12

Key themes:
- The only 1545 edition in Russell's study
- Ben Jonson's theatrical/literary annotations (Hand A)
- Anonymous alchemist's mercury-centered reading (Hand B)
- The Master Mercury flyleaf declaration
- Alchemical ideogram vocabulary
- Provenance: Thomas Bourne purchase (1641)
- The BL concordance confidence problem (sequential photo numbering)

### 2. Buffalo Rare Book Room

Key themes:
- Five interleaved hands (A-E), the most densely annotated copy
- Hands A-D: possibly Jesuit, St. Omer connection
- Hand E: pseudo-Geber alchemist, Sol/Luna emphasis
- Chess match interpretation (h1r)
- Stratigraphic analysis (which hand overwrites which)

### 3. Vatican Chig.II.610

Key themes:
- Alexander VII (Fabio Chigi) as reader
- Focus on acutezze (verbal wit)
- Connection to Bernini's elephant-obelisk commission
- Papal reader as cultural patron

### 4. Cambridge INCUN A.5.13

Key themes:
- Benedetto Giovio's natural-historical reading
- HP as Plinian reference compendium
- Extractive annotation mode (inventio)

### 5. Modena (Panini)

Key themes:
- Also annotated by Giovio
- Comparison with Cambridge copy annotations
- Bibliographic and natural-historical interests

### 6. Siena O.III.38

Key themes:
- Anonymous annotations
- Digital facsimile available (478 images)
- HIGH confidence image matches
- Basis for the most reliable concordance data

## Validation Gates

- All 6 Russell copies have populated hp_copies entries
- Each copy essay has section anchors, citations, and confidence markers
- Links to existing marginalia pages where folios are discussed
- Historical figure scholars link to their copy pages
- Manuscripts tab appears in nav across all pages
- No BL concordance claims without PROVISIONAL markers

## Cross-Linking

- Copy pages link to: scholar pages (annotators), dictionary terms (annotation concepts),
  marginalia pages (specific folios), essays (Russell alchemical hands)
- Scholar pages for historical figures link to their copy pages
- Dictionary terms like annotator-hand, marginalia, world-census link to manuscripts page
- Russell essay links to relevant copy pages
