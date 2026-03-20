# Hypnerotomachia Poliphili -- Digital Marginalia & Scholarship

A digital humanities project documenting the readership, marginalia, and scholarship of the *Hypnerotomachia Poliphili* (Venice: Aldus Manutius, 1499), based on James Russell's PhD thesis *Many Other Things Worthy of Knowledge and Memory* (Durham University, 2014).

**Live site**: [https://t3dy.github.io/HPMarginalia](https://t3dy.github.io/HPMarginalia)

## What's Here

| Section | Content |
|---------|---------|
| **Home** | Marginalia gallery -- 305 annotated folio images with lightbox viewer, filters by manuscript |
| **Marginalia** | 118 individual folio pages with images, hand attributions, alchemist tags, and Russell's commentary |
| **Scholars** | 60 scholar profiles (59 with overviews, 11 historical figures) spanning 1899-2024 |
| **Bibliography** | 109 entries grouped by relevance (Primary, Direct, Indirect), with collection/review badges |
| **Dictionary** | 94 terms across 15 categories with significance prose, cross-links, and provenance badges |
| **Timeline** | 71 events spanning 1499-2024: editions, annotations, scholarship, art inspired by the HP |
| **Manuscripts** | 6 annotated copies studied by Russell, with hand profiles and concordance data |
| **Docs** | 18 project documents (methodology, architecture, audits, critiques, planning) |
| **Code** | 31 Python pipeline scripts with full source and descriptions |
| **Edition** | Digital edition prospectus with phased roadmap |
| **Essays** | Russell's Alchemical Hands + Concordance Methodology, grounded in DB evidence |
| **About** | Database statistics, data provenance, and rebuild instructions |

## Architecture

SQLite is the source of truth. Python scripts generate JSON and static HTML pages. No framework, no build tools, no JavaScript dependencies.

```
db/hp.db                    SQLite database (20 tables)
scripts/                    Python pipeline (31 scripts)
  build_site.py             Unified site generator (all pages + JSON)
  migrate_v2.py             Schema migration (idempotent)
  seed_dictionary.py        Dictionary terms (idempotent)
  validate.py               QA checks and audit report
  ingest_perplexity.py      Web research ingestion
  init_db.py                Initialize base schema
  catalog_images.py         Parse image filenames
  build_signature_map.py    Aldine collation formula
  extract_references.py     Extract refs from thesis PDF
  match_refs_to_images.py   Match refs to images
  add_hands.py              Annotator hand profiles
  add_bibliography.py       Bibliography and timeline
  pdf_to_markdown.py        PDF text extraction
  chunk_documents.py        Semantic chunking for RAG
site/                       Generated static site
  index.html                Marginalia gallery (JS-driven)
  scholars.html             Scholars overview
  bibliography.html         Full HP bibliography
  about.html                Project info and stats
  scholar/*.html            60 individual scholar pages
  dictionary/index.html     Dictionary landing (15 categories)
  dictionary/*.html         94 individual term pages
  marginalia/index.html     Folio grid index
  marginalia/*.html         118 individual folio pages
  timeline.html             Chronological reception history (71 events)
  manuscripts/index.html    Annotated copies landing
  manuscripts/*.html        6 individual copy pages
  digital-edition.html      Edition prospectus
  russell-alchemical-hands.html  Essay on alchemical annotators
  concordance-method.html   Concordance methodology essay
  docs/index.html           Project documents index
  docs/*.html               14 document pages (rendered markdown)
  code/index.html           Pipeline scripts index
  code/*.html               16 script pages (with line numbers)
  data.json                 Gallery data export with confidence flags
  style.css                 Base styles (warm parchment palette)
  scholars.css              Scholar/paper card styles
  components.css             Shared component styles (extracted from inline)
  script.js                 Gallery lightbox and filters
```

## How to Rebuild

```bash
# Full rebuild from database
python scripts/migrate_v2.py        # Schema migration (safe to re-run)
python scripts/seed_dictionary.py   # Dictionary terms (safe to re-run)
python scripts/build_site.py        # Generate all HTML + JSON

# Validation
python scripts/validate.py          # QA checks + audit report

# Full pipeline from scratch (requires PDFs + PyMuPDF)
python scripts/init_db.py
python scripts/catalog_images.py
python scripts/build_signature_map.py
python scripts/extract_references.py
python scripts/match_refs_to_images.py
python scripts/add_hands.py
python scripts/add_bibliography.py
python scripts/migrate_v2.py
python scripts/seed_dictionary.py
python scripts/build_site.py
```

## Data Provenance

| Data | Method | Confidence |
|------|--------|------------|
| Signature map | Deterministic (Aldine collation formula) | Verified |
| Image cataloging | Deterministic (filename parsing) | Verified |
| Siena image matches | Folio-exact (explicit r/v naming) | HIGH |
| BL image matches | Folio-exact (assumes photo# = folio#) | LOW |
| Scholar summaries | LLM-assisted (Claude) | Unreviewed |
| Dictionary definitions | LLM-assisted (Claude) | Unreviewed (Draft) |
| Hand attributions | LLM-assisted (from Russell's prose) | Unreviewed |
| Scholar/bibliography metadata | LLM-assisted + web search | Unreviewed |
| Timeline events | LLM-assisted | Unreviewed |

Content marked **Unreviewed** is displayed with review badges on the site.
BL matches are displayed with LOW confidence badges and "Unverified" warnings.

## Key Database Tables

| Table | Rows | Purpose |
|-------|------|---------|
| `images` | 674 | Cataloged manuscript photographs |
| `signature_map` | 448 | Signature-to-folio concordance |
| `dissertation_refs` | 282 | Folio references from Russell's thesis |
| `matches` | 610 | Image-reference matches (26 HIGH, 218 LOW, 366 MEDIUM) |
| `annotators` | 11 | Identified annotator hands (2 alchemists) |
| `bibliography` | 109 | HP scholarship with gap analysis |
| `scholars` | 60 | Scholar profiles (1780-present) |
| `dictionary_terms` | 37 | HP terminology glossary |
| `dictionary_term_links` | 76 | Cross-reference links between terms |
| `timeline_events` | 42 | Publication/scholarship timeline (1499-2024) |
| `document_topics` | 34 | Multi-value topic cluster assignments |

## Project Documents

See the [Docs tab](https://t3dy.github.io/HPMarginalia/docs/index.html) for full text, or browse in the repo:

| Document | Description |
|----------|-------------|
| `HPCONCORD.md` | Concordance methodology (6-step pipeline) |
| `HPDECKARD.md` / `HPDECKARD2.md` | Deckard boundary audits (deterministic vs. LLM tasks) |
| `HPMIT.md` | MIT Electronic Hypnerotomachia site analysis |
| `HPMULTIMODAL.md` | Multimodal RAG architecture study |
| `HPproposals.md` | Content quality improvement proposals |
| `HPAGENTS.md` | Agent usage analysis |
| `HPEMPTYOUTPUTFILES.md` | Empty output files post-mortem |
| `MISTAKESTOAVOID.md` | 12 lessons learned |
| `HPRACHAEL.md` / `HPWEBAESTHETICS.md` | Visual design logic audit |
| `HPONTOCRIT.md` | Ontology critique (9 issues, gap between model and implementation) |
| `HPengCRIT.md` | Prompt engineering critique (9 patterns identified) |
| `HPromptTRANSCRIPT.md` | Transcript of all user prompts |
| `AUDIT_REPORT.md` | Validation results |

## Progress Log

### Phase 1: Foundation (Database + Gallery)
- Built SQLite database with 18 tables from Russell's PhD thesis
- Extracted 282 folio references via regex from thesis PDF
- Cataloged 674 manuscript images (196 BL, 478 Siena)
- Built 448-entry signature-to-folio concordance
- Created 610 image-reference matches
- Identified 11 annotator hands across 6 manuscript copies
- Deployed marginalia gallery with lightbox viewer and manuscript filters

### Phase 2: Scholarship Layer
- Summarized 34 scholarly articles via LLM batch processing
- Built 30 scholar profile pages with article summaries
- Created 109-entry bibliography with gap analysis against Russell's 310 citations
- Added 42 timeline events spanning 1499-2024
- Ingested web research (Perplexity, web search) discovering O'Neill 2023 Routledge monograph, Rhizopoulou 2016/2022 botanical studies, Young 2024 new translation

### Phase 3: Architecture Hardening (V2 Migration)
- Added review/provenance fields to all tables (confidence, needs_review, reviewed, source_method)
- Downgraded 218 BL matches from MEDIUM to LOW confidence
- Created normalized annotators table and doc_folio_refs with provenance
- Added document_topics junction table for multi-value topic clusters

### Phase 4: Dictionary + New Page Types
- Seeded 37 dictionary terms across 6 categories with 76 cross-reference links
- Built 118 marginalia folio detail pages with hand attributions
- Added bibliography tab (109 entries, 4 relevance tiers)
- Added docs tab (19 project documents rendered as HTML)
- Added code tab (22 pipeline scripts with line-numbered source)
- Added about page with database statistics and provenance documentation

### Phase 5: Alchemist Analysis
- Wrote 13 folio-specific scholarly descriptions for the two alchemist annotators
- BL Hand B (d'Espagnet school): 9 folios analyzed (flyleaf manifesto, dawn/Albedo, Elephant & Obelisk ideograms, Panta Tokadi/cinnabar/digestion, Fons Heptagonis seven metals)
- Buffalo Hand E (pseudo-Geber school): 4 folios analyzed (Geber's ingenium, Bacchus-Demeter as Sol-Luna, chess match as distillation, hermaphroditic metals)

### Phase 6: Design + Deployment
- Extracted inline CSS into shared components.css
- Fixed CSS path inconsistencies for GitHub Pages (relative paths throughout)
- Synchronized navigation bar across all pages (8 tabs)
- Warmed badge colors to match the parchment palette
- Added orientation copy to all tab landing pages
- Deployed via GitHub Actions to https://t3dy.github.io/HPMarginalia/

### Audits Conducted
- 2x Deckard boundary audits (deterministic vs. probabilistic tasks)
- 1x Rachael aesthetic audit (9 design issues, 5 fixed)
- 1x Isidore ontology critique (9 issues, 3 structural)
- 1x Isidore prompt engineering critique (9 patterns)
- 1x Agent usage analysis (with empty output file post-mortem)
- 1x Validation pass (0 critical issues)

### What Still Needs Human Review
- All 34 article summaries (LLM-generated, not verified against source)
- All 37 dictionary definitions (LLM-drafted)
- Scholar birth/death years and institutional affiliations
- BL photo-to-folio mapping (218 matches at LOW confidence)
- 13 alchemist folio descriptions (LLM synthesis from Russell, not Russell's own words)

## Dependencies

- Python 3.10+
- SQLite3 (bundled with Python)
- PyMuPDF (`pip install PyMuPDF`) -- only needed for PDF extraction pipeline

No web framework required. The site is plain HTML/CSS/JS with zero runtime dependencies.
