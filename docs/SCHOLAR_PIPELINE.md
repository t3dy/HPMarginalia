# Scholar Pipeline: Step-by-Step

> Execute these steps in order. Each step has defined inputs, outputs, and validation gates.
> Read SCHOLAR_SPEC.md first for the full data model.

## Prerequisites

- `db/hp.db` with scholars (60 rows), bibliography (109 rows) tables
- `scholars/summaries.json` (34 entries, 30 unique authors)
- Dictionary enrichment pipeline complete (for cross-linking)

## Step 1: Link Scholars to Bibliography

**Script:** `scripts/link_scholars.py` (to be created)
**Mode:** Deterministic

```
python scripts/link_scholars.py
```

**What it does:**
1. Adds `scholar_overview`, `is_historical_subject` columns to scholars table
2. Adds `in_archive` column to bibliography table
3. Creates `scholar_works` junction table
4. Matches summaries.json → bibliography by author+title
5. Matches bibliography → scholars by author name
6. Checks local PDF/md files to set `in_archive` flags
7. Tags historical figures (Colonna, Manutius, Jonson, Chigi, Giovio, Martin, Beroalde)

**Outputs:**
- `scholar_works` table populated
- `staging/scholar/unmatched.json` listing any failures
- Console report of match rates

**Validation gate:**
- ≥80% of summaries.json entries matched to bibliography
- ≥70% of bibliography entries linked to a scholar
- All 8 historical figures tagged

## Step 2: Generate Scholar Overviews

**Script:** `scripts/generate_scholar_overviews.py` (to be created)
**Mode:** LLM-assisted (DRAFT provenance)

```
python scripts/generate_scholar_overviews.py
```

**What it does:**
1. For each modern scholar with 1+ works: generates 2-3 paragraph overview
2. For historical subjects: generates 1-paragraph role description
3. Uses summaries.json content + corpus search for grounding
4. Stores in `scholars.scholar_overview`
5. Sets `source_method='LLM_ASSISTED'`, `review_status='DRAFT'`

**Outputs:**
- `scholars.scholar_overview` populated for all scholars with linked works
- `staging/scholar/overviews.json` with all generated text + provenance

**Validation gate:**
- No overview exceeds 400 words
- All overviews have source_method set
- No VERIFIED content overwritten
- staging/scholar/overviews.json exists and is valid JSON

## Step 3: Rebuild Scholar Pages

**Script:** Already in `build_site.py` → `build_scholars_pages()` (to be updated)
**Mode:** Deterministic

```
python scripts/build_site.py
```

**What changes in build_scholars_pages():**
1. Query scholars with linked works from scholar_works
2. Scholar cards show overview preview (300 chars + "Read more")
3. Detail pages show full overview + "Works in Archive" + "Other Known Works"
4. Historical figures get "Historical Figure" badge
5. Cross-links to dictionary terms where relevant

**Validation gate:**
- All scholar pages have nav
- Cards link to correct detail pages
- Works sections correctly split archive vs non-archive
- Historical figures use different badge

## Execution Checklist

```
[ ] Run link_scholars.py
[ ] Review staging/scholar/unmatched.json
[ ] Fix any critical mismatches manually
[ ] Run generate_scholar_overviews.py
[ ] Review staging/scholar/overviews.json (spot-check 5+ entries)
[ ] Update build_scholars_pages() in build_site.py
[ ] Run build_site.py
[ ] Validate: nav, paths, page count
[ ] Deploy
```

## File Inventory

After completing this pipeline, the following files should exist:

```
scripts/link_scholars.py          # Step 1: deterministic linking
scripts/generate_scholar_overviews.py  # Step 2: LLM-assisted overviews
staging/scholar/unmatched.json    # Unmatched entries log
staging/scholar/overviews.json    # Generated overviews with provenance
docs/SCHOLAR_SPEC.md              # Data model and template spec
docs/SCHOLAR_PIPELINE.md          # This file
```
