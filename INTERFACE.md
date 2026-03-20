# INTERFACE: How Data Becomes Pages

> What the site shows, what it hides, and what needs fixing.

## Navigation (14 tabs)

| Tab | Page(s) | Source Table(s) | Status |
|-----|---------|----------------|--------|
| Home | index.html | matches, images, dissertation_refs | BUILT |
| Marginalia | marginalia/index.html + 113 folios | matches, images, annotations, folio_descriptions, symbol_occurrences | BUILT |
| Scholars | scholars.html + 60 detail | scholars, scholar_works, bibliography, summaries.json | BUILT |
| Bibliography | bibliography.html | bibliography | BUILT |
| Dictionary | dictionary/index.html + 94 terms | dictionary_terms, dictionary_term_links | BUILT |
| Docs | docs/index.html + 23 docs | filesystem .md files via DOC_METADATA | BUILT |
| Code | code/index.html + 31 scripts | filesystem .py files via SCRIPT_METADATA | BUILT |
| Timeline | timeline.html | timeline_events | BUILT |
| Woodcuts | woodcuts/index.html + 18 detail | woodcuts | BUILT |
| Manuscripts | manuscripts/index.html + 6 copies | hp_copies, annotator_hands, matches | BUILT |
| Edition | digital-edition.html | — (static stub) | BUILT (stub) |
| Alchemical Hands | russell-alchemical-hands.html | annotator_hands, matches, folio_descriptions | BUILT |
| Concordance | concordance-method.html | matches, signature_map, images | BUILT |
| About | about.html | aggregate stats from all tables | BUILT |

## UI Surfacing Audit

### FULLY SURFACED (data visible on site)

| Data | Where Shown |
|------|------------|
| 431 matches (48 HIGH, 383 MEDIUM) | Gallery + folio pages |
| 674 images | Gallery + folio pages |
| 94 dictionary terms + significance | Dictionary term pages |
| 247 term cross-links | Related Terms sections |
| 60 scholars + 59 overviews | Scholar pages |
| 109 bibliography entries | Bibliography page |
| 71 timeline events | Timeline page (filterable) |
| 18 woodcuts | Woodcut pages |
| 6 manuscript copies | Manuscripts pages |
| 11 annotator hands | Marginalia + manuscripts pages |
| 13 folio descriptions | Alchemical Analysis sections |
| 10 alchemical symbols + 26 occurrences | Symbol tables on folio pages |
| 282 annotation type badges | Folio pages (6 types) |

### PARTIALLY SURFACED

| Data | Issue | Fix |
|------|-------|-----|
| annotations table (282) | build_site.py still queries dissertation_refs, not annotations | Switch query source in build_marginalia_pages() |
| annotation types | Shown as badges but no filtering capability | Add type filter to marginalia index |
| scholar_works (72) | Used internally but "Works in Archive" vs "Other" split could be clearer | Minor template improvement |

### NOT SURFACED

| Data | Rows | What's Missing |
|------|------|---------------|
| document_topics | 34 | Topic tags not shown on docs pages |
| 4 unmapped signatures | — | No error page or note on site |

### MISLEADING PRESENTATION

| Claim on Site | Reality | Fix Needed |
|---------------|---------|------------|
| "431 matches" | Only 2 of 6 Russell copies have photographs | Add caveat: "Image matches available for BL and Siena copies. 4 copies studied by Russell have no photographs in this project." |
| About page stats | May show stale numbers | Regenerated from DB on each build — should be current |

## Page Generation Architecture

`build_site.py` contains all page builders as functions:

```python
main():
    export_data_json()           # Gallery data
    update_styles()              # CSS injection
    update_index_nav()           # Home page nav
    build_scholars_pages()       # 60 scholar pages
    build_dictionary_pages()     # 94 term pages
    build_marginalia_pages()     # 113 folio pages
    build_bibliography_page()    # 1 page
    build_docs_pages()           # 23 doc pages
    build_code_pages()           # 31 script pages
    build_about_page()           # 1 page
    build_russell_essay_page()   # 1 essay
    build_concordance_essay_page() # 1 essay
    build_digital_edition_page() # 1 stub
    build_timeline_page()        # 1 page
    build_woodcuts_pages()       # 18 woodcut pages
    build_manuscripts_pages()    # 6 copy pages
```

All pages use `page_shell()` for consistent header/nav/footer and
`nav_html()` for the 14-tab navigation with depth-aware relative paths.

## Design Language

- Warm scholarly palette (parchment, leather tones)
- Serif for body text, sans-serif for metadata/badges
- Confidence badges: GREEN (HIGH), AMBER (MEDIUM), RED (LOW)
- Review badges: AMBER (Draft), BLUE (Reviewed), GREEN (Verified)
- Alchemist tags: dark red background
- All CSS in style.css, scholars.css, components.css (inline styles in page builders)
