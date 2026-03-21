# HANDOVER: HP Marginalia Project — Session Continuation Brief

> Paste this at the top of a new Claude Code session to continue work.
> Last updated: 2026-03-20 (after Phase 0+1 completion).
> IMPORTANT: Also read PHASESTATUS.md for current phase status and next steps.

---

## What This Project Is

A static website at **https://t3dy.github.io/HPMarginalia/** presenting
the marginalia, scholarship, and reception history of the 1499
*Hypnerotomachia Poliphili*, focused on the alchemical annotation hands
discovered by James Russell in his PhD dissertation. SQLite database →
Python scripts → static HTML/CSS/JS. Deployed to GitHub Pages.

**Repo:** `C:\Dev\hypnerotomachia polyphili`
**Live site:** https://t3dy.github.io/HPMarginalia/
**Title:** "Alchemical Hands in the Marginalia to Hypnerotomachia Poliphili"

---

## Architecture (read SYSTEM.md for full details)

```
db/hp.db (24 tables, schema v3, ~3500 rows)
    ↓
scripts/ (47 Python scripts)
    ↓
site/ (9 top-level pages + 356 subpages = 365 total HTML pages)
    deployed to GitHub Pages via git push
```

**Rebuild command:** `python scripts/build_site.py`

No frameworks. No server. No dependencies beyond Python standard library.

---

## 5 Core Documents (read in this order)

| File | What It Covers |
|------|---------------|
| **SYSTEM.md** | Architecture, data flow, operating modes, provenance model |
| **ONTOLOGY.md** | All 24 tables, relationships, canonical vs deprecated |
| **PHASESTATUS.md** | Current phase completion, risks, next steps, warning rules |
| **PIPELINE.md** | Every script in execution order |
| **INTERFACE.md** | What's on the site, page builders, nav structure |
| **ROADMAP.md** | What's BUILT, READY, BLOCKED, SPECULATIVE |

---

## Current Database State

| Table | Rows | Status |
|-------|------|--------|
| annotations | 282 | CANONICAL. 204 attributed to hands (72%). 6 types classified. |
| annotator_hands | 11 | Complete. All hands documented. |
| matches | 431 | 48 HIGH + 383 MEDIUM. 0 LOW. 34 refs unmatched (structural). |
| images | 674 | 196 BL + 478 Siena. Has master_path (originals) + web_path (compressed). |
| image_readings | 219 | 30 historical (phase 0) + 189 Phase 1 BL ground truth. 60 woodcuts detected. BL offset confirmed 174/174. |
| dictionary_terms | 94 | All DRAFT. All have definitions + significance prose. |
| bibliography | 109 | All UNREVIEWED. 0 "Unknown" authors. |
| scholars | 60 | 59 have overview prose. All DRAFT. |
| timeline_events | 71 | Complete. Filterable on site. |
| woodcuts | 18 | 18 cataloged. 60 detected by Phase 1 vision reading (pending promotion). |
| folio_descriptions | 13 | All alchemist-annotated folios described. |
| alchemical_symbols | 10 | Complete for Russell's documented symbols. |
| symbol_occurrences | 26 | 9 BL Hand B + 4 Buffalo Hand E + 13 other. |
| hp_copies | 6 | Russell's 6 copies. BL confidence: MEDIUM. |
| signature_map | 448 | Complete for 1499 collation. |

**Deprecated (do NOT add data to):**
- `dissertation_refs` (282) → replaced by `annotations`
- `doc_folio_refs` (282) → replaced by `annotations`
- `annotators` (11) → replaced by `annotator_hands`

**RESOLVED:** `build_site.py` now queries `annotations` (not `dissertation_refs`)
for all display. Annotation type badges show on marginalia pages. (HP320a, 2026-03-20.)

---

## Site Pages

