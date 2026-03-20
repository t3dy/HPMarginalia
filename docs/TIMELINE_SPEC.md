# Timeline Tab Specification

> This spec defines the data model, content structure, and page design for a new
> Timeline tab showing the reception, marginalia, and scholarship history of the HP,
> including art and music inspired by the book.

## Goal

Create a chronological timeline page that presents the HP's 500+ year reception
history as a navigable, categorized visual timeline. The timeline should show:

- Publication and edition history (1499, 1545, translations)
- Annotation and marginalia events (when copies were annotated)
- Scholarly publications (major studies and their dates)
- Art inspired by the HP (Bernini's elephant-obelisk, Watteau, etc.)
- Music and literary works influenced by the HP
- Institutional acquisitions (when copies entered libraries)
- Key biographical events of annotators and scholars

## Data Model

### Existing Table: `timeline_events` (42 rows)

```sql
CREATE TABLE timeline_events (
    id INTEGER PRIMARY KEY,
    year INTEGER,
    year_end INTEGER,           -- for date ranges
    event_type TEXT,            -- PUBLICATION | EDITION | TRANSLATION | ACQUISITION |
                                -- ANNOTATION | SCHOLARSHIP | ART | MUSIC | LITERARY | OTHER
    title TEXT NOT NULL,
    description TEXT,
    scholar_id INTEGER REFERENCES scholars(id),
    bib_id INTEGER REFERENCES bibliography(id),
    manuscript_shelfmark TEXT,
    needs_review BOOLEAN DEFAULT 1,
    source_method TEXT
);
```

### New Columns Needed

```sql
ALTER TABLE timeline_events ADD COLUMN category TEXT;  -- for visual grouping
ALTER TABLE timeline_events ADD COLUMN medium TEXT;     -- for art: painting/sculpture/engraving/etc.
ALTER TABLE timeline_events ADD COLUMN location TEXT;   -- for art: where it is now
ALTER TABLE timeline_events ADD COLUMN image_ref TEXT;  -- optional image reference
ALTER TABLE timeline_events ADD COLUMN confidence TEXT DEFAULT 'MEDIUM';
```

### New Event Types to Add

| Type | Examples |
|------|----------|
| ART | Bernini's elephant-obelisk (1667), Garofalo painting (c.1520), etc. |
| MUSIC | Any musical compositions inspired by the HP |
| LITERARY | Rabelais's Theleme (1534), Swinburne/Beardsley references |
| EDITION | 1554 French, 1561 French, 1804 Italian reprint, etc. |
| SCHOLARSHIP | Major studies: Gnoli 1899, Huelsen 1910, Casella-Pozzi 1959, etc. |

## Page Design

### Timeline Page (`site/timeline.html`)

**Layout:** Vertical scrolling timeline with events as cards.

**Filters:** By event_type (checkboxes: Editions, Annotations, Scholarship, Art, Other)

**Structure:**
```
<div class="timeline">
    <!-- For each year that has events -->
    <div class="timeline-year">
        <div class="year-marker">1499</div>
        <div class="timeline-events">
            <div class="timeline-card" data-type="PUBLICATION">
                <div class="card-type-badge">Publication</div>
                <h4>Hypnerotomachia Poliphili published</h4>
                <p>Description text...</p>
                <div class="card-links">
                    <a href="dictionary/1499-edition.html">1499 Edition</a>
                    <a href="scholar/aldus-manutius.html">Aldus Manutius</a>
                </div>
            </div>
        </div>
    </div>
</div>
```

**CSS:** Timeline line on left, cards extending right. Color-coded type badges.
Year markers as sticky headers during scroll.

**JavaScript:** Filter checkboxes that show/hide event types. No framework required.

## Pipeline

### Step 1: `scripts/seed_timeline_v2.py`

Extend the existing 42 events with:
- Art events (Bernini 1667, Garofalo c.1520, Watteau 1717, etc.)
- Literary influence events (Rabelais 1534, etc.)
- More scholarship events (every major study from the bibliography)
- Music events (if any documented)
- Modern reception events (20th-century editions, exhibitions)

### Step 2: Update `build_site.py`

Add `build_timeline_page()` function. Add "Timeline" tab to nav.

### Step 3: Cross-link

- Timeline events link to scholar pages, dictionary terms, and bibliography entries
- Scholar pages and dictionary terms link back to timeline where relevant

## Validation Gates

- Every timeline event has year, event_type, and title
- Events link to scholars/bibliography where applicable
- No duplicate events
- Timeline page has nav, correct paths
- Chronological order is correct

## Content to Research and Add

### Art Inspired by the HP

| Date | Work | Artist/Creator | Type | Location |
|------|------|---------------|------|----------|
| c.1520 | Painting with HP scene | Garofalo | painting | identified by Saxl (1937) |
| 1667 | Elephant and Obelisk | Gian Lorenzo Bernini | sculpture | Piazza della Minerva, Rome |
| 1717 | L'Embarquement pour Cythere | Antoine Watteau | painting | Louvre, Paris |
| various | Garden designs influenced by HP | various | garden design | across Europe |
| 1893 | Illustrations by Aubrey Beardsley | Beardsley | illustration | (referenced by Praz) |

### Editions and Translations

The bibliography already tracks many of these. Cross-reference with timeline events.

### Scholarly Milestones

Map bibliography entries with year to timeline events. Each major study gets an event.
