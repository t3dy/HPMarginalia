# STATEOFTHEONTOLOGIES: Current State of All Data Models

> A snapshot of every ontological layer in the project as of the end of
> this session. 23 tables, 3223 rows, 5 distinct ontological domains.

---

## Overview

The project's data lives in a single SQLite file (`db/hp.db`) containing
23 tables organized into 5 ontological domains. Three of these tables are
deprecated (data duplicated in canonical replacements). The remaining 20
are active and queried by `build_site.py` to generate 365 pages.

| Domain | Tables | Rows | Purpose |
|--------|--------|------|---------|
| Physical Book | 5 | 1130 | The HP as object: copies, images, signatures, folios |
| Annotations | 5 | 763 | What readers wrote: hands, annotations, symbols, descriptions |
| Concordance | 1 | 431 | The bridge: linking references to photographs |
| Scholarship | 7 | 657 | The field: terms, scholars, bibliography, timeline, woodcuts |
| Corpus | 2 | 72 | The archive: documents and topic assignments |
| System | 1 | 2 | Schema versioning |
| Deprecated | 3 | 575 | Redundant copies of annotation and hand data |

---

## Domain 1: Physical Book (5 tables, 1130 rows)

This domain models the *Hypnerotomachia Poliphili* as a physical artifact
that exists in multiple copies, each containing pages that can be
photographed and referenced by signature notation.

### hp_copies (6 rows, 16 cols) — CANONICAL
Russell's six annotated copies. Each record: shelfmark, institution, city,
country, edition (1499 or 1545), annotation count, hand count, whether
photographs exist in the project, and confidence level.

**State:** Complete for Russell's 6 copies. No ISTC data for the ~200
other known copies. BL confidence recently upgraded from LOW to MEDIUM
after the offset fix.

### manuscripts (2 rows, 7 cols) — ACTIVE (image paths)
The two copies with local photograph directories. Contains the file system
paths to the BL and Siena image folders.

**Relationship to hp_copies:** manuscripts tracks image storage; hp_copies
tracks scholarly metadata. Both reference the same shelfmarks.

### images (674 rows, 10 cols) — ACTIVE
Individual photographs: 196 BL + 478 Siena. Each has folio number (corrected
for BL offset=13), side (recto/verso), page type (PAGE, COVER, GUARD, OTHER),
and confidence level.

**State:** All BL images have corrected folio numbers. All images have been
compressed and deployed to `site/images/`. 27 BL page numbers visually
verified. 180 BL text pages, 468 Siena text pages.

### signature_map (448 rows, 6 cols) — ACTIVE
Deterministic lookup: signature → folio number. Generated from the 1499
collation formula a-z8 A-F8 G4 (omitting j, u, w). Each entry: signature
string, folio number, side, quire letter, leaf-in-quire position.

**State:** Complete and correct for the 1499 edition. Assumed applicable
to the 1545 edition (confirmed by visible quire signatures g ii and K iii
in BL photographs). 4 signatures in Russell's refs don't map (z5v, z6r,
z5r, u3r — collation ambiguities).

### woodcuts (18 rows, 29 cols) — ACTIVE
Woodcuts detected from BL photograph reading. Each: slug, title, signature,
page number, subject category (ARCHITECTURAL, NARRATIVE, HIEROGLYPHIC, etc.),
woodcut type (FULL_PAGE, IN_TEXT, FRIEZE, etc.), description, chapter context,
scholarly discussion, influence, annotation presence, alchemical annotation flag.

**State:** 18 of ~172 woodcuts cataloged. BL photos cover pages 1-176
(38% of the book). 7 woodcuts have confirmed alchemical annotations.

---

## Domain 2: Annotations (5 tables, 763 rows)

This domain models what readers wrote in the margins of the HP: who they
were, what they wrote, and what alchemical system they used.

### annotations (282 rows, 18 cols) — CANONICAL
The canonical annotation record. Each entry: manuscript, hand, signature,
folio, side, annotation text, annotation type (6 types: MARGINAL_NOTE,
CROSS_REFERENCE, INDEX_ENTRY, SYMBOL, EMENDATION, UNDERLINE), thesis page,
chapter, confidence, provenance.

**State:** Migrated from dissertation_refs. 204 of 282 have hand_id
attribution (72%). 6 annotation types classified. All marked needs_review.

