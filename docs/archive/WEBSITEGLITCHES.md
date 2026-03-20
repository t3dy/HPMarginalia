# WEBSITEGLITCHES: Problems, Troubleshooting, and Solutions

> Every glitch encountered during the site build, how it was diagnosed,
> and how it was fixed. Written so future sessions don't repeat them.

---

## 1. BL Photo-to-Folio Offset (THE BIG ONE)

**Problem:** All 218 BL image matches were wrong by 13 positions. The
concordance pipeline assumed photo number = folio number. It was wrong.

**Diagnosis:** Reading actual BL photographs revealed that photos 001-013
are covers, flyleaves, and front matter. The HP text starts at photo 014.

**Fix:** `fix_bl_offset.py` corrected all 196 image folio numbers.
`rebuild_bl_matches.py` deleted 257 stale matches and created 39 correct
ones. Verified at 27 data points across the full book.

**Lesson:** No amount of schema design substitutes for looking at the
actual evidence.

---

## 2. Annotation Type Classification Overfitting

**Problem:** The first classification pass assigned 127 of 282 annotations
as INDEX_ENTRY because the word "nota" appeared in their context. But
Russell uses "nota" in ordinary English ("he noted that...").

**Diagnosis:** Spot-check of 20 INDEX_ENTRY classifications revealed a
~60% false-positive rate.

**Fix:** Reclassified with tighter rules. New distribution: 126
MARGINAL_NOTE, 68 CROSS_REFERENCE, 50 INDEX_ENTRY, 21 SYMBOL, 16
EMENDATION, 1 UNDERLINE.

**Lesson:** Generated classifications must be validated before being
trusted. Regex matching on natural language context produces noise.

---

## 3. Unicode Encoding Errors on Windows

**Problem:** Python print() statements with Unicode characters (arrows,
em dashes, special quotes) failed on Windows with cp1252 encoding errors.

**Diagnosis:** Windows default console encoding (cp1252) cannot represent
many Unicode characters that appear in the HP text and scholarly prose.

**Fix:** Changed arrow characters in print statements from Unicode to
ASCII equivalents ("→" to "->"). For file I/O, always specify
encoding='utf-8'.

**Lesson:** Always use ASCII in console output on Windows. Always
specify encoding='utf-8' when reading/writing files.

---

## 4. Image Paths Breaking on GitHub Pages

**Problem:** Images referenced via deep directory paths (e.g.,
`3 BL C.60.o.12 Photos-20260319T001113Z-3-001/3 BL C.60.o.12 Photos/`)
were 404ing because these directories were not in the site/ deployment.

**Diagnosis:** The original image directories were outside site/ and
were not committed to git. Even if committed, the directory names with
spaces and special characters caused URL encoding issues.

**Fix:** Compressed images into `site/images/bl/` and `site/images/siena/`
with clean filenames. Updated database paths. BL images compressed from
~4 MB to ~200 KB each.

**Lesson:** Deploy images inside site/ with simple paths. Never rely on
deep directory structures with spaces for web serving.

---

## 5. Gallery 404s After Path Migration

**Problem:** After updating image paths in the database, the gallery still
showed 404s for old paths.

**Diagnosis:** The browser cached the old data.json and old page loads.
The network log showed stale requests from before the rebuild.

**Fix:** Rebuilt the site (regenerating data.json with new paths). The
404s were from cached previous loads, not from the current build.

**Lesson:** When debugging image 404s, check whether the current data.json
has the right paths before assuming the code is wrong. Browser caching
creates false negatives.

---

## 6. CHECK Constraint on timeline_events.event_type

**Problem:** `seed_timeline_v2.py` tried to insert events with types
ART, SCHOLARSHIP, LITERARY — but the table's CHECK constraint only allows
PUBLICATION, EDITION, TRANSLATION, DISCOVERY, ATTRIBUTION, ACQUISITION,
EXHIBITION, OTHER.

**Diagnosis:** The CREATE TABLE statement has a restrictive CHECK
constraint that wasn't updated when new event types were conceived.

**Fix:** Mapped new event types to OTHER and used the `category` column
for the real type label. ART events are stored as event_type='OTHER',
category='art'.

**Lesson:** Check DB constraints before inserting new enum values. Use
flexible category fields alongside strict type constraints.

---

## 7. Git Index Lock File

**Problem:** `git commit` failed with "Unable to create index.lock: File
exists."

**Diagnosis:** A previous git process (possibly from another terminal
window) left a stale lock file.

**Fix:** `rm -f .git/index.lock` then retry the commit.

**Lesson:** If git operations fail with lock errors, check for stale
lock files. This happens when git processes are interrupted.

---

## 8. SyntaxError from Escaped Quotes in f-strings

**Problem:** Attempting to use escaped single quotes (`\'`) inside an
f-string for inline HTML generation caused a SyntaxError.

**Diagnosis:** Python f-strings don't support backslash escapes inside
the expression part of the string.

**Fix:** Moved the HTML generation to a separate variable built with
string concatenation, then inserted into the f-string.

**Lesson:** Don't try to embed complex HTML with quotes inside f-string
expressions. Build the HTML string separately.

---

## 9. Siena Recto/Verso Ambiguity in Matches

**Problem:** Each Siena dissertation reference matches BOTH recto and
verso of its computed folio, producing ~2x the expected match count.

**Diagnosis:** The matching pipeline joins by folio number without
resolving which side of the leaf the annotation appears on.

**Fix:** Not fully fixed. These matches remain MEDIUM confidence. The
system is honest about the ambiguity. Resolving it would require
checking each annotation's position on the physical page.

**Lesson:** MEDIUM confidence is the honest answer when you know the
folio but not the side. Don't upgrade to HIGH without verification.

---

## 10. Deprecated Tables Still Queried

**Problem:** `build_site.py` still queries `dissertation_refs` for
marginalia pages instead of the canonical `annotations` table.

**Diagnosis:** The annotations table was consolidated but the page
generator was never updated to use it.

**Status:** Known issue. The annotation_type badges are shown via a
separate query, but the main folio page content still comes from the
deprecated table.

**Fix needed:** Update `build_marginalia_pages()` to query `annotations`
as its primary data source.

---

## 11. hp_copies.confidence Stale After BL Fix

**Problem:** After eliminating all LOW matches, the hp_copies table still
showed confidence='LOW' for the BL copy.

**Diagnosis:** The BL match rebuild updated the matches table but not
the hp_copies metadata.

**Fix:** Manual SQL update: `UPDATE hp_copies SET confidence = 'MEDIUM'
WHERE shelfmark = 'C.60.o.12'`

**Lesson:** When fixing confidence in one table, check for stale
confidence values in related tables.

---

## 12. 4 Unmapped Signatures

**Problem:** z5v, z6r, z5r, u3r don't appear in the signature map.

**Diagnosis:** The signature map omits 'u' (per 1499 collation convention)
and quire z may have fewer than 8 leaves.

**Status:** Documented as KNOWN UNRESOLVABLE. Cannot fix without physical
book access.

---

## 13. CSS Not Applying to Gallery Card Descriptions

**Problem:** Card description styles (font-size, max-height) in
style.css not being picked up by the browser preview.

**Diagnosis:** Browser caching of old CSS. The styles are in the file
but the preview tool's internal browser doesn't always invalidate cache
on file changes.

**Fix:** Hard reload (Ctrl+Shift+R) or cache-busting. The deployed site
picks up the CSS correctly from a fresh load.

**Lesson:** When CSS changes don't appear, always check if the file was
saved before assuming the selectors are wrong. Browser cache is the
most common cause of "my CSS isn't working."
