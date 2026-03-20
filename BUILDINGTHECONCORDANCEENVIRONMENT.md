# BUILDINGTHECONCORDANCEENVIRONMENT: How to Set Up and Run the Concordance System

> Notes on the infrastructure, tools, and methods that make the concordance work.
> Written for a future collaborator (or a future Claude session) who needs to
> understand not just what the concordance does but how the environment is built.

---

## What the Concordance Is

The concordance is a system for connecting three things:
1. **Russell's scholarly claims** about specific marginalia (282 references)
2. **Manuscript photographs** (674 images across 2 copies)
3. **A deterministic mapping** between signature notation (b6v) and folio numbers

When a scholar reads Russell saying "On b6v, the alchemist writes 'Magisteri
Mercurii,'" the concordance lets them see the actual photograph of that page,
verify the annotation is there, and navigate to related pages.

---

## The Environment

### Database

SQLite at `db/hp.db`. No server, no Docker, no credentials. The file IS the database.

```
python -c "import sqlite3; conn = sqlite3.connect('db/hp.db'); print('OK')"
```

If that works, you have everything you need for the data layer.

### Python Dependencies

The project uses only standard library modules:
- `sqlite3` (database)
- `json` (data exchange)
- `re` (regex for reference extraction)
- `pathlib` (file system)
- `html` (escaping for page generation)

No pip installs. No virtual environment. No requirements.txt.
The one external dependency is PyMuPDF (`fitz`) for PDF-to-markdown
extraction, but this is only needed if re-extracting from PDFs.

### Image Reading

Claude reads JPEG manuscript photographs directly using its native
multimodal capability. No OCR library, no image processing pipeline.
The Read tool opens a JPEG and Claude describes what it sees.

This works because:
- The page numbers are large and clearly printed
- Woodcuts are visually distinctive
- Annotation presence is detectable even without reading the text
- The photographs are adequate resolution for page-level analysis

This does NOT work for:
- Transcribing small handwriting
- Distinguishing ink colors (photos are near-grayscale)
- Reading alchemical ideograms (too small)
- Determining recto vs verso from visual features alone

### File System

```
db/hp.db                    The database
scripts/                    All Python pipeline scripts
  build_site.py             Master builder (generates all HTML)
  corpus_search.py          Search across /chunks/ and /md/
  build_bl_ground_truth.py  BL photo-to-folio mapping
  rebuild_bl_matches.py     Rebuild BL matches with correct data
site/                       Generated static HTML (deployed to GitHub Pages)
staging/                    Intermediate artifacts with provenance
  packets/                  94 reading packets for dictionary terms
  scholar/                  Scholar overviews and unmatched log
  bl_ground_truth.json      Verified BL page numbers and observations
md/                         Extracted markdown from PDFs
chunks/                     Semantic chunks for corpus search
docs/                       Specification files (WRITING_TEMPLATES, etc.)
```

### The Manuscript Photos

```
3 BL C.60.o.12 Photos-.../3 BL C.60.o.12 Photos/
  C_60_o_12-001.jpg through C_60_o_12-189.jpg
  BL 2.1.jpg, BL HP 12.jpg, etc. (detail photos)

Siena O.III.38 Digital Facsimile-.../Siena O.III.38 Digital Facsimile/
  O.III.38_0001r.jpg through O.III.38_0240v.jpg (approx)
```

The BL photos are sequentially numbered. Photos 001-013 are front matter.
Photo 014 = page 1 = a1r. Formula: `folio = photo - 13`.

The Siena photos encode folio+side in filenames: `O.III.38_0014r.jpg` =
folio 14 recto.

---

## How to Rebuild the Concordance from Scratch

If the database were lost, here's the full rebuild sequence:

```bash
# Step 1: Initialize schema
python scripts/init_db.py

# Step 2: Build the signature map (deterministic)
python scripts/build_signature_map.py

# Step 3: Catalog manuscript images
python scripts/catalog_images.py

# Step 4: Extract references from Russell's thesis
python scripts/extract_references.py

# Step 5: Match references to images
python scripts/match_refs_to_images.py

# Step 6: Fix BL photo-to-folio offset
python scripts/fix_bl_offset.py
python scripts/build_bl_ground_truth.py
python scripts/rebuild_bl_matches.py

# Step 7: Add annotator hand profiles
python scripts/add_hands.py

# Step 8: Consolidate into annotations table
python scripts/consolidate_annotations.py

# Step 9: Classify annotation types
python scripts/classify_annotations.py

# Step 10: Add bibliography, scholars, dictionary
python scripts/add_bibliography.py
python scripts/seed_dictionary.py
python scripts/seed_dictionary_v2.py
python scripts/seed_dictionary_v3.py

# Step 11: Schema migrations
python scripts/migrate_v2.py
python scripts/migrate_dictionary_v2.py
python scripts/migrate_timeline.py
python scripts/migrate_marginalia.py

# Step 12: Enrichment
python scripts/build_reading_packets.py
python scripts/enrich_dictionary.py
python scripts/generate_dictionary_significance.py
python scripts/generate_significance_v3.py
python scripts/link_scholars.py
python scripts/generate_scholar_overviews.py
python scripts/generate_remaining_overviews.py
python scripts/seed_timeline_v2.py
python scripts/seed_copies.py
python scripts/extract_alchemical_data.py

# Step 13: Generate the site
python scripts/build_site.py
```

