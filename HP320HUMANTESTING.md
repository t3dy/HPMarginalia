# HP320 HUMAN TESTING: Where We Are Running Without Review

> Date: 2026-03-20
> Status: Acknowledged risk. Proceeding.

---

## The Situation

No human review has been performed on any machine-generated output in
this project. Everything downstream of Russell's thesis is either
LLM-assisted, vision-read, or algorithmically derived. The user is
aware and has decided to proceed.

This document tracks where human testing would matter most, ranked by
consequence of errors.

---

## HIGH CONSEQUENCE (errors here break scholarly claims)

### 1. Phase 1 Woodcut Detection (60 detections, 0 reviewed)

**Risk:** Some "woodcuts" may be decorative initials, page ornaments, or
misidentified bleed-through from adjacent pages. The one-sentence
descriptions are vision-model prose, not art-historical terminology.

**What could go wrong:**
- Decorative capital letter counted as a woodcut (inflates inventory)
- Multi-panel page counted as one woodcut vs three (counting inconsistency)
- Description uses wrong subject identification ("figure at a desk" when
  it's actually a specific mythological scene with a known name)

**Current mitigation:** All 60 detections are in `image_readings` with
`concordance_status='UNVERIFIED'`. None have been promoted to the
canonical `woodcuts` table. The gap between 18 (canonical) and 60
(detected) is visible and intentional.

**When to test:** Before running `promote_reading.py`. Spot-check at
least 10 woodcut detections against known HP woodcut catalogs.

### 2. Phase 1 Page Number Readings (174 readings, 0 verified by human)

**Risk:** LOW. The offset formula `page = photo - 13` was confirmed at
174/174 readable points with zero mismatches. This is the strongest
result in the project. A human spot-check of 5-10 pages would take
5 minutes and would likely confirm.

**Current mitigation:** The readings are stored but have not triggered
any database changes. No `matches.confidence` upgrades have been applied.

### 3. Alchemical Site Identifications (3 sites, 0 confirmed)

**Risk:** Pages 28, 42, and 127 were identified as having alchemical
annotations based on vision reading. Page 28 ("bellua") and page 42
(Greek inscription) were already documented by Russell. Page 127
("Synostra Gloria mundi") is a NEW FINDING not cross-referenced against
Russell's thesis.

**What could go wrong:**
- "Synostra Gloria mundi" may not be Hand B (the alchemist) — could be
  another annotator using alchemical-adjacent language
- The annotation may be discussed by Russell in a chapter we haven't
  searched
- "Synostra" may be a misreading of the handwriting

**Current mitigation:** All three are in `image_readings` only. Not in
`symbol_occurrences` or `annotations`. The word PROVISIONAL appears in
the notes.

---

## MEDIUM CONSEQUENCE (errors here affect site quality)

### 4. Annotation Type Classification (282 annotations, 6 types)

All annotation types (MARGINAL_NOTE, CROSS_REFERENCE, SYMBOL, etc.)
were assigned by LLM classification of Russell's text descriptions.
No human has verified that the classification matches what's actually
on each page.

**Risk:** Misclassified annotations would show wrong badges on
marginalia pages. A "CROSS_REFERENCE" might actually be a "MARGINAL_NOTE"
or vice versa.

### 5. Dictionary Terms (94 terms, all DRAFT)

Every `significance_to_hp` and `significance_to_scholarship` paragraph
was LLM-generated from corpus evidence. No human has reviewed any of them.

**Risk:** Factual errors in significance prose. Misattributions.
Anachronistic claims. The terms themselves are correct (from Russell);
the significance prose is the unverified part.

### 6. Scholar Overviews (59 overviews, all DRAFT)

LLM-generated summaries of each scholar's contribution to HP studies.
No human review.

**Risk:** Wrong attribution of arguments. Conflation of scholars.
Overstatement of a scholar's importance or contribution.

### 7. Folio Descriptions (13 descriptions, all LLM-ASSISTED)

Descriptions of alchemist-annotated folios synthesized from Russell's
thesis by LLM. Marked as `source_method='LLM_ASSISTED'`.

**Risk:** Misinterpretation of Russell's arguments. Wrong alchemical
framework assignments. The descriptions are synthesis, not transcription.

---

## LOW CONSEQUENCE (errors here are cosmetic or easily fixed)

### 8. Gallery Card Descriptions (223 entries)

Auto-generated one-sentence descriptions for each gallery card in
`data.json`. Built from hand labels, attribution, and marginal text.

### 9. Bibliography Entries (109, all UNREVIEWED)

Ingested from thesis references. Author names, titles, and dates may
have OCR errors from PDF extraction.

### 10. Site HTML/CSS

No cross-browser testing. No accessibility audit. No mobile testing
beyond basic responsive layout. The site works in Chrome on desktop.

---

## What "Human Testing" Would Actually Look Like

If time becomes available, the highest-value reviews would be:

| Priority | Task | Time | Impact |
|----------|------|------|--------|
| 1 | Spot-check 10 Phase 1 woodcut detections against page images | 15 min | Validates the 60-count inventory |
| 2 | Verify "Synostra Gloria mundi" (page 127) against Russell Ch. 5-9 | 20 min | Confirms or rejects new alchemical site |
| 3 | Read 5 dictionary significance paragraphs for factual accuracy | 15 min | Calibrates quality of all 94 |
| 4 | Read 3 scholar overviews for accuracy | 10 min | Calibrates quality of all 59 |
| 5 | Click through 10 marginalia pages checking annotation type badges | 10 min | Validates classification pipeline |

Total: ~70 minutes for meaningful calibration of the entire project's
machine-generated output.

---

## Current Policy

All unreviewed machine output remains in the system with appropriate
provenance flags:
- `source_method = 'LLM_ASSISTED'` or `'VISION_MODEL'`
- `needs_review = 1`
- `confidence = 'PROVISIONAL'` or `'DRAFT'`

Nothing has been marked VERIFIED that wasn't verified. The risk is not
that wrong data is masquerading as correct — it's that unreviewed data
is being surfaced on a public website with only provenance badges
(not paywalls or warnings) distinguishing it from verified scholarship.

The user has accepted this risk and chosen to proceed.
