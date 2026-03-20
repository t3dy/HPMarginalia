# HP Marginalia Project Instructions

## Architecture

- SQLite (`db/hp.db`) is the source of truth (22 tables)
- Python scripts in `scripts/` (41 scripts) generate static HTML/CSS/JS in `site/`
- No framework. No build tools. No JavaScript dependencies.
- GitHub Pages deploys from `site/`

## Current State (as of 2026-03-20)

- **354 pages** across 14 nav tabs
- **94 dictionary terms** across 15 categories, all with significance prose
- **60 scholar pages** (59 with overviews, 11 historical figures tagged)
- **109 bibliography entries**, **113 marginalia folio pages**
- **18 woodcut pages** with descriptions and scholarly context
- **71 timeline events**, **6 manuscript copy pages**
- **2 essay pages** (Russell Alchemical Hands, Concordance Methodology)
- **431 matches** (48 HIGH, 383 MEDIUM, 0 LOW)
- **282 annotations** classified into 6 types
- **10 alchemical symbols**, **26 symbol occurrences**
- BL offset verified (=13) across 27 data points

## Documentation

Read **DOCUMENTATION_INDEX.md** for a categorized guide to all 40+ project documents.

## Key Specs (read before executing)

| Spec | Purpose | Status |
|------|---------|--------|
| `docs/WRITING_TEMPLATES.md` | Prose templates for all page types | **Active** |
| `docs/DECKARD_MARGINALIA_SPEC.md` | Alchemical symbol system | **Executed** |
| `WOODCUTONTOLOGY.md` | Woodcut data model | **Executed** |
| `NEXTPHASE.md` | Current priority plan | **Active** |

## Canonical Tables (use these, not the deprecated ones)

| Canonical | Deprecated | Why |
|-----------|-----------|-----|
| `annotations` | `dissertation_refs`, `doc_folio_refs` | annotations has types + consolidated data |
| `annotator_hands` | `annotators` | annotator_hands has alchemical_framework |
| `hp_copies` | `manuscripts` (for copy-level data) | hp_copies covers all 6 copies |

## Provenance Model

Every generated datum must carry:
- `source_method`: DETERMINISTIC | CORPUS_EXTRACTION | LLM_ASSISTED | HUMAN_VERIFIED
- `review_status`: DRAFT | REVIEWED | VERIFIED | PROVISIONAL
- `confidence`: HIGH | MEDIUM | LOW | PROVISIONAL

Never overwrite VERIFIED content. Never present DRAFT as VERIFIED.

## Build Commands

```
python scripts/build_site.py        # Rebuild all 354 pages
python scripts/dictionary_audit.py  # Check dictionary coverage
python scripts/validate.py          # Full QA
```
