# HP320 DESCRIPTION ENGINE: Technical Inventory for Image Analysis

> What tools exist, what they do, and how they connect.
> Date: 2026-03-20

---

## Overview

The HP Marginalia project has built a pipeline for reading, describing,
and storing structured observations about manuscript photographs. This
document inventories every component — what exists, what it does, and
where it fits.

---

## 1. Image Storage Infrastructure

### Dual-Path System

Every image in the database carries two paths:

| Column | Points To | Used By |
|--------|----------|---------|
| `images.master_path` | Original high-quality photograph (BL: ~4MB, Siena: ~500KB) | All analysis, vision reading, verification |
| `images.web_path` | Compressed display copy (BL: ~200KB, Siena: ~500KB) | HTML `<img>` tags, gallery display only |

**Built by:** `catalog_images.py` (reads from `manuscripts.image_dir`)
**Enforced by:** `image_utils.py` (shared validation module)

### Source Collections

| Collection | Location | Files | Resolution | Status |
|-----------|---------|-------|-----------|--------|
| BL C.60.o.12 originals | `3 BL C.60.o.12 Photos.../` | 196 | ~4MB each | AVAILABLE, all master_paths populated |
| Siena O.III.38 originals | `Siena O.III.38 Digital Facsimile.../` | 478 | ~500KB each | AVAILABLE, all master_paths populated |
| BL compressed (web) | `site/images/bl/` | 196 | ~200KB each | Display only |
| Siena copy (web) | `site/images/siena/` | 478 | ~500KB each | Display only (identical to originals) |

### Path Validation Module: `scripts/image_utils.py`

Shared Python module imported by all image-touching scripts.

```python
resolve_master_path(conn, image_id) -> Path
    # Returns absolute path to the master image. Raises if missing.

assert_not_web_derivative(path)
    # Raises ValueError if path is under site/images/.

assert_master_dirs_exist(conn)
    # Checks all manuscript.image_dir directories exist. Exits if not.

get_master_images(conn, shelfmark, page_type=None)
    # Yields dicts with id, filename, master_path, folio_number, side.

get_connection()
    # Returns sqlite3 connection to hp.db.
```

**Key property:** Any script that calls `assert_not_web_derivative()`
before reading image bytes is structurally prevented from analyzing
compressed copies. This is a code guard, not a prose rule.

---

## 2. Vision Reading Pipeline

### How It Works

The vision reading pipeline uses Claude Code's native multimodal
capability. There is no external API, no OCR library, no image
processing framework. Claude reads the image file directly via the
Read tool and produces structured JSON.

```
Master image (via images.master_path)
    |
    v
Claude Code reads the image (Read tool)
    |
    v
Human-in-the-loop produces structured JSON
    |
    v
read_images.py --ingest stores result
    |
    v
staging/image_readings/bl/phase1/NNN.json  (raw backup)
    +
image_readings table                        (structured, queryable)
```

### Script: `scripts/read_images.py`

CLI tool for managing the image reading pipeline.

```
read_images.py --phase 1 --source bl --list       # Show pending images
read_images.py --phase 1 --source bl --status      # Show progress
read_images.py --phase 1 --source bl --ingest '{...}'  # Store one result
read_images.py --phase 1 --source bl --ingest-file f.json  # Store batch
read_images.py --phase 1 --source bl --dry-run     # Preview without action
```

**Startup validation:**
- Asserts master image directories exist
- Validates paths are not web derivatives
- Checks idempotency (skips already-processed images)

**Storage:**
- Writes raw JSON to `staging/image_readings/{ms}/phase{N}/{photo}.json`
- Inserts structured row into `image_readings` table
- Computes expected page number from offset formula
- Sets `concordance_status` based on match/mismatch

### Output Schema (Phase 1)

```json
{
  "photo_number": 41,
  "page_number_visible": 28,
  "page_number_readable": true,
  "is_pretext": false,
  "has_woodcut": true,
  "woodcut_description": "Elephant bearing an obelisk with pseudo-hieroglyphic decorations",
  "notes": "Page 28 (b6v). Key alchemical annotation site per Russell Ch. 6"
}
```

---

## 3. Database Infrastructure

### `image_readings` Table (24 columns)

The central storage for all vision model outputs. Created by
`migrate_v3_image_reading.py`.

Key columns:
- `image_id` — FK to `images.id`
- `phase` — pipeline phase (0=historical, 1=ground truth, 2=coverage, 3=deep reading)
- `model` — which vision model produced the reading
- `raw_json` — exact JSON output, preserved verbatim
- `page_number_read` / `page_number_expected` / `page_number_match` — offset verification
- `has_woodcut` / `woodcut_description` — woodcut detection
- `has_annotations` / `annotation_density` — annotation mapping (Phase 2)
- `concordance_status` — CONFIRMED / DISCREPANCY / UNVERIFIED
- `reviewed` / `reviewed_by` / `reviewed_at` — human review tracking
- `promoted_to` — records what canonical table a reading was promoted to

CHECK constraints enforce:
- `annotation_density IN ('LIGHT','MODERATE','HEAVY',NULL)`
- `concordance_status IN ('CONFIRMED','DISCREPANCY','UNVERIFIED')`

