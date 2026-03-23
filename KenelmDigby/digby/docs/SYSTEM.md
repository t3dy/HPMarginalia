# SYSTEM: Kenelm Digby Module Architecture

## Purpose

A data pipeline and static website section presenting Sir Kenelm Digby
(1603-1665) — his life, works, memoir, thematic identities (pirate,
alchemist, courtier), and connection to the Hypnerotomachia Poliphili.

Linked from the main HP Marginalia site under a "Digby" tab.

## Architecture

```
KenelmDigby/ (source corpus: 47 files)
    ↓
KenelmDigby/digby/scripts/ (5-stage pipeline)
    ↓
KenelmDigby/digby/db/digby.db (SQLite, 9 tables)
    ↓
KenelmDigby/digby/data/exports/ (JSON exports)
    ↓
KenelmDigby/digby/site/ (8 static HTML pages)
```

## Data Flow

```
Source files (PDF, TXT, MD, EPUB, XLSX, PPTX)
    ↓ 01_ingest.py
source_documents table
    ↓ 02_excerpt.py
source_excerpts table (with page refs)
    ↓ 03_classify.py
source_excerpts (themes assigned)
    ↓ 04_extract.py
life_events, memoir_episodes, work_records,
digby_theme_records, hypnerotomachia_findings,
hypnerotomachia_evidence, citations
    ↓ 05_export.py
JSON files → site HTML
```

## Provenance Model

Every generated record carries:
- `source_method`: DETERMINISTIC | CORPUS_EXTRACTION | LLM_ASSISTED | HUMAN_VERIFIED
- `review_status`: DRAFT | REVIEWED | VERIFIED
- `confidence`: HIGH | MEDIUM | LOW

Rule: never present DRAFT as VERIFIED. Never fabricate without source.

## Tables (9)

| Table | Purpose |
|-------|---------|
| source_documents | Source files in the corpus |
| source_excerpts | Text excerpts with page refs and themes |
| life_events | Biographical events |
| work_records | Digby's works and associated texts |
| memoir_episodes | Structured memoir summary units |
| digby_theme_records | Themed content (pirate, alchemist, courtier) |
| citations | Provenance linking claims to sources |
| hypnerotomachia_findings | Claims about Digby and the HP |
| hypnerotomachia_evidence | Supporting evidence for HP findings |

## Constraints

1. Digby-focused only. No scope expansion.
2. Source evidence required for all substantive claims.
3. Pipeline stages have explicit input/output contracts.
4. Raw evidence stays separate from summaries.
5. No new tables without updating SCHEMA.md.
