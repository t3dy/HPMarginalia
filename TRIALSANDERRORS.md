# Trials and Errors: Building a Digital Edition of a Renaissance Illustrated Book

**Project:** HPMarginalia -- Alchemical Hands in the Hypnerotomachia Poliphili
**Period:** March 2026
**Tool:** Claude Code (Opus 4.6) with native vision, MCP browser tools

---

## 1. The File Size Hypothesis (Failed Beautifully)

### The Idea
We needed to identify which of 448 pages in the 1499 HP contain woodcut illustrations. The Internet Archive serves individual page images as JPEGs. Surely woodcut pages would be *larger files* than text-only pages -- more visual complexity means more data, right?

### What We Built
`scan_ia_pages.py` -- downloads IA page images and analyzes file sizes with a configurable threshold (default 80 KB). Pages above the threshold are flagged as woodcut candidates.

### What Actually Happened
Every single page came back between 2,000 and 3,000 KB. The median was 2,579 KB with a standard deviation of only 179 KB. At 600 DPI, the high-frequency texture of Renaissance typography produces JPEG files nearly as large as woodcut pages. The scanner resolution drowns out the signal.

**Result:** 51 out of 51 test pages flagged as "woodcut candidates." Zero discrimination.

### The Takeaway
File size analysis works for low-resolution digitizations (72-150 DPI) where text pages compress small and image pages don't. It fails catastrophically at archival resolution. For 600 DPI scans, you need actual image analysis -- or just look at them.

### What We Did Instead
Used Claude Code's native vision capability to read the downloaded JPEG files directly, one page at a time. This worked perfectly but was slow (~120 pages inspected manually across the session). Each page took one Read tool call and a visual judgment. The process could not be parallelized because each page's identification informed which pages to check next.

**Lesson for future projects:** When building automated pipelines for image-heavy historical texts, always start with a calibration set. Download 10 known-woodcut and 10 known-text pages, measure their properties, and verify your detection method works before scaling up.

---

## 2. The Off-By-One Plague (Polyandrion Section)

### The Problem
The Polyandrion (cemetery) section of the HP (pp.233-260) contains approximately 30 small epitaph, monument, and inscription woodcuts crammed onto about 15 pages. Our earlier LLM-assisted seeding had placed these at systematically wrong pages: 241 instead of 242, 243 instead of 244, 247 instead of 246, 249 instead of 250, and so on.

### Why It Happened
The earlier seeding used LLM-generated page estimates based on descriptions from the 1896 facsimile catalog and Pozzi & Ciapponi's critical edition. These sources count pages differently -- the 1896 catalog uses plate numbers, Pozzi uses folio recto/verso notation, and our database uses sequential page numbers. The conversion between these systems introduced systematic off-by-one errors, especially in the dense Polyandrion section where multiple small woodcuts appear on consecutive pages.

### How We Found It
During the IA visual scan, we noticed that confirmed woodcut pages consistently didn't match the database entries. Page 242 had a woodcut, but the database said 241. Page 244 had one, but the database said 243. The pattern was unmistakable once we had ground truth from the images.

### How We Fixed It
`fix_woodcut_pages.py` -- a targeted correction script that:
1. Deletes duplicate entries at wrong pages
2. Updates page numbers for off-by-one errors
3. Merges entries where the corrected page already has a woodcut row
4. Adds genuinely missing entries

The fix reduced 141 woodcut rows to 127 -- not because we lost data, but because duplicates and misplaced entries were cleaned up.

### The Takeaway
When working with historical page numbering, **always build a concordance table first**. The `page_concordance` table -- which maps every page surface to all numbering systems simultaneously -- should have been the first thing we built, not an afterthought. Without it, every script that converts between numbering systems introduces its own conversion bugs.

**Rule:** If your source has more than one way to identify a page (folio number, signature, sequential number, plate number, photo number), build the concordance before doing anything else.

---

## 3. The Duplicate Ceremony Problem

### The Problem
The Temple of Venus ceremony scene (pp.204-221) was over-represented in the database. We had entries at pages 219, 221, 222, and 224 for what turned out to be essentially the same two scenes: the miracle of the roses and receiving fruits from the priestess.

