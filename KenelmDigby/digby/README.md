# Kenelm Digby — Digital Humanities Module

A focused digital humanities project presenting the life, works, and significance
of Sir Kenelm Digby (1603-1665): pirate, alchemist, natural philosopher,
courtier, and annotator of the *Hypnerotomachia Poliphili*.

## Scope

This module produces a **Digby tab** for the HP Marginalia website with 8 pages:

| Page | Content |
|------|---------|
| Digby Home | Overview, significance, navigation |
| Life and Works | Chronological biography, major works, intellectual profile |
| Memoir Summary | Structured episode-by-episode summary of the *Private Memoirs* |
| Pirate | Voyages, privateering, maritime identity |
| Alchemist and Natural Philosopher | Theories, experiments, writings, networks |
| Courtier and Legal Thinker | Court life, patronage, politics, legal thought |
| Digby and the Hypnerotomachia | Russell's research on Digby as the alchemical annotator |
| Sources / Bibliography | All source materials with metadata |

## Source Corpus

47 files in `../` (the parent `KenelmDigby/` folder):
- 1 epub biography (*A Stain in the Blood* by Macleod)
- 1 xlsx cast of characters
- 1 txt (*The Closet of Sir Kenelm Digby*)
- 1 pptx (Russell's HP/Jonson/Digby research)
- 1 md (extracted *Remarkable Voyage*)
- ~40 PDFs (scholarly articles, the *Private Memoirs*, philosophy monograph)

## Pipeline

5-stage pipeline: Ingest → Excerpt → Classify → Extract → Export

```
KenelmDigby/*.pdf,*.md,*.txt
    ↓ 01_ingest.py
db/digby.db → source_documents
    ↓ 02_excerpt.py
source_excerpts (with page refs)
    ↓ 03_classify.py
source_excerpts (with theme labels)
    ↓ 04_extract.py
life_events, memoir_episodes, work_records,
digby_theme_records, hypnerotomachia_findings, citations
    ↓ 05_export.py
data/exports/*.json → site/*.html
```

## Storage

SQLite (`db/digby.db`) with JSON exports for site rendering.
9 tables matching 9 data models. See `docs/SCHEMA.md`.

## Build

```bash
cd KenelmDigby/digby
python src/db.py              # Initialize database
python scripts/01_ingest.py   # Ingest source files
python scripts/05_export.py   # Export JSON for site
python scripts/build_site.py  # Build HTML pages
```

## Status

- [x] Project structure
- [x] Data models (9 types)
- [x] SQLite database (9 tables)
- [x] Validation module
- [x] Pipeline scripts (5 stages)
- [x] Vertical slice with real data
- [x] Website pages (8 HTML)
- [ ] Full memoir episode extraction (future)
- [ ] Complete source corpus ingestion (future)
- [ ] Cross-referencing with main HP Marginalia site (future)
