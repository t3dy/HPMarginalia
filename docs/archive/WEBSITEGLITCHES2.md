# WEBSITEGLITCHES2: CSS Caching and Preview Server Debugging

> Continuation of WEBSITEGLITCHES.md covering the gallery card redesign
> debugging session.

---

## 14. Preview Server CSS Caching

**Problem:** After adding `.card-desc` and `.card-hand` CSS rules to
`style.css`, the preview server continued showing unstyled elements.
`preview_inspect` reported `font-size: 16px` (browser default) and
`max-height: none` instead of the specified `0.82rem` and `4.7em`.

**Diagnosis sequence:**
1. Confirmed CSS was in the file (`grep card-desc site/style.css` → found)
2. Confirmed script.js had no inline styles overriding the class
3. Used `preview_eval` to search loaded stylesheets — rule "not found"
4. Concluded: the preview browser cached the old `style.css`

**What didn't work:**
- `window.location.reload()` — didn't clear CSS cache
- `window.location.reload(true)` — still cached
- Navigating to a different page and back — still cached

**What worked:**
- `preview_stop` + `preview_start` (restart the entire preview server)
- After restart, `preview_inspect` showed correct values:
  `font-size: 13.12px`, `color: rgb(90, 78, 66)`, `max-height: 61.664px`

**Lesson:** The preview server's internal browser has aggressive CSS
caching. When CSS changes don't appear:
1. First check the file is saved (`grep` for the selector)
2. If saved, restart the server (`preview_stop` + `preview_start`)
3. Don't waste time with reload — it doesn't clear the CSS cache

**Note:** The deployed site on GitHub Pages does NOT have this problem.
Fresh browser loads from the CDN always get the current CSS. This is
purely a local preview debugging issue.

---

## 15. Gallery Network 404s from Stale Requests

**Problem:** After updating image paths in the database and rebuilding,
the preview's network log showed hundreds of 404s for the OLD image
paths (the deep directory structure).

**Diagnosis:** The network request log in the preview tool doesn't clear
between page navigations within the same session. All timestamps showed
`41056.xxx` — the same session epoch. The 404s were from a page load
BEFORE the rebuild, not after.

**What was confusing:** The sheer volume of 404s (hundreds of them)
made it look like the path update had failed. But checking `data.json`
showed the new paths were correct, and checking `site/marginalia/b6v.html`
showed `src="../images/bl/C_60_o_12-041.jpg"` — the correct new path.

**Fix:** Ignored the stale 404s. Verified correctness by checking
the generated files directly rather than trusting the accumulated
network log.

**Lesson:** The preview network log is append-only within a session.
Don't diagnose path problems from the network log — check the generated
files directly.

---

## 16. Gallery Cards Without Visible Descriptions

**Problem:** After deploying gallery card descriptions, the user
reported that the descriptions weren't visible on the landing page
screenshot they sent.

**Diagnosis:** The descriptions WERE in the data.json (all 223 entries
had `card_description` populated). The script.js WAS rendering them.
But the CSS wasn't loaded (see glitch #14 above), so the descriptions
appeared as unstyled text that blended into the card layout.

**Fix:** The CSS rules for `.card-desc` (font-size, color, max-height)
and `.card-hand` (attribution line) give the descriptions proper visual
hierarchy. Once CSS loaded correctly (after server restart), the cards
showed: signature → badge → hand attribution → description → marginal
text quote, each visually distinct.

**Lesson:** "I can't see it" can mean "the data isn't there" OR "the
styling isn't applied." Always check both before concluding which.
