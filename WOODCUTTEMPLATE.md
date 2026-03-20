# WOODCUTTEMPLATE: Page Templates for Woodcut Display

> Following docs/WRITING_TEMPLATES.md voice and style.
> Target reader: educated non-specialist who visits exhibitions.

---

## Woodcut Index Page (`site/woodcuts/index.html`)

### Template

```html
<div class="woodcuts-page">
    <h2>Woodcuts of the <em>Hypnerotomachia Poliphili</em></h2>
    <p class="intro">The 1499 HP contains approximately 172 woodcut
    illustrations — the most ambitious visual program of any incunabulum.
    The woodcuts range from full-page architectural compositions to small
    in-text vignettes to the historiated initials that spell the author's
    acrostic. Their designer remains unidentified, though candidates include
    Benedetto Bordon and the anonymous "Master of the Poliphilo."</p>

    <p class="intro">This index presents the woodcuts identified in the
    project's manuscript photographs. Where a BL photograph is available,
    the woodcut can be viewed alongside any marginal annotations.</p>

    <!-- Filter buttons -->
    <div class="woodcut-filters">
        <button data-filter="all" class="active">All</button>
        <button data-filter="ARCHITECTURAL">Architecture</button>
        <button data-filter="NARRATIVE">Narrative</button>
        <button data-filter="HIEROGLYPHIC">Inscriptions</button>
        <button data-filter="PROCESSION">Processions</button>
        <button data-filter="LANDSCAPE">Landscapes</button>
        <button data-filter="DECORATIVE">Decorative</button>
    </div>

    <!-- Woodcut grid -->
    <div class="woodcut-grid">
        <!-- For each woodcut -->
        <div class="woodcut-card" data-category="{subject_category}">
            <div class="woodcut-image">
                <!-- BL photo thumbnail if available -->
                <img src="../{image_path}" alt="{title}" loading="lazy">
            </div>
            <div class="woodcut-info">
                <h4><a href="{slug}.html">{title}</a></h4>
                <div class="woodcut-meta">
                    {signature} | p.{page} | {subject_category}
                </div>
                {annotation_badge if annotated}
                {alchemical_badge if alchemical}
            </div>
        </div>
    </div>
</div>
```

### CSS

```css
.woodcuts-page { max-width: 1000px; margin: 2rem auto; padding: 0 2rem; }
.woodcut-filters { display: flex; gap: 0.5rem; flex-wrap: wrap; margin: 1.5rem 0; }
.woodcut-filters button {
    padding: 0.3rem 0.8rem; border: 1px solid var(--border);
    border-radius: 3px; background: var(--bg); cursor: pointer;
    font-size: 0.85rem; font-family: var(--font-sans);
}
.woodcut-filters button.active { background: var(--accent); color: white; border-color: var(--accent); }
.woodcut-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1.5rem; margin-top: 1.5rem;
}
.woodcut-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 4px; overflow: hidden;
}
.woodcut-card img { width: 100%; height: 200px; object-fit: cover; }
.woodcut-info { padding: 0.75rem 1rem; }
.woodcut-info h4 { margin: 0 0 0.3rem; font-size: 0.95rem; }
.woodcut-info h4 a { color: var(--text); text-decoration: none; }
.woodcut-info h4 a:hover { color: var(--accent); }
.woodcut-meta { font-size: 0.75rem; color: var(--text-muted); font-family: var(--font-sans); }
```

---

## Woodcut Detail Page (`site/woodcuts/{slug}.html`)

### Template

```html
<div class="woodcut-detail">
    <p><a href="index.html">&larr; All Woodcuts</a></p>

    <h2>{title}</h2>
    <div class="woodcut-meta">
        {signature_1499} | Page {page_1499} | {subject_category} |
        {woodcut_type}
    </div>

    <!-- Image (if available) -->
    <div class="woodcut-image-full">
        <img src="../{bl_image_path}" alt="{title}">
        <div class="image-caption">
            BL C.60.o.12, photo {bl_photo_number}.
            {confidence_badge}
        </div>
    </div>

    <!-- Description -->
    <div class="woodcut-description">
        <h3>Description</h3>
        <p>{description}</p>
    </div>

    <!-- Narrative Context -->
    <div class="woodcut-context">
        <h3>In the Narrative</h3>
        <p>{chapter_context}</p>
    </div>

    <!-- Scholarly Discussion (if any) -->
    {if scholarly_discussion:}
    <div class="woodcut-scholarship">
        <h3>In Scholarship</h3>
        <p>{scholarly_discussion}</p>
    </div>

    <!-- Influence (if any) -->
    {if influence:}
    <div class="woodcut-influence">
        <h3>Influence</h3>
        <p>{influence}</p>
    </div>

    <!-- Annotations on this woodcut -->
    {if has_annotation:}
    <div class="woodcut-annotations">
        <h3>Marginal Annotations</h3>
        <p>This woodcut has been annotated by readers of the BL copy.</p>
        {if alchemical_annotation:}
        <div class="provisional">
            The alchemist (Hand B) annotated this woodcut with
            alchemical ideograms. See the
            <a href="../russell-alchemical-hands.html">Alchemical Hands essay</a>
            for analysis.
        </div>
        <!-- Link to marginalia page for this folio -->
        <p><a href="../marginalia/{signature}.html">View folio detail page</a></p>
    </div>

    <!-- 1545 Edition Notes -->
    {if signature_1545 differs:}
    <div class="woodcut-editions">
        <h3>Edition Variants</h3>
        <p>In the 1545 edition, this woodcut was recut from a new block.
        {edition_notes}</p>
    </div>

    <!-- Cross-links -->
    <div class="cross-links">
        <h4>Related Pages</h4>
        {links to dictionary terms, essays, marginalia pages}
    </div>

    <!-- Provenance -->
    <div class="provenance-section">
        {review_status_badge} | Source: {source_basis}
    </div>
</div>
```

### Writing Rules for Woodcut Descriptions

Following docs/WRITING_TEMPLATES.md:

**Voice:** Present tense, active, third-person scholarly but accessible.
**Length:** Description: 60-120 words. Context: 40-80 words.
**Required:** At least one specific reference to what is depicted.
**Citation:** Inline parenthetical for scholarly claims.
**Provenance:** Every generated description marked DRAFT, LLM_ASSISTED.

**Example description:**
"The elephant and obelisk woodcut occupies most of the page. An elephant
stands on a circular base bearing a tall obelisk decorated with
pseudo-hieroglyphic carvings. The composition anticipates Bernini's
1667 sculpture in Piazza della Minerva, Rome, commissioned by Pope
Alexander VII — who himself annotated his copy of the HP. In the BL
copy, Hand B (the alchemist) densely annotated this woodcut with
alchemical ideograms, reading the elephant-obelisk as encoding
alchemical processes (Russell 2014, pp. 156-157)."

**Example context:**
"Poliphilo encounters the elephant-obelisk monument during his exploration
of the great ruined classical complex early in his journey. The monument
represents the HP's fusion of Egyptian and classical antiquity — a
theme that recurs throughout the book's architectural program."
