# Writing Templates for the HP Platform

> This specification governs all generated prose on the site. Every script that produces text
> should read this file and follow the relevant template. Future sessions read this, not prompts.

---

## Global Style Rules

These rules apply to every written asset on the site regardless of page type.

**Voice:** Active, third-person scholarly. "The HP presents" not "we see" or "I argue."
**Tense:** Present tense for descriptions and current state. Past tense for historical events and what scholars argued. "Russell documents" (present: his thesis still documents). "Bernini completed the sculpture in 1667" (past: historical event).
**Person:** Third person throughout. "The project" or "this site" — never "we" or "I."
**Formality:** High scholarly but not jargon-heavy. Clear, direct, specific. No hedging unless the hedge carries information ("provisionally identified" is informative; "it might perhaps be" is not).
**Terminology:**
- "HP" after first use of italicized *Hypnerotomachia Poliphili* on each page
- "folio" not "page" for manuscript references
- "term" not "entry" or "word" for dictionary items
- "scholar" not "researcher" or "academic"
- "BL copy" after first use of "British Library C.60.o.12"
- "Buffalo copy" after first use of "Buffalo Rare Book Room"
**Capitalization:** Proper nouns capitalized. Technical terms lowercase unless proper (signature, quire, folio, recto, verso). Category names capitalized when used as labels.
**Citation:** Inline parenthetical: (Russell 2014, p. 159). No footnotes.
**Provenance markers:** Always present tense. "This entry is marked DRAFT" not "was marked."
**Prohibited patterns:**
- No emoji
- No rhetorical questions
- No "importantly" or "notably" as sentence openers
- No "it is worth noting that" — state the thing directly

---

## Template 1: Dictionary Term Page

### 1a. Short Definition (definition_short)
- **Length:** 15–40 words
- **Structure:** One sentence defining the term in the context of early printed books, HP scholarship, or the HP narrative
- **Required:** Must be self-contained — readable without the expanded definition
- **Example:** "A letter-number code printed at the foot of certain pages to guide the binder in assembling the book."

### 1b. Expanded Definition (definition_long)
- **Length:** 80–200 words
- **Structure:** 2–4 sentences expanding the short definition with HP-specific detail, scholarly context, and cross-references to other terms or scholars
- **Required:** At least one specific reference to the HP (a folio, a passage, a woodcut, an annotator)
- **Required:** At least one scholarly citation in parenthetical form
- **Example pattern:** "[General statement]. In the HP, [specific application]. [Scholarly context with citation]. [Connection to another term or theme]."

### 1c. Significance to the HP (significance_to_hp)
- **Length:** 40–80 words
- **Structure:** 2–3 sentences explaining what this term means for understanding the HP specifically — not the field in general
- **Required:** Reference to a specific passage, structure, or feature of the HP
- **Example pattern:** "In the HP, [term] appears as [specific form]. This matters because [consequence for reading/interpreting the book]. [Specific folio or section reference if available]."

### 1d. Significance to Scholarship (significance_to_scholarship)
- **Length:** 40–80 words
- **Structure:** 2–3 sentences explaining how scholars have used, debated, or reframed this concept in HP studies
- **Required:** At least one scholar name and citation
- **Example pattern:** "[Scholar] ([year]) [verb: argued/demonstrated/reframed] [claim about this term]. This [supported/complicated/extended] earlier work by [other scholar]. The concept remains [current status in the field]."

### 1e. Key Passages / Evidence (source_quotes_short)
- **Length:** 1–3 short quotes, each under 200 characters
- **Structure:** Quote text followed by bracketed source: "[Russell 2014]"
- **Required:** Must be retrieved from corpus, not invented
- **Provenance:** source_method = CORPUS_EXTRACTION

---

## Template 2: Scholar Card (scholars.html index)

### 2a. Card Overview Preview
- **Length:** 200–300 characters (hard truncation with "... Read more")
- **Source:** First ~300 chars of scholar_overview field
- **Required:** Scholar name as clickable link, work count, topic badges, review badge
- **Layout:** Name/badge row, meta row (work count + topics), overview preview paragraph

---

## Template 3: Scholar Detail Page (scholar/*.html)

### 3a. Scholar Overview
- **Length:** 150–400 words (2–3 paragraphs)
- **Structure:**
  - Para 1: Who the scholar is and their primary contribution to HP studies
  - Para 2: Key arguments, methods, or findings
  - Para 3 (optional): Relationship to broader HP scholarly conversation
- **Required:** Cite at least one specific work by the scholar
- **Provenance:** source_method = LLM_ASSISTED, review_status = DRAFT

### 3b. Historical Figure Description (for is_historical_subject = True)
- **Length:** 60–120 words (1 paragraph)
- **Structure:** "[Name] ([dates/role]) [relationship to the HP]. [Specific contribution or annotation activity]. [Connection to other figures or copies]."
- **Badge:** "Historical Figure" not "Scholar"

