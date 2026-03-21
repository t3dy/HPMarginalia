# HPREFLAYER: Reference Layer Database Design

> Status: DESIGN DOCUMENT
> Date: 2026-03-21
> Purpose: Unified concordance between all HP source numbering systems

---

## The Problem

The HP project uses at least **six independent numbering systems** that don't map to each other:

| System | Range | Where Used |
|--------|-------|------------|
| IA scan index | n0–n468 | Internet Archive facsimile (A336080v1) |
| HP 1499 page | 1–~460 | `woodcuts.page_1499`, IA offset formula |
| Signature | a1r–F4v | `woodcuts.signature_1499`, `signature_map` |
| Folio number | 1–224 | `signature_map.folio_number` |
| BL photo number | 1–196 | `images.sort_order` (manuscript_id=1) |
| Woodcut catalog number | 1–168 | 1896 facsimile (not yet in DB) |

**Current pain points:**

1. **Woodcut completion is blocked.** 73 of 168 woodcuts are cataloged. Adding the remaining 95 requires knowing their 1499 page numbers, which requires cross-referencing signatures, IA pages, and narrative sequence. No unified lookup exists.

2. **Signature assignments are unreliable.** The `signature_1499` values in the woodcuts table were LLM-assigned and contain errors (e.g., p.16 labeled "b2v" should be "a8v" based on folio arithmetic).

3. **BL-to-1499 mapping is implicit.** The BL offset formula (`page = photo - 13`) is confirmed but not materialized in a table. You have to compute it every time.

4. **No path from facsimile catalog to database.** The 1896 "Dream of Poliphilus" catalogs all 168 woodcuts with numbered descriptions but no page references. Mapping #71–#168 to 1499 pages requires narrative analysis.

5. **Cross-copy comparison is unmapped.** Siena photos have no page-number linkage to 1499 pages.

---

## Proposed Solution: `page_concordance` Table

A single reference table that maps every page surface of the 1499 edition to all other numbering systems.

### Schema

```sql
CREATE TABLE page_concordance (
    id INTEGER PRIMARY KEY,

    -- 1499 Aldine edition (canonical reference)
    page_seq INTEGER UNIQUE NOT NULL,     -- Sequential page surface (1-460)
    signature TEXT,                         -- Quire signature (a1r, b3v, etc.)
    folio_number INTEGER,                  -- Leaf number (1-224)
    side TEXT CHECK(side IN ('r', 'v')),   -- Recto or verso
    quire TEXT,                            -- Quire letter (a-y, z, A-G)
    leaf_in_quire INTEGER,                 -- Position within quire (1-8)

    -- Internet Archive (University of Seville copy, A336080v1)
    ia_page_index INTEGER,                 -- IA page number (n0-n468)

    -- BL C.60.o.12 (1545 edition, but page-for-page reprint)
    bl_photo_number INTEGER,               -- BL photograph number (1-196)
    bl_photo_has_content BOOLEAN,          -- Whether this page is within BL photo range

    -- Siena Biblioteca Comunale (when mapped)
    siena_photo_number INTEGER,

    -- Content classification
    has_woodcut BOOLEAN DEFAULT 0,         -- Page contains a woodcut illustration
    woodcut_catalog_number INTEGER,        -- 1896 facsimile catalog number (1-168)
    has_text BOOLEAN DEFAULT 1,            -- Page contains printed text
    is_full_page_woodcut BOOLEAN DEFAULT 0,-- Woodcut fills entire page
    section TEXT,                           -- Narrative section label

    -- Provenance
    source_method TEXT DEFAULT 'COMPUTED',
    confidence TEXT DEFAULT 'HIGH',
    verified BOOLEAN DEFAULT 0,
    notes TEXT
);
```

### Key Relationships

```
page_concordance.page_seq  ←→  woodcuts.page_1499
page_concordance.signature ←→  signature_map.signature
page_concordance.bl_photo_number ←→  images.sort_order (WHERE manuscript_id=1)
page_concordance.ia_page_index  =   page_seq + 5  (IA offset formula)
page_concordance.woodcut_catalog_number ←→ woodcut_catalog.catalog_number (new table)
```

---

## Supporting Table: `woodcut_catalog`

The 1896 facsimile provides a canonical numbered catalog of all 168 HP woodcuts. This should be a first-class table.

