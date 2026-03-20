# TIMELINEPLAN: Execution Plan for the Timeline Tab

## What Exists

- **42 timeline events** already in `timeline_events` table (editions, annotations, acquisitions, scholarship)
- **Full spec** at `docs/TIMELINE_SPEC.md` with data model, page design, and content plan
- **109 bibliography entries** with dates that can be mapped to timeline events
- **Writing templates** at `docs/WRITING_TEMPLATES.md` governing prose style

## What Needs Building

### Schema Migration (5 minutes)

Add 5 columns to `timeline_events`:
- `category` TEXT — visual grouping for the timeline
- `medium` TEXT — for art events: painting/sculpture/engraving
- `location` TEXT — where art/objects are now
- `image_ref` TEXT — optional image reference
- `confidence` TEXT DEFAULT 'MEDIUM'

Script: `scripts/migrate_timeline.py` (to create)

### Content Seeding (30 minutes)

Extend 42 events to ~100+ by adding:

**Art inspired by the HP:**
- Garofalo painting with HP scene (c.1520, identified by Saxl 1937)
- Bernini's elephant-obelisk (1667, Piazza della Minerva, Rome)
- Sleeping nymph fountain copies across European gardens (16th-17th c.)
- Watteau's L'Embarquement pour Cythere (1717, Louvre)
- Beardsley illustrations (1890s, referenced by Praz 1947)

**Literary influence:**
- Rabelais, Gargantua — Abbey of Theleme (1534)
- Robert Dallington, English translation (1592)
- Beroalde de Verville, alchemical French edition (1600)
- Swinburne references (19th c., per Praz)

**Scholarly milestones (from bibliography):**
- Gnoli 1899 (first modern study)
- Huelsen 1910 (woodcut sources)
- Blunt 1937 (French reception)
- Fierz-David 1950 (Jungian reading)
- Casella & Pozzi 1959 (authorship attribution)
- Pozzi & Ciapponi 1964 (critical edition)
- Gombrich 1972 (emblematics)
- Calvesi 1996 (Roman Colonna)
- Lefaivre 1997 (Alberti attribution)
- Ariani & Gabriele 2004 (Adelphi edition)
- Russell 2014 (annotation study)
- Young 2024 (new English translation)

**Music:** Research needed — currently no documented musical works confirmed

Script: `scripts/seed_timeline_v2.py` (to create)

### Page Builder (1 hour)

Add `build_timeline_page()` to `build_site.py`:
- Vertical scrolling timeline with year markers
- Event cards color-coded by type
- JavaScript filter checkboxes (Editions, Annotations, Scholarship, Art)
- Cross-links to scholar pages, dictionary terms, bibliography
- No framework — vanilla HTML/CSS/JS

Add "Timeline" tab to `nav_html()`.

### Cross-Linking (15 minutes)

- Timeline events link to scholar pages where `scholar_id` is set
- Timeline events link to bibliography entries where `bib_id` is set
- Dictionary terms like `reception-history`, `1499-edition`, `beroalde-1600` link to timeline

## Execution Order

```
1. scripts/migrate_timeline.py     # Schema migration
2. scripts/seed_timeline_v2.py     # Seed ~60 new events
3. Update build_site.py            # Add build_timeline_page() + nav tab
4. python scripts/build_site.py    # Rebuild
5. Validate                        # Nav, paths, page count
6. Deploy                          # git push
```

## Infrastructure vs Prompts

Everything above is grounded in `docs/TIMELINE_SPEC.md`. A future session reads that file and executes. No prompt archaeology needed.

## What This Plan Does NOT Do

- Does not research music comprehensively (needs separate investigation)
- Does not create interactive JavaScript timeline libraries (keeps it vanilla)
- Does not add images to timeline events (image hosting is a separate concern)
- Does not claim completeness — the timeline will grow as more events are identified
