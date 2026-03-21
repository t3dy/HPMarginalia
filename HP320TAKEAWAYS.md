# HP320 TAKEAWAYS: What We're Learning from Phase 1 Image Reading

> In-progress notes. 139/189 BL photos processed. 50 remaining.
> Date: 2026-03-20

---

## The Offset Is Rock Solid

124 text pages have readable page numbers. Every single one matches the
offset formula `page = photo - 13`. Zero mismatches. Zero. The formula
that was verified at 27 points in the previous session is now verified
at 124 points across the full range of the book.

15 photos have no readable page number — these are either pre-text pages
(photos 1-13) or full-page woodcuts where the illustration obscures the
printed page number (photos 58, 93). This is expected and not a
discrepancy.

**Conclusion:** The BL offset is confirmed. We can trust
`folio = photo - 13` for every sequential scan in the collection.

---

## Woodcut Count Is Much Higher Than Expected

The previous 27-page sample found 7 woodcuts and estimated ~45 total.
After 139 photos (covering pages 1-126), we've found **38 woodcuts**.
That's already more than double the previous estimate from the sample —
and we still have 50 photos to go.

The earlier estimate extrapolated linearly (7/27 = 26%, times 176 pages
= ~45). The actual distribution is not linear. Woodcuts cluster heavily
in certain sections:

| Section | Pages | Woodcuts | Rate |
|---------|-------|----------|------|
| Pre-text (1-13) | 13 | 1 | 8% (title page device) |
| Quires a-b (1-28) | 28 | 12 | 43% |
| Quires c-d (29-56) | 28 | 4 | 14% |
| Quires e-f (57-84) | 28 | 5 | 18% |
| Quires f-h (85-126) | 42 | 16 | 38% |

The densest woodcut zones are the early architectural descriptions
(quires a-b, pages 1-28) and the palace/garden sequences (quires f-h,
pages 85-126). The middle sections (quires c-d) are predominantly text.

**Projected final count:** At the current rate (~38 in 126 pages), the
full 176-page scan may contain 50-55 woodcuts. But the remaining 50
photos cover pages 127-176, which includes the triumphal procession
sequence (known to be woodcut-heavy). Final count could reach 60+.

---

## What We're Learning About Woodcut Types

The woodcuts fall into clear categories that weren't visible from
Russell's text descriptions alone:

### 1. Narrative Scenes (~12 so far)
Full or half-page illustrations showing Poliphilo in action:
- Entering the dark forest (p.4)
- Sleeping by the stream (p.8, p.10)
- Confronting the dragon (p.52)
- Meeting the five nymphs (p.66)
- At the queen's court (p.90)
- At the three doors (p.125)
- Approaching the garden portal (p.126)

### 2. Architectural/Monument Illustrations (~10 so far)
Buildings, monuments, and inscribed objects:
- The great pyramid (p.16)
- Twin inscription monuments (p.23)
- Elephant and Obelisk (p.28) — key alchemical site
- The grand portal (p.45)
- The palace interior with planetary chambers (p.88)
- The obelisk with Greek text (p.119)

### 3. Decorative Objects (~8 so far)
Furniture, vessels, and ornamental objects:
- Tripod table (p.93)
- Ornamental urn (p.94)
- Caryatid table (p.95)
- Candelabra (p.102)
- Fountain chariot (p.105)
- Elaborate tiered fountain (p.80)

### 4. Emblematic/Symbolic (~5 so far)
Medallions, friezes, and inscribed emblems:
- Hieroglyphic frieze (p.31)
- PATIENTIA emblems (p.59)
- GELOIASTOS scene (p.75)
- Grotesque frieze (p.87)
- Medallion portraits (p.92, p.122)

### 5. Figural Groups (~3 so far)
Allegorical groups without clear narrative action:
- TEMPVS figures (p.24)
- Crowned classical figures (p.25)
- Putto/Cupid on fountain (p.71)

**Why this matters:** Our `woodcuts` table currently has 18 entries with
minimal categorization. Phase 1 is producing a vocabulary for
`subject_category` that the database doesn't yet capture. When we
promote these readings, we'll need subject categories like NARRATIVE,
ARCHITECTURAL, DECORATIVE_OBJECT, EMBLEMATIC, and FIGURAL.

