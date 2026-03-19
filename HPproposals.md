# HPproposals: Improving Content Quality Across the Site

Proposals for how to systematically improve the writing, consistency, and accuracy of the dictionary, bibliography, scholar, and summary pages through templating, structured LLM reading, and editorial workflows.

---

## The Problem

The site currently has four kinds of prose content, all generated differently:

| Content | Count | How Generated | Quality |
|---------|-------|---------------|---------|
| Article summaries | 34 | LLM batch agents reading markdown | Uneven -- some rich and precise (Priki, Russell), some thin (Ure, Pumroy) |
| Dictionary definitions | 37 | LLM writing in a single session | Consistent tone but untested against specialist knowledge |
| Scholar profiles | 30 pages | Template-filled from summaries.json | No biographical prose, just paper lists |
| Bibliography entries | 109 | Hardcoded metadata, no annotation | Author-title-year only, no commentary |

The root issue: each content type was generated in a different session with different prompts, producing different levels of depth and different rhetorical registers. There is no shared style guide, no template structure, and no editorial pass.

---

## Proposal 1: Structured Templates for Each Content Type

### Dictionary Term Template

Every dictionary entry should follow this structure:

```
LABEL (Category)

[1-sentence definition suitable for a tooltip or glossary sidebar]

[2-4 sentence contextual definition situating the term within HP scholarship.
Must answer: What is it? Why does it matter for the HP specifically?
What scholarly debate or tradition does it belong to?]

[1-2 sentences on how the term connects to our project's data --
e.g., "Russell documents X instances in the BL copy" or
"The Siena facsimile shows this feature on folios Y-Z."]

Sources: [Specific citations, not vague attributions]
Related: [Linked terms from dictionary_term_links]
```

**Current gap**: Many definitions explain the general concept but don't connect to our specific data. The entry for "marginalia" describes the concept but doesn't say "Russell documented 282 folio references across 6 copies, with 11 distinct hands identified." The template forces this connection.

**Implementation**: Add a `definition_project` TEXT column to `dictionary_terms` for the project-specific paragraph. Generate it by querying the database:

```python
# For each term, query for related data
if term.slug == 'marginalia':
    cur.execute("SELECT COUNT(*) FROM dissertation_refs")
    ref_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM annotators")
    hand_count = cur.fetchone()[0]
    definition_project = f"This project documents {ref_count} folio references..."
```

This keeps the project-specific content deterministic and always current.

### Scholar Profile Template

Currently scholar pages are just lists of papers. Each should have:

```
SCHOLAR NAME

[1-2 sentence biographical context: period, nationality, institution, field]

[1-2 sentences on their HP contribution: what question they addressed,
what they found, why it matters]

Relationship to Other Scholars:
[How their work connects to or responds to other scholars in our database]

Works in Our Collection:
[Paper cards as currently generated]

Works Cited but Not in Collection:
[From bibliography table where in_collection = 0]
```

**Implementation**: The biographical context can be generated from the `scholars` table fields we already have (nationality, institution, specialization, hp_focus). The relationship mapping requires a new query:

```sql
-- Find scholars who cite or are cited by this scholar
SELECT DISTINCT b2.author
FROM bibliography b1
JOIN bibliography b2 ON b2.topic_cluster = b1.topic_cluster
WHERE b1.author = ? AND b2.author != ?
AND b1.year < b2.year
```

This is approximate (same topic + later date suggests engagement) but better than nothing. A proper citation graph would require parsing bibliography sections from the markdown files.

### Article Summary Template

Current summaries vary wildly in structure. Standardize to:

```
TITLE (Author, Year)
Journal/Publisher

[1-sentence thesis statement: what the article argues]

[2-3 sentences on method and evidence: how they make their case]

[1-2 sentences on significance: why this matters for HP scholarship,
what it changes or challenges]

[1 sentence on relationship to our project: which folios, hands,
or copies are relevant]

Topic: [cluster tags]
```

**Current gap**: Some summaries are 200+ words of flowing prose, others are 50 words. The template doesn't restrict length but enforces structure. The "relationship to our project" line is the key addition -- it transforms a generic summary into a pointer into our data.

### Bibliography Entry Template

Currently bare metadata. Add structured annotations:

```
AUTHOR (Year). TITLE. Journal/Publisher. [pub_type]

[1-sentence annotation: what this work contributes to HP scholarship]

Status: In Collection / Cited by Russell / Discovered via Web Search
Verified: Yes (CrossRef DOI) / No (needs verification)
Topics: [badges]
```

**Implementation**: The 1-sentence annotation is the only part that requires LLM generation. Everything else is already in the database. The annotation could be derived from the `notes` field (which already contains brief descriptions for many entries) or generated in a batch pass.

