# PHASESTATUS: Where We Are

> Updated: 2026-03-20
> Schema version: 3
> This document must be updated at the end of every major session.

---

## Project Snapshot

| Fact | Value | Evidence |
|------|-------|----------|
| Database tables | 24 | `SELECT COUNT(*) FROM sqlite_master WHERE type='table'` |
| Schema version | 3 | `SELECT MAX(version) FROM schema_version` |
| Total HTML pages | 365 | `find site -name "*.html" \| wc -l` |
| Python scripts | 47 | `ls scripts/*.py \| wc -l` |
| BL photographs | 196 (189 sequential + 7 supplementary) | `images` table |
| Siena photographs | 478 | `images` table |
| Phase 1 readings complete | 189/189 | `image_readings` table, phase=1 |
| BL offset confirmed | 174/174 readable pages, 0 mismatches | `page_number_match` column |
| Woodcuts detected | 60 | `image_readings` where has_woodcut=1, phase=1 |
| Woodcuts in canonical table | 60 (18 original + 42 promoted) | `woodcuts` table |
| Site builds cleanly | Yes | `python scripts/build_site.py` succeeds |

---

## Phase-by-Phase Status

### Phase 0: Infrastructure
**Status: COMPLETE**

| Deliverable | Done | Evidence |
|-------------|------|----------|
| `image_readings` table (24 columns) | Yes | `sqlite3 db/hp.db ".schema image_readings"` |
| `images.master_path` populated (674 images) | Yes | `SELECT COUNT(*) FROM images WHERE master_path IS NOT NULL` = 674 |
| `images.web_path` populated (674 images) | Yes | Same query, web_path |
| `annotations.source_method` accepts VISION_MODEL | Yes | CHECK constraint expanded in migration v3 |
| `matches.confidence` accepts PROVISIONAL | Yes | CHECK constraint expanded in migration v3 |
| `woodcuts.source_method` CHECK constraint | Yes | Added in migration v3 |
| `symbol_occurrences.source_method` CHECK constraint | Yes | Added in migration v3 |
| `scripts/image_utils.py` (shared validation) | Yes | File exists, tested |
| Staging directories | Yes | `staging/image_readings/bl/phase{1,2,3}/`, `siena/phase4/` |
| Historical readings backfilled | Yes | 30 rows in `image_readings` where phase=0 |
| Schema version recorded | Yes | schema_version = 3 |

**Readiness check for downstream work:**
- All CHECK constraints pass INSERT tests
- All master_path values resolve to existing files on disk
- `image_utils.py` functions tested and working
- No blockers

### Phase 1: Visual Ground Truth (BL)
**Status: COMPLETE**

| Metric | Value |
|--------|-------|
| Photos processed | 189/189 (100%) |
| Pages with readable numbers | 174 |
| Offset confirmed | 174/174 (0 mismatches) |
| Pages without numbers | 15 (13 pre-text + 2 full-page woodcuts) |
| Woodcuts detected | 60 |
| Raw JSON files written | 189 (in `staging/image_readings/bl/phase1/`) |
| DB rows written | 189 (in `image_readings`, phase=1) |

**Method:** Claude Code native vision reading master images (4MB originals).
No external API. No OCR library. Each image read via the Read tool.

**Key findings:**
- BL offset `page = photo - 13` is now empirically confirmed across the
  full range of the book, not just at sample points
- 60 woodcuts detected vs 18 in canonical `woodcuts` table — a 3.3x expansion
- 2 alchemical sites confirmed (pages 28, 42), 1 new site discovered (page 127)
- Triumphal procession sequence (pages 149-167) is 95% woodcuts

