# HPDECKARD: Boundary Map — Deterministic vs. Probabilistic Tasks

> Deckard distinguishes humans from androids. This audit distinguishes tasks that should be deterministic code from tasks that need LLM judgment.

## Current Pipeline: 11 Scripts, All Deterministic

Every script in the pipeline is currently **purely deterministic** — regex, SQL, filesystem parsing, hardcoded data. No LLM processing anywhere in the codebase. This is both a strength and a limitation.

---

## DETERMINISTIC TASKS (correctly deterministic)

| Task | Script | Why Deterministic |
|------|--------|-------------------|
| Schema creation | init_db.py | Fixed structure, no ambiguity |
| Image filename parsing | catalog_images.py | Known naming conventions, regex sufficient |
| Signature map generation | build_signature_map.py | Aldine collation formula is mathematical |
| Folio-to-image matching | match_refs_to_images.py | SQL join on folio numbers, no interpretation |
| JSON export for website | export_showcase_data.py | Data serialization, no judgment needed |
| Markdown chunking | chunk_documents.py | Word count and heading splits, mechanical |
| HTML page generation | build_scholar_profiles.py | Template filling from structured data |
| Database writes | add_hands.py, add_bibliography.py | Inserting curated metadata |

**Verdict: CORRECT.** These tasks are properly deterministic. No LLM needed.

---

## PROBABILISTIC TASKS (currently done by human/LLM in conversation, not in code)

These tasks were performed during our conversation using Claude but are **not captured in any script**. They exist only in conversation context and their outputs were manually inserted into hardcoded data structures.

| Task | Where It Happened | Why Probabilistic |
|------|-------------------|-------------------|
| **Article summarization** | Conversation (batch agents) | Requires reading comprehension, topic identification, judgment about what matters |
| **Topic cluster classification** | Conversation (agent output) | Fuzzy boundaries (is Stewering "text_image" or "architecture_gardens"?) |
| **Hand attribution from dissertation text** | Conversation → add_hands.py HANDS dict | Required reading Russell's prose and interpreting which signature refs belong to which annotator |
| **Author/title extraction from filenames** | pdf_to_markdown.py (hardcoded dict) | Filenames are messy; correct metadata required judgment |
| **Bibliography gap analysis** | Conversation (agent output) | Determining which cited works are "HP-specific" vs. "tangential" requires domain judgment |
| **Scholar profile creation** | Conversation → add_bibliography.py SCHOLARS list | Birth/death years, nationality, specialization all required research and judgment |
| **Mislabeled file identification** | Conversation (agents flagged Jarzombek, Canone/Spruit) | Content-metadata mismatch detection requires reading the actual text |

**Verdict: These are legitimately probabilistic tasks.** The current approach — using Claude in conversation to perform them, then hardcoding the results — is pragmatically correct for a small corpus. But it doesn't scale.

---

## BOUNDARY VIOLATIONS

### WASTE: Tasks using LLM where deterministic code would suffice

| Violation | Current Method | Recommendation |
|-----------|---------------|----------------|
| **Folio reference extraction** | extract_references.py uses regex (CORRECT), but the initial extraction of hand attribution rules was done manually by reading the dissertation | Write a more sophisticated regex/NLP pipeline that detects phrases like "Hand B labels" or "this annotator writes" near signature references, to semi-automate hand attribution |
| **Chapter page ranges** | Hardcoded approximations in extract_references.py | Parse the PDF's table of contents or detect chapter headings automatically |
| **Author/title from filenames** | 250-line hardcoded dictionary in pdf_to_markdown.py | Parse YAML frontmatter from already-generated markdown files, or extract from PDF metadata fields (many academic PDFs embed DOI, author, title) |

### RISK: Deterministic code doing something that needs judgment

| Violation | Current Method | Risk |
|-----------|---------------|------|
| **Signature matching assumes BL photo number = folio number** | match_refs_to_images.py | The BL copy is the 1545 edition, not the 1499. The photos are Russell's research photos, not a systematic facsimile. **Photo 014 may not be folio 14.** All BL matches should be LOW confidence until manually verified. |
| **Single-hand attribution for entire chapters** | add_hands.py attributes all Modena refs to "Primary" hand | Russell documents that Modena has a second hand (possibly Paolo Giovio). The "Primary" blanket attribution hides this nuance. |
| **Topic cluster assignment** | Hardcoded in add_bibliography.py | A work can belong to multiple clusters (Stewering is both architecture and text-image). The single-value schema loses information. |
| **Signature regex false-positive filtering** | extract_references.py filters by stopword list | Some legitimate signatures could be filtered (e.g., if a quire were labeled 'be' or 'do'). The 1499 HP doesn't use these quires, but a generalized tool would need smarter filtering. |