---

## Proposal 2: LLM Reading Pipeline for Quality Improvement

### Phase 1: Audit Existing Summaries Against Source Text

For each article where we have the markdown source:

1. **Load the summary** from `summaries.json`
2. **Load the source markdown** from `md/`
3. **Prompt the LLM** with both:

```
You are reviewing an article summary for accuracy and completeness.

SOURCE ARTICLE (first 3000 words):
{source_text}

EXISTING SUMMARY:
{summary}

Check for:
1. FACTUAL ERRORS: Does the summary misstate the article's argument?
2. MISSING KEY CLAIMS: Does the article make a major argument the summary omits?
3. ATTRIBUTION: Does the summary correctly identify the author's position vs. others'?
4. SPECIFICITY: Does the summary use vague language where the article gives specifics?

Output a JSON object:
{
  "factual_errors": [...],
  "missing_claims": [...],
  "attribution_issues": [...],
  "specificity_gaps": [...],
  "revised_summary": "...",
  "confidence": "HIGH/MEDIUM/LOW"
}
```

4. **If confidence is HIGH** and no errors found, mark the summary as `reviewed`
5. **If errors found**, flag for human review with the specific issues listed

**Key principle**: The LLM reads the source article and checks the summary against it. This is a verification task (probabilistic but grounded), not a generation task (probabilistic and ungrounded). The source text anchors the LLM's judgment.

### Phase 2: Generate Missing Content from Source Text

For articles where we have the markdown but no summary yet (or a thin summary):

1. **Chunk the article** using existing `chunk_documents.py`
2. **Prompt the LLM** with each chunk + the template structure:

```
You are writing a structured summary of an HP scholarship article.
Follow this template exactly:

THESIS: [1 sentence]
METHOD: [2-3 sentences]
SIGNIFICANCE: [1-2 sentences]
PROJECT RELEVANCE: [1 sentence connecting to folio refs, hands, or copies]

Article chunk {n}/{total}:
{chunk_text}
```

3. **Merge chunk-level outputs** into a single summary
4. **Tag** with `source_method = 'LLM_ASSISTED'`, `needs_review = 1`

### Phase 3: Cross-Reference Enhancement

After individual summaries are solid, run a cross-referencing pass:

```
Given these two summaries of HP scholarship, identify:
1. Do they address the same question? (authorship, reception, architecture, etc.)
2. Do they agree or disagree?
3. Does one cite or respond to the other?
4. What folio references do they share?

Article A: {summary_a}
Article B: {summary_b}
```

This produces the "relationship to other scholars" data needed for enhanced scholar profiles.

---

## Proposal 3: Deterministic Quality Checks

Not everything needs an LLM. These checks should be scripted:

### Bibliography Consistency Checks (Pure Python)

```python
# 1. Author name normalization
# "L. E. Semler" and "L.E. Semler" should match
normalize_author(name):
    return re.sub(r'\.(\s)', '.', name).strip()

# 2. Year range validation
# No HP scholarship before 1499, no entries from the future
assert 1499 <= year <= 2026

# 3. Journal name normalization
# "Word & Image" vs "Word and Image" vs "Word & Image 14:1-2"
# Normalize to base journal name + volume/issue

# 4. Duplicate detection
# Fuzzy match on normalized(author) + normalized(title)
# Flag pairs with >85% similarity

# 5. Citation format validation
# Every entry should have: author, title, year, pub_type
# Flag entries missing any required field
```

### Dictionary Consistency Checks

```python
# 1. Every term should have both definition_short and definition_long
# 2. definition_short should be < 200 characters
# 3. Every term should have at least 1 related term link
# 4. No orphan terms (linked to but not existing)
# 5. source_basis should cite at least one specific work
# 6. Category distribution should be roughly even (flag if >50% in one category)
```

### Summary Quality Metrics

```python
# 1. Word count: flag summaries < 80 words or > 400 words
# 2. Specificity: count proper nouns, dates, folio references
#    (summaries with 0 specific references are too vague)
# 3. Template adherence: check for thesis/method/significance structure
# 4. Unique vocabulary: flag summaries that share >60% of their
#    non-stopword vocabulary with another summary (possible duplication)
```

---

## Proposal 4: Editorial Workflow

### Review States

```
DRAFT → LLM_REVIEWED → HUMAN_REVIEWED → VERIFIED
```

