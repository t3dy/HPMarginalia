# HPDECKARD2: Boundary Map v2 -- Bibliography & Digital Edition Expansion

> Second Deckard audit, covering the bibliography expansion, web research ingestion, digital edition planning, and the agent orchestration layer.

## Current System State (Post-V2 Migration)

- **18 database tables**, 97 bibliography entries, 52 scholars, 37 dictionary terms
- **13 Python scripts** in the pipeline, all deterministic
- **LLM-assisted content** generated in conversation, hardcoded into scripts, then loaded into DB
- **New data sources**: HPPERPLEXITY.txt (web research), web search results, MIT site analysis

---

## DETERMINISTIC TASKS

| Task | Current Method | Verdict |
|------|---------------|---------|
| Signature map generation | Aldine collation formula in Python | CORRECT |
| Image filename parsing | Regex on known naming conventions | CORRECT |
| Folio-to-image matching | SQL join on folio numbers | CORRECT |
| Site page generation | Jinja-like string templates in build_site.py | CORRECT |
| Dictionary page generation | DB query -> HTML template | CORRECT |
| Marginalia page generation | DB query -> HTML template | CORRECT |
| JSON data export | SQL query -> JSON serialization | CORRECT |
| Schema migration | Idempotent SQL DDL | CORRECT |
| Validation checks | SQL integrity queries | CORRECT |

**All 13 scripts remain purely deterministic. No LLM in the codebase.** This is correct.

---

## PROBABILISTIC TASKS

### Currently Done by LLM in Conversation

| Task | Where | Appropriate? | Risk Level |
|------|-------|-------------|------------|
| Article summarization (34 papers) | Claude agents -> summaries.json | YES | MEDIUM -- summaries not human-verified |
| Perplexity research ingestion | Claude reading HPPERPLEXITY.txt -> ingest_perplexity.py | YES | LOW -- URLs are verifiable |
| Web scholarship search | Claude web search -> manual extraction | YES | MEDIUM -- author/title/year need verification |
| MIT site analysis | Claude WebFetch -> HPMIT.md | YES | LOW -- architectural analysis, not factual claims |
| Hand attribution from thesis text | Claude reading Russell -> add_hands.py | YES | MEDIUM -- signature-hand mapping is interpretive |
| Dictionary definition writing | Claude -> seed_dictionary.py | YES | MEDIUM -- definitions cite sources but are original compositions |
| Scholar metadata (birth/death, nationality) | Claude -> add_bibliography.py | YES | HIGH -- factual claims that could be wrong |
| Bibliography gap analysis | Claude reading Russell's bibliography | YES | LOW -- gap detection is mechanical; titles are checkable |

### Planned Tasks That SHOULD Be Probabilistic

| Task | Why Probabilistic |
|------|-------------------|
| **Bibliography verification** | Checking if a cited work actually exists, confirming author names and publication details, requires web lookup + judgment |
| **Citation formatting** | Converting messy bibliographic data into consistent format (Chicago, MLA) requires understanding of citation conventions |
| **Cross-referencing scholars to works** | Author name matching is fuzzy (e.g., "James O'Neill" vs "James Calum O'Neill" vs "O'Neill, James C.") |
| **Topic cluster assignment** | Single works span multiple topics; classification requires reading comprehension |
| **Woodcut identification** | Mapping woodcut subjects ("Elephant and Obelisk", "Fons Heptagonis") to specific page images |
| **Timeline event extraction from prose** | Finding datable events in article text requires NLP |

### Planned Tasks That SHOULD Be Deterministic

| Task | Why Deterministic |
|------|-------------------|
| **Bibliography deduplication** | Matching author+title+year strings; fuzzy string matching (Levenshtein) suffices |
| **DOI/ISBN lookup** | CrossRef and WorldCat APIs return structured data deterministically |
| **Citation formatting from structured data** | Given author/title/year/journal, formatting is rule-based |
| **URL validation** | HTTP HEAD request to check if a URL is alive |
| **IIIF manifest generation** | Given image dimensions and folio numbers, manifest structure is formulaic |

---

## BOUNDARY VIOLATIONS

### WASTE: LLM Doing What Code Could Do

| Violation | Current State | Recommendation |
|-----------|--------------|----------------|
| **Scholar-bibliography name matching** | Currently done by SQL LIKE with manual fixup | Use Levenshtein distance or token-set-ratio matching. Libraries like `fuzzywuzzy` or `rapidfuzz` handle this deterministically. |
| **URL alive checking** | Not done at all -- HPPERPLEXITY.txt URLs unchecked | Add a `scripts/check_urls.py` that sends HEAD requests to all URLs in the bibliography table |
| **Bibliography deduplication** | Relies on exact title match in INSERT OR IGNORE | Add fuzzy dedup: normalize titles (lowercase, strip articles, normalize whitespace) before insert |

### RISK: Deterministic Code Doing What Needs Judgment

| Violation | Current State | Risk |
|-----------|--------------|------|
| **BL photo-folio assumption** | match_refs_to_images.py assumes photo_number = folio_number | Now marked LOW confidence (fixed in V2), but still presented as valid matches. Should show "PROVISIONAL: unverified mapping" on BL pages. |
| **Single topic_cluster per bibliography entry** | bibliography.topic_cluster is a single TEXT field | A work like Stewering's straddles architecture AND text-image. The document_topics junction table exists but isn't fully populated. |
| **Author name as scholar identifier** | scholars.name is UNIQUE but author names aren't unique globally | "James O'Neill" vs "James Calum O'Neill" -- these are the same person. Need a normalization step. |

### DANGER: Unvalidated LLM Output Entering the System

