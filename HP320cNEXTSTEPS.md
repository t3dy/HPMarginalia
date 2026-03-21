# HP320c: Next Steps

> Generated: 2026-03-20
> Follows: HP320a (annotations migration), HP320b (image reading plan),
> Phase 0 (infrastructure)

---

## What Was Done This Session

### HP320a: Annotations Migration
Switched `build_site.py` from the deprecated `dissertation_refs` table to
the canonical `annotations` table. Six queries migrated. `annotation_type`
(MARGINAL_NOTE, CROSS_REFERENCE, SYMBOL, etc.) now displays on marginalia
pages and in gallery data. Site rebuilds cleanly.

### Image Path Correction
Added `master_path` and `web_path` columns to the `images` table.
Backfilled all 674 images. `master_path` points to original high-quality
photographs (~4MB BL, ~500KB Siena). `web_path` points to compressed
site copies (~200KB BL). Display code uses `web_path`; all future
analysis code must use `master_path`. See `IMAGECONFUSION.md` for the
diagnosis of how the confusion arose.

### HP320b: Image Reading Plan (v3)
Wrote and revised the image reading plan through three iterations:
- v1: Basic phased plan
- v2: Added image-source boundary, staging layer, concordance feedback loop
- v3 (HiroPlantagenet audit): Added Phase 0 infrastructure, identified
  schema blockers, distinguished prose rules from code enforcement

### Phase 0: Infrastructure (COMPLETE)
Built everything the image reading pipeline depends on:

| Deliverable | Status |
|------------|--------|
| `image_readings` table (24 columns, CHECK constraints) | DONE |
| `annotations.source_method` accepts `VISION_MODEL` | DONE |
| `matches.confidence` accepts `PROVISIONAL` | DONE |
| `woodcuts.source_method` CHECK constraint added | DONE |
| `symbol_occurrences.source_method` CHECK constraint added | DONE |
| `scripts/image_utils.py` (shared path validation) | DONE |
| `staging/image_readings/` directories | DONE |
| 30 previous readings backfilled (phase=0) | DONE |
| Schema version: 3 | DONE |

---

## Current State

```
db/hp.db: 24 tables, schema version 3
  image_readings: 30 rows (24 CONFIRMED, 6 UNVERIFIED)
  annotations: 282 rows (source_method accepts VISION_MODEL)
  matches: 431 rows (confidence accepts PROVISIONAL)
  images: 674 (all have master_path + web_path)
    BL PAGE images: 180 (ready for Phase 1)
    BL total images: 196

scripts/image_utils.py: tested, exports resolve_master_path(),
  assert_not_web_derivative(), assert_master_dirs_exist(), get_master_images()

staging/image_readings/: bl/phase{1,2,3}/, siena/phase4/ exist

Site: builds cleanly, all 232 pages generated
Git: 123 changed files (5 new), uncommitted
```

---

## What Needs Doing Next

### Immediate (commit and deploy)

**1. Commit this session's work.**
123 files changed. Key changes:
- `build_site.py`: annotations migration + web_path queries
- `catalog_images.py`: dual-path image cataloging
- `init_db.py`: updated schema with image_readings + expanded CHECKs
- New: `migrate_v3_image_reading.py`, `backfill_previous_readings.py`,
  `image_utils.py`
- New: `HP320bIMAGEREADINGPLAN.md`, `IMAGECONFUSION.md`
- Site HTML rebuilt with annotation_type badges

**2. Update ONTOLOGY.md.**
The schema has changed. `image_readings` is now a real table (24th table).
`annotations`, `matches`, `woodcuts`, `symbol_occurrences` all have
expanded CHECK constraints. ONTOLOGY.md needs to reflect this.

**3. Update PIPELINE.md.**
New scripts: `migrate_v3_image_reading.py`, `backfill_previous_readings.py`,
`image_utils.py`. These need to appear in the pipeline documentation.

### Phase 1: Visual Ground Truth (next build task)

**What:** Send all 196 BL master images to Claude Vision API. For each,
extract page number, woodcut presence, and page type.

**Prerequisites (all met):**
- [x] `image_readings` table exists
- [x] `images.master_path` populated for all 674 images
- [x] `image_utils.py` provides path validation
- [x] Staging directories exist
- [ ] Claude API key with vision capability (~$2-3 budget)
- [ ] `anthropic` Python SDK installed
- [ ] `scripts/read_images.py` written

