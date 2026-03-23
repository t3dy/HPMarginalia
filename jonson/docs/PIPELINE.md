# PIPELINE: Processing Stages

## Stage 1: INGEST

**Script:** `src/ingest/ingest.py`
**Input:** Markdown files in `../Ben Jonson Life/md/`
**Output:** `data/raw/sources.json`

Catalogs each source document with metadata:
- filename, title, author, type, page_count
- content_summary (first 200 chars)
- stable source_id (slug of filename)

**Contract:**
- Input: directory of .md files
- Output: JSON array of SourceDocument records
- Validation: every record has source_id, title, filename

## Stage 2: EXCERPT EXTRACTION

**Script:** `src/extract/excerpt.py`
**Input:** `data/raw/sources.json` + source markdown files
**Output:** `data/processed/excerpts.json`

Breaks each source into page-sized excerpts preserving page references.

**Contract:**
- Input: sources.json + .md files
- Output: JSON array of SourceExcerpt records
- Validation: every excerpt has source_id, page_ref, text (non-empty)

## Stage 3: CONTENT CLASSIFICATION

**Script:** `src/extract/classify.py`
**Input:** `data/processed/excerpts.json`
**Output:** `data/processed/classified.json`

Labels each excerpt with one or more categories:
- `jonson_life` — biographical material
- `alchemist_alchemy` — alchemical content related to The Alchemist
- `hypnerotomachia_jonson` — Jonson's HP annotations / Russell's findings

**Contract:**
- Input: excerpts.json
- Output: excerpts.json with added `categories` field
- Validation: categories from allowed set only

## Stage 4: STRUCTURED EXTRACTION

**Scripts:**
- `src/transform/life.py` → `data/exports/life_events.json`
- `src/transform/annotations.py` → `data/exports/annotations.json`
- `src/transform/russell.py` → `data/exports/russell_findings.json`

Converts classified excerpts into typed records.
LLM-assisted where needed, with extraction_method marked.

**Contract:**
- Input: classified.json
- Output: typed JSON arrays (LifeEvent, Annotation, RussellFinding)
- Validation: required fields present, citations attached

## Stage 5: WEBSITE EXPORT

**Script:** `src/site/build_jonson.py`
**Input:** `data/exports/*.json`
**Output:** `site/jonson/*.html`

Generates static HTML pages using the HP site's CSS and nav structure.

**Contract:**
- Input: export JSON files
- Output: valid HTML files with working nav links
- Validation: all pages render, nav links resolve
