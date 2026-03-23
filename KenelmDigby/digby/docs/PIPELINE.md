# PIPELINE: Kenelm Digby Data Pipeline

## Overview

5-stage pipeline transforming source PDFs into website-ready structured content.

## Stage 1: Ingest (`scripts/01_ingest.py`)

**Purpose:** Read source files from `../` and register them in the database.

**Input:** Files in `KenelmDigby/` (PDF, TXT, MD, EPUB, XLSX, PPTX)

**Output:** `source_documents` table rows

**Contract:**
- Each file gets one SourceDocument record
- Metadata extracted from filename (author, year, journal, DOI where parseable)
- Text extraction attempted for PDF, TXT, MD files
- Extracted text stored in `data/raw/{id}.txt`
- `text_extracted` flag set accurately

**Validation:**
- All required fields present (id, filename, filepath, title, file_type)
- file_type is valid enum value
- No duplicate filenames

## Stage 2: Excerpt Extraction (`scripts/02_excerpt.py`)

**Purpose:** Break extracted text into manageable excerpts with page references.

**Input:** `source_documents` where `text_extracted = 1`

**Output:** `source_excerpts` table rows

**Contract:**
- Excerpts are ~500-1500 words each
- Page references preserved where detectable (page breaks, headers)
- Section headings captured where present
- One excerpt = one conceptual unit (not arbitrary split)

**Validation:**
- source_document_id references valid document
- text is non-empty
- No orphan excerpts

## Stage 3: Classification (`scripts/03_classify.py`)

**Purpose:** Assign theme labels to excerpts.

**Input:** `source_excerpts` without theme labels

**Output:** `source_excerpts` updated with `themes` field

**Contract:**
- Each excerpt gets 1+ theme labels from: biography, memoir, pirate,
  alchemist_natural_philosopher, courtier_legal_thinker, works,
  bibliography, hypnerotomachia_digby
- Multiple themes allowed (comma-separated)
- Classification based on keyword matching + content analysis

**Validation:**
- All theme values are valid ThemeLabel enum members
- No excerpt left unclassified

## Stage 4: Structured Extraction (`scripts/04_extract.py`)

**Purpose:** From classified excerpts, produce structured records.

**Input:** Classified `source_excerpts`

**Output:** Records in: `life_events`, `memoir_episodes`, `work_records`,
`digby_theme_records`, `hypnerotomachia_findings`, `hypnerotomachia_evidence`,
`citations`

**Contract:**
- Every structured record has at least one Citation
- Citations reference real source_documents and optionally source_excerpts
- Records assigned to correct theme/table
- review_status = DRAFT for all machine-generated records

**Validation:**
- Required fields present
- citation_ids reference valid citations
- Theme labels valid
- No record without provenance

## Stage 5: Export (`scripts/05_export.py`)

**Purpose:** Export database tables to JSON for site rendering.

**Input:** All populated tables in `db/digby.db`

**Output:** JSON files in `data/exports/`

**Contract:**
- One JSON file per table: `{table_name}.json`
- Additionally, page-specific exports combining records for each site page
- Exports are complete snapshots (not incremental)

**Validation:**
- JSON is valid and parseable
- Record counts match database
- All exports written to `data/exports/`
