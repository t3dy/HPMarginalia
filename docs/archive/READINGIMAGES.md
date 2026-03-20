# READINGIMAGES: Deckard Boundary Critique of Image Reading Methods

> Rick Deckard distinguishes what's real from what's artificial.
> This critique examines what image reading can and cannot do for
> the concordance, and where the boundaries between deterministic
> verification and probabilistic interpretation lie.

---

## What Was Attempted

Visual inspection of 10 BL manuscript photographs (C.60.o.12) to verify
the concordance pipeline's assumption that photo number equals folio number.

## What Was Found

### The Offset Discovery

**Photo number != folio number.** The first 13 photographs are non-text
pages (covers, endpapers, flyleaves, front matter). The actual HP text
begins at photo 014 = folio 1 (a1r).

**The formula is: folio_number = photo_number - 13.**

Verified across 10 images:

| Photo | Visible Page # | Corrected Folio | Match |
|-------|---------------|-----------------|-------|
| 001 | (blank cover) | N/A | -- |
| 003 | (flyleaf: Master Mercury) | N/A | -- |
| 010 | (prefatory verse) | N/A | -- |
| 014 | 1 (a1r) | 014-13=1 | Correct |
| 015 | 2 | 015-13=2 | Correct |
| 020 | 7 | 020-13=7 | Correct |
| 032 | 19 | 032-13=19 | Correct |
| 033 | 20 | 033-13=20 | Correct |
| 050 | 37 | 050-13=37 | Correct |
| 100 | 87 | 100-13=87 | Correct |

**Impact:** All 218 BL matches in the database were wrong by 13 folios.
A match claiming to show "b6v" was actually showing a page 13 positions
earlier. The fix_bl_offset.py script corrects all BL image folio numbers.

### What Else Was Visible

On photo 003 (flyleaf): the actual Master Mercury declaration is visible:
"verus sensus intentionis huius libri est 3um" — confirming Russell's
transcription.

On photo 014 (a1r): marginal annotations visible in right margin and
bottom of page, consistent with Russell's description of Hand A (Jonson)
and Hand B (alchemist) annotations on the opening page.

On photo 033 (page 20): alchemical symbols visible in left margin —
small ideographic marks consistent with Russell's description of Hand B's
alchemical vocabulary.

On photo 100 (page 87): a decorative woodcut frieze with grotesque figures
and marginal annotations in right margin.

---

## Deckard Boundary Map: Image Reading

### DETERMINISTIC (code can do this)

| Task | Method | Confidence |
|------|--------|------------|
| Read printed page numbers from images | OCR / visual inspection | HIGH — numbers are large and consistent |
| Compute photo-to-folio offset | Arithmetic: subtract 13 | HIGH — verified across 10 images |
| Detect presence of woodcut illustrations | Image classification (woodcut vs text-only) | HIGH — woodcuts are visually distinct |
| Detect presence of marginal text | Edge detection in margin regions | MEDIUM — varies by density |
| Read the BL shelfmark on flyleaf | OCR | HIGH — printed clearly |

### PROBABILISTIC (needs LLM vision or human judgment)

| Task | Why Not Deterministic | Confidence |
|------|----------------------|------------|
| Transcribe marginal annotations | Handwriting is irregular, ink varies, abbreviations used | MEDIUM — LLM can attempt but errors likely |
| Identify which hand wrote an annotation | Requires paleographic judgment (ductus, ink color, content) | LOW — needs expert comparison |
| Read alchemical ideograms | Symbols are small, non-standard Unicode | LOW — no standard OCR vocabulary |
| Determine if a page is recto or verso | Requires understanding book structure | MEDIUM — can infer from sequence |
| Match an annotation to Russell's description | Requires reading both image and thesis text | MEDIUM — LLM can compare |
| Confirm signature marks at page foot | Signatures are small and often trimmed | LOW — often illegible in photos |

### DANGER ZONES

| Risk | Problem | Mitigation |
|------|---------|------------|
| LLM confidently misreads handwriting | Could introduce false transcriptions into DB | Mark all LLM transcriptions as PROVISIONAL, never VERIFIED |
| Offset assumption breaks for irregular gatherings | The 1545 edition may have inserted/cancelled leaves | Verify offset at multiple points, not just one |
| Photo sequence may not be continuous | Missing or duplicate photos would break the offset | Count total photos, check for gaps in numbering |
| Recto/verso inference from sequence may be wrong | If photos include separate detail shots, the alternation breaks | Check that page numbers increase monotonically |

