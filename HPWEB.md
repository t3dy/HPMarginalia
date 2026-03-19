# HP Web: Building the Hypnerotomachia Poliphili Website

## Vision

The website is a scholarly exhibition space for the 1499 Aldine *Hypnerotomachia Poliphili*. It presents the book itself — its pages, its woodcuts, its readers' marks — alongside the five centuries of scholarship that have tried to make sense of it. The goal is not to be a search engine or a digital edition (those exist). The goal is to make the *experience* of encountering this book and its scholarly conversation accessible to anyone with a browser.

## What We Have Built So Far

### The Database (`db/hp.db`)
- **38 documents** cataloged with filenames, types, and basic metadata
- **2 manuscripts** registered (BL C.60.o.12, Siena O.III.38)
- **674 images** cataloged with parsed folio numbers, sides, and page types
- **448 signature mappings** (a1r through G4v) linking signature notation to sequential folio numbers
- **282 dissertation references** extracted from Russell's thesis
- **610 matches** linking references to images (73 HIGH confidence, 537 MEDIUM)

### The Showcase Page (`site/`)
- Static HTML/CSS/JS page displaying 44 matched entries
- Gallery grid with manuscript images, signature labels, and marginal text quotes
- Lightbox viewer with full-size image, Russell's commentary, and navigation
- Filterable by manuscript (BL / Siena / All)
- Responsive layout, lazy-loaded images

### The Pipeline (`scripts/`)
Five Python scripts that run sequentially:
1. `init_db.py` — schema creation and document/manuscript cataloging
2. `catalog_images.py` — image file scanning and metadata extraction
3. `build_signature_map.py` — deterministic signature-to-folio table
4. `extract_references.py` — regex-based reference extraction from Russell's PDF
5. `match_refs_to_images.py` — cross-referencing dissertation refs to images
6. `export_showcase_data.py` — JSON export for the static page

## Site Architecture: The Full Vision

### Page Map

```
/                           → Home: introduction, featured annotations, navigation
/marginalia/                → Marginalia showcase (current page, expanded)
/marginalia/[signature]     → Individual folio detail page
/manuscripts/               → Manuscript overview (both copies)
/manuscripts/bl/            → BL C.60.o.12 page-by-page viewer
/manuscripts/siena/         → Siena O.III.38 page-by-page viewer
/scholarship/               → Bibliography browser
/scholarship/[id]           → Individual article/thesis page with summary
/scholars/                  → Scholar profiles
/scholars/[name]            → Individual scholar page with their works
/about/                     → Project description, methodology, credits
```

### Design Philosophy

**1. The book comes first.**
Every page on the site should be anchored to the physical artifact. Even the scholarship section should be navigable via the folios that scholars discuss. The question is always: "What does this tell us about *this page* of *this book*?"

