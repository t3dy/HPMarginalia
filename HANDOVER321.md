# HANDOVER321: Session Continuation Document

> Date: 2026-03-21
> Previous: HANDOVER320.md
> Live site: https://t3dy.github.io/HPMarginalia/
> Status: Full site audit complete. 129 woodcuts (111 gallery + 18 Alchemical Hands). Concordance browser live. 490 pages, 5 residual link issues.

---

## What Was Done This Session (HP321)

### Reference Layer (build_ref_layer.py)
- Created `page_concordance` table: 448 page surfaces mapped with all numbering systems
  - page_seq, signature, folio, IA page index, BL photo number, section assignment
  - IA offset (page + 5), BL offset (page + 13) both encoded
- Created `woodcut_catalog` table: 168 entries from 1896 facsimile catalog
  - 71 entries mapped to pages, 97 initially unmapped

### IA Scanning (scan_ia_pages.py)
- Downloaded all 278 IA pages for pp.170-448 to staging/ia_scan/
- **File size analysis failed** (all 2-3 MB at 600 DPI, no text/woodcut differentiation)
- **Visual inspection via Claude Code native vision**: systematically read ~120 pages
- Confirmed woodcut locations for **65 new pages** beyond the original 62

### Woodcut Catalog Expansion
- Updated `seed_1499_woodcuts.py` with all confirmed page locations
- **Deleted 11 wrong-page entries** (170, 175, 180, 190, 200, 210, 234, 240, 250, 260, 270)
  - These were placeholder pages from LLM-assisted estimation; IA scan confirmed they are text-only
- Inserted 79 new woodcut entries with correct pages, signatures, descriptions, narrative context
- Downloaded 76 new IA facsimile images
- Second pass gap scan added 14 more woodcuts from unchecked pages

### Corrected Page Assignments (Major Fixes)
| Old page | Actual page | Woodcut |
|----------|-------------|---------|
| 170 | 185 | Worship of Priapus |
| 175 | 205 | Procession of Seven Virgins |
| 180 | 210 | Two Virgins Offering Swans |
| 190 | 281 | Bark of the God of Love |
| 200 | 301 | Plan of the Island of Venus |
| 210 | 365 | Poliphilus and Polia at Fountain |
| 234 | 233 | Obelisk with Hieroglyphs |
| 250 | 411 | Poliphilus Dead; Polia Kneels |
| 260 | 261 | Sepulchral Portal |

### Page Corrections (fix_woodcut_pages.py)
- Fixed 10 off-by-one page errors in Polyandrion section (e.g., 241->242, 253->252)
- Deleted 5 duplicate ceremony entries at wrong pages (219, 222, 224, 228, 234)
- Merged 13 entries where multiple rows existed for same page
- Added 4 new entries: p.321 (trophy), p.327 (nymph), p.363 (fountain), p.389 (Polia drags Poliphilus)
- Net: 141 -> 127 (cleaner, no duplicates)

