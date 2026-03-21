# HANDOVER320: Session Continuation Document

> Date: 2026-03-21
> Last commit: `fff28b3` on `main`
> Live site: https://t3dy.github.io/HPMarginalia/
> Status: Deployed and working

---

## What This Project Is

A static website presenting the marginalia, scholarship, and reception
history of the 1499 *Hypnerotomachia Poliphili*. SQLite database →
Python scripts → static HTML. Deployed to GitHub Pages.

The site surfaces James Russell's 2014 Durham PhD thesis documenting
the handwritten annotations in six copies of the HP, with particular
focus on the alchemical annotations in the British Library copy
(C.60.o.12).

---

## What Exists Right Now

### Database (db/hp.db)

| Table | Rows | What It Holds |
|-------|------|---------------|
| `images` | 674 | BL (196) + Siena (478) manuscript photographs |
| `image_readings` | 457 | Vision readings: 30 phase-0, 189 phase-1, 189 phase-2, 49 phase-3 |
| `woodcuts` | 115 | 18 corpus + 42 vision-detected + 55 from 1499 catalog |
| `editions` | 8 | Historical editions 1499–1999 |
| `annotations` | 282 | Russell's dissertation references (migrated from dissertation_refs) |
| `matches` | 431 | Annotation-to-image concordance matches |
| `scholars` | 65 | Scholar profiles with HP focus |
| `dictionary_terms` | 101 | HP-specific terminology with significance |
| `timeline_events` | 85 | Publication, scholarship, cultural events |
| `bibliography` | 116 | Academic works cited |
| `annotator_hands` | 11 | Identified hands across 6 copies |
| `signature_map` | 448 | 1499 collation formula (quire signatures → folios) |
| `schema_version` | 3 | Current schema version |

### Website (site/)

| Component | Count |
|-----------|-------|
| HTML pages | 432 |
| Nav tabs | 15 |
| Woodcut gallery images | 73 (from 1499 IA facsimile, compressed to 14MB) |
| BL manuscript images | 199 (compressed for web) |
| Siena manuscript images | 481 |

### Key Tabs

| Tab | What It Shows |
|-----|---------------|
| **Home** | Marginalia gallery (431 cards, JS-driven with lightbox) |
| **Marginalia** | 113 folio detail pages with images, annotations, symbols |
| **Woodcuts** | 73 woodcut pages with 1499 facsimile images, category filters |
| **Editions** | 8 historical editions in timeline layout |
| **Scholars** | 65 scholar profiles |
| **Dictionary** | 101 terms |
| **Timeline** | 85 events |
| **Bibliography** | 116 entries |
| **Alchemical Hands** | Russell essay with BL/Buffalo evidence tables |
| **The Book** | Narrative summary of the HP for non-specialists |
| **Manuscripts** | 6 annotated copy pages |

### Scripts (scripts/)

| Script | Purpose |
|--------|---------|
| `build_site.py` | Master builder — generates all 432 HTML pages |
| `read_images.py` | Image reading pipeline (Phase 1-2 ingestion) |
| `promote_reading.py` | Promotes image_readings to canonical tables |
| `compare_readings.py` | Compares vision readings vs canonical data |
| `image_utils.py` | Path validation (master vs web derivatives) |
| `seed_1499_woodcuts.py` | Seeds 1499 woodcut catalog |
| `fetch_1499_woodcuts.py` | Downloads IA facsimile images |
| `seed_from_deepresearch.py` | Seeds editions/scholars/terms from HPDEEPRESEARCH.txt |
| `compress_images.py` | Compresses master images for web deployment |

---

## What Was Done in Sessions HP320a–i (this window)

### Infrastructure (HP320a-d)
- Created `image_readings` table (24 columns)
- Added `master_path`/`web_path` to all 674 images
- Built `image_utils.py` with `assert_not_web_derivative()` guard
- Added CHECK constraints on `source_method` across 4 tables
- Backfilled 30 historical readings from prior notes
- Schema version → 3

### Phase 1: Visual Ground Truth (HP320d)
- Read all 189 sequential BL photographs via Claude Code native vision
- **BL offset confirmed: page = photo_number - 13 at 174/174 points, 0 mismatches**
- 60 woodcuts detected (vs 18 previously in canonical table)
- 3 alchemical sites confirmed/discovered (pp. 28, 42, 127)

### Phase 2: Coverage Mapping (HP320e)
- Classified annotation density for all 189 pages
- 49 HEAVY, 107 MODERATE, 13 LIGHT, 20 none
- 89% of pages have visible annotations
- Languages: Latin (dominant), Greek (14 pages), English (7), Hebrew (2)

### Phase 3: Targeted Deep Reading (HP320f-g)
- Deep-read all 49 HEAVY pages with partial transcriptions
- ~200 transcription attempts across 49 pages
- Key findings:
  - Master Mercury declaration confirmed ("verus sensus intentionis huius libri")
  - "Synostra Gloria mundi" (p.127) — new alchemical site
  - "Quinta Essentia" / "Chrysopheires" (p.164) — alchemical vocabulary in procession
  - "Mnemophora" (p.84) — reader-coined Greek neologism
  - Possible Boccaccio reference (p.126), Erastus reference (p.125)
  - "Hyra glyphs" + decoding grid (p.31) — English reader's hieroglyph work
  - Mathematical pyramid calculations (p.14) — reader computing dimensions

### Woodcut Promotion (HP320g)
- Promoted 42 vision-detected woodcuts to canonical table
- Built `promote_reading.py` and `compare_readings.py`
- Canonical woodcuts: 18 → 60