| Violation | Source | Danger |
|-----------|--------|--------|
| **Perplexity research with "Unknown" authors** | ingest_perplexity.py inserted 4 entries with "Unknown (botanical study)" etc. | These entries will appear on the bibliography page with no verifiable author. The web search found the actual authors (Rhizopoulou et al. 2016; Godwin 2020) but the DB wasn't updated. |
| **Scholar birth/death years** | add_bibliography.py hardcodes dates from conversation | E.g., "Myriam Billanovich" birth/death years are listed as None -- but if they were guessed wrong, the error would propagate silently. |
| **New Routledge volume misattributed** | HPPERPLEXITY.txt lists "Various (ed. unknown)" for the O'Neill 2023 Routledge book | Web search confirms this is James Calum O'Neill's *The Allegory of Love in the Early Renaissance*. The DB entry is wrong. |

---

## SPECIFIC RECOMMENDATIONS

### Immediate (Before Building Bibliography Tab)

1. **Fix the 4 "Unknown" author entries** from ingest_perplexity.py:
   - "Unknown (botanical study)" -> Sophia Rhizopoulou et al.
   - "Unknown (musicological study)" -> Joscelyn Godwin
   - "Unknown (UPenn repository)" -> needs URL fetch to identify
   - "Unknown (Polish publisher)" -> needs URL fetch to identify
   - "Various (ed. unknown)" -> James Calum O'Neill

2. **Add the new scholarship found in web search**:
   - O'Neill 2023, *The Allegory of Love in the Early Renaissance* (Routledge) -- this is a major new monograph
   - Rhizopoulou et al. 2022, botanical content revisited (Botany Letters 170:1)
   - Priki 2020, Mirrors and Mirroring (Bloomsbury chapter)
   - Koutsogiannis 2024, Greek antiquity images in HP
   - Guo 2021, HP and its afterlife (ICLACE proceedings)
   - Paul Summers Young, new English translation (Black Letter Press / Anathema Publishing)
   - O'Neill 2022, botanical symbolism (Word & Image 39:2)

3. **Add a `verified` flag** to bibliography entries, separate from `needs_review`. An entry can be reviewed (someone looked at it) but still unverified (hasn't been checked against WorldCat/CrossRef).

### For the Bibliography Tab

4. **Hybrid verification pipeline**:
   ```
   Step 1 (DETERMINISTIC): Normalize author names, deduplicate by fuzzy title match
   Step 2 (DETERMINISTIC): Look up DOI/ISBN via CrossRef API for each entry
   Step 3 (DETERMINISTIC): Validate URLs with HEAD requests
   Step 4 (LLM-ASSISTED): For entries without DOI, search the web to verify existence
   Step 5 (DETERMINISTIC): Format citations in Chicago style from structured data
   Step 6 (HUMAN): Review flagged entries where verification failed
   ```

5. **Display bibliography entries with provenance badges**:
   - "In Collection" (we have the PDF)
   - "Verified" (confirmed via CrossRef/WorldCat)
   - "Cited" (appears in Russell's bibliography but not independently verified)
   - "Discovered" (found via web search, needs verification)

### For the Digital Edition Tab

6. **The text transcription is the critical dependency**. The MIT site has a transcription but it's locked in HTML with no structured data. Options:
   - Extract from the MIT site (copyright: MIT Press 1997)
   - Use the Project Gutenberg text of the 1592 English (public domain)
   - Commission a fresh transcription from the public-domain 1499 images
   - License the Pozzi & Ciapponi critical edition text

7. **The marginalia overlay is our unique contribution** and should be the Phase 1 deliverable for the edition tab. We already have the data (282 folio refs, 610 image matches, 11 annotator hands). The text transcription can come later.

---

## BOUNDARY MAP SUMMARY

```
DETERMINISTIC (13/13 scripts -- CORRECT)
|-- Schema, migration, seed       [migrate_v2, seed_dictionary, init_db]
|-- File parsing                  [catalog_images, pdf_to_markdown]
|-- Reference extraction          [extract_references]
|-- Matching                      [match_refs_to_images, build_signature_map]
|-- Export & generation           [build_site, export_showcase_data, build_scholar_profiles]
|-- Ingestion                     [ingest_perplexity, add_hands, add_bibliography]
|-- Validation                    [validate]

PROBABILISTIC (done in conversation, not in code)
|-- Article summarization         APPROPRIATE but unvalidated
|-- Web research ingestion        APPROPRIATE, partially verified
|-- Hand attribution              APPROPRIATE but approximate
|-- Dictionary definitions        APPROPRIATE, cites sources
|-- Scholar metadata              RISKY -- factual claims without cross-reference
|-- MIT site analysis             APPROPRIATE, low risk

BOUNDARY VIOLATIONS
|-- WASTE (3): name matching, URL checking, deduplication
|-- RISK (3): BL photo mapping, single topic clusters, name normalization
|-- DANGER (3): Unknown authors in DB, wrong Routledge attribution, scholar dates

PLANNED HYBRID PIPELINE (bibliography verification)
|-- Steps 1,2,3,5: DETERMINISTIC (normalize, CrossRef, URL check, format)
|-- Step 4: LLM-ASSISTED (web verification of unresolvable entries)
|-- Step 6: HUMAN (review flagged entries)
```

**Overall assessment**: The system's deterministic core is sound. The boundary violations are concentrated in the **ingestion layer** where LLM-generated content enters the database without validation gates. The fix is to add a verification pipeline (deterministic where possible, LLM-assisted where necessary, human-reviewed for flagged items) before displaying content as authoritative. The bibliography tab should be the first feature to implement this hybrid verification model.
