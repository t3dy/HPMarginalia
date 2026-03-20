# CONCORDANCEHACKING: How the Concordance Problem-Solving Is Going

> A Deckard boundary analysis of where the concordance stands,
> what's been solved, what's still broken, and what the next moves are.

---

## The Original Problem

Russell's thesis references folios by signature (b6v, h1r, etc.). Our
photograph collections use different naming schemes. The concordance
pipeline must translate between these systems to connect scholarly claims
to visual evidence.

**Three manuscript photograph sets:**
- Siena O.III.38: 478 photos, filenames encode folio+side (O.III.38_0014r.jpg)
- BL C.60.o.12: 189 photos, sequentially numbered (C_60_o_12-001.jpg)
- Buffalo, Vatican, Cambridge, Modena: no photos available

---

## What's Been Solved

### Siena: SOLVED (HIGH/MEDIUM confidence)
The Siena filenames directly encode folio numbers. The matching pipeline
joins via folio number and side. 392 matches: 26 HIGH (exact signature+side),
366 MEDIUM (folio number matched, side sometimes ambiguous). This has been
stable from the beginning.

### BL Offset: SOLVED (photo 014 = page 1)
The sequential numbering assumption was wrong. Visual inspection of 27
photographs proved that photos 001-013 are front matter. The HP text
begins at photo 014. The offset is exactly 13.

**Before:** Photo 41 was assumed to be folio 41. It was actually page 28 = b6v
(the elephant and obelisk).

**After:** Corrected folio numbers for all 189 BL photos. 39 new MEDIUM
matches created where the corrected folio aligns with a signature reference.

### 1545 Edition Confirmed
Photo 004 (title page) clearly reads "RISTAMPATO DI NOVO... M.D.XXXXV."
This is definitively the 1545 second Aldine edition. The 1499 signature map
applies because quire signature "g ii" is visible at photo 110 (page 97),
confirming the same collation structure.

### BL Photo Range Established
189 sequential photos covering pages 1-176 (approximately quires a through k).
This is the first 38% of the book. The later signatures Russell discusses
(E8v at page 432, y7r at page 333) are beyond the photographic coverage.

### Annotation Classification
282 annotations classified into 6 types from the canonical annotations table:
- MARGINAL_NOTE: 126 (the default scholarly annotation)
- CROSS_REFERENCE: 68 (identifying classical sources)
- INDEX_ENTRY: 50 (keyword labels, short notes)
- SYMBOL: 21 (alchemical ideograms)
- EMENDATION: 16 (textual corrections)
- UNDERLINE: 1

### Hand Attribution
204 of 282 refs now attributed (72%, up from 68%). The improvement came
from chapter-based inference (Ch. 4 = Modena/Giovio, Ch. 5 = Cambridge/Giovio,
Ch. 8 = Vatican/Chigi, Ch. 9 = Siena/anonymous) and regex matching of
"Hand [A-E]" patterns in thesis text.

---

## What's Still Broken

### BL Matches Still LOW Confidence (218 matches)
The offset fix corrected the folio numbers, but most BL matches remain LOW
because the match pipeline originally assigned LOW to all BL data and the
ground-truth verification created 39 new MEDIUM matches rather than
upgrading the original 218. The 218 original matches need to be re-run
against the corrected folio numbers — many may now align correctly and
deserve MEDIUM or even HIGH confidence.

**This is a scripting task, not a research problem.** The data exists to
fix it. A re-matching pass using the corrected folio numbers would upgrade
many LOW matches.

### 78 Unattributed Annotations
78 of 282 annotations still have NULL hand_id. Most are from Russell's
introductory chapters (Ch. 1-3) where he discusses the HP generally rather
than attributing specific annotations to specific hands. Some may be
genuinely multi-copy references that can't be attributed to a single hand.

### Photos Cover Only 38% of the Book
The 189 BL photos cover pages 1-176. Russell discusses annotations on later
pages (e.g., E8v at page 432 for the alchemist, y7r at page 333 for the
fons heptagonis). These folios have no photographic evidence in our
collection.

### Two New Alchemical Sites Unverified
Image reading discovered alchemical annotations on c5v (page 42) and h8r
(page 127) that aren't in the symbol_occurrences table. These need
verification against Russell's thesis text to determine whether he discusses
them and which hand he attributes them to.

### No Buffalo, Vatican, Cambridge, or Modena Images
Four of Russell's six annotated copies have no photographs in the project.
All references to these copies are text-only, with no visual verification
possible.

---

## Deckard Boundary Map: What's Deterministic vs What Needs Judgment

### DETERMINISTIC (can be scripted right now)

