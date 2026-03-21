# HP320 Phase Report: Image Reading Pipeline

> Date: 2026-03-21
> Session: HP320f
> Scope: Phases 0–3 of the BL manuscript image reading pipeline

---

## Executive Summary

We set out to build a machine-readable visual layer for 189 BL
manuscript photographs. That layer now exists. The pipeline has moved
from zero image readings to 428 structured database records across
four phases, confirmed the folio offset at 174 points with zero
mismatches, expanded the woodcut inventory from 18 to 60, and produced
deep scholarly readings of the 20 highest-value pages.

The infrastructure works. The data is real. Nothing has been
auto-promoted to canonical tables. The project is in a strong position
to begin surfacing this evidence on the website.

---

## Phase Completion Status

| Phase | Purpose | Status | Records |
|-------|---------|--------|---------|
| 0 | Infrastructure | **COMPLETE** | 30 backfilled readings |
| 1 | Visual Ground Truth | **COMPLETE** | 189 readings (100% BL) |
| 2 | Coverage Mapping | **COMPLETE** | 189 density classifications |
| 3 | Targeted Deep Reading | **IN PROGRESS** | 20 of 49 HEAVY pages |
| 4 | Siena Cross-Reference | NOT STARTED | 0 |

**Total image_readings rows: 428**

---

## What Each Phase Delivered

### Phase 0: Infrastructure (COMPLETE)

Built before any reading could happen:
- `image_readings` table (24 columns, CHECK constraints)
- `master_path` / `web_path` dual-path model on all 674 images
- `image_utils.py` with `assert_not_web_derivative()` guard
- CHECK constraints on `source_method` across 4 canonical tables
- Staging directory structure
- 30 historical readings backfilled from prior session notes

**Cost:** One session. No rework needed afterward.

### Phase 1: Visual Ground Truth (COMPLETE)

Read all 189 sequential BL photographs using Claude Code native vision
on 4MB master images. Extracted:
- Visible page number (174 readable, 15 unnumbered)
- Woodcut presence (60 detected)
- Pre-text vs body text classification
- One-sentence notes per page

**The single most important result:** BL offset `page = photo_number - 13`
confirmed at 174/174 readable pages with zero mismatches. This was
previously an arithmetic assumption; it is now an empirical fact.

**Woodcut expansion:** 60 detected vs 18 in canonical table. The gap is
intentional — detection is not promotion. The 60 detections include the
triumphal procession sequence (pp. 149–167) which is ~95% woodcuts.

### Phase 2: Coverage Mapping (COMPLETE)

Classified annotation density for all 189 pages:

| Density | Count | % |
|---------|-------|---|
| HEAVY | 49 | 26% |
| MODERATE | 107 | 57% |
| LIGHT | 13 | 7% |
| None | 20 | 11% |

**89% of pages have visible annotations.** This is an extraordinarily
heavily annotated copy — consistent with Russell's characterization but
now quantified across the full book for the first time.

Languages detected across all pages: Latin (dominant), Greek (12 pages),
English (5 pages), Hebrew (2 pages).

### Phase 3: Targeted Deep Reading (IN PROGRESS)

Deep-read 20 pages across three tiers:

**Tier 1 — Legible fragment pages (7/7 complete):**
Photos 2, 3, 27, 41, 138, 139, 140. These had readable marginal text
identified in Phase 2. Every one was deep-read with partial
transcriptions, hand identifications, and scholarly significance notes.

**Tier 2 — Alchemical and key pages (8/8 complete):**
Photos 8, 33, 44, 55, 72, 82, 93, 125. Selected for alchemical content,
extreme annotation density, or important woodcuts.

**Tier 3 — Coverage sample (5/42 complete):**
Photos 29, 31, 101, 132, 164. Representative spread across the book
(pyramid, Greek inscriptions, planetary palace, obelisk, triumphal
procession).

**37 HEAVY pages remain.** They can be deep-read in future sessions.
The highest-value pages have already been done.

---

## Key Scholarly Findings

### Confirmed (already in Russell's thesis)

| Finding | Page | Confidence |
|---------|------|------------|
| Master Mercury declaration | p.3v (photo 3) | HIGH — text partially readable |
| "bellua" annotation on elephant | p.28 (photo 41) | HIGH — clearly visible |
| Alchemical symbols at Bath of Venus | p.42 (photo 55) | HIGH — symbols visible |
| THEODOXIA/COSMODOXIA/EROTOTROPHOS | p.125 (photo 138) | HIGH — printed + annotated |
| Thomas Bourne ownership 1641 | flyleaf (photo 2) | HIGH — clear signature |

### New or Unconfirmed

