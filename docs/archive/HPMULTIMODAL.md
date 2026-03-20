# HPMULTIMODAL: Multimodal RAG Architecture for HP Image Collections

A study of how multimodal retrieval-augmented generation could enhance our work with the 674 manuscript images (BL C.60.o.12 and Siena O.III.38 scans) and the 172 woodcuts of the HP.

---

## Current State: Text-Only Matching

Our entire image pipeline is currently text-based:

```
Russell's thesis (text) → regex extracts signature refs → signature map → folio numbers → image filenames
```

The images themselves are never "read." We match by filename pattern, not by content. This means:

1. **We don't know what's actually on each page.** Photo `C_60_o_12-014.jpg` is *assumed* to show folio b6v based on filename arithmetic. Nobody (human or machine) has verified this by looking at the image.

2. **We can't search the marginalia.** Russell transcribed selected annotations in his thesis. The thousands of other marks, underlines, symbols, and notes on the 196 BL photos are invisible to our system.

3. **We can't identify woodcuts.** We know from the text that folio b6v should contain the Elephant and Obelisk woodcut. But we haven't confirmed this by examining the image.

4. **We can't compare across copies.** The Siena and BL copies show the same text but different marginalia. We can't automatically identify corresponding pages or detect differences.

---

## What Multimodal RAG Would Enable

### Tier 1: Image Understanding (Vision Models)

Use a vision-language model (Claude, GPT-4V, or open-source alternatives like LLaVA) to "read" each image and extract structured data.

**Per-image extraction prompt:**

```
This is a photograph of a page from a 15th-century printed book
(Hypnerotomachia Poliphili, Venice, 1499).

Analyze this image and report:
1. SIGNATURE: Is there a printed signature mark visible at the bottom
   of the page? If so, what does it read? (e.g., "b6", "e1")
2. SIDE: Is this a recto (right-hand page, odd-numbered) or verso
   (left-hand page, even-numbered)?
3. WOODCUT: Is there a woodcut illustration? If yes, describe its
   subject in one sentence.
4. MARGINALIA: Are there handwritten annotations visible in the margins?
   If yes:
   a. How many distinct hands can you identify?
   b. What language(s) are the annotations in?
   c. Can you transcribe any legible text?
   d. Are there any symbols or ideograms (alchemical, astronomical)?
5. TEXT_CONDITION: Is the printed text legible? Any damage, staining,
   or cropping?
6. PAGE_ELEMENTS: List any special features: decorated initials,
   Greek/Hebrew/Arabic passages, shaped text (technopaegnia),
   tables, diagrams.

Output as JSON.
```

**What this would produce:**
- **Verified signature matches**: Instead of assuming `C_60_o_12-014.jpg = folio b6v`, we'd read the actual signature mark from the image. This directly solves the BL confidence problem.
- **Woodcut catalog**: Automatic identification and description of all 172 woodcuts across both copies, enabling a browsable woodcut gallery with subject metadata.
- **Marginalia transcription**: Even partial transcriptions would be a massive scholarly contribution. Russell transcribed selected annotations; multimodal reading could attempt all visible marginalia.
- **Hand identification features**: Ink color, script style, and annotation density could be extracted as features for hand attribution.

### Tier 2: Embedding and Retrieval (Multimodal RAG)

Once images are processed, embed both the image features and the extracted text into a shared vector space for retrieval.

**Architecture:**

```
┌──────────────────┐     ┌──────────────────┐
│  Image Embeddings │     │  Text Embeddings  │
│  (CLIP / SigLIP)  │     │  (text-embedding) │
└────────┬─────────┘     └────────┬─────────┘
         │                         │
         └───────────┬─────────────┘
                     │
              ┌──────▼──────┐
              │ Vector Store │
              │  (ChromaDB)  │
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │  RAG Query   │
              │  Interface   │
              └─────────────┘
```

**What this enables:**

1. **"Show me pages with alchemical symbols"** → retrieves images where the vision model detected ideograms, ranked by relevance.

2. **"Find marginalia discussing mercury"** → searches both Russell's transcribed annotations AND the vision model's new transcriptions.

3. **"Which pages have this woodcut?"** → given a description or a reference image, finds matching pages across both copies.

4. **"Compare folio b6v across copies"** → retrieves the BL and Siena versions of the same folio, with differences highlighted.

5. **"What did the alchemist annotator write on this page?"** → retrieves the specific annotations attributed to Hand B, cross-referenced with Russell's analysis.

### Tier 3: Cross-Copy Alignment

The most ambitious application: automatically aligning corresponding pages across the BL and Siena copies.

**Challenge**: The BL copy is the 1545 edition (recast woodcuts, slightly different layout). The Siena copy is the 1499 edition. Page-for-page correspondence isn't guaranteed.

**Approach**:
1. Extract printed text from each page via OCR (Tesseract or vision model)
2. Use text overlap to identify corresponding pages
3. Build a cross-copy concordance: `BL photo 014 ↔ Siena folio 0014r/v`
4. For aligned pairs, diff the marginalia: what annotations appear in one copy but not the other?