**Top-level (9 pages):**
- index.html (Home — gallery of all matched images with filter tabs)
- the-book.html (Plot summary of the HP)
- russell-alchemical-hands.html (Essay on alchemical annotation hands)
- concordance-method.html (Essay on concordance methodology)
- digital-edition.html (Stub/roadmap for future edition)
- bibliography.html (109 entries)
- scholars.html (60 scholars with overview prose)
- timeline.html (71 events, filterable)
- about.html (Project information)

**Subpages:**
- marginalia/ (109 folio pages with images and annotations)
- dictionary/ (94 term pages + index)
- woodcuts/ (18 woodcut pages + index)

**Nav tabs (14):** Home, The Book, Alchemical Hands, Concordance, Digital
Edition, Marginalia, Dictionary, Woodcuts, Manuscripts, Bibliography,
Scholars, Timeline, About, Docs/Code

---

## Key Technical Facts

- **BL offset = 13** (photo 014 = page 1, i.e. folio number = photo number - 13)
- **BL confidence: MEDIUM** (upgraded from LOW after offset fix + 27-point verification)
- **Siena confidence: HIGH** (direct folio numbering in filenames)
- **Image paths:** `site/images/bl/` and `site/images/siena/` (compressed JPEGs)
- **Gallery data:** `site/data.json` (223 entries with card descriptions)
- **Scholar profiles:** `site/summaries.json` (34 scholar summaries from corpus)

---

## What Was Done Most Recently (HP320 session, 2026-03-20)

1. **HP320a: Annotations migration** — build_site.py switched from
   dissertation_refs to annotations. Annotation type badges on marginalia pages.
2. **Image path correction** — Added master_path/web_path to images table.
   Diagnosed in IMAGECONFUSION.md.
3. **Phase 0: Infrastructure** — image_readings table, schema v3 migration,
   image_utils.py, staging directories, 30 historical readings backfilled.
4. **Phase 1: Visual Ground Truth** — All 189 sequential BL photos read
   via Claude Code native vision. BL offset confirmed 174/174. 60 woodcuts
   detected. All results in image_readings (phase=1) + staging JSON files.
5. **Core doc updates** — PHASESTATUS.md created. All 5 core docs + HANDOVER
   updated to reflect current state.

---

## What Needs Doing Next (from ROADMAP.md)

### READY — Priority Order

1. ~~Switch marginalia pages from dissertation_refs → annotations~~ **DONE (HP320a)**
2. **Add coverage caveats** — state that images exist for 2 of 6 copies — 15 min
3. ~~Read remaining BL photographs~~ **DONE (Phase 1: 189/189, 60 woodcuts found)**
4. **Add annotation type filtering** to marginalia index — 30 min
5. **Phase 2: Coverage Mapping** — annotation density for all BL photos
6. **Woodcut promotion** — review 60 detected woodcuts, promote to canonical table

### From WRITINGPLAN.md — Writing Improvements

Phase 1 items (home/book/about rewrites) are DONE. Remaining:
- **Phase 2:** Add inline dictionary links in essays (~40 links)
- **Phase 3:** Differentiate overlapping page voices (marginalia vs woodcut vs essay)
- **Phase 4:** Scholar-to-content reverse links
- **Phase 5:** Progressive disclosure on landing pages

### From the Original Multi-Phase Prompt (not yet executed)

The user had a large 8-phase prompt for site hardening. What's been done:
- [x] Phase 1: New tabs and nav (all tabs built)
- [x] Phase 2: Dictionary pipeline (94 terms, all enriched)
- [x] Phase 3: Targeted PDF reading infrastructure (corpus_search.py, build_reading_packets.py)
- [x] Phase 4: Russell Alchemical Hands essay (written and illustrated)
- [x] Phase 5: Concordance Method essay (written)
- [x] Phase 6: Digital Edition stub (built)
- [~] Phase 7: Cross-linking (partially done — dictionary links added, scholar links pending)
- [ ] Phase 8: Full QC pass and final audit report

---

## Unresolved Review Items