### Woodcut Gallery (HP320h)
- Rebuilt Woodcuts tab with 1499 IA facsimile images
- Source: Internet Archive A336080v1 (University of Seville, 600ppi)
- IA offset formula: IA page = HP page + 5
- 73 images downloaded and compressed (195MB → 14MB)
- Category filters, narrative context, prev/next navigation
- Seeded 55 new woodcut entries from 1499 catalog

### Editions & HPDEEPRESEARCH (HP320i)
- Created `editions` table with 8 entries (1499–1999)
- Replaced "Edition" stub with full Editions page
- Integrated HPDEEPRESEARCH.txt: +5 scholars, +7 dictionary terms, +14 timeline events, +7 bibliography entries
- `seed_from_deepresearch.py` script

---

## Key Technical Facts

### Image System
- **Master images** (analysis): `images.master_path` → original 4MB JPEGs in local directories (gitignored)
- **Web images** (display): `images.web_path` → compressed copies in `site/images/`
- **1499 facsimile** (woodcut gallery): `site/images/woodcuts_1499/` → from Internet Archive
- **RULE**: Never use web derivatives for analysis. Call `assert_not_web_derivative()`.

### BL Offset
- Formula: `page = photo_number - 13`
- Confirmed at 174/174 readable pages, 0 mismatches
- Hardcoded in `read_images.py` as `BL_OFFSET = 13`

### Image Readings Pipeline
- Phase 0: Historical backfill (30 entries)
- Phase 1: Ground truth — page numbers, woodcut detection (189 entries)
- Phase 2: Coverage mapping — annotation density, locations, languages (189 entries)
- Phase 3: Deep reading — transcription attempts, scholarly analysis (49 entries)
- All readings are `concordance_status='UNVERIFIED'` unless promoted

### Provenance Rules
- No vision output is ever auto-inserted as VERIFIED
- All image-reading results enter as PROVISIONAL / needs_review
- Canonical tables should not be silently overwritten
- Discrepancies are preserved for audit

### Build Command
```bash
python scripts/build_site.py   # Generates all 432 pages
```

---

## What Needs Doing Next

### High Priority

1. **Concordance confidence upgrades**
   174 BL offset confirmations are ready to upgrade `matches.confidence`
   from MEDIUM to HIGH. Needs a script extension to `promote_reading.py`
   or a standalone upgrade script. Low effort, high impact on data quality.

2. **Surface Phase 3 deep readings on marginalia pages**
   49 pages of transcription data and scholarly observations exist in
   `image_readings.deep_reading_json` but are not displayed on the website.
   Modify `build_marginalia_pages()` in `build_site.py` to show deep
   reading content on folio detail pages. Medium effort, high value.

3. **Relocate Russell annotation woodcuts into Alchemical Hands page**
   The 18 original canonical woodcuts (with annotation data, scholarly
   discussion, dictionary term links) should be shown on the Russell
   essay page rather than only in the general gallery. This was planned
   but not executed. Low effort.

### Medium Priority

4. **Complete the 1499 woodcut catalog**
   73 of ~172 woodcuts are in the gallery. The remaining ~100 need:
   - Identification of correct IA page numbers
   - Seed entries in the database
   - Image downloads via `fetch_1499_woodcuts.py`
   - Narrative context descriptions

5. **HPDEEPRESEARCH.txt deeper integration**
   The document contains more data than was extracted:
   - Botanical taxonomy (285 species across 672 passages)
   - F.I.P. project reconstructions
   - Pre-Raphaelite / Art Nouveau influence chain
   - Pedagogical course structure
   - Griffo typeface history
   User wanted a full plan via `/hiro-plantagenet` — not yet done.

6. **Phase 4: Siena cross-reference**
   478 Siena images unread. Lower resolution than BL. Now unblocked
   by BL baseline completion but lower priority.

### Low Priority / Cleanup

7. **51 annotations missing manuscript_id** — backfill linkage
8. **matches.ref_id FK cleanup** — points to dissertation_refs, should point to annotations
9. **Human spot-checks** — see HP320HUMANTESTING.md for the 70-minute review plan
10. **PHASESTATUS.md is stale** — several sections still reference Phase 3 as in-progress and woodcuts as unpromotable. Needs update.

---

## What NOT To Do

- **Do not use `site/images/` for analysis** — those are compressed web copies
- **Do not auto-mark anything as VERIFIED** — all machine output stays PROVISIONAL
- **Do not silently overwrite canonical data** — log discrepancies instead
- **Do not build multimodal RAG yet** — useful only after structured evidence is complete
- **Do not start Phase 4 Siena before BL data is surfaced on the site**

---

## Key Files to Read First

| File | Why |
|------|-----|
| `CLAUDE.md` | Project instructions and constraints |
| `SYSTEM.md` | Architecture, data flow, operating modes |
| `PHASESTATUS.md` | Phase completion status (partially stale — trust this handover over it) |
| `HP320HUMANTESTING.md` | Where human review is lacking |
| `HP320Phase2.md` | Detailed phase report with counts |
| `scripts/build_site.py` | The master builder — understand this and you understand the site |
| `scripts/read_images.py` | The image reading pipeline |

---

## Session Discipline

At the end of every major session, update:
- **PHASESTATUS.md** — phase completion, what changed, next steps, blockers
- **HANDOVER** document if substantial work was done
- Core docs if counts or claims have drifted

Before starting work, check PHASESTATUS.md for:
- Whether proposed work has met prerequisites
- Whether any phases are BLOCKED
- Current schema version and table counts
