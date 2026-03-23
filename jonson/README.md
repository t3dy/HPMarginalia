# Ben Jonson & The Alchemist: Digital Humanities Project

A disciplined digital humanities project presenting Ben Jonson's relationship
to alchemy through three lenses:

1. **An annotated digital edition of *The Alchemist*** explaining the play's
   specifically alchemical dimensions — chemical meanings, alchemical theories,
   terminology, and symbolic/allegorical content relevant to alchemy.

2. **A structured Life of Ben Jonson** extracted from scholarly PDFs, presenting
   key biographical events in chronological order with citations.

3. **A research showcase** presenting James Russell's findings on Ben Jonson's
   annotations in the *Hypnerotomachia Poliphili* (BL C.60.o.12, Venice 1545).

## Scope

This project is intentionally narrow. It does not attempt to be a general
edition of *The Alchemist*, a comprehensive Jonson biography, or a study of
Kenelm Digby. Digby appears only as context for understanding Jonson's copy
of the Hypnerotomachia.

## Source Corpus

All source material lives in `../Ben Jonson Life/`. Converted markdown
versions are in `../Ben Jonson Life/md/`.

Five source documents:
- H.C. Hart's edition of *The Alchemist* (255-page PDF)
- Arden critical reader on *The Alchemist* (EPUB)
- James Mardock, *Our Scene is London* (175-page PDF on Jonson's city)
- Stanton Linden, *Darke Hierogliphicks* extract (alchemy in English literature)
- Russell & O'Neill presentation on Jonson's HP marginalia (46-slide PPTX)

## Pipeline

```
Source PDFs/EPUB/PPTX → Markdown (converted)
    → Ingest (catalog sources)
    → Extract (pull excerpts with page refs)
    → Classify (jonson_life / alchemist_alchemy / hypnerotomachia_jonson)
    → Transform (produce structured records)
    → Export (website-ready JSON)
    → Build (static HTML pages)
```

## Website Sections

- Home (project overview)
- About the Project
- Read The Alchemist
- Alchemical Annotations
- Life of Ben Jonson
- Jonson's Hypnerotomachia Annotations
- Sources / Bibliography

## What Is Implemented

### Seed (current)
- [x] Source documents converted to markdown
- [x] Project structure created
- [x] Data schemas defined
- [x] Ingest pipeline (source cataloging)
- [x] Vertical slice: 1 LifeEvent + 1 Annotation + 1 RussellFinding
- [x] Minimal site pages integrated with HP nav

### Planned
- [ ] Full excerpt extraction from all 5 sources
- [ ] LLM-assisted classification and structured extraction
- [ ] Complete Alchemist text with act/scene structure
- [ ] Full annotation set for alchemical passages
- [ ] Complete life timeline
- [ ] Complete Russell findings showcase
- [ ] Bibliography page

## Build

```bash
python jonson/scripts/build.py
```
