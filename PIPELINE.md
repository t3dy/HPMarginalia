# PIPELINE: How Data Flows from Source to Site

> No abstraction. No speculation. Just the actual scripts and their order.

## End-to-End Pipeline

```
STAGE 1: INGEST
  init_db.py              → Creates schema (24 tables incl. image_readings)
  catalog_images.py       → Parses 674 image filenames → images table (with master_path + web_path)
  build_signature_map.py  → 1499 collation formula → 448 signature_map entries

STAGE 2: EXTRACT
  pdf_to_markdown.py      → 37 PDFs → 37 markdown files in md/
  chunk_documents.py       → 37 markdowns → ~200 chunks in chunks/
  extract_references.py    → Russell thesis → 282 dissertation_refs

STAGE 3: MATCH
  match_refs_to_images.py  → Joins refs + images via signature_map → matches
  fix_bl_offset.py         → Corrects BL folio numbers (offset=13)
  build_bl_ground_truth.py → Verified folio mapping from image reading
  rebuild_bl_matches.py    → Rebuilds BL matches with correct data → 39 BL matches

STAGE 4: ENRICH
  add_hands.py             → 11 annotator hand profiles
  add_bibliography.py      → 109 bibliography + 60 scholars + timeline events
  consolidate_annotations.py → Migrates dissertation_refs → annotations (282)
  classify_annotations.py  → Assigns 6 annotation types
  seed_dictionary.py       → 37 base terms
  seed_dictionary_v2.py    → 43 HP entity terms
  seed_dictionary_v3.py    → 14 additional terms
  migrate_dictionary_v2.py → Extends schema with significance columns
  build_reading_packets.py → 94 evidence packets from corpus
  enrich_dictionary.py     → Populates source docs, quotes, refs
  generate_dictionary_significance.py → significance_to_hp/scholarship for 80 terms
  generate_significance_v3.py → significance for 14 more terms
  link_scholars.py         → scholar_works junction, historical figure tagging
  generate_scholar_overviews.py → 38 scholar overviews
  generate_remaining_overviews.py → 21 more overviews
  migrate_marginalia.py    → alchemical_symbols + symbol_occurrences tables
  extract_alchemical_data.py → 26 symbol occurrences from thesis evidence
  add_alchemist_descriptions.py → 13 folio descriptions
  seed_timeline_v2.py      → 29 new timeline events
  seed_copies.py           → 6 hp_copies entries
  seed_woodcuts.py         → 18 woodcut entries

STAGE 4.5: IMAGE READING INFRASTRUCTURE
  migrate_v3_image_reading.py → Schema v3: image_readings table + expanded CHECKs
  image_utils.py              → Shared path validation (master vs web enforcement)
  backfill_previous_readings.py → 30 historical readings into image_readings

STAGE 4.6: VISUAL GROUND TRUTH (Phase 1)
  read_images.py --phase 1    → 189 BL photos read via Claude Code vision
                              → 189 image_readings rows (phase=1)
                              → 189 raw JSON files in staging/image_readings/bl/phase1/
                              → BL offset confirmed at 174/174 points
                              → 60 woodcuts detected

STAGE 5: BUILD
  build_site.py            → Generates all 365 HTML pages + data.json
```

## Script Dependencies

Scripts must run in stage order. Within each stage, order matters:

**Stage 1:** init_db → catalog_images, build_signature_map (parallel OK)
**Stage 2:** pdf_to_markdown → chunk_documents; extract_references (parallel OK)
**Stage 3:** match_refs_to_images → fix_bl_offset → build_bl_ground_truth → rebuild_bl_matches (sequential)
**Stage 4:** All enrichment scripts depend on Stage 1-3 tables existing. Most are idempotent.
**Stage 5:** build_site.py depends on all data being populated.

## Rebuild from Scratch

```bash
python scripts/init_db.py
python scripts/build_signature_map.py
python scripts/catalog_images.py
python scripts/extract_references.py
python scripts/match_refs_to_images.py
python scripts/fix_bl_offset.py
python scripts/build_bl_ground_truth.py
python scripts/rebuild_bl_matches.py
python scripts/add_hands.py
python scripts/add_bibliography.py
python scripts/migrate_v2.py
python scripts/consolidate_annotations.py
python scripts/classify_annotations.py
python scripts/seed_dictionary.py
python scripts/seed_dictionary_v2.py
python scripts/seed_dictionary_v3.py
python scripts/migrate_dictionary_v2.py
python scripts/build_reading_packets.py
python scripts/enrich_dictionary.py
python scripts/generate_dictionary_significance.py
python scripts/generate_significance_v3.py
python scripts/link_scholars.py
python scripts/generate_scholar_overviews.py
python scripts/generate_remaining_overviews.py
python scripts/migrate_timeline.py
python scripts/seed_timeline_v2.py
python scripts/migrate_marginalia.py
python scripts/extract_alchemical_data.py
python scripts/add_alchemist_descriptions.py
python scripts/seed_copies.py
python scripts/seed_woodcuts.py
python scripts/migrate_v3_image_reading.py
python scripts/backfill_previous_readings.py
# Phase 1 readings: run read_images.py --ingest with pre-computed results
python scripts/build_site.py
```

## What Each Stage Produces

| Stage | Input | Output | Rows Created |
|-------|-------|--------|-------------|
| Ingest | Image directories, collation formula | images (674), signature_map (448) | 1122 |
| Extract | PDFs | md/ (37 files), chunks/ (~200), dissertation_refs (282) | 282 |
| Match | Refs + images + map | matches (431) | 431 |
| Enrich | All above + corpus | annotations, dictionary, scholars, bibliography, timeline, symbols, woodcuts | ~1000 |
| Image Infra | Schema v3 migration | image_readings table, expanded CHECKs | 30 (backfill) |
| Phase 1 | Master BL images (via Claude Code vision) | 189 image_readings rows, 189 staging JSONs | 189 |
| Build | All tables | 365 HTML pages + data.json | — |