This would directly validate (or correct) our current folio-to-image mapping, upgrading 218 BL matches from LOW to HIGH confidence.

---

## Practical Architecture

### Option A: Batch Processing Pipeline (Recommended for Phase 1)

Process all 674 images through a vision model in batch, store results in SQLite.

```python
# scripts/read_images.py

import anthropic
import base64
import sqlite3
import json
from pathlib import Path

client = anthropic.Anthropic()

def analyze_image(image_path):
    """Send image to Claude for structured analysis."""
    with open(image_path, 'rb') as f:
        image_data = base64.standard_b64encode(f.read()).decode()

    response = client.messages.create(
        model="claude-sonnet-4-6",  # Cost-effective for batch processing
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": image_data
                }},
                {"type": "text", "text": EXTRACTION_PROMPT}
            ]
        }]
    )
    return json.loads(response.content[0].text)

def process_all_images():
    """Batch process all manuscript images."""
    conn = sqlite3.connect('db/hp.db')
    cur = conn.cursor()

    cur.execute("""
        SELECT i.id, i.filename, i.relative_path, m.shelfmark
        FROM images i
        JOIN manuscripts m ON i.manuscript_id = m.id
        WHERE i.page_type = 'PAGE'
    """)

    for img_id, filename, rel_path, shelfmark in cur.fetchall():
        result = analyze_image(rel_path)

        # Store vision analysis
        cur.execute("""
            INSERT OR REPLACE INTO image_analysis
                (image_id, detected_signature, detected_side,
                 has_woodcut, woodcut_description,
                 has_marginalia, marginalia_count, marginalia_languages,
                 marginalia_transcription, has_symbols,
                 text_condition, special_features,
                 source_method, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'VISION_MODEL', 'MEDIUM')
        """, (img_id, result.get('signature'), result.get('side'),
              result.get('has_woodcut'), result.get('woodcut_description'),
              ...))

    conn.commit()
```

**New table needed:**

```sql
CREATE TABLE image_analysis (
    id INTEGER PRIMARY KEY,
    image_id INTEGER REFERENCES images(id) UNIQUE,
    detected_signature TEXT,
    detected_side TEXT,
    has_woodcut BOOLEAN,
    woodcut_description TEXT,
    has_marginalia BOOLEAN,
    marginalia_count INTEGER,
    marginalia_languages TEXT,
    marginalia_transcription TEXT,
    has_symbols BOOLEAN,
    symbol_types TEXT,
    text_condition TEXT,
    special_features TEXT,
    source_method TEXT DEFAULT 'VISION_MODEL',
    confidence TEXT DEFAULT 'MEDIUM',
    needs_review BOOLEAN DEFAULT 1,
    model_used TEXT,
    processed_at TEXT DEFAULT (datetime('now'))
);
```

**Cost estimate** (Claude Sonnet):
- 674 images × ~1500 input tokens (image) × ~500 output tokens
- ≈ 1M input tokens + 340K output tokens
- At Sonnet pricing: ~$5-8 total
- Runtime: ~30-45 minutes with rate limiting

### Option B: Embedding Pipeline (Phase 2)

After batch processing, embed images and text for retrieval.

```python
# scripts/embed_images.py

import chromadb
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction

# Use CLIP embeddings for image-text alignment
embedding_fn = OpenCLIPEmbeddingFunction()

client = chromadb.PersistentClient(path="db/chroma")
collection = client.get_or_create_collection(
    name="hp_pages",
    embedding_function=embedding_fn
)

# Add images with their extracted metadata
for image in images:
    collection.add(
        ids=[str(image.id)],
        images=[image.path],  # CLIP embeds the image directly
        metadatas=[{
            "signature": image.detected_signature,
            "shelfmark": image.shelfmark,
            "has_marginalia": image.has_marginalia,
            "has_woodcut": image.has_woodcut,
            "woodcut_description": image.woodcut_description,
        }],
        documents=[image.marginalia_transcription]
    )
```

**Query examples:**

```python
# Text-to-image: find pages matching a description
results = collection.query(
    query_texts=["elephant carrying an obelisk"],
    n_results=5
)

# Image-to-image: find similar pages across copies
results = collection.query(
    query_images=["path/to/BL/C_60_o_12-014.jpg"],
    n_results=3,
    where={"shelfmark": "O.III.38"}  # Search only Siena copy
)
```

### Option C: Interactive Multimodal Chat (Phase 3)

Build a chat interface where users can ask questions about specific pages:

```
User: "What does the alchemist write next to the elephant woodcut?"

System: [Retrieves folio b6v images from both copies]
        [Sends to vision model with context from Russell Ch. 6]

Response: "In the BL copy (C.60.o.12), Hand B wrote alchemical ideograms
around the elephant and obelisk woodcut on b6v. The annotation includes
the symbols for mercury (☿) and gold (☉) with Latin inflections.
Russell (2014, p. 157) transcribes: '[symbol]-ra scintillata' which
may read 'scintillata aurata' (shimmering gold). The Siena copy
shows no marginalia on this folio."
```

