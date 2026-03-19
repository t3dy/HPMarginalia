# Hypnerotomachia Poliphili -- Digital Marginalia & Scholarship

A digital humanities project documenting the readership, marginalia, and scholarship of the *Hypnerotomachia Poliphili* (Venice: Aldus Manutius, 1499), based on James Russell's PhD thesis *Many Other Things Worthy of Knowledge and Memory* (Durham University, 2014).

**Live site**: [https://t3dy.github.io/HPMarginalia](https://t3dy.github.io/HPMarginalia)

## What's Here

| Section | Content |
|---------|---------|
| **Home** | Marginalia gallery -- 305 annotated folio images with lightbox viewer, filters by manuscript |
| **Marginalia** | 118 individual folio pages with images, hand attributions, alchemist tags, and Russell's commentary |
| **Scholars** | 30 scholar profiles with article summaries spanning 1899-2024 |
| **Bibliography** | 109 entries grouped by relevance (Primary, Direct, Indirect), with collection/review badges |
| **Dictionary** | 37 terms across 6 categories (Book History, Annotation Studies, Alchemical, Architecture, Textual Motifs, Scholarly Debates) with 76 cross-reference links |
| **Docs** | 14 project documents (methodology, architecture, audits, proposals, lessons learned) |
| **Code** | 16 Python pipeline scripts with full source and descriptions |
| **About** | Database statistics, data provenance, and rebuild instructions |

## Architecture

SQLite is the source of truth. Python scripts generate JSON and static HTML pages. No framework, no build tools, no JavaScript dependencies.

```
db/hp.db                    SQLite database (18 tables)
scripts/                    Python pipeline (16 scripts)
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
  scholar/*.html            30 individual scholar pages
  dictionary/index.html     Dictionary landing (6 categories)
  dictionary/*.html         37 individual term pages
  marginalia/index.html     Folio grid index
  marginalia/*.html         118 individual folio pages
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
| `AUDIT_REPORT.md` | Validation results |

## Dependencies

- Python 3.10+
- SQLite3 (bundled with Python)
- PyMuPDF (`pip install PyMuPDF`) -- only needed for PDF extraction pipeline

No web framework required. The site is plain HTML/CSS/JS with zero runtime dependencies.