### annotator_hands (11 rows, 13 cols) — CANONICAL
The eleven distinct handwriting identities Russell identified. Each:
hand label, manuscript, attribution (e.g., "Ben Jonson"), language, ink
color, date range, school, interests, description, is_alchemist flag,
alchemical_framework (mercury_despagnet for Hand B, sulphur_pseudo_geber
for Hand E).

**State:** Complete. All 11 hands documented with rich prose descriptions.

### folio_descriptions (13 rows, 12 cols) — ACTIVE
Detailed scholarly analyses of individual annotated folios, focused on the
alchemical hands. Each: signature, manuscript, hand, title, long description,
alchemical element, alchemical process, alchemical framework, Russell page refs.

**State:** 13 entries covering all alchemist-annotated folios with descriptions.
Titles like "The Alchemist's Manifesto: Master Mercury" and "The Chess Match:
Three Rounds of Distillation."

### alchemical_symbols (10 rows, 9 cols) — ACTIVE
Reference table for the alchemical sign vocabulary: 7 planetary metals
(Sol/gold, Luna/silver, Mercury/quicksilver, Venus/copper, Mars/iron,
Jupiter/tin, Saturn/lead) plus cinnabar, sulphur, and the hermaphrodite.
Each: symbol name, Unicode approximation, metal, planet, gender, framework.

**State:** Complete for the symbols Russell documents.

### symbol_occurrences (26 rows, 11 cols) — ACTIVE
Junction: which symbols appear on which folios, attributed to which hand.
Each: symbol, hand, signature, context text, Latin inflection (e.g., "-ra"
for "aurata"), thesis page, confidence.

**State:** 26 occurrences across 13 folios. 9 BL Hand B, 4 Buffalo Hand E.
2 additional sites discovered by image reading (c5v, h8r) not yet in this
table (marked PROVISIONAL).

---

## Domain 3: Concordance (1 table, 431 rows)

### matches (431 rows, 10 cols) — ACTIVE
The critical join linking dissertation references to manuscript photographs.
Each: ref_id, image_id, match method (SIGNATURE_EXACT or FOLIO_EXACT),
confidence (HIGH or MEDIUM — zero LOW), needs_review.

**State:** 48 HIGH (visually verified) + 383 MEDIUM (computed or cross-copy).
All BL matches rebuilt with corrected folio data. No wrong matches remain.
34 refs unmatched (19 no-manuscript, 7 beyond photo range, 8 collation
ambiguities).

---

## Domain 4: Scholarship (7 tables, 657 rows)

This domain models the scholarly conversation around the HP: who has
studied it, what they've written, what terms they use, and how the
book's reception has unfolded over five centuries.

### dictionary_terms (94 rows, 22 cols) — ACTIVE
Glossary across 15 categories: Book History, Annotation Studies, Alchemical
Interpretation, Architecture, Textual Motifs, Scholarly Debates, Characters,
Places, Gardens, Processions, Visual/Typographic, Aesthetic Concepts,
Material Culture, Narrative Form, Architecture & Gardens.

Each: slug, label, category, short definition, long definition, significance
to HP, significance to scholarship, source documents, page refs, evidence
quotes, related scholars, review status, source method, confidence.

**State:** All 94 terms have definitions and significance prose. All DRAFT.
All enriched with corpus evidence (source documents, page refs, quotes).

### dictionary_term_links (247 rows, 4 cols) — ACTIVE
Bidirectional cross-references between terms. Link types: RELATED, SEE_ALSO,
PARENT.

**State:** 247 links. No orphans. All terms have at least one link.

### bibliography (109 rows, 15 cols) — ACTIVE
Works grouped by hp_relevance: PRIMARY (editions/translations), DIRECT
(HP as main subject), INDIRECT (HP in broader argument), TANGENTIAL
(contextual). Each: author, title, year, pub_type, journal, topic cluster,
in_collection flag, review status.

**State:** 109 entries. 0 "Unknown" authors (fixed). 2 "Unidentified"
with explanatory notes. All UNREVIEWED.

### scholars (60 rows, 16 cols) — ACTIVE
Modern scholars and historical figures. Each: name, specialization, HP focus,
overview prose (2-3 paragraphs), is_historical_subject flag, review status.

