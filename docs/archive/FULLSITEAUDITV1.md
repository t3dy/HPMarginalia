# FULLSITEAUDITV1: Complete Site Audit with Gaps and Desiderata

> Everything the site has, everything it's missing, and everything that
> needs a human to check. Written for the project owner who wants to
> know exactly where things stand.

---

## 1. What the Site Has (364 pages)

| Section | Pages | Source Data | Status |
|---------|-------|------------|--------|
| Home | 1 | 223 gallery entries from matches + images | BUILT |
| Marginalia | 109 | 113 folio pages + index | BUILT |
| Scholars | 61 | 60 detail + index, 59 with overviews | BUILT |
| Bibliography | 1 | 109 entries | BUILT |
| Dictionary | 95 | 94 terms + index, all with significance prose | BUILT |
| Docs | 34 | 15 on index + individual pages | BUILT |
| Code | 32 | 31 scripts + index | BUILT |
| Timeline | 1 | 71 events, filterable | BUILT |
| Woodcuts | 19 | 18 detail + index | BUILT |
| Manuscripts | 7 | 6 copies + index | BUILT |
| Edition | 1 | Stub/prospectus | BUILT (stub) |
| Alchemical Hands | 1 | Essay grounded in Russell Ch. 6-7 | BUILT |
| Concordance | 1 | Methodology essay | BUILT |
| About | 1 | Aggregate stats | BUILT |

---

## 2. Data Quality: What Needs Human Review

### NOTHING has been reviewed by a human expert.

Every piece of generated content in the database is marked DRAFT or
UNREVIEWED. The provenance tracking is honest — it says what it is.
But here's what that means in practice:

| Data Type | Count | Review Status | What a Reviewer Should Check |
|-----------|-------|--------------|------------------------------|
| Dictionary definitions | 94 | All DRAFT | Are the definitions accurate? Are the scholarly citations correct? Do the significance statements overstate or understate? |
| Dictionary significance_to_hp | 94 | All DRAFT (LLM_ASSISTED) | Does each significance statement accurately describe what the term means for the HP specifically? Are any claims unsupported? |
| Dictionary significance_to_scholarship | 94 | All DRAFT (LLM_ASSISTED) | Are the scholar attributions correct? Are any major scholars or arguments missing? |
| Scholar overviews | 59 | All DRAFT (LLM_ASSISTED) | Are the biographical details correct? Are the research descriptions accurate? Are any major works missing? |
| Scholar is_historical_subject | 11 tagged | DETERMINISTIC | Are there any scholars tagged as historical who shouldn't be, or vice versa? Is Jean d'Espagnet correctly classified? |
| Bibliography entries | 109 | All UNREVIEWED | Are the citations correct? Are any duplicates? Are the hp_relevance classifications right? |
| Bibliography "Unidentified" | 2 entries | UNRESOLVED | id=91 (UPenn "Architectures of the Text") and id=92 (Polish "Earliest Reception") — who wrote these? |
| Folio descriptions | 13 | All DRAFT (LLM_ASSISTED) | Do the alchemical folio analyses accurately represent Russell's arguments? Are the alchemical process stages correctly identified? |
| Woodcut descriptions | 18 | All DRAFT (CORPUS_EXTRACTION) | Are the subject descriptions accurate? Are any woodcuts misidentified? |
| Timeline events | 71 | All need_review=1 | Are the dates correct? Are any major events missing? |
| Annotation types | 282 | All need_review=1 | Is each annotation classified correctly? The classification was regex-based and refined once; a spot-check by a reader of Russell would improve confidence. |
| Hand attributions | 204 of 282 | Mix of deterministic and inferred | Are the 204 attributions correct? Are any of the 78 unattributed refs attributable from context? |

### Priority Items for Human Review

**High priority (affects trust):**
1. Spot-check 10 dictionary significance entries against their source citations
2. Verify the Russell essay claims against the thesis (especially the chess match reading and the Master Mercury declaration)
3. Check the 2 "Unidentified" bibliography authors

