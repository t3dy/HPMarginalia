# Kenelm Digby Module — Agent Instructions

## Scope

This module is about **Sir Kenelm Digby (1603-1665)** and only him.

## Rules

1. **Stay focused on Digby.** Do not expand into general Renaissance studies,
   other figures, or unrelated subsystems.
2. **Do not fabricate biography.** Every biographical claim must cite a source
   from the corpus in `../` (the parent KenelmDigby folder).
3. **Require evidence and citations.** No structured record without provenance.
   Every LifeEvent, MemoirEpisode, DigbyThemeRecord, and HypnerotomachiaFinding
   must have at least one Citation attached.
4. **Distinguish source evidence from interpretation.** Use `source_method`
   and `review_status` fields honestly. DRAFT means unverified.
5. **Validate outputs before declaring success.** Run validate.py on all
   records before committing them to the database.
6. **No feature creep.** If a new idea emerges, park it — do not build it.
7. **Reality over design.** The database is the source of truth, not docs.

## Source Corpus

47 files in `../` — PDFs, one epub, one txt, one xlsx, one pptx, one md.
Key sources:
- *Private Memoirs* (1827 PDF) — primary for memoir episodes
- *The Remarkable Voyage* (Macleod, .md and .pdf) — primary for biography
- Dobbs articles (Ambix) — primary for alchemy
- Moshenska article — primary for piracy
- Wyndham Miles (Chymia) — primary for overview
- Russell PPTX — primary for Hypnerotomachia connection

## Data Model

9 record types in `src/models.py`. 9 tables in `db/digby.db`.
See `docs/SCHEMA.md` for field definitions.

## Pipeline

5 scripts in `scripts/`: ingest, excerpt, classify, extract, export.
See `docs/PIPELINE.md` for contracts.

## Build

```bash
python src/db.py              # Init DB
python scripts/01_ingest.py   # Ingest sources
python scripts/05_export.py   # Export JSON
python scripts/build_site.py  # Build HTML
```

## Constraints

- Do not modify the parent HP Marginalia database
- Do not write directly to site/ without going through the pipeline
- Do not add tables without updating SCHEMA.md
- Do not skip validation
