# WOODCUTONTOLOGY: Data Model for HP Woodcuts

> Schema design for tracking the 168-172 woodcuts of the Hypnerotomachia
> Poliphili across editions, copies, and scholarly discussions.

---

## The Count Problem

Different sources count differently:
- **172** (including historiated initials and decorative elements) — Pozzi & Ciapponi, MIT edition
- **168** (excluding historiated initials) — Appell 1889 facsimile, Internet Archive
- **11 full-page illustrations** + **39 floriated initials** + **~120 in-text woodcuts** — one decomposition

This ontology uses **172** as the canonical count, following the critical edition tradition,
but tracks which category each woodcut belongs to (full-page, in-text, initial, ornamental).

---

## New Table: `woodcuts`

```sql
CREATE TABLE IF NOT EXISTS woodcuts (
    id INTEGER PRIMARY KEY,
    -- Identification
    woodcut_number INTEGER,           -- sequential number in the 1499 edition
    slug TEXT UNIQUE,                 -- URL-safe identifier
    title TEXT NOT NULL,              -- short descriptive title
    -- Location in the book
    signature_1499 TEXT,              -- signature in the 1499 edition (e.g., 'b6v')
    page_1499 INTEGER,               -- page number in the 1499 edition
    signature_1545 TEXT,              -- signature in the 1545 edition (if different)
    page_1545 INTEGER,               -- page number in the 1545 edition
    chapter_context TEXT,             -- which narrative chapter it illustrates
    -- Description
    description TEXT,                 -- scholarly description (2-4 sentences)
    subject_category TEXT,            -- ARCHITECTURAL | LANDSCAPE | NARRATIVE | HIEROGLYPHIC |
                                     -- PROCESSION | DECORATIVE | PORTRAIT | DIAGRAM | INITIAL
    depicted_elements TEXT,           -- comma-separated: 'elephant, obelisk, hieroglyphs'
    -- Physical properties
    woodcut_type TEXT,                -- FULL_PAGE | IN_TEXT | INITIAL | ORNAMENTAL | FRIEZE
    dimensions_mm TEXT,               -- approximate dimensions if known
    signed TEXT,                      -- 'b' if signed, NULL if not
    -- Attribution
    attributed_to TEXT,               -- 'Benedetto Bordon' | 'unknown' | etc.
    attribution_basis TEXT,           -- scholarly basis for attribution
    -- Scholarly significance
    scholarly_discussion TEXT,        -- who has written about this woodcut
    influence TEXT,                   -- what this woodcut influenced (Bernini, gardens, etc.)
    -- In our collection
    has_bl_photo BOOLEAN DEFAULT 0,   -- do we have a BL photograph showing this woodcut?
    bl_photo_number INTEGER,          -- which BL photo (if available)
    has_siena_photo BOOLEAN DEFAULT 0,
    has_annotation BOOLEAN DEFAULT 0, -- does any annotator mark this woodcut?
    alchemical_annotation BOOLEAN DEFAULT 0,  -- does an alchemist annotate it?
    -- Cross-references
    dictionary_terms TEXT,            -- comma-separated slugs of related dictionary terms
    -- Provenance
    review_status TEXT DEFAULT 'DRAFT',
    source_method TEXT DEFAULT 'LLM_ASSISTED',
    source_basis TEXT,                -- citation for the description
    confidence TEXT DEFAULT 'MEDIUM',
    notes TEXT
);
```

## New Table: `woodcut_editions`

Tracks differences between the 1499 and later edition woodcuts.

```sql
CREATE TABLE IF NOT EXISTS woodcut_editions (
    id INTEGER PRIMARY KEY,
    woodcut_id INTEGER REFERENCES woodcuts(id),
    edition TEXT NOT NULL,             -- '1499' | '1545' | '1546_french'
    block_status TEXT,                 -- ORIGINAL | RECUT | NEW | MODIFIED
    notes TEXT                         -- differences from 1499
);
```

---

## Relationships to Existing Tables

```
woodcuts.signature_1499 → signature_map.signature
woodcuts.bl_photo_number → images.sort_order (via photo number)
woodcuts ←→ annotations (via signature_ref)
woodcuts ←→ symbol_occurrences (via signature_ref)
woodcuts ←→ folio_descriptions (via signature_ref)
woodcuts.dictionary_terms → dictionary_terms.slug
```

---

## Subject Categories

