# Phase Report: Site Hardening and Enrichment

**Date:** 2026-03-18
**Scope:** Layers 1-6 (Schema extension through final build)

## Summary of Changes

### New Infrastructure Scripts (6 files added)

| Script | Purpose | Lines |
|--------|---------|-------|
| `scripts/migrate_dictionary_v2.py` | Extends dictionary_terms with 10 new columns | ~50 |
| `scripts/corpus_search.py` | Keyword-based search across /chunks/ and /md/ corpus | ~170 |
| `scripts/dictionary_audit.py` | Coverage audit: missing fields, duplicates, orphans | ~120 |
| `scripts/build_reading_packets.py` | Assembles structured research packets from corpus | ~160 |
| `scripts/enrich_dictionary.py` | Populates dictionary fields from reading packets | ~150 |
| `scripts/build_essay_data.py` | Extracts structured evidence for both essays | ~200 |

### Modified Files

| File | Changes |
|------|---------|
| `scripts/build_site.py` | Added 3 new nav tabs, 3 new page builders (Russell essay, Concordance essay, Digital Edition stub), enriched dictionary template with 10 sections and provenance badges, new CSS for review status badges and dictionary sections, updated SCRIPT_METADATA |
| `db/hp.db` | 10 new columns on dictionary_terms; 37 terms enriched with source_documents, source_page_refs, source_quotes_short, source_method, confidence, notes |

### New Staging Artifacts

| Artifact | Contents |
|----------|----------|
| `staging/packets/*.json` (37 files) | Reading packets for all dictionary terms |
| `staging/essay_russell.json` | Structured evidence for Russell essay |
| `staging/essay_concordance.json` | Structured evidence for Concordance essay |
| `staging/dictionary_audit.json` | Dictionary coverage report |
| `staging/README.md` | Pipeline documentation |

### New Generated Pages (3 pages added)

| Page | Type | Nav Key |
|------|------|---------|
| `site/russell-alchemical-hands.html` | Essay (grounded in DB + corpus evidence) | russell |
| `site/concordance-method.html` | Methodological essay (grounded in DB stats) | concordance |
| `site/digital-edition.html` | Editorial prospectus stub | edition |

### Updated Generated Pages

- **All 222 pages** now include the updated 11-tab navigation
- **37 dictionary term pages** now display enriched template with:
  - Source documents section
  - Page references section
  - Key passages / evidence section
  - Review status / provenance badges (DRAFT/REVIEWED/VERIFIED)
  - Source method and confidence metadata
- **Code index** now lists 22 scripts (6 new pipeline scripts added)

## Dictionary Pipeline Improvements

- Extended schema with 10 new columns for enrichment data
- Built reusable corpus search (keyword-based, no embedding dependencies)
- Built reading packet pipeline: audit -> search -> packet -> enrich -> build
- All 37 terms enriched with corpus evidence from 20 source documents
- Source provenance tracked on every enriched field
- No VERIFIED content overwritten (promotion rule enforced)

## Validation Results

- **222 pages checked**: 0 errors
- All pages contain the complete 11-tab navigation
- No hardcoded absolute paths detected
- No missing CSS references
- No duplicate dictionary slugs
- No orphaned dictionary links
- All dictionary terms have category and review_status

## What Remains Provisional

### HIGH priority (blocks trustworthy claims)
- All BL C.60.o.12 image-to-folio matches (LOW confidence; sequential numbering assumption unverified)
- The 1545/1499 edition difference for the BL copy is unresolved

### MEDIUM priority (DRAFT content needing expert review)
- All 37 dictionary terms are at DRAFT status
- Dictionary significance_to_hp and significance_to_scholarship fields are currently NULL (not populated by corpus extraction alone; require LLM-assisted or human-written prose)
- Dictionary related_scholars fields are currently NULL
- Scholar summaries remain LLM-generated DRAFT
- Russell essay claims about specific annotations depend on extracted dissertation data, not direct manuscript inspection

### LOWER priority (improvement opportunities)
- Dictionary entries could be further enriched with significance prose via targeted LLM assistance (with DRAFT provenance)
- Bibliography entries lack cross-links to essays and dictionary terms at the DB level
- Scholar pages lack links to relevant dictionary terms
- No structured editorial review workflow exists

## Unresolved Review Items

1. **BL concordance verification**: Manual comparison of BL photograph numbers against physical or high-resolution folio images
2. **Dictionary expert review**: All 37 terms need domain expert review to move from DRAFT to REVIEWED
3. **Essay fact-checking**: Both essays should be reviewed by someone familiar with Russell's thesis
4. **Significance fields**: significance_to_hp and significance_to_scholarship need human or LLM-assisted prose (currently NULL)
5. **Scholar-dictionary cross-links**: Not yet implemented at DB level
6. **Transcription**: No HP text transcription exists in the project

## Recommended Next Phase

**Priority 1: Dictionary Significance Enrichment**
Use LLM-assisted generation with DRAFT provenance to populate significance_to_hp and significance_to_scholarship for all 37 terms. The reading packets already contain the necessary evidence context.

**Priority 2: Scholar Page Improvement**
Enhance scholar pages with longer summaries, individual article/book detail pages, and cross-links to dictionary terms and bibliography. (This aligns with the user's separate request for scholar page improvements.)

**Priority 3: BL Concordance Verification**
If high-resolution BL images become available, use multimodal analysis to verify photo-to-folio mappings and upgrade LOW confidence matches.

**Priority 4: Cross-Linking at DB Level**
Add junction tables or structured fields linking bibliography entries to dictionary terms, scholars to essays, and documents to dictionary terms.
