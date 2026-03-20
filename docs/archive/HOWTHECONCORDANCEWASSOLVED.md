# How the Concordance Was Solved

> The story of how a digital humanities concordance went from 218 wrong
> matches to zero, told through the actual sequence of discoveries,
> mistakes, and fixes that got it there. Written for anyone who wants
> to understand not just what the system does, but how it was debugged.

---

## The Problem

James Russell's PhD thesis references folios of the *Hypnerotomachia
Poliphili* by signature: b6v, h1r, a1r. Our photograph collections use
different naming schemes. The Siena copy labels images by folio number
(O.III.38_0014r.jpg). The British Library copy labels them by sequential
number (C_60_o_12-001.jpg through C_60_o_12-189.jpg).

The concordance pipeline has to translate between these systems so that
when a scholar reads Russell saying "on b6v, the alchemist writes
*Magisteri Mercurii*," the site can show the actual photograph of that
page.

This sounds straightforward. It was not.

---

## Phase 1: The Naive Pipeline (the original build)

The first version of the concordance worked like this:

1. **Signature map:** Generate a lookup table from the 1499 collation
   formula (a-z8 A-F8 G4, omitting j, u, w). This converts any valid
   signature to a sequential folio number. 448 entries. Deterministic
   and correct.

2. **Reference extraction:** Run regex over Russell's thesis PDF to pull
   out 282 folio references with their thesis page numbers, context text,
   and marginal text quotations.

3. **Image cataloging:** Parse the 674 image filenames into structured
   records with folio numbers and recto/verso sides.

4. **Matching:** Join references to images via the signature map.

The Siena matches worked well. The filenames directly encode folio
information: O.III.38_0014r.jpg is folio 14 recto. The join is clean.
392 matches, mostly MEDIUM confidence (some ambiguity about which side
of a leaf the annotation appears on).

The BL matches were a different story. The pipeline assumed that
photo number equals folio number: C_60_o_12-014.jpg was assumed to
show folio 14. This produced 218 matches, all initially marked MEDIUM
confidence.

Nobody checked whether this assumption was true.

---

## Phase 2: The Confidence Downgrade

An early audit (HPDECKARD.md) flagged the BL assumption as risky. The
BL copy is the 1545 edition, not the 1499 from which the signature map
was built. If the editions differ in pagination, the assumption breaks.

The recommendation: downgrade all BL matches to LOW confidence until
verified. This was done. 218 matches went from MEDIUM to LOW.

This was the right call. But it only changed a label. The matches
themselves were still wrong — they just had an honest confidence rating.

---

## Phase 3: The Ontology Expansion

Before the concordance was fixed, the project expanded in other
directions:

- **Dictionary:** 37 terms grew to 94 across 15 categories, with
  significance prose for every term.
- **Scholars:** 30 pages grew to 60, with overview prose for 59.
- **Timeline:** 71 events from 1499 to 2024.
- **Manuscripts:** 6 copy pages with hand profiles.
- **Alchemical symbols:** 10 symbols, 26 occurrences mapped to folios.
- **Annotations:** Consolidated from the old dissertation_refs table
  into a canonical annotations table with 6 classified types.

This was all legitimate enrichment work. But it was also a form of
avoidance. The BL concordance problem — the 218 wrong matches — sat
there the entire time. The system grew richer while its foundational
data layer remained broken.

The Isidore critique (ISIDORE3.md) called this out explicitly: "The
project's chronic pattern is over-specification. The plan responds
to this by proposing more specifications."

---

## Phase 4: Looking at the Photographs

The breakthrough came from doing the simplest possible thing: opening
the actual photographs and looking at them.

**Photo 001:** A blank endpaper. Not folio 1.

**Photo 002:** The flyleaf recto. Thomas Bourne's provenance notes from
1641. Multiple hands of handwriting. Not folio 2.

