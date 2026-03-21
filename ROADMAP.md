# ROADMAP: Execution Tasks Only

> No speculative features. Every item is either BUILT, READY (can execute
> now from existing data), or BLOCKED (requires external resources).
> Tagged per the Antigravity constraint: surface before ingest.

## BUILT (completed, deployed)

- [x] Concordance pipeline (282 refs → 431 matches, 0 LOW)
- [x] BL offset correction (=13, verified at 174/174 readable pages by Phase 1)
- [x] Dictionary (94 terms, 15 categories, all with significance prose)
- [x] Scholars (60 pages, 59 overviews, 11 historical figures)
- [x] Bibliography (109 entries)
- [x] Timeline (71 events, filterable)
- [x] Manuscripts (6 copies with hand profiles)
- [x] Woodcuts (18 in canonical table; 60 detected by Phase 1 vision reading)
- [x] Alchemical symbols (10 symbols, 26 occurrences)
- [x] Annotation classification (282 annotations, 6 types)
- [x] Russell essay + Concordance essay
- [x] Digital edition stub
- [x] 14-tab navigation across 365 pages
- [x] Annotations migration (build_site.py uses annotations, not dissertation_refs)
- [x] Image path correction (master_path + web_path on all 674 images)
- [x] Phase 0 infrastructure (image_readings table, schema v3, image_utils.py)
- [x] Phase 1 BL ground truth (189/189 photos read, 60 woodcuts, offset confirmed)
- [x] Documentation consolidation (5 core docs)

## READY (can execute now, no new research needed)

### ~~Priority 1: Switch marginalia pages to annotations table~~ DONE (HP320a)

### Priority 1 (new): Add coverage caveats to site
**What:** Update about.html and concordance-method.html to state clearly that
image matches exist for 2 of 6 copies, and that 4 copies have text-only evidence.
**Effort:** 15 minutes.

### ~~Priority 3: Read remaining BL photographs~~ DONE (Phase 1)
All 189 sequential BL photos read. 60 woodcuts detected. See PHASESTATUS.md.

### Priority 2 (new): Phase 2 Coverage Mapping
**What:** Classify annotation density (LIGHT/MODERATE/HEAVY) for all 189 BL
photos. Map annotation locations and languages.
**Why:** Identifies targets for Phase 3 deep reading.
**Effort:** ~2 hours (same Claude Code vision workflow as Phase 1).

### Priority 3 (new): Woodcut Promotion
**What:** Review 60 detected woodcuts, promote qualifying entries to canonical
`woodcuts` table via promote_reading.py (to be built).
**Effort:** 1 hour (build script) + review time.

### Priority 4: Add annotation type filtering to marginalia index
**What:** Add filter buttons (like timeline) to marginalia/index.html so
visitors can filter by MARGINAL_NOTE, CROSS_REFERENCE, SYMBOL, etc.
**Effort:** 30 minutes.

## BLOCKED (requires external resources)

### Acquire photographs of 4 remaining copies
Buffalo RBR, Vatican Chig.II.610, Cambridge INCUN A.5.13, Modena (Panini)
have no photographs. All 163 dissertation references for these copies
are text-only. **Blocked by:** institutional access.

### High-resolution BL images
Current BL photos are adequate for page numbers and woodcut detection
but insufficient for handwriting transcription or ideogram identification.
**Blocked by:** BL digital services.

### Full 172-woodcut inventory from 1499 facsimile
The complete inventory requires a digitized 1499 edition (available at
Carnegie Mellon Posner Center or Internet Archive). Our BL photos cover
only pages 1-176 (38% of the book). **Blocked by:** systematic facsimile reading.

## SPECULATIVE (ideas, not commitments)

These are documented in archived docs but are NOT execution commitments:

- Multi-panel manuscript viewer with deep zoom (from HPMIT.md)
- Parallel translation interface (from HPMIT.md)
- Citation network graph (from HPSCHOLARS.md)
- IIIF manifest generation (from HPMULTIMODAL.md)
- Full HP text transcription
- Cross-copy annotation comparison tool

**Rule:** None of these should be started until all READY items are complete.
