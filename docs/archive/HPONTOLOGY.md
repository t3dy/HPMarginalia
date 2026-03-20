# HP Ontology: The Actual Data Model

> This document describes the data model as it exists, not as it was originally designed.
> Revised 2026-03-20 to reflect the current 22-table system after six rounds of expansion.
> For the original aspirational design and its critique, see HPONTOCRIT.md.

## Architecture

SQLite database (`db/hp.db`) is the single source of truth. Python scripts generate
static HTML from it. No ORM, no web framework. Every entity is a table with explicit
provenance columns (source_method, review_status, confidence, needs_review).

---

## Entity Groups

### 1. The Book and Its Copies

These tables model the physical *Hypnerotomachia Poliphili* — the 1499 Aldine edition,
the 1545 reprint, and the specific annotated copies Russell studied.

**`hp_copies`** (6 rows) — Individual copies of the HP worldwide. Each record tracks
shelfmark, institution, city, country, edition (1499 or 1545), whether annotations
are present, how many hands Russell identified, and whether the project holds photographs.
Currently covers Russell's six annotated copies.

**`manuscripts`** (2 rows) — The two copies with local photograph sets: BL C.60.o.12
(196 photos) and Siena O.III.38 (478 photos). Contains the image directory paths.

**`images`** (674 rows) — Individual photographs. Each has a folio number, side (recto/verso),
page type (PAGE, COVER, GUARD, OTHER), and confidence level. The BL images were corrected
in March 2026 after visual verification revealed a 13-photo offset between photo numbers
and folio numbers.

**`signature_map`** (448 rows) — Deterministic lookup table converting signatures (e.g., "b6v")
to sequential folio numbers. Generated from the 1499 collation formula: a-z^8 (omitting j, u, w),
A-F^8, G^4. This map is correct for the 1499 edition. Its applicability to the 1545 edition is
assumed but not fully verified.

### 2. Russell's Dissertation Evidence

These tables capture what Russell documented about HP marginalia in his 2014 thesis.

**`dissertation_refs`** (282 rows) — References extracted from Russell's thesis by regex.
Each records a thesis page, signature reference (e.g., "b6v"), manuscript shelfmark,
context text, marginal text, reference type, and chapter number. 204 of 282 have hand_id
attribution.

**`annotations`** (282 rows) — Canonical annotation table, migrated from dissertation_refs
with additional structure: annotation_type (MARGINAL_NOTE, CROSS_REFERENCE, INDEX_ENTRY,
SYMBOL, EMENDATION, UNDERLINE), confidence, and provenance fields. This is the table that
queries should target.

**`doc_folio_refs`** (282 rows) — Redundant mirror of dissertation_refs with provenance columns
added during V2 migration. Should be deprecated in favor of annotations.

**`matches`** (649 rows) — The critical join: links dissertation references to manuscript
photographs via the signature map. Each match has a confidence level (HIGH, MEDIUM, LOW)
and match method (SIGNATURE_EXACT, FOLIO_EXACT). Siena matches are HIGH/MEDIUM; BL matches
are LOW (pending full verification) or MEDIUM (where ground-truth folio mapping was confirmed).

### 3. Annotator Hands

**`annotator_hands`** (11 rows) — The eleven distinct handwriting identities Russell
identified across six copies. Each record has hand label, manuscript, attribution
(e.g., "Ben Jonson"), language, ink color, date range, school, interests, and whether
the annotator is an alchemist. The two alchemist hands have an `alchemical_framework`
field: Hand B (BL) follows d'Espagnet's mercury-centered framework; Hand E (Buffalo)
follows pseudo-Geber's sulphur/Sol-Luna framework.

**`annotators`** (11 rows) — Redundant duplicate of annotator_hands with slightly
different column names. Created during V2 migration. Should be consolidated.

**`folio_descriptions`** (13 rows) — Detailed scholarly descriptions of individual
annotated folios, focused on the alchemical hands. Each records the signature, hand,
title, full description, alchemical element, alchemical process, alchemical framework,
and Russell page references. All 13 cover alchemist-annotated folios.

### 4. Alchemical Symbol System

**`alchemical_symbols`** (10 rows) — Reference table for the alchemical sign vocabulary:
seven planetary metals (Sol/gold, Luna/silver, Mercury/quicksilver, Venus/copper,
Mars/iron, Jupiter/tin, Saturn/lead) plus cinnabar, sulphur, and the hermaphrodite.
Each has metal, planet, gender, framework association, and source basis from Taylor 1951
and Russell 2014.

**`symbol_occurrences`** (26 rows) — Junction table linking alchemical symbols to specific
folios and hands. Records which symbols Hand B and Hand E used on which pages, with
context text, Latin inflections (e.g., "-ra" for "aurata"), thesis page references,
and confidence levels.