---

## What We're Learning About the System

### 1. The Compressed Images Would Have Been Useless

Multiple pages have page numbers that are small, faint, or partially
obscured. At 200KB / 800px wide (the web derivative resolution), these
numbers would likely be unreadable. The master images at 4MB give enough
resolution to read even marginal annotations — the page numbers are easy
by comparison. The image source boundary enforcement is not paranoia;
it's load-bearing.

### 2. Full-Page Woodcuts Break Page Number Extraction

Photos 58 (page 45) and 93 (page 80) are full-page woodcuts where the
illustration covers the entire page. No page number is visible. This is
not a failure of the vision model — the number literally isn't there.
The comparison script needs to handle `page_number_readable = false`
as a valid state, not a discrepancy.

### 3. Small Decorative Woodcuts Need a Size Threshold

Some pages have tiny decorative initials (historiated capitals at chapter
openings). I've been excluding these and only counting significant
illustrations — but the boundary is judgment-based. Phase 3 deep
reading should establish a clearer criterion. For now, the rule is:
"Only count illustrations that occupy at least ~1/6 of the page area."

### 4. Annotations Are Everywhere but Not Uniform

Almost every page has some marginal annotation. The density varies
dramatically:
- Pre-text pages (esp. 7, 8, 9): MOST DENSE in the entire book
- Early quires (a-c): Heavy throughout
- Middle quires (d-f): Moderate, concentrated around woodcuts
- Late quires (g-h): Variable — some heavy, some light

Phase 2 will quantify this properly. But the pattern is already clear:
readers engaged most with the beginning and with visually striking
passages.

### 5. The Alchemical Sites Are Visible

On page 42 (photo 55), the Greek inscription page, I can see small
marks at the bottom left margin that are consistent with alchemical
ideograms. On page 28 (photo 41, the Elephant and Obelisk), the
marginal text including "bellua" is visible above the woodcut. These
are the two sites Russell discusses most intensely. The master images
have sufficient resolution to detect annotation presence — though
identifying specific alchemical symbols remains beyond reliable
automated reading.

---

## What This Means for the Database

### Woodcuts Table Needs Expansion

Current: 18 woodcuts cataloged.
Phase 1 so far: 38 detected (will likely reach 55-65).
Gap: ~40 woodcuts not in the database.

After Phase 1 completes and results are reviewed, the promotion path
would add ~40 new `woodcuts` rows with:
- `source_method = 'VISION_MODEL'`
- `confidence = 'PROVISIONAL'`
- `subject_category` from the taxonomy above
- `has_bl_photo = 1`
- `bl_photo_number` from the reading

### Concordance Confidence Can Be Upgraded

Every page where the offset is confirmed is a candidate for upgrading
the corresponding `matches` entry from MEDIUM to HIGH confidence. But
per the plan, this requires human review — the comparison script will
flag upgrade candidates, not execute them.

### Phase 2 Targeting Is Already Informed

The pages with the densest annotations (7, 8, 9, 14, 20, 28, 33, 42,
112, 125) are strong candidates for Phase 3 deep reading. Phase 2 will
formalize this, but we already know where to look.

---

## Open Questions

1. **Are the decorative objects woodcuts or are they metalcuts?**
   Some HP scholars distinguish between woodcut illustrations and
   metalcut decorative objects. Our system doesn't yet capture this
   distinction. Does it matter for our purposes?

2. **Should the Aldine device on the title page count as a woodcut?**
   It's a printer's device, not a narrative illustration. I've counted
   it (has_woodcut=true) but it's categorically different from the
   illustrations inside the text.

3. **How do we handle the shaped text (technopaegnia)?**
   Pages 104 and 106 have text arranged in triangular/tapering shapes.
   These aren't woodcuts — they're typographic art. But they're
   visually distinctive page elements that our system should eventually
   capture. Not in Phase 1 scope.

4. **The 1545 vs 1499 woodcut question:** Are these the same woodblocks
   as the 1499 edition, or were they re-cut? Image comparison with
   Siena (Phase 4) would reveal this. For now we're just inventorying.
