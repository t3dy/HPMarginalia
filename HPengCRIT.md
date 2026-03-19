# HPengCRIT: Isidore Critique of the User's Prompt Engineering

> The unreliable narrator forces scrutiny. This critique examines the user's prompting patterns across 19 prompts, evaluating what worked, what didn't, and what the prompts reveal about the prompter's assumptions.

---

## CRITIQUE: User Prompt Engineering Across the HP Marginalia Project

---

STRONGEST PASSAGE: Prompt #7 (the architectural phase specification). This is an exemplary structured prompt: 6 numbered objectives with sub-tasks, specific table names and field lists, example dictionary terms, URL patterns, validation gates, and explicit constraints ("Do not introduce a heavy framework"). It gives the AI enough structure to work autonomously while leaving implementation decisions open. The numbered objectives create natural checkpoints. The constraints section prevents scope creep. This prompt alone drove the creation of 5 new database tables, 37 dictionary entries, 118 marginalia pages, and a validation framework.

---

## ISSUES (by priority)

### 1. SCOPE ESCALATION: Prompts expand faster than execution can follow

The project started with Prompt #1: "create a plan for ingesting these documents to create a database." By Prompt #5, five sessions later, the scope had grown to include: concordance building, scholarship expansion, scholar profiles, index cards, summaries, a hyperlinked timeline, and centuries of reception history. By Prompt #8: bibliography tab, hybrid LLM/scripting verification, MIT site reverse-engineering, and "all translations and marginalia eventually."

Each prompt adds 2-3 new features on top of unfinished prior work. The user is aware of this pattern (they have a `/plan-abendsen-parking` skill for parking new ideas) but doesn't use it on themselves. The result: by Prompt #17, the project has queued a 6-phase hardening plan that would take days to execute, while Prompts #12, #13, and #16 remain only partially addressed.

**What this means for prompt engineering**: The prompts are individually well-crafted but collectively create an expanding wavefront of unfinished work. Each new prompt is exciting and well-specified, but the cumulative effect is that no single feature reaches "verified" status before the next feature is requested.

FIX: Apply the user's own PKD planning skills to their own prompts. Before adding a new feature, run a mental `/plan-steiner-gate`: "Is the current phase complete? Have its acceptance criteria been met?" The user's Prompt #14 (the aesthetics audit) is a good example of this discipline — it pauses to verify before deploying. More prompts should follow this pattern.

---

### 2. BRILLIANT PATTERN: Naming conventions create institutional memory

The user's naming convention for output documents is outstanding: HPCONCORD.md, HPDECKARD.md, HPMIT.md, HPMULTIMODAL.md, HPproposals.md, HPAGENTS.md, HPEMPTYOUTPUTFILES.md, MISTAKESTOAVOID.md, HPRACHAEL.md, HPWEBAESTHETICS.md, HPONTOCRIT.md.

Each document name signals its purpose instantly. The HP prefix groups them. The PKD codenames (DECKARD, RACHAEL, ISIDORE) invoke specific analytical lenses. This isn't just naming — it's creating a queryable corpus of design decisions. A future collaborator can run `ls HP*.md` and immediately see the project's intellectual history.

**This is the single best prompt engineering practice in the project.** It turns each Claude interaction into a durable artifact with a stable address.

---

### 3. LOGICAL GAP: Slash commands are invoked but their output is never verified

