# 321 Phase Report: Afternoon Status

**Date:** 2026-03-21 afternoon
**Previous:** HANDOVER320 (morning), HANDOVER321 (midday)

---

## Where We Started Today

This morning we inherited a project with:
- Phases 0-3 complete (BL image reading, coverage mapping, deep readings)
- 141 woodcuts seeded but with known quality issues (orphans, duplicates, wrong pages)
- No reference layer connecting page numbering systems
- 49 Phase 3 deep readings in JSON blobs, not surfaced on the site
- A plan to build a RAG system (deferred after analysis showed it was premature)

## What We Did Today

### Morning: Deep Reading Surfacing + Consolidation
- Surfaced 44 Phase 3 deep readings on marginalia pages (25 existing pages enhanced, 19 new standalone pages)
- Ran Isidore critique, identified 6 data quality issues
- Built `sync_ref_layer.py` and `link_catalog.py` for consolidation
- Upgraded 383 matches MEDIUM->HIGH, 141 woodcuts to REVIEWED
- Deleted 42 orphaned VISION_MODEL entries
- Total marginalia pages: 113 -> 132

### Afternoon: Reference Layer + IA Scan + Catalog Completion
- Built `page_concordance` table: **448 page surfaces** across 3 numbering systems
- Built `woodcut_catalog` table: all **168 entries** from 1896 facsimile catalog
- Downloaded **299 IA page images** (pp.170-468)
- Visually inspected **~120 pages** using Claude Code native vision
- Mapped all 168 catalog entries to pages at HIGH confidence
- Fixed **10 off-by-one page errors** in the Polyandrion section
- Deleted 5 duplicates, merged 13 entries, added 4 new woodcuts
- Fetched 13 new IA images for corrected/added pages
- **Net: 141 -> 127 woodcuts** (fewer rows, every one correct)

---

## Current Inventory

| Asset | Count | Quality |
|-------|-------|---------|
| Woodcuts | 127 | All HIGH confidence, all with IA images |
| Woodcut catalog | 168 | All mapped to pages, all HIGH |
| Page concordance | 448 | 3 numbering systems, verified |
| Image readings | 457 | Phases 1-3 complete |
| Matches (BL offset) | 431 | All HIGH confidence |
| Annotations | 282 | From Russell dissertation |
| Scholars | 65 | Multi-source |
| Dictionary terms | 101 | Multi-source |
| Timeline events | 85 | Multi-source |
| Bibliography | 116 | Multi-source |
| Editions | 8 | From HPDEEPRESEARCH |
| Signature map | 448 | Complete |
| HTML pages | 535 | All generated, site builds cleanly |
| Woodcut images | 162 | IA facsimile JPEGs |

---

## Phase Status (Updated)

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 0: Infrastructure | COMPLETE | Schema v3, all constraints enforced |
| Phase 1: Visual Ground Truth (BL) | COMPLETE | 189/189 photos read |
| Phase 2: Coverage Mapping | COMPLETE | 189/189 density classified |
| Phase 3: Targeted Deep Reading | COMPLETE | 49/49 HEAVY pages read |
| Phase 3.5: Deep Reading Surfacing | COMPLETE | 44 readings on site |
| Phase 3.6: Woodcut Catalog + Reference Layer | COMPLETE | 168/168 mapped |
| Phase 4: Siena Cross-Reference | NOT STARTED | Lower priority |
| Phase 5: Tilton Ingestion | PARKED | Awaiting richer scholarly apparatus |
| Phase 6: Vision Reading Pipeline | PARKED | Awaiting reference layer enrichment |

---

## What's Left to Do (Priority Order)

### Tier 1: Immediate Value (next session)
1. **Russell annotation woodcuts -> Alchemical Hands page** -- The 18 original corpus-extraction entries have scholarly discussion, dictionary links, and annotation data that belongs on the Alchemical Hands page rather than mixed into the general gallery
2. **Wire woodcut_catalog -> woodcuts cross-references** -- The catalog has 168 entries but only ~71 are linked to woodcuts table rows via `woodcut_id`. Completing this linkage enables catalog-number lookups

### Tier 2: Enrichment
3. **Concordance page browser** -- The `page_concordance` table could power a visual page-by-page browser showing IA image + BL photo + woodcut status side by side
4. **Polyandrion gap fill** -- ~15 pages in the 233-260 range were not individually inspected (scanned at 2-page intervals). Some may have additional small epitaph woodcuts
5. **Book II gap fill** -- Similarly, ~20 pages in the 394-450 range might have uncaught woodcuts

### Tier 3: New Sources
6. **Tilton ingestion** -- 13,881-line markdown. Parked until site can receive the enrichment meaningfully
7. **Siena cross-reference (Phase 4)** -- 478 photos to compare against BL baseline
8. **Vision reading pipeline** -- Blind reading of 127 woodcut images, scored against reference descriptions

---

## Key Lessons from Today (from TRIALSANDERRORS.md)

1. File size analysis fails at 600 DPI for woodcut detection
2. Build the concordance table FIRST in any multi-numbering-system project
3. LLM page estimates need visual verification (Polyandrion off-by-one plague)
4. Multiple scholars describing same woodcut create phantom entries
5. Deduplication is addition by subtraction (141 -> 127 = better)
6. Always read the schema before writing to a table (schema drift across sessions)
7. Strategic sampling beats exhaustive scanning for visual identification
8. Test on 10 before building a pipeline for 300

---

## What Changed Since HANDOVER320

| Metric | HANDOVER320 | Now | Change |
|--------|------------|-----|--------|
| Woodcuts | 73 pages on site | 127 pages on site | +54 |
| Woodcut images | 73 | 162 | +89 |
| Total HTML pages | ~400 | 535 | +135 |
| Marginalia pages | 113 | 132 | +19 |
| Deep readings surfaced | 0 | 44 | +44 |
| Match confidence | Mixed MEDIUM/HIGH | All HIGH | Upgraded |
| Page concordance | Did not exist | 448 pages | NEW |
| Woodcut catalog | Did not exist | 168 entries | NEW |
| Orphaned woodcuts | 42 | 0 | Cleaned |