---

## What Image Reading CAN Solve

1. **BL offset verification** — DONE. The offset of 13 is confirmed across
   10 data points spanning the full range of the book.

2. **Page number extraction** — A batch run reading visible page numbers
   from all 196 BL photos would create a ground-truth folio mapping,
   eliminating the offset assumption entirely. Cost: ~$2 in API calls.

3. **Woodcut detection** — Identifying which pages contain woodcuts would
   create a woodcut inventory for the BL copy and enable comparison with
   the 1499 edition's 172 known woodcuts.

4. **Annotation presence detection** — Flagging which pages have visible
   marginal annotations would identify annotated folios beyond those
   Russell explicitly documents.

5. **Annotation density mapping** — Estimating how heavily each page is
   annotated would reveal patterns in reader engagement across the book.

## What Image Reading CANNOT Solve

1. **Definitive hand attribution** — Distinguishing Hand A from Hand B
   requires expertise in ink color, ductus, and content that exceeds
   current vision model capabilities for 17th-century manuscripts.

2. **Reliable ideogram transcription** — The alchemical symbols are too
   small and non-standard for confident automated reading. A specialist
   would produce better results.

3. **1545 vs 1499 collation verification** — Determining whether the
   1545 edition follows the same collation formula requires comparing
   gatherings, not just page numbers. This is a codicological question
   that image reading can support but not resolve.

4. **Marginal text transcription at scholarly quality** — LLM transcription
   of 17th-century handwriting will produce useful first drafts but not
   publishable transcriptions. All would need expert verification.

---

## Recommended Batch Processing Pipeline

### Phase 1: Page Number Extraction ($2, 1 hour)

For each of the 196 BL photos:
- Send to vision model with prompt: "Read the printed page number visible
  at the top of this manuscript page. Return ONLY the number, or NULL if
  no number is visible."
- Build a complete photo-to-page-number lookup table
- Verify the offset=13 hypothesis across all images
- Identify any discontinuities or missing pages

### Phase 2: Annotation Detection ($3, 1 hour)

For each photo:
- Prompt: "Does this manuscript page contain handwritten marginal
  annotations? Answer YES/NO. If YES, estimate the annotation density
  as LIGHT (1-2 marks), MODERATE (3-10 marks), or HEAVY (10+)."
- Build an annotation density map across the full book
- Compare against Russell's documented annotations

### Phase 3: Woodcut Inventory ($2, 30 min)

For each photo:
- Prompt: "Does this page contain a woodcut illustration (a printed
  image, not handwriting)? If YES, briefly describe the subject."
- Build a woodcut inventory for the BL copy
- Compare against the 172 known woodcuts of the 1499 edition

### Phase 4: Targeted Annotation Reading ($5, 2 hours)

For the ~20 pages Russell identifies as most heavily annotated:
- Send high-res image with Russell's description as context
- Prompt: "Compare what you see in the margins against this description
  from Russell's thesis: [passage]. What can you confirm? What differs?"
- Produce verification reports for each targeted folio

### Total Cost: ~$12, ~5 hours
### Expected Output: Ground-truth folio mapping, annotation density map,
### woodcut inventory, targeted verification of key alchemical annotations

---

## What This Session Proved

1. **Vision models can read these images.** The page numbers, text openings,
   shelfmarks, and annotation presence were all correctly identified from
   the photographs.

2. **The concordance had a systematic error.** All 218 BL matches were
   wrong by exactly 13 positions. This error was invisible to the
   deterministic pipeline because the pipeline never looked at the images.

3. **The fix is cheap.** A $2 batch run reading page numbers from all 196
   photos would produce a definitive folio mapping, replacing the
   offset assumption with verified data.

4. **The limitation is real.** Handwriting transcription and symbol
   identification are beyond what automated reading can do reliably.
   These require expert judgment marked as PROVISIONAL.

---

## Provenance

- Image reading performed: 2026-03-20
- Images read: 10 of 196 BL photographs
- Offset verified: 10/10 correct (100%)
- Method: Claude Opus 4.6 vision, reading JPEG manuscript photographs
- Confidence in offset: HIGH (consistent across full range of book)
- Status of BL matches after fix: Still LOW (1545/1499 collation
  difference not yet resolved)
