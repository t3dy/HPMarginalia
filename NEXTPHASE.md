# NEXTPHASE: Plan for What Comes Next

> This plan follows from ISIDORE4's diagnosis: the project has enough
> infrastructure. What it needs is to surface existing data to readers,
> fix the last-mile gaps, and stop designing before executing.

---

## Guiding Principle

**Build outward, not deeper.** The database has 22 tables, 431 matches,
94 dictionary terms, 60 scholars, 71 timeline events, 10 alchemical symbols,
26 symbol occurrences, 18 detected woodcuts, and 282 classified annotations.
Almost none of the recent enrichments (annotation types, symbol occurrences,
woodcut detections, annotation density data) are visible on the site.

The next phase turns data into pages.

---

## Phase 1: Woodcuts Tab (1 hour)

**What exists:** WOODCUTONTOLOGY.md (schema), WOODCUTTEMPLATE.md (design),
WOODCUTRESEARCHREPORT.md (18 detected woodcuts with subjects).

**What to build:**
1. `scripts/seed_woodcuts.py` — create woodcuts table, seed 18 detected woodcuts
2. Add `build_woodcuts_pages()` to build_site.py — index + detail pages
3. Add "Woodcuts" tab to nav
4. Link woodcut pages to marginalia folio pages, dictionary terms, essays

**Output:** ~20 new pages (index + 18 detail pages).

**Why first:** The woodcut research is the most substantial unbuilt content.
It has descriptions, categories, annotation data, and BL photo references.
Building it requires no new research, only execution.

---

## Phase 2: Surface Annotation Types (30 min)

**What exists:** 282 annotations classified into 6 types (MARGINAL_NOTE,
CROSS_REFERENCE, INDEX_ENTRY, SYMBOL, EMENDATION, UNDERLINE). Not displayed.

**What to build:**
1. Update `build_marginalia_pages()` to query annotations table
2. Display annotation_type badges on folio pages
3. Add filter capability on marginalia index (filter by type)

**Why second:** This makes existing classification work visible. No new data
generation needed — just rendering what's already computed.

---

## Phase 3: Fix Data Gaps (30 min)

**What to fix:**
1. Add flyleaf annotation record (the Master Mercury declaration — currently
   has a folio_description but no annotation row)
2. Document the 4 unmapped signatures (z5v, z6r, u3r, z5r) in
   CONCORDANCESTATUS.md as known collation ambiguities
3. Update hp_copies confidence note for BL (already MEDIUM, but the
   copy_notes still references the old LOW confidence problem)
4. Update CONCORDANCESTATUS.md with current numbers

---

## Phase 4: Organize Documentation (30 min)

**What to fix:**
1. Create DOCUMENTATION_INDEX.md categorizing all 39 .md files by type:
   - Specifications (6): SCHOLAR_SPEC, TIMELINE_SPEC, MANUSCRIPTS_SPEC,
     DECKARD_MARGINALIA_SPEC, WOODCUTONTOLOGY, WRITING_TEMPLATES
   - Execution Plans (4): SCHOLAR_PIPELINE, TIMELINEPLAN, MANUSCRIPTSPLAN,
     CONCORDANCEREBUILD
   - Research Reports (3): WOODCUTRESEARCHREPORT, IMAGEIDENTIFICATION,
     CONCORDANCEHACKING
   - Critiques (4): HPONTOCRIT, HPengCRIT, ISIDORE3, ISIDORE4
   - Design Documents (6): HPONTOLOGY, HPCONCORD, HPWEB, HPSCHOLARS,
     HPMULTIMODAL, HPproposals
   - Audits (4): HPDECKARD, HPDECKARD2, HPWEBAESTHETICS, CONCORDANCESTATUS
   - Post-mortems (3): MISTAKESTOAVOID, HPAGENTS, HPEMPTYOUTPUTFILES
   - Reference (2): HPMIT, HPGPTWEBWRITING.txt
   - Status/Plans (3): CLAUDE.md, NEXTPHASE, BUILDINGTHECONCORDANCEENVIRONMENT
   - Templates (2): WOODCUTTEMPLATE, READINGIMAGES
   - Other (2): HPython, HPromptTRANSCRIPT
2. Add `scripts/README.md` with dependency graph for the 41 scripts
3. Update CLAUDE.md to point to DOCUMENTATION_INDEX.md

---

## Phase 5: Update README.md (15 min)

The README still says some stale numbers. Update to reflect:
- 335 pages, 13 nav tabs, 94 dictionary terms, 60 scholars, 71 timeline
  events, 18 woodcuts detected, 431 matches (0 LOW), 282 classified annotations
- Current architecture: 22 tables, 41 scripts, 6 spec files, 107 staging artifacts
- Corrected BL concordance (offset = 13, verified at 27 points)

---

## Phase 6: Complete BL Image Reading (2 hours, optional)

Read the remaining ~120 BL text pages to:
- Complete the woodcut inventory (estimate: ~27 more woodcuts in pages 1-176)
- Complete the annotation density map
- Confirm page numbers for the full photo range

This is valuable but not blocking. The 69 pages already read provide
sufficient verification for the offset and a representative sample of
woodcuts and annotation patterns.

---

## What This Plan Does NOT Do

- Does not add new database tables (enough tables exist)
- Does not write new specifications (enough specs exist)
- Does not propose new features (enough features are designed)
- Does not research new topics (enough research is staged)

It takes what exists and makes it visible.

---

## Execution Order

```
[Phase 1: Woodcuts tab] ──→ [Phase 2: Annotation types on pages] ──→ [Phase 3: Data fixes]
                                                                       ↓
                                                               [Phase 4: Doc organization]
                                                                       ↓
                                                               [Phase 5: README update]
                                                                       ↓
                                                               [Phase 6: More BL reading]
                                                                       (optional)
```

Total estimated time: 3 hours (Phases 1-5), plus 2 hours optional (Phase 6).

---

## Validation Gates

After all phases:
- [ ] Woodcuts tab exists with 18+ pages
- [ ] Marginalia pages show annotation type badges
- [ ] Flyleaf has an annotation record
- [ ] 4 unmapped signatures documented
- [ ] DOCUMENTATION_INDEX.md exists
- [ ] scripts/README.md exists
- [ ] README.md numbers are current
- [ ] CLAUDE.md points to documentation index
- [ ] 0 nav errors, 0 CSS errors, 0 orphan records
- [ ] Site deployed to GitHub Pages