**2. Images are the primary content.**
The HP is one of the most visually rich books ever printed. The website should let the images breathe — large, zoomable, well-lit. Text (Russell's commentary, scholarly excerpts) is annotation on the images, not the other way around.

**3. Layers of depth.**
A casual visitor should be able to scroll through beautiful manuscript pages and read one-sentence captions. A scholar should be able to drill into Russell's full analysis, cross-reference with other scholarly works, and compare the same folio across manuscripts. The site should serve both without compromising either.

**4. Static first, dynamic later.**
The current implementation is pure HTML/CSS/JS with a JSON data file. This is intentional:
- No server to maintain
- No database exposed to the internet
- Deployable to GitHub Pages, Netlify, or any static host
- Cacheable, fast, resilient

If the site eventually needs search, user accounts, or collaborative annotation, those features can be added behind an API layer. But the core scholarly content should always be available as static pages.

### Technical Stack Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Hosting | GitHub Pages (initial) | Free, version-controlled, custom domain support |
| Build | Static HTML/CSS/JS (no framework) | Zero dependencies, indefinite longevity |
| Data | JSON files generated from SQLite | Human-readable, versionable, no runtime DB |
| Images | JPG originals served directly | No processing pipeline to break; WebP conversion deferred |
| CSS | Custom, no framework | The design language should match the subject: classical, restrained, typographically careful |

### Why Not a Framework?

I considered Hugo, Eleventy, Next.js, and Astro. Each would bring benefits (templating, component reuse, build-time image optimization). But each also brings:
- A dependency that will eventually break
- A build step that must be maintained
- Opinions about structure that may conflict with scholarly presentation needs
- Cognitive overhead for contributors who are humanists, not developers

The HP has survived 527 years. The website representing it should aspire to similar durability. Plain HTML/CSS/JS is the most durable web technology available.

If the site grows beyond ~50 pages, a lightweight static site generator (Eleventy, because it's the least opinionated) would be justified. But not before that threshold.

## Building the Pages

### Home Page
The home page should answer three questions:
1. What is the *Hypnerotomachia Poliphili*? (One paragraph + one iconic woodcut)
2. What is this website? (One paragraph: a digital exhibition of marginalia and scholarship)
3. Where do I go? (Three cards: Marginalia, Manuscripts, Scholarship)

Design: full-width hero image (one of the most famous woodcuts), then a clean three-column card layout. No carousel, no animation, no JavaScript needed on this page.

### Marginalia Showcase (Expansion of Current Page)
The current showcase page is the foundation. It needs:
- **Sorting options**: by signature order (default), by manuscript, by annotation type
- **Richer cards**: include annotation type classification and chapter context
- **Connected detail pages**: clicking a card opens a dedicated `/marginalia/a4r` page rather than a lightbox, with room for full scholarly commentary
- **Cross-manuscript comparison**: when both BL and Siena images exist for the same folio, show them side by side

### Manuscript Viewer
A page-turning interface for each manuscript. This is the most visually demanding page:
- Sequential folio navigation (prev/next, jump to signature)
- Large image display with pan-and-zoom (consider OpenSeadragon for deep zoom)
- Sidebar showing any annotations Russell identified on the current folio
- Links to scholarship discussing this folio

For the initial build, a simple image gallery with signature navigation is sufficient. Deep zoom can be added when high-resolution TIFF originals become available.

### Scholarship Browser
A filterable bibliography with:
- Sort by year, author, topic cluster
- Filter by topic cluster (the 6 clusters identified in HPSCHOLARS.md)
- Each entry shows: author, title, journal, year, and a 2-3 sentence summary
- Click through to a detail page with full abstract and folio references

### About Page
Project methodology, data sources, credits, contact information, and citation guidance. Include:
- How the signature mapping works
- How references were extracted
- Confidence levels in the matching
- How to contribute corrections

## Data Flow: From Database to Website

```
SQLite DB (hp.db)
    ↓
export_showcase_data.py (and future export scripts)
    ↓
JSON files in site/ directory
    ↓
Static HTML pages that load JSON and render
```

This architecture means:
- The database is the authoritative source
- JSON files are generated artifacts (can be regenerated anytime)
- The website never touches the database directly
- Updates flow one way: edit DB → regenerate JSON → rebuild pages

For the full site, we'll need additional export scripts:
- `export_manuscripts.py` — image lists and metadata for the viewer
- `export_bibliography.py` — enhanced document metadata for the scholarship browser
- `export_folio_index.py` — per-folio aggregation of all references and images

## Deployment Plan

### Phase 1 (Current): Local Development
- Static files served via Python `http.server`
- Images referenced from local directories
- Data in `site/data.json`

### Phase 2: GitHub Pages
- Repository on GitHub
- Images hosted via Git LFS or a separate image CDN
- GitHub Actions workflow: run export scripts → commit JSON → deploy
- Custom domain (optional)

### Phase 3: Enhanced Features
- Full-text search (client-side, using something like Pagefind or Lunr.js)
- Deep zoom for high-res images (OpenSeadragon + IIIF tiles)
- Citation export (BibTeX, RIS) for each scholarly work
- Contributor submission form for corrections to the matching

## Open Questions

1. **Image licensing**: What are the reproduction rights for the BL and Siena images? This determines whether the site can be fully public or must restrict image display.

2. **Image optimization**: The 674 JPGs total ~1 GB. For web serving, they should be resized to web-appropriate dimensions (perhaps 1600px wide for full-page views, 400px for thumbnails). This requires a batch processing step not yet built.

3. **URL structure**: Should individual folios be addressed by signature (`/marginalia/a4r`) or by folio number (`/marginalia/folio-4-recto`)? Signatures are more scholarly; folio numbers are more human-readable. I lean toward signatures as the canonical URL with folio numbers shown in the page content.

4. **Multi-language support**: Several scholarship PDFs are in Italian and German. Should the site present summaries in the original language, in English translation, or both?

5. **Long-term preservation**: Should the site be archived in the Internet Archive's Wayback Machine? Should the database and export scripts be deposited in a data repository (Zenodo, Figshare)?

## What Success Looks Like

The website succeeds when a scholar researching the HP can:
1. Find Russell's analysis of a specific marginal annotation in under 30 seconds
2. See the original manuscript image alongside the analysis
3. Discover other scholars who have discussed the same folio
4. Navigate from one annotation to the next in signature order
5. Understand the relationship between different scholarly interpretations

And when a non-specialist visitor can:
1. Appreciate the beauty of the 1499 printing and its marginalia
2. Understand why scholars care about readers' marks in old books
3. Explore the manuscript images at their own pace
4. Come away knowing more about this extraordinary book than when they arrived