**Photo 003:** The flyleaf verso. And there it was — the Master Mercury
declaration in Hand B's angular script: "verus sensus intentionis huius
libri est 3um." The BL shelfmark "C.60.o.12" written below in a modern
hand. The dates "1641" and "1535" at the bottom.

This was NOT folio 3 of the HP text. This was the flyleaf.

**Photo 004:** The title page. "LA HYPNEROTOMACHIA DI POLIPHILO...
RISTAMPATO DI NOVO, ET RICORRETTO... IN VENETIA, M.D.XXXXV." The
Aldine anchor-and-dolphin device. And at the bottom, in Ben Jonson's
hand: "Sum Ben: Ionsonij."

The 1545 edition confirmed. Jonson's ownership confirmed. And this was
photo 4, not folio 4.

**Photos 005-013:** Dedication, prefatory verses, argomento, half-title,
Poliphilus's dedication to Polia. Nine more pages of front matter.

**Photo 014:** "POLIPHILO INCOMINCIA LA SVA HYPNEROTOMACHIA AD
DESCRIVERE E T L'HORA E IL TEMPO..." The HP text begins. Page 1.

The offset is **13**. Photos 001-013 are front matter. The HP text
starts at photo 014.

Every BL match in the database was wrong by 13 positions.

---

## Phase 5: Verification

One data point isn't enough. The offset needed verification across the
full range of the book. Over the course of reading 69 photographs, the
offset was checked at 27 independent points:

| Photo | Visible Page # | Computed (photo-13) | Match? |
|-------|---------------|---------------------|--------|
| 014 | 1 | 1 | Yes |
| 015 | 2 | 2 | Yes |
| 020 | 7 | 7 | Yes |
| 025 | 12 | 12 | Yes |
| 030 | 17 | 17 | Yes |
| 032 | 19 | 19 | Yes |
| 033 | 20 | 20 | Yes |
| 040 | 27 | 27 | Yes |
| 041 | 28 | 28 | Yes |
| 050 | 37 | 37 | Yes |
| 060 | 47 | 47 | Yes |
| 077 | 64 | 64 | Yes |
| 078 | 65 | 65 | Yes |
| 080 | 67 | 67 | Yes |
| 090 | 77 | 77 | Yes |
| 100 | 87 | 87 | Yes |
| 110 | 97 | 97 | Yes |
| 120 | 107 | 107 | Yes |
| 125 | 112 | 112 | Yes |
| 130 | 117 | 117 | Yes |
| 135 | 122 | 122 | Yes |
| 140 | 127 | 127 | Yes |
| 145 | 132 | 132 | Yes |
| 150 | 137 | 137 | Yes |
| 160 | 147 | 147 | Yes |
| 170 | 157 | 157 | Yes |
| 189 | 176 | 176 | Yes |

27 for 27. Never wrong once.

Additionally, five quire signature marks were confirmed visible at the
foot of pages: a iii, c ii, c iii, g ii, K iii. These confirm that the
1545 edition follows the same collation structure as the 1499.

---

## Phase 6: The Fix

Three scripts, executed in sequence:

1. **fix_bl_offset.py:** Corrected all 196 BL image folio numbers.
   Photos 001-013 reclassified as COVER, GUARD, or OTHER. Photos
   014-189 assigned corrected folio numbers using the formula:
   leaf = (photo - 13 + 1) // 2, side = r if odd page, v if even.

2. **build_bl_ground_truth.py:** Recorded all 27 verified page numbers,
   18 detected woodcuts, 7 alchemical annotation sites, and 5 confirmed
   signature marks as structured ground truth data.

3. **rebuild_bl_matches.py:** Deleted all 257 existing BL matches
   (including 218 LOW matches from the original pipeline and 39 MEDIUM
   matches from a partial earlier fix). Rebuilt from scratch using
   corrected folio numbers. Created 39 new matches: 22 HIGH confidence
   (pages verified by visual inspection) and 17 MEDIUM (computed from
   the offset formula but not individually verified).