**State:** 59 of 60 have overview prose. 11 tagged as historical figures
(Colonna, Manutius, Jonson, Chigi, Giovio x2, Martin, Beroalde, Nodier,
d'Espagnet, Dallington). All DRAFT.

### scholar_works (72 rows, 4 cols) — ACTIVE
Junction: scholars ↔ bibliography. has_summary flag (34 entries linked to
summaries.json content).

### timeline_events (71 rows, 16 cols) — ACTIVE
Chronological events 1499-2024: editions, translations, annotations,
scholarship, art, literary influence. Each: year, event type, title,
description, category, medium, location, confidence.

**State:** 71 events. Filterable on the site by category.

### documents (38 rows, 11 cols) — ACTIVE
PDFs and PPTXs in the project collection. Each: filename, title, author,
year, doc_type, page count, file size.

---

## Domain 5: System (1 table)

### schema_version (2 rows, 2 cols)
Migration tracking. Version 1 (initial) and version 2 (V2 migration).

---

## Deprecated Tables (3 tables, 575 rows)

| Table | Rows | Replaced By | Why Kept |
|-------|------|-------------|----------|
| dissertation_refs | 282 | annotations | Original extraction. build_site.py still queries it for marginalia pages. |
| doc_folio_refs | 282 | annotations | V2 duplicate with extra provenance columns. Not queried anywhere. |
| annotators | 11 | annotator_hands | V2 duplicate with different column names. Not queried. |

**Rule:** New code MUST query canonical tables. Deprecated tables will
not be updated. The single remaining dependency (build_site.py querying
dissertation_refs for marginalia pages) should be migrated in a future pass.

---

## Ontological Health

### What's Clean
- **0 orphan records** across all junction tables
- **0 referential integrity violations**
- **0 LOW confidence matches** (eliminated)
- **0 duplicate dictionary slugs**
- **0 orphaned dictionary links**
- **All 94 dictionary terms** have definitions + significance
- **All 11 annotator hands** have descriptions + framework data
- **All 18 woodcuts** have subjects + categories

### What's Not Clean
- **3 deprecated tables** still exist (won't be deleted, but should stop being queried)
- **78 unattributed annotations** (28% of 282)
- **All content DRAFT/UNREVIEWED** — no human expert has verified anything
- **matches.ref_id** still points to dissertation_refs.id, not annotations.id
- **~154 woodcuts uncataloged** (photos cover only 38% of the book)
- **4 copies without photographs** (Buffalo, Vatican, Cambridge, Modena)

### Ontological Completeness by Domain

| Domain | Completeness | Notes |
|--------|-------------|-------|
| Physical Book | **85%** | Missing: ISTC copies, full woodcut inventory |
| Annotations | **75%** | Missing: 78 unattributed, 2 PROVISIONAL alchemical sites |
| Concordance | **90%** | Missing: 34 unmatchable refs (structural limits) |
| Scholarship | **80%** | Missing: bibliography annotations, citation network |
| Corpus | **95%** | All PDFs extracted and chunked |

---

## How the Ontologies Evolved

### V1 (Initial Build)
6 tables: documents, manuscripts, images, signature_map, dissertation_refs, matches.
No provenance. No confidence. No hand attribution.

### V2 (Schema Migration)
Added 12 tables: annotations, annotators, annotator_hands, doc_folio_refs,
dictionary_terms, dictionary_term_links, bibliography, scholars, scholar_works,
timeline_events, schema_version, document_topics.
Added provenance columns (review_status, source_method, confidence, needs_review).
Downgraded BL confidence to LOW.

### V3 (Enrichment Phase)
Added 3 tables: alchemical_symbols, symbol_occurrences, folio_descriptions.
Extended dictionary_terms with significance and evidence columns.
Added scholar_overview and is_historical_subject to scholars.
Added alchemical_framework to annotator_hands.

### V4 (Concordance Fix + Expansion)
Added 2 tables: hp_copies, woodcuts.
Fixed BL offset (=13). Rebuilt all BL matches. Eliminated LOW confidence.
Consolidated annotations table. Classified 6 annotation types.
Extended timeline with art, literary, scholarship events.

### V5 (Antigravity Refactor)
No new tables. Documented canonical vs deprecated. Collapsed 36 design
documents into 5 core docs. Established operating modes and constraints.
Principle: "outward not deeper" — surface existing data before adding more.