| Category | Description | Examples |
|----------|-------------|---------|
| ARCHITECTURAL | Buildings, ruins, columns, arches, portals | Pyramid, ruined temple, triumphal arches |
| LANDSCAPE | Gardens, forests, islands, natural settings | Dark forest, Cythera garden diagram, pergola |
| NARRATIVE | Scenes with characters acting | Poliphilo sleeping, nymphs bathing, sacrifice |
| HIEROGLYPHIC | Inscriptions, pseudo-Egyptian texts, monuments | Elephant-obelisk, GONOS KAI ETOUSIA monument |
| PROCESSION | Triumphal processions, parades, ceremonies | Six triumph scenes, sacrifice to Priapus |
| DECORATIVE | Friezes, borders, ornamental panels | Grotesque frieze, decorative borders |
| PORTRAIT | Single figures, busts, medallions | Circular medallion, deity figures |
| DIAGRAM | Schematic plans, measurements, layouts | Cythera garden plan, architectural proportions |
| INITIAL | Historiated chapter initials (the acrostic letters) | P, O, L, I, A, M... forming POLIAM FRATER... |

---

## Woodcut Type Classification

| Type | Count (est.) | Description |
|------|-------------|-------------|
| FULL_PAGE | 11 | Occupy an entire page |
| IN_TEXT | ~120 | Placed within the text flow |
| INITIAL | 38 | Historiated capital letters at chapter openings |
| ORNAMENTAL | ~3 | Decorative elements, borders |
| FRIEZE | ~2-3 | Horizontal decorative bands |

---

## Artist Attribution State

The woodcut artist remains unidentified. Candidates proposed in scholarship:

| Candidate | Proposed By | Basis |
|-----------|------------|-------|
| Benedetto Bordon | Various | Paduan miniaturist, stylistic analysis |
| Andrea Mantegna | Earlier scholarship | Classical style, Paduan connection |
| Gentile Bellini | Earlier scholarship | Venetian school |
| Giovanni Bellini | Earlier scholarship | Venetian school |
| Jacopo de' Barbari | Some scholars | Perspectival skill |
| The "Master of the Poliphilo" | Convention | Anonymous designation |
| Francesco Colonna (author) | Lefaivre 1997 | Author as designer argument |

Two woodcuts (leaves 10b and 21a in the 1499 edition) are signed with the letter "b,"
which has been interpreted as evidence for Bordon or another artist whose name begins with B.

---

## What We Currently Know from Image Reading

18 woodcuts detected in BL photos (pages 1-176):

| Photo | Page | Signature | Subject | Annotated? |
|-------|------|-----------|---------|------------|
| 17 | 4 | a2v | Dark forest (selva oscura) | Yes |
| 21 | 8 | a4v | Landscape with reclining figure | Moderate |
| 23 | 10 | a5v | Poliphilo sleeping (dream-within-dream) | Moderate |
| 24 | 11 | a6r | Poliphilo in garden with palms and well | Heavy |
| 35 | 22 | b3v | Horse and rider on sarcophagus | Moderate |
| 36 | 23 | b4r | Twin inscribed monuments D.AMBIG.D.D. | Heavy |
| 40 | 27 | b6r | GONOS KAI ETOUSIA inscription monument | Heavy |
| 41 | 28 | b6v | Elephant and Obelisk | Heavy + Alchemical |
| 42 | 29 | b7r | Figure on monument with Greek inscription | Heavy |
| 65 | 52 | d2v | Poliphilo at portal with dragon | Moderate |
| 100 | 87 | f4r | Grotesque frieze with hybrid figures | Moderate |
| 105 | 92 | f6v | Circular medallion/deity figure | Heavy + Alchemical? |
| 115 | 102 | g3v | Ornate candelabrum/fountain structure | Moderate |
| 135 | 122 | h5v | Circular medallion/cameo with figure | Heavy |
| 140 | 127 | h8r | Figures at portal/doorway | Heavy + Alchemical |
| 145 | 132 | i2v | Garden scene with pergola and nymph | Moderate |
| 170 | 157 | k5r | Triumphal procession with soldiers/flags | Moderate |
| 175 | 162 | k7v | Triumph scene PARS ANTIQVA ET POSTERIOR | Moderate |

---

## Pipeline for Populating the Woodcuts Table

### Step 1: `scripts/seed_woodcuts.py` (Deterministic + LLM-assisted)
- Seed the 18 visually detected woodcuts from BL photos
- Add known woodcuts from scholarly literature (Huelsen, Godwin)
- Cross-reference against our BL photo set

### Step 2: Cross-link to existing data
- Link woodcuts to signature_map entries
- Link to annotations and symbol_occurrences where relevant
- Link to dictionary terms (elephant-obelisk, sleeping-nymph-fountain, etc.)

### Step 3: Build site pages
- Woodcut index page with thumbnails (where BL photos available)
- Individual woodcut detail pages with image, description, scholarly context
