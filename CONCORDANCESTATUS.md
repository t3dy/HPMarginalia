# CONCORDANCESTATUS: Current State of the HP Concordance System

> Generated 2026-03-20. All figures drawn from db/hp.db and the live site.

---

## 1. Pipeline Overview

The concordance links Russell's signature-based dissertation references to manuscript photographs through a deterministic pipeline:

```
Russell's thesis (PDF)
  → extract_references.py (regex extraction)
    → 282 dissertation_refs
      → build_signature_map.py (1499 collation formula)
        → 448 signature_map entries
          → match_refs_to_images.py (join via folio number)
            → 610 matches to 674 images
```

Each step is deterministic. The only probabilistic elements enter downstream: hand attribution (68% coverage), folio descriptions (LLM-assisted), and significance prose (LLM-assisted).

---

## 2. Core Data Inventory

| Table | Rows | Status |
|-------|------|--------|
| dissertation_refs | 282 | Complete extraction from Russell's thesis |
| doc_folio_refs | 282 | Redundant mirror of dissertation_refs with provenance columns |
| signature_map | 448 | Deterministic, correct for 1499 edition |
| images | 674 | 196 BL (C.60.o.12) + 478 Siena (O.III.38) |
| matches | 610 | 26 HIGH + 366 MEDIUM + 218 LOW |
| annotations | 0 | Schema exists, never populated |
| annotator_hands | 11 | Complete with prose descriptions |
| folio_descriptions | 13 | Alchemist folios only |
| alchemical_symbols | 10 | 7 planetary metals + 3 substances |
| symbol_occurrences | 26 | Mapped across 13 folios (9 BL, 4 Buffalo) |
| hp_copies | 6 | Russell's 6 annotated copies |

---

## 3. Confidence Distribution

### By Manuscript

| Manuscript | HIGH | MEDIUM | LOW | Total |
|------------|------|--------|-----|-------|
| Siena O.III.38 | 26 | 366 | 0 | 392 |
| BL C.60.o.12 | 0 | 0 | 218 | 218 |
| **Total** | **26** | **366** | **218** | **610** |

### Why BL Is LOW

All 218 BL matches are LOW confidence because:
1. BL photographs are sequentially numbered (001-196), not labeled by folio
2. The matching pipeline assumes photo N = folio N, which is unverified
3. The BL copy is the 1545 edition; the signature map is based on the 1499 collation
4. Any differences in pagination between editions would invalidate the mapping

### Why Siena Is HIGH/MEDIUM

Siena images encode folio information directly in filenames (O.III.38_0014r.jpg = folio 14 recto). HIGH matches are exact signature+side matches. MEDIUM matches are folio-number matches where side is ambiguous or cross-referenced.

---

## 4. Hand Attribution

### Coverage

| Status | Count | Percentage |
|--------|-------|------------|
| Attributed (hand_id set) | 193 | 68% |
| Unattributed (hand_id NULL) | 89 | 32% |

### By Hand

| Hand | Manuscript | Refs | Alchemist | Framework |
|------|-----------|------|-----------|-----------|
| A | C.60.o.12 | 8 | No | — |
| B | C.60.o.12 | 11 | Yes | mercury_despagnet |
| A | Buffalo RBR | 2 | No | — |
| B | Buffalo RBR | 6 | No | — |
| C | Buffalo RBR | 0 | No | — |
| D | Buffalo RBR | 4 | No | — |
| E | Buffalo RBR | 8 | Yes | sulphur_pseudo_geber |
| Primary | Modena (Panini) | 29 | No | — |
| Primary | INCUN A.5.13 | 42 | No | — |
| Primary | Inc.Stam.Chig.II.610 | 55 | No | — |
| Primary | O.III.38 | 28 | No | — |

### Gap: 89 Unattributed References

Most unattributed refs come from introductory/methodological chapters where Russell discusses multiple copies without assigning specific hands. A regex pass against the thesis text could recover some attributions, but many are genuinely multi-copy references.

---

## 5. Dissertation References by Manuscript

| Manuscript | Copy | Refs | Chapter(s) |
|------------|------|------|-----------|
| Buffalo RBR | Buffalo & Erie County PL | 59 | Ch. 7 |
| Inc.Stam.Chig.II.610 | Vatican Library | 55 | Ch. 8 |
| C.60.o.12 | British Library | 50 | Ch. 6 |
| INCUN A.5.13 | Cambridge UL | 42 | Ch. 5 |
| Modena (Panini) | Biblioteca Panini | 29 | Ch. 4 |
| O.III.38 | Biblioteca degli Intronati | 28 | Ch. 9 |

---

## 6. Alchemical Symbol System

### Symbols in Database

| Symbol | Metal | Planet | Gender | Framework |
|--------|-------|--------|--------|-----------|
| Sol | Gold | Sun | masculine | standard |
| Luna | Silver | Moon | feminine | standard |
| Mercury | Quicksilver | Mercury | hermaphroditic | d_espagnet |
| Venus | Copper | Venus | feminine | standard |
| Mars | Iron | Mars | masculine | standard |
| Jupiter | Tin | Jupiter | masculine | standard |
| Saturn | Lead | Saturn | masculine | standard |
| Cinnabar | Mercuric Sulphide | — | — | standard |
| Sulphur | Brimstone | — | masculine | pseudo_geber |
| Hermaphrodite | — | — | hermaphroditic | both |

### Occurrence Distribution