```sql
CREATE TABLE woodcut_catalog (
    id INTEGER PRIMARY KEY,
    catalog_number INTEGER UNIQUE NOT NULL,  -- 1-168 from 1896 facsimile
    description TEXT NOT NULL,                -- From "Descriptive List"
    page_seq INTEGER,                         -- Links to page_concordance
    woodcut_id INTEGER,                       -- Links to woodcuts table (when matched)
    subject_category TEXT,
    is_full_page BOOLEAN DEFAULT 0,
    is_decorative BOOLEAN DEFAULT 0,          -- Small ornamental cut vs narrative
    narrative_section TEXT,                    -- Which part of the HP story

    -- Source
    source TEXT DEFAULT '1896_FACSIMILE',
    confidence TEXT DEFAULT 'HIGH',

    FOREIGN KEY (page_seq) REFERENCES page_concordance(page_seq),
    FOREIGN KEY (woodcut_id) REFERENCES woodcuts(id)
);
```

---

## Populating the Reference Layer

### Step 1: Build `page_concordance` from `signature_map` (deterministic)

The existing `signature_map` (448 rows) already maps signatures to folio numbers. Convert to page_seq:

```python
page_seq = (folio_number - 1) * 2 + (1 if side == 'r' else 2)
ia_page_index = page_seq + IA_OFFSET  # IA_OFFSET = 5 (verified at 174 points)
```

For BL photos, apply the inverse offset:
```python
bl_photo_number = page_seq + 13  # BL offset (photo = page + 13)
# Only valid for pages within BL photo range (~pages 1-176)
```

**Confidence: HIGH** — both offset formulas are empirically verified.

### Step 2: Seed `woodcut_catalog` from 1896 facsimile (deterministic)

The 168 entries with descriptions are known. Catalog numbers are sequential and stable. Page_seq assignments for #1–#70 can be derived from existing woodcuts table. For #71–#168, initial population requires narrative-based estimation.

**Confidence: HIGH for catalog entries, MEDIUM for page assignments.**

### Step 3: Cross-reference BL vision readings (automated)

Phase 1 detected 60 woodcuts across 189 BL photos. Map these to page_concordance:
```sql
UPDATE page_concordance
SET has_woodcut = 1
WHERE page_seq IN (
    SELECT ir.page_number_read
    FROM image_readings ir
    WHERE ir.phase = 1 AND ir.has_woodcut = 1
);
```

### Step 4: IA page-by-page verification (semi-automated)

For the ~290 pages not covered by BL photos (pages 177–460), download IA images and classify:
- **Automated pre-filter:** Compare file sizes. Woodcut pages produce larger JPEG files than text-only pages.
- **Vision confirmation:** Read candidate pages via Claude Code native vision to confirm woodcut presence and identify subject.

---

## Narrative Section Map

The HP divides into well-documented narrative sections. Assigning section labels to `page_concordance` rows enables filtering and navigation.

| Section | Approx Pages | Woodcut Density | Content |
|---------|-------------|-----------------|---------|
| `DARK_FOREST` | 1–15 | Low | Poliphilo enters dream, finds forest |
| `PYRAMID_RUINS` | 16–37 | High | Great pyramid, horse, elephant, inscriptions |
| `DRAGON_PORTAL` | 38–62 | Medium | Portal, temple ruins, dragon, medallions |
| `FIVE_SENSES` | 63–79 | Medium | Nymphs, fountains, bathing |
| `QUEEN_PALACE` | 80–105 | High | Eleuterylida's palace, decorative objects |
| `JOURNEY_DOORS` | 106–139 | Medium | Obelisk, three doors, garden scenes |
| `PROCESSION` | 149–167 | Very high | Six triumphal chariots, 20+ woodcuts |
| `VENUS_TEMPLE` | 168–185 | High | Priapus, temple ceremony, miracle of roses |
| `POLYANDRION` | 186–215 | Very high | Cemetery, 27 epitaphs and monuments |
| `CYTHERA_VOYAGE` | 216–220 | Low | Bark of love, sea crossing |
| `CYTHERA_GARDENS` | 221–255 | High | Topiary, flower beds, trophies, amphitheater |
| `VENUS_FOUNTAIN` | 256–270 | Medium | Fountain, statue, tomb of Adonis |
| `BOOK_II_POLIA` | 271–400+ | Low | Polia's narrative, 17 woodcuts spread thinly |
| `COLOPHON` | 450–460 | None | Printer's colophon and errata |

