# SCHEMA: Kenelm Digby Data Model

## Overview

9 tables in `db/digby.db`. Models defined in `src/models.py`.

---

## 1. source_documents

Represents a source file in the Digby corpus.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | TEXT PK | yes | e.g. "sdoc_a1b2c3d4" |
| filename | TEXT | yes | Original filename |
| filepath | TEXT | yes | Relative path from project root |
| title | TEXT | yes | Human-readable title |
| file_type | TEXT | yes | pdf, txt, md, epub, xlsx, pptx |
| author | TEXT | no | Author(s) |
| year | INTEGER | no | Publication year |
| journal | TEXT | no | Journal name |
| doi | TEXT | no | DOI if available |
| page_count | INTEGER | no | Page count |
| text_extracted | INTEGER | no | 0 or 1 |
| extracted_text_path | TEXT | no | Path to extracted text file |
| ingested_at | TEXT | no | ISO timestamp |
| notes | TEXT | no | |

## 2. source_excerpts

An excerpt from a source document with page reference.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | TEXT PK | yes | e.g. "exc_a1b2c3d4" |
| source_document_id | TEXT FK | yes | References source_documents |
| text | TEXT | yes | Excerpt content |
| page_start | INTEGER | no | Starting page |
| page_end | INTEGER | no | Ending page |
| section_heading | TEXT | no | Section title if detectable |
| themes | TEXT | no | Comma-separated ThemeLabel values |
| source_method | TEXT | no | Default: CORPUS_EXTRACTION |
| review_status | TEXT | no | Default: DRAFT |
| created_at | TEXT | no | ISO timestamp |

## 3. life_events

A structured event in Digby's life.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | TEXT PK | yes | e.g. "evt_a1b2c3d4" |
| title | TEXT | yes | Event title |
| date_display | TEXT | yes | Human-readable date |
| year | INTEGER | no | Year for sorting |
| description | TEXT | yes | Event description |
| life_phase | TEXT | no | youth, voyage, exile, restoration, etc. |
| location | TEXT | no | |
| people_involved | TEXT | no | Comma-separated |
| citation_ids | TEXT | required | Comma-separated Citation ids |
| source_method | TEXT | no | |
| review_status | TEXT | no | Default: DRAFT |
| confidence | TEXT | no | HIGH, MEDIUM, LOW |

## 4. work_records

A work by or closely associated with Digby.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | TEXT PK | yes | |
| title | TEXT | yes | Work title |
| year | INTEGER | no | Publication/composition year |
| work_type | TEXT | no | treatise, memoir, recipe_book, letter, poem |
| subject | TEXT | no | |
| description | TEXT | no | |
| significance | TEXT | no | |
| citation_ids | TEXT | required | |
| source_method | TEXT | no | |
| review_status | TEXT | no | |

## 5. memoir_episodes

A structured unit for summarizing Digby's memoir.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | TEXT PK | yes | |
| title | TEXT | yes | Episode title |
| episode_number | INTEGER | no | Sequence order |
| date_display | TEXT | no | When the episode takes place |
| year | INTEGER | no | |
| summary | TEXT | yes | Episode summary |
| key_events | TEXT | no | Comma-separated |
| people | TEXT | no | Comma-separated |
| places | TEXT | no | Comma-separated |
| themes | TEXT | no | Comma-separated |
| citation_ids | TEXT | required | |
| source_method | TEXT | no | |
| review_status | TEXT | no | |

## 6. digby_theme_records

Thematic content for pirate, alchemist, or courtier showcases.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | TEXT PK | yes | |
| theme | TEXT | yes | pirate, alchemist_natural_philosopher, courtier_legal_thinker |
| title | TEXT | yes | |
| summary | TEXT | yes | |
| key_details | TEXT | no | |
| people | TEXT | no | Comma-separated |
| places | TEXT | no | Comma-separated |
| date_display | TEXT | no | |
| year | INTEGER | no | |
| significance | TEXT | no | |
| citation_ids | TEXT | required | |
| source_method | TEXT | no | |
| review_status | TEXT | no | |
| confidence | TEXT | no | |

## 7. citations

Provenance record tying claims to source materials.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | TEXT PK | yes | e.g. "cit_a1b2c3d4" |
| source_document_id | TEXT FK | yes | References source_documents |
| excerpt_id | TEXT | no | References source_excerpts |
| page_or_location | TEXT | no | Page number or location |
| quote_fragment | TEXT | no | Short identifying quote |
| context | TEXT | no | What this citation supports |
| created_at | TEXT | no | |

## 8. hypnerotomachia_findings

Claims about Digby's connection to the Hypnerotomachia.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | TEXT PK | yes | |
| title | TEXT | yes | Finding title |
| claim | TEXT | yes | The specific claim |
| description | TEXT | yes | Explanation |
| evidence_excerpt | TEXT | no | Key evidence text |
| related_concepts | TEXT | no | e.g. "Jupiter/Tin, Mercury" |
| significance | TEXT | no | |
| citation_ids | TEXT | required | |
| source_method | TEXT | no | |
| review_status | TEXT | no | |
| confidence | TEXT | no | |

## 9. hypnerotomachia_evidence

Supporting evidence for HP findings.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | TEXT PK | yes | |
| finding_id | TEXT FK | yes | References hypnerotomachia_findings |
| excerpt | TEXT | yes | Evidence text |
| source | TEXT | yes | Source title or reference |
| page_or_location | TEXT | no | |
| notes | TEXT | no | |