This combines vision (reading the actual image), retrieval (finding the right images and Russell's commentary), and generation (synthesizing an answer).

---

## What Specifically Changes for Our Data

### BL Confidence Problem: Solved

The single biggest data quality issue is the 218 LOW confidence BL matches. Multimodal processing would:

1. Read the signature mark from each BL photo
2. Compare to our assumed folio number
3. Confirm or correct each match
4. Upgrade confirmed matches to HIGH confidence

**Expected outcome**: Most matches are probably correct (the assumption that photo number ≈ folio number is reasonable). But some may be off by 1-2 folios, and some photos may be detail shots or duplicates. The vision model would catch these.

### Marginalia Discovery

Russell documented ~282 folio references. But the 196 BL photos contain marginalia on virtually every page. A multimodal pass would:

1. Detect all pages with marginalia (not just those Russell discussed)
2. Attempt transcription of visible annotations
3. Classify annotations by type (marginal note, underline, symbol, drawing)
4. Estimate the number of distinct hands per page

**Expected outcome**: Hundreds of new annotation records, mostly partial transcriptions. Quality would vary — some annotations are in clear hands, others are faded or cramped. Each transcription would carry `confidence = 'MEDIUM'` and `source_method = 'VISION_MODEL'`, clearly distinguished from Russell's manual transcriptions.

### Woodcut Identification

The 1499 HP has 172 woodcuts. The Siena facsimile has all of them. A multimodal pass would:

1. Identify which folios contain woodcuts
2. Describe each woodcut's subject
3. Match corresponding woodcuts across the Siena (1499) and BL (1545) copies
4. Detect differences in the recast 1545 woodcuts

**Expected outcome**: A complete, searchable woodcut catalog — something that currently exists only in Huelsen's 1910 study.

### Alchemical Symbol Detection

The BL alchemist (Hand B) used ideograms that are difficult to transcribe as text. A vision model could:

1. Detect non-alphabetic symbols on each page
2. Classify them against known alchemical symbol vocabularies
3. Create a visual index of all symbols used by Hand B
4. Compare with Newton's Keynes MSS vocabulary (if images available)

**Expected outcome**: A visual concordance of alchemical symbols — useful for the specialist but also visually striking for the website.

---

## Risks and Mitigations

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Vision model misreads signatures | Medium | Cross-check against signature_map; flag discrepancies for human review |
| Marginalia transcription errors | High | Mark all vision transcriptions as MEDIUM confidence; display alongside (not replacing) Russell's verified transcriptions |
| Cost overruns from large image batches | Low | Process in small batches; use Sonnet (cheaper) not Opus for routine extraction |
| Hallucinated woodcut descriptions | Medium | Compare vision descriptions against known woodcut subjects from Huelsen |
| 15th-century handwriting defeats OCR | High for some pages | Accept partial transcriptions; flag low-confidence pages; don't claim completeness |
| CLIP embeddings don't capture manuscript-specific features | Medium | Fine-tune or use specialized models (e.g., HTR models for historical handwriting) |

---

## Implementation Roadmap

| Phase | What | Cost | Time | Dependencies |
|-------|------|------|------|-------------|
| 0 | Add `image_analysis` table to schema | Free | 1 hour | None |
| 1 | Batch-process 10 test images with vision model | ~$0.10 | 1 hour | Anthropic API key |
| 2 | Review Phase 1 results; refine extraction prompt | Free | 2 hours | Phase 1 output |
| 3 | Batch-process all 674 images | ~$5-8 | 2 hours | Refined prompt |
| 4 | Validate detected signatures against signature_map | Free | 1 hour | Phase 3 output |
| 5 | Upgrade confirmed BL matches to HIGH confidence | Free | Minutes | Phase 4 |
| 6 | Build woodcut catalog from extracted descriptions | Free | 2 hours | Phase 3 output |
| 7 | Set up ChromaDB with CLIP embeddings | Free | 3 hours | Phase 3 output |
| 8 | Build multimodal search interface | Free | 4 hours | Phase 7 |
| 9 | Interactive chat with page-level context | ~$2/month | 4 hours | Phases 3, 7 |

**Total Phase 1-5 cost: under $10.**
**Total Phase 1-5 time: ~7 hours of work.**

The ROI is clear: for under $10, we solve the BL confidence problem, catalog all woodcuts, and discover hundreds of marginalia records that currently don't exist in our database. Phase 6+ adds search and interaction capabilities.

---

## Recommendation

**Start with Phase 1-2 immediately.** Process 10 representative images (5 BL, 5 Siena; mix of pages with/without marginalia, with/without woodcuts) to calibrate the extraction prompt and measure quality. If the vision model can reliably read signature marks and detect marginalia presence, proceed to full batch processing. If not, identify which subtasks work and which need specialized models.

The multimodal pipeline is not speculative — it directly addresses our single biggest data quality gap (BL match confidence) while producing genuinely new scholarly data (marginalia transcriptions, woodcut catalog). It fits cleanly into our existing architecture: vision model outputs go into SQLite tables with the same `source_method` / `confidence` / `needs_review` pattern as everything else. No new infrastructure required.
