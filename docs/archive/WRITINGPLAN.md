# WRITINGPLAN: How to Improve the Site's Writing

> Based on ISIDORE5's diagnosis ("the site lacks hospitality") and Pris's
> pedagogy mapping (the site starts at Hard difficulty). This plan applies
> the principle of progressive disclosure: meet the reader where they are,
> then walk them deeper.

---

## The Core Problem

The HP is genuinely difficult. A macaronic Renaissance dream narrative
illustrated with 172 woodcuts, annotated by alchemists using planetary
symbols in Latin syntax — this is not material that explains itself.

The site currently presents this material at expert level on every page.
Signature notation, quire structure, d'Espagnet's Enchiridion, pseudo-
Geberian gender inversion — all without establishing what the HP is or
why a non-specialist would care.

The fix is not to dumb anything down. It's to add the entry ramp that's
currently missing.

---

## Phase 1: The Entry Ramp (write first, highest impact)

### 1a. Rewrite the Home page intro (300 words)

Three paragraphs:

**Paragraph 1: The Hook.**
What the HP is. Not "one of the most celebrated and enigmatic books of
the Italian Renaissance" (a claim that means nothing to someone who
hasn't heard of it). Instead: what does the book look and feel like?
A 500-page dream narrative with 172 woodcuts, written in a language
that mixes Italian, Latin, and Greek, published in Venice in 1499 by
the most famous printer of the age. The most elaborately illustrated
book of the fifteenth century.

**Paragraph 2: The Readers.**
Why the marginalia matter. Not "Russell's PhD thesis documented the
marginalia in six copies" (a process description). Instead: what did
Russell discover? Ben Jonson used it for stage design. A pope collected
examples of verbal wit. Two anonymous alchemists independently decoded
it as a chemistry textbook — but they disagreed about what kind.

**Paragraph 3: This Site.**
What the visitor can do here. Browse the folio images. Read the alchemist
analyses. Explore 94 dictionary terms. See the timeline of five centuries
of reception. Trace the concordance that connects Russell's arguments to
the actual manuscript photographs.

### 1b. Add "The Book" page (1500-2000 words)

A narrative summary of the HP's plot, divided by sections. Not a
scholarly analysis — a walkthrough. Written for someone who has never
read the HP and probably never will, but who wants to understand what
happens in it.

Sections:
1. The dark forest and the awakening (a1r-a5v)
2. The ruined temple and the colossal architecture (a6r-b8v)
3. Queen Eleuterylida and the three gates (c-d)
4. The five nymphs and the bath (d-f)
5. The triumphal processions (f-i)
6. The sacrifice to Priapus
7. The voyage to Cythera and the circular garden
8. Venus's temple and the union with Polia
9. Book II: Polia speaks
10. The awakening

Each section should reference the relevant woodcuts (with links to
woodcut pages) and the relevant dictionary terms (with inline links).

### 1c. Rewrite the About page as narrative, not statistics

Structure:
1. What this project is (1 paragraph)
2. What Russell found (2 paragraphs)
3. How the concordance works (1 paragraph, plain language)
4. What's on this site (bullet list of sections with word counts)
5. What's provisional (honest accounting)
6. How it was built (technical details, for the curious)

---

## Phase 2: Inline Links (30 minutes, high leverage)

### 2a. Add dictionary term links within essay prose

When the Russell essay mentions "alchemical allegory," the phrase should
link to dictionary/alchemical-allegory.html. When it mentions "prisca
sapientia," link to dictionary/prisca-sapientia.html. When it mentions
"d'Espagnet," link to the master-mercury entry. This is 15-20 inline
links added to existing text.

### 2b. Add dictionary term links in folio descriptions

The 13 alchemical folio descriptions mention terms that exist in the
dictionary (mercury, Sol/Luna, chemical wedding, ideogram). These should
be linked.

### 2c. Add "What is this?" tooltips or glosses on technical terms

