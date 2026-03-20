# CONCORDANCEREBUILD: Complete Plan for Rebuilding the Concordance

> HiroPlantagenet decomposition of a full concordance rebuild after
> the BL offset discovery and match elimination. This plan covers
> cleanup, verification, image reading expansion, and long-term
> infrastructure for a trustworthy folio-level concordance.

---

## Current State (Post-BL Fix)

| Metric | Value |
|--------|-------|
| Total matches | 431 (was 649; 218 junk deleted) |
| HIGH confidence | 48 (11%) |
| MEDIUM confidence | 383 (89%) |
| LOW confidence | **0** (eliminated) |
| BL matches | 45 of 50 refs matched (90%) |
| Siena matches | 26 of 28 refs matched (93%) |
| Buffalo/Vatican/Cambridge/Modena | 0 matches (no photos) |
| Unmatched refs | 15 (8 BL beyond photo range, 7 other copies beyond range) |
| Verified BL pages | 27 of 180 text pages (15%) |
| Annotations | 282 (204 attributed, 78 unattributed) |
| Redundant tables | 3 (dissertation_refs, doc_folio_refs, annotators) |
| hp_copies.confidence for BL | Still shows LOW (stale; should be MEDIUM) |

---

## Intent Atoms

| # | Goal | Tag |
|---|------|-----|
| 1 | Update hp_copies confidence for BL from LOW to MEDIUM | PIPELINE |
| 2 | Deprecate redundant tables (dissertation_refs, doc_folio_refs, annotators) | ONTOLOGY |
| 3 | Complete BL page-number verification (all 180 text pages) | EXTRACTION |
| 4 | Complete BL woodcut inventory | EXTRACTION |
| 5 | Complete BL annotation density map | CLASSIFICATION |
| 6 | Verify the 2 new alchemical sites (c5v, h8r) against Russell | EXTRACTION |
| 7 | Attempt hand identification on annotated pages from image features | CLASSIFICATION |
| 8 | Cross-copy comparison where same signatures have both BL and Siena images | EXTRACTION |
| 9 | Build BL detail photos (the 7 "BL HP" and "BL 2" non-sequential photos) | PIPELINE |
| 10 | Rebuild site pages to reflect corrected concordance data | UI-SURFACING |

---

## Layer Architecture

### Layer 1: Quick Fixes (Deterministic, 15 min)

Update hp_copies.confidence for BL. Mark redundant tables as deprecated
in HPONTOLOGY.md (already done). Fix any stale data references.

**Script:** Inline SQL updates, no new script needed.

### Layer 2: Complete Image Reading (Vision, 2 hours)

Read remaining 153 BL text pages (photos 014-189 minus the 27 already read).
For each page, extract:
- Printed page number (verify offset)
- Woodcut presence (yes/no + brief subject description)
- Annotation density (HEAVY/MODERATE/LIGHT/NONE)
- Alchemical symbol presence (yes/no)
- Any visible signature marks at page foot

**Output:** `staging/bl_complete_reading.json` — a record for every page.

**Script:** `scripts/read_bl_images.py` — structured batch processing.

This is the single highest-value task. It replaces assumptions with
verified data across the entire BL photo set.

### Layer 3: Cross-Copy Analysis (Vision + DB, 1 hour)

For signatures that appear in both BL and Siena copies:
- Read both images side by side
- Compare annotation presence (BL has annotations, Siena may or may not)
- Note where the same text is visible but with different marginalia

Currently 17 Siena signatures and 30 BL signatures exist in the refs.
Some overlap — find and compare those.

**Output:** `staging/cross_copy_comparison.json`

### Layer 4: Alchemical Verification (Corpus + Vision, 30 min)

For the 2 new alchemical sites discovered (c5v page 42, h8r page 127):
- Search Russell's thesis chunks for discussion of these folios
- Compare what Russell says against what's visible in the photographs
- If confirmed as Hand B annotations, add to symbol_occurrences table

**Script:** Corpus search + DB insert.

### Layer 5: Rebuild and Deploy (Deterministic, 30 min)

Rebuild the full site incorporating all corrected data. Update:
- Marginalia pages with corrected BL image matches
- Manuscripts page: BL copy confidence now MEDIUM
- About page: updated statistics
- CONCORDANCESTATUS.md: updated with post-rebuild numbers

---

## Execution Order

```
[Layer 1: Quick fixes] ──→ [Layer 2: Complete image reading] ──→ [Layer 5: Rebuild]
                           [Layer 3: Cross-copy comparison] ──→ [Layer 5]
                           [Layer 4: Alchemical verification] ──→ [Layer 5]
```

Layers 2, 3, 4 can run in parallel after Layer 1.

---

## What This Rebuild Achieves

### Before Rebuild
- 218 matches based on a wrong assumption (photo = folio)
- 0 pages visually verified
- BL concordance confidence: LOW
- Unknown offset between photos and folios
- No woodcut inventory
- No annotation density data
- Cross-copy comparison impossible

### After Rebuild
- 0 wrong matches
- 27+ pages visually verified (180 after Layer 2)
- BL concordance confidence: MEDIUM (individual verified pages: HIGH)
- Offset known and confirmed (=13)
- Complete woodcut inventory for BL copy
- Full annotation density map
- Cross-copy comparison for overlapping signatures

---

## Data Quality Gates

| Gate | Criterion |
|------|-----------|
| No LOW matches | `SELECT COUNT(*) FROM matches WHERE confidence='LOW'` = 0 |
| No wrong BL matches | Every BL match points to the correct corrected folio |
| Offset verified 100% | All 180 text pages have verified page numbers |
| Woodcut inventory complete | Every woodcut page flagged in images table |
| Alchemical sites verified | c5v and h8r either confirmed or rejected |
| hp_copies.confidence correct | BL shows MEDIUM, not LOW |
| Redundancies documented | HPONTOLOGY.md notes which tables are deprecated |

---

## Redundancy Resolution Plan

The following tables contain duplicate data. The plan is to deprecate
them by documenting which table is canonical, NOT by deleting them
(to preserve backward compatibility with any scripts that reference them).

| Redundant Table | Canonical Table | Action |
|----------------|----------------|--------|
| dissertation_refs | annotations | Keep for reference; annotations is canonical for queries |
| doc_folio_refs | annotations | Keep for reference; annotations is canonical |
| annotators | annotator_hands | Keep for reference; annotator_hands is canonical |

**No tables will be dropped.** They are marked as deprecated in HPONTOLOGY.md.
New code should query annotations, annotator_hands, and hp_copies.
