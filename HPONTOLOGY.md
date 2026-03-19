# HP Ontology: Modeling the Hypnerotomachia Poliphili

## Why an Ontology?

The *Hypnerotomachia Poliphili* (HP) is not a single artifact — it is a constellation of objects, agents, and scholarly acts spread across five centuries. A page in a 1499 Venetian printing press became a leaf in a British Library codex, which became the subject of a photograph, which became evidence in James Russell's dissertation, which became a row in our SQLite database. Each step transforms the thing. An ontology gives us a shared language for these transformations so that we can reliably query across them.

Without an ontology, we end up with a bag of files and hope. "Image 47" means nothing until you know it depicts folio b7r of BL C.60.o.12, that the folio contains a marginal annotation in a sixteenth-century hand reading *"obsidie"* beside Colonna's description of an obsidian elephant, and that Russell discusses this annotation on page 97 of his thesis in the context of lexical extraction practices. That chain — physical artifact to digital surrogate to scholarly interpretation — is what the ontology encodes.

## Domain Analysis

### The Core Entities

After examining the corpus (38 documents, 674 images, 282 extracted references), we identified six fundamental entity types:

#### 1. **Work** — The abstract intellectual creation
The HP exists as an abstract work independent of any physical copy. It was composed (probably by Francesco Colonna) in the late fifteenth century, published by Aldus Manutius in Venice in 1499, and has been translated, excerpted, and reimagined ever since. The Work entity captures:
- Title (in its various forms: *Hypnerotomachia Poliphili*, *Strife of Love in a Dream*, etc.)
- Attributed author(s)
- Date of composition vs. date of publication
- Language (the original is a macaronic blend of Italian, Latin, Greek, Hebrew, Arabic, and Egyptian hieroglyphs)
- Structural divisions (the text is organized into signature-based quires, not numbered chapters)

The 1499 Aldine edition's collation — quires a through G, mostly quaternions of 8 leaves each, producing 224 folios and 448 pages — is itself a structural fact about the Work that governs how every physical copy is organized.

#### 2. **Copy** — A specific physical exemplar
Each surviving copy of the 1499 edition is a distinct historical object with its own provenance, binding, condition, and — crucially — its own marginalia. Russell's thesis examines six copies:

| Shelfmark | Institution | City | Chapter |
|-----------|------------|------|---------|
| F.C. Panini Estate | Private collection | Modena | 4 |
| INCUN A.5.13 | Biblioteca Pubblica | Como | 5 |
| **C.60.o.12** | **British Library** | **London** | **6** |
| RBR ALDUS 1499.C7 | Buffalo & Erie County Public Library | Buffalo | 7 |
| Inc.Stam.Chig.II.610 | Biblioteca Apostolica Vaticana | Vatican City | 8 |
| **O.III.38** | **Biblioteca degli Intronati** | **Siena** | **9** |

Our database currently holds image sets for the two bolded copies. The ontology must support adding the remaining four copies (and any others discovered) without schema changes.

#### 3. **Folio** — A leaf within a copy, identified by signature
This is the critical bridging entity. A folio is identified by its signature (e.g., *a4r*, *c7v*, *p6v*) using the standard bibliographic notation: quire letter + leaf number + side (recto/verso). The `signature_map` table in our database maps each of the 448 signature positions to a sequential folio number, enabling cross-referencing between Russell's textual citations and sequential image filenames.

The mapping is deterministic for the standard collation. However, individual copies may have anomalies: missing leaves, inserted plates, rebound quires. The ontology must accommodate copy-specific deviations from the ideal collation.

#### 4. **Annotation** — A mark left by a reader
An annotation is a marginal note, underline, manicule, cross-reference, or other reader's mark found on a specific folio of a specific copy. Russell's research focuses on these. Key properties:
- **Location**: which copy, which folio, where on the page (margin, interlinear, endpaper)
- **Content**: the text of the annotation (often a Latin or Italian word or phrase)
- **Relationship to printed text**: what passage the annotator was responding to
- **Hand**: which annotator (copies may have multiple historical readers' marks)
- **Type**: lexical extraction, cross-reference, commentary, correction, drawing
- **Date estimate**: based on handwriting, ink, and contextual clues

Russell identified 282 folio references across 124 unique signature positions. The densest annotation occurs in the opening folios (a1r through e1r), consistent with Russell's observation that annotators' energy is strongest at the beginning.

#### 5. **Image** — A digital surrogate
An image is a photograph or scan of a physical folio. Our database holds 674 images:
- **BL C.60.o.12**: 189 sequential page scans (`C_60_o_12-001.jpg` through `C_60_o_12-189.jpg`) plus 7 detail photos of marginalia (`BL HP 12.jpg`, etc.)
- **Siena O.III.38**: 468 folio scans with explicit recto/verso marking (`O.III.38_0001r.jpg` through `O.III.38_0234v.jpg`) plus covers, guard leaves, and 2 marginalia details

The critical design challenge was mapping between three incompatible numbering systems:
- Russell's **signature notation**: `a4r`, `c7v` (bibliographic convention)
- BL's **sequential numbering**: `001`, `002`, `003` (photographer's convention)
- Siena's **folio numbering**: `0001r`, `0001v`, `0002r` (archivist's convention)