### 5. Scholarly Apparatus

**`dictionary_terms`** (94 rows) — Glossary of HP-specific terminology across 15 categories:
Book History, Annotation Studies, Alchemical Interpretation, Architecture, Textual Motifs,
Scholarly Debates, Characters, Places, Gardens, Processions, Visual/Typographic,
Aesthetic Concepts, Material Culture, Narrative Form. Each term has short and long
definitions, significance to the HP, significance to scholarship, source documents,
page references, evidence quotes, and provenance metadata.

**`dictionary_term_links`** (247 rows) — Bidirectional cross-references between terms.
Link types: RELATED, SEE_ALSO, PARENT.

**`bibliography`** (109 rows) — Scholarly works on the HP grouped by relevance: PRIMARY
(editions/translations), DIRECT (HP as main subject), INDIRECT (HP as part of broader
argument), TANGENTIAL (contextual). Each entry has author, title, year, pub_type,
journal, topic cluster, and review status.

**`scholars`** (60 rows) — Scholars and historical figures. Each has name, specialization,
HP focus, overview prose (2-3 paragraphs for modern scholars, 1 paragraph for
historical figures), and an is_historical_subject flag distinguishing modern researchers
from HP subjects (Colonna, Jonson, Chigi, etc.).

**`scholar_works`** (72 rows) — Junction table linking scholars to bibliography entries,
with has_summary flag indicating whether summaries.json contains a detailed summary.

### 6. Corpus and Documents

**`documents`** (38 rows) — PDF and PPTX files in the project collection. Each has
filename, extracted title, author, year, document type (PRIMARY_TEXT, DISSERTATION,
SCHOLARSHIP, PRESENTATION), page count, and file size.

**`document_topics`** (34 rows) — Topic assignments for documents, linking to the
six-cluster taxonomy (authorship, architecture, text-image, reception, dream-religion,
material-bibliographic).

### 7. Timeline

**`timeline_events`** (71 rows) — Chronological events spanning 1499-2024: publications,
editions, translations, annotations, acquisitions, scholarship, art inspired by the HP,
and literary influence. Each has year, event type, title, description, and optional
links to scholars, bibliography, and manuscripts. Category and medium fields support
the filterable timeline page.

### 8. System

**`schema_version`** (2 rows) — Migration version tracking.

---

## Provenance Model

Every table that holds generated or inferred content carries:

| Field | Values | Purpose |
|-------|--------|---------|
| source_method | DETERMINISTIC, PDF_EXTRACTION, CORPUS_EXTRACTION, LLM_ASSISTED, HUMAN_VERIFIED | How the data was produced |
| review_status | DRAFT, REVIEWED, VERIFIED, PROVISIONAL, UNREVIEWED | Editorial state |
| confidence | HIGH, MEDIUM, LOW, PROVISIONAL | Trust level |
| needs_review | Boolean | Whether human review is needed |

**Promotion rule:** Retrieved evidence may populate fields automatically. LLM-generated
prose must be marked DRAFT and never overwrites VERIFIED content.

---

## Known Redundancies

| Redundancy | Tables | Resolution |
|------------|--------|------------|
| Annotation data split across three tables | dissertation_refs, doc_folio_refs, annotations | annotations is canonical; others should be deprecated |
| Hand profiles duplicated | annotator_hands, annotators | annotator_hands is canonical |
| Manuscript tracking split | manuscripts (2 rows, image-holding), hp_copies (6 rows, all copies) | hp_copies is the broader table; manuscripts stores image paths |

---

## Entity Counts (as of 2026-03-20)

| Entity | Table | Rows |
|--------|-------|------|
| HP copies | hp_copies | 6 |
| Manuscripts with images | manuscripts | 2 |
| Photographs | images | 674 |
| Signature mappings | signature_map | 448 |
| Dissertation references | dissertation_refs | 282 |
| Annotations (canonical) | annotations | 282 |
| Matches (ref-to-image) | matches | 649 |
| Annotator hands | annotator_hands | 11 |
| Folio descriptions | folio_descriptions | 13 |
| Alchemical symbols | alchemical_symbols | 10 |
| Symbol occurrences | symbol_occurrences | 26 |
| Dictionary terms | dictionary_terms | 94 |
| Term cross-links | dictionary_term_links | 247 |
| Bibliography entries | bibliography | 109 |
| Scholars | scholars | 60 |
| Scholar-work links | scholar_works | 72 |
| Documents in collection | documents | 38 |
| Timeline events | timeline_events | 71 |
| Site pages generated | (filesystem) | 330 |
