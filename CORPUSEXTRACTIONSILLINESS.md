# Corpus Extraction Silliness: A Post-Mortem

## The Problem

When we moved the 18 CORPUS_EXTRACTION woodcuts from the Woodcuts gallery to the Alchemical Hands page, we created a cascade of broken links across the site. The link validator found **113 broken links** in the initial audit. Here's what went wrong and how we fixed it.

## What Happened

### Act 1: The Move (Intentional)

We excluded `source_method = 'CORPUS_EXTRACTION'` woodcuts from the Woodcuts gallery builder and added them as a gallery section on the Alchemical Hands page. The gallery went from 127 to 109 entries (later 111 after adding 2 Polyandrion woodcuts). This was correct and intentional.

### Act 2: The Ghost Pages (Unintentional)

The build script generates HTML files for each woodcut. When the CORPUS_EXTRACTION entries were excluded from the query, the script simply stopped generating their pages. But it never **deleted** the old pages from previous builds. So `site/woodcuts/dark-forest.html`, `site/woodcuts/elephant-obelisk.html`, and 45 other ghost pages persisted from earlier builds.

This meant:
- The concordance browser linked to `../woodcuts/dark-forest.html` (a ghost page that existed as a stale file)
- The ghost pages had nav links to `concordance-method.html` (no `../` prefix because they were built before the concordance existed)
- Everything appeared to work locally because the stale files were present

### Act 3: The Depth Bug (Compounding)

The concordance page was built with `depth=0` instead of `depth=1`, so ALL its CSS and nav links were wrong. The header appeared unstyled, and every nav link was a 404. This was a simple one-line fix (`depth=1`), but it took an audit to find because the local server happens to resolve some paths differently than GitHub Pages.

### Act 4: The Marginalia Phantom Links

Many woodcut detail pages link to marginalia pages for the corresponding folio signature. But only 127 of 448 signatures have marginalia pages (only folios with Russell annotations get their own pages). The build script checked `has_annotation = 1` in the woodcuts table but never checked whether the target marginalia HTML file actually existed.

This created 33+ broken links like `../marginalia/g3v.html` where `g3v` genuinely has an annotation in the database but doesn't have its own marginalia page.

Similarly, dictionary term links pointed to terms like `hermaphrodite.html` that don't exist in the dictionary.

## What We Fixed

| Fix | Impact | Lines Changed |
|-----|--------|---------------|
| Added `depth=1` to concordance `page_shell()` call | Fixed all CSS and nav links on concordance page | 1 |
| Added stale page cleanup to woodcuts builder | Prevents ghost pages from previous builds | 4 |
| Deleted 47 stale woodcut pages | Removed files that should not exist | 0 (manual cleanup) |
| Added `_wc_marg_sigs` check before linking to marginalia pages | Only links to marginalia pages that actually exist | 8 |
| Added `_wc_dict_slugs` check before linking to dictionary terms | Only links to dictionary terms that actually exist | 4 |
| Added `_ag_marg_sigs` and `_ag_dict_slugs` checks in annotated gallery | Same fix for the Alchemical Hands gallery section | 6 |
| Fixed concordance browser to link CORPUS_EXTRACTION woodcuts to Alchemical Hands | Correct destination for moved woodcuts | 8 |
| Fixed 3 hardcoded links in `the-book.html` | Updated stale woodcut links to Alchemical Hands | 3 |
| Created `check_links.py` validator | Catches broken links before deployment | New script |

## Result

| Metric | Before | After |
|--------|--------|-------|
| Broken links | 113 | 5 |
| Stale pages | 47 | 0 |
| Depth bugs | 1 | 0 |
| Ghost CORPUS_EXTRACTION pages | 18 | 0 |

The 5 remaining issues are BL photo raw-path references in 5 marginalia pages created from Phase 3 deep readings. These are cosmetic — the images exist locally but use filesystem paths instead of web-relative paths. They need a database fix to update the image path resolution, which is a separate task.

## Lessons

### 1. Build scripts must clean up after themselves

The woodcuts builder creates files but never deletes old ones. This means renaming, removing, or excluding entries leaves ghost pages that accumulate over time. **Every builder function should delete stale output before generating new files.**

Fix: Added `for old_file in wc_dir.glob('*.html'): old_file.unlink()` at the top of the woodcuts builder.

### 2. Never link to a page without checking it exists

The build script assumed that if a folio has `has_annotation = 1`, then `marginalia/{sig}.html` exists. This is false — the marginalia builder only generates pages for folios with Russell-specific annotation data, not for every annotated folio in the database.

Fix: Build a set of existing page stems and check membership before generating links.

### 3. Moving content creates a link debt

When 18 entries moved from Woodcuts to Alchemical Hands, every page that linked to those woodcut detail pages became a broken link. The concordance, the-book.html, and the cross-links all needed updating. **Before moving content, grep for all references to the old location.**

### 4. Always run the link validator after builds

`check_links.py` now exists and should be run after every `build_site.py` execution. It catches broken internal links before they reach the deployed site. Consider adding it to the CI pipeline.

### 5. The depth parameter is a footgun

Every subdirectory page needs `depth=1` in its `page_shell()` call, or all CSS and nav links break. There's no compile-time check for this — only visual inspection or the link validator catches it. **The depth check in `check_links.py` catches this specific class of bug.**

## Infrastructure Added

**`scripts/check_links.py`** — Run after builds to validate all internal links:
```
python scripts/check_links.py          # Summary
python scripts/check_links.py -v       # Verbose (shows each broken link)
```

Checks:
- All `href` and `src` attributes in generated HTML
- CSS stylesheet availability (depth/prefix issues)
- Artifact files (`None.html` etc.)
- Reports grouped by issue type

Exit code 0 = all clear, exit code 1 = issues found.
