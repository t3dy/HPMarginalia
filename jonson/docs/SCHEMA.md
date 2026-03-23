# SCHEMA: Data Structures

## 1. SourceDocument

A source PDF, EPUB, or other document in the corpus.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| source_id | string | yes | Stable slug identifier |
| title | string | yes | Human-readable title |
| author | string | no | Author(s) |
| filename | string | yes | Original filename |
| md_filename | string | yes | Converted markdown filename |
| doc_type | string | yes | pdf, epub, pptx, txt |
| page_count | int | no | Number of pages/slides |
| content_focus | string[] | no | What this source covers |
| notes | string | no | Free-text notes |

```json
{
  "source_id": "hart-alchemist",
  "title": "The Alchemist, edited by H.C. Hart",
  "author": "Ben Jonson; ed. H.C. Hart",
  "filename": "The Alchemist by Ben J_Onson...pdf",
  "md_filename": "The_Alchemist_by_Ben_J_Onson_Newly_Edited_by.md",
  "doc_type": "pdf",
  "page_count": 255,
  "content_focus": ["alchemist_text", "alchemist_notes"],
  "notes": "1903 De La More Press edition. OCR has artifacts."
}
```

## 2. SourceExcerpt

A passage extracted from a source document.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| excerpt_id | string | yes | Stable identifier |
| source_id | string | yes | FK to SourceDocument |
| page_ref | string | yes | Page/slide number in original |
| text | string | yes | Extracted text |
| categories | string[] | no | Classification labels |

```json
{
  "excerpt_id": "hart-alchemist-p42",
  "source_id": "hart-alchemist",
  "page_ref": "p. 42",
  "text": "Svb. And all your alchemy, and your algebra...",
  "categories": ["alchemist_alchemy"]
}
```

## 3. PlayPassage

A passage from The Alchemist with act/scene/line reference.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| passage_id | string | yes | e.g. "alch-2.2.72-76" |
| act | int | yes | Act number (1-5) |
| scene | int | yes | Scene number |
| line_start | int | yes | Starting line |
| line_end | int | no | Ending line |
| text | string | yes | Quoted passage |
| speaker | string | no | Character speaking |
| source_id | string | yes | Which edition |
| source_page | string | no | Page in edition |

```json
{
  "passage_id": "alch-2.2.72-76",
  "act": 2,
  "scene": 2,
  "line_start": 72,
  "line_end": 76,
  "text": "My meat shall all come in in Indian shells, / Dishes of agate, set in gold...",
  "speaker": "Mammon",
  "source_id": "hart-alchemist",
  "source_page": "p. 52"
}
```

## 4. Annotation

An alchemical annotation attached to a PlayPassage.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| annotation_id | string | yes | Stable identifier |
| passage_id | string | yes | FK to PlayPassage |
| title | string | yes | Short annotation title |
| explanation | string | yes | What the alchemical content means |
| alchemical_concept | string | no | Core concept (e.g. "projection", "transmutation") |
| alchemical_category | string | no | substances, processes, metals_planets, transmutation, projection, fraud, laboratory, symbolic |
| cultural_context | string | no | Early modern context |
| citations | Citation[] | yes | Provenance |
| confidence | string | no | HIGH, MEDIUM, LOW |
| extraction_method | string | yes | MANUAL, DETERMINISTIC, LLM_ASSISTED |
| notes | string | no | Caveats or uncertainties |

```json
{
  "annotation_id": "ann-alch-2.2.72",
  "passage_id": "alch-2.2.72-76",
  "title": "Mammon's Fantasy of Alchemical Wealth",
  "explanation": "Mammon imagines the fruits of successful projection...",
  "alchemical_concept": "projection",
  "alchemical_category": "transmutation",
  "cultural_context": "The promise of unlimited wealth through the philosopher's stone...",
  "citations": [{"source_id": "arden-critical-reader", "page_ref": "ch. 3"}],
  "confidence": "HIGH",
  "extraction_method": "MANUAL"
}
```

## 5. LifeEvent

A structured event in Ben Jonson's life.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| event_id | string | yes | Stable identifier |
| date | string | yes | Date or approximate (e.g. "1572", "c. 1598", "1616-01") |
| date_sort | string | yes | ISO-ish sortable date |
| title | string | yes | Short title |
| description | string | yes | What happened |
| category | string | yes | literary, theatrical, biographical, religious, political |
| citations | Citation[] | yes | Provenance |
| notes | string | no | Uncertainties |

```json
{
  "event_id": "life-1616-folio",
  "date": "1616",
  "date_sort": "1616-01-01",
  "title": "Publication of the First Folio",
  "description": "Jonson published The Workes of Benjamin Jonson, the first folio...",
  "category": "literary",
  "citations": [{"source_id": "russell-pptx", "page_ref": "slide 3"}]
}
```

## 6. RussellFinding

A finding from James Russell's research on Jonson's HP annotations.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| finding_id | string | yes | Stable identifier |
| title | string | yes | Short title |
| description | string | yes | What Russell found |
| category | string | yes | ownership, signature, hand_characteristics, reading_practices, alchemist_links, attribution |
| evidence | string | no | Specific evidence cited |
| hp_page_ref | string | no | Page in the Hypnerotomachia (BL C.60.o.12) |
| citations | Citation[] | yes | Provenance |
| notes | string | no | Caveats |

```json
{
  "finding_id": "russell-signature",
  "title": "Jonson's Signature and Motto",
  "description": "Jonson signed the title page 'sum Ben: Ionsonii' ('I belong to Ben Jonson') in brown ink, and wrote his motto 'tanquam explorator' ('as an explorer/spy') at the top.",
  "category": "signature",
  "evidence": "Title page of BL C.60.o.12",
  "hp_page_ref": "title page",
  "citations": [{"source_id": "russell-pptx", "page_ref": "slide 5"}]
}
```

## 7. Citation

Provenance linking claims to sources. Embedded in other records.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| source_id | string | yes | FK to SourceDocument |
| page_ref | string | no | Page, slide, or section |
| quote | string | no | Direct quote (brief) |
| note | string | no | Context |

```json
{
  "source_id": "russell-pptx",
  "page_ref": "slide 5",
  "quote": "sum Ben: Ionsonii",
  "note": "Brown ink inscription on title page"
}
```

## Allowed Values

### categories (for excerpts)
- `jonson_life`
- `alchemist_alchemy`
- `hypnerotomachia_jonson`

### alchemical_category (for annotations)
- `substances`
- `processes`
- `metals_planets`
- `transmutation`
- `projection`
- `fraud`
- `laboratory`
- `symbolic`

### life_event category
- `literary`
- `theatrical`
- `biographical`
- `religious`
- `political`

### russell_finding category
- `ownership`
- `signature`
- `hand_characteristics`
- `reading_practices`
- `alchemist_links`
- `attribution`

### extraction_method
- `MANUAL`
- `DETERMINISTIC`
- `LLM_ASSISTED`

### confidence
- `HIGH`
- `MEDIUM`
- `LOW`