### DANGER: LLM output flowing into database without validation

| Violation | Current Method | Danger |
|-----------|---------------|--------|
| **Article summaries** | Generated by Claude agents → saved to summaries.json → used by build_scholar_profiles.py | No human review step between LLM summarization and publication on the website. Summaries could contain hallucinated claims, misattributions, or copyright-infringing quotes. |
| **Scholar metadata** | Generated by Claude from dissertation text → hardcoded in add_bibliography.py | Birth/death years, institutional affiliations, and nationality could be wrong. No cross-reference against authoritative sources (VIAF, ORCID, WorldCat). |
| **Mislabeled file corrections** | Claude identified Jarzombek and Canone/Spruit as misfiled | Correct identifications, but the corrections were applied to summaries.json without verifying against the actual PDF content programmatically. |

---

## RECOMMENDATIONS

### Immediate (before deployment)

1. **Downgrade all BL C.60.o.12 matches to LOW confidence** until a human verifies that photo numbers correspond to folio numbers. The current MEDIUM is overconfident.

2. **Add a `reviewed` flag to summaries.json** and display "unreviewed" badge on scholar pages that haven't been human-checked.

3. **Add multi-value topic_cluster** support (change to comma-separated or junction table) so works can belong to multiple clusters.

### Medium-term (scaling the corpus)

4. **Build an LLM-in-the-loop summarization pipeline** with structured output validation:
   ```
   PDF → extract text → LLM summarize with JSON schema →
   validate (author exists in VIAF? year matches PDF metadata?) →
   human review queue → database
   ```

5. **Semi-automate hand attribution** by searching dissertation text for patterns like `"[Hh]and [A-E].*\b([a-z]\d[rv])\b"` to associate hands with specific signature references.

6. **Extract bibliography programmatically** from the markdown of all articles (look for "References", "Bibliography", "Works Cited" sections) to discover additional cited works we don't have.

### Long-term (website features)

7. **Semantic search** across article summaries and dissertation chunks — this is a legitimate LLM/embedding task that would add real value to the website.

8. **Automated timeline generation** from dated events extracted from all articles — requires NLP for date/event extraction from prose.

9. **Cross-reference graph** showing which scholars cite which other scholars — requires parsing bibliography sections, a mix of deterministic (regex for citation formats) and probabilistic (resolving ambiguous author names).

---

## BOUNDARY MAP SUMMARY

```
DETERMINISTIC (11/11 scripts — CORRECT)
├── Schema & data loading     ✓ init_db, add_hands, add_bibliography
├── File parsing              ✓ catalog_images, pdf_to_markdown
├── Reference extraction      ✓ extract_references (regex)
├── Matching                  ✓ match_refs_to_images, build_signature_map
├── Export                    ✓ export_showcase_data, build_scholar_profiles
└── Chunking                  ✓ chunk_documents

PROBABILISTIC (done in conversation, not in code)
├── Article summarization     ⚠ No validation pipeline
├── Topic classification      ⚠ Single-value, loses nuance
├── Hand attribution          ⚠ Hardcoded from conversation analysis
├── Scholar metadata          ⚠ No authoritative cross-reference
└── Mislabeled file detection ⚠ Correct but ad-hoc

BOUNDARY VIOLATIONS
├── WASTE: Hardcoded metadata that could be auto-extracted    (3 cases)
├── RISK: Deterministic matching with unverified assumptions  (4 cases)
└── DANGER: LLM output → database without validation gate    (3 cases)
```

**Overall assessment**: The pipeline is architecturally sound — deterministic where it should be, with LLM judgment applied only where genuinely needed. The main weakness is the **validation gap** between LLM-generated content (summaries, metadata, attributions) and the database. Before deployment, add review flags and confidence scoring. Before scaling, build a structured validation pipeline for LLM outputs.