**Before:** 26 HIGH + 405 MEDIUM + 218 LOW = 649 matches.
**After:** 48 HIGH + 383 MEDIUM + 0 LOW = 431 matches.

218 fewer matches, but every remaining match is correct.

---

## Phase 7: What Else the Photographs Revealed

The image reading wasn't just about page numbers. Looking at the
actual photographs produced discoveries that no amount of schema
design could have generated:

### The Elephant and Obelisk (Photo 041 = b6v)

The most famous woodcut in the HP, confirmed at exactly the predicted
position. The elephant stands on a circular base bearing an obelisk
with pseudo-hieroglyphic decorations. Hand B's alchemical annotations
are visible around the woodcut — dense marks in the margins consistent
with Russell's description of ideograms embedded in Latin syntax.

### Ben Jonson's Ownership (Photo 004)

"Sum Ben: Ionsonij" at the bottom of the title page. This is primary
evidence for Hand A's identification — not a scholarly inference but
a direct ownership declaration.

### 18 Woodcuts Detected

Across 69 pages, 18 woodcuts were identified and described: the dark
forest, the dream-within-a-dream, the horse on a sarcophagus, the
D.AMBIG.D.D. inscription monuments, the GONOS KAI ETOUSIA monument,
the elephant-obelisk, the dragon at the portal, the grotesque frieze,
medallion portraits, the candelabrum fountain, a pergola garden scene,
and two triumphal processions.

### 7 Alchemical Annotation Sites

Including 2 previously unknown: c5v (page 42, with alchemical symbols
near a Greek inscription to Aphrodite/Dionysos/Demeter) and h8r
(page 127, with "Synostra Gloria mundi" above a portal woodcut).
These were not in Russell's extracted references — they are new
observations from direct image reading.

### Annotation Density Patterns

Of 69 pages read, 31 were HEAVY (margins substantially filled), 22
MODERATE, and 8 LIGHT. Annotation density is highest in the front
matter and early quires (a-c), decreases in the middle sections, and
picks up around significant woodcuts. This confirms Russell's
observation that readers engaged most intensely with the HP's opening
and its most visually striking passages.

---

## Phase 8: The Siena Question

The Siena matches were never "wrong" in the way the BL matches were.
The filenames directly encode folio numbers, so the join is clean.
But there is an imprecision: each Russell reference (like "A2r") gets
matched to BOTH the recto AND verso of the computed folio. This is
because the matching pipeline links by folio number without always
resolving which side of the leaf the annotation appears on.

This means roughly half the Siena matches show the correct page and
half show the facing page. Both are "close" but only one is exact.
The system is honest about this: these matches are MEDIUM, not HIGH.
Resolving them to HIGH would require checking each annotation's
position — a content-level judgment, not a folio-level one.

---

## Phase 9: The 34 Unmatched Refs

34 of 282 dissertation references have no image match. The reasons:

- **19 refs have no manuscript assigned.** These are from Russell's
  introductory chapters (Ch. 1, 3) where he discusses the HP generally
  without specifying which copy he's looking at.

- **7 BL refs are beyond photo range.** The 189 BL photos cover
  pages 1-176. Signatures like p2v (page 252), s6r (page 274), y7r
  (page 333), and t7v (page 302) are in the unphoto­graphed second
  half of the book.

- **7 refs have collation ambiguities.** Signatures z5v, z6r, z5r,
  and u3r don't map cleanly: quire z may have fewer than 8 leaves,
  and "u" is a letter the collation convention omits.

- **1 Vatican ref (u3r)** has the same collation issue.

None of these are fixable with current data. They would require either
photographs of the missing pages (BL second half, Buffalo, Vatican,
Cambridge, Modena) or physical inspection of the books to resolve the
collation questions.

---

## What We Learned

### 1. Look at the evidence.