- **DRAFT**: Initial LLM generation. Displayed with yellow "Unreviewed" badge.
- **LLM_REVIEWED**: Passed the Phase 1 audit (LLM checked summary against source). Badge changes to "LLM-checked."
- **HUMAN_REVIEWED**: A human has read and approved the content. Badge changes to "Reviewed."
- **VERIFIED**: Content has been cross-checked against authoritative sources (VIAF for scholars, CrossRef for citations, specialist review for definitions). Badge removed entirely — verified content needs no badge.

### Display Strategy

- **DRAFT content**: Shown with prominent yellow badge. Tooltip: "This content was generated with AI assistance and has not been verified."
- **LLM_REVIEWED content**: Shown with subtle blue badge. Tooltip: "This content was checked against the source text by AI but has not been human-reviewed."
- **HUMAN_REVIEWED content**: Shown with green checkmark. No tooltip needed.
- **VERIFIED content**: No badge. Clean display.

This gives the site graduated credibility signals rather than the current binary (everything is "Unreviewed").

---

## Proposal 5: Template-Driven Page Generation

### Current Approach (build_site.py)

Pages are generated with inline Python f-strings:

```python
detail_body = f"""
<div class="scholar-detail">
    <h2>{escape(author)} {review_html}</h2>
    ...
"""
```

This works but makes it hard to iterate on the design without touching Python code.

### Proposed Approach: Lightweight Templates

Use Python's built-in `string.Template` or a minimal template library (Jinja2 is overkill; `chevron` for Mustache is 1 file, no dependencies):

```
templates/
  scholar.html        # Scholar profile page template
  scholar_card.html   # Scholar card for index page
  dictionary.html     # Dictionary term page
  dictionary_card.html
  bibliography.html   # Bibliography page
  bib_entry.html      # Individual entry
  marginalia.html     # Folio detail page
  nav.html            # Shared navigation
  footer.html         # Shared footer
  badges.html         # Review/confidence badge partials
```

**Benefits**:
- Designers can edit HTML without touching Python
- Templates can be previewed in a browser with placeholder data
- Consistent structure across page types
- Easier to add new page types (e.g., timeline, digital edition)

**Constraint**: Templates remain static files. No template engine runs at request time. The Python build script reads templates, fills them with data, and writes static HTML. The architecture stays static.

### Implementation Path

1. Extract current f-string templates into `.html` files with `{{variable}}` placeholders
2. Write a `render_template(template_path, context)` function that reads the file and substitutes
3. Update `build_site.py` to use `render_template` instead of inline f-strings
4. Keep the current f-string approach as a fallback for complex logic (e.g., conditional badge display)

---

## Proposal 6: Batch LLM Improvement Runs

### Dictionary Enrichment Run

For each of the 37 dictionary terms, prompt the LLM with:

```
You are enriching a dictionary entry for a digital humanities project
on the Hypnerotomachia Poliphili.

Current entry:
  Term: {label}
  Category: {category}
  Short definition: {definition_short}
  Long definition: {definition_long}
  Sources: {source_basis}

Database context:
  - {n_refs} folio references mention this concept
  - Related annotator hands: {hands}
  - Related folios: {folios}

Tasks:
1. Add a "Project data" paragraph connecting this term to specific
   folios, hands, or images in our database
2. Suggest 1-2 additional related terms we should add to the dictionary
3. Rate the current definition: GOOD / NEEDS_REVISION / NEEDS_SPECIALIST
4. If NEEDS_REVISION, provide a revised definition
```

Run this as a foreground agent batch (7-10 terms per agent, 4 agents in parallel). Each agent reads only dictionary + DB context, no web access needed.

### Summary Improvement Run

For each of the 34 summaries where we have the source markdown:

```
Read the source article and the existing summary.
Rewrite the summary following the template:
  THESIS: [1 sentence]
  METHOD: [2-3 sentences]
  SIGNIFICANCE: [1-2 sentences]
  PROJECT RELEVANCE: [1 sentence]
Keep the total under 200 words.
Do not invent claims not in the source.
```

This standardizes length and structure across all summaries.

---

## Priority Order

| Priority | Proposal | Effort | Impact |
|----------|----------|--------|--------|
| 1 | Deterministic quality checks (Proposal 3) | Low | Catches errors immediately |
| 2 | Structured templates for content types (Proposal 1) | Low | Enforces consistency going forward |
| 3 | LLM audit of existing summaries (Proposal 2, Phase 1) | Medium | Catches factual errors in published content |
| 4 | Editorial workflow with graduated badges (Proposal 4) | Medium | Builds user trust |
| 5 | Template-driven page generation (Proposal 5) | Medium | Enables design iteration |
| 6 | Batch LLM improvement runs (Proposal 6) | Medium | Raises overall quality |
| 7 | Cross-reference enhancement (Proposal 2, Phase 3) | High | Adds scholarly relationship data |
