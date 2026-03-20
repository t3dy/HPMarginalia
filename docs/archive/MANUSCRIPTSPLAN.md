# MANUSCRIPTSPLAN: Execution Plan for the Manuscripts Tab

## What Exists

- **2 manuscripts** in `manuscripts` table (BL and Siena — only copies with local images)
- **11 annotator hands** in `annotator_hands` table across 6 copies
- **282 dissertation references** distributed across 6 shelfmarks
- **610 image matches** linking references to photographs
- **Full spec** at `docs/MANUSCRIPTS_SPEC.md` with data model, essay templates, and pipeline
- **Corpus evidence** in Russell's thesis chunks (73 chunks, covering all 6 copies)

## What Needs Building

### Schema: `hp_copies` Table (5 minutes)

New table tracking all known HP copies worldwide:
```sql
hp_copies (id, shelfmark, institution, city, country, edition,
           has_annotations, studied_by, annotation_summary,
           hand_count, copy_notes, has_images_in_project,
           istc_id, review_status, source_method, confidence)
```

Script: `scripts/seed_copies.py` (to create)

### Content: Russell's 6 Annotated Copies (30 minutes)

Seed with full metadata from the DB:

| Copy | Institution | Hands | Refs | Images | Confidence |
|------|------------|-------|------|--------|------------|
| C.60.o.12 | British Library | 2 | 50 | 196 | LOW (1545 ed.) |
| Buffalo RBR | Buffalo & Erie County PL | 5 | 59 | 0 | N/A |
| Inc.Stam.Chig.II.610 | Vatican Library | 1 | 55 | 0 | N/A |
| INCUN A.5.13 | Cambridge UL | 1 | 42 | 0 | N/A |
| Modena (Panini) | Biblioteca Panini | 1 | 29 | 0 | N/A |
| O.III.38 | Biblioteca degli Intronati | 1 | 28 | 478 | HIGH |

Additional copies from ISTC/bibliography to be researched.

### Per-Copy Essays (2 hours)

Six essays, each 800-2000 words, grounded in DB + corpus evidence:

**1. BL C.60.o.12** — The most complex: two hands (Jonson + alchemist), 1545 edition problem, Master Mercury declaration, alchemical ideogram vocabulary, Thomas Bourne provenance, LOW confidence concordance. Links to: Russell essay, alchemical dictionary terms.

**2. Buffalo RBR** — Five interleaved hands, the most densely annotated copy. Jesuit/St. Omer connection for Hands A-D. Hand E pseudo-Geber alchemist. Chess match interpretation (h1r). Stratigraphic analysis. Links to: Sol/Luna, chemical wedding terms.

**3. Vatican Chig.II.610** — Alexander VII as reader. Acutezze (verbal wit) focus. Connection to Bernini commission. Papal reader as cultural patron. Links to: acutezze, elephant-obelisk terms.

**4. Cambridge INCUN A.5.13** — Benedetto Giovio's Plinian reading. HP as natural history compendium. Extractive annotation mode (inventio). Links to: inventio, activity-book terms.

**5. Modena (Panini)** — Also Giovio. Comparison with Cambridge annotations. Bibliographic and natural-historical interests. Links to: same as Cambridge.

**6. Siena O.III.38** — Anonymous annotations. 478-image digital facsimile. HIGH confidence matches. Basis for the most reliable concordance data. Links to: signature, folio, concordance essay.

Script: `scripts/generate_copy_essays.py` (to create)
Evidence source: `scripts/build_essay_data.py` + `scripts/corpus_search.py`

### Page Builder (1 hour)

Add to `build_site.py`:
- `build_manuscripts_page()` — landing page with annotated copies cards + other copies table
- `build_manuscripts_detail_pages()` — per-copy essay pages in `site/manuscripts/`
- Add "Manuscripts" tab to `nav_html()`

### Cross-Linking (15 minutes)

- Copy pages link to: scholar pages (annotators), dictionary terms, marginalia pages, essays
- Historical figure scholar pages link to their copy pages
- Dictionary terms (annotator-hand, marginalia, world-census) link to manuscripts landing
- Russell essay links to relevant copy pages
- Concordance essay links to BL and Siena copy pages

## Execution Order

```
1. scripts/seed_copies.py              # Create table + seed 6 copies
2. scripts/generate_copy_essays.py     # Generate 6 essays from evidence
3. Update build_site.py                # Add page builders + nav tab
4. python scripts/build_site.py        # Rebuild
5. Validate                            # Nav, paths, page count
6. Deploy                              # git push
```

## Infrastructure vs Prompts

Everything above is grounded in `docs/MANUSCRIPTS_SPEC.md`. The spec defines:
- The exact table schema (lines 25-40)
- The 6 copy metadata (lines 46-56)
- The essay template structure (lines 68-84)
- The pipeline steps (lines 113-143)
- The validation gates (lines 168-178)

A future session reads that file, creates the scripts, and executes. No prompt needed.

## What This Plan Does NOT Do

- Does not populate ISTC copies beyond Russell's 6 (needs ISTC database access)
- Does not create a world map visualization (would require a mapping library)
- Does not host high-resolution manuscript images (storage/permission blocker)
- Does not generate commentary overlays on images (future edition phase)

## Dependencies

- Requires corpus_search.py (already built) for essay evidence retrieval
- Requires build_essay_data.py pattern (already built) for structured evidence extraction
- Requires WRITING_TEMPLATES.md Template 6 (essays) for prose style
- Requires enriched dictionary (already 94 terms) for cross-linking