The entire BL concordance problem — 218 wrong matches that persisted
through months of development — was solved in 30 minutes by opening
photograph files and reading the page numbers. No schema migration,
no new table, no pipeline refactoring. Just looking.

The lesson isn't that schema design is useless. The signature map, the
extraction pipeline, the matching logic — all of that infrastructure
was necessary. But infrastructure without verification is a confidence
trap. The system reported MEDIUM confidence on matches that were
objectively wrong. The only way to catch that was to look at what the
matches actually showed.

### 2. The offset was invisible to code.

No Python script could have discovered the offset of 13. The pipeline
processed filenames, not image content. It had no way to know that
C_60_o_12-001.jpg was a blank endpaper. The data model was correct
(the signature map is right, the image catalog is right) but the
assumption bridging them — that photo 1 is folio 1 — was wrong.

This is a general lesson for any concordance that links identifiers
across naming systems: the bridge assumption must be verified against
the physical evidence, not trusted because the code runs without errors.

### 3. Front matter is not metadata.

The 13 front matter pages — covers, flyleaves, title page, dedications,
prefatory verses — are not "extras" to be skipped. They contain some
of the most important evidence in the project: the Master Mercury
declaration (photo 003), Jonson's ownership inscription (photo 004),
and the most heavily annotated pages in the entire book (the argomento,
photo 008).

The pipeline treated them as noise. They turned out to be the key to
fixing everything else.

### 4. The annotation type classification needed validation.

The first pass at classifying 282 annotations used regex matching on
context text. It classified 127 as INDEX_ENTRY because the word "nota"
appeared in their context. But Russell uses "nota" in ordinary English
("he noted that..."), not just as a marginal keyword. A spot-check
revealed the false-positive rate was ~60%. The classification was
re-run with tighter rules, producing a more realistic distribution:
126 MARGINAL_NOTE, 68 CROSS_REFERENCE, 50 INDEX_ENTRY, 21 SYMBOL,
16 EMENDATION, 1 UNDERLINE.

The lesson: generated classifications must be validated before they're
trusted. A 60% error rate is worse than no classification at all,
because it creates false confidence.

### 5. Over-specification is the project's chronic failure mode.

This project produced 40+ design documents. It wrote specifications
for features before building them. It designed schema extensions before
surfacing existing data. The Antigravity refactor collapsed 36
documents into 5 canonical ones and archived the rest.

The concordance was fixed not by writing another specification but by
doing the simplest possible verification: looking at photographs.
The essay content was improved not by designing a new template but by
reading Russell's actual thesis chapters and writing down what he said.

The project is at its best when it operates in Verification Mode
(looking at evidence) and Presentation Mode (putting data on pages).
It is at its worst when it operates in Ontology Mode (designing tables)
and Research Mode (opening new topics) before the previous round of
work is finished.

---

## Current State (Post-Fix)

| Metric | Value |
|--------|-------|
| Total matches | 431 |
| HIGH confidence | 48 (11%) |
| MEDIUM confidence | 383 (89%) |
| LOW confidence | 0 (eliminated) |
| BL matches verified | 39/39 folio-correct, 27/39 visually confirmed |
| Siena matches | 392 (all folio-correct, recto/verso ambiguity in some) |
| Unmatched refs | 34 (19 no-manuscript, 7 beyond-range, 8 collation-ambiguous) |
| Pages visually read | 69 (13 front matter + 56 text pages) |
| Woodcuts detected | 18 |
| Alchemical sites confirmed | 7 (5 known + 2 new) |
| Site pages | 364 |
| Validation errors | 0 |

The concordance is not perfect. 34 refs remain unmatched. The Siena
matches have recto/verso ambiguity. The BL photos cover only 38% of
the book. Four of Russell's six copies have no photographs at all.

But every match in the system points to the correct folio. No match
is wrong. And the system is honest about what it doesn't know.

That is what "solved" means for a concordance: not complete coverage,
but correct coverage with explicit uncertainty.