### 3c. Per-Work Summary
- **Length:** 80–200 words
- **Structure:** "[Summary of the work's argument and contribution]. [How it relates to HP scholarship]. [Key finding or thesis]."
- **Source:** summaries.json where available; otherwise "Summary not yet available."
- **Provenance:** source_method inherited from summaries.json (LLM_ASSISTED)

---

## Template 4: Bibliography Entry

### 4a. Bibliography Annotation (when available)
- **Length:** 40–100 words
- **Structure:** One-paragraph summary of the work's relevance to HP studies
- **Required:** State whether the work is primarily about the HP or uses it as part of a broader argument
- **Not yet implemented** — future phase

---

## Template 5: Marginalia Folio Page (marginalia/*.html)

### 5a. Folio Orientation Paragraph
- **Length:** 40–80 words
- **Structure:** "This page brings together the evidence currently available for [signature]: [manuscript source], [hand attribution if known], [Russell reference if available], and [linked image if matched]. Confidence and review badges indicate the present status of the linkage."
- **Required:** Mention confidence level explicitly
- **Provenance:** Deterministic (generated from DB data, not LLM prose)

---

## Template 6: Essay Page

### 6a. Essay Evidence Note (opening)
- **Length:** 40–60 words
- **Structure:** States what the essay draws on (DB data, corpus evidence, dissertation) and flags provisional claims
- **Required:** Must appear before the first section heading
- **Example:** "This essay synthesizes evidence from Russell's PhD thesis and data extracted by this project's concordance pipeline. Where claims depend on provisional BL concordance data, this is marked explicitly."

### 6b. Essay Section
- **Length:** 100–300 words per section
- **Structure:** Scholarly prose grounded in retrieved evidence. Each factual claim backed by either a source citation or a [provisional] marker.
- **Required:** Section anchor ID for navigation

### 6c. Provisional Marker
- **Format:** Yellow-left-bordered box: `<div class="provisional">Note: [statement of uncertainty].</div>`
- **Required:** For any claim depending on LOW confidence matches or unverified inference

---

## Template 7: Document Page (docs/*.html)

### 7a. Document Intro
- **Length:** Handled by markdown_to_html() — no template prose needed
- **Context line:** Generated automatically: "{filename} — {word_count:,} words"

---

## Template 8: Code Page (code/*.html)

### 8a. Script Intro
- **Length:** Handled by SCRIPT_METADATA one-liner
- **Context line:** Generated automatically: "{filename} — {line_count} lines"

---

## Template 9: Digital Edition Prospectus

### 9a. Feature Description
- **Length:** 20–40 words per feature
- **Structure:** "[Feature name]: [what it provides]. [Current status indicator]."
- **Status indicators:** `[done]` green, `[partial]` amber, `[planned]` gray, `[blocked]` red

### 9b. Roadmap Phase
- **Length:** 40–80 words
- **Structure:** Phase name, one-sentence purpose, one-sentence current status
- **Required:** Distinguish implemented from planned from blocked

---

## Template 10: Landing Page Intro

### 10a. Section Intro (all landing pages)
- **Length:** 2 paragraphs, 60–100 words total
- **Structure:**
  - Para 1: What this section contains and why it matters for the HP project
  - Para 2: How to use it, what to watch for (review status, provisional content)
- **Source material:** `HPGPTWEBWRITING.txt` contains canonical orientation copy for all sections
- **Required:** Match the voice and specificity of the HPGPTWEBWRITING.txt originals

---

## Provenance Rules for All Templates

| Content Type | source_method | review_status | confidence |
|-------------|--------------|---------------|------------|
| Definition (seeded) | LLM_ASSISTED | DRAFT | MEDIUM |
| Definition (from corpus) | CORPUS_EXTRACTION | DRAFT | MEDIUM |
| Definition (expert-written) | HUMAN_VERIFIED | VERIFIED | HIGH |
| Significance prose | LLM_ASSISTED | DRAFT | MEDIUM |
| Scholar overview | LLM_ASSISTED | DRAFT | MEDIUM |
| Paper summary | LLM_ASSISTED | DRAFT | MEDIUM |
| Folio orientation | DETERMINISTIC | DRAFT | from match data |
| Essay prose | LLM_ASSISTED | DRAFT | varies per claim |
| Landing page intro | LLM_ASSISTED | REVIEWED | HIGH |
| Cross-links | DETERMINISTIC | N/A | N/A |

---

## How to Use This File

1. Before generating any prose, read the relevant template section
2. Check length bounds before and after generation
3. Set source_method and review_status on every generated field
4. Never overwrite fields where review_status = 'VERIFIED'
5. Store generated prose in staging artifacts before promoting to DB
6. Follow the global style rules for voice, tense, person, and terminology