| Finding | Page | Confidence | Action Needed |
|---------|------|------------|---------------|
| "Synostra Gloria mundi" alchemical annotation | p.127 (photo 140) | MEDIUM | Check Russell Ch. 5–9 |
| Possible "Sulphure" annotation at planetary palace | p.88 (photo 101) | LOW | Higher-res scan needed |
| Possible calcination reference at obelisk | p.119 (photo 132) | LOW | Higher-res scan needed |
| Possible Boccaccio reference | p.126 (photo 139) | LOW | Paleographic verification |
| Possible Erastus reference | p.125 (photo 138) | LOW | Paleographic verification |
| English "Hyra glyphs" + decoding grid | p.31 (photo 44) | MEDIUM | Hand identification needed |
| Mathematical calculations on pyramid dimensions | p.14 (photo 27) | HIGH | Well-documented by Russell |

---

## Infrastructure Built

| Component | File | Purpose |
|-----------|------|---------|
| Image path validation | `scripts/image_utils.py` | Prevents reading web derivatives |
| Image reading pipeline | `scripts/read_images.py` | CLI tool for batch reading, ingestion, status |
| Phase 3 ingestion | inline Python | Phase 3 JSON → DB rows |
| Staging files | `staging/image_readings/bl/phase{1,2,3}/` | Raw JSON audit trail |

### What Does NOT Exist Yet

| Component | Why It Matters | Blocked By |
|-----------|---------------|------------|
| `promote_reading.py` | Moves reviewed findings to canonical tables | Human review |
| `compare_readings.py` | Systematic concordance comparison | Design decision |
| Concordance confidence upgrades | 174 matches could go MEDIUM→HIGH | Human review |
| Site display of Phase 3 findings | Deep readings not visible on website | Template work |

---

## Data Integrity Assessment

### What we can trust

- **BL offset formula:** Empirically confirmed, not assumed. Strongest
  result in the project.
- **Woodcut presence/absence:** Binary detection is reliable. Vision
  models are good at "is there a picture here."
- **Annotation density classification:** HEAVY/MODERATE/LIGHT is a
  coarse classification that should be mostly correct.
- **Phase 0 infrastructure:** Schema constraints, path validation,
  staging directories — all tested and working.

### What needs human verification

- **Woodcut descriptions:** One-sentence summaries may misidentify
  subjects. 60 descriptions, 0 reviewed.
- **Partial transcriptions:** ~80 transcription attempts across 20 deep
  readings. Most are LOW or MEDIUM confidence. They are best-effort
  readings of early modern handwriting at JPEG resolution — not
  paleographic transcriptions.
- **Hand identifications:** "Hand B" attributions follow Russell's
  framework but have not been independently verified against his hand
  profiles.
- **New findings:** The 5 possible new sites/references are all
  provisional. None should be cited as established scholarship without
  human verification.

### What is provably safe

- **No canonical table has been modified by vision reading.** All 428
  image_readings rows live in `image_readings` with
  `concordance_status='UNVERIFIED'`.
- **No match confidence has been upgraded.**
- **No woodcut has been promoted.**
- **The site builds and displays correctly** from canonical data only.
  Image reading evidence is not yet surfaced.

---

## What Comes Next

### Immediate (this session)

1. **Continue Phase 3 Tier 3** — deep-read remaining HEAVY pages
2. **Build `promote_reading.py`** — safe promotion pathway with
   audit trail
3. **Build `compare_readings.py`** — systematic concordance comparison

### Near-term

4. **Woodcut promotion** — review and promote detected woodcuts to
   canonical table (requires human spot-check)
5. **Concordance confidence upgrades** — upgrade 174 MEDIUM matches
   to HIGH based on offset confirmation
6. **Site integration** — display Phase 3 deep readings on marginalia
   pages

### Deferred

7. **Phase 4: Siena** — lower resolution images, lower priority
8. **Multimodal RAG** — useful only after structured evidence exists
9. **External API integration** — unnecessary while Claude Code vision
   works

---

## Risk Register

| Risk | Severity | Mitigation |
|------|----------|------------|
| 0 human reviews performed on any machine output | MEDIUM | All data marked UNVERIFIED; provenance flags in place |
| Resolution insufficient for alchemical symbol identification | LOW | Flagged in discrepancy logs; higher-res scans recommended |
| 37 HEAVY pages not yet deep-read | LOW | Tiers 1–2 (highest value) are complete |
| Woodcut promotion gap (60 detected, 18 canonical) | MEDIUM | Promotion script not yet built; data is safe in image_readings |
| 51 annotations missing manuscript_id | LOW | Does not block current work |
| Session-dependent processing (no standalone batch script) | LOW | Claude Code vision works; API path available if needed |

---

## Counts Summary

| Entity | Count | Source |
|--------|-------|--------|
| image_readings (total) | 428 | DB |
| image_readings phase 0 | 30 | DB |
| image_readings phase 1 | 189 | DB |
| image_readings phase 2 | 189 | DB |
| image_readings phase 3 | 20 | DB |
| staging JSON files (phase 1) | 189 | filesystem |
| staging JSON files (phase 2) | 1 (batch) | filesystem |
| staging JSON files (phase 3) | 20 | filesystem |
| woodcuts detected | 60 | image_readings |
| woodcuts canonical | 18 | woodcuts table |
| annotations | 282 | annotations table |
| matches | 431 | matches table |
| total images | 674 | images table |
| BL offset confirmations | 174/174 | page_number_match |
