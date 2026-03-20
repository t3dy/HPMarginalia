# WEBSITEREDESIGNS: Summary of All Website Changes

> Cumulative record of every design change made to the site across
> the last several sessions. From 300 pages to 365 pages, from
> "Hypnerotomachia Poliphili" to "Alchemical Hands," from zero
> images to 674.

---

## Site Rename

**Before:** "Hypnerotomachia Poliphili — Digital Scholarship & Marginalia"
**After:** "Alchemical Hands in the Hypnerotomachia Poliphili — Marginalia, Scholarship & Reception"

The site is now framed as originating from a specific discovery in Russell's
thesis: two anonymous alchemists who independently decoded the HP as a
chemistry textbook, using incompatible chemical frameworks.

## Home Page

**Before:** "The Hypnerotomachia Poliphili, published by Aldus Manutius in
Venice in 1499, is one of the most celebrated and enigmatic books of the
Italian Renaissance."

**After:** "Two anonymous readers, working independently in different copies
of the same Renaissance book, both decided it was secretly about alchemy.
They were wrong about the book — but what they wrote in its margins is
extraordinary."

The hook leads with the alchemical hands discovery. The second paragraph
introduces the HP for non-specialists. The third paragraph guides visitors
to the gallery, dictionary, essay, and timeline.

## New Pages Added

| Page | Words | Content |
|------|-------|---------|
| **The Book** | ~1500 | Narrative walkthrough of the HP's plot for non-specialists. 10 sections from dark forest to awakening, with inline links to 30+ dictionary terms and woodcut pages. |
| **Woodcuts** (18 pages) | ~200 each | Index + 18 detail pages for detected woodcuts with subjects, categories, scholarly discussion. |
| **Timeline** | ~1900 | 71 events from 1499-2024, filterable by category. |
| **Manuscripts** (6 pages) | ~350 each | 6 copies with hand profiles, match statistics, confidence markers. |

## Illustrated Essay

The Russell Alchemical Hands essay now includes 6 manuscript photographs
placed at the narrative points where Russell discusses them:

1. **Flyleaf verso** (photo 003) — Master Mercury declaration
2. **Elephant and Obelisk** (photo 041, b6v) — ideograms in syntax
3. **Opening page a1r** (photo 014) — POLIPHILO INCOMINCIA with both hands
4. **Title page** (photo 004) — 1545 edition, "Sum Ben: Ionsonij"
5. **Page 20** (photo 033) — alchemical ideograms in left margin
6. **D.AMBIG.D.D. monuments** (photo 036, b4r) — hermaphrodite reading

Each with descriptive captions grounded in Russell's analysis.

## Gallery Card Descriptions

Every gallery card on the home page now shows:
- **Signature** and manuscript badge (was already there)
- **Hand attribution** with name and alchemist tag where applicable (new)
- **Description** explaining what the image shows and what Russell found (new)
- **Marginal text** quote from Russell (was already there, now separated by border)

## Image Deployment

- 674 images compressed and deployed to `site/images/`
- BL images: 196 files compressed from ~4 MB to ~200 KB each (95% reduction)
- Siena images: 478 files copied at ~500 KB each
- Total: 275 MB, within GitHub Pages 1 GB limit
- Database paths updated from deep directory structure to `images/bl/` and `images/siena/`

## Annotation Types on Folio Pages

Marginalia folio pages now display annotation type badges:
MARGINAL_NOTE (126), CROSS_REFERENCE (68), INDEX_ENTRY (50),
SYMBOL (21), EMENDATION (16), UNDERLINE (1)

## Dictionary Expansion

37 → 94 terms across 15 categories. All with significance_to_hp and
significance_to_scholarship prose. New categories: Characters & Figures,
Places & Settings, Architecture & Built Form, Gardens & Landscape,
Processions & Ritual, Visual & Typographic, Aesthetic Concepts,
Material Culture, Narrative & Literary Form.

## Scholar Pages

30 → 60 pages. 59 with overview prose. 11 historical figures tagged.
Works in Archive / Other Known Works sections. Provenance badges.

## Writing Style

Updated WRITING_TEMPLATES.md: target reader is now "someone who visits
exhibitions, reads long-form journalism, and is curious about Renaissance
books — not necessarily an academic."

## Inline Dictionary Links

The Russell essay now has inline links within prose: prisca sapientia,
ingegno, Sol/Luna, Master Mercury — so readers can learn terms at the
point of encounter rather than scrolling to a cross-links block.

## Alchemical Symbol System

- 10 symbols (7 planetary metals + cinnabar, sulphur, hermaphrodite)
- 26 occurrences mapped to specific folios
- Symbol tables displayed on marginalia folio pages
- Cross-links to dictionary terms and essays

## Navigation

11 → 15 tabs: added The Book, Timeline, Woodcuts, Manuscripts

## Documentation Refactor (Antigravity)

36 root .md files → 5 core documents (SYSTEM, ONTOLOGY, PIPELINE,
INTERFACE, ROADMAP) + archive of 36 historical documents.

## Concordance Fix

- BL offset discovered (=13) by reading 69 manuscript photographs
- 218 wrong LOW matches eliminated
- 39 correct matches rebuilt (22 HIGH, 17 MEDIUM)
- 0 LOW confidence matches in the system
