# HPAGENTS: Why and How We Used Claude Agents

## Summary

Throughout this project, Claude agents (subprocesses spawned via the Agent tool) were used extensively to parallelize research-intensive tasks. This document explains the rationale, what worked, what didn't, and lessons learned.

## Why Agents Were Used

The HP project involves a large corpus of heterogeneous source material: 34 scholarly PDFs converted to markdown, a 250-page PhD thesis, two image collections (674 images total), and a growing bibliography of 97+ entries. Many tasks required reading large amounts of text and producing structured output -- exactly the pattern where agents add value.

### Tasks Delegated to Agents

| Task | Agent Type | Why Delegated | Outcome |
|------|-----------|---------------|---------|
| **Batch article summarization (3 batches x 7-13 articles)** | general-purpose | Each batch required reading 50-100KB of markdown and producing structured JSON summaries. Too much context for a single pass. | SUCCESS -- produced accurate summaries with important corrections (identified mislabeled files, corrected author attributions) |
| **Full codebase exploration** | Explore | Needed to inventory image folders (674 files), check database schema, and map site structure simultaneously. | SUCCESS -- fast, thorough inventory |
| **Folio reference extraction (4 parallel agents for Ch. 4-9)** | Explore | Russell's thesis has 282 folio references scattered across 250 pages. Parallelizing by chapter was natural. | SUCCESS -- each agent covered its chapter and returned complete reference lists |
| **Bibliography gap analysis** | general-purpose | Required reading Russell's 310-entry bibliography, comparing against our 30-item collection, and categorizing gaps by priority. | SUCCESS -- produced comprehensive gap analysis with priority ranking |
| **MIT site reverse-engineering** | general-purpose (background) | Required fetching multiple pages, analyzing HTML structure, and producing strategic document. | PARTIAL -- agent timed out, work had to be redone manually |
| **Web scholarship search** | general-purpose (background) | Required multiple web searches and synthesis of results. | PARTIAL -- agent timed out, work redone manually |
| **Pipeline audit** | Explore | Needed to read all 11 Python scripts and produce per-script analysis. | SUCCESS -- thorough, accurate audit |

## When Agents Worked Well

1. **Batch processing of independent items**: The article summarization batches (3 agents, each processing 7-13 articles) were the clearest win. Each agent operated on a separate set of files with no dependencies on the others. All three ran in parallel and returned in ~60-170 seconds each.

2. **Exploration tasks with bounded scope**: Explore agents given specific directories or file ranges consistently returned complete, well-structured results.

3. **Foreground agents with immediate consumption**: Agents whose output was needed right away (and was consumed in the next message) worked reliably. The results were visible in the conversation and could be acted on immediately.

## When Agents Failed or Underperformed

1. **Background agents with long-running web tasks**: The MIT site analysis and scholarship search agents were launched in the background with `run_in_background: true`. Both ran for extended periods and their results were not reliably accessible afterward. The output files were 0 bytes despite the agents appearing to complete.

2. **Agents doing work that the main conversation then duplicated**: After the background agents returned empty output files, the same work (MIT site fetching, web search) had to be redone in the main conversation. This doubled the total effort.

3. **Cross-agent coordination**: There was no mechanism for one agent to inform another's work. Each agent started fresh with its full prompt but no awareness of what other agents had found. This meant some overlap (e.g., multiple agents reading the same introductory chapters of Russell's thesis).

## Lessons Learned

### Use Foreground Agents for Critical-Path Work
If you need the output to proceed, run the agent in the foreground. Background agents are appropriate only for genuinely independent, non-blocking tasks where you have other work to do in parallel.

### Batch by Independence, Not by Size
The most successful pattern was batching by **independence** (each agent gets its own non-overlapping set of files) rather than by size. The three article-summarization batches worked because they shared zero source files.

### Give Agents Precise Output Schemas
Agents that were told to output "a JSON array with fields: author, title, year, journal, summary, topic_cluster" produced consistently structured, mergeable results. Agents given vaguer instructions produced harder-to-integrate prose.

### Don't Trust Background Agent Output Files
The 0-byte output file issue (documented in HPEMPTYOUTPUTFILES.md) means background agent results should be treated as fire-and-forget. If you need guaranteed output, use foreground agents or save critical results to a file within the agent's own execution.

### Total Agent Usage

Over the project's lifetime, approximately 15-20 agent invocations were made:
- ~10 foreground agents (all succeeded)
- ~5 background agents (2-3 produced usable results, 2 did not)
- Estimated total tokens consumed by agents: ~500K-700K
- Estimated time saved vs. serial processing: 5-10 minutes of wall-clock time per batch