The `signature_map` table resolves this: signature `a4r` maps to folio 4, which corresponds to BL image `C_60_o_12-004.jpg` and Siena image `O.III.38_0004r.jpg`. This three-way join is the core query pattern of the entire system.

#### 6. **ScholarlyWork** — Secondary literature about the HP
The 38 documents in our corpus represent five centuries of HP scholarship, classifiable as:
- **Primary texts** (3): the 1499 edition itself in various reproductions
- **Dissertations** (2): Russell's thesis and O'Neill's Durham thesis on self-transformation
- **Scholarship** (32): journal articles, monographs, and edited volumes
- **Presentations** (1): a PowerPoint on Ben Jonson and Kenelm Digby's engagement with the HP

These scholarly works reference specific folios, annotations, and copies. The ontology must support linking a scholarly claim to the evidence it cites.

### The Relationships

The entities above are connected by a web of relationships:

```
Work ──contains──> Folio (via signature position)
Copy ──instantiates──> Work
Copy ──has leaf──> Folio (a specific physical leaf)
Folio ──bears──> Annotation
Image ──depicts──> Folio (of a specific Copy)
ScholarlyWork ──references──> Folio
ScholarlyWork ──analyzes──> Annotation
ScholarlyWork ──discusses──> Copy
```

## Current Implementation: SQLite Schema

Our current database implements a pragmatic subset of this ontology:

```
documents       → ScholarlyWork (all 38 documents)
manuscripts     → Copy (BL C.60.o.12 + Siena O.III.38)
images          → Image (674 files, linked to manuscripts)
signature_map   → Folio (448 signature-to-folio mappings)
dissertation_refs → Annotation references (282 extracted from Russell)
matches         → Image↔Annotation links (73 HIGH + 537 MEDIUM confidence)
```

### What's Missing (Future Work)

1. **Annotation entity**: Currently annotations are embedded in `dissertation_refs` rather than being first-class entities. A dedicated `annotations` table would allow multiple scholars to reference the same physical annotation.

2. **Multi-copy support**: The schema can hold any number of manuscripts but the signature-to-image mapping assumes standard collation. Copy-specific collation anomalies need a `copy_collation_overrides` table.

3. **Annotator identification**: Russell identifies distinct hands in some copies. An `annotators` table linking to annotations would support handwriting analysis.

4. **Woodcut inventory**: The HP contains 172 woodcuts. These are not yet cataloged but are referenced by scholars and visible in the images.

5. **Cross-copy comparison**: The ability to view the same folio across all six copies side by side requires all copies to be imaged and registered.

## Design Decisions and Their Rationale

**Why signature-based addressing instead of page numbers?**
Early printed books don't have page numbers. The HP uses signature marks (printed at the bottom of the first few leaves of each quire) as the native addressing system. Every scholar who writes about the HP uses signatures. Any system that imposed modern page numbers would create a translation burden for every user.

**Why SQLite instead of a graph database?**
The relationships in this domain are regular and predictable — they form a tree (Work > Copy > Folio > Annotation) with cross-references (ScholarlyWork > Folio). This is comfortably modeled in relational tables with foreign keys. A graph database would add operational complexity without meaningful querying advantage at this scale. If the project grows to encompass all ~300 known surviving copies, this decision should be revisited.

**Why separate images from folios?**
A single folio may have multiple images (a full-page scan plus a detail crop of a marginal note). The `page_type` field in the `images` table distinguishes PAGE, MARGINALIA_DETAIL, COVER, GUARD, and OTHER. This allows the showcase page to display the most appropriate image for each context.

## Extending the Ontology

The ontology is designed to grow. Adding a new copy requires:
1. One row in `manuscripts`
2. Image files in a new subdirectory
3. Running `catalog_images.py` with a new parser function for that copy's filename convention
4. The `signature_map` already covers all 448 positions — it works for any standard copy

Adding a new scholarly work requires:
1. Dropping the PDF in the root directory
2. Re-running `init_db.py` (it uses INSERT OR IGNORE, so existing records are preserved)
3. Optionally running a reference extraction script tailored to that work's citation style

The ontology's value compounds as more copies, more images, and more scholarship are ingested. Each new data source enriches every existing cross-reference.
