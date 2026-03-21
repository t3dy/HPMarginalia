# HP320d 10:20pm Report

> Session report covering the last 10 prompts.
> Date: 2026-03-20, approximately 10:20pm.

---

## What Happened

This session executed three major workstreams: annotations migration,
image reading infrastructure, and Phase 1 visual ground truth
extraction. All three completed successfully.

---

## Workstream 1: Annotations Migration (HP320a)

**Goal:** Switch the site builder from the deprecated `dissertation_refs`
table to the canonical `annotations` table.

**What was done:**
- 6 SQL queries in `build_site.py` migrated from `dissertation_refs` to `annotations`
- `annotation_type` (MARGINAL_NOTE, CROSS_REFERENCE, SYMBOL, EMENDATION, INDEX_ENTRY, UNDERLINE) now displays as badges on marginalia pages
- `data.json` gallery data now includes `annotation_type`
- `about.html` stats updated to reference `annotations` and `annotator_hands`
- Two aggregate count queries still use `dissertation_refs` (51 annotations lack `manuscript_id` linkage — documented with TODO)

**Files modified:** `build_site.py`, `export_showcase_data.py`, `build_essay_data.py`
**Site rebuilt:** 232 pages, no errors.

---

## Workstream 2: Image Reading Infrastructure

### Image Path Correction

**Problem discovered:** The `images.relative_path` column pointed to
compressed web copies (`images/bl/...`) instead of the original
high-quality photographs. See `IMAGECONFUSION.md` for the full diagnosis.

**Fix:** Added `master_path` and `web_path` columns to the `images` table.
Backfilled all 674 images. Updated `catalog_images.py` to populate both
paths. Updated all display queries to use `web_path`.

**Files modified:** `catalog_images.py`, `build_site.py`, `export_showcase_data.py`, `build_essay_data.py`, `init_db.py`
**Files created:** `IMAGECONFUSION.md`

### HP320b Image Reading Plan (v1 → v2 → v3)

Three iterations of the image reading plan:

| Version | What Changed |
|---------|-------------|
| v1 | Basic phased plan (Phases 1-4), source boundary warning, cost estimates |
| v2 | Image-source enforcement rules, image reading layer (staging vs table), concordance feedback loop, provenance discipline, multimodal RAG section |
| v3 (HiroPlantagenet) | Phase 0 infrastructure, schema blocker inventory, prose-vs-code enforcement table, shared validation module spec |

**Files created:** `HP320bIMAGEREADINGPLAN.md`

### Phase 0: Infrastructure (Schema v3)

**Migration script:** `migrate_v3_image_reading.py`

| Deliverable | Status |
|------------|--------|
| `image_readings` table (24 columns) | DONE |
| `annotations.source_method` CHECK → accepts `VISION_MODEL` | DONE |
| `matches.confidence` CHECK → accepts `PROVISIONAL` | DONE |
| `woodcuts.source_method` CHECK constraint added | DONE |
| `symbol_occurrences.source_method` CHECK constraint added | DONE |
| `scripts/image_utils.py` shared validation module | DONE |
| Staging directories (`staging/image_readings/bl/phase{1,2,3}/`, `siena/phase4/`) | DONE |
| 30 historical readings backfilled (phase=0) | DONE |
| Schema version → 3 | DONE |

**Files created:** `migrate_v3_image_reading.py`, `backfill_previous_readings.py`, `image_utils.py`

---

## Workstream 3: Phase 1 Visual Ground Truth Extraction

**Goal:** Read all 189 sequential BL photographs. For each, extract:
page number, woodcut presence, page type.

**Method:** Claude Code native vision. Each image was read using the Read
tool from the master image directory (4MB originals, not 200KB web
copies). Results stored via `read_images.py --ingest`.

**Script created:** `scripts/read_images.py`

### Results

| Metric | Value |
|--------|-------|
| Photos processed | 189/189 (100%) |
| Pages with readable page numbers | 174 |
| BL offset confirmed | 174/174 (100%) — zero mismatches |
| BL offset mismatches | 0 |
| Pages without readable numbers | 15 (13 pre-text + 2 full-page woodcuts) |
| Woodcuts detected | 60 |
| Previous woodcut estimate | ~45 (from 27-page sample) |
| Previous woodcuts cataloged in DB | 18 |
| New woodcuts discovered | ~42 beyond what the DB had |
| Alchemical sites confirmed | Page 28 (bellua), Page 42 (Greek inscription) |
| New alchemical site | Page 127 (Synostra Gloria mundi) |

