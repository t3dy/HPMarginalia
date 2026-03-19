# HPONTOCRIT: Isidore Critique of the HP Ontology

> Jack Isidore forces you to question every claim. This critique examines HPONTOLOGY.md against what the project actually built, what the user actually asked for, and where the ontology's logic breaks down.

---

## CRITIQUE: HPONTOLOGY.md — "Modeling the Hypnerotomachia Poliphili"

---

STRONGEST PASSAGE: "Without an ontology, we end up with a bag of files and hope. 'Image 47' means nothing until you know it depicts folio b7r of BL C.60.o.12..." — This is the document's best moment. It concretely demonstrates why structured relationships matter by tracing a single image through its chain of meaning. It grounds the abstraction in a specific, verifiable example.

---

## ISSUES (by priority)

### 1. UNSUPPORTED CLAIM: The ontology says six entities, but the system built eighteen tables for at least twelve entities

"After examining the corpus... we identified six fundamental entity types: Work, Copy, Folio, Annotation, Image, ScholarlyWork."

The system as built has: documents, manuscripts, images, signature_map, dissertation_refs, doc_folio_refs, matches, annotator_hands, annotators, annotations, bibliography, scholars, scholar_works, timeline_events, dictionary_terms, dictionary_term_links, document_topics, schema_version.

That's at least **twelve distinct entity types**: Work (implicit), Copy (manuscripts), Folio (signature_map), Annotation (annotations + dissertation_refs + doc_folio_refs — three tables for what the ontology calls one entity), Image (images), ScholarlyWork (documents + bibliography — two tables), Scholar (scholars), Match (matches), Annotator (annotator_hands + annotators — two tables), DictionaryTerm, TimelineEvent, Topic.

The ontology document describes a clean six-entity model. The actual database is a messier twelve-entity model with duplicate tables (annotator_hands AND annotators, dissertation_refs AND doc_folio_refs) and entities that the ontology never mentions (scholars, dictionary terms, timeline events, topics, matches).

**The ontology was written before the system was fully built and was never updated.** It describes the initial design intent, not the actual architecture.

FIX: Rewrite the ontology to describe what actually exists. Either consolidate the duplicate tables (drop annotator_hands in favor of annotators, drop dissertation_refs in favor of doc_folio_refs) or explain why both exist and how they relate.

---

### 2. LOGICAL GAP: The "Annotation" entity was promised but never populated

The ontology devotes a full section to Annotation as entity #4, calling it a "mark left by a reader" with properties for location, content, hand, type, and date estimate. It then says in "What's Missing": "Currently annotations are embedded in dissertation_refs rather than being first-class entities."

The V2 migration created an `annotations` table. It has **zero rows**. Meanwhile `dissertation_refs` still has 282 rows and `doc_folio_refs` (a copy of dissertation_refs with provenance columns) also has 282 rows.

So the project has **three tables** for what should be one entity, and the cleanest of them is empty. The ontology describes an ideal that was never realized, and the migration added a new table without populating it or deprecating the old ones. This is the ontology's most significant failure: it defined the right abstraction but the implementation never followed through.

FIX: Either populate `annotations` from `dissertation_refs` (extracting the actual marginal text and annotator attribution into proper annotation records) and deprecate the old table, or acknowledge that `dissertation_refs` IS the annotations table and drop the empty one.

---

### 3. BURIED LEDE: The real ontological challenge is the Match, not the Annotation

The ontology doesn't mention the `matches` table at all. But matches — the link between a dissertation reference and a specific image — are the **core join** that makes the entire site work. Every gallery card, every marginalia page, every folio detail depends on this join.

The match is not a simple link. It carries confidence (HIGH/MEDIUM/LOW/PROVISIONAL), a method (SIGNATURE_EXACT/FOLIO_EXACT/MANUAL), a review status, and provenance. The BL confidence problem — the single biggest data quality issue in the project — is entirely a Match problem. Yet the ontology describes it as a solved three-way join ("signature a4r maps to folio 4, which corresponds to BL image C_60_o_12-004.jpg") without mentioning that this join is **unverified for 218 of the 610 matches**.

