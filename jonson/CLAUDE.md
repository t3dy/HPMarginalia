# Ben Jonson Project — Working Instructions

## Scope

This project has exactly three goals:

1. An annotated digital edition of **The Alchemist** focused on alchemy
2. A **Life of Ben Jonson** section from PDFs in `../Ben Jonson Life/`
3. A **research showcase** of James Russell's findings on Jonson's annotations in the Hypnerotomachia Poliphili

This project is a **tab** within the parent HP Marginalia website.

## Rules

1. **No feature creep.** Do not add Digby as a separate page. Do not build a knowledge graph. Do not add speculative modules.
2. **Alchemy only.** The Alchemist annotations cover alchemical dimensions only — not general literary commentary.
3. **Ben Jonson only.** The life section and HP annotations showcase are about Jonson. Digby appears only as context.
4. **No fabrication.** Never invent evidence. Never present LLM interpretation as source evidence.
5. **Provenance required.** Every structured record must cite its source document and page.
6. **Validate outputs.** Required fields must be present. Citations must be attached. No orphan records.
7. **Source evidence vs interpretation.** Keep these distinct in every output.

## Source Corpus

All source PDFs live in `../Ben Jonson Life/`. Converted markdown versions are in `../Ben Jonson Life/md/`.

| File | Type | Content |
|------|------|---------|
| Hart edition PDF (255pp) | PDF→MD | The Alchemist text with scholarly apparatus |
| Arden critical reader (EPUB) | EPUB→MD | Modern critical essays on The Alchemist |
| Mardock (175pp) | PDF→MD | Ben Jonson's London, biographical context |
| Darke Hierogliphicks extract | TXT→MD | Alchemy in English lit, Maier chapter |
| Russell/O'Neill PPTX (46 slides) | PPTX→MD | Jonson's HP marginalia, alchemical hand, Digby attribution |

## Architecture

```
../Ben Jonson Life/md/  (converted source markdown)
    ↓
jonson/src/ingest/      (read + catalog sources)
    ↓
jonson/data/raw/        (source document records as JSON)
    ↓
jonson/src/extract/     (excerpt extraction)
    ↓
jonson/data/processed/  (excerpts, classified)
    ↓
jonson/src/transform/   (structured record extraction)
    ↓
jonson/data/exports/    (website-ready JSON)
    ↓
jonson/src/site/        (page builders)
    ↓
site/jonson/            (static HTML, integrated with HP nav)
```

## Storage

JSON files for the seed stage. SQLite later if needed.

## Build

```bash
python jonson/scripts/build.py
```

## Integration with HP Site

The Ben Jonson section appears as a tab in the HP Marginalia nav bar.
Pages live under `site/jonson/`. Nav links use `jonson/` prefix.