**Note:** Page ranges are approximate and will be refined as the reference layer is populated.

---

## How This Solves the Woodcut Problem

### Current workflow (broken):
1. Know a woodcut exists from narrative context
2. Guess its 1499 page number
3. Hope the IA offset works for the guessed page
4. Download and check
5. Repeat if wrong

### With reference layer:
1. Look up woodcut by catalog number (#71–#168) in `woodcut_catalog`
2. Get its `page_seq` from the concordance
3. Compute `ia_page_index = page_seq + 5`
4. Download the correct IA image
5. Verify once

### For the immediate task (completing 168 woodcuts):
1. Pre-populate `page_concordance` from `signature_map` (448 rows, 5 minutes)
2. Seed `woodcut_catalog` with all 168 entries from 1896 descriptions
3. Assign page_seq for entries #1–#70 from existing woodcuts table
4. For entries #71–#168, run IA page scanner to identify woodcut pages in the range n180–n468
5. Match scanner results to catalog entries by narrative sequence
6. Update woodcuts table with confirmed page numbers

---

## Implementation Plan

### Phase A: Schema + Deterministic Population (1 session)
- [ ] Create `page_concordance` table
- [ ] Populate from `signature_map` (448 rows)
- [ ] Compute and set `ia_page_index` for all rows
- [ ] Compute and set `bl_photo_number` for BL-covered pages
- [ ] Mark `has_woodcut` from existing woodcuts table
- [ ] Create `woodcut_catalog` table
- [ ] Seed 168 entries from 1896 facsimile descriptions
- [ ] Link entries #1–#70 to known page_seq values

### Phase B: IA Scanner (1 session)
- [ ] Write `scan_ia_pages.py` — downloads IA pages in bulk, logs file sizes
- [ ] Identify candidate woodcut pages (large file sizes)
- [ ] Vision-confirm candidates in batches
- [ ] Update `page_concordance.has_woodcut` and `woodcut_catalog.page_seq`

### Phase C: Woodcut Completion (1 session)
- [ ] Map all 168 catalog entries to confirmed page_seq values
- [ ] Update `seed_1499_woodcuts.py` with complete inventory
- [ ] Run seed, fetch images, rebuild site
- [ ] Gallery grows from 73 → 168 woodcuts

### Phase D: Cross-Copy Integration (future)
- [ ] Map Siena photos to `page_concordance`
- [ ] Enable cross-copy woodcut comparison
- [ ] Link annotation locations to concordance

---

## What This Is NOT

- **Not a new website section.** The reference layer is infrastructure — it lives in the database and serves scripts.
- **Not a replacement for existing tables.** `woodcuts`, `images`, `signature_map` remain canonical. The concordance links them.
- **Not a scope expansion.** This is the minimum viable reference system needed to complete the woodcut catalog and enable cross-copy comparison.

---

## Dependencies

| Requirement | Status |
|-------------|--------|
| `signature_map` table (448 rows) | EXISTS |
| IA offset formula (verified) | CONFIRMED |
| BL offset formula (verified) | CONFIRMED |
| 1896 facsimile text (168 descriptions) | AVAILABLE (IA) |
| Existing woodcuts table (73 with page_1499) | EXISTS |
| Phase 1 vision readings (60 woodcut detections) | EXISTS |

All prerequisites are met. No external dependencies.

---

## Open Questions

1. **Should `page_concordance` include the 4 preliminary (π) leaves?** They contain the Aldine device and title page but no narrative woodcuts. Recommendation: include them with `section = 'PRELIMINARIES'`.

2. **How to handle multi-woodcut pages?** Some pages (especially in the procession) contain 2–3 stacked woodcut panels. The concordance marks the page as `has_woodcut = 1`; the `woodcut_catalog` handles individual cuts via multiple rows pointing to the same `page_seq`.

3. **Should the BL 1545 edition mapping account for textual differences?** The 1545 is a page-for-page reprint, so the mapping is 1:1 for the first ~230 pages. Book II may have minor differences. For now, treat as identical.

4. **Signature validation.** The `signature_map` table has 448 entries across 29 quires. The bibliographic collation formula (π⁴ a–y⁸ z¹⁰ A–E⁸ F⁴) predicts 468 page surfaces. The 20-page discrepancy suggests either the π leaves are excluded and the quire sizes don't match the formula exactly, or the formula was entered slightly incorrectly. This should be audited.