### Schema Migrations (v3)

`migrate_v3_image_reading.py` expanded CHECK constraints on:
- `annotations.source_method` — now accepts `'VISION_MODEL'`
- `matches.confidence` — now accepts `'PROVISIONAL'`
- `woodcuts.source_method` — added CHECK constraint
- `symbol_occurrences.source_method` — added CHECK constraint

These migrations mean vision-derived data can now be inserted into
canonical tables without CHECK violations — but only through the
review/promotion pathway.

---

## 4. Concordance Verification

### The Offset Formula

```
BL page number = photo number - 13
```

Verified at 174 out of 174 readable pages. Zero mismatches across the
full range of the book (photos 14-189, pages 1-176).

### Comparison Logic

Built into `read_images.py`:
1. For each Phase 1 reading, compute `page_number_expected = photo - 13`
2. Compare against `page_number_read` (what vision saw)
3. Set `page_number_match = true/false`
4. Log discrepancies (none found so far)

### Coverage

| Metric | Count |
|--------|-------|
| Total BL sequential photos | 189 |
| Phase 1 readings completed | 189 |
| Pages with readable numbers | 174 |
| Offset confirmed | 174/174 (100%) |
| Pages without numbers (pre-text + full-page woodcuts) | 15 |
| Woodcuts detected | 60 |

---

## 5. What We Can Describe

### Already Captured (Phase 1)

For every BL photograph:
- Whether it's a text page or pre-text material
- The printed page number (if readable)
- Whether a woodcut illustration is present
- A one-sentence description of the woodcut subject
- Notes on annotation presence, density, and notable features

### Not Yet Captured (Future Phases)

| Capability | Phase | Status |
|-----------|-------|--------|
| Annotation density classification (LIGHT/MODERATE/HEAVY) | 2 | PLANNED |
| Annotation location mapping (which margins) | 2 | PLANNED |
| Language detection (Latin/Italian/Greek/English) | 2 | PLANNED |
| Legible text fragment extraction | 2 | PLANNED |
| Full structured reading of key folios | 3 | PLANNED |
| Cross-copy comparison (BL vs Siena) | 4 | PLANNED |

### What Cannot Be Described (Known Limitations)

- **Ink color distinction** — photos are near-grayscale
- **Specific alchemical symbol identification** — symbols are 2-3mm, too small
- **Hand attribution** — requires paleographic expertise beyond vision capability
- **Signature marks at page foot** — usually trimmed or illegible

---

## 6. Staging and Audit Trail

### File-Based Staging

```
staging/image_readings/
  bl/
    phase1/
      001.json through 189.json    # Individual readings
      batch_001_013.json           # Batch ingest files
      batch_014_020.json
      ...
    phase2/                        # Empty, ready for Phase 2
    phase3/                        # Empty, ready for Phase 3
  siena/
    phase4/                        # Empty, ready for Phase 4
```

Every raw JSON response is written to the filesystem before being
parsed into the database. If the `image_readings` schema changes,
raw files can be re-parsed without re-reading the images.

### Audit Properties

- Every `image_readings` row carries `created_at` timestamp
- `raw_json` preserves the exact original output
- `concordance_status` records whether the reading confirmed or
  contradicted existing database records
- `reviewed` / `reviewed_by` / `reviewed_at` track human review
- `promoted_to` records which canonical table received the data

---

## 7. Promotion Pathway (Not Yet Built)

The infrastructure supports but does not yet implement promotion from
`image_readings` to canonical tables. The planned pathway:

```
image_readings (PROVISIONAL, needs_review=1)
    |
    v
Human review (reviewed=1)
    |
    v
promote_reading.py (to be built)
    |
    v
Canonical table (annotations, woodcuts, symbol_occurrences)
    with source_method='VISION_MODEL'
    confidence='PROVISIONAL'
    needs_review=1
```

Guards (specified in HP320bIMAGEREADINGPLAN.md):
- Refuses to promote if `reviewed=0`
- Refuses to overwrite existing non-vision records
- Records promotion in `image_readings.promoted_to`

---

## 8. Technology Stack

| Component | Technology | Role |
|----------|-----------|------|
| Database | SQLite (hp.db) | All structured data storage |
| Vision model | Claude Code native multimodal (Opus 4.6) | Image reading |
| Image loading | Python pathlib + Read tool | Path resolution and file access |
| Path validation | `scripts/image_utils.py` | Master vs web enforcement |
| Pipeline orchestration | `scripts/read_images.py` | Batch processing, ingest, status |
| Schema management | `scripts/migrate_v3_image_reading.py` | CHECK constraint expansion |
| Site generation | `scripts/build_site.py` | HTML output from database |
| Image compression | `scripts/compress_images.py` (PIL/Pillow) | Master -> web derivative |
| Raw storage | JSON files in `staging/image_readings/` | Audit trail |

No external APIs. No OCR libraries. No image processing frameworks
beyond Pillow for compression. The entire description engine runs on
SQLite + Claude Code + Python standard library.