| Symbol | Occurrences | Primary Hand |
|--------|-------------|-------------|
| Sol | 8 | Both B and E |
| Mercury | 6 | Hand B (BL) |
| Luna | 5 | Both B and E |
| Sulphur | 2 | Hand E (Buffalo) |
| Jupiter | 2 | Hand B (BL) |
| Venus | 1 | Hand B (BL) |
| Hermaphrodite | 1 | Hand E (Buffalo) |
| Cinnabar | 1 | Hand B (BL) |

### Two Alchemical Frameworks

**Hand B (BL, d'Espagnet):** Mercury-centered. The HP's "true sense" is the operations of Master Mercury. Uses extensive ideographic vocabulary with Latin inflections. Possible Royal Society / Cambridge connection (consistency with Newton's Keynes MSS).

**Hand E (Buffalo, pseudo-Geber):** Sulphur and Sol/Luna centered. Emphasizes gender inversion as the principle of transmutation. Reads the chess match (h1r) as three rounds of distillation producing a hermaphrodite (coincidentia oppositorum).

---

## 7. What Works

- **Signature map:** Deterministic and correct for the 1499 edition (448 entries)
- **Siena concordance:** HIGH/MEDIUM confidence, folio-labeled filenames, 478 images
- **Hand profiles:** All 11 hands described with attribution, language, interests
- **Folio descriptions:** 13 detailed analyses of alchemist-annotated folios
- **Symbol mapping:** 26 occurrences tracked across 13 folios with provenance
- **Cross-linking:** Folios link to dictionary terms, essays, and scholar pages

## 8. What Does Not Work or Is Missing

### Critical

| Gap | Impact | What Would Fix It |
|-----|--------|-------------------|
| BL concordance unverified (218 LOW matches) | Cannot trust any BL folio-to-image claim | Manual verification against high-res images, or multimodal AI reading visible signatures |
| `annotations` table empty (0 rows) | No first-class annotation entity; data split across dissertation_refs and folio_descriptions | Migrate dissertation_refs into annotations as canonical table |
| `doc_folio_refs` duplicates `dissertation_refs` | Redundant data, maintenance burden | Deprecate one table, consolidate |
| 89 unattributed refs | 32% of refs have no hand assignment | Regex attribution pass + manual review |

### Structural

| Gap | Impact | What Would Fix It |
|-----|--------|-------------------|
| No annotation type classification | Cannot query "all lexical annotations" vs "all alchemical annotations" | Add annotation_type field, classify with LLM (DRAFT) |
| No hand-to-hand interaction tracking | Cannot model stratigraphic relationships (who overwrites whom) | New table: hand_interactions (hand_a, hand_b, relationship, folio) |
| No HP source text linked to annotations | Cannot show what text the annotator was responding to | Link dissertation_refs to HP passage via signature + folio offset |
| Buffalo copy has no images | Cannot verify any Buffalo annotations visually | Acquire photographs or note limitation |
| Hand C (Buffalo) has 0 extracted refs | Gap in coverage | Re-read thesis Ch. 7 for Hand C mentions |

### Data Quality

| Issue | Current State | Target |
|-------|--------------|--------|
| Folio descriptions | 13 of 282 refs (5%) | All alchemist refs (28) should have descriptions |
| Symbol occurrences | 26 occurrences across 13 folios | Could be expanded with deeper thesis reading |
| Alchemical process stages | Not classified | Each alchemist ref could be tagged with nigredo/albedo/citrinitas/rubedo |

---

## 9. Site Integration Status

| Feature | Pages | Status |
|---------|-------|--------|
| Marginalia folio pages | 118 | Complete with images, annotations, alchemist tags |
| Alchemical analysis blocks | 13 folios | Showing on folio pages with element/process/framework |
| Symbol occurrence tables | 13 folios | Showing on folio pages with symbol/metal/planet/gender |
| Cross-links to dictionary | ~25 terms | Alchemical folios link to relevant dictionary entries |
| Cross-links to essays | 2 essays | Folios link to Russell Alchemical Hands + Concordance Method |
| Manuscripts tab | 6 copies | Each copy page shows hands, match stats, confidence |
| Timeline | 71 events | Chronological view of HP reception and scholarship |

---

## 10. Recommended Next Actions (Priority Order)

1. **Consolidate annotations table:** Migrate dissertation_refs into the annotations table as the canonical source. Deprecate doc_folio_refs.

2. **Regex hand attribution pass:** Run pattern matching on thesis text to attribute some of the 89 unattributed refs. Log all new attributions to staging for review.

3. **Annotation type classification:** Add annotation_type field to annotations. Classify each ref as LEXICAL, ALCHEMICAL, ARCHITECTURAL, BOTANICAL, CROSS_REFERENCE, SOURCE_ID, or OTHER. LLM-assisted, DRAFT provenance.

4. **Expand folio descriptions:** Generate descriptions for the remaining 15 alchemist-attributed refs that currently lack descriptions. Use reading packets + thesis chunks.

5. **Alchemical process stage tagging:** Tag each alchemist ref with the relevant transmutation stage (nigredo, albedo, citrinitas, rubedo) where identifiable from thesis evidence.

6. **Hand interaction table:** Create hand_interactions table tracking stratigraphic relationships (who overwrites whom, on which folios).

7. **BL verification (blocked):** When high-resolution BL images become available, verify the sequential-number-to-folio assumption either manually or via multimodal AI.