| Task | Status | Effort |
|------|--------|--------|
| Re-run BL matching with corrected folios | NOT DONE | 30 min |
| Complete page-number extraction (all 189 photos) | PARTIALLY DONE (27/189) | 2 hours |
| Woodcut inventory (all photos) | PARTIALLY DONE (7 detected) | 2 hours |
| Annotation density map (all photos) | PARTIALLY DONE (27 pages) | 2 hours |
| Build lookup: signature -> photo number | DONE | (in build_bl_ground_truth.py) |

### NEEDS JUDGMENT (LLM-assisted, DRAFT provenance)

| Task | Status | Effort |
|------|--------|--------|
| Verify new alchemical sites (c5v, h8r) against thesis | NOT DONE | 30 min |
| Transcribe visible marginal text | NOT DONE | Full-book: 8+ hours |
| Identify which hand wrote which annotation | NOT DONE | Requires paleographic expertise |
| Compare BL annotations to Buffalo/Vatican equivalents | BLOCKED | No photos for comparison copies |

---

## The Story So Far

### Phase 1: The Naive Pipeline (original build)
Extracted 282 references from Russell's thesis by regex. Built a signature
map from the 1499 collation formula. Cataloged 674 images. Joined via folio
number. Result: 610 matches, but 218 were LOW confidence because the BL
photo-to-folio assumption was unverified.

### Phase 2: The Schema Enrichment (V2 migration)
Added review_status, confidence, needs_review, source_method columns.
Created the annotations, annotator_hands, and folio_descriptions tables.
Added alchemical framework tracking.

### Phase 3: The Image Reading (this session)
Read 27 BL photographs directly. Discovered the offset of 13. Found the
title page confirming 1545 edition. Found Jonson's ownership inscription.
Verified the elephant-obelisk woodcut. Detected 7 woodcuts. Found 2 new
alchemical annotation sites. Confirmed the quire structure.

### Phase 4: The Ground Truth Fix (this session)
Corrected all BL image folio numbers. Created 39 new MEDIUM-confidence
matches. Consolidated the annotations table (282 rows, up from 0).
Classified annotation types. Improved hand attribution to 72%.

---

## What Comes Next

### Immediate (can do now, deterministic)

1. **Re-matching pass.** The 218 original LOW BL matches need to be
   re-evaluated against corrected folio numbers. Many are probably
   pointing at the wrong images entirely (they were 13 positions off).
   The matches should be dropped and rebuilt from scratch using the
   corrected folio data.

2. **Complete page-number reading.** Read remaining 162 BL photographs
   to build a complete page-number verification table. This replaces
   the offset formula with verified data for every page and catches
   any irregularities.

3. **Woodcut detection pass.** Every page that contains a woodcut should
   be flagged. This builds a BL-specific woodcut inventory that can be
   compared against the 172 known woodcuts of the 1499 edition.

### Medium-term (needs some judgment)

4. **Verify new alchemical sites.** Search thesis chunks for Russell's
   discussion of c5v (page 42) and h8r (page 127). Determine whether
   these are Hand B annotations he discusses, or annotations by another
   hand that he doesn't attribute to the alchemist.

5. **Annotation transcription for key folios.** For the 13 folios with
   folio_descriptions (the alchemical analyses), attempt to read and
   transcribe the visible marginal text from the photographs. Compare
   against Russell's quotations.

### Long-term (requires external resources)

6. **Acquire remaining photos.** Buffalo, Vatican, Cambridge, and Modena
   copies need photographs for visual verification. Without them, all
   references to these copies remain text-only.

7. **High-resolution BL images.** The current photographs are adequate
   for page-number reading and woodcut detection, but too low-resolution
   for reliable handwriting transcription or symbol identification.
   Higher-resolution scans would enable more detailed analysis.

---

## Metrics

| Metric | Start of Session | End of Session | Change |
|--------|-----------------|----------------|--------|
| BL offset known | No | Yes (=13) | SOLVED |
| Verified page numbers | 0 | 27 | +27 |
| Woodcuts detected | 0 | 7 | +7 |
| Alchemical sites known | 13 folios | 15 folios | +2 |
| Annotations in table | 0 | 282 | +282 |
| Hand attribution | 193/282 (68%) | 204/282 (72%) | +11 |
| Annotation types | 1 (all MARGINALIA) | 6 types | +5 |
| Match confidence: MEDIUM+ | 392 | 431 | +39 |
| Total matches | 610 | 649 | +39 |
| Site pages | 300 | 335 | +35 |
| Dictionary terms | 80 | 94 | +14 |
| Scholar overviews | 38 | 59 | +21 |
| Timeline events | 42 | 71 | +29 |
| Manuscript copy pages | 0 | 6 | +6 |
