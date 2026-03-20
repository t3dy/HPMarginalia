# ONTOLOGY: The Actual Database Schema

> This describes what EXISTS in db/hp.db. Nothing aspirational.
> Last verified: 2026-03-20. 22 tables, ~2800 total rows.

## Canonical Tables

### The Book and Its Copies

| Table | Rows | Purpose |
|-------|------|---------|
| **hp_copies** | 6 | All known annotated copies (Russell's 6). Shelfmark, institution, edition, hand count, confidence. |
| **manuscripts** | 2 | Copies with local photographs (BL, Siena). Contains image directory paths. |
| **images** | 674 | Individual photographs. 196 BL (offset-corrected, folio=photo-13), 478 Siena (folio in filename). |
| **signature_map** | 448 | Deterministic lookup: signature (b6v) → folio number. From 1499 collation a-z8 A-F8 G4. |

### Annotations and Hands

| Table | Rows | Purpose |
|-------|------|---------|
| **annotations** | 282 | CANONICAL. Migrated from dissertation_refs. Has annotation_type (6 types), hand_id, confidence. |
| **annotator_hands** | 11 | CANONICAL. 11 hands across 6 copies. Has alchemical_framework for Hand B and E. |
| **matches** | 431 | Ref-to-image links. 48 HIGH + 383 MEDIUM + 0 LOW. |
| **folio_descriptions** | 13 | Detailed analyses of alchemist-annotated folios. |
| **woodcuts** | 18 | Detected woodcuts with subjects, categories, annotation data. |

### Alchemical System

| Table | Rows | Purpose |
|-------|------|---------|
| **alchemical_symbols** | 10 | 7 planetary metals + cinnabar, sulphur, hermaphrodite. |
| **symbol_occurrences** | 26 | Which symbols on which folios, attributed to which hand. |

### Scholarly Apparatus

| Table | Rows | Purpose |
|-------|------|---------|
| **dictionary_terms** | 94 | 15 categories. Has significance_to_hp, significance_to_scholarship. |
| **dictionary_term_links** | 247 | Bidirectional cross-references (RELATED, SEE_ALSO, PARENT). |
| **bibliography** | 109 | Works grouped by hp_relevance (PRIMARY/DIRECT/INDIRECT/TANGENTIAL). |
| **scholars** | 60 | 59 with overviews. 11 tagged is_historical_subject. |
| **scholar_works** | 72 | Junction: scholars ↔ bibliography. has_summary flag. |
| **timeline_events** | 71 | 1499-2024. Editions, annotations, scholarship, art, literary influence. |

### Corpus

| Table | Rows | Purpose |
|-------|------|---------|
| **documents** | 38 | PDFs/PPTXs cataloged from filesystem. |
| **document_topics** | 34 | Topic assignments (6-cluster taxonomy). |

### System

| Table | Rows | Purpose |
|-------|------|---------|
| **schema_version** | 2 | Migration tracking. |

## Deprecated Tables (DO NOT QUERY)

| Table | Rows | Replaced By | Why Kept |
|-------|------|-------------|----------|
| **dissertation_refs** | 282 | annotations | Original extraction. Some scripts still reference. |
| **doc_folio_refs** | 282 | annotations | V2 duplicate with provenance columns. Not queried. |
| **annotators** | 11 | annotator_hands | V2 duplicate with different column names. |

**Rule:** New code MUST query canonical tables. Deprecated tables exist
only for backward compatibility and will not be updated.

## Relationships

```
hp_copies.shelfmark ←→ manuscripts.shelfmark (for image-holding copies)
images.manuscript_id → manuscripts.id
matches.ref_id → dissertation_refs.id (LEGACY — should migrate to annotations.id)
matches.image_id → images.id
annotations.hand_id → annotator_hands.id
annotations.manuscript_id → manuscripts.id
symbol_occurrences.symbol_id → alchemical_symbols.id
symbol_occurrences.hand_id → annotator_hands.id
scholar_works.scholar_id → scholars.id
scholar_works.bib_id → bibliography.id
dictionary_term_links.term_id → dictionary_terms.id
woodcuts.signature_1499 ←→ signature_map.signature
```

## Coverage and Confidence

| Data | Coverage | Confidence |
|------|----------|------------|
| Siena matches | 392/478 images matched | HIGH/MEDIUM |
| BL matches | 39/50 refs matched (11 beyond photo range) | MEDIUM (27 visually verified as HIGH) |
| Buffalo/Vatican/Cambridge/Modena | 0 matches (no photographs) | N/A |
| Hand attribution | 204/282 annotations (72%) | MEDIUM |
| Dictionary significance | 94/94 terms | DRAFT (LLM-assisted) |
| Scholar overviews | 59/60 scholars | DRAFT (LLM-assisted) |
| Woodcut inventory | 18/~172 (BL photos cover pages 1-176 only) | MEDIUM |

## 4 Unmapped Signatures

z5v, z6r, u3r, z5r — collation ambiguities. The signature map omits 'u'
per the 1499 convention; Russell may use it differently. z5 may exceed
quire z's leaf count. These are KNOWN UNRESOLVABLE without physical book access.
