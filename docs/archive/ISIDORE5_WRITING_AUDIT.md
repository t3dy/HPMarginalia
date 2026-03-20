# ISIDORE5: Writing Audit of All Website Tabs

> Jack Isidore examines what a visitor actually reads on every tab of the
> site, and asks: does it explain what the user needs to know about the
> Hypnerotomachia Poliphili and Russell's analysis?

---

## CRITIQUE: The HP Marginalia Website (364 pages, 14 tabs)

### STRONGEST PASSAGE

The Russell Alchemical Hands essay. This is the only page on the site
that reads like genuine scholarly writing rather than database output.
It has narrative momentum, specific evidence (the Master Mercury
declaration in Latin with translation, the chess match reading with
Hand E's corrections and cancellations), and intellectual stakes (two
alchemists reading the same book through incompatible frameworks). The
recent revision grounded it in thesis page numbers and connected the
d'Espagnet and pseudo-Geber traditions to the physical annotations.
This page is what the whole site should aspire to.

---

### ISSUES (by priority)

**1. BURIED LEDE: The Home page doesn't tell the visitor what the HP is.**

The Home page opens: "The Hypnerotomachia Poliphili, published by Aldus
Manutius in Venice in 1499, is one of the most celebrated and enigmatic
books of the Italian Renaissance."

This is a scholar talking to scholars. An educated lay reader — the
target audience per WRITING_TEMPLATES.md — needs to know:
- What is this book? (A dream narrative with 172 woodcuts)
- Why does anyone care? (It influenced Bernini, garden design, the
  emblem tradition; it was read by a pope, a playwright, and alchemists)
- What is THIS site? (A concordance linking Russell's thesis to
  manuscript photographs)

The page jumps to "This gallery presents marginal annotations" without
explaining what marginal annotations are, why they matter, or who Russell
is. A first-time visitor has no orientation.

**FIX:** Rewrite the Home intro in three paragraphs: (1) What the HP is
and why it matters, written for someone who has never heard of it.
(2) What Russell's thesis discovered about its readers. (3) What this
site lets you do.

---

**2. AUDIENCE ASSUMPTION: Every tab assumes you already know what the HP is.**

The Marginalia tab opens with signature notation ("a quire letter, leaf
number, and side"). The Dictionary tab opens with "the conceptual
armature of the site." The Bibliography tab opens with "not a simple
reading list." The Manuscripts tab opens with "approximately 200 copies
worldwide."

None of these explain what the *Hypnerotomachia Poliphili* actually is —
a 500-page illustrated dream narrative about a man searching for his
beloved through ruined classical buildings, written in a hybrid language
that mixes Italian, Latin, and Greek. None mention that it contains
172 woodcuts. None explain why it was important enough to attract five
centuries of readers.

**FIX:** Each tab's intro should include one sentence establishing the
HP for a new reader. The HPGPTWEBWRITING.txt (now in docs/archive/)
contains strong orientation copy that does this. It was partially
integrated into landing pages but the version on the site is weaker
than the version in the archive.

---

**3. LOGICAL GAP: The About page gives statistics but no argument.**

The About page tells you: "X dissertation references, Y matches, Z
annotator hands." These numbers mean nothing without context. A visitor
doesn't know whether 431 matches is impressive or inadequate. They don't
know what a "match" is. The page is a database report, not an explanation.

What the About page should do: explain the *project's thesis*. Something
like: "James Russell's 2014 dissertation showed that the HP was not an
unread curiosity — it was actively annotated by humanists, playwrights,
a pope, and alchemists. This site connects his findings to the actual
manuscript photographs, folio by folio."

**FIX:** Restructure About as: (1) the project's purpose, (2) what
Russell found, (3) what this site does with it, (4) how the data was
built, (5) what remains provisional. Move the statistics to a subsection.

---

**4. WEAK TRANSITION: The Concordance page explains methodology but not significance.**

The Concordance page is technically excellent — it explains the signature
map, the extraction pipeline, the matching logic, the BL offset, and
the confidence levels. But it never says *why this matters*.

The concordance is remarkable because it solves a genuinely hard problem:
connecting a scholar's close reading of specific folios (referenced by
a notation system that no one uses in daily life) to photographs that
are named by completely different conventions. The result is that you
can read Russell saying "on b6v, the alchemist labels the elephant with
mercury symbols" and then *see the photograph of that page*.

The page never communicates this. It reads like an engineering report.

**FIX:** Add an opening paragraph that says what the concordance makes
possible before explaining how it works.

---

**5. UNSUPPORTED CLAIM: Dictionary term pages present LLM-generated prose as if it were scholarship.**

Every dictionary term page has a "Why It Matters for the Hypnerotomachia"
section and a "Why It Matters in Scholarship" section. These are
well-formatted and cite scholars by name. They read like expert
commentary. They were generated by an LLM in a single batch.

The "Draft" badge is present but small. A visitor scanning the page
will read "Trippe (2002) argues that the HP has been understudied as
literature" and assume a domain expert wrote this. In fact, a language
model wrote it based on corpus evidence. The claim may be accurate —
Trippe does argue this — but the presentation implies a level of
editorial authority that doesn't exist.

**FIX:** Either enlarge the Draft badge and add a sentence like "This
entry was generated with AI assistance and has not been reviewed by a
domain expert," or suppress the significance sections until they've been
reviewed. The current presentation is formally honest (the badge is there)
but rhetorically misleading (the prose reads as authoritative).

