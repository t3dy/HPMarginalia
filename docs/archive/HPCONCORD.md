# HPCONCORD: Concordance Methodology

## How We Built the Marginalia-to-Image Concordance

### Problem

James Russell's PhD thesis (Durham, 2014) references specific folios of six annotated copies of the *Hypnerotomachia Poliphili* by their **signature marks** (e.g., `b6v`, `e1r`, `y7r`). We have **photographs** of two of these copies — BL C.60.o.12 (196 images) and Siena O.III.38 (478 images) — but the photos are numbered **sequentially** (e.g., `C_60_o_12-014.jpg`, `O.III.38_0022r.jpg`), not by signature. The concordance bridges these two reference systems.

### Step 1: Signature Map (build_signature_map.py)

The 1499 HP uses a standard Aldine signature scheme: gatherings of 8 leaves (16 pages), labeled a–z then A–F. Each leaf has a recto (front) and verso (back) side.

We built a complete mapping of **448 signature positions**:

```
a1r → folio 1, recto    (image 001)
a1v → folio 1, verso    (image 001)
a2r → folio 2, recto    (image 002)
...
b1r → folio 9, recto    (image 009)
...
F3r → folio 227, recto  (image 227)
```

The key insight: the **BL sequential photo numbers** correspond to **folio numbers** (C_60_o_12-014.jpg = folio 14 = signature b6). The **Siena facsimile** uses explicit recto/verso notation (O.III.38_0014r.jpg / O.III.38_0014v.jpg).

**Important caveat**: The BL copy is the **1545 edition**, which has a slightly different layout than the 1499. The signature scheme is the same, but page content may differ by a few leaves. Matches are therefore MEDIUM confidence until manually verified against the actual image content.

### Step 2: Reference Extraction (extract_references.py)

We extracted **282 signature references** from Russell's dissertation PDF using regex pattern matching:

```python
# Matches: (a4r), (c7v), b6v:, etc.
SIG_PATTERN = re.compile(
    r'(?:\(([a-zA-Z]{1,2}\d[rv])\))'   # parenthesized
    r'|(?:\b([a-zA-Z]{1,2}\d[rv]):)'    # with colon
    r'|(?:\b([a-zA-Z]{1,2}\d[rv])\b)'   # bare
)
```

False positives (common English words + digit + r/v, like `in1r`) were filtered by stopword list.

Each reference was tagged with:
- **thesis_page**: page number in the PDF
- **chapter_num**: which copy chapter (4=Modena, 5=Como, 6=BL, 7=Buffalo, 8=Vatican, 9=Siena)
- **manuscript_shelfmark**: which physical copy
- **context_text**: surrounding paragraph
- **marginal_text**: quoted annotation text (if present)

### Step 3: Image Cataloging (catalog_images.py)

Scanned both image directories and inserted **674 image records**:
- **BL C.60.o.12**: 196 images (189 sequential + 7 reference photos)
- **Siena O.III.38**: 478 images (234 recto/verso pairs + covers/guards)

### Step 4: Matching (match_refs_to_images.py)

Joined signature references → signature map → image catalog to produce **610 matches**:

```sql
-- Example match chain:
-- Russell p.157 references "b6v" in BL copy
-- signature_map: b6v → folio 14, verso
-- images: C_60_o_12-014.jpg (folio 14)
-- → MATCH (FOLIO_EXACT, MEDIUM confidence)
```

All automated matches are flagged `needs_review = 1` for manual verification.

### Step 5: Hand Attribution (add_hands.py)

Created **11 annotator hand profiles** across the six copies, with two flagged as alchemists:

| Copy | Hand | Attribution | Alchemist? | School |
|------|------|------------|------------|--------|
| BL C.60.o.12 | A | Ben Jonson | No | — |
| BL C.60.o.12 | B | Anonymous | **Yes** | d'Espagnet |
| Buffalo | A | Anon. (Jesuit?) | No | — |
| Buffalo | B | Anon. (Jesuit?) | No | — |
| Buffalo | C | Anonymous | No | — |
| Buffalo | D | Anonymous | No | — |
| Buffalo | E | Anonymous | **Yes** | pseudo-Geber |
| Modena | Primary | Benedetto Giovio | No | — |
| Como | Primary | Benedetto Giovio | No | — |
| Vatican | Primary | Alexander VII | No | — |
| Siena | Primary | Anonymous | No | — |

Hand attribution rules map specific signature references to hands based on:
1. **Explicit attribution** in Russell's text (e.g., "Hand B labels b6v with alchemical ideograms")
2. **Page range** within the dissertation chapter (alchemical content starts p.155 in Ch. 6)
3. **Single-hand copies** (Modena, Como, Vatican, Siena) get all refs attributed to their primary hand

**193 references** were attributed to specific hands. **89 remain unattributed** (mostly from intro/methodology chapters where Russell discusses copies in general terms).

### Step 6: Bibliography and Timeline (add_bibliography.py)

Extracted **310 works** from Russell's bibliography, of which **58 HP-specific entries** were inserted into the database. Of these:
- **9 are in our collection** (15% coverage)
- **49 are cited but missing** — the expansion roadmap

Created **29 scholar profiles** and **39 timeline events** spanning 1499–2020.

---

## Database Schema Summary

```
manuscripts (2)          → physical copies with image directories
images (674)             → individual photographs
signature_map (448)      → signature → folio number mapping
dissertation_refs (282)  → folio references extracted from Russell
matches (610)            → ref ↔ image joins
annotator_hands (11)     → identified annotator profiles
bibliography (58)        → cited HP scholarship
scholars (29)            → scholar profiles
scholar_works (24)       → scholar ↔ work links
timeline_events (39)     → reception/scholarship timeline
```

## Key Queries

```sql
-- All alchemist annotations with matched images
SELECT h.attribution, h.school, r.thesis_page, r.signature_ref,
       i.filename, r.context_text
FROM annotator_hands h
JOIN dissertation_refs r ON r.hand_id = h.id
JOIN matches m ON m.ref_id = r.id
JOIN images i ON m.image_id = i.id
WHERE h.is_alchemist = 1
ORDER BY h.manuscript_shelfmark, r.thesis_page;

-- Scholarship gap: works we need
SELECT author, title, year, journal_or_publisher, topic_cluster
FROM bibliography
WHERE in_collection = 0 AND hp_relevance = 'DIRECT'
ORDER BY year;

-- Timeline of HP reception
SELECT year, year_end, event_type, title, description
FROM timeline_events ORDER BY year;
```

## Known Limitations

1. **BL 1545 vs. 1499 offset**: The BL copy is the 1545 edition; our signature map is based on the 1499. Content positions may differ by a few leaves. All BL matches are MEDIUM confidence.

2. **Photo coverage**: The 196 BL photos may not cover every annotated folio. Russell photographed selectively, focusing on the most interesting marginalia.

3. **Hand attribution gaps**: 89 of 282 references lack hand attribution. These are mostly introductory cross-references where Russell discusses multiple copies in general terms.

4. **Buffalo images missing**: We have no photographs of the Buffalo copy (5 hands including the pseudo-Geber alchemist). The matched BL/Siena images for Buffalo refs show the *same folio in a different copy*, not the Buffalo marginalia themselves.

5. **Automatic matching assumes sequential numbering = folio numbering**. This holds for both collections but should be verified against the first and last few images.