**Build order:**
1. Write `read_images.py` (the batch reader script)
2. Dry-run to verify paths and prompts
3. Execute Phase 1 on BL images
4. Write `compare_readings.py` (the concordance comparison script)
5. Run comparison, generate discrepancy report
6. Human review of discrepancies

**Expected output:**
- 196 rows in `image_readings` (phase=1)
- 196 raw JSON files in `staging/image_readings/bl/phase1/`
- Ground-truth folio mapping for every BL photo
- Complete woodcut inventory (~45 expected)
- Discrepancy report

**Estimated cost:** ~$2-3
**Estimated time:** ~2 hours (1 hour coding, 1 hour execution)

### Phase 2: Coverage Mapping (after Phase 1)

**What:** For each BL photo, detect annotation presence, density, locations,
and languages.

**Can combine with Phase 1** to save API cost — one call per image
extracting both Phase 1 and Phase 2 data. If combined, insert two
`image_readings` rows per image (one per phase) from the same API response.

**Expected output:**
- 196 rows in `image_readings` (phase=2)
- Full annotation density map
- List of annotated pages Russell did not document
- Targeting data for Phase 3

**Estimated cost:** ~$3 (or ~$0 if combined with Phase 1)

### Phase 3: Targeted Deep Reading (after Phase 2)

**What:** Opus-quality deep reading of ~20 key folios selected from
Phase 2 density rankings + Russell's documented alchemical sites.

**Depends on:** Phase 2 results to select targets.

**Estimated cost:** ~$5

### Other Ready Tasks (from ROADMAP.md)

These do not depend on image reading and can be done independently:

| Task | Effort | Priority |
|------|--------|----------|
| Add coverage caveats to about.html and concordance-method.html | 15 min | HIGH |
| Add annotation type filtering to marginalia index | 30 min | MEDIUM |
| Add inline dictionary links in essays (~40 links) | 1 hour | MEDIUM |
| Backfill `manuscript_id` on 51 annotations missing it | 30 min | MEDIUM |
| Phase 8 of original prompt: full QC pass | 2 hours | LOW |

### Deferred (not blocked, just lower priority)

- Phase 4: Siena cross-reference (after Phases 1-3)
- Multimodal RAG layer (after Phases 1-3 produce structured data)
- Scholar-to-content reverse links
- Progressive disclosure on landing pages
- Acquire photographs of 4 remaining copies (Buffalo, Vatican, Cambridge, Modena)

---

## Decision Needed

**Option A vs Option B for image reading layer:**

The plan recommends Option A (dedicated `image_readings` table) and
Phase 0 implemented it. But the plan says this is a decision point.

If you want to proceed with Option A (already built), no action needed.
If you want Option B (file-based staging only), the `image_readings`
table can be dropped and `read_images.py` would write to staging files
with a separate review-state tracker.

**Recommendation:** Keep Option A. The table exists, is populated with
30 historical readings, and is queryable by SQL. The infrastructure cost
is already paid.

---

## Files Created This Session

| File | Purpose |
|------|---------|
| `HP320bIMAGEREADINGPLAN.md` | Image reading plan (v3, with Phase 0 + HiroPlantagenet corrections) |
| `HP320cNEXTSTEPS.md` | This document |
| `IMAGECONFUSION.md` | Diagnosis of how the pipeline lost track of original images |
| `scripts/migrate_v3_image_reading.py` | Migration v3: image_readings table + CHECK expansions |
| `scripts/backfill_previous_readings.py` | Import 30 historical readings into image_readings |
| `scripts/image_utils.py` | Shared path validation (resolve_master_path, assert_not_web_derivative, etc.) |

## Files Modified This Session

| File | What Changed |
|------|-------------|
| `scripts/build_site.py` | Switched from dissertation_refs to annotations; web_path for display |
| `scripts/catalog_images.py` | Dual-path cataloging (master_path + web_path) |
| `scripts/init_db.py` | Added image_readings table, expanded CHECK constraints |
| `scripts/export_showcase_data.py` | web_path for display |
| `scripts/build_essay_data.py` | web_path for display |
| `db/hp.db` | Schema v3, master_path/web_path backfilled, 30 image_readings rows |
| `site/` | Rebuilt with annotation_type badges on marginalia pages |