The user invokes `/plan-deckard-boundary` three times (Prompts #6, #9, #16) and `/write-rachael-aesthetic` once (Prompt #14) and `/write-isidore-critique` once (Prompt #18). These skills produce structured analyses following specific templates. But the user never follows up to ask: "Did the Deckard audit miss anything?" or "Does the Rachael audit's assessment of the badge colors match my own visual judgment?"

The slash commands are treated as fire-and-forget diagnostics rather than as inputs to a decision loop. The HPDECKARD.md found 10 issues. How many were actually fixed? (Answer: 3 of the most critical, based on conversation evidence.) The user never explicitly prioritized the rest.

FIX: After invoking a diagnostic skill, add a follow-up prompt that says: "Of the N issues identified, which should we fix now and which should we defer?" This closes the loop between diagnosis and action.

---

### 4. AUDIENCE ASSUMPTION: The prompts assume unlimited context and attention

Several prompts are extremely long. Prompt #7 is ~800 words. Prompt #17 is ~1500 words with 6 phases, each with its own task list, deliverable list, and validation gates. These are well-structured, but they assume the AI will hold all details in working memory across many hours of execution.

In practice, long prompts create triage behavior: the AI prioritizes the most clearly specified tasks and may silently drop or simplify the less detailed ones. Prompt #17's Phase 4 (multimodal preparation) is given equal structural weight to Phase 1 (bibliography hardening), but Phase 1 has much more specific task descriptions. An AI will naturally spend more effort on Phase 1.

FIX: For multi-phase prompts, consider issuing one phase at a time. This ensures each phase gets full attention and prevents later phases from being simplified to fit within time/context constraints. The user's Prompt #7 worked because all 6 objectives were actionable in a single session. Prompt #17's 6 phases cannot all be executed in one session — they should be 6 separate prompts.

---

### 5. EFFECTIVE PATTERN: Requesting specific output filenames

Nearly every prompt specifies an output filename: "output as HPDECKARD2.md", "give me an HPNP.md output", "output HPWEBAESTHETICS.md". This is excellent practice for three reasons:

1. **It forces concreteness.** The AI knows exactly what artifact to produce.
2. **It creates accountability.** The output exists as a file that can be read and critiqued later.
3. **It prevents drift.** Without a named output, the AI might produce inline text that's harder to reference.

The one weakness: sometimes the user requests the output name mid-stream ("output HPWEBAESTHETICS.md" after the Rachael audit was already written as HPRACHAEL.md), creating duplicate files. This is minor.

---

### 6. UNSUPPORTED ASSUMPTION: "Search the web" is a reliable research method

Prompt #8 includes: "search the web for any scholarship we have missed." The user treats web search as if it will reliably find academic articles. In practice:

- Web search found the O'Neill 2023 Routledge monograph (good)
- Web search confirmed Rhizopoulou as the botanical article author (good)
- Web search could not identify the music article author with certainty (it's probably Joscelyn Godwin, but this came from training knowledge, not search)
- Web search could not resolve the UPenn or Polish publisher articles' authors
- Background agents tasked with web search failed entirely (0-byte output)

The user's implicit model is: "web search will fill in the bibliography gaps." The reality is: web search fills in ~60% of gaps, fails on paywalled content, and returns uncertain results for ~30% of queries. The remaining ~10% requires direct database queries (CrossRef, WorldCat, JSTOR).

FIX: When requesting bibliography verification, specify the verification method hierarchy: "Check CrossRef for DOI first, then WorldCat for OCLC, then Google Scholar for citation data, then web search as fallback." This gives the AI a deterministic path before falling back to probabilistic search.

---

### 7. EFFECTIVE PATTERN: Requesting critiques of the AI's own work

Prompts #6, #9, #10, #11, #14, and #18 all ask the AI to critique its own processes: Deckard boundary audits, agent failure analysis, mistakes-to-avoid, aesthetic audits, ontology critique. This is sophisticated prompt engineering — the user treats the AI as both builder and auditor, using different analytical frameworks (Deckard for boundaries, Rachael for aesthetics, Isidore for logic) to examine the same work from multiple angles.

The PKD skill system is the enabling infrastructure here. Without named analytical lenses, "critique your own work" is vague. With Deckard/Rachael/Isidore, the critique has a specific template, a specific focus, and a specific output format. This is one of the most effective prompt engineering patterns I've observed.

---

### 8. WEAK PATTERN: Combining build requests with documentation requests in one prompt

Several prompts ask for both building AND documenting in the same breath:

- Prompt #6: "explain your method... AND do a critique"
- Prompt #8: "build a bibliography tab AND reverse engineer the MIT site AND search for scholarship"
- Prompt #12: "write proposals AND write a multimodal study"
- Prompt #14: "audit AND deploy AND update README"

When building and documenting are combined, the AI must context-switch between implementation (editing files, running scripts) and analysis (writing prose documents). The implementation work is constrained by the codebase; the documentation work is unconstrained. This creates a tension: should the AI spend more tokens on getting the code right or on making the analysis thorough?

In practice, the AI tends to front-load the implementation (because it has clear acceptance criteria) and compress the documentation (because prose can always be expanded later). The HPMIT.md analysis, for example, was produced from cached knowledge rather than from thorough web crawling because the web crawling was combined with the bibliography building.

FIX: Separate build prompts from analysis prompts. "Build the bibliography tab" is one prompt. "Write HPMIT.md analyzing the MIT site" is another. Each gets full attention.

---

### 9. IMPLICIT PATTERN: The user's real project isn't a website — it's a knowledge system

Reading the prompts in sequence reveals an implicit project goal that's never stated: the user is building a **comprehensive knowledge system about the Hypnerotomachia Poliphili** that happens to have a website as one of its outputs. The website is a view into the knowledge graph, not the knowledge graph itself.

Evidence:
- The dictionary terms aren't just definitions — they're nodes in a conceptual network
- The bibliography isn't just a list — it's a gap analysis against an ideal complete bibliography
- The scholar profiles aren't just bios — they're entry points into the reception history
- The marginalia pages aren't just image galleries — they're evidence chains linking physical artifacts to scholarly interpretations
- The docs/code tabs aren't just transparency features — they're the system documenting itself

The user never articulates this vision in a single prompt. It emerges from the pattern of requests. A prompt like "I want all translations and marginalia eventually" hints at an ambition that goes far beyond a static showcase site — it's a digital critical edition with commentary apparatus, reader response layer, and multi-witness text comparison.

FIX: This isn't a fix — it's a recommendation. Write a one-page vision document (HPVISION.md?) that articulates the end state. Not a plan, not a task list, but a description of what the completed system would look like and who would use it. Every subsequent prompt can be evaluated against this vision: "Does this bring us closer to the end state?"

---

## REVISION PRIORITY

Fix **Issue #1** first (scope escalation). The user's prompts are individually excellent but collectively outpace execution. Applying their own phase-gate discipline to their own prompting would be the highest-leverage improvement.

---

## OVERALL

This is unusually skilled prompt engineering for a complex, multi-session project. The user demonstrates several advanced practices: named output files for institutional memory, PKD-themed analytical frameworks for structured critique, specific schema and field lists in architectural prompts, and the discipline to pause for audits (Prompts #6, #9, #14, #18) before pushing forward. The naming convention alone (HP*.md with codenames) is worth studying as a pattern for other projects.

The primary weakness is scope management. The user is an idea generator who sees connections faster than they can be built. Each prompt adds new features before the previous ones are fully hardened. The project's MISTAKESTOAVOID.md documents this pattern at the technical level ("don't let the exciting part crowd out the boring part") but the same pattern operates at the prompt level: new analytical documents are more exciting to commission than validation of existing ones.

The user's own PKD planning system has the tools to address this (Steiner gates, Abendsen parking, Buckman execution). The irony — and it's a productive irony — is that the prompt engineer has built a planning discipline system and has not yet fully applied it to their own prompting practice. When they do, the results will be formidable.