### Why It Happened
Earlier LLM-assisted seeding created entries based on textual descriptions from multiple scholarly sources. Each source described the same scenes slightly differently, and the LLM generated separate entries for each description without realizing they referred to the same illustrations. When De Jong says "the sacrifice before the altar" and Fierz-David says "the ritual offering to Venus," they mean the same woodcut on the same page.

### How We Found It
The IA visual scan showed that pages 219, 222, and 224 are text-only. The actual woodcuts are at pages 208 (ceremony) and 221 (miracle of roses). The extra entries were phantoms.

### The Takeaway
When ingesting from multiple scholarly sources, **always cross-reference against the physical artifact**. Textual descriptions can create phantom entries when they paraphrase each other. The image is the ground truth; the description is the interpretation.

**Rule:** Never trust two scholarly descriptions of the same scene to agree on page numbers. Always verify against the facsimile.

---

## 4. The Column Name Mismatch (Schema Drift)

### The Problem
When `fix_woodcut_pages.py` tried to update the `ia_page` column, it crashed: `no such column: ia_page`. The actual column name was `page_1499_ia`. Later, trying to insert new entries, it crashed again: `CHECK constraint failed: source_method IN ('CORPUS_EXTRACTION','LLM_ASSISTED','VISION_MODEL','MANUAL_TRANSCRIPTION','INFERRED')`.

### Why It Happened
The database schema evolved across multiple sessions. Early scripts used `ia_page`; later sessions renamed it to `page_1499_ia`. The `source_method` column has a CHECK constraint that only allows specific values, but the new script tried to insert `'IA_SCAN_VERIFIED'` -- a value we made up.

### How We Fixed It
Read the actual schema (`PRAGMA table_info(woodcuts)`) before writing the script. Used the existing column name and an approved source_method value.

### The Takeaway
**Always read the schema before writing to a table.** In a multi-session project where the database evolves, never assume you know the column names or constraints. `PRAGMA table_info()` takes one second and prevents crashes.

**Rule:** Before any INSERT or UPDATE, run `PRAGMA table_info(tablename)` and `PRAGMA check(tablename)` or at minimum read `docs/ONTOLOGY.md`.

---

## 5. The 168 vs 127 Puzzle (Why Fewer Rows Is Better)

### The Problem
The 1896 facsimile catalog lists 168 woodcuts. Our database ended up with 127 rows. That looks like we're missing 41 woodcuts.