**Medium priority (affects completeness):**
4. Review the 5 thinnest scholar overviews (Pumroy, Keller, Poncet, Temple, Nygren) — are they accurate despite being brief?
5. Check whether the 11 historical figure tags are correct
6. Verify the 18 woodcut subject descriptions against the actual images

**Lower priority (affects refinement):**
7. Review annotation type classifications (sample 20, check accuracy)
8. Check timeline dates and event descriptions
9. Review the Siena match recto/verso assignments

---

## 3. Concordance Gaps

### Verified and Correct
- 39 BL matches: all folio-correct, 27 visually confirmed
- 392 Siena matches: all folio-correct
- 0 LOW confidence matches
- Offset = 13, confirmed at 27 points

### Known Gaps (cannot fix with current data)

| Gap | Count | Reason | What Would Fix It |
|-----|-------|--------|-------------------|
| Refs with no manuscript assigned | 19 | Russell discusses HP generally in Ch. 1, 3 | Manual assignment by someone who has read those chapters |
| BL refs beyond photo range | 7 | Photos cover pages 1-176 only | Photographs of BL pages 177-470 |
| Collation ambiguities | 8 | z5v, z6r, z5r, u3r | Physical examination of the books |
| Buffalo photos | 0 of 59 refs | No photographs available | Acquisition from Buffalo & Erie County PL |
| Vatican photos | 0 of 55 refs | No photographs available | Acquisition from Vatican Library |
| Cambridge photos | 0 of 42 refs | No photographs available | Acquisition from Cambridge UL |
| Modena photos | 0 of 29 refs | No photographs available | Acquisition from Biblioteca Panini |

### Siena Recto/Verso Ambiguity
Each Siena ref matches both recto and verso of its folio. Roughly half
the 392 matches show the correct page; the other half show the facing
page. Resolving this requires checking whether Russell's described
annotation appears on the recto or verso — a content judgment, not a
data-structure issue.

---

## 4. Content Gaps

