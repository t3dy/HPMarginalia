# ISIDORE3: Critique of the Next-Phases Plan

> Jack Isidore forces scrutiny. This critique examines the HiroPlantagenet plan for Layers 1-5 (data fixes, ontology rewrite, alchemical enrichment, multimodal spec, scholarship infrastructure specs) and asks: where does this plan lie to itself?

---

## CRITIQUE: Next-Phases Plan (HiroPlantagenet Output, 2026-03-20)

### STRONGEST PASSAGE

The plan's best move is splitting execution from specification: Layers 1-3 are executable work, Layers 4-5 are spec-only. This prevents the project's chronic pattern of designing five features at once and executing none completely. The explicit marking of "do not execute without user approval" on the multimodal phase is honest about the API-cost boundary.

---

### ISSUES (by priority)

**1. BURIED LEDE: The plan avoids the project's actual crisis.**

The explore agent documented the core problem clearly: "Significant gap between what has been proposed/designed and what has been implemented." The project has 25 specification documents. It has built 330 pages. But the specifications keep growing faster than the execution.

This plan responds by — writing more specifications (Layers 4 and 5).

The plan should lead with: "The next phase is about CLOSING gaps, not opening new ones." Instead it buries this behind five layers of technical work, three of which produce more .md files.

**FIX:** Reframe the plan. Layer 1 is "close the data quality gap." Layer 2 is "close the documentation-reality gap." Layer 3 is "deepen what exists." Layers 4-5 are "prepare — but do not start — the next expansion." The framing should make explicit that the project's failure mode is over-specification, and this plan consciously resists it.

---

**2. LOGICAL GAP: The annotation type classification was done with a blunt instrument and the plan doesn't acknowledge this.**

The classify_annotations.py script assigned 127 of 282 annotations as INDEX_ENTRY based on regex matching for "nota" and "nb" and "index" and "label" in the context text. But Russell's thesis uses "nota" and "label" constantly as ordinary English words ("nota bene" aside, "he labels the passage" is not an index entry). The classification is almost certainly overfitting: many of those 127 INDEX_ENTRY annotations are probably MARGINAL_NOTE or CROSS_REFERENCE that happen to contain "nota" in their context.

The plan proposes no validation of this classification. It treats it as done.

**FIX:** Add a validation step: sample 20 annotations classified as INDEX_ENTRY and manually check whether the classification is correct. If the error rate is >30%, re-run with a more careful regex or reclassify the dubious ones as MARGINAL_NOTE.

---

**3. UNSUPPORTED CLAIM: "15 of 28 alchemist refs need descriptions" is wrong.**

The plan says there are 28 alchemist-attributed refs and 13 folio descriptions, leaving 15 undescribed. But the fact check shows only 11 distinct alchemist signatures. The folio_descriptions table has 13 rows covering all 11 signatures (some signatures have multiple descriptions from different hands). The actual gap is zero — all alchemist signatures have at least one description.

The plan inherited this error from the explore agent, which read the CONCORDANCESTATUS.md (written before consolidation) and treated its numbers as current.

**FIX:** Remove "generate remaining 15 folio descriptions" from Layer 3. The actual remaining work is process-stage tagging and hand-interaction analysis, not more description generation.

---

**4. AUDIENCE ASSUMPTION: The plan assumes the user wants more infrastructure.**

The plan proposes five layers, three of which produce database tables, scripts, and spec files. But the user's actual request was "read through all my design docs and make a plan for the next phases." The user may want to hear: "stop building infrastructure and start writing the book-level content that makes the site worth visiting." Or: "run the multimodal pipeline and solve the BL confidence problem." Or: "write the six manuscript copy essays."

The plan never asks what the user wants to prioritize. It assumes infrastructure is always the answer.

**FIX:** Present the plan with explicit priority choices: "Do you want to (A) fix data quality, (B) write copy essays, (C) run multimodal image reading, or (D) all three in sequence?" Don't default to the builder's preference for schema work over content.

---

**5. REDUNDANCY: Layers 4 and 5 duplicate existing documents.**

Layer 4 proposes writing "docs/MULTIMODAL_SPEC.md" — but HPMULTIMODAL.md already exists and is a detailed, well-written 2000+ word proposal with a complete implementation roadmap, cost estimates, and expected outputs. Writing another spec file duplicates it.

Layer 5 proposes "docs/BIBLIOGRAPHY_VERIFICATION_SPEC.md" — but HPDECKARD2.md already contains the hybrid verification pipeline design, including deterministic normalization, CrossRef lookup, URL validation, LLM fallback, and human review stages.

The plan should reference these existing documents, not propose creating new versions.

**FIX:** Layer 4 becomes "install HPMULTIMODAL.md as the executable spec and create the batch script." Layer 5 becomes "extract the bibliography pipeline from HPDECKARD2.md into a standalone script." Point to existing docs, don't re-spec.

---

**6. WEAK TRANSITION: The plan doesn't connect to what was just built.**

This session built: annotations table (282 rows), type classification, symbol occurrences (26 rows), alchemical framework columns, timeline (71 events), manuscripts (6 copies), 94 dictionary terms with significance, 59 scholar overviews. That is a massive amount of new infrastructure.

The plan should start by acknowledging this and asking: "Is the new infrastructure correct? Has anyone verified it?" Instead it proposes building more on top of unverified foundations.

The 94 significance_to_hp entries were generated by LLM in a single batch without any human review. The 59 scholar overviews were generated the same way. The annotation type classifications are regex-based and likely noisy. The plan proposes adding alchemical process stages and hand interactions on top of this unreviewed base.

**FIX:** Add a Layer 0: "Spot-check session outputs." Sample 10 dictionary significance entries, 5 scholar overviews, 10 annotation type classifications. Identify error rates. Fix systematic errors before building more.

---

**7. MISSING: The plan never mentions the user's actual design documents as actionable.**

HPMIT.md contains specific, excellent design recommendations for the digital edition: parallel translations, multi-panel manuscript viewer, cross-copy comparison tools. HPproposals.md contains 6 concrete proposals for content quality improvement. HPWEBAESTHETICS.md identifies 9 CSS/design issues.

The plan ignores all of these. It proposes ontology rewrites and schema extensions instead.

**FIX:** Add a layer that directly addresses one of the user's own design documents. For example: "Execute HPproposals.md Proposal 3 (deterministic quality checks)" or "Fix the 2 critical issues from HPWEBAESTHETICS.md."

---

### REVISION PRIORITY

Fix Issue #1 first — the buried lede. The plan should open with: "The project's chronic pattern is over-specification. This plan breaks that pattern by executing three layers of concrete work and installing only two future specs that reference existing documents."

Then fix Issue #6 — add the verification layer. Building more on unverified foundations compounds errors.

### OVERALL

The plan is technically competent but strategically evasive. It proposes the kind of work the builder finds satisfying (schema design, data extraction, spec writing) rather than the kind of work the project needs (verification, content depth, closing the gap between specs and execution). The five-layer structure looks like progress but three of the five layers produce documents, not site content. The plan should be honest about this tension: the project has enough infrastructure. What it needs is content, verification, and the courage to stop designing and start finishing.

The plan's best quality is its explicit separation of "execute now" from "spec for later." Its worst quality is that it doesn't interrogate whether the executed work from this session is correct before proposing to build more on top of it.
