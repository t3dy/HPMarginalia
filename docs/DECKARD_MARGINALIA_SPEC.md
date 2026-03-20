# Deckard Boundary Map: Marginalia Ontology & Alchemical Hands

> Deterministic vs probabilistic task boundaries for the marginalia system.
> Read this spec before executing any marginalia or alchemical enrichment work.

## Schema Extensions

### New Table: `alchemical_symbols`
Reference table for the standard alchemical sign vocabulary.

```sql
CREATE TABLE alchemical_symbols (
    id INTEGER PRIMARY KEY,
    symbol_name TEXT NOT NULL UNIQUE,
    symbol_unicode TEXT,
    metal TEXT,
    planet TEXT,
    gender TEXT,
    framework TEXT,
    notes TEXT,
    source_basis TEXT
);
```

### New Table: `symbol_occurrences`
Junction table linking symbols to specific folio annotations.

```sql
CREATE TABLE symbol_occurrences (
    id INTEGER PRIMARY KEY,
    symbol_id INTEGER REFERENCES alchemical_symbols(id),
    hand_id INTEGER REFERENCES annotator_hands(id),
    signature_ref TEXT,
    folio_description_id INTEGER REFERENCES folio_descriptions(id),
    context_text TEXT,
    latin_inflection TEXT,
    thesis_page INTEGER,
    confidence TEXT DEFAULT 'MEDIUM',
    source_method TEXT DEFAULT 'CORPUS_EXTRACTION',
    needs_review BOOLEAN DEFAULT 1
);
```

### New Column: `annotator_hands.alchemical_framework`
```sql
ALTER TABLE annotator_hands ADD COLUMN alchemical_framework TEXT;
```

## Deterministic Tasks
- Fix BL confidence levels (SQL UPDATE)
- Seed alchemical symbols (7 planetary metals from Taylor 1951)
- Populate alchemical_framework for Hand B and Hand E
- Regex attribution pass for 89 unattributed refs
- Extract folio mentions from thesis chunks

## Probabilistic Tasks (LLM, DRAFT provenance)
- Generate folio_descriptions for remaining alchemist refs
- Classify annotations by alchemical process stage
- Map symbol occurrences from thesis evidence
- Generate hand-interaction notes

## Validation
- Every LLM-generated datum: source_method='LLM_ASSISTED', review_status='DRAFT'
- Every corpus-extracted datum: source_method='CORPUS_EXTRACTION'
- Never overwrite VERIFIED content
- All symbol mappings cite Taylor 1951 or Russell 2014