When the marginalia index mentions "signature notation," the first
occurrence should include a brief inline explanation: "a bibliographic
code combining a quire letter, leaf number, and side — so b6v means
the back of the sixth leaf in quire b."

---

## Phase 3: Differentiate Overlapping Pages (1 hour)

### 3a. Give each page type a distinct editorial voice

Currently the marginalia page for b6v, the woodcut page for the
elephant-obelisk, and the Russell essay all describe the same image
in similar terms. Each should have a distinct role:

- **Marginalia folio page:** Evidence dossier. Focus on: what's on this
  page, what annotations are present, what Russell says about it. Tone:
  forensic, specific. "On this folio, Hand B placed five alchemical
  ideograms around the woodcut's elephant figure."

- **Woodcut page:** Art-historical entry. Focus on: what the image
  depicts, its artistic significance, its influence. Tone: descriptive,
  contextual. "The elephant bearing an obelisk combines Egyptian and
  classical elements in the HP's characteristic mode of syncretic
  antiquarianism."

- **Essay:** Interpretive argument. Focus on: what the alchemist's
  reading reveals about the HP's reception. Tone: analytical, narrative.
  "Hand B's dense ideographic annotations on b6v demonstrate how the
  alchemical reader embedded chemical signs into the syntax of Latin
  commentary."

### 3b. Reduce repetition by linking, not restating

When the woodcut page discusses b6v, it should link to the marginalia
page for the annotation details rather than restating them. When the
essay discusses b6v, it should link to the woodcut page for the
art-historical context rather than re-describing Bernini's sculpture.

---

## Phase 4: Scholar-to-Content Reverse Links (30 minutes)

### 4a. Add "HP passages discussed" to scholar pages

For scholars where the data is available (from summaries.json or the
corpus), add a section listing which HP passages, folios, or woodcuts
the scholar discusses. This makes the scholar page a bidirectional
index: not just "what did this scholar write?" but "what part of the
HP did they write about?"

### 4b. Add "Scholars who discuss this" to dictionary term pages

The related_scholars field on dictionary_terms is currently NULL for all
94 terms. Populate it from bibliography cross-references: if a scholar's
bibliography entry has a topic_cluster matching a dictionary term's
category, link them.

---

## Phase 5: Progressive Disclosure on Landing Pages

### 5a. Each landing page intro should answer three questions

1. **What is this section?** (one sentence)
2. **Why does it matter?** (one sentence connecting to the HP or Russell)
3. **How do I use it?** (one sentence of navigation guidance)

The current intros answer #1 but not #2 or #3.

### 5b. Add a "Start Here" path for new visitors

A suggested reading order for someone who has never encountered the HP:
1. Read "The Book" (plot summary)
2. Read the About page (what Russell found)
3. Browse the Home gallery (see the manuscript images)
4. Read the Russell essay (the best writing on the site)
5. Explore the dictionary by category
6. Pick a folio page with alchemical annotations

This could be a simple numbered list on the Home page.

---

## What This Plan Does NOT Do

- Does not rewrite 94 dictionary entries (content is adequate; framing needs work)
- Does not rewrite 60 scholar pages (overviews are functional; links need adding)
- Does not redesign the CSS or navigation
- Does not add new database tables or scripts

It adds ~3000 words of new prose (Home rewrite + Book page + About rewrite),
~40 inline links, and restructures existing content for progressive
disclosure. Total effort: approximately 3-4 hours.

---

## Priority Order

1. **"The Book" page** — the single highest-impact addition (anchors everything)
2. **Home page rewrite** — the first thing every visitor reads
3. **Inline dictionary links in essays** — turns the dictionary into a learning tool
4. **About page rewrite** — establishes the project's purpose
5. **Differentiate overlapping pages** — reduces repetition, clarifies roles
6. **Scholar reverse links** — connects scholars to HP content
7. **Landing page intros** — answers "why does this matter?"
8. **"Start Here" path** — guides new visitors

The first 4 items transform the site from a specialist reference to an
accessible scholarly resource. The remaining items refine what's already built.
