# SYSTEM: HP Marginalia Platform Architecture

## Purpose

A static website presenting the marginalia, scholarship, and reception
history of the 1499 *Hypnerotomachia Poliphili*, built from a SQLite
database via Python scripts. No framework. No server. No dependencies
beyond Python standard library.

## Architecture

```
db/hp.db (SQLite, 22 tables)
    ↓
scripts/ (42 Python scripts)
    ↓
site/ (354 static HTML pages, deployed to GitHub Pages)
```

### Data Flow

```
PDFs → pdf_to_markdown.py → md/ → chunk_documents.py → chunks/
Russell thesis → extract_references.py → dissertation_refs (282)
                                        → consolidate_annotations.py → annotations (282)
Image folders → catalog_images.py → images (674)
Collation formula → build_signature_map.py → signature_map (448)
References + Images + Map → match_refs_to_images.py + rebuild_bl_matches.py → matches (431)
All tables → build_site.py → site/ (354 pages)
```

### Provenance Model

Every generated datum carries:
- `source_method`: DETERMINISTIC | CORPUS_EXTRACTION | LLM_ASSISTED | HUMAN_VERIFIED
- `review_status`: DRAFT | REVIEWED | VERIFIED | PROVISIONAL
- `confidence`: HIGH | MEDIUM | LOW | PROVISIONAL

Rule: never overwrite VERIFIED content. Never present DRAFT as VERIFIED.

## Operating Modes

When working on this project, operate in one of these modes:

### 1. Ontology Mode
Owns the schema. Prevents table duplication. Enforces canonical tables.
Forbidden: creating new tables without deprecating old equivalents.

### 2. Pipeline Mode
Owns scripts. Handles ingestion, matching, enrichment.
Forbidden: modifying site HTML directly.

### 3. Verification Mode
Validates matches against images. Handles confidence upgrades.
Reads manuscript photographs. Produces structured evidence.
Forbidden: generating prose without evidence.

### 4. Presentation Mode
Builds site pages. Ensures all DB entities are visible.
Forbidden: adding new data — only rendering what exists.

### 5. Research Mode
Reads PDFs, images, and web sources. Produces structured outputs
(JSON packets, evidence files). Forbidden: writing directly to DB
without staging.

## Constraints

1. **Outward not deeper.** Do not add data layers if existing layers are incomplete.
2. **Reality over design.** If a document conflicts with the database, the document is wrong.
3. **5 core docs.** SYSTEM.md, ONTOLOGY.md, PIPELINE.md, INTERFACE.md, ROADMAP.md.
   Everything else is in docs/archive/ for reference.
4. **Canonical tables only.** Use `annotations` not `dissertation_refs`.
   Use `annotator_hands` not `annotators`. Use `hp_copies` not `manuscripts` for copy data.

## Build

```bash
python scripts/build_site.py     # Rebuild all 354 pages
python scripts/validate.py       # Full QA
```