1. **All 94 dictionary entries are DRAFT** — no human review done
2. **All 60 scholar overviews are DRAFT** — no human review done
3. **78 annotations (28%) have no hand attribution**
4. **3 PROVISIONAL alchemical sites (c5v, h8r, page 127 "Synostra Gloria mundi")** — found by image reading, not yet in symbol_occurrences
5. **matches.ref_id points to dissertation_refs.id**, not annotations.id
6. **60 woodcuts detected** by Phase 1 but only 18 in canonical woodcuts table — promotion needed
7. **4 copies have no photographs** (Buffalo, Vatican, Cambridge, Modena)
8. **bibliography entries all UNREVIEWED**
9. **The user has writing in progress in another window** — check for updates before modifying content pages

---

## Key Scripts Reference

| Script | Purpose |
|--------|---------|
| `build_site.py` | Main site builder — generates all 365 pages |
| `validate.py` | Runs all validation checks |
| `read_images.py` | Phase 1 image reading pipeline (--ingest, --status, --list) |
| `image_utils.py` | Shared path validation (master vs web enforcement) |
| `migrate_v3_image_reading.py` | Schema v3 migration (image_readings + CHECK expansions) |
| `backfill_previous_readings.py` | Import 30 historical readings into image_readings |
| `catalog_images.py` | Catalog images with master_path + web_path |
| `corpus_search.py` | Search markdown/chunks for evidence passages |
| `rebuild_bl_matches.py` | Rebuild BL concordance matches (uses offset=13) |
| `compress_images.py` | Compress master images → web derivatives |
| `export_showcase_data.py` | Generate data.json for the gallery |

---

## Constraints (Always Follow)

- SQLite is source of truth — never trust documentation over the database
- Never overwrite VERIFIED content with DRAFT/LLM-assisted content
- Every inferred datum must carry: source_method, review_status, confidence, notes
- "Outward not deeper" — surface existing data before adding more
- No frameworks — keep the static site architecture
- BL concordance claims default to PROVISIONAL unless evidence is stronger
- Canonical tables only: annotations (not dissertation_refs), annotator_hands (not annotators)
- Image analysis uses master_path ONLY — never site/images/ (call assert_not_web_derivative)
- Vision outputs go to image_readings first, never directly to canonical tables
- Check PHASESTATUS.md before starting any new phase

---

## File Layout

```
C:\Dev\hypnerotomachia polyphili\
├── db/hp.db                    # SQLite database (23 tables)
├── scripts/                    # 42 Python scripts
├── site/                       # Generated static site
│   ├── *.html                  # 9 top-level pages
│   ├── style.css               # Single stylesheet
│   ├── script.js               # Gallery JS (filter, lazy load)
│   ├── data.json               # Gallery card data (223 entries)
│   ├── summaries.json          # Scholar profile summaries (34)
│   ├── dictionary/             # 95 pages (94 terms + index)
│   ├── marginalia/             # 109 folio pages
│   ├── woodcuts/               # 19 pages (18 woodcuts + index)
│   └── images/                 # Compressed manuscript photographs
│       ├── bl/                 # 196 BL images
│       └── siena/              # 478 Siena images
├── md/                         # PDF-to-markdown outputs
├── chunks/                     # Chunked markdown for search
├── staging/                    # Reading packets and staging data
│   └── packets/                # Per-term evidence packets
├── docs/                       # Active specs
│   ├── SCHOLAR_SPEC.md
│   ├── SCHOLAR_PIPELINE.md
│   ├── TIMELINE_SPEC.md
│   ├── MANUSCRIPTS_SPEC.md
│   ├── WRITING_TEMPLATES.md
│   └── archive/                # 36 archived design docs
├── SYSTEM.md                   # Architecture (read first)
├── ONTOLOGY.md                 # Schema reference
├── PIPELINE.md                 # Script execution order
├── INTERFACE.md                # Site structure
├── ROADMAP.md                  # What to do next
├── CLAUDE.md                   # Project instructions for Claude
└── README.md                   # Build instructions
```