---

**6. REDUNDANCY: Three pages explain the same thing about b6v.**

The elephant-obelisk woodcut on b6v appears on:
- The **marginalia page** (marginalia/b6v.html) with the alchemical
  analysis, symbol table, and folio description
- The **woodcut page** (woodcuts/elephant-obelisk.html) with the
  subject description and scholarly discussion
- The **Russell essay** (russell-alchemical-hands.html) with the
  Hand B analysis

Each page repeats that Bernini was influenced by this woodcut, that
Hand B annotated it with ideograms, and that Heckscher documented the
connection. A visitor who reads all three encounters the same information
three times.

This isn't wrong — cross-linking is good — but the three pages don't
differentiate their perspectives. The marginalia page should focus on
*what's on this specific folio*. The woodcut page should focus on *this
image's art-historical significance*. The essay should focus on *what
the alchemist's reading reveals*. Currently they all blur together.

**FIX:** Give each page a distinct editorial voice: the marginalia page
is a *dossier* (evidence-first), the woodcut page is an *art entry*
(visual-first), the essay is an *argument* (interpretation-first).
Reduce repetition by linking instead of restating.

---

**7. MISSING CONTENT: The site never tells you what the HP actually says.**

Nowhere on the 364-page site can a visitor read what the *Hypnerotomachia
Poliphili* is about. There is no plot summary. There is no description of
Poliphilo's journey. The dictionary has entries for characters (Poliphilo,
Polia, Venus, Eleuterylida) but no narrative overview.

A visitor can learn that "Poliphilo is the protagonist and dreamer of the
HP, whose name means 'lover of many things'" — but they can't learn what
happens to him. They can learn about the elephant-obelisk woodcut but not
where it falls in the story. They can learn about the five nymphs but not
what the nymphs do.

This is the site's deepest content gap. It is a site *about the readers
of a book* that never describes *the book itself*.

**FIX:** Add a "The Book" page (or expand the Digital Edition tab) with
a 1500-2000 word narrative summary of the HP's plot, divided by major
sections: the dark forest, the ruined temple, Queen Eleuterylida's
court, the five nymphs, the triumphal processions, the sacrifice to
Priapus, the voyage to Cythera, Book II (Polia's narration). This would
give every other page on the site a narrative anchor.

---

**8. WEAK LINK: Scholar pages don't connect to the HP's content.**

The scholar pages tell you what each researcher wrote and when. They
don't tell you what part of the HP they wrote about. Rosemary Trippe's
page says she argued the HP "has been understudied as literature" — but
it doesn't say which passages she analyzed, which woodcuts she discussed,
or which folios her argument addresses.

If a visitor wants to know "who has written about the elephant-obelisk?"
they have to search each scholar page individually. There's no reverse
index from HP content to scholars.

**FIX:** Add a "Key folios discussed" or "HP passages analyzed" section
to scholar pages where this data is available. The corpus search
infrastructure could extract this from paper summaries.

---

**9. MISSING: No explanation of what "alchemical reading" means for a non-specialist.**

The Russell essay and the marginalia pages use terms like "alchemical
allegory," "d'Espagnet's framework," "pseudo-Geber," "nigredo," "chemical
wedding," and "coincidentia oppositorum" without defining them for a
non-specialist reader.

The dictionary has entries for these terms. But the essay doesn't link
to them inline — the cross-links are in a block at the bottom of the
page. A reader encountering "d'Espagnet's Enchiridion Physicae Restitutae"
for the first time has to scroll past the entire essay to find the
Related Dictionary Terms section.

**FIX:** Add inline links within essay prose. When the essay mentions
"alchemical allegory," link the phrase to the dictionary term. When it
mentions "d'Espagnet," link to the prisca-sapientia entry. This is the
whole point of having a dictionary — to make specialist vocabulary
accessible at the point of encounter.

---

### REVISION PRIORITY

Fix Issue #7 first — add a narrative summary of the HP. Every other page
on the site assumes the visitor knows the book. Without a plot summary,
the site is a reference work for people who have already read the HP. With
one, it becomes accessible to anyone curious about a remarkable Renaissance
book.

Then fix Issue #1 — rewrite the Home intro for a non-specialist audience.
This is the first thing every visitor reads.

Then fix Issue #9 — add inline dictionary links to the essay. This turns
the dictionary from a standalone reference into an integrated learning tool.

### OVERALL

The site's writing is structurally competent and editorially honest.
Every page has orientation copy, review badges, and provenance markers.
The prose is grammatically clean and avoids the worst habits of academic
jargon. The Russell essay is genuinely good.

But the site writes for an audience that already knows the HP, already
knows what marginalia are, already knows what a signature notation means.
It is a scholar's working tool dressed as a public-facing website. The
WRITING_TEMPLATES.md says the target reader "visits exhibitions, reads
long-form journalism, and is curious about Renaissance books." That reader
would arrive at this site, read "The HP's chapter initials spell POLIAM
FRATER FRANCISCVS COLVMNA PERAMAVIT," and leave — because nobody told
them what the HP is, why anyone would read it, or what happened when they
did.

The site's data is excellent. Its infrastructure is sound. Its writing
is professional. What it lacks is hospitality — the willingness to meet
a curious reader where they are and walk them into the subject.