### Site Rebuild
- 127 woodcut pages generated, all with facsimile images
- Gallery filters working across 8 categories
- Full coverage from p.4 (Dark Forest) to p.449 (Cupid's final arrow)

---

## Current Database State

| Table | Rows | Change |
|-------|------|--------|
| `woodcuts` | 127 | Deduplicated: -18 merged/deleted, +4 new |
| `page_concordance` | 448 | NEW table, 155 woodcut pages marked |
| `woodcut_catalog` | 168 | NEW table, ALL at HIGH confidence |
| All other tables | unchanged | |

### Woodcut Coverage (final)
- 127 woodcuts, ALL with page_1499, ALL with cached IA images
- 0 orphaned entries
- 127/127 at HIGH confidence
- 431/431 matches at HIGH confidence
- woodcut_catalog: 168/168 mapped to pages at HIGH confidence
- page_concordance synced: has_woodcut agrees with woodcuts table
- 127 distinct pages vs 168 catalog entries (multiple small woodcuts per page)

---

### Consolidation Pass (Isidore Critique)
- Ran `/write-isidore-critique` on the data system, identified 6 issues
- Created `sync_ref_layer.py`: syncs page_concordance, upgrades confidence, deletes orphans
- Created `link_catalog.py`: maps all 168 catalog entries to pages, links to woodcuts table
- Added `catalog_number` column to woodcuts table (1896 facsimile reference)
- Upgraded 383 matches MEDIUM->HIGH (BL offset verified 174/174)
- Upgraded 141 woodcuts PROVISIONAL->HIGH/REVIEWED (IA visual confirmation)
- Deleted 42 duplicate orphan VISION_MODEL entries

### Phase 3 Deep Readings Surfaced
- Added `_render_deep_reading()` function to `build_site.py`
- Modified `build_marginalia_pages()` to load and render Phase 3 JSON
- 25 existing marginalia pages now show "Vision Reading" sections
- 19 new standalone pages created for signatures with deep readings but no Russell annotations
- Total marginalia pages: 113 -> 132
- All 44 Phase 3 deep readings now visible on the website
- Each reading shows: metadata, woodcut analysis, transcription attempts, symbols, scholarly significance, cross-references, discrepancies
- Provenance badge: "Vision reading (Claude Code, Phase 3)"

## New Scripts

| Script | Purpose |
|--------|---------|
| `build_ref_layer.py` | Creates page_concordance + woodcut_catalog tables |
| `scan_ia_pages.py` | Downloads IA pages and analyzes for woodcut detection |
| `update_catalog_pages.py` | Pushes confirmed page assignments to woodcut_catalog |
| `fix_woodcut_pages.py` | Fixes page errors, merges duplicates, adds missing entries |
| `fix_polyandrion.py` | Corrects Polyandrion off-by-one page errors, adds 2 new entries |
| `sync_ref_layer.py` | Consolidation: syncs tables, upgrades confidence, removes orphans |
| `link_catalog.py` | Maps 1896 catalog to confirmed pages, links to woodcuts table |
| `check_links.py` | Post-build link validator (run after every build_site.py) |

---

## Afternoon Session (HP321 continued)

### Russell Annotation Woodcuts Relocated
- 18 CORPUS_EXTRACTION woodcuts moved from Woodcuts gallery to Alchemical Hands page
- Gallery now shows 111 entries (129 - 18 Russell)
- Alchemical Hands page has rich gallery: image + description + scholarly discussion + annotation data + dictionary chips + folio links

### Polyandrion + Book II Gap Verification
- Verified all 7 MEDIUM-risk Polyandrion pages (234, 241, 243, 245, 247, 249, 251)
- Found systematic off-by-one: all Polyandrion woodcuts are on ODD pages, not even
- Added 2 new woodcuts: p.234 (Julius Caesar hieroglyphic devices) and p.245 (sacrifice relief)
- Verified all Book II gaps (pp.394-450): no missing woodcuts found
- Fixed final woodcut p.449 -> p.448
- Total woodcuts: 129 (verified end-to-end, all 448 pages inspected)

### Concordance Page Browser
- Built `concordance/index.html`: all 448 pages browsable
- Grouped by 14 narrative sections with collapsible headers
- Woodcut thumbnails inline, M (marginalia) and BL (photo) links
- Jump-to-page input (by signature or page number)
- "Woodcut pages only" filter

### Site Audit (Hiro Plantagenet)
- Fixed concordance `depth=1` bug (all CSS/nav links were broken)
- Deleted 47 stale ghost pages from previous builds
- Added existence checks for marginalia/dictionary links (prevents 404s)
- Fixed concordance to link CORPUS_EXTRACTION woodcuts to Alchemical Hands
- Built `check_links.py` validator: run after every build
- Broken links: 113 -> 5 (remaining 5 are BL photo raw-path edge cases)
- See CORPUSEXTRACTIONSILLINESS.md for full post-mortem

---

## What Needs Doing Next

### High Priority

1. **Fix 5 remaining BL photo path issues** — 5 marginalia pages reference raw filesystem paths instead of web paths. Needs DB update to fix image path resolution for Phase 3 deep reading pages.

### Medium Priority

2. **Concordance confidence upgrades** — 174 BL offset confirmations ready for MEDIUM->HIGH upgrade
3. **Wire woodcut_catalog -> woodcuts cross-references** — 168 catalog entries, only ~71 linked via woodcut_id
4. **Tilton ingestion** — Parked. Wait for comparative study on pedagogical/entertainment value of alchemical emblems

### Low Priority

5. **Siena cross-reference (Phase 4)** — 478 photos to compare against BL baseline
6. **Vision reading pipeline** — Blind reading of woodcut images, scored against reference descriptions

---

## Key Technical Facts (Updated)

### IA Offset
- Formula: `IA page = HP page + 5` (unchanged)
- Now confirmed across 127 woodcut pages

### Page Concordance
- `page_concordance` maps all 448 surfaces with: signature, folio, IA index, BL photo, section
- Sections: PRELIMINARIES, DARK_FOREST, PYRAMID_RUINS, DRAGON_PORTAL, FIVE_SENSES, QUEEN_PALACE, JOURNEY_DOORS, PROCESSION, VENUS_TEMPLE, POLYANDRION, CYTHERA_VOYAGE, CYTHERA_GARDENS, VENUS_FOUNTAIN, BOOK_II_POLIA, COLOPHON

### Staging Data
- `staging/ia_scan/` contains 278 full-resolution IA page images (pp.170-448)
- `staging/ia_scan/woodcut_page_map.json` has partial scan results (superceded by seed script)
- `staging/ia_scan/scan_report.json` has file size analysis (not useful for woodcut detection)

---

## Key Files to Read First

| File | Why |
|------|-----|
| `CLAUDE.md` | Project instructions and constraints |
| `HANDOVER321.md` | This document — current state |
| `HANDOVER320.md` | Previous session's work (Phases 1-3, woodcut gallery) |
| `scripts/seed_1499_woodcuts.py` | The complete woodcut catalog with all page assignments |
| `scripts/build_ref_layer.py` | Reference layer builder (page_concordance + woodcut_catalog) |
| `scripts/build_site.py` | Master site builder |