### Woodcut Distribution

| Section | Pages | Woodcuts | Rate |
|---------|-------|----------|------|
| Pre-text | 1-13 | 1 | 8% |
| Early narrative | 1-28 | 12 | 43% |
| Middle text | 29-56 | 4 | 14% |
| Nymphs + palace | 57-84 | 5 | 18% |
| Palace interior | 85-126 | 16 | 38% |
| Post-garden | 127-148 | 4 | 16% |
| **Triumphal procession** | **149-167** | **18** | **95%** |
| Final text | 168-176 | 0 | 0% |

The triumphal procession sequence (pages 149-167) is almost entirely
woodcuts — 18 illustrations in 19 pages, many with multiple panels
per page.

---

## Current Database State

```
db/hp.db: 24 tables, schema version 3

image_readings:  219 rows (30 phase-0 historical + 189 phase-1)
annotations:     282 rows (source_method now accepts VISION_MODEL)
matches:         431 rows (confidence now accepts PROVISIONAL)
woodcuts:        18 rows  (60 more detected, pending promotion)
images:          674 rows (all have master_path + web_path)
```

---

## Files Created This Session

| File | Purpose |
|------|---------|
| `HP320bIMAGEREADINGPLAN.md` | Image reading plan (v3) |
| `HP320cNEXTSTEPS.md` | Next steps after infrastructure |
| `HP320TAKEAWAYS.md` | Findings from Phase 1 in progress |
| `HP320DESCRIPTIONENGINE.md` | Tech inventory for image description |
| `HP320DESCRIPTIONS.md` | Complete BL image inventory (189 photos) |
| `HP320d1020pmREPORT.md` | This report |
| `IMAGECONFUSION.md` | How the pipeline lost track of originals |
| `scripts/read_images.py` | Phase 1 pipeline script |
| `scripts/image_utils.py` | Shared path validation module |
| `scripts/migrate_v3_image_reading.py` | Schema v3 migration |
| `scripts/backfill_previous_readings.py` | Historical readings import |

## Files Modified This Session

| File | What Changed |
|------|-------------|
| `scripts/build_site.py` | annotations migration + web_path |
| `scripts/catalog_images.py` | Dual-path cataloging |
| `scripts/init_db.py` | image_readings table + expanded CHECKs |
| `scripts/export_showcase_data.py` | web_path for display |
| `scripts/build_essay_data.py` | web_path for display |
| `db/hp.db` | Schema v3, 219 image_readings, master_path/web_path |
| `site/` (113+ files) | Rebuilt with annotation_type badges |

---

## What's Next

### Immediate
1. **Commit** — 127 changed files, 9 new files
2. **Update ONTOLOGY.md** — 24th table (image_readings), expanded CHECKs
3. **Update PIPELINE.md** — new scripts in execution order

### Phase 2: Coverage Mapping
- Annotation density classification for all 189 BL photos
- Can combine with Phase 1 prompt to save cost
- Identifies targets for Phase 3

### Woodcut Promotion
- 60 woodcuts detected vs 18 in database
- Review readings, promote ~42 new `woodcuts` rows
- Requires `promote_reading.py` (not yet built)

### Concordance Confidence
- 174 offset confirmations are upgrade candidates
- Corresponding `matches` entries could move MEDIUM → HIGH
- Requires human review per the plan

---

## Key Takeaways

1. **The offset is rock solid.** 174/174 confirmed. The formula
   `page = photo - 13` is now verified across the full range
   of the book with zero exceptions.

2. **Woodcut count was drastically underestimated.** 60 found vs
   45 estimated vs 18 cataloged. The triumphal procession sequence
   alone accounts for 18 woodcuts.

3. **The image source boundary is load-bearing.** Multiple pages
   have faint page numbers and small annotations that would be
   unreadable at 200KB web resolution. The master images at 4MB
   made the difference.

4. **Infrastructure before execution works.** Phase 0 (schema
   migrations, validation module, staging directories) took
   ~1 hour and cost $0. Without it, Phase 1 would have hit
   CHECK constraint failures on first INSERT.

5. **The alchemical annotations are visible.** The Master Mercury
   declaration (photo 3), the "bellua" annotation (photo 41),
   and the "Synostra Gloria mundi" (photo 140) are all readable
   from the master images.
