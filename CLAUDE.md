# HP Marginalia Project Instructions

## Architecture

- SQLite (`db/hp.db`) is the source of truth
- Python scripts in `scripts/` generate static HTML/CSS/JS in `site/`
- No framework. No build tools. No JavaScript dependencies.
- GitHub Pages deploys from `site/`

## Current State (as of 2026-03-20)

- **314 pages** across 11 nav tabs
- **94 dictionary terms** across 15 categories, all with significance prose
- **60 scholar pages** (59 with overviews, 11 historical figures tagged)
- **109 bibliography entries**, **118 marginalia folio pages**
- **2 essay pages** (Russell Alchemical Hands, Concordance Methodology)
- **1 digital edition stub**

## Spec Files (read these before executing)

| Spec | Purpose | Status |
|------|---------|--------|
| `docs/WRITING_TEMPLATES.md` | Prose templates for all 10 page types: voice, length, structure, provenance | **Active** — governs all content generation |
| `docs/SCHOLAR_SPEC.md` | Scholar data model, page templates, pipeline | **Executed** |
| `docs/SCHOLAR_PIPELINE.md` | Step-by-step scholar execution guide | **Executed** |
| `docs/TIMELINE_SPEC.md` | Timeline tab: reception history, art, music | **Ready to execute** |
| `docs/MANUSCRIPTS_SPEC.md` | Manuscripts tab: HP copies worldwide, per-copy essays | **Ready to execute** |

## Key Scripts

| Script | Purpose |
|--------|---------|
| `scripts/build_site.py` | Master builder — generates all 314 pages |
| `scripts/corpus_search.py` | Search across /chunks/ and /md/ corpus |
| `scripts/build_reading_packets.py` | Build evidence packets for dictionary terms |
| `scripts/enrich_dictionary.py` | Populate dictionary fields from packets |
| `scripts/link_scholars.py` | Link scholars to bibliography + tag historical figures |
| `scripts/dictionary_audit.py` | Coverage audit for dictionary terms |

## Provenance Model

Every generated datum must carry:
- `source_method`: DETERMINISTIC | CORPUS_EXTRACTION | LLM_ASSISTED | HUMAN_VERIFIED
- `review_status`: DRAFT | REVIEWED | VERIFIED | PROVISIONAL
- `confidence`: HIGH | MEDIUM | LOW | PROVISIONAL

Never overwrite VERIFIED content. Never present DRAFT as VERIFIED.

## Build Commands

```
python scripts/build_site.py        # Rebuild all pages
python scripts/dictionary_audit.py  # Check dictionary coverage
python scripts/validate.py          # Full QA
```

## Next Phases (execute from specs)

1. **Timeline tab** — read `docs/TIMELINE_SPEC.md`, then execute
2. **Manuscripts tab** — read `docs/MANUSCRIPTS_SPEC.md`, then execute
3. **Dictionary expansion** — more HP entity terms can be added via `seed_dictionary_v*.py` pattern