**What Phase 1 did NOT do:**
- Did not write to canonical tables (annotations, woodcuts, etc.)
- Did not upgrade match confidence
- Did not perform annotation density classification (that's Phase 2)
- All readings are UNVERIFIED in the database — none have been reviewed

### HP320a: Annotations Migration
**Status: COMPLETE**

`build_site.py` now queries `annotations` (not `dissertation_refs`) for
all display purposes. `annotation_type` badges appear on marginalia pages.
Two aggregate count queries still use `dissertation_refs` because 51
annotations lack `manuscript_id` linkage.

### Phase 2: Coverage Mapping (BL)
**Status: COMPLETE**

| Metric | Value |
|--------|-------|
| Photos classified | 189/189 |
| Pages with annotations | 169 (89%) |
| HEAVY density | 49 pages |
| MODERATE density | 107 pages |
| LIGHT density | 13 pages |
| No annotations | 20 pages |
| Languages detected | Latin (dominant), Greek (12 pages), English (5), Hebrew (2) |
| Legible text fragments | 7 pages with readable marginal text |

**Phase 3 targeting candidates (HEAVY + legible fragments):**
- Photo 3 (flyleaf): Master Mercury declaration
- Photo 27 (page 14): Descriptio Pyramidis, mathematical notations
- Photo 41 (page 28): "bellua" — key alchemical site
- Photo 138 (page 125): THEODOXIA/COSMODOXIA/EROTOTROPHOS trilingual
- Photo 140 (page 127): "Synostra Gloria mundi" — new alchemical site

### Phase 3: Targeted Deep Reading
**Status: COMPLETE (49/49 HEAVY pages deep-read)**

| Metric | Value |
|--------|-------|
| Pages deep-read | 49 |
| Tier 1 (legible fragments) | 7/7 complete |
| Tier 2 (alchemical/key pages) | 8/8 complete |
| Tier 3 (remaining HEAVY) | 34/34 complete |
| Transcription attempts | ~200 across 49 pages |
| New alchemical sites found | 3 (pp. 88, 119, 164 — all unconfirmed) |
| Discrepancies logged | 12 across 49 pages |
| Possible new references | Boccaccio (p.126), Erastus (p.125), Bassetti (p.39) |
| Coined terms found | 'Mnemophora' (p.84), 'Chrysopheires' (p.164) |

**Key findings from Phase 3 deep reading:**
- Master Mercury declaration (p.3v): 'verus sensus intentionis huius libri'
  confirmed. Date ambiguity (1535 vs 1641) flagged.
- Elephant/bellua (p.28): confirmed. Minimal additional text readable.
- Descriptio Pyramidis (p.14): mathematical calculations in margins,
  reader computing pyramid dimensions independently.
- Three doors (pp.125-127): multilingual annotations, possible Boccaccio
  and Erastus references, 'Synostra Gloria mundi' confirmed as new
  alchemical site.
- Planetary palace (p.88): possible 'Sulphure' annotation — would add
  a 4th alchemical site.
- Hieroglyphic frieze (p.31): English reader wrote 'Hyra glyphs' and
  attempted translation. Grid/decoding diagram drawn.
- Fountain (p.80): 'Cornucopia' and 'mortem' annotations — dual
  reading of beauty and mortality.

**Additional findings from Tier 3 expansion (10 more pages):**
- Page 1 (a1r): Greek-derived terminology 'Synephorus' from first line
- Page 12: Vitruvian architectural vocabulary ('proportio altitudinis',
  'obelisco', 'fastigio') — same reader as p.14 calculations
- Page 21: 'lapidem' ambiguity (architectural stone vs philosopher's stone)
- Page 27: 'funerali'/'Simbole' — reader identifies death/symbol register
  immediately before the bellua page
- Page 39: 'martem'/'aries' — astrological vocabulary; possible name 'Bassetti'
- Page 92: Meta-literary commentary ('Auctoris natura', 'verita'/'falsitatis')
- Page 113: Theological virtue mapping ('Fides'/'Gratia'/'Venerantas')
- Page 162: Musical vocabulary ('Cantorum'/'Tonalarium') in procession section

**All 49 HEAVY pages complete.** No remaining Tier 3 work.

**Major discovery in final batch:** Page 164 (photo 177) contains
'Quinta Essentia', 'Chrysopheires', 'transformans', 'Smaraldi' —
the most concentrated alchemical vocabulary in the triumphal
procession section. This extends Hand B's alchemical reading program
into the procession sequence, well beyond previously documented sites.

### Phase 4: Siena Cross-Reference
**Status: BLOCKED by Phase 3**

Lower priority. Siena images are lower resolution. Depends on BL baseline
being established (Phases 1-3).

### Woodcut Promotion
**Status: COMPLETE (42 promoted, 60 total canonical)**

| Metric | Value |
|--------|-------|
| Original canonical woodcuts | 18 (CORPUS_EXTRACTION) |
| Vision-detected promotions | 42 (VISION_MODEL, PROVISIONAL) |
| Total canonical woodcuts | 60 |
| Promotion candidates remaining | 0 |

All 42 candidates promoted via `promote_reading.py --force` (without
human review per user instruction). All promoted entries have:
- `source_method = 'VISION_MODEL'`
- `confidence = 'PROVISIONAL'`
- `review_status = 'DRAFT'`

### Concordance Confidence Upgrades
**Status: NOT STARTED, prerequisites met**

174 BL offset confirmations are upgrade candidates for `matches` entries.
Promotion from MEDIUM to HIGH confidence requires:
- [x] Page number verified by vision reading
- [x] `matches.confidence` accepts PROVISIONAL
- [ ] Human review of each upgrade candidate
- [ ] Promotion script or manual SQL

---

## What Is Actually Working Now

These are capabilities that exist in code, have been tested, and can be
used immediately:

1. **Image path validation** — `image_utils.py` prevents analysis scripts
   from reading compressed web copies. Tested, working.

2. **Phase 1 batch reading pipeline** — `read_images.py` with `--ingest`,
   `--ingest-file`, `--list`, `--status`. Idempotent, resume-capable.

3. **Offset verification** — every BL sequential photo's page number has
   been read and compared. Formula confirmed at 174 points.

4. **Site build from annotations** — `build_site.py` uses the canonical
   `annotations` table. Annotation type badges display on marginalia pages.

5. **Schema enforcement** — CHECK constraints on `source_method` and
   `confidence` across annotations, matches, woodcuts, symbol_occurrences
   prevent invalid values. Vision-derived data can be inserted with
   correct provenance.

6. **Staging audit trail** — raw JSON for every Phase 1 reading stored
   in `staging/image_readings/bl/phase1/`.

---

## What Is Still Only Planned

These are described in plan documents but do not exist as code or data:

1. ~~**Phase 2 coverage mapping**~~ — COMPLETE. 189/189 classified.

2. **Phase 3 deep reading (remaining)** — 37 of 49 HEAVY pages not yet
   deep-read. 20 done (Tiers 1-2 complete, 5 of Tier 3 done). Not blocked.

3. **Phase 4 Siena cross-reference** — cross-copy comparison. Can begin
   once BL baseline is sufficiently established. Not strictly blocked but
   lower priority.

4. **Woodcut promotion pipeline** — `promote_reading.py` EXISTS and
   WORKS. 42 candidates identified. Dry-run tested. Awaiting human
   review before execution.

5. **Concordance comparison script** — `compare_readings.py` EXISTS and
   WORKS. Summary mode shows: offset 174/174 confirmed, 18 woodcuts
   matched + 42 new, annotation comparison needs folio-to-page mapping.

6. **Multimodal RAG** — retrieval layer across images, text, and
   structured data. Deferred until Phases 1-3 produce structured evidence.

---

## Remaining Infrastructure / Environment Risks

### 1. No external API dependency (RESOLVED)

The plan originally assumed Claude Vision API calls via the `anthropic`
SDK. In practice, Phase 1 was executed entirely within Claude Code using
native vision. This is cheaper, simpler, and avoids API key management —
but it means batch processing depends on session length, not a standalone
script.

**Risk:** If a future session wants to re-run Phase 1 or run Phase 2
outside of Claude Code, `read_images.py` would need an API integration
path. Currently it only supports `--ingest` (pre-computed results).

### 2. 51 annotations missing manuscript_id

51 `annotations` rows have neither `hand_id` nor `manuscript_id`. These
came from `dissertation_refs` entries that were never fully linked.
Aggregate count queries for concordance and manuscripts pages still use
`dissertation_refs` for this reason.

**Risk:** Low. Does not block any current work. Should be backfilled
when convenient.

### 3. Woodcut promotion gap

60 woodcuts detected but only 18 in the canonical table. The gap will
grow if Phase 2/3 find more. Until `promote_reading.py` exists, there
is no safe pathway from image_readings to woodcuts.

**Risk:** Medium. Detected woodcuts are stored in image_readings and
won't be lost. But they won't appear on the website until promoted.

### 4. matches.ref_id still points to dissertation_refs

The foreign key in `matches` references `dissertation_refs.id`, not
`annotations.id`. This works because the IDs are identical, but it's
a legacy dependency that should eventually be cleaned up.

---

## Prudent Next Steps

In priority order:

1. **Complete Phase 3 Tier 3** — 19 HEAVY pages remaining. Diminishing
   returns but completeness is valuable.

2. **Human spot-check** — Review 10 woodcut detections against known
   catalogs. Review the 'Synostra Gloria mundi' finding against Russell.
   ~30 minutes total. See HP320HUMANTESTING.md.

3. **Woodcut promotion** — `promote_reading.py` is ready. Run with
   `--dry-run` first, then promote after review. Will expand canonical
   woodcuts from 18 to 60.

4. **Concordance confidence upgrades** — 174 offset confirmations are
   ready to upgrade from MEDIUM to HIGH. Needs promotion script extension.

5. **Site integration** — Surface Phase 3 deep readings on marginalia
   pages. Requires template modifications to `build_site.py`.

---

## Things We Are Not Ready To Do Yet

### ~~Do not run Phase 3 deep reading~~ (RESOLVED — Phase 3 in progress, 30/49 done)

### Do not promote woodcuts to canonical table without review
60 woodcuts were detected by vision reading. Some may be decorative
initials, some may be misclassified. Human review is required before
any `promote_reading.py` execution.

### Do not build multimodal RAG
RAG is most useful after Phases 1-3 produce structured evidence units.
We have Phase 1 only. RAG now would be premature infrastructure.

### Do not upgrade match confidence automatically
The plan explicitly states: "Vision reading can flag upgrade candidates.
It cannot execute upgrades." Even though 174/174 offsets are confirmed,
confidence upgrades require human review.

### Do not build an API integration for read_images.py
Phase 1 proved that Claude Code native vision works. Adding API
integration adds complexity for a problem we don't have. Revisit only
if batch sizes exceed session capacity.

---

## Warning Rules for Future Sessions

These rules must be followed by any session continuing this project:

### 1. Do not start a phase whose prerequisites are not complete
Check this document's phase status before beginning work. If a phase
says BLOCKED, do not start it. If prerequisites are listed as incomplete,
complete them first.

### 2. Do not trust prose rules without schema/code enforcement
The project went through a correction cycle (HiroPlantagenet audit) where
five "non-negotiable" provenance rules existed only as English sentences.
If a rule matters, it must be enforced by a CHECK constraint, a validation
function, or a code guard — not by a markdown document.

### 3. Do not use web derivatives for analysis
`site/images/bl/` and `site/images/siena/` are compressed display copies.
All vision reading, OCR, embedding, or comparison must use `master_path`.
Call `assert_not_web_derivative()` before reading any image bytes.

### 4. Do not silently overwrite canonical data
If a vision model reading contradicts an existing record in `annotations`,
`woodcuts`, or `symbol_occurrences`, log the discrepancy. Do not UPDATE
or DELETE the existing record. The existing record stands until human review.

### 5. Do not treat provisional vision output as verified scholarship
All `image_readings` rows are UNVERIFIED. They are machine observations,
not scholarly conclusions. They must pass through review and promotion
before entering canonical tables with `source_method='VISION_MODEL'`.

### 6. Update PHASESTATUS.md at end of every major session
Before ending a session, update:
- Phase completion status
- What changed (scripts, schema, data)
- Prudent next steps
- Any new blockers
- Whether the proposed next action would skip prerequisites

This is project operating discipline, not a suggestion.

---

## Update Log

| Date | Session | What Changed |
|------|---------|-------------|
| 2026-03-20 | HP320a-d | Phase 0 complete. Phase 1 complete (189/189 BL photos). Annotations migration done. 60 woodcuts detected. Schema v3. 8 new scripts. PHASESTATUS.md created. |
| 2026-03-20 | HP320e | Phase 2 complete (189/189 density classified). 49 HEAVY, 107 MODERATE, 13 LIGHT, 20 none. Core docs updated. HP320HUMANTESTING.md created. Phase 3 now READY. |
| 2026-03-21 | HP320f-g | Phase 3 COMPLETE: all 49 HEAVY pages deep-read (457 total image_readings). promote_reading.py + compare_readings.py built. 42 woodcuts promoted to canonical (60 total). Major finding: p.164 has 'Quinta Essentia'/'Chrysopheires' alchemical cluster. Coined term 'Mnemophora' found on p.84. HP320Phase2.md report written. |
| 2026-03-21 | HP320h | Woodcut gallery rebuilt with 1499 IA facsimile images. 73 woodcut pages with 600ppi images from University of Seville copy (A336080v1). 115 total woodcuts in DB (18 original + 42 vision + 55 new 1499 catalog). seed_1499_woodcuts.py + fetch_1499_woodcuts.py created. Category filters, narrative context, cross-links to BL annotations. Images compressed to 14MB total. |
| 2026-03-21 | HP320i | Editions tab created from HPDEEPRESEARCH.txt. 8 historical editions (1499-1999). HPDEEPRESEARCH data integrated: +5 scholars (65 total), +7 dictionary terms (101 total), +14 timeline events (85 total), +7 bibliography entries (116 total). editions table created. seed_from_deepresearch.py script. Nav updated to "Editions". |
