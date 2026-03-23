# SYSTEM: Ben Jonson Project Architecture

## Purpose

A static website section presenting Ben Jonson's alchemical world:
annotated *Alchemist*, biographical timeline, and Russell's findings
on Jonson's Hypnerotomachia annotations. Integrated as a tab in the
HP Marginalia site.

## Architecture

```
../Ben Jonson Life/md/  (5 converted source documents)
    ↓
src/ingest/ingest.py    (catalog sources → data/raw/sources.json)
    ↓
src/extract/excerpt.py  (pull passages → data/processed/excerpts.json)
    ↓
src/extract/classify.py (label excerpts → data/processed/classified.json)
    ↓
src/transform/life.py          → data/exports/life_events.json
src/transform/annotations.py   → data/exports/annotations.json
src/transform/russell.py       → data/exports/russell_findings.json
    ↓
src/site/build_jonson.py       → site/jonson/*.html
```

## Storage

JSON files at every stage. No database for seed phase.
Each JSON file is an array of typed records with stable IDs.

## Provenance

Every record carries:
- `source_id`: which source document
- `source_page`: page/slide number in original
- `extraction_method`: MANUAL | DETERMINISTIC | LLM_ASSISTED
- `confidence`: HIGH | MEDIUM | LOW

Rule: no record without a citation. No citation without a source_id.

## Integration

Pages deploy to `site/jonson/`. The HP nav bar gets a "Ben Jonson" tab
linking to `jonson/index.html`. Jonson pages use the same CSS variables
and header/nav structure as the parent site.

## Constraints

1. Alchemist annotations are about alchemy only
2. Life section is about Jonson only
3. Russell showcase is about Jonson's annotations only
4. Digby appears only as context, never as primary subject
5. No speculative modules or knowledge graphs
