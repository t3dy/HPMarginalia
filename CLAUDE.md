# HP Marginalia: Project Instructions

## What This Is

A static website presenting the marginalia, scholarship, and reception
history of the 1499 *Hypnerotomachia Poliphili*. SQLite database →
Python scripts → static HTML. Deployed to GitHub Pages.

## 5 Core Documents

| Doc | What It Covers |
|-----|---------------|
| **SYSTEM.md** | Architecture, data flow, operating modes, constraints |
| **ONTOLOGY.md** | All 24 tables (canonical + deprecated), relationships, coverage |
| **PIPELINE.md** | Every script in execution order, rebuild sequence |
| **INTERFACE.md** | What's surfaced on the site, what's hidden, page builders |
| **ROADMAP.md** | What's BUILT, what's READY, what's BLOCKED, what's SPECULATIVE |

Read SYSTEM.md first. It has everything you need to start working.

## Quick Reference

- **365 pages**, 14 nav tabs
- **24 tables**, 3 deprecated (dissertation_refs, doc_folio_refs, annotators)
- **47 scripts** in scripts/
- **431 matches** (48 HIGH, 383 MEDIUM, 0 LOW)
- **219 image_readings** (30 historical + 189 Phase 1)
- BL offset = 13 (photo 014 = page 1) — confirmed at 174/174 readable pages
- **60 woodcuts** detected by vision reading (18 in canonical table)

## Canonical Tables

Use `annotations` (not dissertation_refs). Use `annotator_hands` (not annotators).
Use `hp_copies` (not manuscripts for copy-level data).

## Constraints

1. **Outward not deeper.** Surface existing data before adding more.
2. **Reality over design.** Database beats documentation. Always.
3. **No new specs without execution.** Build what's designed before designing more.

## Build

```bash
python scripts/build_site.py   # All 365 pages
```

## Spec Files (in docs/)

Detailed specs for writing templates, scholar pipeline, timeline, manuscripts,
marginalia symbols. Read these before modifying those subsystems.

## Session Discipline

At the end of every major session, update:
- **PHASESTATUS.md** — phase completion, what changed, next steps, blockers
- Core docs if any counts or claims have drifted

Before starting work, check PHASESTATUS.md for:
- Whether proposed work has met prerequisites
- Whether any phases are BLOCKED
- Current schema version and table count

## Image Reading Rules

- ALL analysis uses `images.master_path` (originals), NEVER `images.web_path` (compressed)
- Call `image_utils.assert_not_web_derivative()` before reading any image
- All vision outputs go to `image_readings` table first, never directly to canonical tables
- Promotion from `image_readings` to canonical tables requires human review

## Archived Documents

36+ design docs, critiques, plans, and research reports in `docs/archive/`.
These are project history — readable but not authoritative. The 5 core
docs above supersede them.
