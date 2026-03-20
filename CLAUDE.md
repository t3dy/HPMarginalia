# HP Marginalia: Project Instructions

## What This Is

A static website presenting the marginalia, scholarship, and reception
history of the 1499 *Hypnerotomachia Poliphili*. SQLite database →
Python scripts → static HTML. Deployed to GitHub Pages.

## 5 Core Documents

| Doc | What It Covers |
|-----|---------------|
| **SYSTEM.md** | Architecture, data flow, operating modes, constraints |
| **ONTOLOGY.md** | All 22 tables (canonical + deprecated), relationships, coverage |
| **PIPELINE.md** | Every script in execution order, rebuild sequence |
| **INTERFACE.md** | What's surfaced on the site, what's hidden, page builders |
| **ROADMAP.md** | What's BUILT, what's READY, what's BLOCKED, what's SPECULATIVE |

Read SYSTEM.md first. It has everything you need to start working.

## Quick Reference

- **354 pages**, 14 nav tabs
- **22 tables**, 3 deprecated (dissertation_refs, doc_folio_refs, annotators)
- **42 scripts** in scripts/
- **431 matches** (48 HIGH, 383 MEDIUM, 0 LOW)
- BL offset = 13 (photo 014 = page 1)

## Canonical Tables

Use `annotations` (not dissertation_refs). Use `annotator_hands` (not annotators).
Use `hp_copies` (not manuscripts for copy-level data).

## Constraints

1. **Outward not deeper.** Surface existing data before adding more.
2. **Reality over design.** Database beats documentation. Always.
3. **No new specs without execution.** Build what's designed before designing more.

## Build

```bash
python scripts/build_site.py   # All 354 pages
```

## Spec Files (in docs/)

Detailed specs for writing templates, scholar pipeline, timeline, manuscripts,
marginalia symbols. Read these before modifying those subsystems.

## Archived Documents

36 design docs, critiques, plans, and research reports in `docs/archive/`.
These are project history — readable but not authoritative. The 5 core
docs above supersede them.
