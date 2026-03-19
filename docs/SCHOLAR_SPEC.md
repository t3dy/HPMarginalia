# Scholar Infrastructure Specification

> This spec defines the data model, page templates, and pipeline for improved scholar pages.
> Future sessions should read this file, not re-derive the requirements from prompts.

## Goal

Transform scholar pages from paper-list views into rich scholarly profiles with:
- Per-scholar overview prose (2-3 paragraphs)
- Individual article/book summaries for works in the archive
- Bibliography entries for works NOT in the archive
- Cross-links to dictionary terms, essays, and bibliography

## Data Model

### New Table: `scholar_works`

Links scholars to bibliography entries. Many-to-many junction.

```sql
CREATE TABLE IF NOT EXISTS scholar_works (
    id INTEGER PRIMARY KEY,
    scholar_id INTEGER REFERENCES scholars(id),
    bib_id INTEGER REFERENCES bibliography(id),
    has_summary BOOLEAN DEFAULT 0,
    summary_source TEXT,  -- 'summaries.json' | 'corpus_extraction' | NULL
    UNIQUE(scholar_id, bib_id)
);
```

### New Column: `scholars.scholar_overview`

```sql
ALTER TABLE scholars ADD COLUMN scholar_overview TEXT;
ALTER TABLE scholars ADD COLUMN is_historical_subject BOOLEAN DEFAULT 0;
```

- `scholar_overview`: 2-3 paragraph overview of the scholar's HP-related work
- `is_historical_subject`: True for Colonna, Manutius, Jonson, Chigi, Giovio, etc.

### New Column: `bibliography.in_archive`

```sql
ALTER TABLE bibliography ADD COLUMN in_archive BOOLEAN DEFAULT 0;
```

Set to 1 for any bibliography entry that has a corresponding local PDF/markdown file.

## Name Matching Rules

Scholars, bibliography, and summaries.json use string author names with no foreign keys.
Matching rules:

1. Case-insensitive comparison
2. Strip trailing/leading whitespace
3. Normalize periods and spaces: "L.E. Semler" == "L. E. Semler"
4. Strip accents for comparison but preserve in display
5. If ambiguous, log to `staging/scholar/unmatched.json` rather than guessing

## Historical Figure vs Modern Scholar

Historical figures are HP subjects, not modern researchers. They get different treatment:

**Historical figures** (is_historical_subject = True):
- Francesco Colonna, Aldus Manutius, Ben Jonson, Fabio Chigi (Alexander VII),
  Benedetto Giovio, Paolo Giovio, Jean Martin, Beroalde de Verville
- Card shows: name, 1-paragraph role description, "Historical Figure" badge
- Detail page: role description, links to relevant folios/annotations

**Modern scholars** (is_historical_subject = False):
- All others in the scholars table
- Card shows: name, overview paragraph (first ~300 chars), work count, topic badges
- Detail page: full overview, works in archive (with summaries), other known works

## Scholar Card Template (scholars.html)

```
<div class="scholar-card">
    <h3><a href="scholar/{slug}.html">{name}</a> {review_badge} {historical_badge?}</h3>
    <div class="scholar-meta">{work_count} works | {topic_badges}</div>
    <div class="scholar-overview-preview">
        {first 300 chars of scholar_overview}...
        <a href="scholar/{slug}.html">Read more</a>
    </div>
</div>
```

## Scholar Detail Page Template (scholar/{slug}.html)

```
<div class="scholar-detail">
    <a href="../scholars.html">← All Scholars</a>
    <h2>{name} {review_badge}</h2>
    <div class="scholar-overview">{full scholar_overview}</div>

    <h3>Works in Archive</h3>
    <!-- For each linked bib entry with has_summary = True -->
    <div class="work-entry">
        <h4>{title}</h4>
        <div class="work-meta">{journal} ({year}) [{pub_type}]</div>
        <div class="work-summary">{full summary from summaries.json}</div>
    </div>

    <h3>Other Known Works</h3>
    <!-- For each linked bib entry with has_summary = False -->
    <div class="work-entry">
        <h4>{title}</h4>
        <div class="work-meta">{journal} ({year}) [{pub_type}]</div>
        <p class="no-summary">Summary not yet available.</p>
    </div>

    <div class="cross-links">
        <h4>Related Pages</h4>
        <!-- Links to dictionary terms, essays, etc. -->
    </div>

    <div class="provenance-section">
        <h4>Review Status / Provenance</h4>
        {review_status_badge} | Source: {source_method}
    </div>
</div>
```

## Pipeline

### Step 1: `scripts/link_scholars.py`

**Inputs:** scholars table, bibliography table, summaries.json, local PDF/md files
**Outputs:** populated scholar_works table, in_archive flags, is_historical_subject flags
**Reasoning mode:** deterministic (name matching, file existence checks)

1. Add new columns (scholar_overview, is_historical_subject, in_archive) if not exist
2. Mark historical figures by matching against known list
3. Match summaries.json entries to bibliography rows by author + title
4. Match bibliography authors to scholars by name
5. Check which bibliography entries have local PDFs/markdown
6. Populate scholar_works junction table
7. Log unmatched entries to staging/scholar/unmatched.json

### Step 2: `scripts/generate_scholar_overviews.py`

**Inputs:** scholar_works data, summaries.json, corpus chunks
**Outputs:** scholars.scholar_overview populated, staging/scholar/overviews.json
**Reasoning mode:** generative (LLM-assisted, DRAFT provenance)

1. For each modern scholar with 1+ linked works:
   - Compile bibliography entries and any summaries
   - Search corpus for additional context about the scholar
   - Generate 2-3 paragraph overview (max 400 words)
   - Store in scholars.scholar_overview with source_method='LLM_ASSISTED', review_status='DRAFT'
2. For historical subjects: generate 1-paragraph role description
3. Write all generated text to staging/scholar/overviews.json for review

### Step 3: Update `build_scholars_pages()` in `build_site.py`

**Inputs:** scholars table (with overviews), scholar_works, bibliography, summaries.json
**Outputs:** rebuilt scholars.html + scholar/*.html
**Reasoning mode:** deterministic (HTML template generation)

1. Query scholars with their linked works
2. Generate cards with overview preview
3. Generate detail pages with full overview + work sections
4. Add cross-links to dictionary terms where relevant

## Validation Gates

- Every summaries.json entry matched to a bibliography row OR logged as unmatched
- Every bibliography entry linked to a scholar OR logged as unmatched
- No scholar_overview exceeds 400 words
- All generated overviews carry source_method = 'LLM_ASSISTED' and review_status = 'DRAFT'
- No VERIFIED content overwritten
- Historical figures tagged correctly (check against known list)
- All scholar pages include nav, CSS links, back-navigation

## Provenance Model

| Data | source_method | review_status |
|------|--------------|---------------|
| Scholar name, institution | DETERMINISTIC | from existing DB |
| scholar_works links | DETERMINISTIC | from name matching |
| in_archive flag | DETERMINISTIC | from file existence |
| is_historical_subject | DETERMINISTIC | from known list |
| scholar_overview (modern) | LLM_ASSISTED | DRAFT |
| scholar_overview (historical) | LLM_ASSISTED | DRAFT |
| Paper summaries (from summaries.json) | LLM_ASSISTED | DRAFT |
