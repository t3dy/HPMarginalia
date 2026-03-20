# HPRACHAEL: Visual Design Logic Audit

> Rachael is designed to be indistinguishable from real. This audit evaluates whether the visual design communicates the RIGHT things.

---

## COLOR SYSTEM

**INTENT**: Warm, scholarly palette evoking parchment and leather — appropriate for a Renaissance book project.

**REALITY**: The palette is consistent and well-chosen. `--bg: #f5f0e8` (warm parchment), `--accent: #8b4513` (saddlebrown/leather), `--header-bg: #2c2418` (dark walnut). The warm earth tones correctly signal "historical/scholarly" without veering into kitsch.

**GAP**: The badge system introduces Bootstrap-derived colors (#d4edda green, #f8d7da red, #fff3cd yellow, #e2e3e5 gray) that don't belong to the warm palette. They work functionally but feel imported from a different design system.

**FIX**: Warm the badge colors to match the palette. Replace Bootstrap greens/reds with earthy variants:
- HIGH confidence: `#dce8d4` / `#3d5a2d` (sage)
- LOW confidence: `#e8d4d0` / `#6b3028` (terracotta)
- Review badge: `#e8dcc8` / `#6b5420` (ochre)
- Collection badge: use the same sage/terracotta scheme

---

## TYPOGRAPHY HIERARCHY

**INTENT**: Serif body text (Georgia) for scholarly gravitas, sans-serif (Segoe UI/system) for UI elements and metadata.

**REALITY**: The dual-font system is correctly applied. Headings and body use serif; nav, badges, metadata, and labels use sans-serif. Line-height at 1.7 is generous and readable.

**GAP**: The heading hierarchy across generated pages is inconsistent:
- index.html: `h1` in header (2.4rem), no other headings in body
- Generated pages: `h1` in header (same), then `h2` as page titles (1.4rem in scholars, variable elsewhere)
- Dictionary pages use `h2` for term name, `h3` for category sections, `h4` for related terms — correct
- Docs pages use `h2`-`h4` from markdown conversion — correct
- **Problem**: Bibliography page has no heading hierarchy — section titles use `h3` but the page title is just a `<h2>` inside a div, not in a consistent location

**FIX**: All generated content pages should follow: `h2` = page title (in `.intro` or equivalent), `h3` = section headers, `h4` = subsection/entry titles. This is already mostly true but should be enforced in the template.

---

## SPACING SYSTEM

**INTENT**: Comfortable academic reading with generous whitespace.

**REALITY**: Mostly consistent. Max-widths are 800px (intro, dictionary, docs), 900px (scholars, bibliography), 1000px (marginalia, footer), 1200px (scholars grid), 1400px (gallery). The variety is intentional — narrower for reading, wider for grids.

**GAP**: The inline `<style>` blocks on generated pages repeat spacing values with slight inconsistencies. Dictionary margins are `2rem auto` while bibliography is also `2rem auto` — but docs use `2rem auto` for `.docs-page` and also `2rem auto` for `.doc-content`. The repetition is fine but the different max-widths create a subtle jarring effect when navigating between sections.

**FIX**: Standardize to three max-width tiers: `--width-reading: 800px`, `--width-content: 960px`, `--width-grid: 1200px`. Apply reading width to dictionary terms, docs content, and about page. Content width to scholars detail, bibliography, marginalia detail. Grid width to index pages with card layouts.

---

## COMPONENT CONSISTENCY

**INTENT**: Cards, badges, and tables should look like they belong to the same design system.

**REALITY**: Three inconsistencies found:

1. **Nav bar inconsistency**: The index.html (hand-written) has a 5-link nav, while all generated pages have the current 8-link nav. A visitor clicking from the gallery to any other page will see the nav suddenly gain 3 more items. **This is a functional bug, not just aesthetic.**

2. **CSS path inconsistency**: index.html uses `href="style.css"` (relative), generated pages use `href="/style.css"` (absolute). On GitHub Pages served from `/HPMarginalia/`, absolute paths will break — `/style.css` will resolve to the GitHub root, not the project. All paths need to be relative or use a base URL.

3. **Inline styles vs. shared CSS**: Every generated page type (dictionary, marginalia, bibliography, docs, code) injects its own `<style>` block with page-specific CSS. This means the same styles are duplicated across 100+ pages. Dictionary styles appear in all 38 dictionary pages identically.

**FIX**:
1. Rebuild index.html nav via the build script (replace the hand-inserted nav with the current 8-link version)
2. Make all CSS/link paths relative to the page's location (use `../style.css` from subdirectories)
3. Extract inline styles into a shared `site/components.css` loaded by all pages

---

## VISUAL WEIGHT

**INTENT**: The primary content (manuscript images, annotations, definitions) should dominate; metadata and navigation should be subordinate.

**REALITY**: Generally correct. The gallery cards lead with the image, the dictionary leads with the definition, the bibliography leads with the author/title. The badge system is appropriately small and secondary.

**GAP**: On marginalia detail pages, the LOW confidence badge and "Unverified" review badge are visually prominent because they use red/yellow colors that clash with the warm palette. For the BL copy (218 matches), every single image has both badges, creating a wall of warning that overwhelms the actual content.

**FIX**: On pages where ALL items have the same status (e.g., all BL images are LOW confidence), show the status once at the top of the page as a notice banner rather than on every individual image card. Reserve per-item badges for pages where items have mixed statuses.

---

## BRAND COHERENCE

**INTENT**: A recognizable visual identity as a serious digital humanities project.

**REALITY**: Strong. The warm palette, serif typography, and understated design correctly signal "scholarly but accessible." The use of the HP's own vocabulary (signature, quire, folio) in the UI reinforces the subject matter.

**GAP**: The site has no favicon, no open graph tags, and no meta description. When shared on social media or bookmarked, it will show a generic browser icon and no preview.

**FIX**: Add a favicon (a small version of a woodcut initial or the HP's distinctive 'P' initial would be appropriate). Add `<meta name="description">` and OG tags to the page shell.

---

## DARK PATTERNS

**INTENT**: None.

**REALITY**: None found. The site is read-only with no forms, no tracking, no cookies, no analytics. Clean.

---

## FUNCTIONAL ISSUES FOUND

Beyond aesthetics, the audit identified these functional problems:

1. **Broken nav on index.html** — missing Bibliography, Docs, Code links
2. **GitHub Pages path issue** — absolute paths (`/style.css`) will fail when deployed to `t3dy.github.io/HPMarginalia/` because GitHub Pages serves from a subdirectory
3. **Inline CSS duplication** — same styles repeated across 100+ generated pages, inflating total page weight
4. **No `<main>` tag in index.html** — it uses `<main>` but the closing tag and footer structure differ from generated pages
5. **Scholar page footer** — generated pages have a footer with provenance info; index.html has a different footer layout. The footers should be consistent.

---

## SUMMARY

**9 design logic issues. 5 are CSS fixes, 2 need template refactoring, 2 need design decisions.**

| # | Issue | Type | Severity |
|---|-------|------|----------|
| 1 | Nav bar out of sync on index.html | Template fix | **Critical** |
| 2 | CSS absolute paths will break on GH Pages | Template fix | **Critical** |
| 3 | Badge colors from Bootstrap, not palette | CSS fix | Minor |
| 4 | Inline styles duplicated across 100+ pages | CSS refactor | Medium |
| 5 | Per-item LOW badges overwhelm BL pages | Design decision | Medium |
| 6 | Max-width inconsistencies across page types | CSS fix | Minor |
| 7 | No favicon or OG tags | CSS/HTML fix | Minor |
| 8 | Footer inconsistency between index and generated | Template fix | Minor |
| 9 | Heading hierarchy inconsistency | CSS fix | Minor |