### What's Actually Happening
Many HP pages have multiple small woodcuts stacked vertically -- especially in the Polyandrion (epitaph monuments), Cythera Gardens (topiary designs, trophies), and Procession (relief panels). The 1896 catalog counts each individual illustration as a separate entry, but our database has one row per page with one image. Page 319 alone has four trophy standards (catalog #132-135); page 317 has three designs.

### Why This Is Correct
Our database models *page images*, not *individual illustrations*. When you view the site, you see one IA facsimile image per woodcut page -- and that image shows all the stacked illustrations on that page. The `woodcut_catalog` table preserves the full 168-entry inventory with proper page assignments; the `woodcuts` table has the 127 distinct pages.

### The Takeaway
**Know what your unit of analysis is.** In a database of page images, the row is a page, not an illustration. In a catalog of illustrations, the row is an illustration. These are different things and trying to force one model to serve both purposes creates duplicates or gaps. Having two tables (woodcuts for pages, woodcut_catalog for illustrations) resolves this cleanly.

---

## 6. The Vision Reading Bottleneck (Slow but Right)

### The Problem
We needed to inspect ~280 pages to identify woodcuts. Claude Code can read images natively via the Read tool. But each page requires a separate tool call, the response includes a visual analysis, and the results need human judgment about whether the page contains a woodcut and which catalog entry it matches.

### What We Tried
Initially we attempted to scan in parallel by launching a background agent. The agent couldn't get web access permissions and returned a scholarly summary instead of actual page data.

### What Actually Worked
Sequential page reading with strategic jumps:
1. Start with known sections (e.g., "the Polyandrion should have epitaph woodcuts around pp.233-260")
2. Read a page at the center of the expected range
3. If woodcut found, read adjacent pages to find the cluster boundaries
4. If text-only, jump 5-10 pages and try again
5. Record findings in a JSON checkpoint file after each batch

This took about 120 page reads across the session. We covered pp.170-460, finding all 57 woodcut pages in the range.

### The Takeaway
For visual identification tasks on historical texts, **strategic sampling beats exhaustive scanning**. You don't need to read every page if you know the narrative structure. The HP has predictable woodcut density patterns: dense in the Procession (every page), sparse in Book II (one every 10-15 pages). Using narrative knowledge to guide sampling is much faster than brute force.

**Rule:** Before scanning, read the table of contents or a scholarly summary to identify high-density and low-density regions. Scan dense regions exhaustively; sample sparse regions at intervals.

---

## 7. The Commit-Before-Crash Lesson

### The Problem
`fix_woodcut_pages.py` crashed midway through (on the INSERT step) due to the CHECK constraint error. But it had already executed DELETE and UPDATE statements in Step 1.

### What Saved Us
SQLite's transaction behavior. Since the script only calls `conn.commit()` at the end (after all steps), the crash before commit meant all changes were rolled back. When we fixed the bug and re-ran, the data was exactly as it was before.

### The Takeaway
**Always commit at the end of multi-step database operations, not after each step.** This gives you implicit transaction safety. If any step fails, everything rolls back. This is especially important in scripts that mix destructive operations (DELETE, UPDATE) with constructive ones (INSERT).

---

## 8. The Slug Generation Gap

### The Problem
After adding 4 new woodcut entries and rebuilding the site, the new pages didn't appear at their expected URLs. Navigating to `p363.html` returned a 404.

### Why It Happened
The `fix_woodcut_pages.py` script inserted entries with all required fields except `slug` -- the URL-friendly identifier. The site builder uses slugs to generate page filenames. Empty slug = no page file generated (it was generated with a `None.html` filename).

### How We Fixed It
Manually set slugs for the 4 new entries:
```sql
UPDATE woodcuts SET slug = 'fountain-of-venus-sarcophagus-of-adonis' WHERE page_1499 = 363;
```

### The Takeaway
**When adding rows to a table that drives page generation, always check what the site builder needs.** Read the build script first to understand which columns are required for rendering. A row without a slug is a row without a page.

---

## General Principles for Renaissance Text + Image Projects

### 1. Build the concordance first
Before any content work, map every physical page to every numbering system (sequential, signature, folio, photo number, digital scan index). This table becomes the backbone that prevents conversion errors everywhere else.

### 2. The image is the ground truth
Textual descriptions from scholars are interpretations. Different scholars describe the same image differently, assign different page numbers, and use different naming conventions. When in doubt, look at the picture.

### 3. Multiple woodcuts per page is the norm, not the exception
Renaissance illustrated books commonly have 2-4 small woodcuts on a single page, especially for decorative elements (trophies, ornaments, garden designs) and serial content (epitaphs, relief panels). Model your data accordingly -- either one row per page-image or one row per illustration, but be consistent.

### 4. LLM page estimates need visual verification
LLMs can estimate which page a woodcut appears on based on scholarly descriptions, but these estimates are frequently off by 1-5 pages. Dense sections (where woodcuts appear on every other page) make these errors catastrophic. Always verify against the digital facsimile.

### 5. Start with 10, not 100
Before building a pipeline to process 300 pages, test it on 10. The file-size detection method would have been caught in 5 minutes with a calibration set. Instead, we built the whole pipeline, downloaded 51 pages, and discovered it was useless.

### 6. Schema drift is real in multi-session projects
When a project spans multiple Claude Code sessions, column names, constraints, and table structures evolve. Always read the current schema before writing to it. Document schema changes in ONTOLOGY.md immediately.

### 7. Narrative knowledge accelerates scanning
Knowing that Book II is text-heavy and the Procession section has a woodcut on every page saves hours of blind scanning. Use the book's structure as a search heuristic.

### 8. Deduplication is addition by subtraction
Going from 141 to 127 woodcuts felt like losing data. It was actually gaining accuracy. Fewer rows with correct page numbers are worth more than more rows with wrong ones.