### Dictionary
- **94 terms** is substantial but not exhaustive. The HP has hundreds
  of describable entities. Missing terms include: specific woodcut
  subjects (Sacrifice to Priapus, the sleeping nymph fountain as a
  distinct woodcut), specific architectural measurements and proportions
  that Poliphilo describes, and specific scholars' methodological
  concepts (e.g., Griggs's concept of "antiquarian syllogae").
- **related_scholars field** is NULL for all 94 terms. This should link
  terms to the scholars who have written about them.
- **No term has been VERIFIED.** All 94 are DRAFT.

### Scholars
- **59 overviews** range from 18 words (Poncet) to 1091 words (Russell).
  The shortest are placeholders, not genuine overviews.
- **scholar_works linking** has 72 entries but the scholars table has 60
  rows. Some scholars with no bibliography links have no "Works" section
  on their pages.
- **No scholar has been REVIEWED.** All 59 overviews are LLM-assisted DRAFT.

### Bibliography
- **109 entries, all UNREVIEWED.** No entry has been verified against
  its actual publication.
- **2 entries have "Unidentified" authors.** These need web or library
  research to resolve.
- **hp_relevance classifications** (PRIMARY, DIRECT, INDIRECT, TANGENTIAL)
  have not been checked by anyone who has read the works.
- **No bibliography annotations** (per-entry summaries) exist. The
  WRITING_TEMPLATES.md defines a template (Template 4) but it was
  never implemented.

### Woodcuts
- **18 of ~172 detected.** The BL photos cover only 38% of the book.
  The remaining ~154 woodcuts are known from scholarship but not
  cataloged in the database.
- **No woodcut attribution data** in the database beyond the general
  "Master of the Poliphilo" convention.
- **No 1499 vs 1545 comparison data** — the BL copy is the 1545 edition
  with recut blocks, but no field tracks which blocks were recut.

### Manuscripts
- **6 copy pages** with basic metadata and hand profiles.
- **No per-copy essays.** MANUSCRIPTS_SPEC.md defines 6 essays
  (800-2000 words each) but none have been written.
- **No ISTC data.** The ~200 known copies from ISTC are not cataloged.

### Timeline
- **71 events** covering 1499-2024. No music events confirmed.
  Art events are limited to major examples (Bernini, Watteau, Garofalo).
  Scholarship events cover major milestones but not all 109 bibliography
  entries.

---

## 5. Technical Gaps

### Site Architecture
- **build_site.py still queries dissertation_refs** for marginalia pages
  instead of the canonical annotations table. The annotation_type badges
  are shown, but the underlying data source should be switched.
- **Inline CSS** in page builder functions (~500 lines of embedded styles).
  Should be extracted to stylesheets for maintainability.
- **No favicon or OG tags.** The site has no social sharing metadata.
- **No search functionality.** The 364 pages are navigable only through
  the nav and internal links.

### Database
- **3 deprecated tables** (dissertation_refs, doc_folio_refs, annotators)
  still exist. They are documented as deprecated in ONTOLOGY.md but
  dissertation_refs is still actively queried.
- **matches.ref_id** still points to dissertation_refs.id, not
  annotations.id. A full migration would require updating this FK.

### Scripts
- **42 scripts** with no formal dependency graph beyond the rebuild
  sequence in PIPELINE.md.
- **No test suite.** No automated tests for any script.
- **No CI/CD.** Build is manual; deployment is git push.

---

## 6. What Only a Human Can Do

These items cannot be resolved by further automated processing:

1. **Read Russell's thesis** and verify that the essay claims accurately
   represent his arguments. Especially: the Master Mercury declaration
   translation, the chess match interpretation, the d'Espagnet vs
   pseudo-Geber distinction, and the Newton/Royal Society suggestion.

2. **Identify the 2 unknown bibliography authors.** id=91 and id=92
   need library research or web investigation by someone who can
   access the UPenn repository and the Polish academic press catalog.

3. **Spot-check dictionary significance prose.** Read 10 random
   significance_to_hp and significance_to_scholarship entries and flag
   any that are inaccurate, misleading, or unsupported by the cited source.

4. **Review the annotation type classifications.** Read 20 annotations
   classified as INDEX_ENTRY and verify they are genuine keyword labels,
   not false positives from the regex.

5. **Assess the scholar overview quality.** Are the 5 shortest overviews
   (18-27 words) worth publishing, or should they be replaced with
   "Overview not yet available"?

6. **Verify the BL photograph subjects against Russell's descriptions.**
   For the 13 folios with folio_descriptions, compare what's visible in
   the photograph against what Russell describes in the thesis. Flag
   any discrepancies.

7. **Decide whether the "facing page" Siena matches should be shown.**
   Currently both recto and verso are matched for each folio. Should the
   site show both, or should one be suppressed?

8. **Write the 6 manuscript copy essays.** These require synthesis of
   Russell's arguments about each copy, which is interpretive work
   beyond what automated extraction can produce reliably.

9. **Determine whether z5v/z6r/z5r/u3r are valid signatures.** This
   requires checking the physical collation of the relevant copies.

10. **Acquire photographs of the 4 remaining copies.** Buffalo, Vatican,
    Cambridge, Modena — this requires institutional contact and
    permission negotiation.

---

## 7. Summary Scorecard

| Dimension | Score | Notes |
|-----------|-------|-------|
| **Structural integrity** | A | 0 orphan records, 0 integrity violations, 0 nav errors |
| **Concordance accuracy** | A- | All matches correct; 34 refs unmatchable with current data |
| **Content coverage** | B | 94 terms, 60 scholars, 109 bib, 18 woodcuts — but gaps remain |
| **Content quality** | C+ | All DRAFT/UNREVIEWED; no human verification of any content |
| **Presentation** | B+ | 364 pages, 14 tabs, annotation types shown, woodcuts built |
| **Documentation** | A- | 5 core docs + specs + archive; clear and structured |
| **Provenance honesty** | A | Every generated datum marked with source_method and status |
| **Maintainability** | B- | 42 scripts, no tests, inline CSS, deprecated tables still queried |

**Overall: the system is honest about what it knows and doesn't know.
The biggest risk is not that the data is wrong — it's that DRAFT content
reads as authoritative because it's well-formatted. The review badges
mitigate this, but a human expert reviewing even 20% of the content
would substantially increase the project's trustworthiness.**
