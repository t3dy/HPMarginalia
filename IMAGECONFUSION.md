# IMAGECONFUSION: How the Pipeline Lost Track of the Original Images

---

## The Short Version

The database thinks our images live at `images/bl/` and `images/siena/` — the
compressed copies we made for the website. The actual high-quality originals
sit in two folders at the project root. No script or query currently points
to the originals. If we try to read handwriting, symbols, or fine print from
the images the database knows about, we'd be reading 200KB compressed JPEGs
instead of 4MB originals — like trying to read a manuscript through frosted
glass.

---

## What Happened, Step by Step

### Step 1: The originals arrived

Two folders of manuscript photographs were downloaded to the project root:

```
3 BL C.60.o.12 Photos-20260319T001113Z-3-001/
  3 BL C.60.o.12 Photos/
    C_60_o_12-001.jpg  (4-5 MB each, 196 files, 778 MB total)

Siena O.III.38 Digital Facsimile-20260319T001110Z-3-001/
  Siena O.III.38 Digital Facsimile/
    O.III.38_0001r.jpg  (~500 KB each, 478 files, 234 MB total)
```

These are the research-quality images. The BL photos are large, detailed
scans where you can read handwriting and see small symbols. The Siena images
are lower resolution but still the best available.

### Step 2: Images were compressed for the website

`compress_images.py` was written to make web-friendly copies:

- BL originals (4 MB each) were resized from full resolution to 800px wide
  and saved at 75% JPEG quality → ~200 KB each (95% size reduction)
- Siena originals (~500 KB) were copied as-is (already small enough)

The compressed copies went into `site/images/bl/` and `site/images/siena/`.
This was correct — GitHub Pages can't serve a 778 MB image folder.

### Step 3: The database was pointed at the compressed copies

When `catalog_images.py` first ran to build the `images` table, the
`manuscripts.image_dir` field pointed to the *compressed* `site/images/`
folders, not the originals. So every `images.relative_path` in the database
was set to paths like:

```
images/bl/C_60_o_12-014.jpg       (200 KB compressed copy)
images/siena/O.III.38_0042r.jpg   (500 KB copy)
```

Instead of:

```
3 BL C.60.o.12 Photos.../C_60_o_12-014.jpg   (4.5 MB original)
Siena O.III.38 Digital Facsimile.../O.III.38_0042r.jpg  (500 KB original)
```

### Step 4: manuscripts.image_dir was updated, but nothing else

At some point later, `manuscripts.image_dir` was updated to point to the
original high-quality folders:

```sql
-- manuscripts table now says:
C.60.o.12  → image_dir = "3 BL C.60.o.12 Photos.../3 BL C.60.o.12 Photos"
O.III.38   → image_dir = "Siena O.III.38 Digital Facsimile.../Siena O.III.38 Digital Facsimile"
```

But `catalog_images.py` was never re-run after this change. So now:

- `manuscripts.image_dir` → points to **originals** (correct)
- `images.relative_path` → points to **compressed web copies** (stale)

These two sources of truth disagree.

### Step 5: Everything downstream followed relative_path

Every script and query that needs an image path uses `images.relative_path`:

- `build_site.py` builds `<img src>` tags from it → works fine (web display)
- `export_showcase_data.py` puts it in `data.json` → works fine (gallery)
- `match_refs_to_images.py` joins through it → works fine (matching is by
  folio number, not file content)
- Any future image-reading script would use it → **would read the wrong
  files** (compressed instead of originals)

The mismatch was invisible because:
1. The website only needs compressed images, and that's what `relative_path`
   points to — so the site looks correct
2. Matching is done by folio number arithmetic, not by reading image content
   — so matches are unaffected
3. Nobody has built the image-reading pipeline yet — so the fact that it
   would read compressed images has never caused a visible error

---

## The Consequence

If we run the planned image-reading pipeline (HP320bIMAGEREADINGPLAN.md)
using the paths currently in the database, we'd send 200KB compressed JPEGs
to the vision model instead of 4MB originals. For the BL images, that's a
**95% reduction in image data** — exactly the kind of detail loss that makes
handwriting illegible and small symbols invisible.

The Siena images happen to be identical (the originals were small enough to
copy as-is), so only BL is affected in practice. But the principle is wrong
for both: the database should know where the originals are.

---

## The Fix

The `images` table needs two paths:

| Column | Points To | Used By |
|--------|----------|---------|
| `master_path` (new) | Original high-quality image | Image reading, analysis, verification |
| `web_path` (new) | Compressed copy in `site/images/` | HTML `<img>` tags, gallery display |

Current `relative_path` becomes `web_path`. New `master_path` is computed
from `manuscripts.image_dir` + `images.filename`.

All display code keeps using `web_path`. All reading/analysis code uses
`master_path`. No data is lost, no existing behavior changes.

---

## Why It Wasn't Caught

1. **The site looked fine.** Compressed images display perfectly on the web.
   Nobody noticed the database pointed to them instead of the originals
   because the site was the only consumer.

2. **No script reads image content.** The entire pipeline operates on
   metadata (filenames, folio numbers, signature references). Image bytes
   are never opened by any script except `compress_images.py` — which
   correctly reads from the originals.

3. **The discrepancy was between two different fields.** `manuscripts.image_dir`
   was correct; `images.relative_path` was stale. Unless you compared them
   side by side, the inconsistency was invisible.

4. **Image reading was planned but not built.** The consequences of using
   compressed images only matter when you actually try to read them. Since
   the reading pipeline (Phases 1-4 in HP320b) hasn't been built yet,
   the error never manifested.

---

## Provenance

- Discovered: 2026-03-20
- Root cause: `catalog_images.py` ran before `manuscripts.image_dir` was
  updated to point to originals
- Impact: `images.relative_path` stores web-copy paths, not original paths
- Severity: Low (site works fine), but blocks image-reading pipeline
- Fix: Add `master_path` and `web_path` columns, backfill from known data
