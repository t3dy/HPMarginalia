# OUTWARDNOTDEEPER: Session Findings and the Shift to Presentation

> This document records what was discovered, built, and learned across
> a marathon session, and why the project's next move is surfacing
> existing data rather than generating more.

---

## What Was Discovered

### The BL Offset (the session's defining finding)

Every BL manuscript match in the database was wrong. The concordance
pipeline assumed photo number = folio number. By reading 69 actual
photographs, the offset was found: the first 13 photos are covers,
flyleaves, and front matter. Photo 014 = page 1 = a1r.

This was verified at 27 independent data points across the full range
of the book, never wrong once. The fix was trivial (subtract 13) but
the discovery required looking at the images — no schema design or
script engineering would have caught this.

257 junk matches were deleted. 39 correct matches were rebuilt. The
system went from 218 LOW confidence matches to zero.

### What the Photographs Show

| Finding | Detail |
|---------|--------|
| Title page confirms 1545 edition | "RISTAMPATO DI NOVO... M.D.XXXXV" |
| Ben Jonson's ownership | "Sum Ben: Ionsonij" on title page |
| Master Mercury declaration visible | Flyleaf verso, Hand B's Latin text readable |
| 18 woodcuts detected | Dark forest, elephant-obelisk, triumphal processions, etc. |
| 7 alchemical annotation sites | Including 2 new (c5v, h8r) not in Russell's extracted refs |
| 5 quire signatures confirmed | a iii, c ii, c iii, g ii, K iii |
| Annotation density mapped | 31 HEAVY, 22 MODERATE, 8 LIGHT across 69 pages |
| BL photos cover pages 1-176 | 38% of the book; later Russell refs are beyond range |

### What Was Built This Session

| Component | Before | After |
|-----------|--------|-------|
| Site pages | 300 | **335** |
| Dictionary terms | 80 | **94** (15 categories) |
| Terms with significance prose | 0 | **94** |
| Scholar pages | 30 (no overviews) | **60** (59 with overviews) |
| Timeline tab | Did not exist | **71 events** |
| Manuscripts tab | Did not exist | **6 copy pages** |
| Annotations table | 0 rows | **282 rows, 6 types** |
| Alchemical symbols | Did not exist | **10 symbols, 26 occurrences** |
| Match confidence: LOW | 218 | **0** |
| Match confidence: HIGH | 26 | **48** |
| Nav tabs | 11 | **13** |
| Woodcuts detected | 0 | **18** (not yet built into site) |
| BL pages verified | 0 | **69** |
| Design docs written | 6 | **12** |

### What Was Fixed

- BL photo-to-folio offset corrected (=13)
- 257 wrong matches deleted, 39 correct matches created
- Annotation types classified (was all MARGINALIA, now 6 distinct types)
- Hand attribution improved (193 → 204 of 282)
- Bibliography "Unknown" authors fixed (Priki identified, Routledge volume attributed to O'Neill)
- HPONTOLOGY.md rewritten to describe actual 22-table system
- WRITING_TEMPLATES.md updated for educated lay reader voice
- hp_copies confidence for BL updated from LOW to MEDIUM

---

## What the Isidore Critique Found

The concordance is structurally sound: zero orphan records, zero integrity
violations, zero nav errors, zero LOW matches. The problems are all
presentation gaps:

1. **Woodcut research done but not built into the site** — 18 woodcuts
   detected, ontology designed, template written, nothing rendered
2. **Annotation types computed but invisible** — 282 annotations classified
   into 6 types, none shown on folio pages
3. **Flyleaf has no annotation record** — the Master Mercury declaration
   has a folio description but no annotation row
4. **33 .md files unorganized** — documentation overload without an index
5. **41 scripts without a dependency graph** — no one knows the execution order
6. **Match count overstates coverage** — 431 matches sounds comprehensive
   but 4 of 6 studied copies have zero photographs

---

## Why "Outward Not Deeper"

The project's chronic pattern is: research a topic, design the schema,
write the spec, generate the data — then move on to the next topic before
building the pages. The result is a rich database with a thin website.

The database has:
- 94 dictionary terms with significance prose (not all shown on site)
- 282 classified annotations (types not displayed)
- 26 symbol occurrences (shown on some folio pages but not all)
- 18 detected woodcuts (not in the database at all)
- 71 timeline events (page built)
- 6 manuscript copy descriptions (pages built)
- 59 scholar overviews (shown on pages)

The site has 335 pages but many of the enrichments from this session
are invisible to visitors. The next phase should make them visible.

---

## The Plan (from NEXTPHASE.md)

### Phase 1: Woodcuts Tab (1 hour)
Seed 18 woodcuts into the database. Build index + detail pages. Add to nav.
This is the highest-impact unbuilt content.

### Phase 2: Annotation Types on Pages (30 min)
Update marginalia pages to show annotation_type badges and query the
annotations table instead of dissertation_refs.

### Phase 3: Data Fixes (30 min)
Add flyleaf annotation record. Document 4 unmapped signatures. Update
concordance status numbers.

### Phase 4: Documentation Organization (30 min)
Create DOCUMENTATION_INDEX.md categorizing all 39 .md files. Create
scripts/README.md with dependency graph. Update CLAUDE.md.

### Phase 5: README Update (15 min)
Current numbers, architecture, build instructions.

### Phase 6: More BL Reading (2 hours, optional)
Read remaining ~120 text pages for complete woodcut inventory and
annotation density map.

---

## What Not To Do Next

- Do not design another database table
- Do not write another specification document
- Do not start another research investigation
- Do not expand the dictionary further
- Do not add more scholar overviews

Instead: build the pages, display the data, fix the gaps, organize
the documentation. Then deploy and let the site speak for itself.