Most of these scripts are idempotent (safe to re-run).

---

## Key Decisions That Shaped the Environment

### Why SQLite, Not PostgreSQL
The database is 1 MB. It has 22 tables with ~3000 total rows.
PostgreSQL would add deployment complexity for zero benefit.
SQLite works on every machine with Python installed. The file
can be committed to git. There is no concurrent write pressure.

### Why Static HTML, Not a Web Framework
The site has 335 pages. They change when the data changes, not
when users visit. A static site generator produces files that
GitHub Pages serves for free. No server to maintain. No uptime
to worry about. The MIT Electronic Hypnerotomachia (1997) is
still online after 29 years because it's static HTML. That's
the durability model.

### Why Offset Correction, Not OCR
When the BL photo-to-folio mapping was wrong, the fix was to
read 27 photographs by eye and count. This took 30 minutes.
Setting up an OCR pipeline would have taken longer and produced
noisier results. The page numbers are large, consistent, and
in a known position. Human (or LLM) visual inspection is the
right tool for this specific problem.

### Why Provenance Columns on Everything
Every table with generated content has source_method, review_status,
confidence, and needs_review columns. This was not in the original
design (V1 had none of these). The V2 migration added them after
the project learned that mixing verified and unverified data without
labels creates a trust problem that compounds over time.

### Why Three Redundant Tables Still Exist
dissertation_refs, doc_folio_refs, and annotators duplicate data
in annotations and annotator_hands respectively. They're kept
because: (1) some scripts still reference them, (2) they contain
the original extracted data before normalization, (3) deleting
tables is irreversible and risks breaking unknown dependencies.
The solution is documentation (HPONTOLOGY.md marks them deprecated)
rather than deletion.

---

## How Image Reading Works in Practice

### The Process
1. Use the Read tool to open a JPEG file
2. Claude sees the image and describes what's visible
3. Extract: page number, woodcut presence, annotation density, signature marks
4. Record findings in a structured format (JSON)

### What Makes It Reliable
- **Page numbers** are printed in a consistent position (top corner) in a
  consistent typeface. They are almost always readable.
- **Woodcuts** are visually distinctive blocks of illustration within the
  text flow. False negatives are unlikely; false positives (confusing
  decorated initials with woodcuts) are possible but rare.
- **Annotation presence** is detectable as dark marks in the margins that
  differ from the regular printed text. Density estimation (HEAVY/MODERATE/
  LIGHT) is subjective but consistently applied.

### What Makes It Unreliable
- **Handwriting transcription** requires reading 17th-century secretary
  hand at low resolution. Error rate is high.
- **Ink color** is not reliably distinguishable in these photographs.
  Russell uses ink color as a primary hand-discrimination criterion,
  which makes automated hand identification difficult.
- **Alchemical symbols** are typically 2-3mm in the original, rendered
  as a few pixels in the photograph. They are detectable as "marks" but
  not identifiable as specific symbols.

### The Offset Discovery
The most important finding from image reading was that photo 001 is NOT
page 1. It's a blank endpaper. The HP text starts at photo 014. This
13-photo offset invalidated every BL match in the database. The fix
was trivial (subtract 13) but the discovery required actually looking
at the images — no amount of schema design or script engineering would
have caught this error.

**Lesson:** The concordance is ultimately about physical artifacts.
No amount of metadata engineering substitutes for looking at the actual
evidence.

---

## Environment Checklist for Future Sessions

```
[ ] Can you access db/hp.db? (python -c "import sqlite3; ...")
[ ] Can you read images? (Read tool on a JPEG path)
[ ] Do you know the BL offset? (=13, photo 014 = page 1)
[ ] Have you read CLAUDE.md? (project instructions)
[ ] Have you read docs/WRITING_TEMPLATES.md? (prose style)
[ ] Have you read HPONTOLOGY.md? (actual 22-table schema)
[ ] Have you read CONCORDANCESTATUS.md? (concordance state)
[ ] Do you know which tables are canonical?
    - annotations (not dissertation_refs or doc_folio_refs)
    - annotator_hands (not annotators)
    - hp_copies (not manuscripts, for copy-level data)
```

If you can check all of these, you have a complete concordance
development environment. No installs. No configuration. No API keys.
Just a SQLite file, some Python scripts, and the ability to look
at old photographs.