The match is the most intellectually interesting entity in the system. It's where certainty degrades, where different numbering systems collide, where edition differences create ambiguity. The ontology treats it as plumbing.

FIX: Elevate Match to a first-class entity in the ontology. Describe its properties, its confidence semantics, and the conditions under which a match can be upgraded or downgraded.

---

### 4. AUDIENCE ASSUMPTION: The ontology addresses no one in particular

Who is this document for? It opens with "Why an Ontology?" as if persuading a skeptic, uses FRBR-adjacent terminology (Work/Copy) without citing FRBR, then drops into SQLite column names. A librarian would find the FRBR-without-FRBR framing frustrating. A developer would skip the philosophy and want the ER diagram. A scholar would want to know how to query for "all annotations by Ben Jonson on folios containing woodcuts."

The document tries to be all three things and succeeds at none completely.

FIX: Pick a primary audience. If it's developers, lead with the schema and explain the domain model through the tables. If it's scholars, lead with example queries that answer real research questions. If it's both, split into two sections with a shared introduction.

---

### 5. UNSUPPORTED CLAIM: "The ontology is designed to grow"

The document claims: "Adding a new copy requires: one row in manuscripts, image files, running catalog_images.py with a new parser function." This is presented as if it's trivially extensible.

But adding the Buffalo copy (which the user has expressed interest in) would require:
- No images (we don't have them) — so the "image files" step fails immediately
- Buffalo has 5 interleaved hands — the annotators table supports this but the hand attribution rules in `add_hands.py` are hardcoded per-copy
- Buffalo's marginalia are described only in Russell's prose — the extraction pipeline is tied to Russell's thesis page ranges, also hardcoded
- The 1499 vs. 1545 collation difference (BL is 1545, all others are 1499) is not modeled anywhere in the schema — it's handled by a blanket LOW confidence flag

"Designed to grow" is aspirational. The actual system is hardcoded to the specific data sources it was built from. Growth requires writing new scripts, not just inserting rows.

FIX: Be honest about what extensibility means. Document the actual steps for adding a new copy, including the scripting work. Or better: generalize the extraction and attribution pipelines so they genuinely are copy-agnostic.

---

### 6. MISSING ENTITY: The User's Requests Reveal Entities the Ontology Doesn't Model

Reviewing the user's prompts across this project reveals several entities they care about that the ontology ignores:

- **Translation**: The user asked for "all translations and marginalia eventually." The ontology models the 1499 text as a single Work but has no concept of the 1546 French, 1592 English, 1600 alchemical, or 2024 Young translations as related-but-distinct entities. These are not just ScholarlyWorks — they're instantiations of the Work in different languages, with different woodcut programs, different paratextual apparatus.

- **Woodcut**: The user asked about showcasing woodcuts. The ontology mentions 172 woodcuts in passing ("not yet cataloged") but doesn't model them. A woodcut is a visual entity that appears on a specific folio, may be modified across editions, and is referenced by scholars. It deserves its own table.

- **Alchemical Symbol**: The user was particularly interested in the alchemist annotators. The ontology doesn't model individual symbols or ideograms, which are the most visually distinctive feature of the alchemical marginalia.

- **Timeline Event**: The system has a timeline_events table with 42 entries. The ontology doesn't mention it. This is a significant omission — the user asked for "a hyperlinked timeline of the reception and scholarship of the HP."

- **Dictionary Term**: 37 terms with 76 cross-links. Not in the ontology. The user explicitly asked for a Dictionary tab and the system built it, but the ontological model pretends concepts don't exist as entities.

FIX: Extend the ontology to include Translation, Woodcut, Symbol, TimelineEvent, and DictionaryTerm as entities. Or acknowledge that the six-entity model is a simplification and point to the actual schema for the full picture.

---

### 7. REDUNDANCY: "Design Decisions and Their Rationale" repeats what the domain analysis already implies

The section on "Why signature-based addressing?" answers a question nobody asked — the entire document is already organized around signatures. The section on "Why SQLite?" makes a reasonable argument but could be one sentence: "The relationships are regular, the data is small, and SQLite has zero dependencies." The section on "Why separate images from folios?" is genuinely useful but repeats information from entity #5.

FIX: Cut the first two rationale sections to one sentence each. Keep the image/folio separation explanation but move it into the Image entity section.

---

### 8. WEAK TRANSITION: The "Current Implementation" section doesn't connect to "What's Missing"

The document goes from "here's what the schema looks like" directly to "here's what's missing" without evaluating what works. There's no assessment of whether the current schema successfully implements the ontology it describes. The reader has to do that analysis themselves.

In fact, the current schema DOESN'T implement the ontology — it implements something different (more tables, different relationships, duplicate entities). The gap between design and implementation is the document's most important finding and it's presented as a casual afterthought.

FIX: Add an "Implementation Assessment" section between the schema description and the gap list. Honestly evaluate where the schema matches the ontology and where it diverges. This is the section where you admit that the six-entity model was aspirational and the eighteen-table reality is what you actually have.

---

### 9. LOGICAL GAP: No entity for the Reader/User of this system

The ontology models historical readers (Annotators) but not the modern reader — the scholar or student using this website. The user's prompts reveal a consistent concern with how data is presented, what's trustworthy, and what needs review. The review_status / needs_review / confidence apparatus that now pervades the schema is a response to the ontological question: "Who is reading this data and what can they trust?"

The ontology doesn't ask this question. It models the HP's historical world but not the epistemological relationship between the system's outputs and its users. The HPDECKARD audits address this gap, but the ontology should have anticipated it.

FIX: Add a section on "Provenance and Trust" as an ontological dimension. Every entity has not just properties and relationships but also a trust level — how was this datum produced, by whom, and has it been verified? This isn't just metadata; it's an ontological commitment about the nature of the system's claims.

---

## REVISION PRIORITY

Fix **Issue #2** first (the empty annotations table) — it's the widest gap between what the ontology promises and what the system delivers. Then fix **Issue #1** (rewrite to match reality) and **Issue #6** (add missing entities). The other issues are improvements; these three are structural integrity problems.

---

## OVERALL

HPONTOLOGY.md is a well-written design document that was overtaken by events. It articulates a clean six-entity model for a Renaissance book project — Work, Copy, Folio, Annotation, Image, ScholarlyWork — and makes sensible arguments for signature-based addressing and relational storage. The writing is clear, the examples are concrete, and the opening paragraph is genuinely good.

But the document describes a system that doesn't exist. The actual system has eighteen tables implementing at least twelve entity types, with three tables for what the ontology calls "Annotation" (one of which is empty), two tables for "Annotator" (one a vestigial predecessor), and six entity types that the ontology doesn't mention at all (Scholar, DictionaryTerm, TimelineEvent, Topic, Match, Translation). The ontology was written early in the project and never revisited as the user's requests drove the system in directions the initial model didn't anticipate.

The deepest problem is not the gap between model and implementation — that's normal in iterative development. The deepest problem is that the ontology doesn't model **trust**. Every entity in this system exists on a spectrum from "verified deterministic fact" to "LLM-generated guess that hasn't been checked." The V2 migration added confidence/review fields to every table, the HPDECKARD audits formalized the boundary between deterministic and probabilistic data, and the site displays review badges everywhere. This entire apparatus addresses an ontological question — "what is the epistemic status of this datum?" — that the ontology document never asks. A revised ontology should make provenance and trust first-class concepts, not afterthoughts bolted on during migration.
